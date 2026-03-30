# Apply Quake Live UI symbol map to a Ghidra project.
#@author QuakeLive-reverse
#@category QuakeLive/UI
#@menupath Tools.QuakeLive.Apply UI Symbol Map
#@toolbar

"""Apply the committed ui.json symbol map to the currently open uix86.dll Ghidra project.

For each entry in the map the script:
  1. Looks up the function at the recorded address.
  2. Renames the function to the ``normalized_name`` from the map.
  3. Appends the ``comment`` field from the map as a plate comment on the
     function entry point when one is present.

Run via the Ghidra GUI (Script Manager) or headless::

    analyzeHeadless <project_dir> <project_name> \
        -process uix86.dll \
        -postScript ApplyUISymbolMap.py \
        [<symbol_map_path>]

The optional first argument overrides the default location::

    <repo_root>/references/symbol-maps/ui.json

The script resolves ``<repo_root>`` relative to its own location
(``<repo_root>/ghidra_scripts/``).
"""

import json
import os

from ghidra.program.model.symbol import SourceType


def main():
	program = currentProgram
	if program is None:
		printerr("No program is active; aborting")
		return

	script_dir = os.path.dirname(os.path.abspath(str(sourceFile)))
	repo_root = os.path.dirname(script_dir)
	default_map = os.path.join(repo_root, "references", "symbol-maps", "ui.json")

	args = list(getScriptArgs())
	map_path = args[0] if args else default_map

	if not os.path.isfile(map_path):
		printerr("Symbol map not found: %s" % map_path)
		return

	with open(map_path, "r") as fh:
		manifest = json.load(fh)

	functions = manifest.get("functions", [])
	if not functions:
		printerr("No functions found in symbol map: %s" % map_path)
		return

	println("Loaded %d function entries from %s" % (len(functions), map_path))

	func_manager = program.getFunctionManager()
	addr_factory = program.getAddressFactory()
	listing = program.getListing()

	renamed = 0
	commented = 0
	skipped = 0
	transaction_id = program.startTransaction("Apply UI Symbol Map")
	try:
		for entry in functions:
			addr_str = entry.get("address", "")
			normalized = entry.get("normalized_name", "")
			comment = entry.get("comment", "")

			if not addr_str or not normalized:
				skipped += 1
				continue

			try:
				addr = addr_factory.getAddress(addr_str)
			except Exception:
				printerr("Could not parse address: %s" % addr_str)
				skipped += 1
				continue

			func = func_manager.getFunctionAt(addr)
			if func is None:
				skipped += 1
				continue

			current_name = func.getName()
			if current_name != normalized:
				try:
					func.setName(normalized, SourceType.USER_DEFINED)
					renamed += 1
				except Exception as exc:
					printerr("Could not rename %s -> %s: %s" % (current_name, normalized, exc))
					skipped += 1
					continue

			if comment:
				existing = listing.getComment(0, addr)
				if not existing:
					listing.setComment(addr, 0, comment)
					commented += 1
	finally:
		program.endTransaction(transaction_id, True)

	println(
		"ApplyUISymbolMap: renamed=%d commented=%d skipped=%d" % (renamed, commented, skipped)
	)


main()
