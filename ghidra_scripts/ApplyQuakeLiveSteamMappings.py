# Apply committed quakelive_steam.exe aliases and analysis symbols to a Ghidra project.
#@author QuakeLive-reverse
#@category QuakeLive/Host
#@menupath Tools.QuakeLive.Apply quakelive_steam Mappings
#@toolbar

"""Apply the committed quakelive_steam.exe naming corpus to the current program.

The script combines:

1. ``references/analysis/quakelive_symbol_aliases.json`` ``quakelive_steam``
   aliases for recovered function-level names.
2. ``references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt``
   labels for switch cases, RTTI, globals, and other non-function symbols.

Run via the Ghidra GUI or headless::

    analyzeHeadless <project_dir> <project_name> \
        -process quakelive_steam.exe \
        -postScript ApplyQuakeLiveSteamMappings.py \
        [<alias_json>] [<analysis_symbols_txt>]
"""

import json
import os
import re

from ghidra.program.model.symbol import SourceType


_ADDRESS_KEY_RE = re.compile(r"(?:^|_)([0-9A-Fa-f]{6,8})$")
_DEFAULT_NAME_RE = re.compile(r"^(?:FUN_[0-9A-Fa-f]+|sub_[0-9A-Fa-f]+|j_sub_[0-9A-Fa-f]+)$")
_ANALYSIS_LABEL_RE = re.compile(
	r"^(?:switchD_|caseD_|switchdataD_|Catch_|LAB_|DAT_|PTR_|UNK_)",
	re.IGNORECASE,
)


def _parse_address_from_key(key):
	match = _ADDRESS_KEY_RE.search(key or "")
	if not match:
		return None
	return int(match.group(1), 16)


def _normalize_symbol_name(name):
	return (name or "").strip()


def _set_primary_label(symbol_table, address, name):
	symbol = symbol_table.getPrimarySymbol(address)
	if symbol is not None:
		if symbol.getName() != name:
			try:
				symbol.setName(name, SourceType.USER_DEFINED)
				return 1, 0
			except Exception:
				return 0, 0
		return 0, 0

	try:
		new_symbol = symbol_table.createLabel(address, name, SourceType.USER_DEFINED)
		new_symbol.setPrimary()
		return 0, 1
	except Exception:
		return 0, 0


def _ensure_non_primary_label(symbol_table, address, name):
	for symbol in symbol_table.getSymbols(address):
		if symbol.getName() == name:
			return 0

	primary_symbol = symbol_table.getPrimarySymbol(address)
	try:
		new_symbol = symbol_table.createLabel(address, name, SourceType.USER_DEFINED)
		if primary_symbol is not None:
			primary_symbol.setPrimary()
		else:
			new_symbol.setPrimary()
		return 1
	except Exception:
		return 0


def _rename_function_if_default(func, desired_name):
	current_name = func.getName()
	if current_name == desired_name:
		return 0
	if not _DEFAULT_NAME_RE.match(current_name):
		return 0

	try:
		func.setName(desired_name, SourceType.USER_DEFINED)
		return 1
	except Exception:
		return 0


def _load_alias_bucket(alias_path):
	with open(alias_path, "r") as handle:
		alias_data = json.load(handle)
	return alias_data.get("quakelive_steam_srp", {}) or {}


def _iter_analysis_symbols(analysis_path):
	with open(analysis_path, "r") as handle:
		for raw_line in handle:
			line = raw_line.strip()
			if not line or line.startswith("#"):
				continue

			parts = line.split(None, 2)
			if len(parts) != 3:
				continue

			try:
				address = int(parts[0], 16)
			except ValueError:
				continue

			yield address, parts[1], parts[2].strip()


def main():
	program = currentProgram
	if program is None:
		printerr("No program is active; aborting")
		return

	script_dir = os.path.dirname(os.path.abspath(str(sourceFile)))
	repo_root = os.path.dirname(script_dir)
	default_alias_path = os.path.join(
		repo_root,
		"references",
		"analysis",
		"quakelive_symbol_aliases.json",
	)
	default_analysis_path = os.path.join(
		repo_root,
		"references",
		"reverse-engineering",
		"ghidra",
		"quakelive_steam_srp",
		"analysis_symbols.txt",
	)

	args = list(getScriptArgs())
	alias_path = args[0] if args else default_alias_path
	analysis_path = args[1] if len(args) > 1 else default_analysis_path

	if not os.path.isfile(alias_path):
		printerr("Alias file not found: %s" % alias_path)
		return
	if not os.path.isfile(analysis_path):
		printerr("Analysis symbol file not found: %s" % analysis_path)
		return

	alias_bucket = _load_alias_bucket(alias_path)
	addr_factory = program.getAddressFactory()
	func_manager = program.getFunctionManager()
	symbol_table = program.getSymbolTable()

	alias_function_renames = 0
	alias_label_updates = 0
	alias_label_creates = 0
	analysis_function_renames = 0
	analysis_label_creates = 0
	skipped_aliases = 0

	transaction_id = program.startTransaction("Apply quakelive_steam mappings")
	try:
		for raw_name, desired_name in sorted(alias_bucket.items()):
			desired_name = _normalize_symbol_name(desired_name)
			if not desired_name:
				skipped_aliases += 1
				continue

			address_value = _parse_address_from_key(raw_name)
			if address_value is None:
				skipped_aliases += 1
				continue

			address = addr_factory.getAddress("0x%08X" % address_value)
			if address is None:
				skipped_aliases += 1
				continue

			func = func_manager.getFunctionAt(address)
			if func is not None:
				alias_function_renames += _rename_function_if_default(func, desired_name)

			updated, created = _set_primary_label(symbol_table, address, desired_name)
			alias_label_updates += updated
			alias_label_creates += created

		for address_value, _symbol_kind, name in _iter_analysis_symbols(analysis_path):
			name = _normalize_symbol_name(name)
			if not name:
				continue

			address = addr_factory.getAddress("0x%08X" % address_value)
			if address is None:
				continue

			analysis_label_creates += _ensure_non_primary_label(symbol_table, address, name)

			func = func_manager.getFunctionAt(address)
			if func is None or _ANALYSIS_LABEL_RE.match(name):
				continue

			analysis_function_renames += _rename_function_if_default(func, name)
	finally:
		program.endTransaction(transaction_id, True)

	println(
		"ApplyQuakeLiveSteamMappings: alias_function_renames=%d alias_label_updates=%d "
		"alias_label_creates=%d analysis_function_renames=%d analysis_label_creates=%d "
		"skipped_aliases=%d"
		% (
			alias_function_renames,
			alias_label_updates,
			alias_label_creates,
			analysis_function_renames,
			analysis_label_creates,
			skipped_aliases,
		)
	)


main()
