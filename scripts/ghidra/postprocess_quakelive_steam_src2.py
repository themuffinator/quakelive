"""Post-process the generated quakelive_steam Ghidra source recreation.

This script upgrades the raw Ghidra export under ``src2/ghidra/quakelive_steam``
by:

1. mining exact signatures from the current hand-authored source tree when a
   function name is uniquely recoverable there,
2. normalizing the most common Ghidra placeholder integer types into
   fixed-width C++ names,
3. removing small decompiler-export formatting artifacts, and
4. running ``clang-format`` over the generated files.

Usage::

    py -3.11 scripts/ghidra/postprocess_quakelive_steam_src2.py \
        --repo-root E:\Repositories\QuakeLive-reverse \
        --output-root E:\Repositories\QuakeLive-reverse\src2\ghidra\quakelive_steam
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl"}
CONTROL_KEYWORDS = {"if", "for", "while", "switch", "return", "sizeof", "catch", "typedef"}
RAW_SYMBOL_TOKEN_RE = re.compile(r"\b(?P<token>(?:FUN|DAT|LAB|PTR)_[0-9A-Fa-f]{8})\b")
RAW_ALIAS_KEY_RE = re.compile(r"^(?P<prefix>sub|FUN|DAT|LAB|PTR)_(?P<address>[0-9A-Fa-f]+)$")
MAPPING_DOC_ALIAS_RE = re.compile(
	r"^-\s+`(?P<raw>(?:sub|FUN|DAT|LAB|PTR)_[0-9A-Fa-f]+)`\s+->\s+`(?P<name>[^`]+)`$"
)
ANALYSIS_SYMBOL_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]{8})\s+ANALYSIS\s+(?P<name>\S+)\s*$")
SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
TYPE_REPLACEMENTS = [
	("ulonglong", "std::uint64_t"),
	("longlong", "std::int64_t"),
	("undefined8", "std::uint64_t"),
	("undefined4", "std::uint32_t"),
	("undefined2", "std::uint16_t"),
	("undefined1", "std::uint8_t"),
	("undefined", "std::uint8_t"),
	("float10", "long double"),
	("ushort", "std::uint16_t"),
	("uchar", "std::uint8_t"),
	("ulong", "std::uint32_t"),
	("uint", "std::uint32_t"),
	("byte", "std::uint8_t"),
	("code", "void"),
]
CLANG_FORMAT_STYLE = (
	"{BasedOnStyle: LLVM, BreakBeforeBraces: Allman, ColumnLimit: 120, IndentWidth: 4, "
	"UseTab: Never, AllowShortBlocksOnASingleLine: Never, AllowShortFunctionsOnASingleLine: None, "
	"SortIncludes: Never, PointerAlignment: Left}"
)
CURATED_SYMBOL_REMAPS = {
	"FUN_004C9550": "_copyDWord",
	"FUN_004C95E0": "Com_Memset",
	"FUN_004C9AB0": "Com_DPrintf",
	"FUN_004CD250": "Cvar_Set",
	"FUN_0050B5D0": "png_format_buffer",
	"FUN_0050B7C0": "png_default_warning",
	"FUN_0050B940": "png_error",
	"FUN_0050BA00": "png_warning",
	"FUN_0050BA60": "png_chunk_error",
	"FUN_0050BAB0": "png_chunk_warning",
	"FUN_0050E3A0": "png_crc_error",
	"FUN_0050F4B0": "png_crc_finish",
	"FUN_00526F40": "oggpack_look",
}


@dataclass(frozen=True)
class SignatureCandidate:
	signature: str
	kind: str
	path: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument(
		"--repo-root",
		type=Path,
		default=Path(__file__).resolve().parents[2],
		help="Repository root (default: two levels above this script).",
	)
	parser.add_argument(
		"--output-root",
		type=Path,
		default=None,
		help="Generated quakelive_steam output root (default: <repo>/src2/ghidra/quakelive_steam).",
	)
	return parser.parse_args(argv)


def strip_comments(text: str) -> str:
	text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
	text = re.sub(r"//[^\n]*", "", text)
	return text


def count_paren_delta(text: str) -> int:
	return text.count("(") - text.count(")")


def normalize_signature(signature: str) -> str:
	signature = re.sub(r"\s+", " ", signature).strip()
	return signature.replace("( ", "(").replace(" )", ")")


def scan_signatures(path: Path) -> list[SignatureCandidate]:
	try:
		text = path.read_text(encoding="utf-8", errors="ignore")
	except OSError:
		return []

	lines = strip_comments(text).splitlines()
	candidates: list[SignatureCandidate] = []
	index = 0
	while index < len(lines):
		line = lines[index].strip()
		if not line or line.startswith("#") or "(" not in line:
			index += 1
			continue

		statement_lines = [line]
		depth = count_paren_delta(line)
		trailer = "{" if "{" in line else ";" if ";" in line else None
		next_index = index
		while trailer is None and next_index + 1 < len(lines):
			next_index += 1
			next_line = lines[next_index].strip()
			if next_line and not next_line.startswith("#"):
				statement_lines.append(next_line)
			depth += count_paren_delta(next_line)
			if depth <= 0:
				if "{" in next_line:
					trailer = "{"
				elif ";" in next_line:
					trailer = ";"

		index = next_index + 1
		if trailer is None:
			continue

		statement = normalize_signature(" ".join(statement_lines))
		cut = statement.rfind(trailer)
		if cut == -1:
			continue
		signature = normalize_signature(statement[:cut])
		if not signature or "(" not in signature:
			continue
		if signature.startswith(tuple(keyword + " " for keyword in CONTROL_KEYWORDS)):
			continue

		prefix = signature[: signature.find("(")].strip()
		if not prefix or "=" in prefix or "(*" in prefix:
			continue
		if len(prefix.split()) < 2:
			continue

		name_match = re.search(r"([A-Za-z_]\w*)\s*$", prefix)
		if not name_match:
			continue

		name = name_match.group(1)
		if name in CONTROL_KEYWORDS:
			continue

		candidates.append(SignatureCandidate(signature=signature, kind="definition" if trailer == "{" else "declaration", path=str(path)))

	return candidates


def build_signature_map(repo_root: Path) -> tuple[dict[str, str], dict[str, list[str]]]:
	signatures_by_name: dict[str, list[SignatureCandidate]] = defaultdict(list)

	for root in (repo_root / "src" / "code", repo_root / "src-re"):
		if not root.exists():
			continue
		for path in root.rglob("*"):
			if path.suffix.lower() not in SOURCE_SUFFIXES or not path.is_file():
				continue
			for candidate in scan_signatures(path):
				name_match = re.search(r"([A-Za-z_]\w*)\s*\(", candidate.signature)
				if name_match is None:
					continue
				signatures_by_name[name_match.group(1)].append(candidate)

	unique_signatures: dict[str, str] = {}
	ambiguous_names: dict[str, list[str]] = {}
	for name, candidates in signatures_by_name.items():
		best_rank = min(_candidate_rank(candidate.path) for candidate in candidates)
		best_candidates = [candidate for candidate in candidates if _candidate_rank(candidate.path) == best_rank]
		definition_sigs = sorted({candidate.signature for candidate in best_candidates if candidate.kind == "definition"})
		declaration_sigs = sorted({candidate.signature for candidate in best_candidates if candidate.kind == "declaration"})

		if len(definition_sigs) == 1:
			unique_signatures[name] = definition_sigs[0]
			continue
		if not definition_sigs and len(declaration_sigs) == 1:
			unique_signatures[name] = declaration_sigs[0]
			continue

		all_sigs = definition_sigs or declaration_sigs
		if len(all_sigs) > 1:
			ambiguous_names[name] = all_sigs

	return unique_signatures, ambiguous_names


def _candidate_rank(path: str) -> int:
	lower = path.replace("\\", "/").lower()
	if "/src/code/win32/" in lower:
		return 0
	if "/src/code/" in lower:
		return 1
	if "/src-re/" in lower:
		return 2
	return 3


def extract_signature_name(signature: str) -> str | None:
	match = re.search(r"([A-Za-z_]\w*)\s*\(", signature)
	return match.group(1) if match else None


def collect_raw_symbol_tokens(text: str) -> set[str]:
	return {match.group("token").upper() for match in RAW_SYMBOL_TOKEN_RE.finditer(text)}


def count_raw_symbol_occurrences(text: str, prefix: str) -> int:
	return len(re.findall(rf"\b{re.escape(prefix)}_[0-9A-Fa-f]{{8}}\b", text))


def normalize_raw_alias_key(raw_key: str) -> str | None:
	match = RAW_ALIAS_KEY_RE.fullmatch(raw_key)
	if match is None:
		return None

	prefix = match.group("prefix").upper()
	if prefix == "SUB":
		prefix = "FUN"

	address = match.group("address").upper().zfill(8)
	return f"{prefix}_{address}"


def is_safe_symbol_name(name: str) -> bool:
	return SAFE_IDENTIFIER_RE.fullmatch(name) is not None


def _iter_alias_entries(node: object) -> list[tuple[str, str]]:
	entries: list[tuple[str, str]] = []
	if isinstance(node, dict):
		for key, value in node.items():
			if isinstance(value, str):
				entries.append((key, value))
			else:
				entries.extend(_iter_alias_entries(value))
	return entries


def load_alias_corpus_symbols(repo_root: Path) -> dict[str, str]:
	alias_path = repo_root / "references" / "analysis" / "quakelive_symbol_aliases.json"
	if not alias_path.is_file():
		return {}

	try:
		payload = json.loads(alias_path.read_text(encoding="utf-8"))
	except (OSError, json.JSONDecodeError):
		return {}

	symbols: dict[str, str] = {}
	for raw_key, name in _iter_alias_entries(payload):
		token = normalize_raw_alias_key(raw_key)
		if token is None or not is_safe_symbol_name(name):
			continue
		symbols[token] = name

	return symbols


def load_mapping_doc_symbols(repo_root: Path) -> dict[str, str]:
	docs_root = repo_root / "docs" / "reverse-engineering"
	if not docs_root.is_dir():
		return {}

	symbols: dict[str, str] = {}
	for path in sorted(docs_root.glob("quakelive_steam_mapping_round_*.md")):
		try:
			lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
		except OSError:
			continue
		for line in lines:
			match = MAPPING_DOC_ALIAS_RE.fullmatch(line.strip())
			if match is None:
				continue
			token = normalize_raw_alias_key(match.group("raw"))
			name = match.group("name").strip()
			if token is None or not is_safe_symbol_name(name):
				continue
			symbols[token] = name

	return symbols


def load_analysis_symbols(repo_root: Path, present_tokens: set[str]) -> dict[str, str]:
	analysis_path = (
		repo_root / "references" / "reverse-engineering" / "ghidra" / "quakelive_steam_srp" / "analysis_symbols.txt"
	)
	if not analysis_path.is_file():
		return {}

	try:
		lines = analysis_path.read_text(encoding="utf-8", errors="ignore").splitlines()
	except OSError:
		return {}

	symbols: dict[str, str] = {}
	for line in lines:
		match = ANALYSIS_SYMBOL_RE.fullmatch(line.strip())
		if match is None:
			continue
		name = match.group("name").strip()
		if not is_safe_symbol_name(name):
			continue
		token = f"FUN_{match.group('address').upper()}"
		if token in present_tokens:
			symbols[token] = name

	return symbols


def build_symbol_map(
	repo_root: Path, present_tokens: set[str]
) -> tuple[dict[str, str], dict[str, int], dict[str, int], int]:
	source_maps = [
		("mapping_docs", load_mapping_doc_symbols(repo_root)),
		("alias_corpus", load_alias_corpus_symbols(repo_root)),
		("analysis_symbols", load_analysis_symbols(repo_root, present_tokens)),
		("curated", {token: name for token, name in CURATED_SYMBOL_REMAPS.items() if is_safe_symbol_name(name)}),
	]
	token_to_name: dict[str, str] = {}
	token_sources: dict[str, str] = {}
	conflicts = 0

	for source_name, source_map in source_maps:
		for token, name in source_map.items():
			existing = token_to_name.get(token)
			if existing is not None and existing != name:
				conflicts += 1
			token_to_name[token] = name
			token_sources[token] = source_name

	source_counts: dict[str, int] = defaultdict(int)
	applicable_counts: dict[str, int] = defaultdict(int)
	for token, source_name in token_sources.items():
		source_counts[source_name] += 1
		if token in present_tokens:
			applicable_counts[source_name] += 1

	return token_to_name, dict(sorted(source_counts.items())), dict(sorted(applicable_counts.items())), conflicts


def apply_symbol_replacements(text: str, symbol_map: dict[str, str]) -> tuple[str, int, dict[str, int]]:
	present_tokens = collect_raw_symbol_tokens(text)
	applicable_map = {token: name for token, name in symbol_map.items() if token in present_tokens}
	if not applicable_map:
		return text, 0, {}

	updated = text
	replacement_counts: dict[str, int] = {}
	for token, name in sorted(applicable_map.items()):
		updated, replacement_count = re.subn(rf"\b{re.escape(token)}\b", name, updated, flags=re.I)
		if replacement_count:
			replacement_counts[token] = replacement_count

	return updated, sum(replacement_counts.values()), replacement_counts


def replace_main_signatures(text: str, signature_map: dict[str, str]) -> tuple[str, int]:
	lines = text.splitlines()
	replaced = 0
	for index, line in enumerate(lines):
		stripped = line.strip()
		if not stripped or stripped.startswith("/*") or stripped.startswith("#") or "(" not in stripped:
			continue

		name = extract_signature_name(stripped)
		if not name or name not in signature_map:
			continue

		next_index = index + 1
		while next_index < len(lines) and not lines[next_index].strip():
			next_index += 1
		if next_index >= len(lines) or lines[next_index].strip() != "{":
			continue

		new_signature = signature_map[name]
		if lines[index].strip() != new_signature:
			lines[index] = new_signature
			replaced += 1

	return "\n".join(lines) + "\n", replaced


def replace_prototype_signatures(text: str, signature_map: dict[str, str]) -> tuple[str, int]:
	lines = text.splitlines()
	replaced = 0
	for index, line in enumerate(lines):
		stripped = line.strip()
		if not stripped or stripped.startswith("/*") or stripped.startswith("#") or "(" not in stripped or not stripped.endswith(";"):
			continue

		name = extract_signature_name(stripped.rstrip(";"))
		if not name or name not in signature_map:
			continue

		new_signature = signature_map[name].rstrip(";") + ";"
		if lines[index].strip() != new_signature:
			lines[index] = new_signature
			replaced += 1

	return "\n".join(lines) + "\n", replaced


def apply_type_replacements(text: str) -> tuple[str, dict[str, int]]:
	counts: dict[str, int] = {}
	updated = text
	for old, new in TYPE_REPLACEMENTS:
		pattern = re.compile(r"\b%s\b" % re.escape(old))
		updated, replacement_count = pattern.subn(new, updated)
		if replacement_count:
			counts[old] = replacement_count

	return updated, counts


def remove_export_artifacts(text: str) -> str:
	text = text.replace(";;", ";")
	text = re.sub(r"\n{4,}", "\n\n\n", text)
	return text


def run_clang_format(paths: list[Path]) -> None:
	command = ["clang-format", "-i", f"-style={CLANG_FORMAT_STYLE}"] + [str(path) for path in paths]
	subprocess.run(command, check=True)


def update_manifest(manifest_path: Path, payload: dict[str, object]) -> None:
	manifest: dict[str, object] = {}
	if manifest_path.exists():
		try:
			manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
		except json.JSONDecodeError:
			manifest = {}

	manifest.update(payload)
	manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)
	repo_root = args.repo_root.resolve()
	output_root = (args.output_root or (repo_root / "src2" / "ghidra" / "quakelive_steam_srp")).resolve()

	main_cpp = output_root / "quakelive_steam_decomp.cpp"
	compat_hpp = output_root / "include" / "quakelive_steam_ghidra_compat.hpp"
	proto_hpp = output_root / "include" / "quakelive_steam_prototypes.hpp"
	manifest_json = output_root / "quakelive_steam_manifest.json"

	for path in (main_cpp, compat_hpp, proto_hpp):
		if not path.is_file():
			print(f"ERROR: required generated file not found: {path}", file=sys.stderr)
			return 1

	signature_map, ambiguous_names = build_signature_map(repo_root)

	main_text = main_cpp.read_text(encoding="utf-8", errors="ignore")
	proto_text = proto_hpp.read_text(encoding="utf-8", errors="ignore")
	compat_text = compat_hpp.read_text(encoding="utf-8", errors="ignore")

	present_tokens = collect_raw_symbol_tokens(main_text) | collect_raw_symbol_tokens(proto_text)
	symbol_map, symbol_source_counts, applicable_symbol_source_counts, symbol_conflicts = build_symbol_map(
		repo_root, present_tokens
	)

	main_text, main_symbol_replacements, main_symbol_counts = apply_symbol_replacements(main_text, symbol_map)
	proto_text, proto_symbol_replacements, proto_symbol_counts = apply_symbol_replacements(proto_text, symbol_map)

	main_text, main_signature_replacements = replace_main_signatures(main_text, signature_map)
	proto_text, proto_signature_replacements = replace_prototype_signatures(proto_text, signature_map)

	main_text, main_type_counts = apply_type_replacements(main_text)
	proto_text, proto_type_counts = apply_type_replacements(proto_text)
	compat_text = remove_export_artifacts(compat_text)

	main_text = remove_export_artifacts(main_text)
	proto_text = remove_export_artifacts(proto_text)

	main_cpp.write_text(main_text, encoding="utf-8")
	proto_hpp.write_text(proto_text, encoding="utf-8")
	compat_hpp.write_text(compat_text, encoding="utf-8")

	run_clang_format([main_cpp, proto_hpp, compat_hpp])

	combined_type_counts = defaultdict(int)
	for mapping in (main_type_counts, proto_type_counts):
		for key, value in mapping.items():
			combined_type_counts[key] += value

	applied_symbol_tokens = set(main_symbol_counts) | set(proto_symbol_counts)
	post_main_present_tokens = collect_raw_symbol_tokens(main_text)
	post_proto_present_tokens = collect_raw_symbol_tokens(proto_text)

	update_manifest(
		manifest_json,
		{
			"postprocess": {
				"symbol_candidate_count": len(symbol_map),
				"symbol_conflict_count": symbol_conflicts,
				"symbol_source_counts": symbol_source_counts,
				"applicable_symbol_source_counts": applicable_symbol_source_counts,
				"applied_symbol_token_count": len(applied_symbol_tokens),
				"main_symbol_replacements": main_symbol_replacements,
				"prototype_symbol_replacements": proto_symbol_replacements,
				"signature_candidate_count": len(signature_map),
				"ambiguous_signature_name_count": len(ambiguous_names),
				"main_signature_replacements": main_signature_replacements,
				"prototype_signature_replacements": proto_signature_replacements,
				"remaining_raw_function_token_count": sum(
					1 for token in (post_main_present_tokens | post_proto_present_tokens) if token.startswith("FUN_")
				),
				"remaining_raw_data_token_count": sum(
					1 for token in (post_main_present_tokens | post_proto_present_tokens) if token.startswith("DAT_")
				),
				"remaining_raw_label_token_count": sum(
					1 for token in (post_main_present_tokens | post_proto_present_tokens) if token.startswith("LAB_")
				),
				"type_replacements": dict(sorted(combined_type_counts.items())),
				"clang_format_style": CLANG_FORMAT_STYLE,
				"source_roots": [
					str((repo_root / "src" / "code").resolve()),
					str((repo_root / "src-re").resolve()),
				],
			}
		},
	)

	print(
		"postprocess_quakelive_steam_src2: "
		f"symbol_candidates={len(symbol_map)} "
		f"applied_symbol_tokens={len(applied_symbol_tokens)} "
		f"main_symbol_replacements={main_symbol_replacements} "
		f"prototype_symbol_replacements={proto_symbol_replacements} "
		f"signature_candidates={len(signature_map)} "
		f"ambiguous_names={len(ambiguous_names)} "
		f"main_signature_replacements={main_signature_replacements} "
		f"prototype_signature_replacements={proto_signature_replacements}"
	)
	return 0


if __name__ == "__main__":
	sys.exit(main())
