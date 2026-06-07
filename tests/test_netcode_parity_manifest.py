from __future__ import annotations

import json
import ctypes
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "docs/reverse-engineering/netcode-parity-manifest.json"
NETWORKING_2_LEDGER_PATH = REPO_ROOT / "docs/reverse-engineering/network-protocol-parity-ledger-2026-06-05.json"
NETWORKING_2_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-protocol-parity-ledger-2026-06-05.md"
NETWORKING_2_HEADER_SPEC_PATH = REPO_ROOT / "docs/reverse-engineering/network-protocol-header-transport-spec-2026-06-05.json"
NETWORKING_2_HEADER_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-protocol-header-transport-spec-2026-06-05.md"
NETWORKING_2_CLIENT_PARSER_GRAMMAR_PATH = REPO_ROOT / "docs/reverse-engineering/network-client-message-parser-grammar-2026-06-05.json"
NETWORKING_2_CLIENT_PARSER_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-client-message-parser-grammar-2026-06-05.md"
NETWORKING_2_XOR_CODEC_PATH = REPO_ROOT / "docs/reverse-engineering/network-xor-codec-parity-2026-06-05.json"
NETWORKING_2_XOR_CODEC_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-xor-codec-parity-2026-06-05.md"
NETWORKING_2_CLIENT_SIDEBAND_PRODUCERS_PATH = REPO_ROOT / "docs/reverse-engineering/network-client-message-sideband-producers-2026-06-05.json"
NETWORKING_2_CLIENT_SIDEBAND_PRODUCERS_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-client-message-sideband-producers-2026-06-05.md"
NETWORKING_2_USERCMD_DELTA_PATH = REPO_ROOT / "docs/reverse-engineering/network-usercmd-delta-parity-2026-06-05.json"
NETWORKING_2_USERCMD_DELTA_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-usercmd-delta-parity-2026-06-05.md"
NETWORKING_2_PLAYERSTATE_FIELDS_PATH = REPO_ROOT / "docs/reverse-engineering/network-playerstate-fields-parity-2026-06-05.json"
NETWORKING_2_PLAYERSTATE_FIELDS_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-playerstate-fields-parity-2026-06-05.md"
NETWORKING_2_ENTITYSTATE_FIELDS_PATH = REPO_ROOT / "docs/reverse-engineering/network-entitystate-fields-parity-2026-06-05.json"
NETWORKING_2_ENTITYSTATE_FIELDS_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-entitystate-fields-parity-2026-06-05.md"
NETWORKING_2_OOB_CONNECT_AUTH_PATH = REPO_ROOT / "docs/reverse-engineering/network-oob-connect-auth-parity-2026-06-05.json"
NETWORKING_2_OOB_CONNECT_AUTH_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-oob-connect-auth-parity-2026-06-05.md"
NETWORKING_2_HUFFMAN_FIXTURES_PATH = REPO_ROOT / "docs/reverse-engineering/network-adaptive-huffman-fixtures-2026-06-05.json"
NETWORKING_2_HUFFMAN_FIXTURES_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-adaptive-huffman-fixtures-2026-06-05.md"
NETWORKING_2_REPLAY_VALIDATION_PATH = REPO_ROOT / "docs/reverse-engineering/network-demo-capture-replay-validation-2026-06-05.json"
NETWORKING_2_REPLAY_VALIDATION_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-demo-capture-replay-validation-2026-06-05.md"
NETWORKING_2_HARDENING_PATH = REPO_ROOT / "docs/reverse-engineering/network-protocol-hardening-parity-2026-06-05.json"
NETWORKING_2_HARDENING_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-protocol-hardening-parity-2026-06-05.md"
NETWORKING_2_CAPTURE_DIFF_TOOLING_PATH = REPO_ROOT / "docs/reverse-engineering/network-capture-diff-tooling-2026-06-05.json"
NETWORKING_2_CAPTURE_DIFF_TOOLING_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-capture-diff-tooling-2026-06-05.md"
NETWORKING_2_CAPTURE_EVIDENCE_BUNDLE_VALIDATION_PATH = REPO_ROOT / "docs/reverse-engineering/network-capture-evidence-bundle-validation-2026-06-05.json"
NETWORKING_2_CAPTURE_EVIDENCE_BUNDLE_VALIDATION_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-capture-evidence-bundle-validation-2026-06-05.md"
NETWORKING_2_FRAGMENT_QUEUE_TIMING_VALIDATION_PATH = REPO_ROOT / "docs/reverse-engineering/network-fragment-queue-timing-validation-2026-06-05.json"
NETWORKING_2_FRAGMENT_QUEUE_TIMING_VALIDATION_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-fragment-queue-timing-validation-2026-06-05.md"
NETWORKING_2_INVALID_LC_PROBE_VALIDATION_PATH = REPO_ROOT / "docs/reverse-engineering/network-invalid-lc-probe-validation-2026-06-05.json"
NETWORKING_2_INVALID_LC_PROBE_VALIDATION_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-invalid-lc-probe-validation-2026-06-05.md"
NETWORKING_2_SNAPSHOT_FIELD_DECODE_VALIDATION_PATH = REPO_ROOT / "docs/reverse-engineering/network-snapshot-field-decode-validation-2026-06-05.json"
NETWORKING_2_SNAPSHOT_FIELD_DECODE_VALIDATION_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-snapshot-field-decode-validation-2026-06-05.md"
NETWORKING_2_CAPTURE_FIXTURE_VALIDATION_PATH = REPO_ROOT / "docs/reverse-engineering/network-capture-fixture-validation-2026-06-05.json"
NETWORKING_2_CAPTURE_FIXTURE_VALIDATION_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-capture-fixture-validation-2026-06-05.md"
NETWORKING_2_DEMO_TRANSCRIPT_INTAKE_PATH = REPO_ROOT / "docs/reverse-engineering/network-demo-transcript-intake-2026-06-05.json"
NETWORKING_2_DEMO_TRANSCRIPT_INTAKE_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-demo-transcript-intake-2026-06-05.md"
NETWORKING_2_CAPTURE_BLOCKERS_PATH = REPO_ROOT / "docs/reverse-engineering/network-residual-capture-blockers-2026-06-05.json"
NETWORKING_2_CAPTURE_BLOCKERS_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-residual-capture-blockers-2026-06-05.md"
NETWORK_BROWSER_HEARTBEAT_AUDIT_PATH = (
	REPO_ROOT / "docs/reverse-engineering/network-server-browser-master-heartbeat-parity-2026-06-05.md"
)
NETWORKING_2_PLAN_PATH = REPO_ROOT / "docs/plans/2026-06-05-networking-2.md"
OUTSTANDING_WORK_CHECKLIST_PATH = REPO_ROOT / "docs/plans/2026-06-05-outstanding-work-checklist.md"
RESIDUAL_POLICY_SPOT_CHECK_PATH = REPO_ROOT / "docs/reverse-engineering/residual-policy-spot-check-2026-06-05.json"
RESIDUAL_POLICY_SPOT_CHECK_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/residual-policy-spot-check-2026-06-05.md"
UI_OWNERDRAWTYPE_PARITY_INDEX_PATH = REPO_ROOT / "docs/reverse-engineering/ui-ownerdrawtype-parity-index.md"
PLATFORM_CONFIG_PATH = REPO_ROOT / "src/common/platform/platform_config.h"
PLATFORM_SERVICES_PATH = REPO_ROOT / "src/common/platform/platform_services.c"
QCOMMON_H_PATH = REPO_ROOT / "src/code/qcommon/qcommon.h"
Q_SHARED_PATH = REPO_ROOT / "src/code/game/q_shared.h"
HUFFMAN_C_PATH = REPO_ROOT / "src/code/qcommon/huffman.c"
MSG_C_PATH = REPO_ROOT / "src/code/qcommon/msg.c"
SV_SNAPSHOT_PATH = REPO_ROOT / "src/code/server/sv_snapshot.c"
SV_BOT_PATH = REPO_ROOT / "src/code/server/sv_bot.c"
SV_GAME_PATH = REPO_ROOT / "src/code/server/sv_game.c"
SV_MAIN_PATH = REPO_ROOT / "src/code/server/sv_main.c"
G_SYSCALLS_PATH = REPO_ROOT / "src/code/game/g_syscalls.c"
G_PUBLIC_PATH = REPO_ROOT / "src/code/game/g_public.h"
AI_MAIN_PATH = REPO_ROOT / "src/code/game/ai_main.c"
CL_INPUT_PATH = REPO_ROOT / "src/code/client/cl_input.c"
CL_CGAME_PATH = REPO_ROOT / "src/code/client/cl_cgame.c"
CL_MAIN_PATH = REPO_ROOT / "src/code/client/cl_main.c"
CLIENT_H_PATH = REPO_ROOT / "src/code/client/client.h"
CG_PUBLIC_PATH = REPO_ROOT / "src/code/cgame/cg_public.h"
TR_PUBLIC_PATH = REPO_ROOT / "src/code/renderer/tr_public.h"
TR_CMDS_PATH = REPO_ROOT / "src/code/renderer/tr_cmds.c"
CL_PARSE_PATH = REPO_ROOT / "src/code/client/cl_parse.c"
CL_NET_CHAN_PATH = REPO_ROOT / "src/code/client/cl_net_chan.c"
SV_CLIENT_PATH = REPO_ROOT / "src/code/server/sv_client.c"
SV_NET_CHAN_PATH = REPO_ROOT / "src/code/server/sv_net_chan.c"
SERVER_H_PATH = REPO_ROOT / "src/code/server/server.h"
NET_CHAN_PATH = REPO_ROOT / "src/code/qcommon/net_chan.c"
COMMON_C_PATH = REPO_ROOT / "src/code/qcommon/common.c"
WIN_NET_PATH = REPO_ROOT / "src/code/win32/win_net.c"
GHIDRA_FUNCTIONS_PATH = REPO_ROOT / "references/reverse-engineering/ghidra/quakelive_steam/functions.csv"
GHIDRA_DECOMPILE_TOP_PATH = REPO_ROOT / "references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c"
HLIL_PART02_PATH = (
	REPO_ROOT
	/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt"
)
HLIL_PART04_PATH = (
	REPO_ROOT
	/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt"
)
HLIL_PART05_PATH = (
	REPO_ROOT
	/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt"
)
HLIL_PART06_PATH = (
	REPO_ROOT
	/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt"
)
HLIL_PART07_PATH = (
	REPO_ROOT
	/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt"
)
PLAN_PATH = REPO_ROOT / "docs/plans/2026-06-04-networking.md"
NETCODE_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/engine-netcode-parity-audit-2026-04-16.md"
NETWORKING_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/networking-parity-audit-2026-05-24.md"
NETWORK_HANDSHAKE_PATH = REPO_ROOT / "docs/reverse-engineering/network-handshake.md"


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _manifest() -> dict:
	return json.loads(_read(MANIFEST_PATH))


def _networking_2_ledger() -> dict:
	return json.loads(_read(NETWORKING_2_LEDGER_PATH))


def _networking_2_header_spec() -> dict:
	return json.loads(_read(NETWORKING_2_HEADER_SPEC_PATH))


def _networking_2_client_parser_grammar() -> dict:
	return json.loads(_read(NETWORKING_2_CLIENT_PARSER_GRAMMAR_PATH))


def _networking_2_xor_codec_spec() -> dict:
	return json.loads(_read(NETWORKING_2_XOR_CODEC_PATH))


def _networking_2_client_sideband_producers_spec() -> dict:
	return json.loads(_read(NETWORKING_2_CLIENT_SIDEBAND_PRODUCERS_PATH))


def _networking_2_usercmd_delta_spec() -> dict:
	return json.loads(_read(NETWORKING_2_USERCMD_DELTA_PATH))


def _networking_2_playerstate_fields_spec() -> dict:
	return json.loads(_read(NETWORKING_2_PLAYERSTATE_FIELDS_PATH))


def _networking_2_entitystate_fields_spec() -> dict:
	return json.loads(_read(NETWORKING_2_ENTITYSTATE_FIELDS_PATH))


def _networking_2_oob_connect_auth_spec() -> dict:
	return json.loads(_read(NETWORKING_2_OOB_CONNECT_AUTH_PATH))


def _networking_2_huffman_fixtures_spec() -> dict:
	return json.loads(_read(NETWORKING_2_HUFFMAN_FIXTURES_PATH))


def _networking_2_replay_validation_spec() -> dict:
	return json.loads(_read(NETWORKING_2_REPLAY_VALIDATION_PATH))


def _networking_2_hardening_spec() -> dict:
	return json.loads(_read(NETWORKING_2_HARDENING_PATH))


def _networking_2_capture_fixture_validation_spec() -> dict:
	return json.loads(_read(NETWORKING_2_CAPTURE_FIXTURE_VALIDATION_PATH))


def _networking_2_capture_diff_tooling_spec() -> dict:
	return json.loads(_read(NETWORKING_2_CAPTURE_DIFF_TOOLING_PATH))


def _networking_2_capture_evidence_bundle_validation_spec() -> dict:
	return json.loads(_read(NETWORKING_2_CAPTURE_EVIDENCE_BUNDLE_VALIDATION_PATH))


def _networking_2_fragment_queue_timing_validation_spec() -> dict:
	return json.loads(_read(NETWORKING_2_FRAGMENT_QUEUE_TIMING_VALIDATION_PATH))


def _networking_2_invalid_lc_probe_validation_spec() -> dict:
	return json.loads(_read(NETWORKING_2_INVALID_LC_PROBE_VALIDATION_PATH))


def _networking_2_snapshot_field_decode_validation_spec() -> dict:
	return json.loads(_read(NETWORKING_2_SNAPSHOT_FIELD_DECODE_VALIDATION_PATH))


def _networking_2_demo_transcript_intake_spec() -> dict:
	return json.loads(_read(NETWORKING_2_DEMO_TRANSCRIPT_INTAKE_PATH))


def _networking_2_capture_blockers_spec() -> dict:
	return json.loads(_read(NETWORKING_2_CAPTURE_BLOCKERS_PATH))


def _residual_policy_spot_check_spec() -> dict:
	return json.loads(_read(RESIDUAL_POLICY_SPOT_CHECK_PATH))


def _ql_reliable_xor(data: bytes, start: int, initial_key: int, command_bytes: bytes) -> bytes:
	out = bytearray(data)
	key = initial_key & 0xff
	index = 0

	if not command_bytes:
		command_bytes = b"\x00"

	for offset in range(start, len(out)):
		command_byte = command_bytes[index] if index < len(command_bytes) else 0
		if command_byte == 0:
			index = 0
			command_byte = command_bytes[index] if index < len(command_bytes) else 0
		if command_byte > 0x7f or command_byte == ord("%"):
			command_byte = ord(".")

		key = (key ^ ((command_byte << (offset & 1)) & 0xff)) & 0xff
		out[offset] ^= key
		index += 1

	return bytes(out)


def _entry(symbol: str) -> dict:
	for item in _manifest()["entries"]:
		if item["symbol"] == symbol:
			return item
	raise AssertionError(f"missing manifest entry: {symbol}")


def _netfield_count(source: str, table_name: str) -> int:
	start = source.index(f"netField_t\t{table_name}[]")
	table = source[start:source.index("};", start)]
	macro = "PSF(" if table_name == "playerStateFields" else "NETF("
	return table.count("{ " + macro)


def _msg_t_block(source: str) -> str:
	return source.split("typedef struct {", 1)[1].split("} msg_t;", 1)[0]


def _netchan_t_block(source: str) -> str:
	start = source.find("typedef struct {\n\tnetsrc_t\tsock;")
	if start == -1:
		raise AssertionError("netchan_t structure start not found")
	return source[start:].split("} netchan_t;", 1)[0]


def _function_block(source: str, signature: str) -> str:
	start = source.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = source.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	in_string = False
	escaped = False

	for index in range(brace_start, len(source)):
		char = source[index]
		if in_string:
			if escaped:
				escaped = False
			elif char == "\\":
				escaped = True
			elif char == '"':
				in_string = False
			continue

		if char == '"':
			in_string = True
		elif char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def _assert_order(block: str, *needles: str) -> None:
	cursor = 0
	for needle in needles:
		index = block.find(needle, cursor)
		if index == -1:
			raise AssertionError(f"expected ordered snippet not found after {cursor}: {needle}")
		cursor = index + len(needle)


def test_compact_msg_t_layout_matches_hlil_wrapper_layer() -> None:
	qcommon_h = _read(QCOMMON_H_PATH)
	msg_c = _read(MSG_C_PATH)
	sv_snapshot = _read(SV_SNAPSHOT_PATH)
	hlil = _read(HLIL_PART04_PATH)
	plan = _read(PLAN_PATH)
	manifest = _manifest()
	msg_entry = _entry("msg_t")

	assert manifest["reference_profile"]["protocol"] == 91
	assert msg_entry["status"] == "verified"
	assert "no distinct allowoverflow field survives" in " ".join(msg_entry["behavior_checkpoints"])

	msg_t_block = _msg_t_block(qcommon_h)
	assert "allowoverflow" not in msg_t_block
	assert "qboolean\toverflowed;" in msg_t_block
	assert "qboolean\toob;" in msg_t_block
	assert msg_t_block.index("qboolean\toverflowed;") < msg_t_block.index("qboolean\toob;")
	assert msg_t_block.index("qboolean\toob;") < msg_t_block.index("byte\t*data;")
	assert msg_t_block.index("byte\t*data;") < msg_t_block.index("int\t\tmaxsize;")
	assert msg_t_block.index("int\t\tmaxsize;") < msg_t_block.index("int\t\tcursize;")
	assert msg_t_block.index("int\t\tcursize;") < msg_t_block.index("int\t\treadcount;")
	assert msg_t_block.index("int\t\treadcount;") < msg_t_block.index("int\t\tbit;")

	assert "buf->overflowed = qfalse;" in msg_c
	assert "msg->overflowed = qtrue;" in msg_c
	assert "Com_Memcpy(buf, src, sizeof(msg_t));" in msg_c
	assert ".allowoverflow" not in sv_snapshot

	assert "004d4ac6  sub_4cb7d0(arg1, arg4, 0x1c)" in hlil
	assert "004d4a50    int32_t* sub_4d4a50(int32_t* arg1)" in hlil
	round_56 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_56.md")
	assert "compact retail\n   `msg_t` setup helpers" in round_56
	assert "`allowoverflow` field from the GPL source no longer survives" in round_56
	assert "Implementation round - 2026-06-04, compact `msg_t` and netchan manifest seed" in plan


def test_manifest_covers_protocol_profile_and_token_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	qcommon_h = _read(QCOMMON_H_PATH)
	common_c = _read(COMMON_C_PATH)
	net_chan = _read(NET_CHAN_PATH)
	cl_main = _read(CL_MAIN_PATH)
	cl_parse = _read(CL_PARSE_PATH)
	cl_net_chan = _read(CL_NET_CHAN_PATH)
	sv_main = _read(SV_MAIN_PATH)
	sv_client = _read(SV_CLIENT_PATH)
	sv_net_chan = _read(SV_NET_CHAN_PATH)
	plan = _read(PLAN_PATH)
	audit = _read(NETCODE_AUDIT_PATH)
	round_290 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_290.md")

	for symbol in (
		"netprofile_desc_t",
		"s_netProtocolProfile",
		"NET_ProtocolCoreAccessors",
		"NET_ProfileCommandAccessors",
		"NET_ProfileCommandPredicates",
		"NET_IsConnectRequestPacket",
		"NET_ProtocolFeatureGates",
	):
		assert entries[symbol]["status"] == "reconstructed"
		assert entries[symbol]["retail_address"] is None
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_protocol_profile_and_token_lane" in entries[symbol]["tests"]

	assert "source reconstruction layer around retail-observed constants" in entries["netprofile_desc_t"]["compatibility_notes"][0]
	assert "build-gated" in entries["s_netProtocolProfile"]["compatibility_notes"][0]
	assert "source reconstruction helper introduced to identify retail compressed connect OOB payloads" in entries["NET_IsConnectRequestPacket"]["compatibility_notes"][0]

	for expected in (
		"#define\tQL_RETAIL_PROTOCOL_VERSION\t91",
		"#define\tPROTOCOL_VERSION\tQL_RETAIL_PROTOCOL_VERSION",
		"NETPROFILE_QL_RETAIL",
		"} netprofile_desc_t;",
		"const char\t\t*getChallengeCommand;",
		"const char\t\t*challengeResponseCommand;",
		"const char\t\t*connectCommand;",
		"const char\t\t*connectResponseCommand;",
		"const char\t\t*downloadCommand;",
		"const char\t\t*nextDownloadCommand;",
		"const char\t\t*stopDownloadCommand;",
		"const char\t\t*doneDownloadCommand;",
		"const char\t\t*userinfoCommand;",
		"const char\t\t*reliableDisconnectCommand;",
		"const char\t\t*protocolInfoKey;",
		"const char\t\t*qportInfoKey;",
		"const char\t\t*challengeInfoKey;",
		"int\t\t\t\tconnectProtocol;",
		"int\t\t\t\tdemoProtocol;",
		"qboolean\t\tusesChallengeHandshake;",
		"qboolean\t\tusesClientQport;",
		"qboolean\t\tusesNetchanClientQport;",
		"qboolean\t\tusesReliableXorCodec;",
		"qboolean\t\tusesCompressedConnect;",
		"qboolean\t\tusesLegacyQ3Authorize;",
		"qboolean\t\tsupportsPlatformAuth;",
		"qboolean\t\trequiresPlatformAuth;",
		"qboolean\t\tsupportsWorkshopContent;",
		"const netprofile_desc_t *NET_GetProtocolProfile( void );",
		"qboolean NET_IsConnectRequestPacket( const msg_t *msg );",
		"qboolean NET_ProtocolUsesReliableXorCodec( void );",
		"qboolean NET_ProtocolSupportsPlatformAuth( void );",
	):
		assert expected in qcommon_h

	profile_block = common_c.split("static const netprofile_desc_t s_netProtocolProfile = {", 1)[1].split("\n};", 1)[0]
	_assert_order(
		profile_block,
		"NETPROFILE_QL_RETAIL,",
		"\"ql-retail-steam\",",
		"\"getchallenge\",",
		"\"challengeResponse\",",
		"\"connect\",",
		"\"connectResponse\",",
		"\"getinfo\",",
		"\"infoResponse\",",
		"\"getstatus\",",
		"\"statusResponse\",",
		"\"disconnect\",",
		"\"print\",",
		"\"echo\",",
		"\"rcon\",",
		"\"getservers\",",
		"\"getserversResponse\",",
		"\"getmotd\",",
		"\"motd\",",
		"\"getKeyAuthorize\",",
		"\"keyAuthorize\",",
		"\"getIpAuthorize\",",
		"\"ipAuthorize\",",
		"\"heartbeat\",",
		"\"QuakeArena-1\",",
		"\"download\",",
		"\"nextdl\",",
		"\"stopdl\",",
		"\"donedl\",",
		"\"cp\",",
		"\"Yf\",",
		"\"vdr\",",
		"\"userinfo\",",
		"\"disconnect\",",
		"\"protocol\",",
		"\"qport\",",
		"\"challenge\",",
		"\"sv_serverid\",",
		"\"sv_cheats\",",
		"\"sv_paks\",",
		"\"sv_pakNames\",",
		"\"sv_referencedPaks\",",
		"\"sv_referencedPakNames\",",
		"\"fs_game\",",
		"\"sv_pure\",",
		"QL_RETAIL_PROTOCOL_VERSION,",
		"QL_RETAIL_PROTOCOL_VERSION,",
		"qtrue,",
		"qtrue,",
		"qtrue,",
		"qtrue,",
		"qtrue,",
		"qfalse,",
		"NET_PROFILE_SUPPORTS_PLATFORM_AUTH,",
		"qfalse,",
		"NET_PROFILE_SUPPORTS_WORKSHOP_CONTENT",
	)

	_assert_order(
		_function_block(common_c, "const netprofile_desc_t *NET_GetProtocolProfile( void )"),
		"return &s_netProtocolProfile;",
	)
	assert "return NET_GetProtocolProfile()->name;" in _function_block(common_c, "const char *NET_ProtocolName( void )")
	assert "return NET_GetProtocolProfile()->connectProtocol;" in _function_block(common_c, "int NET_ProtocolVersion( void )")
	assert "return NET_GetProtocolProfile()->demoProtocol;" in _function_block(common_c, "int NET_DemoProtocol( void )")
	assert "return ( protocol == NET_GetProtocolProfile()->connectProtocol ) ? qtrue : qfalse;" in _function_block(
		common_c, "qboolean NET_ProtocolSupports( int protocol )"
	)

	for signature, field in (
		("const char *NET_GetChallengeRequestCommand( void )", "getChallengeCommand"),
		("const char *NET_GetChallengeResponseCommand( void )", "challengeResponseCommand"),
		("const char *NET_GetConnectRequestCommand( void )", "connectCommand"),
		("const char *NET_GetConnectResponseCommand( void )", "connectResponseCommand"),
		("const char *NET_GetDownloadRequestCommand( void )", "downloadCommand"),
		("const char *NET_GetDownloadNextCommand( void )", "nextDownloadCommand"),
		("const char *NET_GetDownloadStopCommand( void )", "stopDownloadCommand"),
		("const char *NET_GetDownloadDoneCommand( void )", "doneDownloadCommand"),
		("const char *NET_GetUserinfoCommand( void )", "userinfoCommand"),
		("const char *NET_GetReliableDisconnectCommand( void )", "reliableDisconnectCommand"),
		("const char *NET_GetProtocolInfoKey( void )", "protocolInfoKey"),
		("const char *NET_GetQportInfoKey( void )", "qportInfoKey"),
		("const char *NET_GetChallengeInfoKey( void )", "challengeInfoKey"),
		("const char *NET_GetServerIdInfoKey( void )", "serverIdInfoKey"),
		("const char *NET_GetFsGameInfoKey( void )", "fsGameInfoKey"),
		("const char *NET_GetSystemPureInfoKey( void )", "systemPureInfoKey"),
	):
		assert f"return NET_GetProtocolProfile()->{field};" in _function_block(common_c, signature)

	matches = _function_block(common_c, "static qboolean NET_CommandMatchesProfileToken( const char *command, const char *profileCommand )")
	_assert_order(
		matches,
		"if ( !command || !profileCommand ) {",
		"return qfalse;",
		"return !Q_stricmp( command, profileCommand ) ? qtrue : qfalse;",
	)

	starts_with = _function_block(common_c, "static qboolean NET_CommandStartsWithProfileToken( const char *command, const char *profileCommand )")
	_assert_order(
		starts_with,
		"if ( !command || !profileCommand ) {",
		"commandLength = strlen( profileCommand );",
		"if ( !commandLength ) {",
		"return !Q_strncmp( command, profileCommand, commandLength ) ? qtrue : qfalse;",
	)

	for signature, getter in (
		("qboolean NET_IsGetChallengeRequest( const char *command )", "NET_GetChallengeRequestCommand()"),
		("qboolean NET_IsChallengeResponse( const char *command )", "NET_GetChallengeResponseCommand()"),
		("qboolean NET_IsConnectRequest( const char *command )", "NET_GetConnectRequestCommand()"),
		("qboolean NET_IsConnectResponse( const char *command )", "NET_GetConnectResponseCommand()"),
		("qboolean NET_IsGetInfoRequest( const char *command )", "NET_GetInfoRequestCommand()"),
		("qboolean NET_IsGetStatusRequest( const char *command )", "NET_GetStatusRequestCommand()"),
		("qboolean NET_IsDownloadRequestCommand( const char *command )", "NET_GetDownloadRequestCommand()"),
		("qboolean NET_IsDownloadNextCommand( const char *command )", "NET_GetDownloadNextCommand()"),
		("qboolean NET_IsDownloadStopCommand( const char *command )", "NET_GetDownloadStopCommand()"),
		("qboolean NET_IsDownloadDoneCommand( const char *command )", "NET_GetDownloadDoneCommand()"),
		("qboolean NET_IsUserinfoCommand( const char *command )", "NET_GetUserinfoCommand()"),
		("qboolean NET_IsReliableDisconnectCommand( const char *command )", "NET_GetReliableDisconnectCommand()"),
	):
		assert f"return NET_CommandMatchesProfileToken( command, {getter} );" in _function_block(common_c, signature)

	assert "return NET_CommandStartsWithProfileToken( command, NET_GetServersResponseCommand() );" in _function_block(
		common_c, "qboolean NET_IsServersResponse( const char *command )"
	)

	connect_packet = common_c.split("qboolean NET_IsConnectRequestPacket( const msg_t *msg )", 1)[1].split(
		"NET_ProtocolUsesClientQport", 1
	)[0]
	_assert_order(
		connect_packet,
		"if ( !msg || !msg->data || msg->cursize < 4 ) {",
		"command = NET_GetConnectRequestCommand();",
		"if ( !command || !command[0] ) {",
		"commandLength = strlen( command );",
		"if ( msg->cursize < 4 + commandLength ) {",
		"payload = (const char *)msg->data + 4;",
		"if ( Q_strncmp( payload, command, commandLength ) ) {",
		"if ( msg->cursize == 4 + commandLength ) {",
		"delimiter = payload[commandLength];",
		"delimiter == '\\0' || delimiter == ' ' || delimiter == '\"' || delimiter == '\\n' || delimiter == '\\r'",
	)

	for signature, field in (
		("qboolean NET_ProtocolUsesClientQport( void )", "usesClientQport"),
		("qboolean NET_ProtocolUsesNetchanClientQport( void )", "usesNetchanClientQport"),
		("qboolean NET_ProtocolUsesReliableXorCodec( void )", "usesReliableXorCodec"),
		("qboolean NET_ProtocolUsesLegacyAuthorize( void )", "usesLegacyQ3Authorize"),
		("qboolean NET_ProtocolUsesCompressedConnect( void )", "usesCompressedConnect"),
		("qboolean NET_ProtocolSupportsPlatformAuth( void )", "supportsPlatformAuth"),
	):
		assert f"return NET_GetProtocolProfile()->{field};" in _function_block(common_c, signature)

	for expected in (
		'Info_SetValueForKey( info, NET_GetProtocolInfoKey(), va("%i", NET_ProtocolVersion() ) );',
		'Info_SetValueForKey( info, NET_GetQportInfoKey(), va("%i", port ) );',
		'Info_SetValueForKey( info, NET_GetChallengeInfoKey(), va("%i", clc.challenge ) );',
		'Com_sprintf( data, sizeof( data ), "%s \\"%s\\"", NET_GetConnectRequestCommand(), info );',
		"if ( NET_ProtocolUsesCompressedConnect() ) {",
		"if ( NET_ProtocolUsesLegacyAuthorize() && !Sys_IsLANAddress( clc.serverAddress ) ) {",
		"NET_ProtocolSupportsPlatformAuth()",
		'CL_AddReliableCommand( va("%s %s", NET_GetDownloadRequestCommand(), remoteName) );',
		'CL_AddReliableCommand( NET_GetDownloadDoneCommand() );',
	):
		assert expected in cl_main

	for expected in (
		'CL_AddReliableCommand( NET_GetDownloadStopCommand() );',
		'CL_AddReliableCommand( va("%s %d", NET_GetDownloadNextCommand(), clc.downloadBlock) );',
		'cl.serverId = atoi( Info_ValueForKey( systemInfo, NET_GetServerIdInfoKey() ) );',
		'if ( !Q_stricmp( key, NET_GetFsGameInfoKey() ) ) {',
		'cl_connectedToPureServer = Cvar_VariableValue( NET_GetSystemPureInfoKey() );',
	):
		assert expected in cl_parse

	for expected in (
		"NET_ProtocolUsesNetchanClientQport()",
		"if ( chan->sock == NS_CLIENT && NET_ProtocolUsesNetchanClientQport() ) {",
		"if ( chan->sock == NS_SERVER && NET_ProtocolUsesNetchanClientQport() ) {",
	):
		assert expected in net_chan

	assert "NET_ProtocolUsesReliableXorCodec()" in cl_net_chan
	assert "NET_ProtocolUsesReliableXorCodec()" in sv_net_chan

	for expected in (
		"if ( NET_ProtocolUsesCompressedConnect() && NET_IsConnectRequestPacket( msg ) ) {",
		"if ( NET_IsGetStatusRequest( c ) ) {",
		"} else if ( NET_IsGetInfoRequest( c ) ) {",
		"} else if ( NET_IsGetChallengeRequest( c ) ) {",
		"} else if ( NET_IsConnectRequest( c ) ) {",
	):
		assert expected in sv_main

	for expected in (
		"if ( !NET_ProtocolSupports( version ) ) {",
		"qport = atoi( Info_ValueForKey( userinfo, NET_GetQportInfoKey() ) );",
		'Info_SetValueForKey( userinfo, NET_GetClientIpInfoKey(), NET_AdrToString( from ) );',
		'NET_OutOfBandPrint( NS_SERVER, from, "%s", NET_GetConnectResponseCommand() );',
		"{NULL, NET_GetDownloadRequestCommand, SV_BeginDownload_f},",
		"{NULL, NET_GetDownloadNextCommand, SV_NextDownload_f},",
		"{NULL, NET_GetDownloadStopCommand, SV_StopDownload_f},",
		"{NULL, NET_GetDownloadDoneCommand, SV_DoneDownload_f},",
		"{NULL, NET_GetUserinfoCommand, SV_UpdateUserinfo_f},",
		"{NULL, NET_GetReliableDisconnectCommand, SV_Disconnect_f},",
	):
		assert expected in sv_client

	for hardcoded in (
		'NET_OutOfBandPrint(NS_CLIENT, clc.serverAddress, "getchallenge");',
		'if ( !Q_stricmp(c, "challengeResponse") ) {',
		'if ( !Q_stricmp(c, "connectResponse") ) {',
		'if (!Q_stricmp(c, "getchallenge")) {',
		'if (!Q_stricmp(c, "connect")) {',
	):
		assert hardcoded not in cl_main
		assert hardcoded not in sv_main
		assert hardcoded not in sv_client

	for expected in (
		"0x5b / 91",
		"`data_5684dc = 0x5b`",
		"`NET_GetProtocolProfile()`, `NET_ProtocolVersion()`,",
		"profile-aware `NET_IsConnectRequestPacket()` guard",
		"`NET_ProtocolSupportsPlatformAuth` exposes the active protocol profile",
	):
		assert expected in (audit + round_290)

	assert "Implementation round - 2026-06-04, protocol profile manifest expansion" in plan


def test_ql_server_browser_protocol_and_master_heartbeat_parity_closure() -> None:
	common_c = _read(COMMON_C_PATH)
	cl_main = _read(CL_MAIN_PATH)
	sv_main = _read(SV_MAIN_PATH)
	sv_init = _read(REPO_ROOT / "src/code/server/sv_init.c")
	steamworks = _read(REPO_ROOT / "src/common/platform/platform_steamworks.c")
	ghidra_imports = _read(REPO_ROOT / "references/reverse-engineering/ghidra/quakelive_steam/imports.txt")
	ghidra_decompile = _read(GHIDRA_DECOMPILE_TOP_PATH)
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part05 = _read(HLIL_PART05_PATH)
	audit = _read(NETWORK_BROWSER_HEARTBEAT_AUDIT_PATH)
	implementation_plan = _read(REPO_ROOT / "IMPLEMENTATION_PLAN.md")

	profile_block = common_c.split("static const netprofile_desc_t s_netProtocolProfile = {", 1)[1].split("\n};", 1)[0]
	_assert_order(
		profile_block,
		"\"getinfo\",",
		"\"infoResponse\",",
		"\"getstatus\",",
		"\"statusResponse\",",
		"\"getservers\",",
		"\"getserversResponse\",",
		"\"heartbeat\",",
		"\"QuakeArena-1\",",
		"QL_RETAIL_PROTOCOL_VERSION,",
	)

	servers_response = _function_block(cl_main, "void CL_ServersResponsePacket( netadr_t from, msg_t *msg )")
	connectionless = _function_block(cl_main, "void CL_ConnectionlessPacket( netadr_t from, msg_t *msg )")
	request_global = _function_block(cl_main, "static void CL_RequestGlobalServers( int masterNum, const char *protocol, const char *keywords ) {")
	master_heartbeat = _function_block(sv_main, "void SV_MasterHeartbeat( void )")
	steam_masters = _function_block(sv_init, "static qboolean SV_SteamServerHasConfiguredMasters( void )")
	spawn_server = _function_block(sv_init, "void SV_SpawnServer( char *server, qboolean killBots )")
	enable_heartbeats = _function_block(steamworks, "qboolean QL_Steamworks_ServerEnableHeartbeats( qboolean enable )")

	assert "#define MAX_SERVERSPERPACKET\t256" in cl_main
	_assert_order(
		servers_response,
		"buffptr    = msg->data;",
		"buffend    = buffptr + msg->cursize;",
		"if (*buffptr++ == '\\\\')",
		"addresses[numservers].ip[0] = *buffptr++;",
		"addresses[numservers].ip[3] = *buffptr++;",
		"addresses[numservers].port = (*buffptr++)<<8;",
		"addresses[numservers].port = BigShort( addresses[numservers].port );",
		"if (buffptr[1] == 'E' && buffptr[2] == 'O' && buffptr[3] == 'T') {",
		"CL_InitServerInfo( server, &addresses[i] );",
	)
	assert "if ( NET_IsServersResponse( c ) ) {" in connectionless
	assert "CL_ServersResponsePacket( from, msg );" in connectionless

	_assert_order(
		request_global,
		"#if QL_PLATFORM_HAS_ONLINE_SERVICES && QL_ENABLE_LEGACY_Q3_SERVICES",
		"NET_StringToAdr( MASTER_SERVER_NAME, &to );",
		"to.port = BigShort(PORT_MASTER);",
		"Com_sprintf( command, sizeof( command ), \"%s %s\", NET_GetServersRequestCommand(), protocol );",
		"Q_strcat( command, sizeof( command ), keywords );",
		"NET_OutOfBandPrint( NS_SERVER, to, command );",
	)

	assert "#if QL_PLATFORM_HAS_ONLINE_SERVICES && QL_ENABLE_LEGACY_Q3_SERVICES" in master_heartbeat
	assert "if ( !strstr( sv_master[i]->string, \":\" ) ) {" in master_heartbeat
	assert "strstr( \":\", sv_master[i]->string )" not in master_heartbeat
	assert 'NET_OutOfBandPrint( NS_SERVER, adr[i], "%s %s\\n", NET_GetHeartbeatCommand(), NET_GetHeartbeatGameName() );' in master_heartbeat
	assert "SV_LogMasterVACHeartbeat( &adr[i], sv_master[i]->string );" in master_heartbeat
	assert "if ( sv_masterAdvertise && sv_masterAdvertise->integer ) {" in steam_masters
	assert "if ( sv_master[i] && sv_master[i]->string[0] ) {" in steam_masters
	assert "QL_Steamworks_ServerEnableHeartbeats( SV_SteamServerHasConfiguredMasters() );" in spawn_server
	assert "vtable[0x9c / 4]" in enable_heartbeats
	assert "fn( gameServer, NULL, enable ? 1 : 0 );" in enable_heartbeats

	for expected in (
		"STEAM_API.DLL!SteamGameServer @",
		"STEAM_API.DLL!SteamMatchmakingServers @",
	):
		assert expected in ghidra_imports

	for expected in (
		"iVar3 = FUN_004d9020(uVar1,\"getserversResponse\",0x12);",
		"004bc11c      if (sub_4d9020(eax_4, \"getserversResponse\", 0x12) == 0)",
		"004bbf0c  if (sub_4d9060(eax_4, \"infoResponse\") == 0)",
		"004bbf59  if (sub_4d9060(eax_4, \"statusResponse\") == 0)",
	):
		assert expected in (ghidra_decompile + hlil_part04)

	for expected in (
		"004bb084                              *(esi_1 + 0x10), \"getinfo xxx\")",
		"004ba971              sub_4d7080(0, var_1c, var_18, var_14, var_10, var_c, \"getstatus\")",
		"004e3b9b  data_13e17e4 = sub_4ce0d0(x87_r6, \"sv_master\", U\"1\", 1)",
		"004e3bc4  sub_4ce0d0(x87_r2, \"protocol\", sub_4d9220(&data_52e930), 0x44)",
	):
		assert expected in (hlil_part04 + hlil_part05)

	for expected in (
		"Focused server browser protocol and master heartbeat slice: before **96%**",
		"after **100%**",
		"Task A211: Close server browser protocol and master heartbeat parity [COMPLETED]",
	):
		assert expected in (audit + implementation_plan)


def test_ql_server_browser_and_master_heartbeat_related_wiring_parity_recheck() -> None:
	platform_config = _read(REPO_ROOT / "src/common/platform/platform_config.h")
	client_h = _read(CLIENT_H_PATH)
	cl_cgame = _read(REPO_ROOT / "src/code/client/cl_cgame.c")
	cl_main = _read(CL_MAIN_PATH)
	common_c = _read(COMMON_C_PATH)
	sv_main = _read(SV_MAIN_PATH)
	sv_init = _read(REPO_ROOT / "src/code/server/sv_init.c")
	sv_client = _read(SV_CLIENT_PATH)
	sv_ccmds = _read(REPO_ROOT / "src/code/server/sv_ccmds.c")
	steamworks_h = _read(REPO_ROOT / "src/common/platform/platform_steamworks.h")
	steamworks = _read(REPO_ROOT / "src/common/platform/platform_steamworks.c")
	aliases = _read(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json")
	ghidra_imports = _read(REPO_ROOT / "references/reverse-engineering/ghidra/quakelive_steam/imports.txt")
	ghidra_decompile = _read(GHIDRA_DECOMPILE_TOP_PATH)
	hlil_part02 = _read(HLIL_PART02_PATH)
	audit = _read(NETWORK_BROWSER_HEARTBEAT_AUDIT_PATH)
	implementation_plan = _read(REPO_ROOT / "IMPLEMENTATION_PLAN.md")

	method_block = _function_block(
		cl_cgame,
		"static qboolean QLJSHandler_OnMethodCall( const char *methodName, const char **arguments, int argumentCount ) {",
	)
	native_mode = _function_block(
		cl_main,
		"static ql_steam_server_browser_request_mode_t CL_SteamBrowser_RequestModeToNativeMode( int requestMode )",
	)
	native_available = _function_block(cl_main, "static qboolean CL_SteamBrowser_NativeListAvailable( void )")
	begin_native = _function_block(cl_main, "static qboolean CL_SteamBrowser_BeginNativeRequest( int requestMode )")
	native_response = _function_block(
		cl_main,
		"static void CL_SteamBrowser_PublishNativeServerResponse( const ql_steam_server_browser_response_t *response )",
	)
	native_server_responded = _function_block(
		cl_main,
		"static void CL_SteamBrowser_NativeServerRespondedImpl( clSteamNativeServerListResponse_t *self, ql_steam_server_list_request_t request, int serverIndex )",
	)
	native_server_failed = _function_block(
		cl_main,
		"static void CL_SteamBrowser_NativeServerFailedToRespondImpl( clSteamNativeServerListResponse_t *self, ql_steam_server_list_request_t request, int serverIndex )",
	)
	complete_native = _function_block(cl_main, "static void CL_SteamBrowser_CompleteNativeRefresh( qboolean timedOut )")
	native_ping_responded = _function_block(
		cl_main,
		"static void CL_SteamBrowser_NativePingRespondedImpl( clSteamNativeServerPingResponse_t *self, const void *serverDetails )",
	)
	native_rule_responded = _function_block(
		cl_main,
		"static void CL_SteamBrowser_NativeRuleRespondedImpl( clSteamNativeServerRulesResponse_t *self, const char *rule, const char *value )",
	)
	native_player_responded = _function_block(
		cl_main,
		"static void CL_SteamBrowser_NativePlayerRespondedImpl( clSteamNativeServerPlayersResponse_t *self, const char *name, int score, float timePlayed )",
	)
	begin_native_detail = _function_block(
		cl_main, "static qboolean CL_SteamBrowser_BeginNativeDetailRequest( uint32_t serverIp, uint16_t serverPort )"
	)
	request_servers = _function_block(cl_main, "qboolean CL_Steam_RequestServers( int requestMode )")
	request_details = _function_block(
		cl_main, "qboolean CL_Steam_RequestServerDetails( unsigned int serverIp, unsigned short serverPort )"
	)
	refresh_list = _function_block(cl_main, "qboolean CL_Steam_RefreshServerList( void )")
	browser_frame = _function_block(cl_main, "static void CL_SteamBrowser_Frame( void )")
	publish_refresh_end = _function_block(cl_main, "static void CL_SteamBrowser_PublishRefreshEnd( void )")
	publish_server_response = _function_block(
		cl_main,
		"static void CL_SteamBrowser_PublishServerResponse( const netadr_t *address, uint32_t serverIp, uint16_t serverPort, const char *infoString, int ping )",
	)
	server_info_packet = _function_block(cl_main, "void CL_ServerInfoPacket( netadr_t from, msg_t *msg )")
	server_status_response = _function_block(cl_main, "void CL_ServerStatusResponse( netadr_t from, msg_t *msg ) {")
	compute_counts = _function_block(sv_main, "static void SV_ComputeDisplayedCounts( int *clientCount, int *botCount ) {")
	status_response = _function_block(sv_main, "void SVC_Status( netadr_t from )")
	info_response = _function_block(sv_main, "void SVC_Info( netadr_t from )")
	published_state = _function_block(sv_main, "void SV_SteamServerUpdatePublishedState( qboolean fullUpdate )")
	server_frame = _function_block(sv_main, "void SV_Frame( int msec )")
	spawn_server = _function_block(sv_init, "void SV_SpawnServer( char *server, qboolean killBots )")
	shutdown_server = _function_block(sv_init, "void SV_Shutdown( char *finalmsg )")
	steam_masters = _function_block(sv_init, "static qboolean SV_SteamServerHasConfiguredMasters( void )")
	steam_connected = _function_block(
		sv_client, "static void SV_SteamServerConnectedCallback( void *context, const ql_steam_server_connected_t *event )"
	)
	direct_connect = _function_block(sv_client, "void SV_DirectConnect( netadr_t from )")
	drop_client = _function_block(sv_client, "void SV_DropClient( client_t *drop, const char *reason )")
	heartbeat_command = _function_block(sv_ccmds, "void SV_Heartbeat_f( void )")
	add_operator_commands = _function_block(sv_ccmds, "void SV_AddOperatorCommands( void )")
	steam_bootstrap = _function_block(common_c, "void Com_InitSteamGameServer( void )")
	browser_owner_entry = _function_block(
		steamworks,
		"qboolean QL_Steamworks_BeginServerBrowserOwnerRequest( ql_steam_server_browser_owner_t *owner, ql_steam_server_browser_request_mode_t requestMode, void *responseObject )",
	)
	browser_owner = _function_block(
		steamworks,
		"qboolean QL_Steamworks_BeginServerBrowserOwnerRequestForApp( ql_steam_server_browser_owner_t *owner, ql_steam_server_browser_request_mode_t requestMode, uint32_t appId, void *responseObject )",
	)
	request_server_list = _function_block(
		steamworks,
		"ql_steam_server_list_request_t QL_Steamworks_RequestServerListForApp( ql_steam_server_browser_request_mode_t requestMode, uint32_t appId, void *responseObject )",
	)
	get_server_details = _function_block(
		steamworks, "const void *QL_Steamworks_GetServerListDetails( ql_steam_server_list_request_t request, int index )"
	)
	release_request = _function_block(steamworks, "void QL_Steamworks_ReleaseServerListRequest( ql_steam_server_list_request_t request )")
	refresh_request = _function_block(steamworks, "void QL_Steamworks_RefreshServerListRequest( ql_steam_server_list_request_t request )")
	detail_request = _function_block(
		steamworks,
		"qboolean QL_Steamworks_RequestServerDetails( uint32_t serverIp, uint16_t serverPort, void *pingResponse, void *playersResponse, void *rulesResponse, ql_steam_server_query_t *outPingQuery, ql_steam_server_query_t *outPlayersQuery, ql_steam_server_query_t *outRulesQuery )",
	)
	ping_response_reader = _function_block(
		steamworks,
		"qboolean QL_Steamworks_ReadServerBrowserPingResponseForApp( const void *serverDetails, uint32_t appId, ql_steam_server_browser_response_t *outResponse )",
	)
	enable_heartbeats = _function_block(steamworks, "qboolean QL_Steamworks_ServerEnableHeartbeats( qboolean enable )")

	assert "#define QL_BUILD_ONLINE_SERVICES 0" in platform_config
	assert "#define QL_ENABLE_LEGACY_Q3_SERVICES 0" in platform_config
	assert "qboolean CL_Steam_RequestServers( int requestMode );" in client_h
	assert "qboolean CL_Steam_RequestServerDetails( unsigned int serverIp, unsigned short serverPort );" in client_h
	assert "qboolean CL_Steam_RefreshServerList( void );" in client_h

	assert "case CL_WEB_METHOD_REQUEST_SERVERS:" in method_block
	assert "return CL_Steam_RequestServers( QLJSHandler_CoerceIntegerArgument( arguments[0] ) );" in method_block
	assert "case CL_WEB_METHOD_REQUEST_SERVER_DETAILS:" in method_block
	assert "return CL_Steam_RequestServerDetails(" in method_block
	assert "case CL_WEB_METHOD_REFRESH_LIST:" in method_block
	assert "return CL_Steam_RefreshServerList();" in method_block
	for expected in (
		"return QL_STEAM_SERVER_BROWSER_INTERNET;",
		"return QL_STEAM_SERVER_BROWSER_LAN;",
		"return QL_STEAM_SERVER_BROWSER_FRIENDS;",
		"return QL_STEAM_SERVER_BROWSER_FAVORITES;",
		"return QL_STEAM_SERVER_BROWSER_HISTORY;",
	):
		assert expected in native_mode
	assert "CL_MatchmakingServiceAvailable()" in native_available
	assert "QL_Steamworks_HasServerBrowserInterface()" in native_available
	assert "QL_Steamworks_BeginServerBrowserOwnerRequestForApp( &cl_steamNativeBrowserOwner, nativeMode, cl_steamBrowserState.nativeAppId, &cl_steamNativeListResponse )" in begin_native
	assert 'CL_Steam_PublishBrowserEvent( "servers.refresh.start", NULL );' in begin_native
	assert 'Com_sprintf( eventName, sizeof( eventName ), "servers.details.%s.response", response->id );' in native_response
	assert "if ( self != &cl_steamNativeListResponse || request != cl_steamNativeBrowserOwner.request ) {" in native_server_responded
	assert "!cl_steamBrowserState.nativeRefreshActive" not in native_server_responded
	assert "QL_Steamworks_ReadServerBrowserResponseForApp( request, serverIndex, cl_steamBrowserState.nativeAppId, &response )" in native_server_responded
	assert "CL_SteamBrowser_PublishNativeServerResponse( &response );" in native_server_responded
	assert "if ( self != &cl_steamNativeListResponse || request != cl_steamNativeBrowserOwner.request ) {" in native_server_failed
	assert "!cl_steamBrowserState.nativeRefreshActive" not in native_server_failed
	assert "CL_SteamBrowser_PublishServerFailed( serverIndex );" in native_server_failed
	assert "CL_STEAM_BROWSER_USE_MSVC_C_THISCALL_THUNKS" in cl_main
	assert "static __declspec(naked) void CL_SteamBrowser_NativeServerResponded" in cl_main
	assert "CL_SteamBrowser_NativeServerRespondedImpl( self, request, serverIndex );" in cl_main
	assert "QL_Steamworks_CompleteServerBrowserOwnerRequest( &cl_steamNativeBrowserOwner );" in complete_native
	assert "const clSteamNativeServerRulesResponseVTable_t *rulesVtable;" in cl_main
	assert "const clSteamNativeServerPlayersResponseVTable_t *playersVtable;" in cl_main
	assert "const clSteamNativeServerPingResponseVTable_t *pingVtable;" in cl_main
	assert "QL_Steamworks_ReadServerBrowserPingResponseForApp( serverDetails, detail->appId, &response )" in native_ping_responded
	assert "CL_SteamBrowser_PublishNativeServerResponse( &response );" in native_ping_responded
	assert "QL_Steamworks_BuildServerBrowserRuleResponse( &detail->request.lifecycle.identity, rule, value, &response )" in native_rule_responded
	assert "CL_SteamBrowser_PublishNativeRuleResponse( &response );" in native_rule_responded
	assert "QL_Steamworks_BuildServerBrowserPlayerResponse( &detail->request.lifecycle.identity, name, score, (int)timePlayed, &response )" in native_player_responded
	assert "CL_SteamBrowser_PublishNativePlayerResponse( &response );" in native_player_responded
	assert "QL_Steamworks_BeginServerBrowserDetailRequest( &detail->request, serverIp, serverPort, detail )" in begin_native_detail
	assert "CL_SteamBrowser_FreeNativeDetail( detail, qfalse );" in cl_main
	assert "CL_SteamBrowser_FreeNativeDetail( cl_steamNativeDetails, qtrue );" in cl_main

	_assert_order(
		request_servers,
		"CL_SteamBrowser_RequestModeToSource( requestMode )",
		"CL_SteamBrowser_BeginNativeRequest( requestMode )",
		"cl_steamBrowserState.nativeRefreshActive = qfalse;",
		"cl_steamBrowserState.refreshActive = qtrue;",
		'CL_Steam_PublishBrowserEvent( "servers.refresh.start", NULL );',
		"CL_SteamBrowser_PublishCompatibilitySource( requestMode, source );",
		"CL_RequestLocalServers();",
		'CL_RequestGlobalServers( masterNum, debugProtocol, "full empty" );',
		'CL_RequestGlobalServers( masterNum, va( "%d", protocol ), "full empty" );',
	)
	assert "CL_SteamBrowser_BeginNativeDetailRequest( (uint32_t)serverIp, (uint16_t)serverPort )" in request_details
	assert "CL_SteamBrowser_BeginDetailRequest( (uint32_t)serverIp, (uint16_t)serverPort, &address );" in request_details
	assert "CL_ServerStatus( addressString, NULL, 0 );" in request_details
	assert "CL_ServerStatus( addressString, serverStatus, sizeof( serverStatus ) );" in request_details
	assert "QL_Steamworks_RefreshServerBrowserOwnerRequest( &cl_steamNativeBrowserOwner )" in refresh_list
	assert "cl_steamBrowserState.nativeAppId = CL_SteamBrowser_GetDiscoveryAppID();" in refresh_list
	assert 'CL_Steam_PublishBrowserEvent( "servers.refresh.start", NULL );' not in refresh_list
	assert "cl_steamBrowserState.nativeRefreshActive = qtrue;" not in refresh_list
	assert "cl_steamBrowserState.refreshActive = qtrue;" not in refresh_list
	assert "cl_steamBrowserState.refreshTimeoutTime = cls.realtime + CL_STEAM_BROWSER_REFRESH_TIMEOUT_MSEC;" not in refresh_list
	assert "return CL_Steam_RequestServers( cl_steamBrowserState.requestMode );" in refresh_list
	assert "if ( timedOut && !cl_steamBrowserState.nativeRefreshActive ) {" in complete_native
	assert "CL_SteamBrowser_FailDetailRequest();" in browser_frame
	assert "CL_SteamBrowser_CompleteNativeRefresh( qtrue );" in browser_frame
	assert "CL_UpdateVisiblePings_f( cl_steamBrowserState.requestSource )" in browser_frame
	assert "CL_SteamBrowser_PublishRefreshEnd();" in browser_frame
	assert "CL_SteamBrowser_PublishServerFailed( i );" in publish_refresh_end
	assert 'CL_Steam_PublishBrowserEvent( "servers.refresh.end", NULL );' in publish_refresh_end
	assert 'Com_sprintf( eventName, sizeof( eventName ), "servers.details.%s.response", responseId );' in publish_server_response
	assert 'Info_ValueForKey( infoString, "botPlayers" )' in publish_server_response
	assert 'Info_ValueForKey( infoString, "vac" )' in publish_server_response
	assert 'Info_ValueForKey( infoString, "steamid" )' in publish_server_response
	assert "CL_SteamBrowser_PublishServerResponse(" in server_info_packet
	assert "CL_SteamBrowser_PackAddressIP( &from )" in server_info_packet
	assert "publishBrowserDetails = CL_SteamBrowser_DetailMatchesAddress( &from );" in server_status_response
	assert "CL_SteamBrowser_PublishRulesFromInfoString(" in server_status_response
	assert "CL_SteamBrowser_PublishPlayerResponse(" in server_status_response
	assert "CL_SteamBrowser_PublishPlayersEnd( cl_steamBrowserState.detailId );" in server_status_response
	assert "CL_SteamBrowser_ClearDetailRequest();" in server_status_response

	assert "SV_ClientIsBot( cl )" in compute_counts
	assert "sv_maskBots && sv_maskBots->integer" in compute_counts
	assert "reportedBots++;" in compute_counts
	for expected in (
		"NET_GetClientsInfoKey()",
		"NET_GetBotPlayersInfoKey()",
		"NET_GetVACInfoKey()",
		"NET_GetServerTypeInfoKey()",
	):
		assert expected in status_response
		assert expected in info_response
	assert "if ( sv_maskBots->integer && SV_ClientIsBot( cl ) ) {" in status_response

	for expected in (
		"QL_Steamworks_ServerSetMaxPlayerCount",
		"QL_Steamworks_ServerSetPasswordProtected",
		"QL_Steamworks_ServerSetServerName",
		"QL_Steamworks_ServerSetMapName",
		"QL_Steamworks_ServerSetGameDescription",
		"QL_Steamworks_ServerSetGameTags",
		'QL_Steamworks_ServerSetKeyValue( "g_redScore", redScore )',
		'QL_Steamworks_ServerSetKeyValue( "g_blueScore", blueScore )',
		"QL_Steamworks_ServerUpdateUserData",
		"QL_Steamworks_ServerSetBotPlayerCount",
	):
		assert expected in published_state
	assert "SV_SteamServerNetworkingFrame();" in server_frame
	assert "QL_Steamworks_ServerSetKeyValuesFromInfoString( serverInfo );" in server_frame
	assert "SV_SteamServerUpdatePublishedState( qfalse );" in server_frame
	assert "SV_MasterHeartbeat();" in server_frame
	assert "SV_RefreshPlatformServiceCvars();" in spawn_server
	assert "SV_SteamServerPublishIdentity();" in spawn_server
	assert "QL_Steamworks_ServerEnableHeartbeats( SV_SteamServerHasConfiguredMasters() );" in spawn_server
	assert "SV_SteamServerUpdatePublishedState( qtrue );" in spawn_server
	assert "QL_Steamworks_ServerSetKeyValuesFromInfoString( serverInfo );" in spawn_server
	assert "SV_Heartbeat_f();" in spawn_server
	assert "SV_MasterShutdown();" in shutdown_server
	assert "QL_Steamworks_ServerEnableHeartbeats( qfalse );" in shutdown_server
	assert "QL_Steamworks_ServerShutdown();" in shutdown_server
	assert "SV_SteamServerPublishIdentity();" in steam_connected
	assert "SV_SteamServerUpdatePublishedState( qtrue );" in steam_connected
	assert "if ( sv_masterAdvertise && sv_masterAdvertise->integer ) {" in steam_masters
	assert "if ( sv_master[i] && sv_master[i]->string[0] ) {" in steam_masters
	assert "newcl->state = CS_CONNECTED;" in direct_connect
	assert "if ( count == 1 || count == sv_maxclients->integer ) {" in direct_connect
	assert "SV_SetUserinfo( drop - svs.clients, \"\" );" in drop_client
	assert "if ( i == sv_maxclients->integer ) {" in drop_client
	assert "svs.nextHeartbeatTime = -9999999;" in heartbeat_command
	assert 'Cmd_AddCommand ("heartbeat", SV_Heartbeat_f);' not in add_operator_commands
	assert "QL_Steamworks_ServerEnableHeartbeats( qfalse );" in steam_bootstrap
	assert "QL_Steamworks_ServerSetProduct( QL_PRODUCT_NAME );" in steam_bootstrap
	assert "QL_Steamworks_ServerSetGameDir( QL_BASEGAME );" in steam_bootstrap

	for expected in (
		"ql_steam_server_browser_owner_t",
		"ql_steam_server_browser_detail_request_t",
		"ql_steam_server_browser_response_t",
		"qboolean QL_Steamworks_ReadServerBrowserPingResponse",
		"qboolean QL_Steamworks_ReadServerBrowserPingResponseForApp",
		"qboolean QL_Steamworks_BeginServerBrowserOwnerRequest",
		"qboolean QL_Steamworks_BeginServerBrowserOwnerRequestForApp",
		"qboolean QL_Steamworks_BeginServerBrowserDetailRequest",
	):
		assert expected in steamworks_h
	assert "return QL_Steamworks_BeginServerBrowserOwnerRequestForApp( owner, requestMode, QL_Steamworks_GetAppID(), responseObject );" in browser_owner_entry
	assert "QL_Steamworks_ReleaseServerListRequest( owner->request );" in browser_owner
	assert "ql_steam_server_list_request_t request;" in browser_owner
	assert "if ( appId == 0u ) {" in browser_owner
	assert "request = QL_Steamworks_RequestServerListForApp( requestMode, appId, responseObject );" in browser_owner
	assert "if ( !request ) {" in browser_owner
	assert "owner->refreshActive = qfalse;" in browser_owner
	assert "owner->request = NULL;" in browser_owner
	assert "owner->request = request;" in browser_owner
	assert 'Q_strncpyz( filter->key, "gamedir", sizeof( filter->key ) );' in steamworks
	assert "Q_strncpyz( filter->value, QL_BASEGAME, sizeof( filter->value ) );" in steamworks
	for expected in (
		"vtable[0x00 / 4]",
		"vtable[0x04 / 4]",
		"vtable[0x08 / 4]",
		"vtable[0x0c / 4]",
		"vtable[0x10 / 4]",
	):
		assert expected in request_server_list
	assert "vtable[0x1c / 4]" in get_server_details
	assert "vtable[0x18 / 4]" in release_request
	assert "vtable[0x24 / 4]" in refresh_request
	assert "vtable[0x34 / 4]" in detail_request
	assert "vtable[0x38 / 4]" in detail_request
	assert "vtable[0x3c / 4]" in detail_request
	assert "raw = (const ql_steam_gameserveritem_raw_t *)serverDetails;" in ping_response_reader
	assert "raw->appId != appId" in ping_response_reader
	assert "QL_Steamworks_CopyServerBrowserResponse( outResponse, &server );" in ping_response_reader
	_assert_order(
		detail_request,
		"pingQuery = pingFn( serverBrowser, NULL, serverIp, serverPort, pingResponse );",
		"rulesQuery = rulesFn( serverBrowser, NULL, serverIp, serverPort, rulesResponse );",
		"playersQuery = playersFn( serverBrowser, NULL, serverIp, serverPort, playersResponse );",
		"if ( pingQuery <= 0 || rulesQuery <= 0 || playersQuery <= 0 ) {",
		"QL_Steamworks_CancelServerQuery( pingQuery );",
		"QL_Steamworks_CancelServerQuery( rulesQuery );",
		"QL_Steamworks_CancelServerQuery( playersQuery );",
		"return qfalse;",
		"if ( outPingQuery ) {",
	)
	assert "vtable[0x9c / 4]" in enable_heartbeats
	assert "fn( gameServer, NULL, enable ? 1 : 0 );" in enable_heartbeats

	for expected in (
		"STEAM_API.DLL!SteamMatchmakingServers @",
		"STEAM_API.DLL!SteamGameServer @",
	):
		assert expected in ghidra_imports
	for expected in (
		'"sub_461F70": "JSBrowserDetails_RequestServerDetails"',
		'"sub_461FE0": "JSBrowserDetails_OnServerResponded"',
		'"sub_462360": "JSBrowserDetails_OnRuleResponded"',
		'"sub_4626B0": "JSBrowserDetails_OnPlayerResponded"',
		'"sub_462EB0": "JSBrowser_RequestServers"',
		'"sub_463090": "SteamBrowser_RequestServers"',
		'"sub_4630B0": "SteamBrowser_RequestServerDetails"',
		'"sub_465DB0": "SteamServer_EnableHeartbeats"',
		'"sub_4DF660": "SV_DropClient"',
		'"sub_4E0750": "SV_DirectConnect"',
	):
		assert expected in aliases
	for expected in (
		"00461fab  (*(*SteamMatchmakingServers() + 0x34))(arg2, arg3, arg1 + 8)",
		"00461fbd  (*(*SteamMatchmakingServers() + 0x3c))(arg2, arg3, arg1)",
		"00461fd8  return (*(*SteamMatchmakingServers() + 0x38))(arg2, arg3, arg1 + 4)",
		'0046245d  sub_4f3260(arg1, arg1 + 0x14, sub_4d9220("servers.rules.%s.response"), &var_20)',
		'004627fc  sub_4f3260(arg1, arg1 + 0x10, sub_4d9220("servers.players.%s.response"), &var_20)',
		'00463058      result = sub_4f3260(arg1, edi_1, "servers.refresh.start", nullptr)',
		'00462e73  return sub_4f3260(esi, edi, "servers.refresh.end", nullptr)',
		"00465dd7      (*(*SteamGameServer() + 0x9c))(arg1 == 1)",
		"00467073          (*(*SteamGameServer() + 0x9c))(0)",
	):
		assert expected in hlil_part02
	for expected in (
		'DAT_013e17e4 = FUN_004ce0d0("sv_master",&DAT_00551624,1);',
		"FUN_00465db0(*(int *)(DAT_013e17e4 + 0x30) != 0);",
	):
		assert expected in ghidra_decompile
	for expected in (
		"Related browser/heartbeat wiring recheck: before **97%**, after **100%**",
		"Retail `SV_Startup` / `SV_SpawnServer` evidence gates Steam heartbeats from",
		"graph remains pinned at **100%**",
	):
		assert expected in (audit + implementation_plan)


def test_manifest_covers_transport_constants_and_netchan_layout_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	qcommon_h = _read(QCOMMON_H_PATH)
	net_chan = _read(NET_CHAN_PATH)
	client_h = _read(CLIENT_H_PATH)
	server_h = _read(SERVER_H_PATH)
	plan = _read(PLAN_PATH)
	networking_audit = _read(NETWORKING_AUDIT_PATH)
	network_handshake = _read(NETWORK_HANDSHAKE_PATH)

	for symbol in (
		"SharedTransportConstants",
		"NetchanFragmentConstants",
		"netchan_t",
		"netchan_buffer_t",
	):
		assert entries[symbol]["status"] == "verified"
		assert entries[symbol]["retail_address"] is None
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_transport_constants_and_netchan_layout_lane" in entries[symbol]["tests"]

	assert entries["SharedTransportConstants"]["kind"] == "constant_group"
	assert entries["NetchanFragmentConstants"]["kind"] == "constant_group"
	assert entries["netchan_t"]["kind"] == "structure"
	assert entries["netchan_buffer_t"]["kind"] == "structure"
	assert "no standalone retail address" in entries["SharedTransportConstants"]["compatibility_notes"][0]
	assert "no standalone retail address" in entries["NetchanFragmentConstants"]["compatibility_notes"][0]
	assert "field layout is verified" in entries["netchan_t"]["compatibility_notes"][0]
	assert "retained slow-link companion" in entries["netchan_buffer_t"]["compatibility_notes"][0]

	for expected in (
		"#define\tPACKET_BACKUP\t32",
		"#define\tPACKET_MASK\t\t(PACKET_BACKUP-1)",
		"#define\tMAX_RELIABLE_COMMANDS\t64",
		"#define\tMAX_MSGLEN\t\t\t\t16384",
		"#define MAX_DOWNLOAD_WINDOW\t\t\t8",
	):
		assert expected in qcommon_h

	for expected in (
		"#define\tMAX_PACKETLEN\t\t\t1400",
		"#define\tFRAGMENT_SIZE\t\t\t(MAX_PACKETLEN - 100)",
		"#define\tPACKET_HEADER\t\t\t10",
		"#define\tFRAGMENT_BIT\t(1<<31)",
	):
		assert expected in net_chan

	netchan_block = _netchan_t_block(qcommon_h)
	_assert_order(
		netchan_block,
		"netsrc_t\tsock;",
		"int\t\t\tdropped;",
		"netadr_t\tremoteAddress;",
		"int\t\t\tqport;",
		"int\t\t\tincomingSequence;",
		"int\t\t\toutgoingSequence;",
		"int\t\t\tfragmentSequence;",
		"int\t\t\tfragmentLength;",
		"byte\t\tfragmentBuffer[MAX_MSGLEN];",
		"qboolean\tunsentFragments;",
		"int\t\t\tunsentFragmentStart;",
		"int\t\t\tunsentLength;",
		"byte\t\tunsentBuffer[MAX_MSGLEN];",
	)

	setup = _function_block(net_chan, "void Netchan_Setup( netsrc_t sock, netchan_t *chan, netadr_t adr, int qport )")
	_assert_order(
		setup,
		"Com_Memset (chan, 0, sizeof(*chan));",
		"chan->sock = sock;",
		"chan->remoteAddress = adr;",
		"chan->qport = qport;",
		"chan->incomingSequence = 0;",
		"chan->outgoingSequence = 1;",
	)

	next_fragment = _function_block(net_chan, "void Netchan_TransmitNextFragment( netchan_t *chan )")
	_assert_order(
		next_fragment,
		"byte\t\tsend_buf[MAX_PACKETLEN];",
		"MSG_WriteLong( &send, chan->outgoingSequence | FRAGMENT_BIT );",
		"fragmentLength = FRAGMENT_SIZE;",
		"if ( chan->unsentFragmentStart  + fragmentLength > chan->unsentLength ) {",
		"MSG_WriteShort( &send, chan->unsentFragmentStart );",
		"MSG_WriteShort( &send, fragmentLength );",
		"MSG_WriteData( &send, chan->unsentBuffer + chan->unsentFragmentStart, fragmentLength );",
		"chan->unsentFragmentStart += fragmentLength;",
		"if ( chan->unsentFragmentStart == chan->unsentLength && fragmentLength != FRAGMENT_SIZE ) {",
		"chan->outgoingSequence++;",
		"chan->unsentFragments = qfalse;",
	)

	transmit = _function_block(net_chan, "void Netchan_Transmit( netchan_t *chan, int length, const byte *data )")
	_assert_order(
		transmit,
		"byte\t\tsend_buf[MAX_PACKETLEN];",
		"if ( length > MAX_MSGLEN ) {",
		"chan->unsentFragmentStart = 0;",
		"if ( length >= FRAGMENT_SIZE ) {",
		"chan->unsentFragments = qtrue;",
		"chan->unsentLength = length;",
		"Com_Memcpy( chan->unsentBuffer, data, length );",
		"Netchan_TransmitNextFragment( chan );",
		"MSG_WriteLong( &send, chan->outgoingSequence );",
		"chan->outgoingSequence++;",
		"MSG_WriteData( &send, data, length );",
	)

	process = _function_block(net_chan, "qboolean Netchan_Process( netchan_t *chan, msg_t *msg )")
	_assert_order(
		process,
		"sequence = MSG_ReadLong( msg );",
		"if ( sequence & FRAGMENT_BIT ) {",
		"sequence &= ~FRAGMENT_BIT;",
		"fragmented = qtrue;",
		"if ( fragmented ) {",
		"fragmentStart = MSG_ReadShort( msg );",
		"fragmentLength = MSG_ReadShort( msg );",
		"if ( sequence != chan->fragmentSequence ) {",
		"chan->fragmentSequence = sequence;",
		"chan->fragmentLength = 0;",
		"if ( fragmentStart != chan->fragmentLength ) {",
		"chan->fragmentLength + fragmentLength > sizeof( chan->fragmentBuffer )",
		"Com_Memcpy( chan->fragmentBuffer + chan->fragmentLength,",
		"chan->fragmentLength += fragmentLength;",
		"if ( fragmentLength == FRAGMENT_SIZE ) {",
		"if ( chan->fragmentLength > msg->maxsize ) {",
		"Com_Memcpy( msg->data + 4, chan->fragmentBuffer, chan->fragmentLength );",
	)

	for expected in (
		"outPacket_t\toutPackets[PACKET_BACKUP];",
		"clSnapshot_t\tsnapshots[PACKET_BACKUP];",
		"char\t\treliableCommands[MAX_RELIABLE_COMMANDS][MAX_STRING_CHARS];",
		"char\t\tserverCommands[MAX_RELIABLE_COMMANDS][MAX_STRING_CHARS];",
		"netchan_t\tnetchan;",
	):
		assert expected in client_h

	for expected in (
		"typedef struct netchan_buffer_s {",
		"msg_t           msg;",
		"byte            msgBuffer[MAX_MSGLEN];",
		"struct netchan_buffer_s *next;",
		"} netchan_buffer_t;",
		"char\t\t\treliableCommands[MAX_RELIABLE_COMMANDS][MAX_STRING_CHARS];",
		"unsigned char\t*downloadBlocks[MAX_DOWNLOAD_WINDOW];",
		"clientSnapshot_t\tframes[PACKET_BACKUP];",
		"netchan_t\t\tnetchan;",
		"netchan_buffer_t *netchan_start_queue;",
		"netchan_buffer_t **netchan_end_queue;",
	):
		assert expected in server_h

	for expected in (
		"`FRAGMENT_SIZE` is `MAX_PACKETLEN - 100`, matching retail `0x514`",
		"fragment size matches the retail `MAX_PACKETLEN - 100` shape",
	):
		assert expected in networking_audit

	assert "`fragmentLength`" in network_handshake
	assert "`< FRAGMENT_SIZE` marks last fragment" in network_handshake
	assert "`MAX_MSGLEN` is `16384`; `MAX_PACKETLEN` is `1400`; `FRAGMENT_SIZE` is `MAX_PACKETLEN - 100`" in plan
	assert "Implementation round - 2026-06-04, transport constants and netchan layout manifest expansion" in plan


def test_manifest_covers_huffman_compression_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	qcommon_h = _read(QCOMMON_H_PATH)
	huffman_c = _read(HUFFMAN_C_PATH)
	msg_c = _read(MSG_C_PATH)
	net_chan = _read(NET_CHAN_PATH)
	sv_main = _read(SV_MAIN_PATH)
	plan = _read(PLAN_PATH)
	round_56 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_56.md")
	round_57 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_57.md")
	round_65 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_65.md")

	for symbol in (
		"Huff_putBit",
		"Huff_getBit",
		"Huff_addRef",
		"Huff_Receive",
		"Huff_offsetReceive",
		"Huff_transmit",
		"Huff_offsetTransmit",
		"Huff_Decompress",
		"Huff_Compress",
		"Huff_Init",
		"MSG_initHuffman",
	):
		assert entries[symbol]["status"] == "verified"
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_huffman_compression_lane" in entries[symbol]["tests"]

	assert entries["Huff_putBit"]["retail_address"] == "0x004D3790"
	assert entries["Huff_getBit"]["retail_address"] == "0x004D37D0"
	assert entries["Huff_addRef"]["retail_address"] == "0x004D3980"
	assert entries["Huff_Receive"]["retail_address"] == "0x004D3B20"
	assert entries["Huff_offsetReceive"]["retail_address"] == "0x004D3B80"
	assert entries["Huff_transmit"]["retail_address"] == "0x004D3C90"
	assert entries["Huff_offsetTransmit"]["retail_address"] == "0x004D3E20"
	assert entries["Huff_Decompress"]["retail_address"] == "0x004D3E60"
	assert entries["Huff_Compress"]["retail_address"] == "0x004D40F0"
	assert entries["Huff_Init"]["retail_address"] == "0x004D4260"
	assert entries["MSG_initHuffman"]["retail_address"] == "0x004D6BB0"

	for expected in (
		"void\tHuff_Compress(msg_t *buf, int offset);",
		"void\tHuff_Decompress(msg_t *buf, int offset);",
		"void\tHuff_Init(huffman_t *huff);",
		"void\tHuff_addRef(huff_t* huff, byte ch);",
		"int\t\tHuff_Receive (node_t *node, int *ch, byte *fin);",
		"void\tHuff_transmit (huff_t *huff, int ch, byte *fout);",
		"void\tHuff_offsetReceive (node_t *node, int *ch, byte *fin, int *offset);",
		"void\tHuff_offsetTransmit (huff_t *huff, int ch, byte *fout, int *offset);",
		"void\tHuff_putBit( int bit, byte *fout, int *offset);",
		"int\t\tHuff_getBit( byte *fout, int *offset);",
	):
		assert expected in qcommon_h

	for expected in (
		"FUN_004d3790,004d3790,59,0,unknown",
		"FUN_004d37d0,004d37d0,44,0,unknown",
		"FUN_004d3980,004d3980,415,0,unknown",
		"FUN_004d3b20,004d3b20,94,0,unknown",
		"FUN_004d3b80,004d3b80,113,0,unknown",
		"FUN_004d3c90,004d3c90,396,0,unknown",
		"FUN_004d3e20,004d3e20,61,0,unknown",
		"FUN_004d3e60,004d3e60,645,0,unknown",
		"FUN_004d40f0,004d40f0,357,0,unknown",
		"FUN_004d4260,004d4260,225,0,unknown",
		"FUN_004d6bb0,004d6bb0,87,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004d3790    int32_t sub_4d3790(char arg1, int32_t arg2, int32_t* arg3)",
		"004d37aa      *((eax s>> 3) + arg2) = 0",
		"004d37bd  *esi_5 |= ebx.b",
		"004d37c6  *arg3 = eax + 1",
		"004d37d0    int32_t sub_4d37d0(int32_t arg1, int32_t* arg2)",
		"004d37ed  int32_t result = zx.d(*((edx s>> 3) + arg1)) u>> (edx.b & 7) & 1",
		"004d37f1  *arg2 = edx + 1",
		"004d3980    int32_t sub_4d3980(int32_t* arg1, char arg2)",
		"004d3990  if (ecx_1 != 0)",
		"004d3afd  arg1[zx.d(arg2) + 5] = &arg1[ecx_2 * 8 + 0x107]",
		"004d3b20    int32_t sub_4d3b20(void** arg1, int32_t* arg2, int32_t arg3)",
		"004d3b4d          uint32_t eax_4 = zx.d(*((edx_1 s>> 3) + arg3)) u>> (edx_1.b & 7)",
		"004d3b80    void sub_4d3b80(void** arg1, int32_t* arg2, int32_t arg3, int32_t* arg4)",
		"004d3be9              *arg4 = edx",
		"004d3c90    char* sub_4d3c90(int32_t arg1, int32_t arg2, char* arg3)",
		"004d3cb1  sub_4d3c90(arg1, 0x100, arg3)",
		"004d3dfc  data_1239df0 = eax + 8",
		"004d3e20    void* sub_4d3e20(int32_t arg1, int32_t arg2, int32_t arg3, int32_t* arg4)",
		"004d3e36  data_1239df0 = edx",
		"004d3e53  *arg4 = eax_2",
		"004d3e60    int32_t sub_4d3e60(void* arg1, int32_t arg2)",
		"004d3f2f      uint32_t edi_3 = (zx.d(*esi_1) << 8) + zx.d(esi_1[1])",
		"004d3f48      data_1239df0 = 0x10",
		"004d3f88              sub_4d3b20(&(&__saved_ebp)[ecx_1 * 8 - 0x5b01], &var_17030, esi_1)",
		"004d407f              sub_4d3980(&var_17024, var_14_3)",
		"004d40bb      *(arg1 + 0x10) = arg2 + edi_3",
		"004d40f0    int32_t sub_4d40f0(void* arg1, int32_t arg2)",
		"004d41bd      char var_10008 = (ebx_2 s>> 8).b",
		"004d41c3      char var_10007_1 = ebx_2.b",
		"004d41c9      data_1239df0 = 0x10",
		"004d41f9              sub_4d3c90(&var_17024, edi_1, &var_10008)",
		"004d4206              sub_4d3980(&var_17024, edi_1.b)",
		"004d4233      *(arg1 + 0x10) = eax_8 + result",
		"004d4260    void* sub_4d4260(char* arg1)",
		"004d4272  sub_4c95e0(arg1, 0, 0x701c)",
		"004d4284  sub_4c95e0(&arg1[0x701c], 0, 0x701c)",
		"004d42b9  *((ecx << 5) + arg1 + 0x7454) = 0x100",
		"004d430d  *((eax_6 << 5) + arg1 + 0x438) = 0x100",
		"004d6bb0    void* sub_4d6bb0()",
		"004d6bb8  data_124a630 = 1",
		"004d6bc2  void* result = sub_4d4260(&data_123c5f8)",
		"004d6be6              sub_4d3980(&data_123c5f8, esi.b)",
		"004d6bf1              result = sub_4d3980(&data_1243614, esi.b)",
	):
		assert expected in hlil_part04

	put_bit = _function_block(huffman_c, "void\tHuff_putBit( int bit, byte *fout, int *offset)")
	get_bit = _function_block(huffman_c, "int\t\tHuff_getBit( byte *fin, int *offset)")
	add_ref = _function_block(huffman_c, "void Huff_addRef(huff_t* huff, byte ch)")
	receive = _function_block(huffman_c, "int Huff_Receive (node_t *node, int *ch, byte *fin)")
	offset_receive = _function_block(huffman_c, "void Huff_offsetReceive (node_t *node, int *ch, byte *fin, int *offset)")
	transmit = _function_block(huffman_c, "void Huff_transmit (huff_t *huff, int ch, byte *fout)")
	offset_transmit = _function_block(huffman_c, "void Huff_offsetTransmit (huff_t *huff, int ch, byte *fout, int *offset)")
	decompress = _function_block(huffman_c, "void Huff_Decompress(msg_t *mbuf, int offset)")
	compress = _function_block(huffman_c, "void Huff_Compress(msg_t *mbuf, int offset)")
	init = _function_block(huffman_c, "void Huff_Init(huffman_t *huff)")
	msg_init_huffman = _function_block(msg_c, "void MSG_initHuffman() {")

	_assert_order(
		put_bit,
		"bloc = *offset;",
		"if ((bloc&7) == 0) {",
		"fout[(bloc>>3)] = 0;",
		"fout[(bloc>>3)] |= bit << (bloc&7);",
		"bloc++;",
		"*offset = bloc;",
	)

	_assert_order(
		get_bit,
		"bloc = *offset;",
		"t = (fin[(bloc>>3)] >> (bloc&7)) & 0x1;",
		"bloc++;",
		"*offset = bloc;",
		"return t;",
	)

	_assert_order(
		add_ref,
		"if (huff->loc[ch] == NULL)",
		"tnode = &(huff->nodeList[huff->blocNode++]);",
		"tnode2 = &(huff->nodeList[huff->blocNode++]);",
		"tnode2->symbol = INTERNAL_NODE;",
		"tnode->symbol = ch;",
		"huff->loc[ch] = tnode;",
		"increment(huff, tnode2->parent);",
		"} else {",
		"increment(huff, huff->loc[ch]);",
	)

	_assert_order(
		receive,
		"while (node && node->symbol == INTERNAL_NODE) {",
		"if (get_bit(fin)) {",
		"node = node->right;",
		"} else {",
		"node = node->left;",
		"if (!node) {",
		"return 0;",
		"return (*ch = node->symbol);",
	)

	_assert_order(
		offset_receive,
		"bloc = *offset;",
		"while (node && node->symbol == INTERNAL_NODE) {",
		"if (get_bit(fin)) {",
		"node = node->right;",
		"} else {",
		"node = node->left;",
		"if (!node) {",
		"*ch = 0;",
		"*ch = node->symbol;",
		"*offset = bloc;",
	)

	_assert_order(
		transmit,
		"if (huff->loc[ch] == NULL) {",
		"Huff_transmit(huff, NYT, fout);",
		"for (i = 7; i >= 0; i--) {",
		"add_bit((char)((ch >> i) & 0x1), fout);",
		"} else {",
		"send(huff->loc[ch], NULL, fout);",
	)

	_assert_order(
		offset_transmit,
		"bloc = *offset;",
		"send(huff->loc[ch], NULL, fout);",
		"*offset = bloc;",
	)

	_assert_order(
		decompress,
		"size = mbuf->cursize - offset;",
		"buffer = mbuf->data + offset;",
		"if ( size <= 0 ) {",
		"Com_Memset(&huff, 0, sizeof(huff_t));",
		"huff.tree = huff.lhead = huff.ltail = huff.loc[NYT] = &(huff.nodeList[huff.blocNode++]);",
		"cch = buffer[0]*256 + buffer[1];",
		"if ( cch > mbuf->maxsize - offset ) {",
		"cch = mbuf->maxsize - offset;",
		"bloc = 16;",
		"if ( (bloc >> 3) > size ) {",
		"Huff_Receive(huff.tree, &ch, buffer);",
		"if ( ch == NYT ) {",
		"for ( i = 0; i < 8; i++ ) {",
		"ch = (ch<<1) + get_bit(buffer);",
		"Huff_addRef(&huff, (byte)ch);",
		"mbuf->cursize = cch + offset;",
		"Com_Memcpy(mbuf->data + offset, seq, cch);",
	)

	_assert_order(
		compress,
		"size = mbuf->cursize - offset;",
		"buffer = mbuf->data+ + offset;",
		"if (size<=0) {",
		"Com_Memset(&huff, 0, sizeof(huff_t));",
		"huff.tree = huff.lhead = huff.loc[NYT] =  &(huff.nodeList[huff.blocNode++]);",
		"seq[0] = (size>>8);",
		"seq[1] = size&0xff;",
		"bloc = 16;",
		"ch = buffer[i];",
		"Huff_transmit(&huff, ch, seq);",
		"Huff_addRef(&huff, (byte)ch);",
		"bloc += 8;",
		"mbuf->cursize = (bloc>>3) + offset;",
		"Com_Memcpy(mbuf->data+offset, seq, (bloc>>3));",
	)

	_assert_order(
		init,
		"Com_Memset(&huff->compressor, 0, sizeof(huff_t));",
		"Com_Memset(&huff->decompressor, 0, sizeof(huff_t));",
		"huff->decompressor.tree = huff->decompressor.lhead = huff->decompressor.ltail = huff->decompressor.loc[NYT] = &(huff->decompressor.nodeList[huff->decompressor.blocNode++]);",
		"huff->decompressor.tree->symbol = NYT;",
		"huff->compressor.tree = huff->compressor.lhead = huff->compressor.loc[NYT] =  &(huff->compressor.nodeList[huff->compressor.blocNode++]);",
		"huff->compressor.tree->symbol = NYT;",
		"huff->compressor.loc[NYT] = huff->compressor.tree;",
	)

	_assert_order(
		msg_init_huffman,
		"msgInit = qtrue;",
		"Huff_Init(&msgHuff);",
		"for(i=0;i<256;i++) {",
		"for (j=0;j<msg_hData[i];j++) {",
		"Huff_addRef(&msgHuff.compressor,\t(byte)i);",
		"Huff_addRef(&msgHuff.decompressor,\t(byte)i);",
	)

	assert "Huff_Compress( &mbuf, 12);" in _function_block(
		net_chan,
		"void QDECL NET_OutOfBandData( netsrc_t sock, netadr_t adr, byte *format, int len )",
	)
	_assert_order(
		_function_block(sv_main, "void SV_ConnectionlessPacket( netadr_t from, msg_t *msg )"),
		"MSG_BeginReadingOOB( msg );",
		"MSG_ReadLong( msg );",
		"if ( NET_ProtocolUsesCompressedConnect() && NET_IsConnectRequestPacket( msg ) ) {",
		"Huff_Decompress(msg, 12);",
		"}",
		"s = MSG_ReadStringLine( msg );",
	)

	for expected in (
		"`sub_4D3790 -> Huff_putBit`",
		"`sub_4D37D0 -> Huff_getBit`",
		"`sub_4D3980 -> Huff_addRef`",
		"`sub_4D3B20 -> Huff_Receive`",
		"`sub_4D3B80 -> Huff_offsetReceive`",
		"`sub_4D3C90 -> Huff_transmit`",
		"`sub_4D3E20 -> Huff_offsetTransmit`",
		"`sub_4D3E60 -> Huff_Decompress`",
		"`sub_4D40F0 -> Huff_Compress`",
		"`sub_4D4260 -> Huff_Init`",
		"`sub_4D6BB0 -> MSG_initHuffman`",
	):
		assert expected in (round_56 + round_57)

	assert "`Huff_Decompress(msg, 12)`" in round_65
	assert "Implementation round - 2026-06-04, Huffman compression manifest expansion" in plan


def test_manifest_covers_msg_scalar_data_wrapper_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	qcommon_h = _read(QCOMMON_H_PATH)
	msg_c = _read(MSG_C_PATH)
	plan = _read(PLAN_PATH)
	round_56 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_56.md")

	for symbol in (
		"MSG_WriteData",
		"MSG_WriteShort",
		"MSG_WriteLong",
		"MSG_ReadShort",
		"MSG_ReadLong",
	):
		assert entries[symbol]["status"] == "verified"
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_msg_scalar_data_wrapper_lane" in entries[symbol]["tests"]

	assert entries["MSG_WriteData"]["retail_address"] == "0x004D4DE0"
	assert entries["MSG_WriteShort"]["retail_address"] == "0x004D4E10"
	assert entries["MSG_WriteLong"]["retail_address"] == "0x004D4E30"
	assert entries["MSG_ReadShort"]["retail_address"] == "0x004D4FF0"
	assert entries["MSG_ReadLong"]["retail_address"] == "0x004D5020"

	for expected in (
		"void MSG_WriteData (msg_t *buf, const void *data, int length);",
		"void MSG_WriteShort (msg_t *sb, int c);",
		"void MSG_WriteLong (msg_t *sb, int c);",
		"int\t\tMSG_ReadShort (msg_t *sb);",
		"int\t\tMSG_ReadLong (msg_t *sb);",
	):
		assert expected in qcommon_h

	for expected in (
		"FUN_004d4de0,004d4de0,47,0,unknown",
		"FUN_004d4e10,004d4e10,23,0,unknown",
		"FUN_004d4e30,004d4e30,23,0,unknown",
		"FUN_004d4ff0,004d4ff0,33,0,unknown",
		"FUN_004d5020,004d5020,32,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004d4de0    void sub_4d4de0(int32_t* arg1, int32_t arg2, int32_t arg3)",
		"004d4dec  if (arg3 s> 0)",
		"004d4dfd          sub_4d4af0(arg1, zx.d(*(esi + arg2)), 8)",
		"004d4e08      while (esi s< arg3)",
		"004d4e10    int32_t* sub_4d4e10(int32_t* arg1, int32_t arg2)",
		"004d4e26  return sub_4d4af0(arg1, arg2, 0x10)",
		"004d4e30    int32_t* sub_4d4e30(int32_t* arg1, int32_t arg2)",
		"004d4e46  return sub_4d4af0(arg1, arg2, 0x20)",
		"004d4ff0    int32_t sub_4d4ff0(void* arg1)",
		"004d5020    uint32_t sub_4d5020(void* arg1)",
	):
		assert expected in hlil_part04

	write_data = _function_block(msg_c, "void MSG_WriteData( msg_t *buf, const void *data, int length )")
	write_short = _function_block(msg_c, "void MSG_WriteShort( msg_t *sb, int c )")
	write_long = _function_block(msg_c, "void MSG_WriteLong( msg_t *sb, int c )")
	read_short = _function_block(msg_c, "int MSG_ReadShort( msg_t *msg )")
	read_long = _function_block(msg_c, "int MSG_ReadLong( msg_t *msg )")

	_assert_order(
		write_data,
		"int i;",
		"for(i=0;i<length;i++) {",
		"MSG_WriteByte(buf, ((byte *)data)[i]);",
	)
	assert "Com_Memcpy" not in write_data

	assert "MSG_WriteBits( sb, c, 16 );" in write_short
	assert "MSG_WriteBits( sb, c, 32 );" in write_long

	_assert_order(
		read_short,
		"c = (short)MSG_ReadBits( msg, 16 );",
		"if ( msg->readcount > msg->cursize ) {",
		"c = -1;",
		"return c;",
	)

	_assert_order(
		read_long,
		"c = MSG_ReadBits( msg, 32 );",
		"if ( msg->readcount > msg->cursize ) {",
		"c = -1;",
		"return c;",
	)

	for expected in (
		"`sub_4D4DE0 -> MSG_WriteData`",
		"`sub_4D4E10 -> MSG_WriteShort`",
		"`sub_4D4E30 -> MSG_WriteLong`",
		"`sub_4D4FF0 -> MSG_ReadShort`",
		"`sub_4D5020 -> MSG_ReadLong`",
		"The standalone `MSG_WriteChar`, `MSG_BeginReading`, and `MSG_Init*` entry",
	):
		assert expected in round_56

	assert "Implementation round - 2026-06-04, MSG scalar data wrapper manifest expansion" in plan


def test_manifest_covers_msg_change_vector_reporter_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	ghidra_decompile_top = _read(GHIDRA_DECOMPILE_TOP_PATH)
	alias_map = _read(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json")
	qcommon_h = _read(QCOMMON_H_PATH)
	msg_c = _read(MSG_C_PATH)
	common_c = _read(COMMON_C_PATH)
	plan = _read(PLAN_PATH)
	round_57 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_57.md")

	entry = entries["MSG_ReportChangeVectors_f"]
	assert entry["status"] == "verified"
	assert entry["retail_address"] == "0x004D5750"
	assert "debug/report helper only; does not alter wire-format serialization" in entry["behavior_checkpoints"]
	assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_msg_change_vector_reporter_lane" in entry["tests"]

	for expected in (
		"void MSG_ReportChangeVectors_f( void );",
		"int pcount[256];",
	):
		assert expected in (qcommon_h + msg_c)

	for expected in (
		"004cc558      sub_4c81d0(\"changeVectors\", sub_4d5750)",
		"004d5750    int32_t sub_4d5750()",
		"004d5774  for (int32_t i = 0; i s< 0x100; i += 1)",
		"004d575c      if (result != 0)",
		"004d5765          result = sub_4c9860(i, \"%d used %d\\n\")",
	):
		assert expected in hlil_part04

	assert 'FUN_004c81d0("changeVectors",&LAB_004d5750);' in ghidra_decompile_top
	assert '"sub_4D5750": "MSG_ReportChangeVectors_f"' in alias_map

	reporter = _function_block(msg_c, "void MSG_ReportChangeVectors_f( void )")
	_assert_order(
		reporter,
		"int i;",
		"for(i=0;i<256;i++) {",
		"if (pcount[i]) {",
		"Com_Printf(\"%d used %d\\n\", i, pcount[i]);",
	)

	assert 'Cmd_AddCommand ("changeVectors", MSG_ReportChangeVectors_f );' in common_c

	for expected in (
		"`sub_4D5750 -> MSG_ReportChangeVectors_f`",
		"`sub_4D5750` is the exact debug command handler registered under",
		"`changeVectors`, iterating `pcount[256]` and printing `%d used %d\\n`.",
		"The `MSG_ReportChangeVectors_f` helper is an HLIL-backed closure rather than a",
	):
		assert expected in round_57

	assert "Implementation round - 2026-06-04, MSG change-vector reporter manifest expansion" in plan


def test_manifest_covers_msg_bitstream_primitive_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	qcommon_h = _read(QCOMMON_H_PATH)
	msg_c = _read(MSG_C_PATH)
	plan = _read(PLAN_PATH)
	round_56 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_56.md")
	round_57 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_57.md")

	for symbol in (
		"MSG_Init",
		"MSG_InitOOB",
		"MSG_Clear",
		"MSG_Bitstream",
		"MSG_BeginReadingOOB",
		"MSG_WriteBits",
		"MSG_ReadBits",
		"MSG_WriteByte",
		"MSG_WriteString",
		"MSG_WriteBigString",
		"MSG_ReadByte",
		"MSG_ReadString",
		"MSG_ReadBigString",
		"MSG_ReadStringLine",
	):
		assert entries[symbol]["status"] in {"verified", "reconstructed"}
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_msg_bitstream_primitive_lane" in entries[symbol]["tests"]

	for symbol in ("MSG_WriteString", "MSG_WriteBigString", "MSG_ReadString"):
		assert entries[symbol]["status"] == "reconstructed"
		assert "high-byte scrub loop was removed" in entries[symbol]["compatibility_notes"][0]

	assert entries["MSG_Init"]["retail_address"] == "0x004D6C10"
	assert entries["MSG_InitOOB"]["retail_address"] == "0x004D6C50"
	assert entries["MSG_Clear"]["retail_address"] == "0x004D4A50"
	assert entries["MSG_Bitstream"]["retail_address"] == "0x004D4A70"
	assert entries["MSG_BeginReadingOOB"]["retail_address"] == "0x004D4A80"
	assert entries["MSG_WriteBits"]["retail_address"] == "0x004D4AF0"
	assert entries["MSG_ReadBits"]["retail_address"] == "0x004D4C70"
	assert entries["MSG_WriteByte"]["retail_address"] == "0x004D4DC0"
	assert entries["MSG_WriteString"]["retail_address"] == "0x004D4E50"
	assert entries["MSG_WriteBigString"]["retail_address"] == "0x004D4F00"
	assert entries["MSG_ReadByte"]["retail_address"] == "0x004D4FC0"
	assert entries["MSG_ReadString"]["retail_address"] == "0x004D5040"
	assert entries["MSG_ReadBigString"]["retail_address"] == "0x004D50A0"
	assert entries["MSG_ReadStringLine"]["retail_address"] == "0x004D5100"

	for expected in (
		"void MSG_Init (msg_t *buf, byte *data, int length);",
		"void MSG_InitOOB( msg_t *buf, byte *data, int length );",
		"void MSG_Clear (msg_t *buf);",
		"void MSG_Bitstream( msg_t *buf );",
		"void MSG_WriteBits( msg_t *msg, int value, int bits );",
		"int\t\tMSG_ReadBits( msg_t *msg, int bits );",
		"char\t*MSG_ReadString (msg_t *sb);",
		"char\t*MSG_ReadBigString (msg_t *sb);",
	):
		assert expected in qcommon_h

	for expected in (
		"FUN_004d6c10,004d6c10,49,0,unknown",
		"FUN_004d6c50,004d6c50,56,0,unknown",
		"FUN_004d4a50,004d4a50,18,0,unknown",
		"FUN_004d4a70,004d4a70,15,0,unknown",
		"FUN_004d4a80,004d4a80,23,0,unknown",
		"FUN_004d4af0,004d4af0,371,0,unknown",
		"FUN_004d4c70,004d4c70,333,0,unknown",
		"FUN_004d4dc0,004d4dc0,23,0,unknown",
		"FUN_004d4e50,004d4e50,174,0,unknown",
		"FUN_004d4f00,004d4f00,177,0,unknown",
		"FUN_004d4fc0,004d4fc0,35,0,unknown",
		"FUN_004d5040,004d5040,91,0,unknown",
		"FUN_004d50a0,004d50a0,91,0,unknown",
		"FUN_004d5100,004d5100,96,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004d4a50    int32_t* sub_4d4a50(int32_t* arg1)",
		"004d4a58  arg1[4] = 0",
		"004d4a5b  *arg1 = 0",
		"004d4a5d  arg1[6] = 0",
		"004d4a70    void* sub_4d4a70(void* arg1)",
		"004d4a76  *(arg1 + 4) = 0",
		"004d4a80    void* sub_4d4a80(void* arg1)",
		"004d4a88  *(arg1 + 0x14) = 0",
		"004d4a8b  *(arg1 + 0x18) = 0",
		"004d4a8e  *(arg1 + 4) = 1",
		"004d4af0    int32_t* sub_4d4af0(int32_t* arg1, int32_t arg2, void* arg3)",
		"004d4b22  if (__saved_ebx_1 == 0 || __saved_ebx_1 s< 0xffffffe1 || __saved_ebx_1 s> 0x20)",
		"004d4b2c      sub_4c9b60(1, \"MSG_WriteBits: bad bits %i\")",
		"004d4b7c  if (arg1[1] != 0)",
		"004d4ba6              *(arg1[2] + eax_4) = arg2.w",
		"004d4bc1          *(arg1[2] + arg1[4]) = arg2",
		"004d4bc8          arg1[6] += 8",
		"004d4c12              sub_4d3790(ebx_1.b & 1, arg1[2], &arg1[6])",
		"004d4c46          eax_7 = sub_4d3e20(&data_123c5f8, zx.d(ebx_1.b), arg1[2], &arg1[6])",
		"004d4c5d  arg1[4] = (arg1[6] s>> 3) + 1",
		"004d4c70    uint32_t sub_4d4c70(void* arg1, int32_t arg2)",
		"004d4c82  if (__saved_ebx_1 s>= 0)",
		"004d4c9b  if (*(esi + 4) == 0)",
		"004d4d25                  int32_t eax_3 = sub_4d37d0(*(esi + 8), esi + 0x18) << edi.b",
		"004d4d56                  sub_4d3b80(data_124361c, &arg1, *(esi + 8), esi + 0x18)",
		"004d4d7a      ecx_1 = (*(esi + 0x18) s>> 3) + 1",
		"004d4dab  return not.d((1 << __saved_ebx_1.b) - 1) | result",
		"004d4dc0    int32_t* sub_4d4dc0(int32_t* arg1, int32_t arg2)",
		"004d4dd6  return sub_4d4af0(arg1, arg2, 8)",
		"004d4e50    int32_t* sub_4d4e50(int32_t* arg1, char* arg2)",
		"004d4e6c  if (arg2 == 0)",
		"004d4ea1  if (eax_4 s< 0x400)",
		"004d4ed7      sub_4d8f40(&var_408, arg2, 0x400)",
		"004d4ee6      int32_t eax_6 = sub_4d4de0(arg1, &var_408, eax_4 + 1)",
		"004d4ea8  sub_4c9860(eax_4, \"MSG_WriteString: MAX_STRING_CHAR",
		"004d4f00    int32_t* sub_4d4f00(int32_t arg1 @ edi, int32_t* arg2, char* arg3)",
		"004d4f54  if (eax_4 s< 0x2000)",
		"004d4f8a      void var_2008",
		"004d4f99      int32_t eax_6 = sub_4d4de0(arg2, &var_2008, eax_4 + 1)",
		"004d4f5b  sub_4c9860(eax_4, \"MSG_WriteString: BIG_INFO_STRING\")",
		"004d4fc0    uint32_t sub_4d4fc0(void* arg1)",
		"004d4fd8  uint32_t result = zx.d(sub_4d4c70(arg1, 8))",
		"004d4fde  return 0xffffffff",
		"004d5040    int32_t sub_4d5040(void* arg1)",
		"004d5089  for (i = 0; i u< 0x3ff; i += 1)",
		"004d5075      if (eax_2 == 0x25)",
		"004d5077          eax_2 = 0x2e",
		"004d50a0    int32_t sub_4d50a0(void* arg1)",
		"004d50e9  void* i",
		"004d50d5      if (eax_2 == 0x25)",
		"004d5100    int32_t sub_4d5100(void* arg1)",
		"004d5135      if (eax_2 == 0xa)",
		"004d513a      if (eax_2 == 0x25)",
		"004d6c10    int32_t sub_4d6c10(char* arg1, int32_t arg2, int32_t arg3)",
		"004d6c1a  if (data_124a630 == 0)",
		"004d6c2a  sub_4c95e0(arg1, 0, 0x1c)",
		"004d6c38  *(arg1 + 8) = arg2",
		"004d6c50    int32_t sub_4d6c50(char* arg1, int32_t arg2, int32_t arg3)",
		"004d6c7e  *(arg1 + 4) = 1",
	):
		assert expected in hlil_part04

	msg_init = _function_block(msg_c, "void MSG_Init( msg_t *buf, byte *data, int length )")
	msg_init_oob = _function_block(msg_c, "void MSG_InitOOB( msg_t *buf, byte *data, int length )")
	clear = _function_block(msg_c, "void MSG_Clear( msg_t *buf )")
	bitstream = _function_block(msg_c, "void MSG_Bitstream( msg_t *buf )")
	begin_oob = _function_block(msg_c, "void MSG_BeginReadingOOB( msg_t *msg )")
	write_bits = _function_block(msg_c, "void MSG_WriteBits( msg_t *msg, int value, int bits )")
	read_bits = _function_block(msg_c, "int MSG_ReadBits( msg_t *msg, int bits )")
	write_byte = _function_block(msg_c, "void MSG_WriteByte( msg_t *sb, int c )")
	write_string = _function_block(msg_c, "void MSG_WriteString( msg_t *sb, const char *s )")
	write_big_string = _function_block(msg_c, "void MSG_WriteBigString( msg_t *sb, const char *s )")
	read_byte = _function_block(msg_c, "int MSG_ReadByte( msg_t *msg )")
	read_string = _function_block(msg_c, "char *MSG_ReadString( msg_t *msg )")
	read_big_string = _function_block(msg_c, "char *MSG_ReadBigString( msg_t *msg )")
	read_string_line = _function_block(msg_c, "char *MSG_ReadStringLine( msg_t *msg )")

	_assert_order(
		msg_init,
		"if (!msgInit) {",
		"MSG_initHuffman();",
		"Com_Memset (buf, 0, sizeof(*buf));",
		"buf->data = data;",
		"buf->maxsize = length;",
	)

	_assert_order(
		msg_init_oob,
		"if (!msgInit) {",
		"MSG_initHuffman();",
		"Com_Memset (buf, 0, sizeof(*buf));",
		"buf->data = data;",
		"buf->maxsize = length;",
		"buf->oob = qtrue;",
	)

	_assert_order(clear, "buf->cursize = 0;", "buf->overflowed = qfalse;", "buf->bit = 0;")
	assert "buf->oob = qfalse;" in bitstream
	_assert_order(begin_oob, "msg->readcount = 0;", "msg->bit = 0;", "msg->oob = qtrue;")

	_assert_order(
		write_bits,
		"oldsize += bits;",
		"if ( msg->maxsize - msg->cursize < 4 ) {",
		"msg->overflowed = qtrue;",
		"if ( bits == 0 || bits < -31 || bits > 32 ) {",
		"Com_Error( ERR_DROP, \"MSG_WriteBits: bad bits %i\", bits );",
		"if ( bits != 32 ) {",
		"overflows++;",
		"if ( bits < 0 ) {",
		"bits = -bits;",
		"if (msg->oob) {",
		"if (bits==8) {",
		"msg->data[msg->cursize] = value;",
		"} else if (bits==16) {",
		"*sp = LittleShort(value);",
		"} else if (bits==32) {",
		"*ip = LittleLong(value);",
		"msg->cursize += 4;",
		"msg->bit += 8;",
		"Com_Error(ERR_DROP, \"can't read %d bits\\n\", bits);",
		"value &= (0xffffffff>>(32-bits));",
		"Huff_putBit((value&1), msg->data, &msg->bit);",
		"Huff_offsetTransmit (&msgHuff.compressor, (value&0xff), msg->data, &msg->bit);",
		"msg->cursize = (msg->bit>>3)+1;",
	)

	_assert_order(
		read_bits,
		"if ( bits < 0 ) {",
		"bits = -bits;",
		"sgn = qtrue;",
		"if (msg->oob) {",
		"if (bits==8) {",
		"value = msg->data[msg->readcount];",
		"} else if (bits==16) {",
		"value = LittleShort(*sp);",
		"} else if (bits==32) {",
		"value = LittleLong(*ip);",
		"Com_Error(ERR_DROP, \"can't read %d bits\\n\", bits);",
		"Huff_getBit(msg->data, &msg->bit)<<i",
		"Huff_offsetReceive (msgHuff.decompressor.tree, &get, msg->data, &msg->bit);",
		"msg->readcount = (msg->bit>>3)+1;",
		"if ( sgn ) {",
		"value |= -1 ^ ( ( 1 << bits ) - 1 );",
	)

	assert "MSG_WriteBits( sb, c, 8 );" in write_byte

	_assert_order(
		write_string,
		"if ( !s ) {",
		"MSG_WriteData (sb, \"\", 1);",
		"l = strlen( s );",
		"if ( l >= MAX_STRING_CHARS ) {",
		"Com_Printf( \"MSG_WriteString: MAX_STRING_CHARS\" );",
		"Q_strncpyz( string, s, sizeof( string ) );",
		"MSG_WriteData (sb, string, l+1);",
	)
	assert "> 127" not in write_string
	assert "old clients don't like" not in write_string

	_assert_order(
		write_big_string,
		"if ( !s ) {",
		"MSG_WriteData (sb, \"\", 1);",
		"l = strlen( s );",
		"if ( l >= BIG_INFO_STRING ) {",
		"Com_Printf( \"MSG_WriteString: BIG_INFO_STRING\" );",
		"Q_strncpyz( string, s, sizeof( string ) );",
		"MSG_WriteData (sb, string, l+1);",
	)
	assert "> 127" not in write_big_string
	assert "old clients don't like" not in write_big_string

	_assert_order(read_byte, "c = (unsigned char)MSG_ReadBits( msg, 8 );", "if ( msg->readcount > msg->cursize ) {", "c = -1;")

	_assert_order(
		read_string,
		"c = MSG_ReadByte(msg);",
		"if ( c == -1 || c == 0 ) {",
		"if ( c == '%' ) {",
		"c = '.';",
		"string[l] = c;",
	)
	assert "> 127" not in read_string

	_assert_order(
		read_big_string,
		"c = MSG_ReadByte(msg);",
		"if ( c == -1 || c == 0 ) {",
		"if ( c == '%' ) {",
		"c = '.';",
		"string[l] = c;",
	)

	_assert_order(
		read_string_line,
		"c = MSG_ReadByte(msg);",
		"if (c == -1 || c == 0 || c == '\\n') {",
		"if ( c == '%' ) {",
		"c = '.';",
		"string[l] = c;",
	)

	for expected in (
		"`sub_4D4A50 -> MSG_Clear`",
		"`sub_4D4A70 -> MSG_Bitstream`",
		"`sub_4D4A80 -> MSG_BeginReadingOOB`",
		"`sub_4D4AF0 -> MSG_WriteBits`",
		"`sub_4D4C70 -> MSG_ReadBits`",
		"`sub_4D4DC0 -> MSG_WriteByte`",
		"`sub_4D4E50 -> MSG_WriteString`",
		"`sub_4D4F00 -> MSG_WriteBigString`",
		"`sub_4D4FC0 -> MSG_ReadByte`",
		"`sub_4D5040 -> MSG_ReadString`",
		"`sub_4D50A0 -> MSG_ReadBigString`",
		"`sub_4D5100 -> MSG_ReadStringLine`",
		"`sub_4D6C10 -> MSG_Init`",
		"`sub_4D6C50 -> MSG_InitOOB`",
		"`MSG_WriteBits: bad bits %i` and `can't read %d bits\\n` diagnostics",
	):
		assert expected in (round_56 + round_57)

	assert "Implementation round - 2026-06-04, MSG bitstream primitive reconstruction" in plan


def test_manifest_covers_msg_entity_playerstate_delta_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	msg_c = _read(MSG_C_PATH)
	plan = _read(PLAN_PATH)
	round_56 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_56.md")
	round_57 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_57.md")
	playerstate_test = _read(REPO_ROOT / "tests/test_playerstate_replication.py")
	event_transport_test = _read(REPO_ROOT / "tests/test_cgame_event_transport_parity.py")

	for symbol in (
		"MSG_ReadData",
		"MSG_WriteDeltaEntity",
		"MSG_ReadDeltaEntity",
		"MSG_WriteDeltaPlayerstate",
		"MSG_ReadDeltaPlayerstate",
	):
		assert entries[symbol]["status"] == "verified"
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_msg_entity_playerstate_delta_lane" in entries[symbol]["tests"]

	assert entries["MSG_ReadData"]["retail_address"] == "0x004D5160"
	assert entries["MSG_WriteDeltaEntity"]["retail_address"] == "0x004D5780"
	assert entries["MSG_ReadDeltaEntity"]["retail_address"] == "0x004D5AC0"
	assert entries["MSG_WriteDeltaPlayerstate"]["retail_address"] == "0x004D5D50"
	assert entries["MSG_ReadDeltaPlayerstate"]["retail_address"] == "0x004D66C0"
	assert "tests/test_playerstate_replication.py::test_playerstate_delta_codec_preserves_retail_signed_byte_and_array_mask_wiring" in entries["MSG_WriteDeltaPlayerstate"]["tests"]
	assert "tests/test_cgame_event_transport_parity.py::test_shared_entity_state_restores_retail_event_data_slot" in entries["MSG_WriteDeltaEntity"]["tests"]

	for expected in (
		"FUN_004d5160,004d5160,59,0,unknown",
		"FUN_004d5780,004d5780,828,0,unknown",
		"FUN_004d5ac0,004d5ac0,654,0,unknown",
		"FUN_004d5d50,004d5d50,2398,0,unknown",
		"FUN_004d66c0,004d66c0,1250,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004d5160    void sub_4d5160(void* arg1, int32_t arg2, int32_t arg3)",
		"004d5180          char eax = sub_4d4c70(arg1, 8)",
		"004d5188              eax = -1",
		"004d518e          esi[arg2] = eax",
		"004d5780    int32_t* sub_4d5780(int32_t* arg1, int32_t* arg2, int32_t* arg3, int32_t arg4)",
		"004d57c6      if (__saved_ebx_1 s< 0 || __saved_ebx_1 s>= 0x400)",
		"004d57d0          sub_4c9b60(0, \"MSG_WriteDeltaEntity: Bad entity",
		"004d583a          sub_4d4af0(arg1, *arg3, 0xa)",
		"004d585a          return sub_4d4af0(arg1, i_4, 1)",
		"004d5864          sub_4d4af0(arg1, *arg3, 0xa)",
		"004d590a          result = sub_4d4af0(arg1, i_4, 8)",
		"004d5a5d                                  sub_4d4af0(arg1, 0, 1)",
		"004d5aa3                                  result = sub_4d4af0(arg1, *(edi_3 + arg3), 0x20)",
		"004d5ac0    int32_t sub_4d5ac0(void* arg1, int32_t arg2, int32_t* arg3, void* const arg4)",
		"004d5ad6  if (arg4 s< 0 || arg4 s>= 0x400)",
		"004d5ae0      sub_4c9b60(1, \"Bad delta entity number: %i\")",
		"004d5b26      sub_4c95e0(arg3, 0, 0xec)",
		"004d5b2b      *arg3 = 0x3ff",
		"004d5b80          __builtin_memcpy(dest: arg3, src: arg2, n: 0xec)",
		"004d5b96      uint32_t i_4 = zx.d(sub_4d4c70(ebx, 8))",
		"004d5c5b                          eax_16 = sub_4d4c70(ebx, 0xd) - 0x1000",
		"004d5d3f          return sub_4c9860(i_4, \" (%i bits)\\n\")",
		"004d5d50    int32_t* sub_4d5d50(int32_t* arg1, char (* arg2)[0x250], void* arg3)",
		"004d5d6d  if (arg2 == 0)",
		"004d5dee  sub_4d4af0(arg1, i_20, 8)",
		"004d5f37                      sub_4d4af0(arg1, edi_3 + 0x1000, 0xd)",
		"004d61fd  if (var_260_1 == 0 && var_26c == var_260_1 && var_268 == var_260_1",
		"004d633e      sub_4d4af0(arg1, var_260_1, 0x10)",
		"004d6429      sub_4d4af0(arg1, var_26c, 0x10)",
		"004d650f      eax_47 = sub_4d4af0(arg1, var_268, 0x10)",
		"004d65f9  int32_t* eax_52 = sub_4d4af0(arg1, var_25c, 0x10)",
		"004d6624          eax_52 = sub_4d4af0(arg1, *ebx_15, 0x20)",
		"004d66c0    uint32_t sub_4d66c0(int32_t arg1 @ esi, void* arg2, char (* arg3)[0x250], void* arg4)",
		"004d66e5  if (arg3 == 0)",
		"004d670b  int32_t* esi_1 = __builtin_memcpy(dest: arg4, src: arg3, n: 0x250)",
		"004d675f      sub_4c9860(esi_1, \"%3i: playerstate \")",
		"004d6772  uint32_t i_12 = zx.d(sub_4d4c70(arg2, 8))",
		"004d67ef                  int32_t eax_9 = sub_4d4c70(arg2, 0xd) - 0x1000",
		"004d68f8              char const* const var_280_5 = \"PS_STATS\"",
		"004d699d              char const* const var_280_6 = \"PS_PERSISTANT\"",
		"004d6a3d              char const* const var_280_7 = \"PS_AMMO\"",
		"004d6add              char const* const var_280_8 = \"PS_POWERUPS\"",
	):
		assert expected in hlil_part04

	read_data = _function_block(msg_c, "void MSG_ReadData( msg_t *msg, void *data, int len )")
	write_entity = _function_block(msg_c, "void MSG_WriteDeltaEntity( msg_t *msg, struct entityState_s *from, struct entityState_s *to,")
	read_entity = _function_block(msg_c, "void MSG_ReadDeltaEntity( msg_t *msg, entityState_t *from, entityState_t *to,")
	write_playerstate = _function_block(msg_c, "void MSG_WriteDeltaPlayerstate( msg_t *msg, struct playerState_s *from, struct playerState_s *to )")
	read_playerstate = _function_block(msg_c, "void MSG_ReadDeltaPlayerstate (msg_t *msg, playerState_t *from, playerState_t *to )")

	_assert_order(
		read_data,
		"for (i=0 ; i<len ; i++) {",
		"((byte *)data)[i] = MSG_ReadByte (msg);",
	)

	assert "{ NETF(generic1), 8 }" in msg_c
	assert "{ NETF(retailEventData), 8 }" not in msg_c
	_assert_order(
		write_entity,
		"if ( to == NULL ) {",
		"MSG_WriteBits( msg, from->number, GENTITYNUM_BITS );",
		"MSG_WriteBits( msg, 1, 1 );",
		"if ( to->number < 0 || to->number >= MAX_GENTITIES ) {",
		"Com_Error (ERR_FATAL, \"MSG_WriteDeltaEntity: Bad entity number: %i\", to->number );",
		"for ( i = 0, field = entityStateFields ; i < numFields ; i++, field++ ) {",
		"if ( lc == 0 ) {",
		"if ( !force ) {",
		"MSG_WriteBits( msg, to->number, GENTITYNUM_BITS );",
		"MSG_WriteBits( msg, 0, 1 );\t\t// not removed",
		"MSG_WriteBits( msg, 0, 1 );\t\t// no delta",
		"MSG_WriteByte( msg, lc );\t// # of changes",
		"if ( field->bits == 0 ) {",
		"if (fullFloat == 0.0f) {",
		"MSG_WriteBits( msg, trunc + FLOAT_INT_BIAS, FLOAT_INT_BITS );",
		"MSG_WriteBits( msg, *toF, 32 );",
		"MSG_WriteBits( msg, *toF, field->bits );",
	)

	_assert_order(
		read_entity,
		"if ( number < 0 || number >= MAX_GENTITIES) {",
		"Com_Error( ERR_DROP, \"Bad delta entity number: %i\", number );",
		"if ( MSG_ReadBits( msg, 1 ) == 1 ) {",
		"Com_Memset( to, 0, sizeof( *to ) );",
		"to->number = MAX_GENTITIES - 1;",
		"if ( MSG_ReadBits( msg, 1 ) == 0 ) {",
		"*to = *from;",
		"to->number = number;",
		"lc = MSG_ReadByte(msg);",
		"to->number = number;",
		"if ( ! MSG_ReadBits( msg, 1 ) ) {",
		"*toF = *fromF;",
		"if ( field->bits == 0 ) {",
		"*(float *)toF = 0.0f;",
		"trunc = MSG_ReadBits( msg, FLOAT_INT_BITS );",
		"trunc -= FLOAT_INT_BIAS;",
		"*toF = MSG_ReadBits( msg, 32 );",
		"*toF = MSG_ReadBits( msg, field->bits );",
		"for ( i = lc, field = &entityStateFields[lc] ; i < numFields ; i++, field++ ) {",
	)

	for expected in (
		"{ PSF(weaponPrimary), 8 }",
		"{ PSF(fov), 8 }",
		"{ PSF(forwardmove), 8 }",
		"{ PSF(rightmove), 8 }",
		"{ PSF(upmove), 8 }",
		"static qboolean MSG_PlayerStateFieldIsSignedByte",
		"MSG_PlayerStateFieldNetworkValue( to, field )",
		"MSG_SetPlayerStateFieldValue( to, field, value );",
	):
		assert expected in msg_c

	_assert_order(
		write_playerstate,
		"if (!from) {",
		"Com_Memset (&dummy, 0, sizeof(dummy));",
		"lc = 0;",
		"fromValue = MSG_PlayerStateFieldValue( from, field );",
		"toValue = MSG_PlayerStateFieldValue( to, field );",
		"MSG_WriteByte( msg, lc );\t// # of changes",
		"oldsize += numFields - lc;",
		"MSG_WriteBits( msg, 1, 1 );\t// changed",
		"MSG_WriteBits( msg, trunc + FLOAT_INT_BIAS, FLOAT_INT_BITS );",
		"MSG_WriteBits( msg, *toF, 32 );",
		"MSG_WriteBits( msg, MSG_PlayerStateFieldNetworkValue( to, field ), field->bits );",
		"statsbits = 0;",
		"persistantbits = 0;",
		"ammobits = 0;",
		"powerupbits = 0;",
		"if (!statsbits && !persistantbits && !ammobits && !powerupbits) {",
		"MSG_WriteShort( msg, statsbits );",
		"MSG_WriteShort (msg, to->stats[i]);",
		"MSG_WriteShort( msg, persistantbits );",
		"MSG_WriteShort (msg, to->persistant[i]);",
		"MSG_WriteShort( msg, ammobits );",
		"MSG_WriteShort (msg, to->ammo[i]);",
		"MSG_WriteShort( msg, powerupbits );",
		"MSG_WriteLong( msg, to->powerups[i] );",
	)

	_assert_order(
		read_playerstate,
		"if ( !from ) {",
		"Com_Memset( &dummy, 0, sizeof( dummy ) );",
		"*to = *from;",
		"lc = MSG_ReadByte(msg);",
		"if ( ! MSG_ReadBits( msg, 1 ) ) {",
		"MSG_SetPlayerStateFieldValue( to, field, MSG_PlayerStateFieldValue( from, field ) );",
		"if ( field->bits == 0 ) {",
		"trunc = MSG_ReadBits( msg, FLOAT_INT_BITS );",
		"trunc -= FLOAT_INT_BIAS;",
		"*toF = MSG_ReadBits( msg, 32 );",
		"value = MSG_ReadBits( msg, field->bits );",
		"MSG_SetPlayerStateFieldValue( to, field, value );",
		"for ( i=lc,field = &playerStateFields[lc];i<numFields; i++, field++) {",
		"MSG_SetPlayerStateFieldValue( to, field, MSG_PlayerStateFieldValue( from, field ) );",
		"if (MSG_ReadBits( msg, 1 ) ) {",
		"LOG(\"PS_STATS\");",
		"to->stats[i] = MSG_ReadShort(msg);",
		"LOG(\"PS_PERSISTANT\");",
		"to->persistant[i] = MSG_ReadShort(msg);",
		"LOG(\"PS_AMMO\");",
		"to->ammo[i] = MSG_ReadShort(msg);",
		"LOG(\"PS_POWERUPS\");",
		"to->powerups[i] = MSG_ReadLong(msg);",
	)

	for expected in (
		"`sub_4D5160 -> MSG_ReadData`",
		"`sub_4D5780 -> MSG_WriteDeltaEntity`",
		"`sub_4D5AC0 -> MSG_ReadDeltaEntity`",
		"`sub_4D5D50 -> MSG_WriteDeltaPlayerstate`",
		"`sub_4D66C0 -> MSG_ReadDeltaPlayerstate`",
		"`MSG_WriteDeltaEntity: Bad entity number`",
		"`Bad delta entity number: %i`",
		"`PS_STATS`",
		"`PS_PERSISTANT`",
		"`PS_AMMO`",
		"`PS_POWERUPS`",
	):
		assert expected in (round_56 + round_57)

	for expected in (
		"test_playerstate_delta_codec_preserves_retail_signed_byte_and_array_mask_wiring",
		"test_playerstate_netfield_table_matches_retail_quake_live_scalar_order",
		"assert values.forwardmove == -127",
		"assert offsets.forwardmove == 0x1DC",
	):
		assert expected in playerstate_test

	for expected in (
		"test_shared_entity_state_restores_retail_event_data_slot",
		"assert \"{ NETF(generic1), 8 }\" in msg_source",
		"assert \"{ NETF(retailEventData), 8 }\" not in msg_source",
		"assert \"assert( serializedBytes <= sizeof( *from ) );\" in msg_source",
	):
		assert expected in event_transport_test

	assert "Implementation round - 2026-06-04, MSG entity and playerstate delta manifest expansion" in plan


def test_manifest_covers_xor_and_fragment_checkpoint_slice() -> None:
	manifest = _manifest()
	entries = {entry["symbol"]: entry for entry in manifest["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part05 = _read(HLIL_PART05_PATH)
	cl_net_chan = _read(CL_NET_CHAN_PATH)
	sv_net_chan = _read(SV_NET_CHAN_PATH)
	net_chan = _read(NET_CHAN_PATH)

	for symbol in (
		"Netchan_TransmitNextFragment",
		"Netchan_Transmit",
		"Netchan_Process",
		"CL_Netchan_Encode",
		"CL_Netchan_Decode",
		"SV_Netchan_Encode",
		"SV_Netchan_Decode",
	):
		assert entries[symbol]["status"] == "verified"
		assert entries[symbol]["behavior_checkpoints"]
		assert entries[symbol]["reference"]["binary_ninja_hlil"]

	for expected in (
		"004bce30    void sub_4bce30(void* arg1 @ esi)",
		"004bce89      char edx_1 = data_15f6b6c.b ^ eax_2 ^ eax_3",
		"004bcf2b  result.b = *edx",
		"004bcf9a  sub_4d4dc0(arg2, 5)",
		"004bcfba  return sub_4d74e0(arg1, arg2[4], arg2[2])",
		"004bcfcc  int32_t result = sub_4d7640(&__saved_ebp, arg2, edi, arg1, arg2)",
		"004d750f      sub_4c9b60(1, \"Netchan_Transmit: length = %i\")",
		"004d7858      if (eax_2 s< 0 || *(arg5 + 0x14) + eax_2 s> *(arg5 + 0x10) || ecx_7 + eax_2 u> 0x8000)",
	):
		assert expected in hlil_part04

	for expected in (
		"004e4cd0    void sub_4e4cd0(void* arg1 @ esi, void* arg2)",
		"004e4d12      char edx_1 = *(ecx_2 + 0x15b08) ^ *(ecx_2 + 0x10418)",
		"004e4d70    int32_t sub_4e4d70(void* arg1 @ esi, void* arg2)",
		"004e4e79          sub_4e4cd0(esi_1, arg1)",
		"004e4e8d          sub_4d74e0(arg1 + 0x15ae4, *(esi_1 + 0x10), *(esi_1 + 8))",
		"004e4f93  int32_t result = sub_4d7640(&__saved_ebp, arg2, arg1, arg1 + 0x15ae4, arg2)",
	):
		assert expected in hlil_part05

	for expected in (
		"if ( msg->cursize <= CL_ENCODE_START ) {",
		"key = clc.challenge ^ serverId ^ messageAcknowledge;",
		"for (i = msg->readcount + CL_DECODE_START; i < msg->cursize; i++) {",
		"MSG_WriteByte( msg, clc_EOF );",
	):
		assert expected in cl_net_chan

	for expected in (
		"if ( msg->cursize < SV_ENCODE_START ) {",
		"key = client->challenge ^ client->netchan.outgoingSequence;",
		"for (i = msg->readcount + SV_DECODE_START; i < msg->cursize; i++) {",
		"MSG_WriteByte( msg, svc_EOF );",
	):
		assert expected in sv_net_chan

	for expected in (
		"if ( chan->sock == NS_CLIENT && NET_ProtocolUsesNetchanClientQport() ) {",
		"if ( chan->sock == NS_SERVER && NET_ProtocolUsesNetchanClientQport() ) {",
		"if ( fragmentLength < 0 || msg->readcount + fragmentLength > msg->cursize ||",
		"chan->incomingSequence = sequence;",
	):
		assert expected in net_chan


def test_manifest_covers_endpoint_netchan_wrapper_and_queue_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part05 = _read(HLIL_PART05_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	cl_net_chan = _read(CL_NET_CHAN_PATH)
	sv_net_chan = _read(SV_NET_CHAN_PATH)
	client_h = _read(CLIENT_H_PATH)
	server_h = _read(SERVER_H_PATH)
	networking_audit = _read(NETWORKING_AUDIT_PATH)
	round_280 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_280.md")
	round_65 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_65.md")
	plan = _read(PLAN_PATH)

	expected_addresses = {
		"CL_Netchan_TransmitNextFragment": "0x004BCF80",
		"CL_Netchan_Transmit": "0x004BCF90",
		"CL_Netchan_Process": "0x004BCFC0",
		"SV_Netchan_TransmitNextFragment": "0x004E4E20",
		"SV_Netchan_Transmit": "0x004E4EE0",
		"SV_Netchan_Process": "0x004E4F80",
	}

	for symbol, address in expected_addresses.items():
		assert entries[symbol]["status"] == "verified"
		assert entries[symbol]["retail_address"] == address
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_endpoint_netchan_wrapper_and_queue_lane" in entries[symbol]["tests"]

	assert "retained client call sites pass the active clc.netchan" in entries["CL_Netchan_TransmitNextFragment"]["compatibility_notes"][0]

	for expected in (
		"FUN_004bcf80,004bcf80,9,0,unknown",
		"FUN_004bcf90,004bcf90,43,0,unknown",
		"FUN_004bcfc0,004bcfc0,49,0,unknown",
		"FUN_004e4e20,004e4e20,189,0,unknown",
		"FUN_004e4ee0,004e4ee0,160,0,unknown",
		"FUN_004e4f80,004e4f80,53,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004bcf80    int32_t sub_4bcf80()",
		"004bcf84  return sub_4d7370() __tailcall",
		"004bcf90    int32_t sub_4bcf90(int32_t* arg1, int32_t* arg2)",
		"004bcf9a  sub_4d4dc0(arg2, 5)",
		"004bcf9f  sub_4bce30(arg2)",
		"004bcfba  return sub_4d74e0(arg1, arg2[4], arg2[2])",
		"004bcfc0    int32_t sub_4bcfc0(int32_t arg1, void* arg2)",
		"004bcfcc  int32_t result = sub_4d7640(&__saved_ebp, arg2, edi, arg1, arg2)",
		"004bcfdb  sub_4bcef0(arg2)",
		"004bcfe3  data_114c140 += *(arg2 + 0x10)",
	):
		assert expected in hlil_part04

	for expected in (
		"004e4e20    int32_t sub_4e4e20(void* arg1)",
		"004e4e2e  int32_t result = sub_4d7370(arg1 + 0x15ae4)",
		"004e4e53          sub_4c9b60(1, \"netchan queue is not properly in",
		"004e4e71          sub_4c9ab0(\"#462 Netchan_TransmitNextFragmen",
		"004e4e79          sub_4e4cd0(esi_1, arg1)",
		"004e4e8d          sub_4d74e0(arg1 + 0x15ae4, *(esi_1 + 0x10), *(esi_1 + 8))",
		"004e4eaf          *(arg1 + 0x25b24) = arg1 + 0x25b20",
		"004e4ee0    int32_t sub_4e4ee0(void* arg1, int32_t* arg2)",
		"004e4eeb  sub_4d4dc0(arg2, 8)",
		"004e4f05  sub_4c9ab0(\"#462 SV_Netchan_Transmit: unsent",
		"004e4f0f  void* eax = sub_4ca3a0(0x8020)",
		"004e4f21  sub_4d4aa0(eax, eax + 0x1c, 0x8000, arg2)",
		"004e4f36  **(arg1 + 0x25b24) = eax",
		"004e4f5e  return sub_4d7370(arg1 + 0x15ae4)",
		"004e4f60      sub_4e4cd0(arg2, arg1)",
		"004e4f7f      return sub_4d74e0(arg1 + 0x15ae4, arg2[4], arg2[2])",
		"004e4f80    int32_t sub_4e4f80(void* arg1, void* arg2)",
		"004e4f93  int32_t result = sub_4d7640(&__saved_ebp, arg2, arg1, arg1 + 0x15ae4, arg2)",
		"004e4fa4  sub_4e4d70(arg2, arg1)",
	):
		assert expected in hlil_part05

	for expected in (
		"| `sub_4BCF80` | `CL_Netchan_TransmitNextFragment` | High | Tail wrapper to `Netchan_TransmitNextFragment`. |",
		"| `sub_4BCF90` | `CL_Netchan_Transmit` | High | Writes `clc_EOF`, encodes, then calls `Netchan_Transmit`. |",
		"| `sub_4BCFC0` | `CL_Netchan_Process` | High | Calls `Netchan_Process`, decodes accepted packets, and updates size accounting. |",
	):
		assert expected in round_280

	for expected in (
		"`sub_4E4E20 -> SV_Netchan_TransmitNextFragment`",
		"`sub_4E4EE0 -> SV_Netchan_Transmit`",
		"`sub_4E4F80 -> SV_Netchan_Process`",
		"preserve the retained queued\n   fragment transmit path and the final `SV_Netchan_Decode` wrapper",
	):
		assert expected in round_65

	for expected in (
		"void CL_Netchan_Transmit( netchan_t *chan, msg_t* msg);",
		"void CL_Netchan_TransmitNextFragment( netchan_t *chan );",
		"qboolean CL_Netchan_Process( netchan_t *chan, msg_t *msg );",
	):
		assert expected in client_h

	for expected in (
		"void SV_Netchan_Transmit( client_t *client, msg_t *msg);",
		"void SV_Netchan_TransmitNextFragment( client_t *client );",
		"qboolean SV_Netchan_Process( client_t *client, msg_t *msg );",
	):
		assert expected in server_h

	client_next = _function_block(cl_net_chan, "void CL_Netchan_TransmitNextFragment( netchan_t *chan )")
	assert "Netchan_TransmitNextFragment( chan );" in client_next

	client_transmit = _function_block(cl_net_chan, "void CL_Netchan_Transmit( netchan_t *chan, msg_t* msg )")
	_assert_order(
		client_transmit,
		"MSG_WriteByte( msg, clc_EOF );",
		"if ( NET_ProtocolUsesReliableXorCodec() ) {",
		"CL_Netchan_Encode( msg );",
		"Netchan_Transmit( chan, msg->cursize, msg->data );",
	)

	client_process = _function_block(cl_net_chan, "qboolean CL_Netchan_Process( netchan_t *chan, msg_t *msg )")
	_assert_order(
		client_process,
		"ret = Netchan_Process( chan, msg );",
		"if (!ret)",
		"return qfalse;",
		"if ( NET_ProtocolUsesReliableXorCodec() ) {",
		"CL_Netchan_Decode( msg );",
		"newsize += msg->cursize;",
		"return qtrue;",
	)

	server_next = _function_block(sv_net_chan, "void SV_Netchan_TransmitNextFragment( client_t *client )")
	_assert_order(
		server_next,
		"Netchan_TransmitNextFragment( &client->netchan );",
		"if (!client->netchan.unsentFragments)",
		"if (!client->netchan_end_queue) {",
		"Com_Error(ERR_DROP, \"netchan queue is not properly initialized in SV_Netchan_TransmitNextFragment\\n\");",
		"if (client->netchan_start_queue) {",
		"netbuf = client->netchan_start_queue;",
		"if ( NET_ProtocolUsesReliableXorCodec() ) {",
		"SV_Netchan_Encode( client, &netbuf->msg );",
		"Netchan_Transmit( &client->netchan, netbuf->msg.cursize, netbuf->msg.data );",
		"client->netchan_start_queue = netbuf->next;",
		"if (!client->netchan_start_queue) {",
		"client->netchan_end_queue = &client->netchan_start_queue;",
		"Z_Free(netbuf);",
	)

	server_transmit = sv_net_chan.split("void SV_Netchan_Transmit( client_t *client, msg_t *msg) {", 1)[1].split(
		"/*\n=================\nNetchan_SV_Process",
		1,
	)[0]
	_assert_order(
		server_transmit,
		"MSG_WriteByte( msg, svc_EOF );",
		"if (client->netchan.unsentFragments) {",
		"netbuf = (netchan_buffer_t *)Z_Malloc(sizeof(netchan_buffer_t));",
		"MSG_Copy(&netbuf->msg, netbuf->msgBuffer, sizeof( netbuf->msgBuffer ), msg);",
		"netbuf->next = NULL;",
		"*client->netchan_end_queue = netbuf;",
		"client->netchan_end_queue = &(*client->netchan_end_queue)->next;",
		"Netchan_TransmitNextFragment(&client->netchan);",
		"} else {",
		"if ( NET_ProtocolUsesReliableXorCodec() ) {",
		"SV_Netchan_Encode( client, msg );",
		"Netchan_Transmit( &client->netchan, msg->cursize, msg->data );",
	)

	server_process = _function_block(sv_net_chan, "qboolean SV_Netchan_Process( client_t *client, msg_t *msg )")
	_assert_order(
		server_process,
		"ret = Netchan_Process( &client->netchan, msg );",
		"if (!ret)",
		"return qfalse;",
		"if ( NET_ProtocolUsesReliableXorCodec() ) {",
		"SV_Netchan_Decode( client, msg );",
		"return qtrue;",
	)

	for expected in (
		"Reliable XOR codec | Client and server encode/decode are gated by the protocol profile. | Strong parity",
		"Server netchan queue | Retail `#462` queued netchan behavior is retained. | Strong parity",
	):
		assert expected in networking_audit

	assert "Implementation round - 2026-06-04, endpoint netchan wrapper and queue manifest expansion" in plan


def test_manifest_covers_oob_socket_framing_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part05 = _read(HLIL_PART05_PATH)
	hlil_part06 = _read(HLIL_PART06_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	net_chan = _read(NET_CHAN_PATH)
	win_net = _read(WIN_NET_PATH)
	plan = _read(PLAN_PATH)
	round_57 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_57.md")
	networking_audit = _read(REPO_ROOT / "docs/reverse-engineering/networking-parity-audit-2026-05-24.md")
	qcommon_audit = _read(REPO_ROOT / "docs/reverse-engineering/qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md")

	for symbol in (
		"Netchan_Init",
		"Netchan_Setup",
		"NET_SendPacket",
		"NET_OutOfBandPrint",
		"NET_OutOfBandData",
		"NET_OutOfBandRaw",
		"Sys_GetPacket",
		"Sys_SendPacket",
	):
		assert entries[symbol]["status"] in {"verified", "reconstructed"}
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_oob_socket_framing_lane" in entries[symbol]["tests"]

	assert entries["Netchan_Init"]["retail_address"] == "0x004D6C90"
	assert entries["Netchan_Setup"]["retail_address"] == "0x004D6D00"
	assert entries["NET_SendPacket"]["retail_address"] == "0x004D6FD0"
	assert entries["NET_OutOfBandPrint"]["retail_address"] == "0x004D7080"
	assert entries["NET_OutOfBandData"]["retail_address"] == "0x004D7120"
	assert entries["NET_OutOfBandRaw"]["retail_address"] is None
	assert entries["Sys_GetPacket"]["retail_address"] == "0x004EE260"
	assert entries["Sys_SendPacket"]["retail_address"] == "0x004EE460"

	for expected in (
		"FUN_004d6c90,004d6c90,101,0,unknown",
		"FUN_004d6d00,004d6d00,81,0,unknown",
		"FUN_004d6fd0,004d6fd0,170,0,unknown",
		"FUN_004d7080,004d7080,159,0,unknown",
		"FUN_004d7120,004d7120,296,0,unknown",
		"FUN_004ee260,004ee260,505,0,unknown",
		"FUN_004ee460,004ee460,268,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004d6c90    void** sub_4d6c90(int16_t arg1)",
		"004d6cb6  data_142c340 = sub_4ce0d0(x87_r0, \"showpackets\", U\"0\", 0x100)",
		"004d6cc0  data_14372f0 = sub_4ce0d0(x87_r2, \"showdrop\", U\"0\", 0x100)",
		"004d6ce6  void** result = sub_4ce0d0(x87_r4, \"net_qport\", sub_4d9220(&data_52e930), 0x10)",
		"004d6d00    int32_t sub_4d6d00",
		"004d6d0f  sub_4c95e0(arg2, 0, 0x1003c)",
		"004d6d40  *(arg2 + 0x20) = 0",
		"004d6d47  *(arg2 + 0x24) = 1",
		"004d6fd0    int32_t sub_4d6fd0",
		"004d6fea  if (*(eax + 0x30) != 0 && *arg3 == 0xffffffff)",
		"004d7000  if (arg4 == 2)",
		"004d704a  if (arg4 == 0 || arg4 == 1)",
		"004d706d  return sub_4ee460(arg2, arg3, arg4)",
		"004d7080    int32_t sub_4d7080",
		"004d709c  char var_8008 = 0xff",
		"004d70c0  vsprintf(&var_8004, arg7, &arg_20)",
		"004d7109      sub_4d6fd0(arg1, eax_2 - &var_8007, &var_8008, arg2, arg3, arg4, arg5, arg6)",
		"004d7120    int32_t sub_4d7120",
		"004d713d  int32_t var_10008 = 0xffffffff",
		"004d7157      memcpy(&var_10004, arg7, arg8)",
		"004d717d  int32_t eax_3 = sub_4d40f0(&var_10024, 0xc)",
		"004d71e6      int32_t eax_8 = sub_4cb7d0(edi_3, var_1001c, arg8 + 4)",
		"004d722f      eax_3 = sub_4ee460(arg8 + 4, var_1001c, arg2)",
	):
		assert expected in hlil_part04

	for expected in (
		"004ee260    int32_t sub_4ee260",
		"004ee2a7      eax_2, edx_1 = recvfrom(s, buf, len, flags: 0, &from, &fromlen)",
		"004ee2c7          if (eax_3 != WSAEWOULDBLOCK && eax_3 != WSAECONNRESET)",
		"004ee2d4              sub_4c9860(arg5, \"Sys_GetPacket: %s\\n\")",
		"004ee38d                  *arg4 = 4",
		"004ee3c6                  *(arg5 + 0x14) = 0xa",
		"004ee425              sub_4c9860(arg5, \"Oversize packet from %s\\n\")",
		"004ee460    int32_t sub_4ee460",
		"004ee480  if (len_1 != 3 && len_1 != 4)",
		"004ee4da          memcpy(0x12d010a, arg2, arg1)",
		"004ee4eb          len_1 = arg1 + 0xa",
		"004ee504      result = sendto(s, buf, len, flags: 0, to, tolen: 0x10)",
		"004ee527          if (result != 0x2733 && (result != 0x2741 || arg3 != 3))",
	):
		assert expected in hlil_part05

	for expected in (
		"00547684  char const data_547684[0x13] = \"Sys_GetPacket: %s\\n\", 0",
		"00547698  char const data_547698[0x21] = \"Sys_SendPacket: bad address type\", 0",
	):
		assert expected in hlil_part06

	netchan_init = _function_block(net_chan, "void Netchan_Init( int port )")
	netchan_setup = _function_block(net_chan, "void Netchan_Setup( netsrc_t sock, netchan_t *chan, netadr_t adr, int qport )")
	send_packet = _function_block(net_chan, "void NET_SendPacket( netsrc_t sock, int length, const void *data, netadr_t to )")
	oob_print = _function_block(net_chan, "void QDECL NET_OutOfBandPrint( netsrc_t sock, netadr_t adr, const char *format, ... )")
	oob_raw = _function_block(net_chan, "void NET_OutOfBandRaw( netsrc_t sock, netadr_t adr, const byte *data, int len )")
	oob_data = _function_block(net_chan, "void QDECL NET_OutOfBandData( netsrc_t sock, netadr_t adr, byte *format, int len )")
	get_packet = _function_block(win_net, "qboolean Sys_GetPacket( netadr_t *net_from, msg_t *net_message )")
	sys_send_packet = _function_block(win_net, "void Sys_SendPacket( int length, const void *data, netadr_t to )")

	_assert_order(
		netchan_init,
		"port &= 0xffff;",
		"showpackets = Cvar_Get (\"showpackets\", \"0\", CVAR_TEMP );",
		"showdrop = Cvar_Get (\"showdrop\", \"0\", CVAR_TEMP );",
		"qport = Cvar_Get (\"net_qport\", va(\"%i\", port), CVAR_INIT );",
	)

	_assert_order(
		netchan_setup,
		"Com_Memset (chan, 0, sizeof(*chan));",
		"chan->sock = sock;",
		"chan->remoteAddress = adr;",
		"chan->qport = qport;",
		"chan->incomingSequence = 0;",
		"chan->outgoingSequence = 1;",
	)

	_assert_order(
		send_packet,
		"if ( showpackets->integer && *(int *)data == -1 )",
		"if ( to.type == NA_LOOPBACK ) {",
		"NET_SendLoopPacket (sock, length, data, to);",
		"if ( to.type == NA_BOT ) {",
		"if ( to.type == NA_BAD ) {",
		"Sys_SendPacket( length, data, to );",
	)

	_assert_order(
		oob_print,
		"string[0] = -1;",
		"string[1] = -1;",
		"string[2] = -1;",
		"string[3] = -1;",
		"va_start( argptr, format );",
		"vsprintf( string+4, format, argptr );",
		"NET_SendPacket( sock, strlen( string ), string, adr );",
	)

	_assert_order(
		oob_raw,
		"if ( !data || len < 0 || len > (int)sizeof( string ) - 4 ) {",
		"string[0] = 0xff;",
		"string[1] = 0xff;",
		"string[2] = 0xff;",
		"string[3] = 0xff;",
		"Com_Memcpy( string + 4, data, len );",
		"NET_SendPacket( sock, len + 4, string, adr );",
	)

	_assert_order(
		oob_data,
		"string[0] = 0xff;",
		"string[1] = 0xff;",
		"string[2] = 0xff;",
		"string[3] = 0xff;",
		"for(i=0;i<len;i++) {",
		"string[i+4] = format[i];",
		"mbuf.data = string;",
		"mbuf.cursize = len+4;",
		"Huff_Compress( &mbuf, 12);",
		"NET_SendPacket( sock, mbuf.cursize, mbuf.data, adr );",
	)

	_assert_order(
		get_packet,
		"if( !ip_socket ) {",
		"ret = recvfrom( ip_socket, net_message->data, net_message->maxsize, 0,",
		"if( err == WSAEWOULDBLOCK || err == WSAECONNRESET ) {",
		"Com_Printf( \"Sys_GetPacket: %s\\n\", NET_ErrorString() );",
		"memset( ((struct sockaddr_in *)&from)->sin_zero, 0, 8 );",
		"if ( usingSocks && memcmp( &from, &socksRelayAddr, fromlen ) == 0 ) {",
		"if ( ret < 10 || net_message->data[0] != 0 || net_message->data[1] != 0 || net_message->data[2] != 0 || net_message->data[3] != 1 ) {",
		"net_message->readcount = 10;",
		"if( ret == net_message->maxsize ) {",
		"net_message->cursize = ret;",
	)
	assert "NET_GetPacket: %s" not in get_packet

	_assert_order(
		sys_send_packet,
		"if( to.type != NA_BROADCAST && to.type != NA_IP ) {",
		"Com_Error( ERR_FATAL, \"Sys_SendPacket: bad address type\" );",
		"net_socket = ip_socket;",
		"if( !net_socket ) {",
		"NetadrToSockadr( &to, &addr );",
		"if( usingSocks && to.type == NA_IP ) {",
		"socksBuf[0] = 0;",
		"memcpy( &socksBuf[10], data, length );",
		"ret = sendto( net_socket, socksBuf, length+10, 0, &socksRelayAddr, sizeof(socksRelayAddr) );",
		"ret = sendto( net_socket, data, length, 0, &addr, sizeof(addr) );",
		"if( err == WSAEWOULDBLOCK ) {",
		"if( ( err == WSAEADDRNOTAVAIL ) && to.type == NA_BROADCAST ) {",
		"Com_Printf( \"NET_SendPacket: %s\\n\", NET_ErrorString() );",
	)

	for expected in (
		"`sub_4D6C90 -> Netchan_Init`",
		"`sub_4D6D00 -> Netchan_Setup`",
		"`sub_4D6FD0 -> NET_SendPacket`",
		"`sub_4D7080 -> NET_OutOfBandPrint`",
		"`sub_4D7120 -> NET_OutOfBandData`",
		"`sub_4D6FD0`, `sub_4D7080`, and `sub_4D7120` preserve Quake III OOB packet",
		"`sub_4D6C90` as `Netchan_Init`",
	):
		assert expected in (round_57 + networking_audit + qcommon_audit)

	assert "Implementation round - 2026-06-04, OOB socket framing manifest expansion" in plan


def test_manifest_covers_address_loopback_helper_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	net_chan = _read(NET_CHAN_PATH)
	plan = _read(PLAN_PATH)
	round_57 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_57.md")

	for symbol in (
		"NET_CompareBaseAdr",
		"NET_AdrToString",
		"NET_CompareAdr",
		"NET_IsLocalAddress",
		"NET_GetLoopPacket",
		"NET_SendLoopPacket",
		"NET_StringToAdr",
	):
		assert entries[symbol]["status"] == "verified"
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_address_loopback_helper_lane" in entries[symbol]["tests"]

	assert entries["NET_CompareBaseAdr"]["retail_address"] == "0x004D6D60"
	assert entries["NET_AdrToString"]["retail_address"] == "0x004D6DD0"
	assert entries["NET_CompareAdr"]["retail_address"] == "0x004D6EB0"
	assert entries["NET_IsLocalAddress"]["retail_address"] == "0x004D6F30"
	assert entries["NET_GetLoopPacket"]["retail_address"] == "0x004D6F40"
	assert entries["NET_SendLoopPacket"]["retail_address"] is None
	assert entries["NET_StringToAdr"]["retail_address"] == "0x004D7250"
	assert entries["NET_SendLoopPacket"]["kind"] == "source_helper"
	assert "NA_LOOPBACK branch inside NET_SendPacket" in entries["NET_SendLoopPacket"]["compatibility_notes"][0]

	for expected in (
		"FUN_004d6d60,004d6d60,107,0,unknown",
		"FUN_004d6dd0,004d6dd0,220,0,unknown",
		"FUN_004d6eb0,004d6eb0,127,0,unknown",
		"FUN_004d6f30,004d6f30,14,0,unknown",
		"FUN_004d6f40,004d6f40,142,0,unknown",
		"FUN_004d7250,004d7250,276,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004d6d60    int32_t sub_4d6d60(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4)",
		"004d6d69  if (arg1 == arg3)",
		"004d6d7a      if (arg1 == 4)",
		"004d6dab          if (arg2.b == arg4.b && (arg2 u>> 8).b == (arg4 u>> 8).b",
		"004d6dbf      sub_4c9860(esi, \"NET_CompareBaseAdr: bad address",
		"004d6dd0    int32_t sub_4d6dd0",
		"004d6de7      sub_4d9160(&data_124a638, 0x40, \"loopback\")",
		"004d6e47      sub_4d9160(&data_124a638, 0x40, \"%i.%i.%i.%i:%hu\")",
		"004d6e9d  sub_4d9160(&data_124a638, 0x40, \"%02x%02x%02x%02x.%02x%02x%02x%02",
		"004d6eb0    int32_t sub_4d6eb0",
		"004d6ec2      if (arg1 == 2 || arg1 == 0)",
		"004d6f08                  && arg3 u>> 0x10 == arg6 u>> 0x10)",
		"004d6f1c      sub_4c9860(esi, \"NET_CompareAdr: bad address type",
		"004d6f30    int32_t sub_4d6f30(int32_t arg1) __pure",
		"004d6f39  result.b = arg1 == 2",
		"004d6f40    int32_t sub_4d6f40(int32_t arg1, int32_t* arg2, void* arg3)",
		"004d6f63  if (eax - *(arg1 * 0x57c8 + 0x1431b20) s> 0x10)",
		"004d6f88  void* esi_3 = (edx_3 & 0xf) * 0x57c + arg1 * 0x57c8 + 0x142c360",
		"004d6fa1  sub_4cb7d0(*(arg3 + 8), esi_3, *(esi_3 + 0x578))",
		"004d6fb4  *(arg3 + 0x10) = *(esi_3 + 0x578)",
		"004d6fc0  *arg2 = 2",
		"004d7000  if (arg4 == 2)",
		"004d7013      int32_t edx_1 = *((arg1 ^ 1) * 0x57c8 + 0x1431b24)",
		"004d7030      int32_t eax_5 = sub_4cb7d0(esi_4, arg3, arg2)",
		"004d7038      *(esi_4 + 0x578) = arg2",
		"004d7250    int32_t sub_4d7250(char* arg1, int32_t* arg2)",
		"004d726b  char const* const ecx = \"localhost\"",
		"004d72bf      sub_4d8f40(&var_408, arg1, 0x400)",
		"004d72d6      int32_t esi_1 = strstr(&var_408, &data_54fff0)",
		"004d72f5      if (sub_4ee210(&var_408, arg2) == 0)",
		"004d72f7          *arg2 = 1",
		"004d7323      if (arg2[1].b == 0xff && *(arg2 + 5) == 0xff && *(arg2 + 6) == 0xff",
		"004d7343          eax_10 = sub_4d8ac0(0x6d38)",
		"004d7334          eax_10 = sub_4d8ac0(zx.d(atoi(esi_1)))",
		"004d734b      *(arg2 + 0x12) = eax_10",
		"004d729f      sub_4c95e0(arg2, eax_4, 0x14)",
		"004d72a7      *arg2 = 2",
	):
		assert expected in hlil_part04

	compare_base = _function_block(net_chan, "NET_CompareBaseAdr (netadr_t a, netadr_t b)")
	adr_to_string = _function_block(net_chan, "NET_AdrToString (netadr_t a)")
	compare_adr = _function_block(net_chan, "NET_CompareAdr (netadr_t a, netadr_t b)")
	is_local = _function_block(net_chan, "NET_IsLocalAddress( netadr_t adr )")
	get_loop = _function_block(net_chan, "NET_GetLoopPacket (netsrc_t sock, netadr_t *net_from, msg_t *net_message)")
	send_loop = _function_block(net_chan, "NET_SendLoopPacket (netsrc_t sock, int length, const void *data, netadr_t to)")
	string_to_adr = _function_block(net_chan, "NET_StringToAdr( const char *s, netadr_t *a )")

	_assert_order(
		compare_base,
		"if (a.type != b.type)",
		"if (a.type == NA_LOOPBACK)",
		"if (a.type == NA_IP)",
		"if (a.ip[0] == b.ip[0] && a.ip[1] == b.ip[1] && a.ip[2] == b.ip[2] && a.ip[3] == b.ip[3])",
		"Com_Printf (\"NET_CompareBaseAdr: bad address type\\n\");",
	)

	_assert_order(
		adr_to_string,
		"if (a.type == NA_LOOPBACK) {",
		"Com_sprintf (s, sizeof(s), \"loopback\");",
		"} else if (a.type == NA_BOT) {",
		"Com_sprintf (s, sizeof(s), \"bot\");",
		"} else if (a.type == NA_IP) {",
		"Com_sprintf (s, sizeof(s), \"%i.%i.%i.%i:%hu\",",
		"BigShort(a.port));",
		"Com_sprintf (s, sizeof(s), \"%02x%02x%02x%02x.%02x%02x%02x%02x%02x%02x:%hu\",",
		"return s;",
	)

	_assert_order(
		compare_adr,
		"if (a.type != b.type)",
		"if (a.type == NA_LOOPBACK || a.type == NA_BOT)",
		"if (a.type == NA_IP)",
		"if (a.ip[0] == b.ip[0] && a.ip[1] == b.ip[1] && a.ip[2] == b.ip[2] && a.ip[3] == b.ip[3] && a.port == b.port)",
		"Com_Printf (\"NET_CompareAdr: bad address type\\n\");",
	)

	assert "return adr.type == NA_LOOPBACK;" in is_local

	_assert_order(
		get_loop,
		"loop = &loopbacks[sock];",
		"if (loop->send - loop->get > MAX_LOOPBACK)",
		"loop->get = loop->send - MAX_LOOPBACK;",
		"if (loop->get >= loop->send)",
		"return qfalse;",
		"i = loop->get & (MAX_LOOPBACK-1);",
		"loop->get++;",
		"Com_Memcpy (net_message->data, loop->msgs[i].data, loop->msgs[i].datalen);",
		"net_message->cursize = loop->msgs[i].datalen;",
		"Com_Memset (net_from, 0, sizeof(*net_from));",
		"net_from->type = NA_LOOPBACK;",
	)

	_assert_order(
		send_loop,
		"loop = &loopbacks[sock^1];",
		"i = loop->send & (MAX_LOOPBACK-1);",
		"loop->send++;",
		"Com_Memcpy (loop->msgs[i].data, data, length);",
		"loop->msgs[i].datalen = length;",
	)

	_assert_order(
		string_to_adr,
		"if (!strcmp (s, \"localhost\")) {",
		"Com_Memset (a, 0, sizeof(*a));",
		"a->type = NA_LOOPBACK;",
		"Q_strncpyz( base, s, sizeof( base ) );",
		"port = strstr( base, \":\" );",
		"*port = 0;",
		"r = Sys_StringToAdr( base, a );",
		"if ( !r ) {",
		"a->type = NA_BAD;",
		"if ( a->ip[0] == 255 && a->ip[1] == 255 && a->ip[2] == 255 && a->ip[3] == 255 ) {",
		"a->type = NA_BAD;",
		"if ( port ) {",
		"a->port = BigShort( (short)atoi( port ) );",
		"a->port = BigShort( PORT_SERVER );",
	)

	for expected in (
		"`sub_4D6D60 -> NET_CompareBaseAdr`",
		"`sub_4D6DD0 -> NET_AdrToString`",
		"`sub_4D6EB0 -> NET_CompareAdr`",
		"`sub_4D6F30 -> NET_IsLocalAddress`",
		"`sub_4D6F40 -> NET_GetLoopPacket`",
		"`sub_4D7250 -> NET_StringToAdr`",
		"`sub_4D6D60`, `sub_4D6DD0`, `sub_4D6EB0`, `sub_4D6F30`, and `sub_4D6F40`",
		"`sub_4D7250` is the retained `NET_StringToAdr` path",
	):
		assert expected in round_57

	assert "Implementation round - 2026-06-04, address and loopback helper manifest expansion" in plan


def test_manifest_covers_client_command_generation_and_send_cadence_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	cl_input = _read(CL_INPUT_PATH)
	round_277 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_277.md")
	client_audit = _read(REPO_ROOT / "docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md")
	plan = _read(PLAN_PATH)

	expected_addresses = {
		"CL_CreateCmd": "0x004B5C70",
		"CL_CreateNewCommands": "0x004B5DE0",
		"CL_ReadyToSendPacket": "0x004B5E60",
		"CL_SendCmd": "0x004B62A0",
	}

	for symbol, address in expected_addresses.items():
		assert entries[symbol]["status"] == "verified"
		assert entries[symbol]["retail_address"] == address
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_client_command_generation_and_send_cadence_lane" in entries[symbol]["tests"]

	assert "retail HLIL inlines the final move storage" in entries["CL_CreateCmd"]["compatibility_notes"][0]

	for expected in (
		"FUN_004b5c70,004b5c70,364,0,unknown",
		"FUN_004b5de0,004b5de0,118,0,unknown",
		"FUN_004b5e60,004b5e60,265,0,unknown",
		"FUN_004b62a0,004b62a0,88,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004b5c70    void sub_4b5c70(int32_t* arg1)",
		"004b5c89  sub_4b5290()",
		"004b5c96  sub_4c95e0(arg1, 0, 0x1c)",
		"004b5c9c  sub_4b5bd0(arg1)",
		"004b5ca2  sub_4b5360(arg1)",
		"004b5ca8  sub_4b5800(arg1)",
		"004b5cae  sub_4b55b0(arg1)",
		"004b5d60  int32_t eax_5 = *(data_1647f08 + 0x30)",
		"004b5de0    void sub_4b5de0()",
		"004b5ded  if (data_1528ba0 s>= 7)",
		"004b5dfd      data_165d598 = eax_2",
		"004b5e07      if (eax_2 u> 0xc8)",
		"004b5e09          data_165d598 = 0xc8",
		"004b5e18      int32_t eax_4 = data_14725d0 + 1",
		"004b5e4e      __builtin_memcpy(dest: (eax_4 & 0x3f) * 0x1c + &data_1471ed0, src: eax, n: 0x1c)",
		"004b5e60    int32_t sub_4b5e60()",
		"004b5e69  if (data_16177e0 == 0)",
		"004b5f28                          sub_4cd250(\"cl_maxpackets\", \"15\")",
		"004b5f28                          sub_4cd250(\"cl_maxpackets\", \"125\")",
		"004b5f5c                          - *(((data_1617c20 - 1) & 0x1f) * 0xc + &data_14725dc)",
		"004b62a0    void sub_4b62a0()",
		"004b62cc      sub_4b5de0()",
		"004b62d8      if (sub_4b5e60() != 0)",
		"004b62f3          return sub_4b5f70(esi) __tailcall",
		"004b62ea          sub_4c9860(esi, &data_53da6c)",
	):
		assert expected in hlil_part04

	for expected in (
		"| `sub_4B5C70` | `CL_CreateCmd` | High | Usercmd construction owner. |",
		"| `sub_4B5DE0` | `CL_CreateNewCommands` | High | Primed/active command creation owner. |",
		"| `sub_4B5E60` | `CL_ReadyToSendPacket` | High | Send throttling and `cl_maxpackets` owner. |",
		"| `sub_4B62A0` | `CL_SendCmd` | High | Top-level usercmd send orchestration owner. |",
		"`CL_WritePacket`, including the `cl_packetdup` resend window",
	):
		assert expected in round_277

	for expected in (
		"`CL_CreateCmd`, `CL_CreateNewCommands`, `CL_ReadyToSendPacket`, and",
		"`CL_SendCmd` into the alias ledger and focused parity guard.",
	):
		assert expected in client_audit

	create_cmd = _function_block(cl_input, "usercmd_t CL_CreateCmd( void )")
	create_new = _function_block(cl_input, "void CL_CreateNewCommands( void )")
	ready = _function_block(cl_input, "qboolean CL_ReadyToSendPacket( void )")
	send_cmd = _function_block(cl_input, "void CL_SendCmd( void )")

	_assert_order(
		create_cmd,
		"VectorCopy( cl.viewangles, oldAngles );",
		"CL_AdjustAngles ();",
		"Com_Memset( &cmd, 0, sizeof( cmd ) );",
		"CL_CmdButtons( &cmd );",
		"CL_KeyMove( &cmd );",
		"CL_MouseMove( &cmd );",
		"CL_JoystickMove( &cmd );",
		"if ( cl.viewangles[PITCH] - oldAngles[PITCH] > 90 ) {",
		"cl.viewangles[PITCH] = oldAngles[PITCH] + 90;",
		"} else if ( oldAngles[PITCH] - cl.viewangles[PITCH] > 90 ) {",
		"cl.viewangles[PITCH] = oldAngles[PITCH] - 90;",
		"CL_FinishMove( &cmd );",
		"if ( cl_debugMove->integer ) {",
		"SCR_DebugGraph( abs(cl.viewangles[YAW] - oldAngles[YAW]), 0 );",
		"SCR_DebugGraph( abs(cl.viewangles[PITCH] - oldAngles[PITCH]), 0 );",
		"return cmd;",
	)

	_assert_order(
		create_new,
		"if ( cls.state < CA_PRIMED ) {",
		"return;",
		"frame_msec = com_frameTime - old_com_frameTime;",
		"if ( frame_msec > 200 ) {",
		"frame_msec = 200;",
		"old_com_frameTime = com_frameTime;",
		"cl.cmdNumber++;",
		"cmdNum = cl.cmdNumber & CMD_MASK;",
		"cl.cmds[cmdNum] = CL_CreateCmd ();",
		"cmd = &cl.cmds[cmdNum];",
	)

	_assert_order(
		ready,
		"if ( clc.demoplaying || cls.state == CA_CINEMATIC ) {",
		"return qfalse;",
		"if ( *clc.downloadTempName &&",
		"cls.realtime - clc.lastPacketSentTime < 50 ) {",
		"return qfalse;",
		"if ( cls.state != CA_ACTIVE &&",
		"cls.state != CA_PRIMED &&",
		"!*clc.downloadTempName &&",
		"cls.realtime - clc.lastPacketSentTime < 1000 ) {",
		"return qfalse;",
		"if ( clc.netchan.remoteAddress.type == NA_LOOPBACK ) {",
		"return qtrue;",
		"if ( Sys_IsLANAddress( clc.netchan.remoteAddress ) ) {",
		"return qtrue;",
		"if ( cl_maxpackets->integer < 15 ) {",
		"Cvar_Set( \"cl_maxpackets\", \"15\" );",
		"} else if ( cl_maxpackets->integer > 125 ) {",
		"Cvar_Set( \"cl_maxpackets\", \"125\" );",
		"oldPacketNum = (clc.netchan.outgoingSequence - 1) & PACKET_MASK;",
		"delta = cls.realtime -  cl.outPackets[ oldPacketNum ].p_realtime;",
		"if ( delta < 1000 / cl_maxpackets->integer ) {",
		"return qfalse;",
		"return qtrue;",
	)

	_assert_order(
		send_cmd,
		"if ( cls.state < CA_CONNECTED ) {",
		"return;",
		"if ( com_sv_running->integer && sv_paused->integer && cl_paused->integer ) {",
		"return;",
		"CL_CreateNewCommands();",
		"if ( !CL_ReadyToSendPacket() ) {",
		"if ( cl_showSend->integer ) {",
		"Com_Printf( \". \" );",
		"return;",
		"CL_WritePacket();",
	)

	assert "Implementation round - 2026-06-04, client command generation and send-cadence manifest expansion" in plan


def test_manifest_covers_client_usercmd_packet_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	cl_input = _read(CL_INPUT_PATH)
	msg_c = _read(MSG_C_PATH)
	sv_client = _read(SV_CLIENT_PATH)
	plan = _read(PLAN_PATH)

	for symbol in (
		"CL_WritePacket",
		"MSG_WriteDeltaUsercmdKey",
		"MSG_ReadDeltaUsercmdKey",
		"SV_UserMove",
		"SV_ExecuteClientMessage",
	):
		assert entries[symbol]["status"] == "verified"
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_client_usercmd_packet_lane" in entries[symbol]["tests"]

	for expected in (
		"FUN_004b5f70,004b5f70,802,0,unknown",
		"FUN_004d51a0,004d51a0,756,0,unknown",
		"FUN_004d54a0,004d54a0,683,0,unknown",
		"FUN_004e05c0,004e05c0,385,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004b5f70    int32_t sub_4b5f70(int32_t arg1 @ esi)",
		"004b5ff0      sub_4d4e30(&var_8044, data_1472870)",
		"004b6003      sub_4d4e30(&var_8044, data_1606b7c)",
		"004b6015      sub_4d4e30(&var_8044, data_1606b80)",
		"004b6030      sub_4d4dc0(&var_8044, zx.d(sub_4af4d0()) ^ data_1606b80.b)",
		"004b6045      for (int32_t i = data_15f6b78 + 1; i s<= data_15f6b74; i += 1)",
		"004b6153          sub_4d4dc0(__saved_ebx_5, __saved_edi_6)",
		"004b618f          int32_t edi_3 = data_15f6b70 ^ data_1606b7c",
		"004b61d6                  sub_4d51a0(&var_8044, edi_3, var_8028_1, eax_16 * 0x1c + &data_1471ed0)",
		"004d51a0    int32_t* sub_4d51a0(int32_t* arg1, int32_t arg2, int32_t* arg3, int32_t arg4)",
		"004d5421  int32_t eax_28 = zx.d(*(edi + 0x15))",
		"004d545b  uint32_t edi_1 = zx.d(*(edi + 0x16))",
		"004d54a0    int32_t sub_4d54a0(void* arg1, int32_t arg2, void* arg3, int32_t* arg4)",
		"004e0411          sub_4d54a0(arg1, edi_2, eax_8, esi)",
		"004e05c0    uint32_t sub_4e05c0(int32_t* arg1, void* arg2)",
		"004e05fe      sub_4d4fc0(arg2)",
		"004e06fc              return sub_4e0320(arg2, 1)",
		"004e0711              return sub_4e0320(arg2, 0)",
		"004e0734              return sub_4c9860(arg2, \"WARNING: bad command byte for cl",
	):
		assert expected in hlil_part04

	write_packet = _function_block(cl_input, "void CL_WritePacket( void )")
	write_delta = _function_block(msg_c, "void MSG_WriteDeltaUsercmdKey( msg_t *msg, int key, usercmd_t *from, usercmd_t *to )")
	read_delta = _function_block(msg_c, "void MSG_ReadDeltaUsercmdKey( msg_t *msg, int key, usercmd_t *from, usercmd_t *to )")
	user_move = _function_block(sv_client, "static void SV_UserMove( client_t *cl, msg_t *msg, qboolean delta )")
	execute_message = _function_block(sv_client, "void SV_ExecuteClientMessage( client_t *cl, msg_t *msg )")

	_assert_order(
		write_packet,
		"MSG_Bitstream( &buf );",
		"MSG_WriteLong( &buf, cl.serverId );",
		"MSG_WriteLong( &buf, clc.serverMessageSequence );",
		"MSG_WriteLong( &buf, clc.serverCommandSequence );",
		"MSG_WriteByte( &buf, CL_RetailClientMessageFlags() ^ ( clc.serverCommandSequence & 0xff ) );",
		"for ( i = clc.reliableAcknowledge + 1 ; i <= clc.reliableSequence ; i++ ) {",
		"MSG_WriteByte( &buf, clc_clientCommand );",
		"oldPacketNum = (clc.netchan.outgoingSequence - 1 - cl_packetdup->integer) & PACKET_MASK;",
		"count = cl.cmdNumber - cl.outPackets[ oldPacketNum ].p_cmdNumber;",
		"if ( cl_nodelta->integer || !cl.snap.valid || clc.demowaiting",
		"MSG_WriteByte (&buf, clc_moveNoDelta);",
		"MSG_WriteByte( &buf, count );",
		"key = clc.checksumFeed;",
		"key ^= clc.serverMessageSequence;",
		"key ^= Com_HashKey(clc.serverCommands[ clc.serverCommandSequence & (MAX_RELIABLE_COMMANDS-1) ], 32);",
		"MSG_WriteDeltaUsercmdKey (&buf, key, oldcmd, cmd);",
		"cl.outPackets[ packetNum ].p_realtime = cls.realtime;",
		"CL_Netchan_Transmit (&clc.netchan, &buf);",
	)

	_assert_order(
		write_delta,
		"if ( to->serverTime - from->serverTime < 256 ) {",
		"MSG_WriteBits( msg, 1, 1 );",
		"MSG_WriteBits( msg, to->serverTime - from->serverTime, 8 );",
		"key ^= to->serverTime;",
		"MSG_WriteDeltaKey( msg, key, from->angles[0], to->angles[0], 16 );",
		"MSG_WriteDeltaKey( msg, key, from->forwardmove, to->forwardmove, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->weaponPrimary, to->weaponPrimary, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->fov, to->fov, 8 );",
	)
	assert "oldsize += 7;" in write_delta

	_assert_order(
		read_delta,
		"if ( MSG_ReadBits( msg, 1 ) ) {",
		"to->serverTime = from->serverTime + MSG_ReadBits( msg, 8 );",
		"key ^= to->serverTime;",
		"to->angles[0] = MSG_ReadDeltaKey( msg, key, from->angles[0], 16);",
		"to->forwardmove = MSG_ReadDeltaKey( msg, key, from->forwardmove, 8);",
		"to->weaponPrimary = MSG_ReadDeltaKey( msg, key, from->weaponPrimary, 8);",
		"to->fov = MSG_ReadDeltaKey( msg, key, from->fov, 8);",
		"to->angles[0] = from->angles[0];",
	)
	assert "to->weaponPrimary = from->weaponPrimary;" in read_delta
	assert "to->fov = from->fov;" in read_delta

	_assert_order(
		user_move,
		"if ( delta ) {",
		"cl->deltaMessage = cl->messageAcknowledge;",
		"cmdCount = MSG_ReadByte( msg );",
		"if ( cmdCount < 1 ) {",
		"if ( cmdCount > MAX_PACKET_USERCMDS ) {",
		"key = sv.checksumFeed;",
		"key ^= cl->messageAcknowledge;",
		"key ^= Com_HashKey(cl->reliableCommands[ cl->reliableAcknowledge & (MAX_RELIABLE_COMMANDS-1) ], 32);",
		"MSG_ReadDeltaUsercmdKey( msg, key, oldcmd, cmd );",
		"cl->frames[ cl->messageAcknowledge & PACKET_MASK ].messageAcked = svs.time;",
		"if ( cl->state == CS_PRIMED ) {",
		"SV_ClientEnterWorld( cl, &cmds[0] );",
		"SV_ClientThink (cl, &cmds[ i ]);",
	)

	_assert_order(
		execute_message,
		"MSG_Bitstream(msg);",
		"serverId = MSG_ReadLong( msg );",
		"cl->messageAcknowledge = MSG_ReadLong( msg );",
		"cl->reliableAcknowledge = MSG_ReadLong( msg );",
		"(void)MSG_ReadByte( msg );",
		"if ( serverId != sv.serverId && !*cl->downloadName && !strstr(cl->lastClientCommandString, NET_GetDownloadNextCommand()) ) {",
		"do {",
		"c = MSG_ReadByte( msg );",
		"if ( c != clc_clientCommand ) {",
		"if ( c == clc_move ) {",
		"SV_UserMove( cl, msg, qtrue );",
		"} else if ( c == clc_moveNoDelta ) {",
		"SV_UserMove( cl, msg, qfalse );",
	)
	assert 'Com_Printf( "WARNING: bad command byte for client %i\\n", cl - svs.clients );' in execute_message
	assert "Implementation round - 2026-06-04, client usercmd packet manifest expansion" in plan


def test_manifest_covers_client_connectionless_handshake_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	ghidra_decompile = _read(GHIDRA_DECOMPILE_TOP_PATH)
	cl_main = _read(CL_MAIN_PATH)
	client_h = _read(CLIENT_H_PATH)
	plan = _read(PLAN_PATH)
	round_105 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_105.md")
	round_290 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_290.md")

	for symbol in (
		"CL_CheckForResend",
		"CL_BuildSteamChallengeRequest",
		"CL_SendChallengeRequest",
		"CL_ConnectionlessPacket",
		"CL_PacketEvent",
	):
		assert entries[symbol]["status"] in {"verified", "reconstructed"}
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_client_connectionless_handshake_lane" in entries[symbol]["tests"]

	assert entries["CL_CheckForResend"]["retail_address"] == "0x004B9150"
	assert entries["CL_ConnectionlessPacket"]["retail_address"] == "0x004BBBE0"
	assert entries["CL_PacketEvent"]["retail_address"] == "0x004BC190"
	assert entries["CL_BuildSteamChallengeRequest"]["retail_address"] is None
	assert entries["CL_SendChallengeRequest"]["retail_address"] is None
	assert "SteamServer_HandleIncomingPacket" in " ".join(entries["CL_ConnectionlessPacket"]["compatibility_notes"])

	for expected in (
		"FUN_004b9150,004b9150,735,0,unknown",
		"FUN_004bbbe0,004bbbe0,1445,0,unknown",
		"FUN_004bc190,004bc190,391,0,unknown",
		"FUN_00465d50,00465d50,94,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"/* FUN_004bbbe0 @ 004bbbe0 size 1445 */",
		"FUN_004c9ab0(\"CL packet %s: %s\\n\",uVar2);",
		"iVar3 = FUN_004d9060(uVar1,\"challengeResponse\");",
		"FUN_004d8f40(&DAT_016177fc,uVar1);",
		"iVar3 = FUN_004d9060(uVar1,\"connectResponse\");",
		"FUN_004d6d00(0,&DAT_01617bfc,local_1c,local_18,local_14,local_10,local_c,uVar1);",
	):
		assert expected in ghidra_decompile

	for expected in (
		"004b9150    int32_t sub_4b9150(int32_t arg1 @ esi)",
		"004b8e0d      int32_t result = sub_4f3570(\"Bad server address\")",
		"004b9182      if (eax_1 == 3 || eax_1 == 4)",
		"004b91c1                      sub_4c9b60(0, \"CL_CheckForResend: bad cls.state\")",
		"004b9221                  sub_4d9620(&var_808, \"protocol\", sub_4d9220(&data_52e930))",
		"004b928b                  __builtin_strncpy(dest: &var_408, src: \"connect \", n: 9)",
		"004b9386              __builtin_strncpy(dest: &var_9804, src: \"getchallenge \", n: 0xd)",
		"004b9418              eax_1 = sub_4d6fd0(0, eax_13 + 0x19, &var_9808, data_15f6750, data_15f6754,",
		"004bbbe0    void* sub_4bbbe0",
		"004bbc7d  if (sub_4d9060(eax_4, \"challengeResponse\") == 0)",
		"004bbcd4          sub_4d8f40(0x16177fc, sub_4c7ee0(2), 0x400)",
		"004bbd2e          void* eax_12 = sub_4c9ab0(\"challengeResponse: %d\\n\")",
		"004bbd56  if (sub_4d9060(eax_4, \"connectResponse\") == 0)",
		"004bbd8d              int32_t eax_16 = sub_4c9860(arg9, \"connectResponse packet while not",
		"004bbe0d          sub_4c9860(arg9, \"connectResponse from a different",
		"004bbff2  if (sub_4d9060(eax_4, \"echo\") == 0)",
		"004bc046  uint32_t eax_30 = sub_4d9060(eax_4, \"keyAuthorize\")",
		"004bc11c      if (sub_4d9020(eax_4, \"getserversResponse\", 0x12) == 0)",
		"004bc15c      eax_30 = sub_465d50(&var_1c, arg9)",
		"004bc16d          eax_30 = sub_4c9ab0(\"Unknown connectionless packet co",
		"004bc190    int32_t sub_4bc190",
		"004bc1b0  if (result s>= 4 && **(arg6 + 8) == 0xffffffff)",
		"004bc1e0      return sub_4bbbe0(&__saved_ebp, arg6.b, edi.b, arg1, arg2, arg3, arg4, arg5, arg6)",
		"004bc22b          return sub_4c9860(arg6, \"%s: Runt packet\\n\")",
		"004bc2be          return sub_4c9ab0(\"%s:sequenced packet without conn",
		"004bc2c5      result = sub_4bcfc0(&data_1617bfc, arg6)",
		"004bc2ef          result, ecx_15, edx_14 = sub_4bda00(arg6)",
	):
		assert expected in hlil_part04

	build_challenge = _function_block(cl_main, "static qboolean CL_BuildSteamChallengeRequest( byte *data, int dataSize, int *dataLength )")
	send_challenge = _function_block(cl_main, "static void CL_SendChallengeRequest( void )")
	connect_f = _function_block(cl_main, "void CL_Connect_f( void )")
	check_resend = _function_block(cl_main, "void CL_CheckForResend( void ) {")
	connectionless = _function_block(cl_main, "void CL_ConnectionlessPacket( netadr_t from, msg_t *msg )")
	packet_event = _function_block(cl_main, "void CL_PacketEvent( netadr_t from, msg_t *msg )")

	_assert_order(
		client_h,
		"int\t\t\ttimeDemoBaseTime;",
		"char\t\tchallengeResponseText[MAX_STRING_CHARS];",
		"netchan_t\tnetchan;",
	)

	_assert_order(
		connect_f,
		"if (!NET_StringToAdr( cls.servername, &clc.serverAddress) ) {",
		"Com_Printf (\"Bad server address\\n\");",
		"CL_WebView_PublishGameError( \"Bad server address\" );",
		"cls.state = CA_DISCONNECTED;",
		"return;",
	)

	_assert_order(
		build_challenge,
		"if ( !NET_ProtocolSupportsPlatformAuth() ) {",
		"if ( !QL_ClientAuth_RequestSteamChallengeTicket( ticket, sizeof( ticket ), &ticketLength, &steamIdLow, &steamIdHigh ) ) {",
		"command = NET_GetChallengeRequestCommand();",
		"payloadLength = commandLength + 1 + 8 + ticketLength;",
		"if ( ticketLength <= 0 || payloadLength > dataSize ) {",
		"Com_Memcpy( data, command, commandLength );",
		"data[commandLength] = ' ';",
		"CL_WriteSteamChallengeWord( data + commandLength + 1, steamIdLow );",
		"CL_WriteSteamChallengeWord( data + commandLength + 5, steamIdHigh );",
		"Com_Memcpy( data + commandLength + 9, ticket, ticketLength );",
		"*dataLength = payloadLength;",
	)

	_assert_order(
		send_challenge,
		"if ( CL_BuildSteamChallengeRequest( data, sizeof( data ), &dataLength ) ) {",
		"NET_OutOfBandRaw( NS_CLIENT, clc.serverAddress, data, dataLength );",
		"return;",
		"if ( NET_ProtocolSupportsPlatformAuth() && !Sys_IsLANAddress( clc.serverAddress ) ) {",
		"Com_DPrintf( \"Steam challenge auth unavailable; falling back to bare %s\\n\", NET_GetChallengeRequestCommand() );",
		"NET_OutOfBandPrint( NS_CLIENT, clc.serverAddress, \"%s\", NET_GetChallengeRequestCommand() );",
	)

	_assert_order(
		check_resend,
		"if ( clc.demoplaying ) {",
		"if ( cls.state != CA_CONNECTING && cls.state != CA_CHALLENGING ) {",
		"if ( cls.realtime - clc.connectTime < RETRANSMIT_TIMEOUT ) {",
		"clc.connectTime = cls.realtime;",
		"clc.connectPacketCount++;",
		"case CA_CONNECTING:",
		"if ( NET_ProtocolUsesLegacyAuthorize() && !Sys_IsLANAddress( clc.serverAddress ) ) {",
		"CL_SendChallengeRequest();",
		"case CA_CHALLENGING:",
		"port = Cvar_VariableValue (\"net_qport\");",
		"Info_SetValueForKey( info, NET_GetProtocolInfoKey(), va(\"%i\", NET_ProtocolVersion() ) );",
		"if ( NET_ProtocolUsesClientQport() ) {",
		"Info_SetValueForKey( info, NET_GetChallengeInfoKey(), va(\"%i\", clc.challenge ) );",
		"Com_sprintf( data, sizeof( data ), \"%s \\\"%s\\\"\", NET_GetConnectRequestCommand(), info );",
		"if ( NET_ProtocolUsesCompressedConnect() ) {",
		"NET_OutOfBandData( NS_CLIENT, clc.serverAddress, (byte *)data, dataLength );",
		"NET_OutOfBandPrint( NS_CLIENT, clc.serverAddress, \"%s\", data );",
		"cvar_modifiedFlags &= ~CVAR_USERINFO;",
		"Com_Error( ERR_FATAL, \"CL_CheckForResend: bad cls.state\" );",
	)

	_assert_order(
		connectionless,
		"MSG_BeginReadingOOB( msg );",
		"MSG_ReadLong( msg );",
		"s = MSG_ReadStringLine( msg );",
		"Cmd_TokenizeString( s );",
		"c = Cmd_Argv(0);",
		"if ( NET_IsChallengeResponse( c ) ) {",
		"if ( cls.state != CA_CONNECTING ) {",
		"clc.challenge = atoi(Cmd_Argv(1));",
		"Q_strncpyz( clc.challengeResponseText, Cmd_Argv(2), sizeof( clc.challengeResponseText ) );",
		"cls.state = CA_CHALLENGING;",
		"clc.connectPacketCount = 0;",
		"clc.connectTime = -99999;",
		"clc.serverAddress = from;",
		"if ( NET_IsConnectResponse( c ) ) {",
		"if ( cls.state >= CA_CONNECTED ) {",
		"if ( cls.state != CA_CHALLENGING ) {",
		"if ( !NET_CompareBaseAdr( from, clc.serverAddress ) ) {",
		"Netchan_Setup (NS_CLIENT, &clc.netchan, from, Cvar_VariableValue( \"net_qport\" ) );",
		"cls.state = CA_CONNECTED;",
		"clc.lastPacketSentTime = -9999;",
		"if ( NET_IsInfoResponse( c ) ) {",
		"if ( NET_IsStatusResponse( c ) ) {",
		"if ( NET_IsDisconnectCommand( c ) ) {",
		"if ( NET_IsEchoCommand( c ) ) {",
		"if ( NET_IsKeyAuthorizeResponse( c ) ) {",
		"if ( NET_IsMotdResponse( c ) ) {",
		"if ( NET_IsPrintCommand( c ) ) {",
		"if ( NET_IsServersResponse( c ) ) {",
		"Com_DPrintf (\"Unknown connectionless packet command.\\n\");",
	)

	_assert_order(
		packet_event,
		"clc.lastPacketTime = cls.realtime;",
		"if ( msg->cursize >= 4 && *(int *)msg->data == -1 ) {",
		"CL_ConnectionlessPacket( from, msg );",
		"if ( cls.state < CA_CONNECTED ) {",
		"if ( msg->cursize < 4 ) {",
		"if ( !NET_CompareAdr( from, clc.netchan.remoteAddress ) ) {",
		"if (!CL_Netchan_Process( &clc.netchan, msg) ) {",
		"headerBytes = msg->readcount;",
		"clc.serverMessageSequence = LittleLong( *(int *)msg->data );",
		"CL_ParseServerMessage( msg );",
		"if ( clc.demorecording && !clc.demowaiting ) {",
		"CL_WriteDemoMessage( msg, headerBytes );",
	)

	for expected in (
		"`sub_4BBBE0` starts by printing",
		"`sub_4BC190` stamps the last-packet time",
		"`sub_4BBBE0` (`0x004BBBE0`) | `CL_ConnectionlessPacket`",
		"`sub_4BC190` (`0x004BC190`) | `CL_PacketEvent`",
		"shows retail `CL_CheckForResend` copying `getchallenge `",
		"`CL_BuildSteamChallengeRequest` builds the retail payload",
	):
		assert expected in (round_105 + round_290)

	assert "Implementation round - 2026-06-04, client connectionless handshake manifest expansion" in plan


def test_manifest_covers_download_bootstrap_and_compatibility_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	cl_main = _read(CL_MAIN_PATH)
	cl_parse = _read(CL_PARSE_PATH)
	sv_client = _read(SV_CLIENT_PATH)
	common_c = _read(COMMON_C_PATH)
	plan = _read(PLAN_PATH)
	round_105 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_105.md")
	round_62 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_62.md")
	netcode_audit = _read(REPO_ROOT / "docs/reverse-engineering/engine-netcode-parity-audit-2026-04-16.md")

	for symbol in (
		"CL_DownloadsComplete",
		"CL_InitDownloads",
		"CL_Workshop_Frame",
		"SV_DoneDownload_f",
		"ClassicUdpAutodownloadCompatibility",
	):
		assert entries[symbol]["status"] in {"verified", "reconstructed", "compatibility"}
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_download_bootstrap_and_compatibility_lane" in entries[symbol]["tests"]

	assert entries["CL_DownloadsComplete"]["retail_address"] == "0x004BB9C0"
	assert entries["CL_InitDownloads"]["retail_address"] == "0x004BBA30"
	assert entries["CL_Workshop_Frame"]["retail_address"] == "0x004BC320"
	assert entries["SV_DoneDownload_f"]["retail_address"] == "0x004DFAC0"
	assert entries["ClassicUdpAutodownloadCompatibility"]["retail_address"] is None
	assert "inactive compatibility lane" in " ".join(entries["ClassicUdpAutodownloadCompatibility"]["compatibility_notes"])
	assert "no longer injects svc_download payloads" in " ".join(entries["ClassicUdpAutodownloadCompatibility"]["compatibility_notes"])
	assert "classic donedl restart branch" in " ".join(entries["CL_DownloadsComplete"]["compatibility_notes"])

	for expected in (
		"FUN_004bb9c0,004bb9c0,107,0,unknown",
		"FUN_004bba30,004bba30,422,0,unknown",
		"FUN_004bc320,004bc320,187,0,unknown",
		"FUN_004dfac0,004dfac0,44,0,unknown",
		"FUN_004dfee0,004dfee0,78,0,unknown",
		"FUN_004e0090,004e0090,235,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004bb9c0    int32_t sub_4bb9c0()",
		"004bb9c0  data_1528ba0 = 6",
		"004bb9f5  sub_4cd250(\"r_uiFullScreen\", U\"0\")",
		"004bba30    int32_t sub_4bba30()",
		"004bbaa0          sub_4c9860(esi, \"Server requires the following wo",
		"004bbb0f              sscanf(i_4, \"%llu\", &var_18)",
		"004bbb29              if (sub_4699c0(var_18, var_14, 1) != 0)",
		"004bbb4d                  sub_4cd250(\"cl_downloadItem\", sub_4d9220(&data_52d0f4))",
		"004bbb67                  sub_4cd250(\"cl_downloadName\", sub_4d9220(\"Workshop item %i of %i\"))",
		"004bc320    int32_t sub_4bc320()",
		"004bc35b              sub_4c9860(esi, \"Steamworks downloads complete - ",
		"004bc392          sub_4c9ab0(\"Steamworks downloads complete\\n\")",
		"004dfac0    void* sub_4dfac0(int32_t* arg1)",
		"004dfad3  void* result = sub_4c9ab0(\"clientDownload: %s Done\\n\")",
		"004dfade  if (*arg1 != 4)",
		"004dfae1      st0_1, result = sub_4df850(arg1, arg1)",
	):
		assert expected in hlil_part04

	for absent in (
		"svc_download",
		"nextdl",
		"stopdl",
		"donedl",
		"broken download",
		"writing block",
	):
		assert absent not in hlil_part04

	downloads_complete = _function_block(cl_main, "void CL_DownloadsComplete( void )")
	workshop_bootstrap = _function_block(cl_main, "static qboolean CL_Workshop_BeginBootstrap( void )")
	workshop_frame = _function_block(cl_main, "static void CL_Workshop_Frame( void )")
	init_downloads = _function_block(cl_main, "void CL_InitDownloads(void)")
	begin_download = _function_block(cl_main, "void CL_BeginDownload( const char *localName, const char *remoteName )")
	parse_download = _function_block(cl_parse, "void CL_ParseDownload ( msg_t *msg )")
	done_download = _function_block(sv_client, "void SV_DoneDownload_f( client_t *cl )")
	begin_download_server = _function_block(sv_client, "void SV_BeginDownload_f( client_t *cl )")
	write_download = _function_block(sv_client, "void SV_WriteDownloadToClient( client_t *cl , msg_t *msg )")

	_assert_order(
		downloads_complete,
		"if (clc.downloadRestart) {",
		"FS_Restart(clc.checksumFeed);",
		"CL_AddReliableCommand( NET_GetDownloadDoneCommand() );",
		"return;",
		"cls.state = CA_LOADING;",
		"Com_EventLoop();",
		"if ( cls.state != CA_LOADING ) {",
		"Cvar_Set(\"r_uiFullScreen\", \"0\");",
		"CL_FlushMemory();",
		"cls.cgameStarted = qtrue;",
		"CL_InitCGame();",
		"CL_SendPureChecksums();",
		"CL_WritePacket();",
		"CL_WritePacket();",
		"CL_WritePacket();",
	)

	_assert_order(
		workshop_bootstrap,
		"requiredItems = CL_GetConfigStringValue( CL_STEAM_WORKSHOP_ITEMS_CONFIGSTRING );",
		"Q_strncpyz( workshopItems, requiredItems, sizeof( workshopItems ) );",
		"Com_Printf( \"Server requires the following workshop items: %s\\n\", workshopItems );",
		"if ( !CL_WorkshopServiceSupportsSteamBootstrap() ) {",
		"for ( token = strtok( workshopItems, CL_STEAM_WORKSHOP_ITEM_DELIMS ); token; token = strtok( NULL, CL_STEAM_WORKSHOP_ITEM_DELIMS ) ) {",
		"CL_Workshop_ClearBootstrapState( qtrue );",
		"cl_steamWorkshopDownloadState.active = qtrue;",
		"if ( !CL_ParseSteamIdString( token, &itemIdLow, &itemIdHigh ) ) {",
		"if ( CL_Workshop_RequestDownload( itemIndex ) ) {",
		"CL_Workshop_SetDownloadRequestCvars( itemIndex );",
		"cls.state = CA_CONNECTED;",
	)

	_assert_order(
		workshop_frame,
		"if ( !cl_steamWorkshopDownloadState.active ) {",
		"if ( !CL_Workshop_DownloadsSettled() ) {",
		"if ( cl_steamWorkshopDownloadState.downloadsRequested ) {",
		"Com_Printf( \"Steamworks downloads complete - FS restart is required\\n\" );",
		"FS_Restart( clc.checksumFeed );",
		"return;",
		"Com_Printf( \"Steamworks downloads complete\\n\" );",
		"if ( FS_ComparePaks( missingfiles, sizeof( missingfiles ), qfalse ) ) {",
		"cl_steamWorkshopDownloadState.active = qfalse;",
		"CL_DownloadsComplete();",
	)

	_assert_order(
		init_downloads,
		"CL_Workshop_ClearBootstrapState( qtrue );",
		"if ( CL_Workshop_BeginBootstrap() ) {",
		"if ( FS_ComparePaks( clc.downloadList, sizeof( clc.downloadList ) , qtrue ) ) {",
		"cls.state = CA_CONNECTED;",
		"CL_NextDownload();",
		"CL_DownloadsComplete();",
	)

	_assert_order(
		begin_download,
		"Cvar_Set( \"cl_downloadName\", remoteName );",
		"clc.downloadBlock = 0;",
		"CL_AddReliableCommand( va(\"%s %s\", NET_GetDownloadRequestCommand(), remoteName) );",
	)

	_assert_order(
		parse_download,
		"block = MSG_ReadShort ( msg );",
		"if ( !block )",
		"clc.downloadSize = MSG_ReadLong ( msg );",
		"size = MSG_ReadShort ( msg );",
		"MSG_ReadData( msg, data, size );",
		"if (clc.downloadBlock != block) {",
		"CL_AddReliableCommand( NET_GetDownloadStopCommand() );",
		"CL_AddReliableCommand( va(\"%s %d\", NET_GetDownloadNextCommand(), clc.downloadBlock) );",
		"clc.downloadBlock++;",
		"FS_SV_Rename ( clc.downloadTempName, clc.downloadName );",
		"CL_WritePacket();",
		"CL_WritePacket();",
		"CL_NextDownload ();",
	)

	_assert_order(
		done_download,
		"Com_DPrintf( \"clientDownload: %s Done\\n\", cl->name);",
		"if ( cl->state != CS_ACTIVE ) {",
		"SV_SendClientGameState( cl );",
	)
	assert "SV_SendClientGameState(cl);" not in done_download

	_assert_order(
		begin_download_server,
		"SV_CloseDownload( cl );",
		"Com_DPrintf( \"clientDownload: %d : legacy UDP download request",
	)
	assert "Q_strncpyz( cl->downloadName" not in begin_download_server

	_assert_order(
		write_download,
		"if (!*cl->downloadName)",
		"MSG_WriteByte( msg, svc_download );",
		"MSG_WriteShort( msg, 0 );",
		"MSG_WriteLong( msg, -1 );",
		"while (cl->downloadCurrentBlock - cl->downloadClientBlock < MAX_DOWNLOAD_WINDOW",
		"cl->downloadBlockSize[cl->downloadCurrentBlock % MAX_DOWNLOAD_WINDOW] = 0;",
		"if (cl->downloadXmitBlock == cl->downloadCurrentBlock) {",
		"cl->downloadXmitBlock = cl->downloadClientBlock;",
		"MSG_WriteByte( msg, svc_download );",
		"MSG_WriteShort( msg, cl->downloadXmitBlock );",
		"MSG_WriteData( msg, cl->downloadBlocks[curindex], cl->downloadBlockSize[curindex] );",
	)

	for expected in (
		"\"download\",",
		"\"nextdl\",",
		"\"stopdl\",",
		"\"donedl\",",
		"qboolean NET_IsDownloadRequestCommand( const char *command )",
		"qboolean NET_IsDownloadNextCommand( const char *command )",
		"qboolean NET_IsDownloadStopCommand( const char *command )",
		"qboolean NET_IsDownloadDoneCommand( const char *command )",
	):
		assert expected in common_c

	for expected in (
		"{NULL, NET_GetDownloadRequestCommand, SV_BeginDownload_f}",
		"{NULL, NET_GetDownloadNextCommand, SV_NextDownload_f}",
		"{NULL, NET_GetDownloadStopCommand, SV_StopDownload_f}",
		"{NULL, NET_GetDownloadDoneCommand, SV_DoneDownload_f}",
	):
		assert expected in sv_client

	for expected in (
		"`sub_4BB9C0` is the exact `CL_DownloadsComplete` owner",
		"`sub_4BBA30` is the retained `CL_InitDownloads` owner",
		"`sub_4DFAC0 -> SV_DoneDownload_f`",
		"autodownload reliable-command tokens: `download`, `nextdl`, `stopdl`, and",
		"Preserved the existing UDP pk3 autodownload behavior",
	):
		assert expected in (round_105 + round_62 + netcode_audit)

	assert "Implementation round - 2026-06-04, download bootstrap and compatibility manifest expansion" in plan


def test_manifest_covers_client_server_message_parse_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part06 = _read(HLIL_PART06_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	cl_parse = _read(CL_PARSE_PATH)
	plan = _read(PLAN_PATH)
	round_125 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_125.md")
	round_127 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_127.md")
	round_131 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_131.md")
	round_280 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_280.md")
	netcode_audit = _read(REPO_ROOT / "docs/reverse-engineering/engine-netcode-parity-audit-2026-04-16.md")

	for symbol in (
		"CL_ParsePacketEntities",
		"CL_ParseSnapshot",
		"CL_SystemInfoChanged",
		"CL_ParseGamestate",
		"CL_ParseServerMessage",
	):
		assert entries[symbol]["status"] in {"verified", "reconstructed"}
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_client_server_message_parse_lane" in entries[symbol]["tests"]

	assert entries["CL_ParsePacketEntities"]["retail_address"] == "0x004BD000"
	assert entries["CL_ParseSnapshot"]["retail_address"] == "0x004BD350"
	assert entries["CL_SystemInfoChanged"]["retail_address"] == "0x004BD620"
	assert entries["CL_ParseGamestate"]["retail_address"] == "0x004BD790"
	assert entries["CL_ParseServerMessage"]["retail_address"] == "0x004BDA00"
	assert "svc_download" in " ".join(entries["CL_ParseServerMessage"]["compatibility_notes"])

	for expected in (
		"FUN_004bd000,004bd000,827,0,unknown",
		"FUN_004bd350,004bd350,713,0,unknown",
		"FUN_004bd620,004bd620,360,0,unknown",
		"FUN_004bd790,004bd790,622,0,unknown",
		"FUN_004bda00,004bda00,367,0,unknown",
		"FUN_004d5ac0,004d5ac0,654,0,unknown",
		"FUN_004d66c0,004d66c0,1250,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004bd000    uint32_t sub_4bd000(void* arg1, void* arg2, void* arg3)",
		"004bd012  *(arg3 + 0x290) = data_1471e98",
		"004bd094              sub_4c9b60(1, \"CL_ParsePacketEntities: end of m",
		"004bd17d                  sub_4c9860(esi, \"%3i:  delta: %i\\n\")",
		"004bd221                  sub_4c9860(esi, \"%3i:  baseline: %i\\n\")",
		"004bd350    uint32_t sub_4bd350(void* arg1)",
		"004bd390  uint32_t var_298 = sub_4d5020(arg1)",
		"004bd407  if (eax_7 u> 0x20)",
		"004bd414      sub_4c9b60(1, \"CL_ParseSnapshot: Invalid size %",
		"004bd510  uint32_t result = sub_4bd000(arg1, esi, &var_2a0)",
		"004bd620    int32_t sub_4bd620(int32_t arg1 @ esi)",
		"004bd657  int32_t result = atoi(sub_4d9260(i_2, \"sv_serverid\"))",
		"004bd689          sub_4cd2f0()",
		"004bd6b2      sub_4d20c0(i, eax_5)",
		"004bd770              result = sub_4cd250(\"fs_game\", &data_54f9da)",
		"004bd790    int32_t* sub_4bd790(void* arg1)",
		"004bd7a7  sub_4b4930()",
		"004bd7c2  data_1606b80 = sub_4d5020(arg1)",
		"004bd80e              sub_4c9b60(1, \"configstring > MAX_CONFIGSTRINGS\")",
		"004bd8b3              sub_4c9b60(1, \"Baseline number out of range: %i\")",
		"004bd92a  sub_4bd620(esi)",
		"004bd948  sub_4bba30()",
		"004bda00    uint32_t sub_4bda00(void* arg1)",
		"004bda3b  sub_4d4a70(arg1)",
		"004bda41  uint32_t eax_2 = sub_4d5020(arg1)",
		"004bda59  if (eax_2 s< ecx_2 - 0x40)",
		"004bdb04                      sub_4bd790(arg1)",
		"004bdb0f                      sub_4bd350(arg1)",
		"004bdb21          sub_4c9b60(1, \"CL_ParseServerMessage: Illegible",
		"004bdb3c  sub_4c9b60(1, \"CL_ParseServerMessage: read past",
	):
		assert expected in hlil_part04

	for expected in (
		"0053f3d0  char const data_53f3d0[0x30] = \"CL_ParseSnapshot: Invalid size %d for areamask.\", 0",
		"0053f4c8  char const data_53f4c8[0x37] = \"CL_ParseServerMessage: read past end of server message\", 0",
		"0053f500  char const data_53f500[0x34] = \"CL_ParseServerMessage: Illegible server message %d\\n\", 0",
		"0053f534  char const data_53f534[0x10] = \"%3i:BAD CMD %i\\n\", 0",
	):
		assert expected in hlil_part06

	packet_entities = _function_block(cl_parse, "void CL_ParsePacketEntities( msg_t *msg, clSnapshot_t *oldframe, clSnapshot_t *newframe)")
	parse_snapshot = _function_block(cl_parse, "void CL_ParseSnapshot( msg_t *msg )")
	systeminfo = _function_block(cl_parse, "void CL_SystemInfoChanged( void )")
	gamestate = _function_block(cl_parse, "void CL_ParseGamestate( msg_t *msg )")
	command_string = _function_block(cl_parse, "void CL_ParseCommandString( msg_t *msg )")
	server_message = _function_block(cl_parse, "void CL_ParseServerMessage( msg_t *msg )")

	_assert_order(
		packet_entities,
		"newframe->parseEntitiesNum = cl.parseEntitiesNum;",
		"newframe->numEntities = 0;",
		"oldstate = NULL;",
		"if (!oldframe) {",
		"oldnum = 99999;",
		"newnum = MSG_ReadBits( msg, GENTITYNUM_BITS );",
		"if ( newnum == (MAX_GENTITIES-1) ) {",
		"if ( msg->readcount > msg->cursize ) {",
		"while ( oldnum < newnum ) {",
		"CL_DeltaEntity( msg, newframe, oldnum, oldstate, qtrue );",
		"if (oldnum == newnum) {",
		"CL_DeltaEntity( msg, newframe, newnum, oldstate, qfalse );",
		"if ( oldnum > newnum ) {",
		"CL_DeltaEntity( msg, newframe, newnum, &cl.entityBaselines[newnum], qfalse );",
		"while ( oldnum != 99999 ) {",
		"CL_DeltaEntity( msg, newframe, oldnum, oldstate, qtrue );",
	)

	_assert_order(
		parse_snapshot,
		"Com_Memset (&newSnap, 0, sizeof(newSnap));",
		"newSnap.serverCommandNum = clc.serverCommandSequence;",
		"newSnap.serverTime = MSG_ReadLong( msg );",
		"newSnap.messageNum = clc.serverMessageSequence;",
		"deltaNum = MSG_ReadByte( msg );",
		"newSnap.snapFlags = MSG_ReadByte( msg );",
		"if ( newSnap.deltaNum <= 0 ) {",
		"clc.demowaiting = qfalse;",
		"if ( !old->valid ) {",
		"len = MSG_ReadByte( msg );",
		"if ( len > sizeof( newSnap.areamask ) ) {",
		"Com_Error( ERR_DROP, \"CL_ParseSnapshot: Invalid size %d for areamask.\", len );",
		"MSG_ReadData( msg, &newSnap.areamask, len);",
		"SHOWNET( msg, \"playerstate\" );",
		"MSG_ReadDeltaPlayerstate( msg, &old->ps, &newSnap.ps );",
		"MSG_ReadDeltaPlayerstate( msg, NULL, &newSnap.ps );",
		"SHOWNET( msg, \"packet entities\" );",
		"CL_ParsePacketEntities( msg, old, &newSnap );",
		"if ( !newSnap.valid ) {",
		"cl.snap = newSnap;",
		"cl.snap.ping = 999;",
		"cl.snapshots[cl.snap.messageNum & PACKET_MASK] = cl.snap;",
		"cl.newSnapshots = qtrue;",
	)

	_assert_order(
		systeminfo,
		"systemInfo = cl.gameState.stringData + cl.gameState.stringOffsets[ CS_SYSTEMINFO ];",
		"cl.serverId = atoi( Info_ValueForKey( systemInfo, NET_GetServerIdInfoKey() ) );",
		"if ( clc.demoplaying ) {",
		"s = Info_ValueForKey( systemInfo, NET_GetCheatsInfoKey() );",
		"Cvar_SetCheatState();",
		"s = Info_ValueForKey( systemInfo, NET_GetPaksInfoKey() );",
		"FS_PureServerSetLoadedPaks( s, t );",
		"s = Info_ValueForKey( systemInfo, NET_GetReferencedPaksInfoKey() );",
		"FS_PureServerSetReferencedPaks( s, t );",
		"gameSet = qfalse;",
		"Info_NextPair( &s, key, value );",
		"if ( !Q_stricmp( key, NET_GetFsGameInfoKey() ) ) {",
		"Cvar_Set( key, value );",
		"if ( !gameSet && *Cvar_VariableString( NET_GetFsGameInfoKey() ) ) {",
		"Cvar_Set( NET_GetFsGameInfoKey(), \"\" );",
		"cl_connectedToPureServer = Cvar_VariableValue( NET_GetSystemPureInfoKey() );",
	)

	_assert_order(
		gamestate,
		"Con_Close();",
		"clc.connectPacketCount = 0;",
		"CL_ClearState();",
		"clc.serverCommandSequence = MSG_ReadLong( msg );",
		"cl.gameState.dataCount = 1;",
		"cmd = MSG_ReadByte( msg );",
		"if ( cmd == svc_EOF ) {",
		"if ( cmd == svc_configstring ) {",
		"i = MSG_ReadShort( msg );",
		"if ( i < 0 || i >= MAX_CONFIGSTRINGS ) {",
		"s = MSG_ReadBigString( msg );",
		"if ( len + 1 + cl.gameState.dataCount > MAX_GAMESTATE_CHARS ) {",
		"cl.gameState.stringOffsets[ i ] = cl.gameState.dataCount;",
		"} else if ( cmd == svc_baseline ) {",
		"newnum = MSG_ReadBits( msg, GENTITYNUM_BITS );",
		"if ( newnum < 0 || newnum >= MAX_GENTITIES ) {",
		"MSG_ReadDeltaEntity( msg, &nullstate, es, newnum );",
		"Com_Error( ERR_DROP, \"CL_ParseGamestate: bad command byte\" );",
		"clc.clientNum = MSG_ReadLong(msg);",
		"clc.checksumFeed = MSG_ReadLong( msg );",
		"CL_SystemInfoChanged();",
		"FS_ConditionalRestart( clc.checksumFeed );",
		"CL_InitDownloads();",
		"Cvar_Set( \"cl_paused\", \"0\" );",
	)

	_assert_order(
		command_string,
		"seq = MSG_ReadLong( msg );",
		"s = MSG_ReadString( msg );",
		"if ( clc.serverCommandSequence >= seq ) {",
		"clc.serverCommandSequence = seq;",
		"index = seq & (MAX_RELIABLE_COMMANDS-1);",
		"Q_strncpyz( clc.serverCommands[ index ], s, sizeof( clc.serverCommands[ index ] ) );",
	)

	_assert_order(
		server_message,
		"MSG_Bitstream(msg);",
		"clc.reliableAcknowledge = MSG_ReadLong( msg );",
		"if ( clc.reliableAcknowledge < clc.reliableSequence - MAX_RELIABLE_COMMANDS ) {",
		"if ( msg->readcount > msg->cursize ) {",
		"cmd = MSG_ReadByte( msg );",
		"if ( cmd == svc_EOF) {",
		"if ( cl_shownet->integer >= 2 ) {",
		"switch ( cmd ) {",
		"Com_Error (ERR_DROP,\"CL_ParseServerMessage: Illegible server message %d\\n\", cmd);",
		"case svc_serverCommand:",
		"CL_ParseCommandString( msg );",
		"case svc_gamestate:",
		"CL_ParseGamestate( msg );",
		"case svc_snapshot:",
		"CL_ParseSnapshot( msg );",
		"case svc_download:",
		"CL_ParseDownload( msg );",
	)

	for expected in (
		"`sub_4BD000 -> CL_ParsePacketEntities`",
		"`sub_4BD350` -> `CL_ParseSnapshot`",
		"`sub_4BD790` -> `CL_ParseGamestate`",
		"| `sub_4BD620` | `CL_SystemInfoChanged` |",
		"| `sub_4BDA00` | `CL_ParseServerMessage` |",
		"CL_SystemInfoChanged` server-id extraction",
	):
		assert expected in (round_125 + round_127 + round_131 + round_280 + netcode_audit)

	assert "Implementation round - 2026-06-04, client server-message parse manifest expansion" in plan


def test_manifest_covers_server_connectionless_control_plane_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part02 = _read(
		REPO_ROOT
		/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt"
	)
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part05 = _read(HLIL_PART05_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	ghidra_decompile = _read(GHIDRA_DECOMPILE_TOP_PATH)
	sv_main = _read(SV_MAIN_PATH)
	sv_client = _read(SV_CLIENT_PATH)
	server_h = _read(SERVER_H_PATH)
	plan = _read(PLAN_PATH)
	round_04 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_04.md")
	round_65 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_65.md")
	round_290 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_290.md")
	networking_audit = _read(REPO_ROOT / "docs/reverse-engineering/networking-parity-audit-2026-05-24.md")

	for symbol in (
		"SV_ConnectionlessPacket",
		"SV_PacketEvent",
		"SV_GetChallenge",
		"SV_DirectConnect",
	):
		assert entries[symbol]["status"] in {"verified", "reconstructed"}
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_server_connectionless_control_plane_lane" in entries[symbol]["tests"]

	assert "SteamServer_HandleIncomingPacket" in " ".join(entries["SV_ConnectionlessPacket"]["compatibility_notes"])
	assert "does not reject clients solely because sv_vac is zero" in entries["SV_GetChallenge"]["behavior_checkpoints"]
	assert "does not reject clients solely because sv_vac is zero" in entries["SV_DirectConnect"]["behavior_checkpoints"]

	for expected in (
		"FUN_004e4340,004e4340,445,0,unknown",
		"FUN_004e4500,004e4500,419,0,unknown",
		"FUN_004df430,004df430,555,0,unknown",
		"FUN_004e0750,004e0750,2381,0,unknown",
		"FUN_00465d50,00465d50,94,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"00465d50    uint32_t sub_465d50(void* arg1, void* arg2)",
		"00465d82  uint32_t esi_6 = (((((zx.d(*(arg1 + 4)) << 8) + zx.d(*(arg1 + 5))) << 8)",
		"00465d84  int32_t eax_2 = SteamGameServer()",
		"00465dad  return zx.d((*(*eax_2 + 0x94))(*(arg2 + 8), *(arg2 + 0x10), esi_6, zx.d(*(arg1 + 0x12))))",
	):
		assert expected in hlil_part02

	for expected in (
		"004e4340    int32_t sub_4e4340",
		"004e4375  sub_4d4a80(arg9)",
		"004e437b  sub_4d5020(arg9)",
		"004e4398  if (sub_4d9020(\"connect\", *(arg9 + 8) + 4, 7) == 0)",
		"004e439d      sub_4d3e60(arg9, 0xc)",
		"004e43a6  sub_4d5100(arg9)",
		"004e4405  if (sub_4d9060(eax_5, \"getchallenge\") == 0)",
		"004e442a      int32_t eax_7 = sub_4df430(var_1c, arg5, arg6, arg7, arg8, arg9)",
		"004e4453  if (sub_4d9060(eax_5, \"connect\") == 0)",
		"004e4477      int32_t eax_9 = sub_4e0750(var_1c, arg5, arg6, arg7, arg8)",
		"004e44a7      eax_10 = sub_465d50(&var_1c, arg9)",
		"004e44e4          eax_10 = sub_4c9ab0(\"bad connectionless packet from %…\")",
		"004e4500    int32_t sub_4e4500",
		"004e452d      if (*(arg6 + 0x10) s>= 4 && **(arg6 + 8) == 0xffffffff)",
		"004e455d          return sub_4e4340(&__saved_ebp, esi.b, edi.b, arg1, arg2, arg3, arg4, arg5, arg6)",
		"004e4565      sub_4d5020(arg6)",
		"004e456b      int16_t eax_1 = sub_4d4ff0(arg6)",
		"004e4660          sub_4c9860(esi_2, \"SV_PacketEvent: fixing up a tran…\")",
		"004e4675      result = sub_4e4f80(esi_2, arg6)",
		"004e46a2          return sub_4e05c0(esi_2, arg6)",
	):
		assert expected in hlil_part05

	for expected in (
		"004df430    int32_t sub_4df430",
		"004df527  for (i = 0; i s< 0x400; )",
		"004df51b      esi += 0x2b8",
		"004df5e7      var_18_3 = \"print\\nAuth token too large.\\n\"",
		"004df5b1      var_18_3 = \"print\\nNo Steam auth token.\\n\"",
		"004df65a          return sub_4d7080(1, arg1, arg2, arg3, ebx, edi_4, \"challengeResponse %i\")",
		"004e0750    int32_t sub_4e0750",
		"004e07d0  if (atoi(sub_4d9260(&var_408, sub_4af500(6))) != 0x5b)",
		"004e09e0          for (void* i = &data_13337d4; i s< &data_13e17d4; i += 0x2b8)",
		"&& eax_11 == *i)",
	):
		assert expected in hlil_part04

	assert 'FUN_004d9620(local_408,"steam",uVar2);' in ghidra_decompile

	connectionless = _function_block(sv_main, "void SV_ConnectionlessPacket( netadr_t from, msg_t *msg )")
	packet_event = _function_block(sv_main, "void SV_PacketEvent( netadr_t from, msg_t *msg )")
	parse_challenge = _function_block(
		sv_client, "static qboolean SV_ParseSteamChallengeAuth( challenge_t *challenge, const msg_t *msg, const char **rejectMessage )"
	)
	get_challenge = _function_block(sv_client, "void SV_GetChallenge( netadr_t from, msg_t *msg )")
	direct_connect = _function_block(sv_client, "void SV_DirectConnect( netadr_t from )")

	_assert_order(
		connectionless,
		"MSG_BeginReadingOOB( msg );",
		"MSG_ReadLong( msg );",
		"if ( NET_ProtocolUsesCompressedConnect() && NET_IsConnectRequestPacket( msg ) ) {",
		"Huff_Decompress(msg, 12);",
		"s = MSG_ReadStringLine( msg );",
		"Cmd_TokenizeString( s );",
		"c = Cmd_Argv(0);",
		"if ( NET_IsGetStatusRequest( c ) ) {",
		"SVC_Status( from",
		"} else if ( NET_IsGetInfoRequest( c ) ) {",
		"SVC_Info( from );",
		"} else if ( NET_IsGetChallengeRequest( c ) ) {",
		"SV_GetChallenge( from, msg );",
		"} else if ( NET_IsConnectRequest( c ) ) {",
		"SV_DirectConnect( from );",
		"} else if ( NET_IsIpAuthorizeResponse( c ) ) {",
		"SV_AuthorizeIpPacket( from );",
		"} else if ( NET_IsRconCommand( c ) ) {",
		"SVC_RemoteCommand( from, msg );",
		"} else if ( NET_IsDisconnectCommand( c ) ) {",
		"Com_DPrintf (\"bad connectionless packet from %s:\\n%s\\n\"",
	)

	_assert_order(
		packet_event,
		"if ( msg->cursize >= 4 && *(int *)msg->data == -1) {",
		"SV_ConnectionlessPacket( from, msg );",
		"MSG_BeginReadingOOB( msg );",
		"MSG_ReadLong( msg );",
		"qport = MSG_ReadShort( msg ) & 0xffff;",
		"for (i=0, cl=svs.clients ; i < sv_maxclients->integer ; i++,cl++) {",
		"if (cl->state == CS_FREE) {",
		"if ( !NET_CompareBaseAdr( from, cl->netchan.remoteAddress ) ) {",
		"if (cl->netchan.qport != qport) {",
		"Com_Printf( \"SV_PacketEvent: fixing up a translated port\\n\" );",
		"if (SV_Netchan_Process(cl, msg)) {",
		"if (cl->state != CS_ZOMBIE) {",
		"cl->lastPacketTime = svs.time;",
		"SV_ExecuteClientMessage( cl, msg );",
		"NET_OutOfBandPrint( NS_SERVER, from, \"%s\", NET_GetDisconnectCommand() );",
	)

	_assert_order(
		parse_challenge,
		"steamIdOffset = 4 + (int)strlen( command ) + 1;",
		"ticketOffset = steamIdOffset + 8;",
		"ticketLength = msg->cursize - ticketOffset;",
		"if ( ticketLength <= QL_STEAM_CHALLENGE_TOKEN_MIN_LENGTH ) {",
		"*rejectMessage = \"No Steam auth token.\";",
		"if ( ticketLength > QL_STEAM_AUTH_TICKET_MAX_LENGTH ) {",
		"*rejectMessage = \"Auth token too large.\";",
		"challenge->platformSteamIdLow = SV_ReadSteamChallengeWord( data + steamIdOffset );",
		"challenge->platformSteamIdHigh = SV_ReadSteamChallengeWord( data + steamIdOffset + 4 );",
		"Com_Memcpy( challenge->platformAuthTicket, data + ticketOffset, ticketLength );",
	)

	assert "#define\tMAX_CHALLENGES\t1024" in server_h
	assert "platformAuthTicket[QL_STEAM_AUTH_TICKET_MAX_LENGTH]" in server_h
	assert '"VAC is disabled on this server"' not in sv_client
	assert 'NET_OutOfBandPrint( NS_SERVER, from, "%s\\n%s\\n", NET_GetPrintCommand(), message );' not in get_challenge

	_assert_order(
		get_challenge,
		"if ( Cvar_VariableValue( \"g_gametype\" ) == GT_SINGLE_PLAYER || Cvar_VariableValue(\"ui_singlePlayerActive\")) {",
		"oldest = 0;",
		"challenge = &svs.challenges[0];",
		"for (i = 0 ; i < MAX_CHALLENGES ; i++, challenge++) {",
		"challenge->challenge = ( (rand() << 16) ^ rand() ) ^ svs.time;",
		"SV_ClearChallengePlatformAuth( challenge );",
		"if ( Sys_IsLANAddress( from ) ) {",
		"NET_OutOfBandPrint( NS_SERVER, from, \"%s %i\", NET_GetChallengeResponseCommand(), challenge->challenge );",
		"if ( NET_ProtocolSupportsPlatformAuth() ) {",
		"if ( !SV_ParseSteamChallengeAuth( challenge, msg, &rejectMessage ) ) {",
		"NET_OutOfBandPrint( NS_SERVER, from, \"%s\\n%s\\n\", NET_GetPrintCommand(),",
		"challenge->pingTime = svs.time;",
		"NET_OutOfBandPrint( NS_SERVER, from, \"%s %i\", NET_GetChallengeResponseCommand(), challenge->challenge );",
	)

	assert 'NET_OutOfBandPrint( NS_SERVER, from, "%s\\n%s\\n", NET_GetPrintCommand(), message );' not in direct_connect
	_assert_order(
		direct_connect,
		"version = atoi( Info_ValueForKey( userinfo, NET_GetProtocolInfoKey() ) );",
		"if ( !NET_ProtocolSupports( version ) ) {",
		"challenge = atoi( Info_ValueForKey( userinfo, NET_GetChallengeInfoKey() ) );",
		"if ( NET_ProtocolUsesClientQport() ) {",
		"serverTypeError[0] = '\\0';",
		"if ( !SV_ServerTypeAllowsConnection( from, serverTypeError, sizeof( serverTypeError ) ) ) {",
		"for (i=0,cl=svs.clients ; i < sv_maxclients->integer ; i++,cl++) {",
		"challengeIndex = -1;",
		"if ( !NET_IsLocalAddress (from) ) {",
		"for (i=0 ; i<MAX_CHALLENGES ; i++) {",
		"Info_SetValueForKey( userinfo, NET_GetClientIpInfoKey(), NET_AdrToString( from ) );",
		"SV_LogVACStatus( &from, \"accepted\", ( sv_vac && sv_vac->integer ) ? \"enabled\" : \"disabled\",",
		"Netchan_Setup (NS_SERVER, &newcl->netchan , from, qport);",
		"capturedFromChallenge = ( challengeIndex >= 0 )",
		"? SV_CapturePlatformAuthFromChallenge( newcl, &svs.challenges[challengeIndex] )",
		"Info_SetValueForKey( userinfo, \"steam\", newcl->platformSteamId );",
		"Info_SetValueForKey( userinfo, \"steamid\", newcl->platformSteamId );",
		"denied = SV_GameClientConnect( clientNum, qtrue, qfalse );",
		"denied = SV_BeginPlatformAuthSession( newcl, &from );",
		"NET_OutOfBandPrint( NS_SERVER, from, \"%s\", NET_GetConnectResponseCommand() );",
	)

	for expected in (
		"`sub_465d50` (`0x00465d50`) | `SteamServer_HandleIncomingPacket`",
		"`sub_4E4340 -> SV_ConnectionlessPacket`",
		"`sub_4E4500 -> SV_PacketEvent`",
		"`sub_4DF430` as `SV_GetChallenge`",
		"`sub_4E0750` as `SV_DirectConnect`",
		"Retail `SV_GetChallenge` derives token length from the packet cursor size",
		"`SV_DirectConnect` now publishes `steam` and `steamid` userinfo",
	):
		assert expected in (round_04 + round_65 + round_290 + networking_audit)

	assert "This pass did not find the local rejection text `VAC is disabled on this" in networking_audit
	assert "Implementation round - 2026-06-04, server connectionless control-plane manifest expansion" in plan


def test_manifest_covers_server_rate_scheduler_helper_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part05 = _read(HLIL_PART05_PATH)
	sv_snapshot = _read(SV_SNAPSHOT_PATH)
	round_65 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_65.md")
	plan = _read(PLAN_PATH)

	entry = entries["SV_RateMsec"]
	assert entry["kind"] == "source_helper"
	assert entry["status"] == "verified"
	assert entry["retail_address"] is None
	assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_server_rate_scheduler_helper_lane" in entry["tests"]
	assert "static source helper has no separate promoted retail address" in entry["compatibility_notes"][0]

	for expected in (
		"HEADER_RATE_BYTES is 48",
		"clamps message sizes above 1500 bytes",
		"forces sv_MaxRate to at least 1000",
		"SV_SendMessageToClient uses the helper for full messages",
	):
		assert expected in " ".join(entry["behavior_checkpoints"])

	for expected in (
		"#define\tHEADER_RATE_BYTES\t48",
		"static int SV_RateMsec( client_t *client, int messageSize )",
		"rateMsec = SV_RateMsec( client, msg->cursize );",
		"SV_RateMsec( c, c->netchan.unsentLength - c->netchan.unsentFragmentStart );",
	):
		assert expected in sv_snapshot

	rate_msec = _function_block(sv_snapshot, "static int SV_RateMsec( client_t *client, int messageSize )")
	_assert_order(
		rate_msec,
		"if ( messageSize > 1500 ) {",
		"messageSize = 1500;",
		"rate = client->rate;",
		"if ( sv_maxRate->integer ) {",
		"if ( sv_maxRate->integer < 1000 ) {",
		"Cvar_Set( \"sv_MaxRate\", \"1000\" );",
		"if ( sv_maxRate->integer < rate ) {",
		"rate = sv_maxRate->integer;",
		"rateMsec = ( messageSize + HEADER_RATE_BYTES ) * 1000 / rate;",
		"return rateMsec;",
	)

	send_message = _function_block(sv_snapshot, "void SV_SendMessageToClient( msg_t *msg, client_t *client )")
	_assert_order(
		send_message,
		"SV_Netchan_Transmit( client, msg );",
		"if ( client->netchan.remoteAddress.type == NA_LOOPBACK",
		"client->nextSnapshotTime = svs.time - 1;",
		"rateMsec = SV_RateMsec( client, msg->cursize );",
		"if ( rateMsec < client->snapshotMsec ) {",
		"rateMsec = client->snapshotMsec;",
		"client->rateDelayed = qfalse;",
		"} else {",
		"client->rateDelayed = qtrue;",
		"client->nextSnapshotTime = svs.time + rateMsec;",
		"if ( client->state != CS_ACTIVE ) {",
		"if ( !*client->downloadName && client->nextSnapshotTime < svs.time + 1000 ) {",
		"client->nextSnapshotTime = svs.time + 1000;",
	)

	send_messages = _function_block(sv_snapshot, "void SV_SendClientMessages( void )")
	_assert_order(
		send_messages,
		"if ( svs.time < c->nextSnapshotTime ) {",
		"continue;",
		"if ( c->netchan.unsentFragments ) {",
		"c->nextSnapshotTime = svs.time +",
		"SV_RateMsec( c, c->netchan.unsentLength - c->netchan.unsentFragmentStart );",
		"SV_Netchan_TransmitNextFragment( c );",
		"continue;",
		"SV_SendClientSnapshot( c );",
	)

	for expected in (
		"004e5900    void sub_4e5900(int32_t* arg1, float arg2)",
		"004e59c6  if (edi_1 s> 0x5dc)",
		"004e59c8      edi_1 = 0x5dc",
		"004e59f8  arg1 = divs.dp.d(sx.q((edi_1 + 0x30) * 0x3e8),",
		"004e5a0f  if ((eax_13:1.b & 0x41) != 0)",
		"004e5a2a      *(arg2 i+ 0x109c8) = 1",
		"004e5a1c      *(arg2 i+ 0x109c8) = 0",
		"004e5a51  *(arg2 i+ 0x109c4) = edi_2",
		"004e5b90    void* sub_4e5b90()",
		"004e5bde                  if (edi_2 s> 0x5dc)",
		"004e5be0                      edi_2 = 0x5dc",
		"004e5c0e                  esi[0x4271] = divs.dp.d(sx.q((edi_2 + 0x30) * 0x3e8),",
		"004e5c14                  result = sub_4e4e20(esi)",
	):
		assert expected in hlil_part05

	for expected in (
		"`sub_4E5900 -> SV_SendMessageToClient`",
		"`sub_4E5B90 -> SV_SendClientMessages`",
		"preserve the retained rate\n   control, snapshot emit, fragment-drain, and per-client send loop",
	):
		assert expected in round_65

	assert "Implementation round - 2026-06-04, server rate scheduler helper manifest expansion" in plan


def test_manifest_covers_server_snapshot_authoring_lane() -> None:
	entries = {entry["symbol"]: entry for entry in _manifest()["entries"]}
	hlil_part05 = _read(HLIL_PART05_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	sv_snapshot = _read(SV_SNAPSHOT_PATH)
	plan = _read(PLAN_PATH)
	round_65 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_65.md")
	netcode_audit = _read(REPO_ROOT / "docs/reverse-engineering/engine-netcode-parity-audit-2026-04-16.md")

	for symbol in (
		"SV_EmitPacketEntities",
		"SV_WriteSnapshotToClient",
		"SV_UpdateServerCommandsToClient",
		"SV_BuildClientSnapshot",
		"SV_SendMessageToClient",
		"SV_SendClientSnapshot",
		"SV_SendClientMessages",
	):
		assert entries[symbol]["status"] == "verified"
		assert entries[symbol]["behavior_checkpoints"]
		assert "tests/test_netcode_parity_manifest.py::test_manifest_covers_server_snapshot_authoring_lane" in entries[symbol]["tests"]

	send_snapshot_entry = entries["SV_SendClientSnapshot"]
	assert send_snapshot_entry.get("compatibility_notes", []) == []

	for expected in (
		"FUN_004e4fc0,004e4fc0,281,0,unknown",
		"FUN_004e50e0,004e50e0,348,0,unknown",
		"FUN_004e5240,004e5240,111,0,unknown",
		"FUN_004e5680,004e5680,628,0,unknown",
		"FUN_004e5900,004e5900,444,0,unknown",
		"FUN_004e5ac0,004e5ac0,203,0,unknown",
		"FUN_004e5b90,004e5b90,174,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004e4fc0    int32_t* sub_4e4fc0(void* arg1, void* arg2, int32_t* arg3)",
		"004e50df              return sub_4d4af0(arg3, 0x3ff, 0xa)",
		"004e50e0    void* __convention(\"regparm\") sub_4e50e0(int32_t* arg1, int32_t* arg2 @ edi)",
		"004e5173  sub_4d4dc0(arg2, 7)",
		"004e5194  sub_4d4e30(arg2, eax_6)",
		"004e51d0  sub_4d4dc0(arg2, arg1[(eax & 0x1f) * 0xa2 + 0x4274])",
		"004e51dd  sub_4d4de0(arg2, &arg1[(eax & 0x1f) * 0xa2 + 0x4275], arg1[(eax & 0x1f) * 0xa2 + 0x4274])",
		"004e51fa  sub_4d5d50(arg2, var_1c_6, var_18_6)",
		"004e5205  sub_4e4fc0(ebx, &arg1[(eax & 0x1f) * 0xa2 + 0x4274], arg2)",
		"004e5240    int32_t* sub_4e5240(void* arg1, int32_t* arg2)",
		"004e5263      sub_4d4dc0(arg2, 5)",
		"004e526a      sub_4d4e30(arg2, i)",
		"004e5280      eax_4 = sub_4d4e50(arg2, ((i & 0x3f) << 0xa) + arg1 + 0x404)",
		"004e5680    int32_t sub_4e5680()",
		"004e5697  data_12e0358 += 1",
		"004e56cc  *(ebx_1 + 0x274) = 0",
		"004e5719      __builtin_memcpy(dest: ebx_1 + 0x24, src: eax_7, n: 0x250)",
		"004e5793      sub_4e5330(&var_14, ebx_1, &var_1018, 0)",
		"004e57ad      qsort(&var_1014, var_1018, 4, sub_4e52c0)",
		"004e5802      *(ebx_1 + 0x278) = data_13337b4",
		"004e58b6                  var_14 = \"svs.nextSnapshotEntities wrapped\"",
		"004e5900    void sub_4e5900(int32_t* arg1, float arg2)",
		"004e595b  sub_4e4ee0(arg2, arg1)",
		"004e5ac0    void* sub_4e5ac0(int32_t arg1 @ esi, float arg2)",
		"004e5add  sub_4e5680()",
		"004e5b20      sub_4d4e30(&var_8024, *(arg2 i+ 0x1043c))",
		"004e5b2d      sub_4e5240(arg2, &var_8024)",
		"004e5b3d      sub_4e50e0(arg2, &var_8024)",
		"004e5b52          void* __saved_edi_1 = arg2 i+ 0x10844",
		"004e5b64          sub_4d4a50(&var_8024)",
		"004e5b74      st0_1, result = sub_4e5900(&var_8024, arg2)",
		"004e5b90    void* sub_4e5b90()",
		"004e5bc1          if (*esi != 0 && data_13337a4 s>= esi[0x4271])",
		"004e5c14                  result = sub_4e4e20(esi)",
		"004e5c1c                  result = sub_4e5ac0(esi, esi)",
	):
		assert expected in hlil_part05

	emit_block = _function_block(sv_snapshot, "static void SV_EmitPacketEntities( clientSnapshot_t *from, clientSnapshot_t *to, msg_t *msg )")
	write_block = _function_block(sv_snapshot, "static void SV_WriteSnapshotToClient( client_t *client, msg_t *msg )")
	update_commands = _function_block(sv_snapshot, "void SV_UpdateServerCommandsToClient( client_t *client, msg_t *msg )")
	build_block = _function_block(sv_snapshot, "static void SV_BuildClientSnapshot( client_t *client )")
	send_message = _function_block(sv_snapshot, "void SV_SendMessageToClient( msg_t *msg, client_t *client )")
	send_snapshot = _function_block(sv_snapshot, "void SV_SendClientSnapshot( client_t *client )")
	send_messages = _function_block(sv_snapshot, "void SV_SendClientMessages( void )")

	_assert_order(
		emit_block,
		"while ( newindex < to->num_entities || oldindex < from_num_entities ) {",
		"MSG_WriteDeltaEntity (msg, oldent, newent, qfalse );",
		"MSG_WriteDeltaEntity (msg, &sv.svEntities[newnum].baseline, newent, qtrue );",
		"MSG_WriteDeltaEntity (msg, oldent, NULL, qtrue );",
		"MSG_WriteBits( msg, (MAX_GENTITIES-1), GENTITYNUM_BITS );",
	)

	assert "client->netchan.outgoingSequence - client->deltaMessage" in write_block
	assert ">= (PACKET_BACKUP - 3)" in write_block
	assert "oldframe->first_entity <= svs.nextSnapshotEntities - svs.numSnapshotEntities" in write_block
	_assert_order(
		write_block,
		"frame = &client->frames[ client->netchan.outgoingSequence & PACKET_MASK ];",
		"if ( client->deltaMessage <= 0 || client->state != CS_ACTIVE ) {",
		"MSG_WriteByte (msg, svc_snapshot);",
		"MSG_WriteLong (msg, svs.time);",
		"MSG_WriteByte (msg, lastframe);",
		"snapFlags = svs.snapFlagServerBit;",
		"MSG_WriteByte (msg, snapFlags);",
		"MSG_WriteByte (msg, frame->areabytes);",
		"MSG_WriteData (msg, frame->areabits, frame->areabytes);",
		"MSG_WriteDeltaPlayerstate( msg,",
		"SV_EmitPacketEntities (oldframe, frame, msg);",
		"if ( sv_padPackets->integer ) {",
	)

	_assert_order(
		update_commands,
		"for ( i = client->reliableAcknowledge + 1 ; i <= client->reliableSequence ; i++ ) {",
		"MSG_WriteByte( msg, svc_serverCommand );",
		"MSG_WriteLong( msg, i );",
		"MSG_WriteString( msg, client->reliableCommands[ i & (MAX_RELIABLE_COMMANDS-1) ] );",
		"client->reliableSent = client->reliableSequence;",
	)

	_assert_order(
		build_block,
		"sv.snapshotCounter++;",
		"frame = &client->frames[ client->netchan.outgoingSequence & PACKET_MASK ];",
		"entityNumbers.numSnapshotEntities = 0;",
		"frame->num_entities = 0;",
		"clent = client->gentity;",
		"ps = SV_GameClientNum( client - svs.clients );",
		"frame->ps = *ps;",
		"clientNum = frame->ps.clientNum;",
		"svEnt->snapshotCounter = sv.snapshotCounter;",
		"VectorCopy( ps->origin, org );",
		"SV_AddEntitiesVisibleFromPoint( org, frame, &entityNumbers, qfalse );",
		"qsort( entityNumbers.snapshotEntities, entityNumbers.numSnapshotEntities,",
		"frame->first_entity = svs.nextSnapshotEntities;",
		"*state = ent->s;",
		"svs.nextSnapshotEntities++;",
		"Com_Error(ERR_FATAL, \"svs.nextSnapshotEntities wrapped\");",
	)

	_assert_order(
		send_message,
		"client->frames[client->netchan.outgoingSequence & PACKET_MASK].messageSize = msg->cursize;",
		"client->frames[client->netchan.outgoingSequence & PACKET_MASK].messageSent = svs.time;",
		"client->frames[client->netchan.outgoingSequence & PACKET_MASK].messageAcked = -1;",
		"SV_Netchan_Transmit( client, msg );",
		"if ( client->netchan.remoteAddress.type == NA_LOOPBACK",
		"rateMsec = SV_RateMsec( client, msg->cursize );",
		"if ( rateMsec < client->snapshotMsec ) {",
		"client->nextSnapshotTime = svs.time + rateMsec;",
		"if ( client->state != CS_ACTIVE ) {",
	)

	_assert_order(
		send_snapshot,
		"SV_BuildClientSnapshot( client );",
		"if ( client->gentity && client->gentity->r.svFlags & SVF_BOT ) {",
		"MSG_Init (&msg, msg_buf, sizeof(msg_buf));",
		"MSG_WriteLong( &msg, client->lastClientCommand );",
		"SV_UpdateServerCommandsToClient( client, &msg );",
		"SV_WriteSnapshotToClient( client, &msg );",
		"if ( msg.overflowed ) {",
		"MSG_Clear (&msg);",
		"SV_SendMessageToClient( &msg, client );",
	)
	assert "SV_WriteDownloadToClient( client, &msg );" not in send_snapshot

	send_snapshot_hlil = hlil_part05.split("004e5ac0    void* sub_4e5ac0", 1)[1].split("004e5b8b", 1)[0]
	_assert_order(
		send_snapshot_hlil,
		"sub_4e5680()",
		"sub_4d6c10(&var_8024, &var_8008, 0x8000)",
		"sub_4d4e30(&var_8024, *(arg2 i+ 0x1043c))",
		"sub_4e5240(arg2, &var_8024)",
		"sub_4e50e0(arg2, &var_8024)",
		"if (var_8024 != 0)",
		"sub_4d4a50(&var_8024)",
		"sub_4e5900(&var_8024, arg2)",
	)

	_assert_order(
		send_messages,
		"for (i=0, c = svs.clients ; i < sv_maxclients->integer ; i++, c++) {",
		"if (!c->state) {",
		"if ( svs.time < c->nextSnapshotTime ) {",
		"if ( c->netchan.unsentFragments ) {",
		"SV_Netchan_TransmitNextFragment( c );",
		"continue;",
		"SV_SendClientSnapshot( c );",
	)

	for expected in (
		"`sub_4E4FC0 -> SV_EmitPacketEntities`",
		"`sub_4E50E0 -> SV_WriteSnapshotToClient`",
		"`sub_4E5240 -> SV_UpdateServerCommandsToClient`",
		"`sub_4E5680 -> SV_BuildClientSnapshot`",
		"`sub_4E5900 -> SV_SendMessageToClient`",
		"`sub_4E5AC0 -> SV_SendClientSnapshot`",
		"`sub_4E5B90 -> SV_SendClientMessages`",
		"preserve the retained rate",
	):
		assert expected in round_65

	assert "Preserved the existing UDP pk3 autodownload behavior" in netcode_audit
	assert "Implementation round - 2026-06-04, server snapshot authoring manifest expansion" in plan


def test_related_snapshot_wiring_pins_bot_snapshot_bridge_to_retail_aliases() -> None:
	aliases = json.loads(_read(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part05 = _read(HLIL_PART05_PATH)
	ghidra_functions = _read(GHIDRA_FUNCTIONS_PATH)
	sv_bot = _read(SV_BOT_PATH)
	sv_game = _read(SV_GAME_PATH)
	g_syscalls = _read(G_SYSCALLS_PATH)
	g_public = _read(G_PUBLIC_PATH)
	ai_main = _read(AI_MAIN_PATH)
	round_61 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_61.md")
	round_64 = _read(REPO_ROOT / "docs/reverse-engineering/quakelive_steam_mapping_round_64.md")
	botlib_audit = _read(
		REPO_ROOT / "docs/reverse-engineering/botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md"
	)

	assert aliases["sub_4DDAC0"] == "SV_BotGetSnapshotEntity"
	assert aliases["sub_4E17E0"] == "QL_G_trap_BotGetSnapshotEntity"

	for expected in (
		"FUN_004ddac0,004ddac0,91,0,unknown",
		"FUN_004e17e0,004e17e0,9,0,unknown",
	):
		assert expected in ghidra_functions

	for expected in (
		"004ddac0    int32_t sub_4ddac0(int32_t arg1, int32_t arg2)",
		"004ddae1  void* eax_3 = (*(eax_2 + 0x15b08) & 0x1f) * 0x288 + eax_2 + 0x109d0",
		"004ddaf5  if (arg2 s< 0 || arg2 s>= *(eax_3 + 0x274))",
		"004ddb1a      return 0xffffffff",
		"004ddb15  return *(mods.dp.d(sx.q(*(eax_3 + 0x278) + arg2), data_13337b0) * 0xec + data_13337b8)",
	):
		assert expected in hlil_part04

	for expected in (
		"004e17e0    int32_t sub_4e17e0()",
		"004e17e4  return sub_4ddac0() __tailcall",
	):
		assert expected in hlil_part05

	bot_snapshot = _function_block(sv_bot, "int SV_BotGetSnapshotEntity( int client, int sequence )")
	_assert_order(
		bot_snapshot,
		"cl = &svs.clients[client];",
		"frame = &cl->frames[cl->netchan.outgoingSequence & PACKET_MASK];",
		"if (sequence < 0 || sequence >= frame->num_entities) {",
		"return -1;",
		"return svs.snapshotEntities[(frame->first_entity + sequence) % svs.numSnapshotEntities].number;",
	)

	legacy_syscall = _function_block(sv_game, "static int SV_GameSystemCallsImpl( int *args, qboolean logContract )")
	native_imports = _function_block(sv_game, "static void SV_InitGameImports( void )")
	qagame_syscall_map = _function_block(g_syscalls, "static int G_MapNativeImport")
	game_ai_snapshot = _function_block(ai_main, "int BotAI_GetSnapshotEntity( int clientNum, int sequence, entityState_t *state )")

	assert "G_QL_IMPORT_BOTLIB_GET_SNAPSHOT_ENTITY = 58," in g_public
	assert "case BOTLIB_GET_SNAPSHOT_ENTITY:" in legacy_syscall
	assert "return SV_BotGetSnapshotEntity( args[1], args[2] );" in legacy_syscall
	assert "[BOTLIB_GET_SNAPSHOT_ENTITY] = (ql_import_f)QL_G_trap_BotGetSnapshotEntity" in sv_game
	assert "ql_game_imports[G_QL_IMPORT_BOTLIB_GET_SNAPSHOT_ENTITY] = (ql_import_f)QL_G_trap_BotGetSnapshotEntity;" in native_imports
	assert "case BOTLIB_GET_SNAPSHOT_ENTITY: return G_QL_IMPORT_BOTLIB_GET_SNAPSHOT_ENTITY;" in qagame_syscall_map

	_assert_order(
		game_ai_snapshot,
		"entNum = trap_BotGetSnapshotEntity( clientNum, sequence );",
		"if ( entNum == -1 ) {",
		"memset(state, 0, sizeof(entityState_t));",
		"return -1;",
		"BotAI_GetEntityState( entNum, state );",
		"return sequence + 1;",
	)

	for expected in (
		"`sub_4DDAC0 -> SV_BotGetSnapshotEntity`",
		"`sub_4E17E0 -> QL_G_trap_BotGetSnapshotEntity`",
		"`SV_BotGetSnapshotEntity`",
		"`QL_G_trap_BotGetSnapshotEntity`",
	):
		assert expected in (round_61 + round_64 + botlib_audit)


def test_networking_2_focused_parity_ledger_maps_first_plan_entry() -> None:
	ledger = _networking_2_ledger()
	msg_source = _read(MSG_C_PATH)
	qcommon_h = _read(QCOMMON_H_PATH)
	aliases = json.loads(_read(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	hlil_part04 = _read(HLIL_PART04_PATH)
	audit_note = _read(NETWORKING_2_AUDIT_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)

	assert ledger["schema_version"] == 1
	assert ledger["last_updated"] == "2026-06-05"
	assert ledger["owning_retail_binary"]["path"] == "assets/quakelive/quakelive_steam.exe"
	assert ledger["owning_retail_binary"]["function_count"] == 5473
	assert ledger["source_profile"]["protocol"] == 91
	assert ledger["source_profile"]["source_constant"] == "QL_RETAIL_PROTOCOL_VERSION"
	assert "#define\tQL_RETAIL_PROTOCOL_VERSION\t91" in qcommon_h

	focus = {area["id"]: area for area in ledger["focus_areas"]}
	assert set(focus) == {
		"protocol_gates_and_packet_headers",
		"netchan_transport",
		"xor_netchan_encoding",
		"usercmd_delta",
		"playerstate_delta_fields",
		"entity_delta_fields",
		"client_message_parser",
		"oob_connect_auth",
	}

	for symbol, address in {
		"CL_WritePacket": "sub_4B5F70",
		"SV_ExecuteClientMessage": "sub_4E05C0",
		"CL_Netchan_Encode": "sub_4BCE30",
		"CL_Netchan_Decode": "sub_4BCEF0",
		"MSG_WriteDeltaUsercmdKey": "sub_4D51A0",
		"MSG_ReadDeltaUsercmdKey": "sub_4D54A0",
		"MSG_WriteDeltaEntity": "sub_4D5780",
		"MSG_ReadDeltaEntity": "sub_4D5AC0",
		"MSG_WriteDeltaPlayerstate": "sub_4D5D50",
		"MSG_ReadDeltaPlayerstate": "sub_4D66C0",
		"Netchan_Process": "sub_4D7640",
		"SV_Netchan_Encode": "sub_4E4CD0",
		"SV_Netchan_Decode": "sub_4E4D70",
	}.items():
		assert aliases[address] == symbol

	xor_offsets = {
		item["name"]: item["value"]
		for item in focus["xor_netchan_encoding"]["packet_offsets"]
	}
	assert xor_offsets == {
		"CL_ENCODE_START": 12,
		"CL_DECODE_START": 4,
		"SV_ENCODE_START": 4,
		"SV_DECODE_START": 12,
	}
	for expected in (
		"#define\tSV_ENCODE_START\t\t4",
		"#define SV_DECODE_START\t\t12",
		"#define\tCL_ENCODE_START\t\t12",
		"#define CL_DECODE_START\t\t4",
	):
		assert expected in qcommon_h

	usercmd_offsets = {
		item["field"]: item["offset"]
		for item in focus["usercmd_delta"]["struct_offsets"]
	}
	assert usercmd_offsets["weaponPrimary"] == "0x15"
	assert usercmd_offsets["fov"] == "0x16"
	assert usercmd_offsets["forwardmove"] == "0x17"
	assert focus["usercmd_delta"]["wire_order"][-2:] == ["weaponPrimary", "fov"]

	player_table = focus["playerstate_delta_fields"]["field_table"]
	assert player_table["retail_table_base"] == "0x005424D8"
	assert player_table["retail_field_count"] == 58
	assert player_table["source_field_count"] == _netfield_count(msg_source, "playerStateFields")
	assert "005424D8" not in msg_source
	assert "{ PSF(pm_flags), 24 }" in msg_source
	assert "{ PSF(weaponPrimary), 8 }" in msg_source
	assert "{ PSF(fov), 8 }" in msg_source

	entity_table = focus["entity_delta_fields"]["field_table"]
	assert focus["entity_delta_fields"]["status"] == "completed_by_network_entitystate_fields_parity_2026_06_05"
	assert entity_table["retail_table_base"] == "0x00542220"
	assert entity_table["retail_field_count"] == 58
	assert entity_table["source_field_count"] == _netfield_count(msg_source, "entityStateFields")
	assert entity_table["retail_field_count"] - entity_table["source_field_count"] == 0
	assert entity_table["source_tail_field"] == {"field": "location", "bits": 8}
	assert "{ NETF(location), 8 }" in msg_source
	assert "{ NETF(retailEventData), 8 }" not in msg_source
	q_shared_source = _read(REPO_ROOT / "src/code/game/q_shared.h")
	assert "int\t\tretailEventPadding[4];" not in q_shared_source
	assert "int\tretailEventData;" in q_shared_source

	write_entity_hlil = hlil_part04.split("004d5780    int32_t* sub_4d5780", 1)[1].split("004d5ac0", 1)[0]
	read_entity_hlil = hlil_part04.split("004d5ac0    int32_t sub_4d5ac0", 1)[1].split("004d5d50", 1)[0]
	assert "data_124a634 += 0x3a" in write_entity_hlil
	assert "i_4 s< 0x3a" in read_entity_hlil
	assert "__builtin_memcpy(dest: arg3, src: arg2, n: 0xec)" in read_entity_hlil

	parser_offsets = focus["client_message_parser"]["packet_offsets"][0]
	assert parser_offsets["serverId"] == 0
	assert parser_offsets["messageAcknowledge"] == 4
	assert parser_offsets["reliableAcknowledge"] == 8
	assert parser_offsets["retailClientMessageSideband"] == 12
	assert parser_offsets["first_opcode"] == 13
	parser_hlil = hlil_part04.split("004e05c0    uint32_t sub_4e05c0", 1)[1].split("004e0750", 1)[0]
	_assert_order(
		parser_hlil,
		"sub_4d4a70(arg2)",
		"uint32_t eax = sub_4d5020(arg2)",
		"uint32_t i = sub_4d5020(arg2)",
		"arg1[0x4102] = sub_4d5020(arg2)",
		"sub_4d4fc0(arg2)",
		"i, edx_2 = sub_4d4fc0(arg2)",
	)

	assert ledger["completion_status"]["status"] == "completed_with_follow_up_gaps"
	assert "Retail entityStateFields count is 58" in ledger["completion_status"]["new_high_value_findings"][0]
	assert "NET2-G01" in audit_note
	assert "NET2-Q01" in audit_note
	assert "Focused networking-ledger task" in audit_note
	assert "Build a **parity ledger**" in plan
	assert "**[COMPLETED 2026-06-05]**" in plan
	assert "network-protocol-parity-ledger-2026-06-05.json" in plan
	assert "Retail `entityStateFields` uses `58` entries" in plan


def test_networking_2_header_transport_spec_freezes_protocol_gates_and_headers() -> None:
	spec = _networking_2_header_spec()
	qcommon_h = _read(QCOMMON_H_PATH)
	common_c = _read(COMMON_C_PATH)
	net_chan = _read(NET_CHAN_PATH)
	cl_main = _read(CL_MAIN_PATH)
	sv_main = _read(SV_MAIN_PATH)
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part05 = _read(HLIL_PART05_PATH)
	audit_note = _read(NETWORKING_2_HEADER_AUDIT_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["depends_on"] == "docs/reverse-engineering/network-protocol-parity-ledger-2026-06-05.json"
	assert spec["owning_retail_binary"]["path"] == "assets/quakelive/quakelive_steam.exe"

	profile = spec["active_profile"]
	assert profile["profile"] == "NETPROFILE_QL_RETAIL"
	assert profile["name"] == "ql-retail-steam"
	assert profile["connect_protocol"] == 91
	assert profile["demo_protocol"] == 91
	assert profile["uses_challenge_handshake"] is True
	assert profile["uses_client_qport"] is True
	assert profile["uses_netchan_client_qport"] is True
	assert profile["uses_reliable_xor_codec"] is True
	assert profile["uses_compressed_connect"] is True
	assert profile["uses_legacy_q3_authorize"] is False
	assert profile["requires_platform_auth"] is False
	assert "QL_BUILD_ONLINE_SERVICES" in profile["supports_platform_auth"]

	for expected in (
		"#define\tQL_RETAIL_PROTOCOL_VERSION\t91",
		"#define\tPROTOCOL_VERSION\tQL_RETAIL_PROTOCOL_VERSION",
		"#define\tMAX_MSGLEN\t\t\t\t16384",
		"#define\tSV_ENCODE_START\t\t4",
		"#define SV_DECODE_START\t\t12",
		"#define\tCL_ENCODE_START\t\t12",
		"#define CL_DECODE_START\t\t4",
	):
		assert expected in qcommon_h

	profile_block = common_c.split("static const netprofile_desc_t s_netProtocolProfile = {", 1)[1].split("\n};", 1)[0]
	_assert_order(
		profile_block,
		"NETPROFILE_QL_RETAIL,",
		"\"ql-retail-steam\",",
		"\"connect\",",
		"\"qport\",",
		"\"challenge\",",
		"QL_RETAIL_PROTOCOL_VERSION,",
		"QL_RETAIL_PROTOCOL_VERSION,",
		"qtrue,",
		"qtrue,",
		"qtrue,",
		"qtrue,",
		"qtrue,",
		"qfalse,",
		"NET_PROFILE_SUPPORTS_PLATFORM_AUTH,",
		"qfalse,",
		"NET_PROFILE_SUPPORTS_WORKSHOP_CONTENT",
	)

	for signature, field in (
		("qboolean NET_ProtocolUsesClientQport( void )", "usesClientQport"),
		("qboolean NET_ProtocolUsesNetchanClientQport( void )", "usesNetchanClientQport"),
		("qboolean NET_ProtocolUsesReliableXorCodec( void )", "usesReliableXorCodec"),
		("qboolean NET_ProtocolUsesLegacyAuthorize( void )", "usesLegacyQ3Authorize"),
		("qboolean NET_ProtocolUsesCompressedConnect( void )", "usesCompressedConnect"),
		("qboolean NET_ProtocolSupportsPlatformAuth( void )", "supportsPlatformAuth"),
	):
		assert f"return NET_GetProtocolProfile()->{field};" in _function_block(common_c, signature)

	headers = {item["id"]: item for item in spec["packet_headers"]}
	assert set(headers) == {
		"connectionless_oob",
		"compressed_connect_oob",
		"client_netchan_unfragmented",
		"server_netchan_unfragmented",
		"client_netchan_fragment",
		"server_netchan_fragment",
		"client_message_body",
		"server_message_body",
	}

	def fields(header_id: str) -> dict:
		return {field["name"]: field for field in headers[header_id]["fields"]}

	assert fields("connectionless_oob")["sentinel"]["value"] == "0xffffffff"
	assert fields("connectionless_oob")["command_or_payload"]["offset"] == 4
	assert fields("compressed_connect_oob")["sentinel"]["offset"] == 0
	assert fields("compressed_connect_oob")["clear_connect_token"]["offset"] == 4
	assert fields("compressed_connect_oob")["clear_connect_token"]["value"] == "connect"
	assert fields("compressed_connect_oob")["clear_delimiter"]["offset"] == 11
	assert fields("compressed_connect_oob")["compressed_remainder"]["offset"] == 12
	assert headers["compressed_connect_oob"]["compression"]["client_compress_offset"] == 12
	assert headers["compressed_connect_oob"]["compression"]["server_decompress_offset"] == 12
	assert headers["compressed_connect_oob"]["compression"]["detector_command_offset"] == 4

	assert fields("client_netchan_unfragmented")["sequence"]["offset"] == 0
	assert fields("client_netchan_unfragmented")["qport"]["offset"] == 4
	assert fields("client_netchan_unfragmented")["client_message_body"]["offset"] == 6
	assert fields("server_netchan_unfragmented")["sequence"]["offset"] == 0
	assert fields("server_netchan_unfragmented")["server_message_body"]["offset"] == 4
	assert fields("client_netchan_fragment")["sequence_with_fragment_bit"]["offset"] == 0
	assert fields("client_netchan_fragment")["qport"]["offset"] == 4
	assert fields("client_netchan_fragment")["fragment_start"]["offset"] == 6
	assert fields("client_netchan_fragment")["fragment_length"]["offset"] == 8
	assert fields("client_netchan_fragment")["fragment_payload"]["offset"] == 10
	assert fields("server_netchan_fragment")["fragment_start"]["offset"] == 4
	assert fields("server_netchan_fragment")["fragment_length"]["offset"] == 6
	assert fields("server_netchan_fragment")["fragment_payload"]["offset"] == 8

	client_body = fields("client_message_body")
	assert client_body["serverId"]["offset"] == 0
	assert client_body["messageAcknowledge"]["offset"] == 4
	assert client_body["reliableAcknowledge"]["offset"] == 8
	assert client_body["retailClientMessageSideband"]["offset"] == 12
	assert client_body["first_opcode"]["offset"] == 13
	assert fields("server_message_body")["reliableAcknowledge"]["offset"] == 0
	assert fields("server_message_body")["first_opcode"]["offset"] == 4

	constants = spec["netchan_constants"]
	assert constants["source_MAX_MSGLEN"] == 16384
	assert constants["retail_transmit_rejects_above"] == 32768
	assert constants["FRAGMENT_SIZE"] == 1300
	assert constants["FRAGMENT_SIZE_SOURCE"] == "MAX_PACKETLEN - 100"
	assert constants["fragment_bit_hex"] == "0x80000000"

	assert spec["qport_rules"]["connect_userinfo_key"] == "qport"
	assert spec["qport_rules"]["connect_userinfo_included_when"] == "NET_ProtocolUsesClientQport()"
	assert "SV_PacketEvent reads sequence then qport" in spec["qport_rules"]["server_packet_lookup"]

	xor = spec["xor_windows"]
	assert xor["client_to_server"]["encode_start"] == 12
	assert xor["client_to_server"]["decode_start"] == 12
	assert xor["server_to_client"]["encode_start"] == 4
	assert xor["server_to_client"]["decode_start"] == 4
	assert xor["source_constants"] == {
		"SV_ENCODE_START": 4,
		"SV_DECODE_START": 12,
		"CL_ENCODE_START": 12,
		"CL_DECODE_START": 4,
	}

	connect_packet = common_c.split("qboolean NET_IsConnectRequestPacket( const msg_t *msg )", 1)[1].split(
		"NET_ProtocolUsesClientQport", 1
	)[0]
	_assert_order(
		connect_packet,
		"if ( !msg || !msg->data || msg->cursize < 4 ) {",
		"command = NET_GetConnectRequestCommand();",
		"commandLength = strlen( command );",
		"payload = (const char *)msg->data + 4;",
		"if ( Q_strncmp( payload, command, commandLength ) ) {",
		"delimiter = payload[commandLength];",
		"delimiter == '\\0' || delimiter == ' ' || delimiter == '\"' || delimiter == '\\n' || delimiter == '\\r'",
	)

	check_resend = cl_main.split("void CL_CheckForResend( void ) {", 1)[1].split("CL_DisconnectPacket", 1)[0]
	_assert_order(
		check_resend,
		"if ( NET_ProtocolUsesLegacyAuthorize() && !Sys_IsLANAddress( clc.serverAddress ) ) {",
		"CL_SendChallengeRequest();",
		"port = Cvar_VariableValue (\"net_qport\");",
		'Info_SetValueForKey( info, NET_GetProtocolInfoKey(), va("%i", NET_ProtocolVersion() ) );',
		"if ( NET_ProtocolUsesClientQport() ) {",
		'Info_SetValueForKey( info, NET_GetQportInfoKey(), va("%i", port ) );',
		'Info_SetValueForKey( info, NET_GetChallengeInfoKey(), va("%i", clc.challenge ) );',
		'Com_sprintf( data, sizeof( data ), "%s \\"%s\\"", NET_GetConnectRequestCommand(), info );',
		"if ( NET_ProtocolUsesCompressedConnect() ) {",
		"NET_OutOfBandData( NS_CLIENT, clc.serverAddress, (byte *)data, dataLength );",
		"NET_OutOfBandPrint( NS_CLIENT, clc.serverAddress, \"%s\", data );",
	)

	connectionless = _function_block(sv_main, "void SV_ConnectionlessPacket( netadr_t from, msg_t *msg )")
	_assert_order(
		connectionless,
		"MSG_BeginReadingOOB( msg );",
		"MSG_ReadLong( msg );",
		"if ( NET_ProtocolUsesCompressedConnect() && NET_IsConnectRequestPacket( msg ) ) {",
		"Huff_Decompress(msg, 12);",
		"s = MSG_ReadStringLine( msg );",
		"Cmd_TokenizeString( s );",
	)

	packet_event = _function_block(sv_main, "void SV_PacketEvent( netadr_t from, msg_t *msg )")
	_assert_order(
		packet_event,
		"if ( msg->cursize >= 4 && *(int *)msg->data == -1) {",
		"SV_ConnectionlessPacket( from, msg );",
		"MSG_BeginReadingOOB( msg );",
		"MSG_ReadLong( msg );",
		"qport = MSG_ReadShort( msg ) & 0xffff;",
		"if (cl->netchan.qport != qport) {",
		"if (SV_Netchan_Process(cl, msg)) {",
		"SV_ExecuteClientMessage( cl, msg );",
	)

	oob_print = _function_block(net_chan, "void QDECL NET_OutOfBandPrint( netsrc_t sock, netadr_t adr, const char *format, ... )")
	_assert_order(
		oob_print,
		"string[0] = -1;",
		"string[1] = -1;",
		"string[2] = -1;",
		"string[3] = -1;",
		"vsprintf( string+4, format, argptr );",
		"NET_SendPacket( sock, strlen( string ), string, adr );",
	)

	oob_data = _function_block(net_chan, "void QDECL NET_OutOfBandData( netsrc_t sock, netadr_t adr, byte *format, int len )")
	_assert_order(
		oob_data,
		"string[0] = 0xff;",
		"string[1] = 0xff;",
		"string[2] = 0xff;",
		"string[3] = 0xff;",
		"string[i+4] = format[i];",
		"mbuf.cursize = len+4;",
		"Huff_Compress( &mbuf, 12);",
		"NET_SendPacket( sock, mbuf.cursize, mbuf.data, adr );",
	)

	next_fragment = _function_block(net_chan, "void Netchan_TransmitNextFragment( netchan_t *chan )")
	_assert_order(
		next_fragment,
		"MSG_InitOOB (&send, send_buf, sizeof(send_buf));",
		"MSG_WriteLong( &send, chan->outgoingSequence | FRAGMENT_BIT );",
		"if ( chan->sock == NS_CLIENT && NET_ProtocolUsesNetchanClientQport() ) {",
		"MSG_WriteShort( &send, qport->integer );",
		"fragmentLength = FRAGMENT_SIZE;",
		"MSG_WriteShort( &send, chan->unsentFragmentStart );",
		"MSG_WriteShort( &send, fragmentLength );",
		"MSG_WriteData( &send, chan->unsentBuffer + chan->unsentFragmentStart, fragmentLength );",
	)

	transmit = _function_block(net_chan, "void Netchan_Transmit( netchan_t *chan, int length, const byte *data )")
	_assert_order(
		transmit,
		"if ( length > MAX_MSGLEN ) {",
		"if ( length >= FRAGMENT_SIZE ) {",
		"Netchan_TransmitNextFragment( chan );",
		"MSG_InitOOB (&send, send_buf, sizeof(send_buf));",
		"MSG_WriteLong( &send, chan->outgoingSequence );",
		"chan->outgoingSequence++;",
		"if ( chan->sock == NS_CLIENT && NET_ProtocolUsesNetchanClientQport() ) {",
		"MSG_WriteShort( &send, qport->integer );",
		"MSG_WriteData( &send, data, length );",
	)

	process = _function_block(net_chan, "qboolean Netchan_Process( netchan_t *chan, msg_t *msg )")
	_assert_order(
		process,
		"MSG_BeginReadingOOB( msg );",
		"sequence = MSG_ReadLong( msg );",
		"if ( sequence & FRAGMENT_BIT ) {",
		"sequence &= ~FRAGMENT_BIT;",
		"if ( chan->sock == NS_SERVER && NET_ProtocolUsesNetchanClientQport() ) {",
		"(void)MSG_ReadShort( msg );",
		"if ( fragmented ) {",
		"fragmentStart = MSG_ReadShort( msg );",
		"fragmentLength = MSG_ReadShort( msg );",
	)

	oob_data_hlil = hlil_part04.split("004d7120    int32_t sub_4d7120", 1)[1].split("004d7248", 1)[0]
	_assert_order(
		oob_data_hlil,
		"int32_t var_10008 = 0xffffffff",
		"if (arg8 s> 0)",
		"memcpy(&var_10004, arg7, arg8)",
		"int32_t eax_3 = sub_4d40f0(&var_10024, 0xc)",
		"eax_3 = sub_4ee460(arg8 + 4, var_1001c, arg2)",
	)

	netchan_hlil = hlil_part04.split("004d7370    int32_t sub_4d7370", 1)[1].split("004d7640", 1)[0]
	_assert_order(
		netchan_hlil,
		"sub_4d6c50(&var_59c, &var_580, 0x578)",
		"sub_4d4e30(&var_59c, arg1[9] | 0x80000000)",
		"if (*arg1 == 0)",
		"sub_4d4e10(&var_59c, *(data_142c344 + 0x30))",
		"int32_t edi = 0x514",
		"sub_4d4e10(&var_59c, ecx_2)",
		"sub_4d4e10(&var_59c, edi)",
		"if (arg2 s> 0x8000)",
		"if (arg2 s>= 0x514)",
		"sub_4d4e30(&var_59c, arg1[9])",
		"if (*arg1 == 0)",
		"sub_4d4e10(&var_59c, *(data_142c344 + 0x30))",
	)

	process_hlil = hlil_part04.split("004d7640    int32_t sub_4d7640", 1)[1].split("004d794f", 1)[0]
	_assert_order(
		process_hlil,
		"sub_4d4a80(arg5)",
		"uint32_t ebx_1 = sub_4d5020(arg5)",
		"ebx_1 &= 0x7fffffff",
		"if (*esi == 1)",
		"sub_4d4ff0(arg5)",
		"var_c = sub_4d4ff0(arg5)",
		"eax_2 = sub_4d4ff0(arg5)",
	)

	packet_hlil = hlil_part05.split("004e4500    int32_t sub_4e4500", 1)[1].split("004e46a3", 1)[0]
	_assert_order(
		packet_hlil,
		"if (*(arg6 + 0x10) s>= 4 && **(arg6 + 8) == 0xffffffff)",
		"return sub_4e4340",
		"sub_4d4a80(arg6)",
		"sub_4d5020(arg6)",
		"int16_t eax_1 = sub_4d4ff0(arg6)",
		"esi_2[0x56c0] == zx.d(eax_1)",
		"result = sub_4e4f80(esi_2, arg6)",
		"return sub_4e05c0(esi_2, arg6)",
	)

	anchors = {item["symbol"]: item for item in spec["retail_anchors"]}
	assert anchors["CL_CheckForResend"]["address"] == "0x004B9150"
	assert anchors["NET_OutOfBandData"]["address"] == "0x004D7120"
	assert anchors["Netchan_Transmit"]["address"] == "0x004D74E0"
	assert anchors["SV_PacketEvent"]["address"] == "0x004E4500"

	assert spec["completion_status"]["status"] == "completed_static_spec_and_assertions"
	assert spec["completion_status"]["focused_task_parity_before_percent"] == 70
	assert spec["completion_status"]["focused_task_parity_after_percent"] == 90
	assert spec["completion_status"]["overall_network_protocol_parity_before_percent"] == 72
	assert spec["completion_status"]["overall_network_protocol_parity_after_percent"] == 74
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_header_transport_spec_freezes_protocol_gates_and_headers" in spec["assertion_tests"]

	assert "Network Protocol Header And Transport Spec" in audit_note
	assert "Offset `12`: compressed remainder." in audit_note
	assert "Offset `12`: retail client-message sideband byte." in audit_note
	assert "Source `MAX_MSGLEN` is `16384`; committed retail HLIL shows" in audit_note
	assert "Focused protocol-gate/header slice: `70%` before, `90%` after." in audit_note
	assert "Freeze **protocol gates and packet headers**" in plan
	assert "network-protocol-header-transport-spec-2026-06-05.json" in plan
	assert "completed_static_spec_and_assertions" in plan


def test_networking_2_oob_connect_auth_matrix_and_negative_compression_contract() -> None:
	spec = _networking_2_oob_connect_auth_spec()
	ledger = _networking_2_ledger()
	msg_c = _read(MSG_C_PATH)
	huffman_c = _read(HUFFMAN_C_PATH)
	common_c = _read(COMMON_C_PATH)
	net_chan = _read(NET_CHAN_PATH)
	cl_main = _read(CL_MAIN_PATH)
	sv_main = _read(SV_MAIN_PATH)
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part05 = _read(HLIL_PART05_PATH)
	audit_note = _read(NETWORKING_2_OOB_CONNECT_AUTH_AUDIT_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-protocol-parity-ledger-2026-06-05.json",
		"docs/reverse-engineering/network-protocol-header-transport-spec-2026-06-05.json",
	]
	assert spec["owning_retail_binary"]["path"] == "assets/quakelive/quakelive_steam.exe"

	profile = spec["active_profile"]
	assert profile["profile"] == "NETPROFILE_QL_RETAIL"
	assert profile["connect_protocol"] == 91
	assert profile["uses_compressed_connect"] is True
	assert profile["uses_legacy_q3_authorize"] is False
	assert profile["requires_platform_auth"] is False
	assert "QL_BUILD_ONLINE_SERVICES" in profile["supports_platform_auth"]

	matrix = {item["id"]: item for item in spec["compatibility_matrix"]}
	assert set(matrix) == {
		"generic_oob_text_commands",
		"steam_auth_getchallenge_binary",
		"compressed_connect_request",
		"legacy_q3_authorize",
	}
	assert matrix["generic_oob_text_commands"]["compression"] == "none"
	assert "getinfo" in matrix["generic_oob_text_commands"]["commands"]
	assert "statusResponse" in matrix["generic_oob_text_commands"]["commands"]
	assert matrix["steam_auth_getchallenge_binary"]["sender_helpers"] == [
		"CL_BuildSteamChallengeRequest",
		"NET_OutOfBandRaw",
	]
	assert matrix["steam_auth_getchallenge_binary"]["compression"] == "none"
	connect = matrix["compressed_connect_request"]
	assert connect["clear_window"] == {
		"sentinel_offset": 0,
		"command_offset": 4,
		"clear_token": "connect",
		"clear_delimiter_offset": 11,
		"compressed_remainder_offset": 12,
	}
	assert connect["compression"]["client_offset"] == 12
	assert connect["compression"]["server_offset"] == 12
	assert connect["compression"]["server_guard"] == "NET_ProtocolUsesCompressedConnect() && NET_IsConnectRequestPacket(msg)"
	assert matrix["legacy_q3_authorize"]["profile_state"] == "uses_legacy_q3_authorize is false for NETPROFILE_QL_RETAIL"

	assert spec["oob_scalar_primitives"]["huffman_used"] is False
	vectors = {vector["id"]: vector for vector in spec["golden_vectors"]}
	assert vectors["oob_primitive_little_endian"]["read_sequence"] == [
		{"bits": 8, "value_hex": "0x12"},
		{"bits": 16, "value_hex": "0x3456"},
		{"bits": 32, "value_hex": "0x89abcdef"},
	]
	assert vectors["raw_getinfo_text"]["huffman_expected"] is False
	assert vectors["steam_getchallenge_raw_prefix"]["clear_bytes_after_sentinel"] == "getchallenge "
	assert vectors["compressed_connect_clear_window"]["compressed_remainder_offset"] == 12
	assert vectors["compressed_connect_clear_window"]["huffman_expected"] is True

	init_oob = _function_block(msg_c, "void MSG_InitOOB( msg_t *buf, byte *data, int length )")
	begin_oob = _function_block(msg_c, "void MSG_BeginReadingOOB( msg_t *msg )")
	bitstream = _function_block(msg_c, "void MSG_Bitstream( msg_t *buf )")
	assert "buf->oob = qtrue;" in init_oob
	assert "msg->oob = qtrue;" in begin_oob
	assert "buf->oob = qfalse;" in bitstream

	write_bits = _function_block(msg_c, "void MSG_WriteBits( msg_t *msg, int value, int bits )")
	write_oob = write_bits.split("if (msg->oob) {", 1)[1].split("\n\t} else {", 1)[0]
	write_bitstream = write_bits.split("\n\t} else {", 1)[1]
	for expected in (
		"msg->data[msg->cursize] = value;",
		"*sp = LittleShort(value);",
		"*ip = LittleLong(value);",
	):
		assert expected in write_oob
	assert "Huff_" not in write_oob
	assert "Huff_putBit" in write_bitstream
	assert "Huff_offsetTransmit" in write_bitstream

	read_bits = _function_block(msg_c, "int MSG_ReadBits( msg_t *msg, int bits )")
	read_oob = read_bits.split("if (msg->oob) {", 1)[1].split("\n\t} else {", 1)[0]
	read_bitstream = read_bits.split("\n\t} else {", 1)[1]
	for expected in (
		"value = msg->data[msg->readcount];",
		"value = LittleShort(*sp);",
		"value = LittleLong(*ip);",
	):
		assert expected in read_oob
	assert "Huff_" not in read_oob
	assert "Huff_getBit" in read_bitstream
	assert "Huff_offsetReceive" in read_bitstream

	huff_compress = _function_block(huffman_c, "void Huff_Compress(msg_t *mbuf, int offset)")
	huff_decompress = _function_block(huffman_c, "void Huff_Decompress(msg_t *mbuf, int offset)")
	assert "size = mbuf->cursize - offset;" in huff_compress
	assert "mbuf->cursize = (bloc>>3) + offset;" in huff_compress
	assert "size = mbuf->cursize - offset;" in huff_decompress
	assert "mbuf->cursize = cch + offset;" in huff_decompress

	profile_block = common_c.split("static const netprofile_desc_t s_netProtocolProfile = {", 1)[1].split("\n};", 1)[0]
	_assert_order(
		profile_block,
		"NETPROFILE_QL_RETAIL,",
		"\"getchallenge\",",
		"\"connect\",",
		"\"getKeyAuthorize\",",
		"\"ipAuthorize\",",
		"qtrue,",
		"qfalse,",
		"NET_PROFILE_SUPPORTS_PLATFORM_AUTH,",
	)
	assert "return NET_GetProtocolProfile()->usesCompressedConnect;" in _function_block(
		common_c, "qboolean NET_ProtocolUsesCompressedConnect( void )"
	)
	assert "return NET_GetProtocolProfile()->usesLegacyQ3Authorize;" in _function_block(
		common_c, "qboolean NET_ProtocolUsesLegacyAuthorize( void )"
	)

	connect_detector = common_c.split("qboolean NET_IsConnectRequestPacket( const msg_t *msg )", 1)[1].split(
		"NET_ProtocolUsesClientQport", 1
	)[0]
	_assert_order(
		connect_detector,
		"payload = (const char *)msg->data + 4;",
		"if ( Q_strncmp( payload, command, commandLength ) ) {",
		"delimiter = payload[commandLength];",
		"delimiter == '\\0' || delimiter == ' ' || delimiter == '\"' || delimiter == '\\n' || delimiter == '\\r'",
	)

	oob_print = _function_block(net_chan, "void QDECL NET_OutOfBandPrint( netsrc_t sock, netadr_t adr, const char *format, ... )")
	oob_raw = _function_block(net_chan, "void NET_OutOfBandRaw( netsrc_t sock, netadr_t adr, const byte *data, int len )")
	oob_data = _function_block(net_chan, "void QDECL NET_OutOfBandData( netsrc_t sock, netadr_t adr, byte *format, int len )")
	for raw_block in (oob_print, oob_raw):
		assert "Huff_Compress" not in raw_block
		assert "NET_SendPacket" in raw_block
	_assert_order(
		oob_print,
		"string[0] = -1;",
		"vsprintf( string+4, format, argptr );",
		"NET_SendPacket( sock, strlen( string ), string, adr );",
	)
	_assert_order(
		oob_raw,
		"string[0] = 0xff;",
		"Com_Memcpy( string + 4, data, len );",
		"NET_SendPacket( sock, len + 4, string, adr );",
	)
	_assert_order(
		oob_data,
		"string[0] = 0xff;",
		"string[i+4] = format[i];",
		"mbuf.cursize = len+4;",
		"Huff_Compress( &mbuf, 12);",
		"NET_SendPacket( sock, mbuf.cursize, mbuf.data, adr );",
	)

	build_challenge = _function_block(cl_main, "static qboolean CL_BuildSteamChallengeRequest( byte *data, int dataSize, int *dataLength )")
	send_challenge = _function_block(cl_main, "static void CL_SendChallengeRequest( void )")
	check_resend = _function_block(cl_main, "void CL_CheckForResend( void ) {")
	_assert_order(
		build_challenge,
		"if ( !NET_ProtocolSupportsPlatformAuth() ) {",
		"command = NET_GetChallengeRequestCommand();",
		"data[commandLength] = ' ';",
		"CL_WriteSteamChallengeWord( data + commandLength + 1, steamIdLow );",
		"CL_WriteSteamChallengeWord( data + commandLength + 5, steamIdHigh );",
		"Com_Memcpy( data + commandLength + 9, ticket, ticketLength );",
	)
	_assert_order(
		send_challenge,
		"if ( CL_BuildSteamChallengeRequest( data, sizeof( data ), &dataLength ) ) {",
		"NET_OutOfBandRaw( NS_CLIENT, clc.serverAddress, data, dataLength );",
		"NET_OutOfBandPrint( NS_CLIENT, clc.serverAddress, \"%s\", NET_GetChallengeRequestCommand() );",
	)
	assert "NET_OutOfBandData" not in send_challenge
	_assert_order(
		check_resend,
		"CL_SendChallengeRequest();",
		"Com_sprintf( data, sizeof( data ), \"%s \\\"%s\\\"\", NET_GetConnectRequestCommand(), info );",
		"if ( NET_ProtocolUsesCompressedConnect() ) {",
		"NET_OutOfBandData( NS_CLIENT, clc.serverAddress, (byte *)data, dataLength );",
		"NET_OutOfBandPrint( NS_CLIENT, clc.serverAddress, \"%s\", data );",
	)

	connectionless = _function_block(sv_main, "void SV_ConnectionlessPacket( netadr_t from, msg_t *msg )")
	_assert_order(
		connectionless,
		"MSG_BeginReadingOOB( msg );",
		"MSG_ReadLong( msg );",
		"if ( NET_ProtocolUsesCompressedConnect() && NET_IsConnectRequestPacket( msg ) ) {",
		"Huff_Decompress(msg, 12);",
		"s = MSG_ReadStringLine( msg );",
		"if ( NET_IsGetStatusRequest( c ) ) {",
		"} else if ( NET_IsGetChallengeRequest( c ) ) {",
		"} else if ( NET_IsConnectRequest( c ) ) {",
	)

	write_bits_hlil = hlil_part04.split("004d4af0    int32_t* sub_4d4af0", 1)[1].split("004d4c70", 1)[0]
	read_bits_hlil = hlil_part04.split("004d4c70    uint32_t sub_4d4c70", 1)[1].split("004d4dc0", 1)[0]
	_assert_order(
		write_bits_hlil,
		"if (arg1[1] != 0)",
		"*(arg1[2] + eax_4) = arg2.w",
		"*(arg1[2] + arg1[4]) = arg2",
		"arg1[2][arg1[4]] = arg2.b",
		"sub_4d3790(ebx_1.b & 1, arg1[2], &arg1[6])",
		"sub_4d3e20(&data_123c5f8, zx.d(ebx_1.b), arg1[2], &arg1[6])",
	)
	_assert_order(
		read_bits_hlil,
		"if (*(esi + 4) == 0)",
		"sub_4d37d0(*(esi + 8), esi + 0x18)",
		"sub_4d3b80(data_124361c, &arg1, *(esi + 8), esi + 0x18)",
		"else if (__saved_ebx_1 == 8)",
		"uint32_t result_1 = zx.d(*(*(esi + 8) + ecx))",
		"else if (__saved_ebx_1 != 0x10)",
		"uint32_t result_3 = *(ecx_3 + *(esi + 8))",
	)
	oob_data_hlil = hlil_part04.split("004d7120    int32_t sub_4d7120", 1)[1].split("004d7248", 1)[0]
	_assert_order(
		oob_data_hlil,
		"int32_t var_10008 = 0xffffffff",
		"memcpy(&var_10004, arg7, arg8)",
		"int32_t eax_3 = sub_4d40f0(&var_10024, 0xc)",
		"eax_3 = sub_4ee460(arg8 + 4, var_1001c, arg2)",
	)
	check_resend_hlil = hlil_part04.split("004b9150    int32_t sub_4b9150", 1)[1].split("004b942f", 1)[0]
	assert '__builtin_strncpy(dest: &var_408, src: "connect ", n: 9)' in check_resend_hlil
	assert "sub_4d7120(0, edx_3" in check_resend_hlil
	assert '__builtin_strncpy(dest: &var_9804, src: "getchallenge ", n: 0xd)' in check_resend_hlil
	assert "eax_1 = sub_4d6fd0(0, eax_13 + 0x19, &var_9808" in check_resend_hlil
	connectionless_hlil = hlil_part05.split("004e4340    int32_t sub_4e4340", 1)[1].split("004e4500", 1)[0]
	_assert_order(
		connectionless_hlil,
		"sub_4d4a80(arg9)",
		"sub_4d5020(arg9)",
		"if (sub_4d9020(\"connect\", *(arg9 + 8) + 4, 7) == 0)",
		"sub_4d3e60(arg9, 0xc)",
		"sub_4d5100(arg9)",
		"if (sub_4d9060(eax_5, \"getchallenge\") == 0)",
		"if (sub_4d9060(eax_5, \"connect\") == 0)",
	)

	anchors = {item["symbol"]: item for item in spec["retail_anchors"]}
	assert anchors["MSG_WriteBits"]["address"] == "0x004D4AF0"
	assert anchors["MSG_ReadBits"]["address"] == "0x004D4C70"
	assert anchors["Huff_Compress"]["address"] == "0x004D40F0"
	assert anchors["Huff_Decompress"]["address"] == "0x004D3E60"
	assert anchors["NET_OutOfBandData"]["address"] == "0x004D7120"
	assert anchors["SV_ConnectionlessPacket"]["address"] == "0x004E4340"

	focus = {area["id"]: area for area in ledger["focus_areas"]}
	assert focus["oob_connect_auth"]["status"] == "completed_by_network_oob_connect_auth_parity_2026_06_05"
	assert "Compressed connect is the only confirmed profile-91 OOB Huffman exception" in focus["oob_connect_auth"]["observed_facts"][1]
	assert "Capture-diff compressed connect" in focus["oob_connect_auth"]["open_questions"][0]

	assert spec["completion_status"]["status"] == "completed_static_matrix_and_negative_assertions"
	assert spec["completion_status"]["source_patch_required"] is False
	assert spec["completion_status"]["focused_task_parity_before_percent"] == 62
	assert spec["completion_status"]["focused_task_parity_after_percent"] == 90
	assert spec["completion_status"]["overall_network_protocol_parity_before_percent"] == 84
	assert spec["completion_status"]["overall_network_protocol_parity_after_percent"] == 85
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_oob_connect_auth_matrix_and_negative_compression_contract" in spec["assertion_tests"]

	assert "Network OOB Connect/Auth Parity" in audit_note
	assert "profile-91 Huffman exception" in audit_note
	assert "Steam auth `getchallenge` payload" in audit_note
	assert "Focused OOB/connect/auth slice: `62%` before, `90%` after" in audit_note
	assert "Audit **OOB/connect/auth** behavior" in plan
	assert "network-oob-connect-auth-parity-2026-06-05.json" in plan
	assert "focused OOB/connect/auth slice" in plan


def test_networking_2_capture_scoped_adaptive_huffman_fixtures() -> None:
	spec = _networking_2_huffman_fixtures_spec()
	header_spec = _networking_2_header_spec()
	oob_spec = _networking_2_oob_connect_auth_spec()
	replay_spec = _networking_2_replay_validation_spec()
	usercmd_spec = _networking_2_usercmd_delta_spec()
	huffman_c = _read(HUFFMAN_C_PATH)
	msg_c = _read(MSG_C_PATH)
	net_chan = _read(NET_CHAN_PATH)
	cl_main = _read(CL_MAIN_PATH)
	sv_main = _read(SV_MAIN_PATH)
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part05 = _read(HLIL_PART05_PATH)
	audit_note = _read(NETWORKING_2_HUFFMAN_FIXTURES_AUDIT_PATH)
	oob_note = _read(NETWORKING_2_OOB_CONNECT_AUTH_AUDIT_PATH)
	replay_note = _read(NETWORKING_2_REPLAY_VALIDATION_AUDIT_PATH)
	usercmd_note = _read(NETWORKING_2_USERCMD_DELTA_AUDIT_PATH)
	checklist = _read(OUTSTANDING_WORK_CHECKLIST_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-protocol-header-transport-spec-2026-06-05.json",
		"docs/reverse-engineering/network-oob-connect-auth-parity-2026-06-05.json",
		"docs/reverse-engineering/network-demo-capture-replay-validation-2026-06-05.json",
		"docs/reverse-engineering/network-usercmd-delta-parity-2026-06-05.json",
	]
	assert spec["owning_retail_binary"]["path"] == "assets/quakelive/quakelive_steam.exe"
	assert spec["source_files"] == [
		"src/code/qcommon/huffman.c",
		"src/code/qcommon/msg.c",
		"src/code/qcommon/net_chan.c",
		"src/code/client/cl_main.c",
		"src/code/server/sv_main.c",
	]

	scopes = {scope["id"]: scope for scope in spec["huffman_scopes"]}
	assert set(scopes) == {"huffcompress_local_reset", "msghuff_seeded_bitstream"}
	assert scopes["huffcompress_local_reset"]["owner"] == "Huff_Compress"
	assert scopes["huffcompress_local_reset"]["retail_anchor"] == "0x004D40F0"
	assert scopes["huffcompress_local_reset"]["state_model"] == "local NYT tree per call"
	assert "Huff_transmit then Huff_addRef" in scopes["huffcompress_local_reset"]["update_policy"]
	assert scopes["msghuff_seeded_bitstream"]["owner"] == "MSG_WriteBits"
	assert scopes["msghuff_seeded_bitstream"]["retail_anchor"] == "0x004D4AF0"
	assert "msg_hData" in scopes["msghuff_seeded_bitstream"]["state_model"]
	assert "do not add per-symbol references after MSG_initHuffman" in scopes["msghuff_seeded_bitstream"]["update_policy"]

	fixtures = {fixture["id"]: fixture for fixture in spec["fixtures"]}
	assert set(fixtures) == {
		"compressed_connect_profile91_numeric_challenge",
		"huffcompress_local_reset_abc",
		"msghuff_seeded_three_ascii_bytes",
		"msghuff_seeded_client_sideband_move_body",
	}

	connect = fixtures["compressed_connect_profile91_numeric_challenge"]
	clear_prefix = bytes.fromhex(connect["clear_prefix_hex"])
	encoded_remainder = bytes.fromhex(connect["encoded_remainder_hex"])
	encoded_datagram = bytes.fromhex(connect["encoded_datagram_hex"])
	uncompressed_remainder = bytes.fromhex(connect["uncompressed_remainder_hex"])
	assert connect["scope"] == "huffcompress_local_reset"
	assert connect["clear_datagram_ascii_after_sentinel"] == 'connect "\\protocol\\91\\qport\\1234\\challenge\\1234"'
	assert clear_prefix == b"\xff\xff\xff\xffconnect "
	assert connect["compressed_remainder_offset"] == 12
	assert len(uncompressed_remainder) == connect["uncompressed_remainder_size"] == 40
	assert encoded_remainder[:2] == connect["uncompressed_remainder_size"].to_bytes(2, "big")
	assert len(encoded_remainder) == connect["encoded_remainder_size"] == 42
	assert len(encoded_datagram) == connect["encoded_datagram_size"] == 54
	assert encoded_datagram[:12] == clear_prefix
	assert encoded_datagram[12:] == encoded_remainder
	assert connect["encoded_bit_count"] == 317
	assert connect["encoded_bit_count_mod8"] == connect["encoded_bit_count"] % 8 == 5
	assert connect["encoded_remainder_size"] == ((16 + connect["encoded_bit_count"] + 8) >> 3)
	assert connect["unstable_terminal_pad_bytes"] == 0

	local_abc = fixtures["huffcompress_local_reset_abc"]
	assert local_abc["encoded_remainder_hex"] == "00 03 86 8c 30 06"
	assert len(bytes.fromhex(local_abc["encoded_remainder_hex"])) == local_abc["encoded_remainder_size"]
	assert local_abc["encoded_remainder_size"] == ((16 + local_abc["encoded_bit_count"] + 8) >> 3)
	assert local_abc["encoded_bit_count_mod8"] == local_abc["encoded_bit_count"] % 8 == 3

	seeded_ascii = fixtures["msghuff_seeded_three_ascii_bytes"]
	assert seeded_ascii["input_hex"] == "61 62 63"
	assert seeded_ascii["encoded_hex"] == "3c ab 1f 03"
	assert len(bytes.fromhex(seeded_ascii["encoded_hex"])) == seeded_ascii["encoded_size"]
	assert seeded_ascii["encoded_size"] == (seeded_ascii["encoded_bit_count"] >> 3) + 1
	assert seeded_ascii["encoded_bit_count_mod8"] == seeded_ascii["encoded_bit_count"] % 8 == 2

	seeded_body = fixtures["msghuff_seeded_client_sideband_move_body"]
	assert seeded_body["input_hex"] == "04 03 02 01 0d 0c 0b 0a 02 00 00 00 80 02 01 05"
	assert seeded_body["encoded_hex"] == "a1 6c e4 6e 27 8b 34 52 fd 90 3b 02"
	assert len(bytes.fromhex(seeded_body["encoded_hex"])) == seeded_body["encoded_size"]
	assert seeded_body["encoded_size"] == (seeded_body["encoded_bit_count"] >> 3) + 1
	assert seeded_body["encoded_bit_count_mod8"] == seeded_body["encoded_bit_count"] % 8 == 5
	assert all(fixture["unstable_terminal_pad_bytes"] == 0 for fixture in fixtures.values())

	header_packets = {packet["id"]: packet for packet in header_spec["packet_headers"]}
	compressed_header_fields = {
		field["name"]: field
		for field in header_packets["compressed_connect_oob"]["fields"]
	}
	assert compressed_header_fields["compressed_remainder"]["offset"] == 12
	oob_connect = {item["id"]: item for item in oob_spec["compatibility_matrix"]}["compressed_connect_request"]
	assert oob_connect["compression"]["client_offset"] == connect["compressed_remainder_offset"]
	assert oob_connect["compression"]["server_offset"] == connect["compressed_remainder_offset"]
	assert "network-adaptive-huffman-fixtures-2026-06-05.json" in replay_spec["completion_status"]["remaining_gaps"][1]
	assert "network-adaptive-huffman-fixtures-2026-06-05.json" in usercmd_spec["completion_status"]["residual_risks"][0]

	huff_compress = _function_block(huffman_c, "void Huff_Compress(msg_t *mbuf, int offset)")
	_assert_order(
		huff_compress,
		"Com_Memset(&huff, 0, sizeof(huff_t));",
		"huff.tree = huff.lhead = huff.loc[NYT] =  &(huff.nodeList[huff.blocNode++]);",
		"seq[0] = (size>>8);",
		"seq[1] = size&0xff;",
		"bloc = 16;",
		"Huff_transmit(&huff, ch, seq);",
		"Huff_addRef(&huff, (byte)ch);",
		"bloc += 8;",
		"mbuf->cursize = (bloc>>3) + offset;",
	)
	write_bits = _function_block(msg_c, "void MSG_WriteBits( msg_t *msg, int value, int bits )")
	assert "Huff_offsetTransmit (&msgHuff.compressor, (value&0xff), msg->data, &msg->bit);" in write_bits
	assert "Huff_addRef" not in write_bits
	msg_init = _function_block(msg_c, "void MSG_initHuffman() {")
	_assert_order(
		msg_init,
		"Huff_Init(&msgHuff);",
		"for(i=0;i<256;i++) {",
		"for (j=0;j<msg_hData[i];j++) {",
		"Huff_addRef(&msgHuff.compressor,\t(byte)i);",
		"Huff_addRef(&msgHuff.decompressor,\t(byte)i);",
	)

	oob_data = _function_block(net_chan, "void QDECL NET_OutOfBandData( netsrc_t sock, netadr_t adr, byte *format, int len )")
	_assert_order(
		oob_data,
		"string[0] = 0xff;",
		"string[i+4] = format[i];",
		"mbuf.data = string;",
		"mbuf.cursize = len+4;",
		"Huff_Compress( &mbuf, 12);",
	)
	check_resend = _function_block(cl_main, "void CL_CheckForResend( void ) {")
	_assert_order(
		check_resend,
		"Com_sprintf( data, sizeof( data ), \"%s \\\"%s\\\"\", NET_GetConnectRequestCommand(), info );",
		"dataLength = strlen( data );",
		"if ( NET_ProtocolUsesCompressedConnect() ) {",
		"NET_OutOfBandData( NS_CLIENT, clc.serverAddress, (byte *)data, dataLength );",
	)
	connectionless = _function_block(sv_main, "void SV_ConnectionlessPacket( netadr_t from, msg_t *msg )")
	_assert_order(
		connectionless,
		"if ( NET_ProtocolUsesCompressedConnect() && NET_IsConnectRequestPacket( msg ) ) {",
		"Huff_Decompress(msg, 12);",
		"s = MSG_ReadStringLine( msg );",
	)

	for expected in (
		"004d40f0    int32_t sub_4d40f0(void* arg1, int32_t arg2)",
		"004d41bd      char var_10008 = (ebx_2 s>> 8).b",
		"004d41c3      char var_10007_1 = ebx_2.b",
		"004d41c9      data_1239df0 = 0x10",
		"004d41f9              sub_4d3c90(&var_17024, edi_1, &var_10008)",
		"004d4206              sub_4d3980(&var_17024, edi_1.b)",
		"004d4233      *(arg1 + 0x10) = eax_8 + result",
		"004d6bb0    void* sub_4d6bb0()",
		"004d6be6              sub_4d3980(&data_123c5f8, esi.b)",
		"004d6bf1              result = sub_4d3980(&data_1243614, esi.b)",
	):
		assert expected in hlil_part04
	connectionless_hlil = hlil_part05.split("004e4340    int32_t sub_4e4340", 1)[1].split("004e4500", 1)[0]
	assert "sub_4d3e60(arg9, 0xc)" in connectionless_hlil

	anchors = {item["symbol"]: item for item in spec["retail_anchors"]}
	assert anchors["MSG_initHuffman"]["address"] == "0x004D6BB0"
	assert anchors["MSG_WriteBits"]["address"] == "0x004D4AF0"
	assert anchors["Huff_Compress"]["address"] == "0x004D40F0"
	assert anchors["NET_OutOfBandData"]["address"] == "0x004D7120"
	assert anchors["SV_ConnectionlessPacket"]["address"] == "0x004E4340"

	assert "Network Adaptive Huffman Fixtures" in audit_note
	assert "compressed_connect_profile91_numeric_challenge" in audit_note
	assert "Focused Huffman fixture slice: `35%` before, `82%` after." in audit_note
	assert "- [x] Add capture-scoped adaptive Huffman fixtures" in checklist
	assert "network-adaptive-huffman-fixtures-2026-06-05.md" in checklist
	assert "network-adaptive-huffman-fixtures-2026-06-05.json" in plan
	assert "focused Huffman fixture" in plan
	assert "`35%` -> `82%`" in plan
	assert "network-adaptive-huffman-fixtures-2026-06-05.md" in replay_note
	assert "network-adaptive-huffman-fixtures-2026-06-05.md" in usercmd_note
	assert "network-adaptive-huffman-fixtures-2026-06-05.md" in oob_note

	assert spec["completion_status"]["status"] == "completed_capture_scoped_fixture_contract"
	assert spec["completion_status"]["runtime_launch_required"] is False
	assert spec["completion_status"]["source_patch_required"] is False
	assert spec["completion_status"]["focused_huffman_fixture_slice_before_percent"] == 35
	assert spec["completion_status"]["focused_huffman_fixture_slice_after_percent"] == 82
	assert spec["completion_status"]["overall_network_protocol_parity_before_percent"] == 87
	assert spec["completion_status"]["overall_network_protocol_parity_after_percent"] == 88
	assert "retail packet capture" in spec["completion_status"]["remaining_gaps"][0]
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_capture_scoped_adaptive_huffman_fixtures" in spec["assertion_tests"]


def test_networking_2_client_message_parser_grammar_and_sideband_byte() -> None:
	grammar = _networking_2_client_parser_grammar()
	qcommon_h = _read(QCOMMON_H_PATH)
	msg_c = _read(MSG_C_PATH)
	cl_input = _read(CL_INPUT_PATH)
	cl_net_chan = _read(CL_NET_CHAN_PATH)
	sv_client = _read(SV_CLIENT_PATH)
	sv_net_chan = _read(SV_NET_CHAN_PATH)
	hlil_part04 = _read(HLIL_PART04_PATH)
	audit_note = _read(NETWORKING_2_CLIENT_PARSER_AUDIT_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)

	assert grammar["schema_version"] == 1
	assert grammar["last_updated"] == "2026-06-05"
	assert grammar["depends_on"] == [
		"docs/reverse-engineering/network-protocol-parity-ledger-2026-06-05.json",
		"docs/reverse-engineering/network-protocol-header-transport-spec-2026-06-05.json",
	]
	assert grammar["owning_retail_binary"]["path"] == "assets/quakelive/quakelive_steam.exe"

	opcodes = grammar["opcode_enum"]
	assert opcodes == {
		"clc_bad": 0,
		"clc_nop": 1,
		"clc_move": 2,
		"clc_moveNoDelta": 3,
		"clc_clientCommand": 4,
		"clc_EOF": 5,
	}
	opcode_names = {value: name for name, value in opcodes.items()}

	clc_enum = qcommon_h.split("enum clc_ops_e {", 1)[1].split("};", 1)[0]
	_assert_order(
		clc_enum,
		"clc_bad,",
		"clc_nop,",
		"clc_move,",
		"clc_moveNoDelta,",
		"clc_clientCommand,",
		"clc_EOF",
	)

	body_fields = {
		field["name"]: field
		for field in grammar["client_message_body"]["fields"]
	}
	assert body_fields["serverId"]["offset"] == 0
	assert body_fields["messageAcknowledge"]["offset"] == 4
	assert body_fields["reliableAcknowledge"]["offset"] == 8
	assert body_fields["retailClientMessageSideband"]["offset"] == 12
	assert body_fields["firstOpcode"]["offset"] == 13
	assert body_fields["retailClientMessageSideband"]["source_value"] == "CL_RetailClientMessageFlags() ^ (clc.serverCommandSequence & 0xff)"
	assert body_fields["retailClientMessageSideband"]["retail_value"] == "sub_4AF4D0() ^ (serverCommandSequence & 0xff)"

	def parse_body(vector: dict) -> dict:
		body = bytes.fromhex(vector["hex"])
		return {
			"serverId": int.from_bytes(body[0:4], "little"),
			"messageAcknowledge": int.from_bytes(body[4:8], "little"),
			"reliableAcknowledge": int.from_bytes(body[8:12], "little"),
			"sideband": body[12],
			"first_opcode": opcode_names[body[13]],
			"body": body,
		}

	vectors = {vector["id"]: vector for vector in grammar["golden_vectors"]}
	assert set(vectors) == {
		"zero_sideband_move",
		"server_command_sequence_sideband_move_no_delta",
		"client_command_then_move",
		"legacy_no_sideband_negative",
	}

	zero_move = parse_body(vectors["zero_sideband_move"])
	assert f"0x{zero_move['serverId']:08x}" == vectors["zero_sideband_move"]["expected"]["serverId"]
	assert f"0x{zero_move['messageAcknowledge']:08x}" == vectors["zero_sideband_move"]["expected"]["messageAcknowledge"]
	assert zero_move["reliableAcknowledge"] == vectors["zero_sideband_move"]["expected"]["reliableAcknowledge"]
	assert zero_move["sideband"] == 0
	assert zero_move["first_opcode"] == "clc_move"
	assert zero_move["body"][14] == 1

	no_delta = parse_body(vectors["server_command_sequence_sideband_move_no_delta"])
	assert no_delta["sideband"] == 0x77
	assert no_delta["first_opcode"] == "clc_moveNoDelta"
	assert no_delta["body"][14] == 1

	client_command = parse_body(vectors["client_command_then_move"])
	client_command_body = client_command["body"]
	assert client_command["sideband"] == 0x77
	assert client_command["first_opcode"] == "clc_clientCommand"
	assert int.from_bytes(client_command_body[14:18], "little") == 0x10
	string_start = vectors["client_command_then_move"]["expected"]["client_command_string_offset"]
	string_end = client_command_body.index(0, string_start)
	assert client_command_body[string_start:string_end].decode("ascii") == "userinfo"
	assert opcode_names[client_command_body[27]] == "clc_move"
	assert client_command_body[28] == 1

	legacy_negative = parse_body(vectors["legacy_no_sideband_negative"])
	assert legacy_negative["sideband"] == opcodes["clc_move"]
	assert legacy_negative["first_opcode"] == "clc_nop"

	write_byte = _function_block(msg_c, "void MSG_WriteByte( msg_t *sb, int c )")
	read_byte = _function_block(msg_c, "int MSG_ReadByte( msg_t *msg )")
	write_long = _function_block(msg_c, "void MSG_WriteLong( msg_t *sb, int c )")
	read_long = _function_block(msg_c, "int MSG_ReadLong( msg_t *msg )")
	assert "MSG_WriteBits( sb, c, 8 );" in write_byte
	assert "c = (unsigned char)MSG_ReadBits( msg, 8 );" in read_byte
	assert "MSG_WriteBits( sb, c, 32 );" in write_long
	assert "c = MSG_ReadBits( msg, 32 );" in read_long

	flags = _function_block(cl_input, "static int CL_RetailClientMessageFlags( void )")
	_assert_order(
		flags,
		"return cl_retailClientMessageFlags;",
	)
	assert "static int cl_retailClientMessageFlags = RETAIL_CLIENT_MESSAGE_FLAG_INITIAL_HIGH_BIT;" in cl_input

	write_packet = _function_block(cl_input, "void CL_WritePacket( void )")
	_assert_order(
		write_packet,
		"MSG_Bitstream( &buf );",
		"MSG_WriteLong( &buf, cl.serverId );",
		"MSG_WriteLong( &buf, clc.serverMessageSequence );",
		"MSG_WriteLong( &buf, clc.serverCommandSequence );",
		"MSG_WriteByte( &buf, CL_RetailClientMessageFlags() ^ ( clc.serverCommandSequence & 0xff ) );",
		"MSG_WriteByte( &buf, clc_clientCommand );",
		"MSG_WriteByte (&buf, clc_moveNoDelta);",
		"MSG_WriteByte( &buf, count );",
		"CL_Netchan_Transmit (&clc.netchan, &buf);",
	)

	client_encode = _function_block(cl_net_chan, "static void CL_Netchan_Encode( msg_t *msg )")
	_assert_order(
		client_encode,
		"if ( msg->cursize <= CL_ENCODE_START ) {",
		"serverId = MSG_ReadLong(msg);",
		"messageAcknowledge = MSG_ReadLong(msg);",
		"reliableAcknowledge = MSG_ReadLong(msg);",
		"for (i = CL_ENCODE_START; i < msg->cursize; i++) {",
	)
	client_transmit = _function_block(cl_net_chan, "void CL_Netchan_Transmit( netchan_t *chan, msg_t* msg )")
	_assert_order(
		client_transmit,
		"MSG_WriteByte( msg, clc_EOF );",
		"if ( NET_ProtocolUsesReliableXorCodec() ) {",
		"CL_Netchan_Encode( msg );",
		"Netchan_Transmit( chan, msg->cursize, msg->data );",
	)

	server_decode = _function_block(sv_net_chan, "static void SV_Netchan_Decode( client_t *client, msg_t *msg )")
	_assert_order(
		server_decode,
		"serverId = MSG_ReadLong(msg);",
		"messageAcknowledge = MSG_ReadLong(msg);",
		"reliableAcknowledge = MSG_ReadLong(msg);",
		"for (i = msg->readcount + SV_DECODE_START; i < msg->cursize; i++) {",
	)

	execute = _function_block(sv_client, "void SV_ExecuteClientMessage( client_t *cl, msg_t *msg )")
	_assert_order(
		execute,
		"MSG_Bitstream(msg);",
		"serverId = MSG_ReadLong( msg );",
		"cl->messageAcknowledge = MSG_ReadLong( msg );",
		"cl->reliableAcknowledge = MSG_ReadLong( msg );",
		"(void)MSG_ReadByte( msg );",
		"do {",
		"c = MSG_ReadByte( msg );",
		"if ( c == clc_EOF ) {",
		"if ( c != clc_clientCommand ) {",
		"if ( c == clc_move ) {",
		"SV_UserMove( cl, msg, qtrue );",
		"} else if ( c == clc_moveNoDelta ) {",
		"SV_UserMove( cl, msg, qfalse );",
	)

	write_hlil = hlil_part04.split("004b5f70    int32_t sub_4b5f70", 1)[1].split("004b6262", 1)[0]
	_assert_order(
		write_hlil,
		"sub_4d4e30(&var_8044, data_1472870)",
		"sub_4d4e30(&var_8044, data_1606b7c)",
		"sub_4d4e30(&var_8044, data_1606b80)",
		"sub_4d4dc0(&var_8044, zx.d(sub_4af4d0()) ^ data_1606b80.b)",
		"sub_4d4dc0(&var_8044, 4)",
		"sub_4d4e30(&var_8044, i)",
		"sub_4d4dc0(__saved_ebx_5, __saved_edi_6)",
	)

	execute_hlil = hlil_part04.split("004e05c0    uint32_t sub_4e05c0", 1)[1].split("004e0750", 1)[0]
	_assert_order(
		execute_hlil,
		"uint32_t eax = sub_4d5020(arg2)",
		"uint32_t i = sub_4d5020(arg2)",
		"arg1[0x4102] = sub_4d5020(arg2)",
		"sub_4d4fc0(arg2)",
		"i, edx_2 = sub_4d4fc0(arg2)",
		"while (i == 4)",
		"i, edx_2 = sub_4d4fc0(arg2)",
		"if (i == 2)",
		"return sub_4e0320(arg2, 1)",
		"if (i == 3)",
		"return sub_4e0320(arg2, 0)",
	)
	assert "004af4d0    int32_t sub_4af4d0()" in hlil_part04
	assert "004af4d5  return data_565948" in hlil_part04
	assert "data_565948 |= 0x40" in hlil_part04
	assert "data_565948 |= 0x20" in hlil_part04

	anchors = {item["symbol"]: item for item in grammar["retail_anchors"]}
	assert anchors["CL_WritePacket"]["address"] == "0x004B5F70"
	assert anchors["SV_ExecuteClientMessage"]["address"] == "0x004E05C0"
	assert anchors["CL_RetailClientMessageFlags_source_partial"]["address"] is None

	assert grammar["resolved_conflict"]["source_change_required"] is True
	assert "unassigned MSG_ReadByte" in grammar["resolved_conflict"]["resolution"]
	assert grammar["completion_status"]["status"] == "completed_source_patch_static_grammar_and_golden_vectors"
	assert grammar["completion_status"]["focused_task_parity_before_percent"] == 55
	assert grammar["completion_status"]["focused_task_parity_after_percent"] == 90
	assert grammar["completion_status"]["overall_network_protocol_parity_before_percent"] == 74
	assert grammar["completion_status"]["overall_network_protocol_parity_after_percent"] == 76
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_client_message_parser_grammar_and_sideband_byte" in grammar["assertion_tests"]

	assert "Network Client Message Parser Grammar" in audit_note
	assert "Retail client-message sideband byte" in audit_note
	assert "Focused client-parser header slice: `55%` before, `90%` after." in audit_note
	assert "Verify **client-parser header semantics**" in plan
	assert "network-client-message-parser-grammar-2026-06-05.json" in plan
	assert "focused client-parser header slice" in plan


def test_networking_2_client_message_sideband_producer_map_and_constant_high_bit() -> None:
	spec = _networking_2_client_sideband_producers_spec()
	grammar = _networking_2_client_parser_grammar()
	xor_spec = _networking_2_xor_codec_spec()
	ledger = _networking_2_ledger()
	cl_input = _read(CL_INPUT_PATH)
	cl_cgame = _read(CL_CGAME_PATH)
	cl_main = _read(CL_MAIN_PATH)
	client_h = _read(CLIENT_H_PATH)
	cg_public = _read(CG_PUBLIC_PATH)
	tr_public = _read(TR_PUBLIC_PATH)
	tr_cmds = _read(TR_CMDS_PATH)
	functions_csv = _read(GHIDRA_FUNCTIONS_PATH)
	ghidra_top = _read(GHIDRA_DECOMPILE_TOP_PATH)
	aliases = json.loads(_read(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam_srp"]
	hlil_part02 = _read(HLIL_PART02_PATH)
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part07 = _read(HLIL_PART07_PATH)
	audit_note = _read(NETWORKING_2_CLIENT_SIDEBAND_PRODUCERS_AUDIT_PATH)
	parser_note = _read(NETWORKING_2_CLIENT_PARSER_AUDIT_PATH)
	xor_note = _read(NETWORKING_2_XOR_CODEC_AUDIT_PATH)
	checklist = _read(OUTSTANDING_WORK_CHECKLIST_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-client-message-parser-grammar-2026-06-05.json",
		"docs/reverse-engineering/network-xor-codec-parity-2026-06-05.json",
	]
	assert spec["owning_retail_binary"]["path"] == "assets/quakelive/quakelive_steam.exe"
	assert spec["source_files"] == [
		"src/code/client/cl_cgame.c",
		"src/code/client/cl_input.c",
		"src/code/client/cl_main.c",
		"src/code/client/client.h",
		"src/code/renderer/tr_cmds.c",
		"src/code/renderer/tr_public.h",
	]

	state = spec["retail_state"]
	assert state["symbol"] == "data_565948"
	assert state["address"] == "0x00565948"
	assert state["initial_value"] == "0x80"
	assert state["read_helper"] == {
		"symbol": "sub_4AF4D0",
		"address": "0x004AF4D0",
		"observed": "return data_565948",
	}

	producers = {producer["id"]: producer for producer in spec["producer_map"]}
	assert set(producers) == {
		"initial_high_bit",
		"renderer_low_five_bits",
		"cgame_import_pointer_guard",
		"viewangle_delta_bit",
	}
	assert producers["initial_high_bit"]["mask"] == "0x80"
	assert producers["initial_high_bit"]["source_status"] == "implemented_by_persistent_CL_RetailClientMessageFlags_initializer"
	assert producers["renderer_low_five_bits"]["mask"] == "0x1f"
	assert producers["renderer_low_five_bits"]["function"] == "sub_43C120"
	assert producers["renderer_low_five_bits"]["source_status"] == "implemented_by_refimport_SetClientMessageRendererNodeCount"
	assert producers["cgame_import_pointer_guard"]["mask"] == "0x40"
	assert producers["cgame_import_pointer_guard"]["function"] == "sub_4B0A50"
	assert producers["cgame_import_pointer_guard"]["source_status"] == "implemented_by_CL_CheckCGameNativeImportIntegrity"
	assert "R_AddRefEntityToScene and R_RenderScene" in producers["cgame_import_pointer_guard"]["inferred_meaning"]
	assert producers["viewangle_delta_bit"]["mask"] == "0x20"
	assert producers["viewangle_delta_bit"]["function"] == "sub_4BC3E0 / CL_Frame"
	assert producers["viewangle_delta_bit"]["source_status"] == "implemented_by_CL_Frame_viewangle_compare_after_SCR_UpdateScreen"

	source_status = spec["source_status"]
	assert source_status["helper"] == "CL_RetailClientMessageFlags"
	assert source_status["current_return"] == "persistent cl_retailClientMessageFlags, initialized to 0x80"
	assert source_status["classification"] == "all_observed_retail_sideband_producers_implemented_static_capture_diff_pending"
	assert source_status["byte_for_byte_complete"] is False

	assert "#define RETAIL_CLIENT_MESSAGE_FLAG_VIEWANGLE_DELTA\t0x20" in cl_input
	assert "#define RETAIL_CLIENT_MESSAGE_FLAG_CGAME_IMPORT_GUARD\t0x40" in cl_input
	assert "#define RETAIL_CLIENT_MESSAGE_FLAG_INITIAL_HIGH_BIT\t0x80" in cl_input
	assert "#define RETAIL_CLIENT_MESSAGE_RENDERER_NODE_MASK\t\t0x1f" in cl_input
	assert "#define RETAIL_CLIENT_MESSAGE_RENDERER_NODE_LIMIT\t0x20" in cl_input
	assert "static int cl_retailClientMessageFlags = RETAIL_CLIENT_MESSAGE_FLAG_INITIAL_HIGH_BIT;" in cl_input
	setter = _function_block(cl_input, "void CL_SetRetailClientMessageViewangleDeltaFlag( void )")
	assert "cl_retailClientMessageFlags |= RETAIL_CLIENT_MESSAGE_FLAG_VIEWANGLE_DELTA;" in setter
	cgame_guard_setter = _function_block(cl_input, "void CL_SetRetailClientMessageCGameImportGuardFlag( void )")
	assert "cl_retailClientMessageFlags |= RETAIL_CLIENT_MESSAGE_FLAG_CGAME_IMPORT_GUARD;" in cgame_guard_setter
	renderer_setter = _function_block(cl_input, "void CL_SetRetailClientMessageRendererNodeCount( int nodeCount )")
	_assert_order(
		renderer_setter,
		"if ( nodeCount < 0 ) {",
		"clampedNodeCount = 0;",
		"} else if ( nodeCount > RETAIL_CLIENT_MESSAGE_RENDERER_NODE_LIMIT ) {",
		"clampedNodeCount = RETAIL_CLIENT_MESSAGE_RENDERER_NODE_LIMIT;",
		"cl_retailClientMessageFlags ^= ( cl_retailClientMessageFlags ^ clampedNodeCount ) & RETAIL_CLIENT_MESSAGE_RENDERER_NODE_MASK;",
	)
	flags = _function_block(cl_input, "static int CL_RetailClientMessageFlags( void )")
	assert "return cl_retailClientMessageFlags;" in flags
	assert "return 0;" not in flags
	assert "Dynamic producer bits are only" in cl_input
	assert "void CL_SetRetailClientMessageViewangleDeltaFlag( void );" in client_h
	assert "void CL_SetRetailClientMessageCGameImportGuardFlag( void );" in client_h
	assert "void CL_SetRetailClientMessageRendererNodeCount( int nodeCount );" in client_h
	assert "void CL_CheckCGameNativeImportIntegrity( void );" in client_h
	assert "(*SetClientMessageRendererNodeCount)( int nodeCount );" in tr_public
	assert "CG_QL_IMPORT_R_ADDREFENTITYTOSCENE = 71," in cg_public
	assert "CG_QL_IMPORT_R_RENDERSCENE = 76," in cg_public

	frame = _function_block(cl_main, "void CL_Frame ( int msec )")
	_assert_order(
		frame,
		"CL_SendCmd();",
		"CL_CheckForResend();",
		"CL_CheckCGameNativeImportIntegrity();",
		"CL_SetCGameTime();",
		"oldViewYaw = cl.viewangles[YAW];",
		"oldViewPitch = cl.viewangles[PITCH];",
		"SCR_UpdateScreen();",
		"if ( oldViewYaw != cl.viewangles[YAW] || oldViewPitch != cl.viewangles[PITCH] ) {",
		"CL_SetRetailClientMessageViewangleDeltaFlag();",
		"S_Update();",
	)
	init_ref = _function_block(cl_main, "void CL_InitRef( void )")
	_assert_order(
		init_ref,
		"ri.CIN_RunCinematic = CIN_RunCinematic;",
		"ri.SetClientMessageRendererNodeCount = CL_SetRetailClientMessageRendererNodeCount;",
		"ri.AdvertisementBridge_GetCellDisplayState = CL_AdvertisementBridge_GetCellDisplayState;",
	)
	cgame_imports = _function_block(cl_cgame, "static void CL_InitCGameImports( void )")
	_assert_order(
		cgame_imports,
		"ql_cgame_imports[CG_QL_IMPORT_R_CLEARSCENE] = (ql_import_f)QL_CG_trap_R_ClearScene;",
		"ql_cgame_imports[CG_QL_IMPORT_R_ADDREFENTITYTOSCENE] = (ql_import_f)QL_CG_trap_R_AddRefEntityToScene;",
		"ql_cgame_imports[CG_QL_IMPORT_R_RENDERSCENE] = (ql_import_f)QL_CG_trap_R_RenderScene;",
	)
	cgame_integrity = _function_block(cl_cgame, "void CL_CheckCGameNativeImportIntegrity( void )")
	_assert_order(
		cgame_integrity,
		"ql_cgame_imports[CG_QL_IMPORT_R_ADDREFENTITYTOSCENE] != (ql_import_f)QL_CG_trap_R_AddRefEntityToScene ||",
		"ql_cgame_imports[CG_QL_IMPORT_R_RENDERSCENE] != (ql_import_f)QL_CG_trap_R_RenderScene ) {",
		"CL_SetRetailClientMessageCGameImportGuardFlag();",
	)
	performance_counters = _function_block(tr_cmds, "void R_PerformanceCounters( void )")
	_assert_order(
		performance_counters,
		"nodeCount = tr.pc.c_leafs;",
		"if ( ri.SetClientMessageRendererNodeCount ) {",
		"ri.SetClientMessageRendererNodeCount( nodeCount );",
		"if ( !r_speeds->integer ) {",
		"Com_Memset( &tr.pc, 0, sizeof( tr.pc ) );",
	)

	for expected in (
		"FUN_0043c120,0043c120,692,0,unknown",
		"FUN_004af4d0,004af4d0,6,0,unknown",
		"FUN_004b0a50,004b0a50,32,0,unknown",
		"FUN_004bc3e0,004bc3e0,674,0,unknown",
	):
		assert expected in functions_csv
	assert aliases["sub_43C120"] == "R_PerformanceCounters"
	assert aliases["sub_4B0000"] == "QLCGImport_R_AddRefEntityToScene"
	assert aliases["sub_4BEF80"] == "QLCGImport_R_RenderScene"
	assert aliases["sub_4BC3E0"] == "CL_Frame"
	assert aliases["sub_4B07C0"] == "CL_SetCGameTime"
	assert aliases["sub_4BE3A0"] == "SCR_UpdateScreen"

	assert "00565948  int32_t data_565948 = 0x80" in hlil_part07
	assert "00565a74  void* data_565a74 = sub_4b0000" in hlil_part07
	assert "00565a88  void* data_565a88 = sub_4bef80" in hlil_part07
	assert "004af4d0    int32_t sub_4af4d0()" in hlil_part04
	assert "004af4d5  return data_565948" in hlil_part04
	assert "0043c120    int32_t sub_43c120()" in hlil_part02
	assert "0043c13a      int32_t eax_2 = sub_4d8970(eax_1, 0x20, data_1745edc)" in hlil_part02
	assert "data_565948 = ecx_2 ^ ((ecx_2 ^ eax_2) & 0x1f)" in hlil_part02
	assert "0043c33b              data_1740d20(0, \"Nodes:%i\\n\", data_1745edc)" in hlil_part02
	assert "0043c396  int32_t eax_27 = sub_4d8970(0, 0x20, data_1745edc)" in hlil_part02
	assert "data_565948 = ecx_18 ^ ((ecx_18 ^ eax_27) & 0x1f)" in hlil_part02
	assert "004d8970    int32_t sub_4d8970(int32_t arg1, int32_t arg2, int32_t arg3) __pure" in hlil_part04
	assert "004b0a50    int32_t sub_4b0a50()" in hlil_part04
	assert "004b0a66  if (data_565a74 != sub_4b0000 || data_565a88 != sub_4bef80)" in hlil_part04
	assert "data_565948 |= 0x40" in hlil_part04
	assert "data_565948 |= 0x20" in hlil_part04
	assert "DAT_01740f6c = (*DAT_01740d40)(\"r_speeds\"" in ghidra_top
	assert "004bc568      sub_4b0a50()" in hlil_part04
	assert "004bc632      sub_4be3a0()" in hlil_part04
	assert "004bc661          data_565948 |= 0x20" in hlil_part04

	assert grammar["retail_anchors"][2]["observed"].startswith(
		"Source reconstruction helper now returns a persistent retail sideband flag byte initialized to 0x80"
	)
	assert "The sideband producer map is captured" in grammar["completion_status"]["residual_risks"][0]
	assert "source now emits all observed retail sideband producers" in xor_spec["completion_status"]["residual_risks"][1]
	assert "0x80 initializer bit, recovered 0x20 CL_Frame viewangle-delta bit, recovered low-five renderer count, and recovered 0x40 native cgame import guard are implemented" in ledger["focus_areas"][0]["open_questions"][0]
	assert "Capture-diff client packet bytes against retail" in ledger["focus_areas"][6]["open_questions"][0]

	assert "Network Client Message Sideband Producers" in audit_note
	assert "`0x80` | data initializer `0x00565948`" in audit_note
	assert "`0x1f` | `sub_43C120` / `R_PerformanceCounters`" in audit_note
	assert "`0x40` | `sub_4B0A50`" in audit_note
	assert "Focused sideband producer slice: `88%` before, `100%` after." in audit_note
	assert "The source emits all observed sideband producers" in parser_note
	assert "remaining sideband proof is capture-backed packet comparison" in xor_note
	assert "- [x] Map the observed retail sideband producers" in checklist
	assert "- [x] Recover the retail `0x20` `CL_Frame` viewangle-delta sideband producer" in checklist
	assert "- [x] Recover the retail low-five renderer counter bits behind `sub_43C120`" in checklist
	assert "- [x] Recover the retail `0x40` native cgame/import guard" in checklist
	assert "network-client-message-sideband-producers-2026-06-05.json" in plan
	assert "focused sideband producer" in plan
	assert "`88%` -> `100%`" in plan

	assert spec["completion_status"]["status"] == "producer_map_captured_all_observed_producers_implemented_static_capture_diff_pending"
	assert spec["completion_status"]["runtime_launch_required"] is False
	assert spec["completion_status"]["focused_sideband_slice_before_percent"] == 88
	assert spec["completion_status"]["focused_sideband_slice_after_percent"] == 100
	assert spec["completion_status"]["overall_network_protocol_parity_before_percent"] == 89
	assert spec["completion_status"]["overall_network_protocol_parity_after_percent"] == 90
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_client_message_sideband_producer_map_and_constant_high_bit" in spec["assertion_tests"]


def test_networking_2_xor_codec_golden_vectors_and_capture_diff_windows() -> None:
	spec = _networking_2_xor_codec_spec()
	header_spec = _networking_2_header_spec()
	qcommon_h = _read(QCOMMON_H_PATH)
	cl_net_chan = _read(CL_NET_CHAN_PATH)
	sv_net_chan = _read(SV_NET_CHAN_PATH)
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part05 = _read(HLIL_PART05_PATH)
	audit_note = _read(NETWORKING_2_XOR_CODEC_AUDIT_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-protocol-parity-ledger-2026-06-05.json",
		"docs/reverse-engineering/network-protocol-header-transport-spec-2026-06-05.json",
		"docs/reverse-engineering/network-client-message-parser-grammar-2026-06-05.json",
	]
	assert spec["owning_retail_binary"]["path"] == "assets/quakelive/quakelive_steam.exe"

	constants = spec["codec_constants"]
	assert constants == {
		"SV_ENCODE_START": 4,
		"SV_DECODE_START": 12,
		"CL_ENCODE_START": 12,
		"CL_DECODE_START": 4,
		"rolling_key_width_bits": 8,
		"command_ring_mask": "MAX_RELIABLE_COMMANDS - 1",
	}
	for expected in (
		"#define\tSV_ENCODE_START\t\t4",
		"#define SV_DECODE_START\t\t12",
		"#define\tCL_ENCODE_START\t\t12",
		"#define CL_DECODE_START\t\t4",
	):
		assert expected in qcommon_h

	assert header_spec["xor_windows"]["client_to_server"]["encode_start"] == spec["codec_windows"]["client_to_server"]["encode_start"]
	assert header_spec["xor_windows"]["client_to_server"]["decode_start"] == spec["codec_windows"]["client_to_server"]["decode_start_relative_to_msg_readcount"]
	assert header_spec["xor_windows"]["server_to_client"]["encode_start"] == spec["codec_windows"]["server_to_client"]["encode_start"]
	assert header_spec["xor_windows"]["server_to_client"]["decode_start"] == spec["codec_windows"]["server_to_client"]["decode_start_relative_to_msg_readcount"]

	assert spec["algorithm"]["symmetric"] is True
	assert spec["algorithm"]["sanitized_command_replacement_hex"] == "2e"
	assert spec["algorithm"]["sanitized_conditions"] == [
		"command_byte > 0x7f",
		"command_byte == 0x25",
	]

	vectors = {vector["id"]: vector for vector in spec["golden_vectors"]}
	assert set(vectors) == {
		"client_to_server_sideband_move",
		"client_to_server_sanitized_command_bytes",
		"server_to_client_reliable_acknowledge",
		"server_to_client_sanitized_command_bytes",
	}

	for vector in vectors.values():
		clear_body = bytes.fromhex(vector["clear_body_hex"])
		encoded_body = bytes.fromhex(vector["encoded_body_hex"])
		command_bytes = bytes.fromhex(vector["command_string_bytes_hex"])
		initial_key = int(vector["initial_key_low_byte"], 16)

		assert _ql_reliable_xor(clear_body, vector["encode_start"], initial_key, command_bytes) == encoded_body
		assert _ql_reliable_xor(encoded_body, vector["encode_start"], initial_key, command_bytes) == clear_body
		assert clear_body[:vector["encode_start"]] == encoded_body[:vector["encode_start"]]

		clear_datagram = bytes.fromhex(vector["clear_datagram_hex"])
		encoded_datagram = bytes.fromhex(vector["encoded_datagram_hex"])
		body_offset = vector["datagram_body_offset"]
		decode_start = vector["decoder_readcount_after_netchan_process"] + vector["decode_start_relative_to_msg_readcount"]

		assert clear_datagram[:body_offset] == encoded_datagram[:body_offset]
		assert clear_datagram[body_offset:] == clear_body
		assert encoded_datagram[body_offset:] == encoded_body
		assert _ql_reliable_xor(clear_datagram, decode_start, initial_key, command_bytes) == encoded_datagram
		assert _ql_reliable_xor(encoded_datagram, decode_start, initial_key, command_bytes) == clear_datagram

	sideband = vectors["client_to_server_sideband_move"]
	sideband_clear = bytes.fromhex(sideband["clear_body_hex"])
	sideband_encoded = bytes.fromhex(sideband["encoded_body_hex"])
	assert sideband_clear[12] == 0x77
	assert sideband_encoded[12] == 0x45
	assert sideband_clear[:12] == sideband_encoded[:12]
	assert sideband["capture_diff_assertions"] == [
		"datagram bytes 0 through 17 remain clear",
		"client body byte 12 changes from 0x77 to 0x45",
	]

	for vector_id in (
		"client_to_server_sanitized_command_bytes",
		"server_to_client_sanitized_command_bytes",
	):
		command_bytes = bytes.fromhex(vectors[vector_id]["command_string_bytes_hex"])
		assert command_bytes[0] == ord("%")
		assert command_bytes[1] == 0x80

	client_encode = _function_block(cl_net_chan, "static void CL_Netchan_Encode( msg_t *msg )")
	_assert_order(
		client_encode,
		"if ( msg->cursize <= CL_ENCODE_START ) {",
		"serverId = MSG_ReadLong(msg);",
		"messageAcknowledge = MSG_ReadLong(msg);",
		"reliableAcknowledge = MSG_ReadLong(msg);",
		"string = (byte *)clc.serverCommands[ reliableAcknowledge & (MAX_RELIABLE_COMMANDS-1) ];",
		"key = clc.challenge ^ serverId ^ messageAcknowledge;",
		"for (i = CL_ENCODE_START; i < msg->cursize; i++) {",
		"if (!string[index])",
		"if (string[index] > 127 || string[index] == '%') {",
		"key ^= '.' << (i & 1);",
		"*(msg->data + i) = (*(msg->data + i)) ^ key;",
	)

	client_decode = _function_block(cl_net_chan, "static void CL_Netchan_Decode( msg_t *msg )")
	_assert_order(
		client_decode,
		"reliableAcknowledge = MSG_ReadLong(msg);",
		"string = clc.reliableCommands[ reliableAcknowledge & (MAX_RELIABLE_COMMANDS-1) ];",
		"key = clc.challenge ^ LittleLong( *(unsigned *)msg->data );",
		"for (i = msg->readcount + CL_DECODE_START; i < msg->cursize; i++) {",
		"if (string[index] > 127 || string[index] == '%') {",
		"key ^= '.' << (i & 1);",
		"*(msg->data + i) = *(msg->data + i) ^ key;",
	)

	server_encode = _function_block(sv_net_chan, "static void SV_Netchan_Encode( client_t *client, msg_t *msg )")
	_assert_order(
		server_encode,
		"if ( msg->cursize < SV_ENCODE_START ) {",
		"reliableAcknowledge = MSG_ReadLong(msg);",
		"string = (byte *)client->lastClientCommandString;",
		"key = client->challenge ^ client->netchan.outgoingSequence;",
		"for (i = SV_ENCODE_START; i < msg->cursize; i++) {",
		"if (string[index] > 127 || string[index] == '%') {",
		"key ^= '.' << (i & 1);",
		"*(msg->data + i) = *(msg->data + i) ^ key;",
	)

	server_decode = _function_block(sv_net_chan, "static void SV_Netchan_Decode( client_t *client, msg_t *msg )")
	_assert_order(
		server_decode,
		"serverId = MSG_ReadLong(msg);",
		"messageAcknowledge = MSG_ReadLong(msg);",
		"reliableAcknowledge = MSG_ReadLong(msg);",
		"string = (byte *)client->reliableCommands[ reliableAcknowledge & (MAX_RELIABLE_COMMANDS-1) ];",
		"key = client->challenge ^ serverId ^ messageAcknowledge;",
		"for (i = msg->readcount + SV_DECODE_START; i < msg->cursize; i++) {",
		"if (string[index] > 127 || string[index] == '%') {",
		"key ^= '.' << (i & 1);",
		"*(msg->data + i) = *(msg->data + i) ^ key;",
	)

	client_encode_hlil = hlil_part04.split("004bce30    void sub_4bce30", 1)[1].split("004bcef0", 1)[0]
	_assert_order(
		client_encode_hlil,
		"if (*(arg1 + 0x10) s> 0xc)",
		"char eax_2 = sub_4d5020(arg1)",
		"char eax_3 = sub_4d5020(arg1)",
		"uint32_t eax_4 = sub_4d5020(arg1)",
		"char edx_1 = data_15f6b6c.b ^ eax_2 ^ eax_3",
		"int32_t edi_2 = 0xc",
		"if (eax.b u> 0x7f || eax.b == 0x25)",
		"eax.b = 0x2e",
		"eax.b <<= edi_2.b & 1",
		"*(eax + edi_2 - 1) ^= edx_1",
	)

	client_decode_hlil = hlil_part04.split("004bcef0    int32_t sub_4bcef0", 1)[1].split("004bcf80", 1)[0]
	_assert_order(
		client_decode_hlil,
		"uint32_t eax_1 = sub_4d5020(arg1)",
		"result.b = *edx",
		"result.b ^= data_15f6b6c.b",
		"int32_t edx_1 = ebx + 4",
		"if (ebx.b u> 0x7f || ebx.b == 0x25)",
		"ebx.b = 0x2e",
		"ebx.b <<= edx_1.b & 1",
		"*(ecx_5 + edx_1 - 1) ^= result.b",
	)

	server_encode_hlil = hlil_part05.split("004e4cd0    void sub_4e4cd0", 1)[1].split("004e4d70", 1)[0]
	_assert_order(
		server_encode_hlil,
		"if (*(arg1 + 0x10) s>= 4)",
		"sub_4d5020(arg1)",
		"char edx_1 = *(ecx_2 + 0x15b08) ^ *(ecx_2 + 0x10418)",
		"int32_t eax = 4",
		"if (ebx_1.b u> 0x7f || ebx_1.b == 0x25)",
		"ebx_1.b = 0x2e",
		"ebx_1.b <<= eax.b & 1",
		"*(ecx_5 + eax - 1) ^= edx_1",
	)

	server_decode_hlil = hlil_part05.split("004e4d70    int32_t sub_4e4d70", 1)[1].split("004e4e20", 1)[0]
	_assert_order(
		server_decode_hlil,
		"char eax_1 = sub_4d5020(arg1)",
		"char eax_2 = sub_4d5020(arg1)",
		"int32_t result = (sub_4d5020(arg1) & 0x3f) << 0xa",
		"result.b = *(arg2 + 0x10418)",
		"result.b ^= eax_1",
		"int32_t edi_1 = edi + 0xc",
		"result.b ^= eax_2",
		"if (edx.b u> 0x7f || edx.b == 0x25)",
		"edx.b = 0x2e",
		"edx.b <<= edi_1.b & 1",
		"*(ecx_4 + edi_1 - 1) ^= result.b",
	)

	anchors = {item["symbol"]: item for item in spec["retail_anchors"]}
	assert anchors["CL_Netchan_Encode"]["address"] == "0x004BCE30"
	assert anchors["CL_Netchan_Decode"]["address"] == "0x004BCEF0"
	assert anchors["SV_Netchan_Encode"]["address"] == "0x004E4CD0"
	assert anchors["SV_Netchan_Decode"]["address"] == "0x004E4D70"

	assert spec["capture_diff_status"]["status"] == "static_wire_datagram_vectors_added"
	assert spec["capture_diff_status"]["external_retail_captures_available"] is False
	assert spec["completion_status"]["status"] == "completed_static_golden_vectors_capture_diff_ready"
	assert spec["completion_status"]["focused_task_parity_before_percent"] == 80
	assert spec["completion_status"]["focused_task_parity_after_percent"] == 94
	assert spec["completion_status"]["overall_network_protocol_parity_before_percent"] == 76
	assert spec["completion_status"]["overall_network_protocol_parity_after_percent"] == 78
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_xor_codec_golden_vectors_and_capture_diff_windows" in spec["assertion_tests"]

	assert "Network XOR Codec Parity" in audit_note
	assert "client body byte 12 changes from `0x77` to `0x45`" in audit_note
	assert "focused XOR codec slice `80%` -> `94%`" in audit_note
	assert "Finalize **XOR codec parity**" in plan
	assert "network-xor-codec-parity-2026-06-05.json" in plan
	assert "focused XOR codec slice" in plan


def test_networking_2_usercmd_delta_struct_layout_and_logical_vectors() -> None:
	spec = _networking_2_usercmd_delta_spec()
	q_shared = _read(Q_SHARED_PATH)
	msg_c = _read(MSG_C_PATH)
	hlil_part04 = _read(HLIL_PART04_PATH)
	audit_note = _read(NETWORKING_2_USERCMD_DELTA_AUDIT_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-protocol-parity-ledger-2026-06-05.json",
		"docs/reverse-engineering/network-protocol-header-transport-spec-2026-06-05.json",
		"docs/reverse-engineering/network-client-message-parser-grammar-2026-06-05.json",
	]
	assert spec["owning_retail_binary"]["path"] == "assets/quakelive/quakelive_steam.exe"

	class Usercmd(ctypes.Structure):
		_fields_ = [
			("serverTime", ctypes.c_int),
			("angles", ctypes.c_int * 3),
			("buttons", ctypes.c_int),
			("weapon", ctypes.c_ubyte),
			("weaponPrimary", ctypes.c_ubyte),
			("fov", ctypes.c_ubyte),
			("forwardmove", ctypes.c_byte),
			("rightmove", ctypes.c_byte),
			("upmove", ctypes.c_byte),
		]

	layout = spec["struct_layout"]
	assert layout["name"] == "usercmd_t"
	assert layout["sizeof_bytes"] == ctypes.sizeof(Usercmd) == 0x1c
	assert layout["alignment_bytes"] == ctypes.alignment(Usercmd) == 4

	expected_offsets = {
		"serverTime": Usercmd.serverTime.offset,
		"angles[0]": Usercmd.angles.offset,
		"angles[1]": Usercmd.angles.offset + ctypes.sizeof(ctypes.c_int),
		"angles[2]": Usercmd.angles.offset + ctypes.sizeof(ctypes.c_int) * 2,
		"buttons": Usercmd.buttons.offset,
		"weapon": Usercmd.weapon.offset,
		"weaponPrimary": Usercmd.weaponPrimary.offset,
		"fov": Usercmd.fov.offset,
		"forwardmove": Usercmd.forwardmove.offset,
		"rightmove": Usercmd.rightmove.offset,
		"upmove": Usercmd.upmove.offset,
	}
	spec_offsets = {field["name"]: int(field["offset"], 16) for field in layout["fields"]}
	assert spec_offsets == expected_offsets

	usercmd_decl = q_shared[q_shared.index("typedef struct usercmd_s {") : q_shared.index("} usercmd_t;")]
	_assert_order(
		usercmd_decl,
		"int\t\t\t\tserverTime;",
		"int\t\t\t\tangles[3];",
		"int \t\t\tbuttons;",
		"byte\t\t\tweapon;",
		"byte\t\t\tweaponPrimary;",
		"byte\t\t\tfov;",
		"signed char\tforwardmove, rightmove, upmove;",
	)

	field_widths = spec["field_widths"]
	field_order = [(field["field"], field["bits"], field["signed_assignment"]) for field in field_widths]
	expected_field_order = [
		("angles[0]", 16, False),
		("angles[1]", 16, False),
		("angles[2]", 16, False),
		("forwardmove", 8, True),
		("rightmove", 8, True),
		("upmove", 8, True),
		("buttons", 16, False),
		("weapon", 8, False),
		("weaponPrimary", 8, False),
		("fov", 8, False),
	]
	assert field_order == expected_field_order
	assert spec["wire_order"] == [
		"serverTime delta flag and payload",
		"changed-command flag for keyed commands only",
		"angles[0]",
		"angles[1]",
		"angles[2]",
		"forwardmove",
		"rightmove",
		"upmove",
		"buttons",
		"weapon",
		"weaponPrimary",
		"fov",
	]

	def mask(bits: int) -> int:
		return (1 << bits) - 1

	def signed_byte(value: int) -> int:
		value &= 0xff
		return value - 0x100 if value & 0x80 else value

	def hex_value(value: int, bits: int) -> str:
		return f"0x{value & mask(bits):0{bits // 4}x}"

	def expected_time(from_cmd: dict, to_cmd: dict) -> dict:
		delta = to_cmd["serverTime"] - from_cmd["serverTime"]
		if delta < 256:
			return {"encoding": "delta8", "flag_bit": 1, "bits": 8, "written_value": delta}
		return {"encoding": "full32", "flag_bit": 0, "bits": 32, "written_value": to_cmd["serverTime"]}

	def expected_field_event(vector: dict, field_name: str, bits: int, signed: bool) -> dict:
		from_cmd = vector["from"]
		to_cmd = vector["to"]
		old = from_cmd[field_name]
		new = to_cmd[field_name]
		event = {
			"field": field_name,
			"bits": bits,
			"old": old,
			"new": new,
			"changed": old != new,
		}
		if old != new:
			if vector["codec"] == "keyed":
				key = int(vector["effective_key"], 16)
				written = (new ^ key) & mask(bits)
				decoded = written ^ (key & mask(bits))
			else:
				written = new & mask(bits)
				decoded = written
			if signed:
				decoded = signed_byte(decoded)
			event["written_value"] = hex_value(written, bits)
			event["decoded_value"] = decoded
		return event

	def expected_bit_count(vector: dict) -> int:
		total = 1 + vector["time"]["bits"]
		if vector["codec"] == "keyed":
			total += 1
			if vector["changed_command_bit"]:
				total += sum(1 + (event["bits"] if event["changed"] else 0) for event in vector["field_events"])
		else:
			total += sum(1 + (event["bits"] if event["changed"] else 0) for event in vector["field_events"])
		return total

	vectors = {vector["id"]: vector for vector in spec["golden_vectors"]}
	assert set(vectors) == {
		"keyed_compact_all_fields_changed",
		"keyed_compact_no_field_changes",
		"keyed_full_time_tail_only",
		"unkeyed_compact_all_fields_changed",
		"unkeyed_full_time_tail_only",
	}

	for vector in vectors.values():
		assert vector["time"] == expected_time(vector["from"], vector["to"])
		if vector["codec"] == "keyed":
			assert vector["effective_key"] == f"0x{(int(vector['base_key'], 16) ^ vector['to']['serverTime']):08x}"
			changed = any(vector["from"][field_name] != vector["to"][field_name] for field_name, _bits, _signed in field_order)
			assert vector["changed_command_bit"] == (1 if changed else 0)
			if not changed:
				assert vector["field_events"] == []
				assert vector["copied_fields"] == [field_name for field_name, _bits, _signed in field_order]
			else:
				assert vector["field_events"] == [
					expected_field_event(vector, field_name, bits, signed)
					for field_name, bits, signed in field_order
				]
		else:
			assert vector["field_events"] == [
				expected_field_event(vector, field_name, bits, signed)
				for field_name, bits, signed in field_order
			]
		assert vector["logical_bit_count"] == expected_bit_count(vector)

	assert vectors["keyed_compact_all_fields_changed"]["field_events"][3]["decoded_value"] == -127
	assert vectors["keyed_compact_all_fields_changed"]["field_events"][5]["decoded_value"] == -12
	assert vectors["unkeyed_compact_all_fields_changed"]["field_events"][3]["written_value"] == "0x81"
	assert vectors["unkeyed_compact_all_fields_changed"]["field_events"][5]["written_value"] == "0xf4"
	assert vectors["keyed_full_time_tail_only"]["field_events"][8]["written_value"] == "0x00"
	assert vectors["unkeyed_full_time_tail_only"]["field_events"][8]["written_value"] == "0x0e"
	assert vectors["keyed_compact_no_field_changes"]["logical_bit_count"] == 10

	write_unkeyed = _function_block(msg_c, "void MSG_WriteDeltaUsercmd( msg_t *msg, usercmd_t *from, usercmd_t *to )")
	read_unkeyed = _function_block(msg_c, "void MSG_ReadDeltaUsercmd( msg_t *msg, usercmd_t *from, usercmd_t *to )")
	write_keyed = _function_block(msg_c, "void MSG_WriteDeltaUsercmdKey( msg_t *msg, int key, usercmd_t *from, usercmd_t *to )")
	read_keyed = _function_block(msg_c, "void MSG_ReadDeltaUsercmdKey( msg_t *msg, int key, usercmd_t *from, usercmd_t *to )")

	_assert_order(
		write_unkeyed,
		"MSG_WriteBits( msg, 1, 1 );",
		"MSG_WriteBits( msg, to->serverTime - from->serverTime, 8 );",
		"MSG_WriteBits( msg, 0, 1 );",
		"MSG_WriteBits( msg, to->serverTime, 32 );",
		"MSG_WriteDelta( msg, from->angles[0], to->angles[0], 16 );",
		"MSG_WriteDelta( msg, from->angles[1], to->angles[1], 16 );",
		"MSG_WriteDelta( msg, from->angles[2], to->angles[2], 16 );",
		"MSG_WriteDelta( msg, from->forwardmove, to->forwardmove, 8 );",
		"MSG_WriteDelta( msg, from->rightmove, to->rightmove, 8 );",
		"MSG_WriteDelta( msg, from->upmove, to->upmove, 8 );",
		"MSG_WriteDelta( msg, from->buttons, to->buttons, 16 );",
		"MSG_WriteDelta( msg, from->weapon, to->weapon, 8 );",
		"MSG_WriteDelta( msg, from->weaponPrimary, to->weaponPrimary, 8 );",
		"MSG_WriteDelta( msg, from->fov, to->fov, 8 );",
	)
	_assert_order(
		read_unkeyed,
		"to->serverTime = from->serverTime + MSG_ReadBits( msg, 8 );",
		"to->serverTime = MSG_ReadBits( msg, 32 );",
		"to->angles[0] = MSG_ReadDelta( msg, from->angles[0], 16);",
		"to->angles[1] = MSG_ReadDelta( msg, from->angles[1], 16);",
		"to->angles[2] = MSG_ReadDelta( msg, from->angles[2], 16);",
		"to->forwardmove = MSG_ReadDelta( msg, from->forwardmove, 8);",
		"to->rightmove = MSG_ReadDelta( msg, from->rightmove, 8);",
		"to->upmove = MSG_ReadDelta( msg, from->upmove, 8);",
		"to->buttons = MSG_ReadDelta( msg, from->buttons, 16);",
		"to->weapon = MSG_ReadDelta( msg, from->weapon, 8);",
		"to->weaponPrimary = MSG_ReadDelta( msg, from->weaponPrimary, 8);",
		"to->fov = MSG_ReadDelta( msg, from->fov, 8);",
	)
	_assert_order(
		write_keyed,
		"from->weaponPrimary == to->weaponPrimary",
		"from->fov == to->fov) {",
		"MSG_WriteBits( msg, 0, 1 );",
		"oldsize += 7;",
		"key ^= to->serverTime;",
		"MSG_WriteBits( msg, 1, 1 );",
		"MSG_WriteDeltaKey( msg, key, from->angles[0], to->angles[0], 16 );",
		"MSG_WriteDeltaKey( msg, key, from->angles[1], to->angles[1], 16 );",
		"MSG_WriteDeltaKey( msg, key, from->angles[2], to->angles[2], 16 );",
		"MSG_WriteDeltaKey( msg, key, from->forwardmove, to->forwardmove, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->rightmove, to->rightmove, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->upmove, to->upmove, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->buttons, to->buttons, 16 );",
		"MSG_WriteDeltaKey( msg, key, from->weapon, to->weapon, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->weaponPrimary, to->weaponPrimary, 8 );",
		"MSG_WriteDeltaKey( msg, key, from->fov, to->fov, 8 );",
	)
	_assert_order(
		read_keyed,
		"key ^= to->serverTime;",
		"to->angles[0] = MSG_ReadDeltaKey( msg, key, from->angles[0], 16);",
		"to->angles[1] = MSG_ReadDeltaKey( msg, key, from->angles[1], 16);",
		"to->angles[2] = MSG_ReadDeltaKey( msg, key, from->angles[2], 16);",
		"to->forwardmove = MSG_ReadDeltaKey( msg, key, from->forwardmove, 8);",
		"to->rightmove = MSG_ReadDeltaKey( msg, key, from->rightmove, 8);",
		"to->upmove = MSG_ReadDeltaKey( msg, key, from->upmove, 8);",
		"to->buttons = MSG_ReadDeltaKey( msg, key, from->buttons, 16);",
		"to->weapon = MSG_ReadDeltaKey( msg, key, from->weapon, 8);",
		"to->weaponPrimary = MSG_ReadDeltaKey( msg, key, from->weaponPrimary, 8);",
		"to->fov = MSG_ReadDeltaKey( msg, key, from->fov, 8);",
		"to->angles[0] = from->angles[0];",
		"to->weaponPrimary = from->weaponPrimary;",
		"to->fov = from->fov;",
	)

	write_hlil = hlil_part04.split("004d51a0    int32_t* sub_4d51a0", 1)[1].split("004d54a0", 1)[0]
	_assert_order(
		write_hlil,
		"if (*edi - *arg3 s>= 0x100)",
		"sub_4d4af0(arg1, 0, 1)",
		"var_20 = 0x20",
		"sub_4d4af0(arg1, 1, 1)",
		"var_20 = 8",
		"if (arg3[1] == edi[1] && arg3[2] == edi[2] && arg3[3] == edi[3])",
		"*(arg3 + 0x17)",
		"arg3[6].b",
		"*(arg3 + 0x19)",
		"arg3[4] == edi[4]",
		"arg3[5].b",
		"*(arg3 + 0x15)",
		"*(arg3 + 0x16)",
		"sub_4d4af0(arg1, 0, 1)",
		"int32_t ebx_2 = arg2 ^ *edi",
	)
	for expected in (
		"sub_4d4af0(arg1, eax_4 ^ ebx_2, 0x10)",
		"sub_4d4af0(arg1, eax_13 ^ ebx_2, 8)",
		"sub_4d4af0(arg1, eax_22 ^ ebx_2, 0x10)",
		"sub_4d4af0(arg1, eax_25 ^ ebx_2, 8)",
		"sub_4d4af0(arg1, eax_28 ^ ebx_2, 8)",
		"return sub_4d4af0(arg1, edi_1 ^ ebx_2, 8)",
	):
		assert expected in write_hlil

	read_hlil = hlil_part04.split("004d54a0    int32_t sub_4d54a0", 1)[1].split("004d5750", 1)[0]
	_assert_order(
		read_hlil,
		"if (sub_4d4c70(arg1, 1) == 0)",
		"eax_2 = sub_4d4c70(arg1, 0x20)",
		"eax_2 = sub_4d4c70(arg1, 8) + *arg3",
		"*arg4 = eax_2",
		"if (sub_4d4c70(arg1, 1) == 0)",
		"arg4[1] = *(arg3 + 4)",
		"*(arg4 + 0x17) = *(arg3 + 0x17)",
		"arg4[6].b = *(arg3 + 0x18)",
		"*(arg4 + 0x19) = *(arg3 + 0x19)",
		"arg4[5].b = *(arg3 + 0x14)",
		"*(arg4 + 0x15) = *(arg3 + 0x15)",
		"*(arg4 + 0x16) = eax_40",
	)
	_assert_order(
		read_hlil,
		"arg2 ^= *arg4",
		"arg4[1] = eax_7",
		"arg4[2] = eax_11",
		"arg4[3] = eax_14",
		"*(arg4 + 0x17) = eax_17",
		"arg4[6].b = eax_20",
		"*(arg4 + 0x19) = eax_23",
		"arg4[4] = eax_26",
		"arg4[5].b = eax_29",
		"*(arg4 + 0x15) = eax_32",
		"*(arg4 + 0x16) = eax_35",
	)
	assert "004b61d6                  sub_4d51a0" in hlil_part04
	assert "eax_16 * 0x1c + &data_1471ed0" in hlil_part04
	assert "004e0411          sub_4d54a0" in hlil_part04

	anchors = {item["symbol"]: item for item in spec["retail_anchors"]}
	assert anchors["MSG_WriteDeltaUsercmdKey"]["address"] == "0x004D51A0"
	assert anchors["MSG_ReadDeltaUsercmdKey"]["address"] == "0x004D54A0"
	assert anchors["CL_WritePacket"]["address"] == "0x004B5F70"
	assert anchors["SV_UserMove"]["address"] == "0x004E0320"

	assert spec["completion_status"]["status"] == "completed_static_struct_layout_and_logical_vectors"
	assert spec["completion_status"]["source_patch_required"] is False
	assert spec["completion_status"]["focused_task_parity_before_percent"] == 78
	assert spec["completion_status"]["focused_task_parity_after_percent"] == 94
	assert spec["completion_status"]["overall_network_protocol_parity_before_percent"] == 78
	assert spec["completion_status"]["overall_network_protocol_parity_after_percent"] == 80
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_usercmd_delta_struct_layout_and_logical_vectors" in spec["assertion_tests"]

	assert "Network Usercmd Delta Parity" in audit_note
	assert "focused `usercmd_t` delta slice `78%` -> `94%`" in audit_note
	assert "regular message payload bytes go through the adaptive Huffman bitstream layer" in audit_note
	assert "Finalize **usercmd_t delta parity**" in plan
	assert "network-usercmd-delta-parity-2026-06-05.json" in plan
	assert "focused `usercmd_t` delta slice" in plan


def test_networking_2_playerstate_fields_source_of_truth_and_roundtrip_contract() -> None:
	spec = _networking_2_playerstate_fields_spec()
	msg_c = _read(MSG_C_PATH)
	q_shared = _read(Q_SHARED_PATH)
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part06 = _read(HLIL_PART06_PATH)
	audit_note = _read(NETWORKING_2_PLAYERSTATE_FIELDS_AUDIT_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-protocol-parity-ledger-2026-06-05.json",
		"docs/reverse-engineering/network-protocol-header-transport-spec-2026-06-05.json",
		"docs/reverse-engineering/network-usercmd-delta-parity-2026-06-05.json",
	]
	assert spec["owning_retail_binary"]["path"] == "assets/quakelive/quakelive_steam.exe"

	entries = spec["source_of_truth"]["entries"]
	assert len(entries) == spec["retail_table"]["field_count"] == 0x3a
	assert spec["retail_table"]["base_address"] == "0x005424D8"
	assert spec["retail_table"]["entry_stride_bytes"] == 12
	assert spec["retail_table"]["read_copy_bytes"] == "0x250"
	assert [entry["index"] for entry in entries] == list(range(58))
	assert [
		int(entry["table_address"], 16)
		for entry in entries
	] == [0x5424D8 + index * 0x0C for index in range(58)]

	table_start = msg_c.index("netField_t\tplayerStateFields[]")
	table = msg_c[table_start:msg_c.index("};", table_start)]
	source_entries = re.findall(r"\{ PSF\(([^)]+)\), ([^ }]+) \}", table)
	spec_entries = [(entry["field"], entry["source_bits"]) for entry in entries]
	assert source_entries == spec_entries
	assert _netfield_count(msg_c, "playerStateFields") == 58
	_assert_order(
		table,
		"{ PSF(groundEntityNum), GENTITYNUM_BITS }",
		"{ PSF(weaponstate), 4 }",
		"{ PSF(loopSound), 16 }",
		"{ PSF(jumpTime), 32 }",
		"{ PSF(doubleJumped), 1 }",
		"{ PSF(crouchTime), 32 }",
	)

	class PlayerState(ctypes.Structure):
		_fields_ = [
			("commandTime", ctypes.c_int),
			("pm_type", ctypes.c_int),
			("bobCycle", ctypes.c_int),
			("pm_flags", ctypes.c_int),
			("pm_time", ctypes.c_int),
			("origin", ctypes.c_float * 3),
			("velocity", ctypes.c_float * 3),
			("weaponTime", ctypes.c_int),
			("gravity", ctypes.c_int),
			("speed", ctypes.c_int),
			("delta_angles", ctypes.c_int * 3),
			("groundEntityNum", ctypes.c_int),
			("legsTimer", ctypes.c_int),
			("legsAnim", ctypes.c_int),
			("torsoTimer", ctypes.c_int),
			("torsoAnim", ctypes.c_int),
			("movementDir", ctypes.c_int),
			("grapplePoint", ctypes.c_float * 3),
			("eFlags", ctypes.c_int),
			("eventSequence", ctypes.c_int),
			("events", ctypes.c_int * 2),
			("eventParms", ctypes.c_int * 2),
			("externalEvent", ctypes.c_int),
			("externalEventParm", ctypes.c_int),
			("clientNum", ctypes.c_int),
			("location", ctypes.c_int),
			("weapon", ctypes.c_int),
			("weaponPrimary", ctypes.c_int),
			("weaponstate", ctypes.c_int),
			("fov", ctypes.c_int),
			("viewangles", ctypes.c_float * 3),
			("viewheight", ctypes.c_int),
			("damageEvent", ctypes.c_int),
			("damageYaw", ctypes.c_int),
			("damagePitch", ctypes.c_int),
			("damageCount", ctypes.c_int),
			("stats", ctypes.c_int * 16),
			("persistant", ctypes.c_int * 16),
			("powerups", ctypes.c_int * 16),
			("ammo", ctypes.c_int * 16),
			("generic1", ctypes.c_int),
			("loopSound", ctypes.c_int),
			("jumppad_ent", ctypes.c_int),
			("jumpTime", ctypes.c_int),
			("doubleJumped", ctypes.c_int),
			("crouchTime", ctypes.c_int),
			("crouchSlideTime", ctypes.c_int),
			("forwardmove", ctypes.c_byte),
			("rightmove", ctypes.c_byte),
			("upmove", ctypes.c_byte),
			("commandMirrorPad", ctypes.c_byte),
			("ping", ctypes.c_int),
			("pmove_framecount", ctypes.c_int),
			("jumppad_frame", ctypes.c_int),
			("entityEventSequence", ctypes.c_int),
			("externalEventTime", ctypes.c_int),
			("armorTier", ctypes.c_int),
		]

	int_size = ctypes.sizeof(ctypes.c_int)
	float_size = ctypes.sizeof(ctypes.c_float)
	expected_offsets = {
		"commandTime": PlayerState.commandTime.offset,
		"origin[0]": PlayerState.origin.offset,
		"origin[1]": PlayerState.origin.offset + float_size,
		"bobCycle": PlayerState.bobCycle.offset,
		"velocity[0]": PlayerState.velocity.offset,
		"velocity[1]": PlayerState.velocity.offset + float_size,
		"viewangles[1]": PlayerState.viewangles.offset + float_size,
		"viewangles[0]": PlayerState.viewangles.offset,
		"weaponTime": PlayerState.weaponTime.offset,
		"origin[2]": PlayerState.origin.offset + float_size * 2,
		"velocity[2]": PlayerState.velocity.offset + float_size * 2,
		"legsTimer": PlayerState.legsTimer.offset,
		"pm_time": PlayerState.pm_time.offset,
		"eventSequence": PlayerState.eventSequence.offset,
		"torsoAnim": PlayerState.torsoAnim.offset,
		"movementDir": PlayerState.movementDir.offset,
		"events[0]": PlayerState.events.offset,
		"legsAnim": PlayerState.legsAnim.offset,
		"events[1]": PlayerState.events.offset + int_size,
		"pm_flags": PlayerState.pm_flags.offset,
		"groundEntityNum": PlayerState.groundEntityNum.offset,
		"weaponstate": PlayerState.weaponstate.offset,
		"eFlags": PlayerState.eFlags.offset,
		"externalEvent": PlayerState.externalEvent.offset,
		"gravity": PlayerState.gravity.offset,
		"speed": PlayerState.speed.offset,
		"delta_angles[1]": PlayerState.delta_angles.offset + int_size,
		"externalEventParm": PlayerState.externalEventParm.offset,
		"viewheight": PlayerState.viewheight.offset,
		"damageEvent": PlayerState.damageEvent.offset,
		"damageYaw": PlayerState.damageYaw.offset,
		"damagePitch": PlayerState.damagePitch.offset,
		"damageCount": PlayerState.damageCount.offset,
		"generic1": PlayerState.generic1.offset,
		"pm_type": PlayerState.pm_type.offset,
		"delta_angles[0]": PlayerState.delta_angles.offset,
		"delta_angles[2]": PlayerState.delta_angles.offset + int_size * 2,
		"torsoTimer": PlayerState.torsoTimer.offset,
		"eventParms[0]": PlayerState.eventParms.offset,
		"eventParms[1]": PlayerState.eventParms.offset + int_size,
		"clientNum": PlayerState.clientNum.offset,
		"weapon": PlayerState.weapon.offset,
		"weaponPrimary": PlayerState.weaponPrimary.offset,
		"viewangles[2]": PlayerState.viewangles.offset + float_size * 2,
		"grapplePoint[0]": PlayerState.grapplePoint.offset,
		"grapplePoint[1]": PlayerState.grapplePoint.offset + float_size,
		"grapplePoint[2]": PlayerState.grapplePoint.offset + float_size * 2,
		"jumppad_ent": PlayerState.jumppad_ent.offset,
		"loopSound": PlayerState.loopSound.offset,
		"jumpTime": PlayerState.jumpTime.offset,
		"doubleJumped": PlayerState.doubleJumped.offset,
		"crouchTime": PlayerState.crouchTime.offset,
		"crouchSlideTime": PlayerState.crouchSlideTime.offset,
		"location": PlayerState.location.offset,
		"fov": PlayerState.fov.offset,
		"forwardmove": PlayerState.forwardmove.offset,
		"rightmove": PlayerState.rightmove.offset,
		"upmove": PlayerState.upmove.offset,
	}
	assert {
		entry["field"]: int(entry["offset_hex"], 16)
		for entry in entries
	} == expected_offsets
	assert PlayerState.forwardmove.offset == 0x1DC
	assert PlayerState.commandMirrorPad.offset == 0x1DF
	assert PlayerState.ping.offset == 0x1E0

	playerstate_decl = q_shared[q_shared.index("typedef struct playerState_s {") : q_shared.index("} playerState_t;")]
	_assert_order(
		playerstate_decl,
		"int\t\t\tgeneric1;",
		"int\t\t\tloopSound;",
		"int\t\t\tjumppad_ent;",
		"int\t\t\tjumpTime;",
		"int\t\t\tdoubleJumped;",
		"int\t\t\tcrouchTime;",
		"int\t\t\tcrouchSlideTime;",
		"signed char\tforwardmove;",
	)

	hlil_lines = {
		line[:8].lower(): line
		for line in hlil_part06.splitlines()
		if re.match(r"^[0-9a-f]{8}\s", line)
	}
	for entry in entries:
		address = entry["table_address"].lower().removeprefix("0x")
		line = hlil_lines[address]
		if entry["field"] == "fov":
			assert line == "00542760  void* data_542760 = 0x53d0b0"
			assert "0053d0a9                             00 00 00 4e 41 00 00 66 6f 76 00" in hlil_part06
		else:
			assert f'{{"{entry["field"]}"}}' in line

	for expected in (
		"005425c0  0c 00 00 00 18 00 00 00",
		"00542728                          cc 01 00 00 20 00 00 00",
		"00542734                                                              d0 01 00 00 01 00 00 00",
		"00542764              9c 00 00 00 08 00 00 00",
		"00542770                                                  dc 01 00 00 08 00 00 00",
		"0054277c                                                                                      dd 01 00 00",
		"00542788                          de 01 00 00 08 00 00 00",
	):
		assert expected in hlil_part06

	write_hlil = hlil_part04.split("004d5d50    int32_t* sub_4d5d50", 1)[1].split("004d66c0", 1)[0]
	read_hlil = hlil_part04.split("004d66c0    uint32_t sub_4d66c0", 1)[1].split("004d6ba2", 1)[0]
	_assert_order(
		write_hlil,
		"void* const eax_2 = &data_5424e8",
		"int32_t i_15 = 0x1d",
		"sub_4d4af0(arg1, i_20, 8)",
		"void* const var_260 = &data_5424e0",
		"sub_4d4af0(arg1, *(ebx_1 + arg3), eax_7)",
		"sub_4d4af0(arg1, edi_3 + 0x1000, 0xd)",
		"sub_4d4af0(arg1, var_260_1, 0x10)",
		"sub_4d4af0(arg1, var_26c, 0x10)",
		"eax_47 = sub_4d4af0(arg1, var_268, 0x10)",
		"int32_t* eax_52 = sub_4d4af0(arg1, var_25c, 0x10)",
		"eax_52 = sub_4d4af0(arg1, *ebx_15, 0x20)",
	)
	_assert_order(
		read_hlil,
		"__builtin_memcpy(dest: arg4, src: arg3, n: 0x250)",
		"uint32_t i_12 = zx.d(sub_4d4c70(arg2, 8))",
		"void* const edi_1 = &data_5424e0",
		"if (i_12 s< 0x3a)",
		"int32_t i_11 = 0x3a - i_12",
		"void* ecx_10 = i_12 * 0xc + 0x5424dc",
		"char const* const var_280_5 = \"PS_STATS\"",
		"char const* const var_280_6 = \"PS_PERSISTANT\"",
		"char const* const var_280_7 = \"PS_AMMO\"",
		"char const* const var_280_8 = \"PS_POWERUPS\"",
	)

	assert spec["signed_byte_fields"] == ["forwardmove", "rightmove", "upmove"]
	signed_byte_block = _function_block(msg_c, "static qboolean MSG_PlayerStateFieldIsSignedByte")
	network_value_block = _function_block(msg_c, "static int MSG_PlayerStateFieldNetworkValue")
	set_value_block = _function_block(msg_c, "static void MSG_SetPlayerStateFieldValue")
	for field in spec["signed_byte_fields"]:
		assert f"field->offset == PSF_OFFSET({field})" in signed_byte_block
	assert "return (unsigned char)value;" in network_value_block
	assert "*(signed char *)( (byte *)ps + field->offset ) = (signed char)value;" in set_value_block

	array_masks = {mask["name"]: mask for mask in spec["array_masks"]}
	assert array_masks == {
		"stats": {"name": "stats", "mask_bits": 16, "value_bits": 16, "retail_offset_hex": "0x0c0"},
		"persistant": {"name": "persistant", "mask_bits": 16, "value_bits": 16, "retail_offset_hex": "0x100"},
		"ammo": {"name": "ammo", "mask_bits": 16, "value_bits": 16, "retail_offset_hex": "0x180"},
		"powerups": {"name": "powerups", "mask_bits": 16, "value_bits": 32, "retail_offset_hex": "0x140"},
	}
	assert PlayerState.stats.offset == 0x0C0
	assert PlayerState.persistant.offset == 0x100
	assert PlayerState.powerups.offset == 0x140
	assert PlayerState.ammo.offset == 0x180

	field_indices = {entry["field"]: entry["index"] for entry in entries}
	field_bits = {entry["field"]: entry["bits"] for entry in entries}
	vectors = {vector["id"]: vector for vector in spec["golden_vectors"]}
	assert set(vectors) == {
		"jump_time_tail_lc",
		"double_jump_tail_lc",
		"command_mirror_tail_lc",
		"pm_flags_24_bit",
		"origin0_integral_float",
	}
	for vector in vectors.values():
		changed_indices = [field_indices[field] for field in vector["changed_fields"]]
		assert vector["retail_zero_based_indices"] == changed_indices
		assert vector["expected_lc"] == (max(changed_indices) + 1 if changed_indices else 0)
		for event in vector["written_events"]:
			field = event["field"]
			if field in field_bits and event.get("changed", True):
				assert event["bits"] == field_bits[field]

	assert vectors["jump_time_tail_lc"]["expected_lc"] == 50
	assert vectors["double_jump_tail_lc"]["expected_lc"] == 51
	assert vectors["command_mirror_tail_lc"]["expected_lc"] == 58
	assert vectors["pm_flags_24_bit"]["written_events"][0] == {
		"field": "pm_flags",
		"bits": 24,
		"written_value": "0xabcdef",
	}
	command_events = {event["field"]: event for event in vectors["command_mirror_tail_lc"]["written_events"]}
	assert command_events["forwardmove"]["written_value"] == "0x81"
	assert command_events["forwardmove"]["decoded_signed_value"] == -127
	assert command_events["upmove"]["written_value"] == "0xf4"
	assert command_events["upmove"]["decoded_signed_value"] == -12
	assert vectors["origin0_integral_float"]["float_int_bias"] == 4096
	assert vectors["origin0_integral_float"]["float_int_bits"] == 13
	assert vectors["origin0_integral_float"]["written_events"][1]["written_value"] == 128 + 4096

	anchors = {item["symbol"]: item for item in spec["retail_anchors"]}
	assert anchors["MSG_WriteDeltaPlayerstate"]["address"] == "0x004D5D50"
	assert anchors["MSG_ReadDeltaPlayerstate"]["address"] == "0x004D66C0"
	assert anchors["playerStateFields"]["address"] == "0x005424D8"

	assert spec["retail_order_corrections"] == [
		{"field": "jumpTime", "previous_source_index": 21, "retail_index": 49, "source_patch_required": True},
		{"field": "doubleJumped", "previous_source_index": 22, "retail_index": 50, "source_patch_required": True},
	]
	assert spec["completion_status"]["status"] == "completed_source_patch_retail_table_source_of_truth"
	assert spec["completion_status"]["source_patch_required"] is True
	assert spec["completion_status"]["focused_task_parity_before_percent"] == 70
	assert spec["completion_status"]["focused_task_parity_after_percent"] == 94
	assert spec["completion_status"]["overall_network_protocol_parity_before_percent"] == 80
	assert spec["completion_status"]["overall_network_protocol_parity_after_percent"] == 82
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_playerstate_fields_source_of_truth_and_roundtrip_contract" in spec["assertion_tests"]

	assert "Network PlayerState Fields Parity" in audit_note
	assert "`jumpTime` and `doubleJumped` after `loopSound`" in audit_note
	assert "focused `playerStateFields` slice `70%` -> `94%`" in audit_note
	assert "Reconstruct **playerStateFields** exactly from retail" in plan
	assert "network-playerstate-fields-parity-2026-06-05.json" in plan
	assert "focused `playerStateFields` slice" in plan


def test_networking_2_entitystate_fields_source_of_truth_and_delta_contract() -> None:
	spec = _networking_2_entitystate_fields_spec()
	msg_c = _read(MSG_C_PATH)
	q_shared = _read(Q_SHARED_PATH)
	bg_misc = _read(REPO_ROOT / "src/code/game/bg_misc.c")
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part06 = _read(HLIL_PART06_PATH)
	audit_note = _read(NETWORKING_2_ENTITYSTATE_FIELDS_AUDIT_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-protocol-parity-ledger-2026-06-05.json",
		"docs/reverse-engineering/network-protocol-header-transport-spec-2026-06-05.json",
		"docs/reverse-engineering/network-playerstate-fields-parity-2026-06-05.json",
	]
	assert spec["owning_retail_binary"]["path"] == "assets/quakelive/quakelive_steam.exe"

	entries = spec["source_of_truth"]["entries"]
	assert len(entries) == spec["retail_table"]["field_count"] == 0x3a
	assert spec["retail_table"]["base_address"] == "0x00542220"
	assert spec["retail_table"]["entry_stride_bytes"] == 12
	assert spec["retail_table"]["read_copy_bytes"] == "0xec"
	assert [entry["index"] for entry in entries] == list(range(58))
	assert [
		int(entry["table_address"], 16)
		for entry in entries
	] == [0x542220 + index * 0x0C for index in range(58)]

	table_start = msg_c.index("netField_t\tentityStateFields[]")
	table = msg_c[table_start:msg_c.index("};", table_start)]
	source_entries = re.findall(r"\{ NETF\(([^)]+)\), ([^ }]+) \}", table)
	spec_entries = [(entry["field"], entry["source_bits"]) for entry in entries]
	assert source_entries == spec_entries
	assert _netfield_count(msg_c, "entityStateFields") == 58
	_assert_order(
		table,
		"{ NETF(apos.trBase[0]), 0 }",
		"{ NETF(pos.gravity), 32 }",
		"{ NETF(event), 10 }",
		"{ NETF(generic1), 8 }",
		"{ NETF(apos.trDelta[2]), 0 }",
		"{ NETF(apos.gravity), 32 }",
		"{ NETF(time2), 32 }",
		"{ NETF(jumpTime), 32 }",
		"{ NETF(doubleJumped), 1 }",
		"{ NETF(health), 16 }",
		"{ NETF(armor), 16 }",
		"{ NETF(location), 8 }",
	)
	assert "{ NETF(retailEventData), 8 }" not in table

	class Trajectory(ctypes.Structure):
		_fields_ = [
			("trType", ctypes.c_int),
			("trTime", ctypes.c_int),
			("trDuration", ctypes.c_int),
			("trBase", ctypes.c_float * 3),
			("trDelta", ctypes.c_float * 3),
			("gravity", ctypes.c_float),
		]

	class Generic1Slot(ctypes.Union):
		_fields_ = [
			("generic1", ctypes.c_int),
			("retailEventData", ctypes.c_int),
		]

	class EntityState(ctypes.Structure):
		_fields_ = [
			("number", ctypes.c_int),
			("eType", ctypes.c_int),
			("eFlags", ctypes.c_int),
			("pos", Trajectory),
			("apos", Trajectory),
			("time", ctypes.c_int),
			("time2", ctypes.c_int),
			("origin", ctypes.c_float * 3),
			("origin2", ctypes.c_float * 3),
			("angles", ctypes.c_float * 3),
			("angles2", ctypes.c_float * 3),
			("otherEntityNum", ctypes.c_int),
			("otherEntityNum2", ctypes.c_int),
			("groundEntityNum", ctypes.c_int),
			("constantLight", ctypes.c_int),
			("loopSound", ctypes.c_int),
			("modelindex", ctypes.c_int),
			("modelindex2", ctypes.c_int),
			("clientNum", ctypes.c_int),
			("frame", ctypes.c_int),
			("solid", ctypes.c_int),
			("event", ctypes.c_int),
			("eventParm", ctypes.c_int),
			("powerups", ctypes.c_int),
			("health", ctypes.c_int),
			("armor", ctypes.c_int),
			("weapon", ctypes.c_int),
			("location", ctypes.c_int),
			("legsAnim", ctypes.c_int),
			("torsoAnim", ctypes.c_int),
			("generic1Slot", Generic1Slot),
			("jumpTime", ctypes.c_int),
			("doubleJumped", ctypes.c_int),
		]

	int_size = ctypes.sizeof(ctypes.c_int)
	float_size = ctypes.sizeof(ctypes.c_float)
	assert ctypes.sizeof(Trajectory) == 0x28
	assert Trajectory.gravity.offset == 0x24
	assert ctypes.sizeof(EntityState) == int(spec["retail_table"]["read_copy_bytes"], 16) == 0xEC
	assert EntityState.generic1Slot.offset == 0xE0
	assert Generic1Slot.generic1.offset == Generic1Slot.retailEventData.offset == 0

	expected_offsets = {
		"pos.trTime": EntityState.pos.offset + Trajectory.trTime.offset,
		"pos.trBase[0]": EntityState.pos.offset + Trajectory.trBase.offset,
		"pos.trBase[1]": EntityState.pos.offset + Trajectory.trBase.offset + float_size,
		"pos.trDelta[0]": EntityState.pos.offset + Trajectory.trDelta.offset,
		"pos.trDelta[1]": EntityState.pos.offset + Trajectory.trDelta.offset + float_size,
		"pos.trBase[2]": EntityState.pos.offset + Trajectory.trBase.offset + float_size * 2,
		"apos.trBase[1]": EntityState.apos.offset + Trajectory.trBase.offset + float_size,
		"pos.trDelta[2]": EntityState.pos.offset + Trajectory.trDelta.offset + float_size * 2,
		"apos.trBase[0]": EntityState.apos.offset + Trajectory.trBase.offset,
		"pos.gravity": EntityState.pos.offset + Trajectory.gravity.offset,
		"event": EntityState.event.offset,
		"angles2[1]": EntityState.angles2.offset + float_size,
		"eType": EntityState.eType.offset,
		"torsoAnim": EntityState.torsoAnim.offset,
		"eventParm": EntityState.eventParm.offset,
		"legsAnim": EntityState.legsAnim.offset,
		"groundEntityNum": EntityState.groundEntityNum.offset,
		"pos.trType": EntityState.pos.offset + Trajectory.trType.offset,
		"eFlags": EntityState.eFlags.offset,
		"otherEntityNum": EntityState.otherEntityNum.offset,
		"weapon": EntityState.weapon.offset,
		"clientNum": EntityState.clientNum.offset,
		"angles[1]": EntityState.angles.offset + float_size,
		"pos.trDuration": EntityState.pos.offset + Trajectory.trDuration.offset,
		"apos.trType": EntityState.apos.offset + Trajectory.trType.offset,
		"origin[0]": EntityState.origin.offset,
		"origin[1]": EntityState.origin.offset + float_size,
		"origin[2]": EntityState.origin.offset + float_size * 2,
		"solid": EntityState.solid.offset,
		"powerups": EntityState.powerups.offset,
		"modelindex": EntityState.modelindex.offset,
		"otherEntityNum2": EntityState.otherEntityNum2.offset,
		"loopSound": EntityState.loopSound.offset,
		"generic1": EntityState.generic1Slot.offset,
		"origin2[2]": EntityState.origin2.offset + float_size * 2,
		"origin2[0]": EntityState.origin2.offset,
		"origin2[1]": EntityState.origin2.offset + float_size,
		"modelindex2": EntityState.modelindex2.offset,
		"angles[0]": EntityState.angles.offset,
		"time": EntityState.time.offset,
		"apos.trTime": EntityState.apos.offset + Trajectory.trTime.offset,
		"apos.trDuration": EntityState.apos.offset + Trajectory.trDuration.offset,
		"apos.trBase[2]": EntityState.apos.offset + Trajectory.trBase.offset + float_size * 2,
		"apos.trDelta[0]": EntityState.apos.offset + Trajectory.trDelta.offset,
		"apos.trDelta[1]": EntityState.apos.offset + Trajectory.trDelta.offset + float_size,
		"apos.trDelta[2]": EntityState.apos.offset + Trajectory.trDelta.offset + float_size * 2,
		"apos.gravity": EntityState.apos.offset + Trajectory.gravity.offset,
		"time2": EntityState.time2.offset,
		"angles[2]": EntityState.angles.offset + float_size * 2,
		"angles2[0]": EntityState.angles2.offset,
		"angles2[2]": EntityState.angles2.offset + float_size * 2,
		"constantLight": EntityState.constantLight.offset,
		"frame": EntityState.frame.offset,
		"jumpTime": EntityState.jumpTime.offset,
		"doubleJumped": EntityState.doubleJumped.offset,
		"health": EntityState.health.offset,
		"armor": EntityState.armor.offset,
		"location": EntityState.location.offset,
	}
	assert {
		entry["field"]: int(entry["offset_hex"], 16)
		for entry in entries
	} == expected_offsets

	entity_decl = q_shared[q_shared.index("typedef struct entityState_s {") : q_shared.index("} entityState_t;")]
	_assert_order(
		q_shared[q_shared.index("typedef struct {", q_shared.index("TR_QL_ACCEL")) : q_shared.index("} trajectory_t;")],
		"vec3_t\ttrDelta;",
		"float\tgravity;",
	)
	_assert_order(
		entity_decl,
		"int\t\teventParm;",
		"int\t\tpowerups;",
		"int\t\thealth;",
		"int\t\tarmor;",
		"int\t\tweapon;",
		"int\t\tlocation;",
		"int\t\tlegsAnim;",
		"int\t\ttorsoAnim;",
		"union {",
		"int\tgeneric1;",
		"int\tretailEventData;",
		"int\t\tjumpTime;",
		"int\t\tdoubleJumped;",
	)
	assert "int\t\tretailEventPadding[4];" not in entity_decl

	hlil_lines = {
		line[:8].lower(): line
		for line in hlil_part06.splitlines()
		if re.match(r"^[0-9a-f]{8}\s", line)
	}
	for entry in entries:
		address = entry["table_address"].lower().removeprefix("0x")
		assert f'{{"{entry["field"]}"}}' in hlil_lines[address]
	for expected in (
		"00542290                                                  30 00 00 00 20 00 00 00",
		"0054244c                                      58 00 00 00 20 00 00 00",
		"005423b0                                                  e0 00 00 00 08 00 00 00",
		"005424a0  e4 00 00 00 20 00 00 00",
		"005424ac                                      e8 00 00 00 01 00 00 00",
		"005424b8                                                                          c8 00 00 00 10 00 00 00",
		"005424c4              cc 00 00 00 10 00 00 00",
		"005424d0                                                  d4 00 00 00 08 00 00 00",
	):
		assert expected in hlil_part06

	write_hlil = hlil_part04.split("004d5780    int32_t* sub_4d5780", 1)[1].split("004d5ac0", 1)[0]
	read_hlil = hlil_part04.split("004d5ac0    int32_t sub_4d5ac0", 1)[1].split("004d5d50", 1)[0]
	_assert_order(
		write_hlil,
		"sub_4d4af0(arg1, *arg3, 0xa)",
		"result = sub_4d4af0(arg1, i_4, 8)",
		"data_124a634 += 0x3a",
		"if (i_4 s> 0)",
		"if (result != *(edi_3 + ebx_5))",
		"if (*var_8_1 == 0)",
		"sub_4d4af0(arg1, ebx_7 + 0x1000, 0xd)",
		"result = sub_4d4af0(arg1, *(edi_3 + ebx_5), *var_8_1)",
	)
	_assert_order(
		read_hlil,
		"__builtin_memcpy(dest: arg3, src: arg2, n: 0xec)",
		"uint32_t i_4 = zx.d(sub_4d4c70(ebx, 8))",
		"arg4 = &data_542228",
		"if (*arg4 != 0)",
		"eax_16 = sub_4d4c70(ebx, *arg4)",
		"else if (sub_4d4c70(ebx, 1) != 0)",
		"sub_4d4c70(ebx, 0xd) - 0x1000",
		"eax_4 = &(&data_542220)[i_4 * 3]",
		"if (i_4 s< 0x3a)",
	)

	trajectory_accel = _function_block(bg_misc, "static float BG_TrajectoryAcceleration( const trajectory_t *tr )")
	assert "return tr->gravity;" in trajectory_accel
	bridge = _function_block(bg_misc, "void BG_PlayerStateToEntityState( playerState_t *ps, entityState_t *s, qboolean snap )")
	for expected in (
		"s->pos.gravity = ps->gravity;",
		"s->apos.gravity = 0.0f;",
		"s->health = ps->stats[STAT_HEALTH];",
		"s->armor = ps->stats[STAT_ARMOR];",
		"s->location = ps->location;",
		"s->jumpTime = ps->jumpTime;",
		"s->doubleJumped = ps->doubleJumped;",
	):
		assert expected in bridge

	field_indices = {entry["field"]: entry["index"] for entry in entries}
	field_bits = {entry["field"]: entry["bits"] for entry in entries}
	vectors = {vector["id"]: vector for vector in spec["golden_vectors"]}
	assert set(vectors) == {
		"terminal_location_lc",
		"health_armor_tail_lc",
		"jump_state_tail_lc",
		"trajectory_gravity_lc",
		"generic1_alias_event_payload",
	}
	for vector in vectors.values():
		changed_indices = [field_indices[field] for field in vector["changed_fields"]]
		assert vector["retail_zero_based_indices"] == changed_indices
		assert vector["expected_lc"] == max(changed_indices) + 1
		for event in vector["written_events"]:
			assert event["bits"] == field_bits[event["field"]]
	assert vectors["terminal_location_lc"]["expected_lc"] == 58
	assert vectors["health_armor_tail_lc"]["expected_lc"] == 57
	assert vectors["jump_state_tail_lc"]["expected_lc"] == 55
	assert vectors["trajectory_gravity_lc"]["expected_lc"] == 47
	assert vectors["generic1_alias_event_payload"]["source_alias"] == "retailEventData"
	assert vectors["generic1_alias_event_payload"]["expected_lc"] == 34

	anchors = {item["symbol"]: item for item in spec["retail_anchors"]}
	assert anchors["MSG_WriteDeltaEntity"]["address"] == "0x004D5780"
	assert anchors["MSG_ReadDeltaEntity"]["address"] == "0x004D5AC0"
	assert anchors["entityStateFields"]["address"] == "0x00542220"

	corrections = {item["field"]: item for item in spec["retail_order_corrections"]}
	assert set(corrections) == {
		"pos.gravity",
		"apos.gravity",
		"jumpTime",
		"doubleJumped",
		"health",
		"armor",
		"location",
		"retailEventData",
	}
	assert corrections["retailEventData"]["resolution"] == "removed from the network table; retained as a source alias of retail generic1 at 0x0e0"
	assert spec["completion_status"]["status"] == "completed_source_patch_retail_table_source_of_truth"
	assert spec["completion_status"]["source_patch_required"] is True
	assert spec["completion_status"]["focused_task_parity_before_percent"] == 48
	assert spec["completion_status"]["focused_task_parity_after_percent"] == 92
	assert spec["completion_status"]["overall_network_protocol_parity_before_percent"] == 82
	assert spec["completion_status"]["overall_network_protocol_parity_after_percent"] == 84
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_entitystate_fields_source_of_truth_and_delta_contract" in spec["assertion_tests"]

	assert "Network EntityState Fields Parity" in audit_note
	assert "`pos.gravity` at index `9`" in audit_note
	assert "`location`-only delta emits retail `lc == 58`" in audit_note
	assert "focused `entityStateFields` slice `48%` -> `92%`" in audit_note
	assert "Reconstruct **entityStateFields** exactly from retail" in plan
	assert "network-entitystate-fields-parity-2026-06-05.json" in plan
	assert "focused `entityStateFields` slice" in plan


def test_networking_2_demo_capture_replay_validation_contract_and_semantic_diff_lanes() -> None:
	spec = _networking_2_replay_validation_spec()
	cl_parse = _read(CL_PARSE_PATH)
	sv_snapshot = _read(SV_SNAPSHOT_PATH)
	sv_net_chan = _read(SV_NET_CHAN_PATH)
	net_chan = _read(NET_CHAN_PATH)
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part05 = _read(HLIL_PART05_PATH)
	audit_note = _read(NETWORKING_2_REPLAY_VALIDATION_AUDIT_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-protocol-parity-ledger-2026-06-05.json",
		"docs/reverse-engineering/network-protocol-header-transport-spec-2026-06-05.json",
		"docs/reverse-engineering/network-client-message-parser-grammar-2026-06-05.json",
		"docs/reverse-engineering/network-xor-codec-parity-2026-06-05.json",
		"docs/reverse-engineering/network-usercmd-delta-parity-2026-06-05.json",
		"docs/reverse-engineering/network-playerstate-fields-parity-2026-06-05.json",
		"docs/reverse-engineering/network-entitystate-fields-parity-2026-06-05.json",
		"docs/reverse-engineering/network-oob-connect-auth-parity-2026-06-05.json",
	]
	assert spec["owning_retail_binary"]["path"] == "assets/quakelive/quakelive_steam.exe"

	lanes = {lane["id"]: lane for lane in spec["validation_lanes"]}
	assert set(lanes) == {
		"gamestate_baseline_replay",
		"snapshot_delta_replay",
		"packet_entity_merge_replay",
		"delta_aging_rejection",
		"fragment_reassembly_replay",
		"queued_fragment_send_replay",
		"capture_diff_report_contract",
	}
	assert lanes["gamestate_baseline_replay"]["retail_anchor"] == "0x004BD790"
	assert lanes["snapshot_delta_replay"]["retail_anchors"] == ["0x004E50E0", "0x004BD350"]
	assert lanes["packet_entity_merge_replay"]["retail_anchors"] == ["0x004E4FC0", "0x004BD000"]
	assert lanes["delta_aging_rejection"]["constants"]["stale_parse_entities_threshold"] == 1920
	assert lanes["delta_aging_rejection"]["constants"]["reject_when_difference_greater_than"] == 1920
	assert lanes["fragment_reassembly_replay"]["source_owner"] == "Netchan_Process"
	assert lanes["queued_fragment_send_replay"]["retail_anchors"] == ["0x004E4EE0", "0x004E4E20"]
	assert lanes["capture_diff_report_contract"]["diff_report_columns"] == [
		"fixtureId",
		"fixtureType",
		"laneId",
		"expectedHash",
		"actualHash",
		"matchKind",
		"status",
	]

	vectors = {vector["id"]: vector for vector in spec["semantic_replay_vectors"]}
	assert set(vectors) == {
		"gamestate_baseline_from_nullstate",
		"snapshot_uncompressed_baseline",
		"snapshot_valid_delta",
		"stale_delta_parse_entities_reject",
		"packet_entities_merge_cases",
		"fragmented_message_final_reassembly",
		"queued_fragment_xor_timing",
	}
	assert vectors["snapshot_uncompressed_baseline"]["expected_steps"] == [
		"newSnap.deltaNum becomes -1",
		"old snapshot pointer is NULL",
		"clc.demowaiting is cleared",
		"MSG_ReadDeltaPlayerstate uses NULL baseline",
		"CL_ParsePacketEntities uses entity baselines for new entities",
	]
	assert vectors["stale_delta_parse_entities_reject"]["input_shape"].endswith("is 1921")
	assert vectors["fragmented_message_final_reassembly"]["expected_steps"][-1] == "msg->readcount becomes 4 and msg->bit becomes 32"
	assert vectors["queued_fragment_xor_timing"]["expected_outcome"] == "queued datagram bytes are encoded with send-time sequence and command-string state"

	parse_gamestate = _function_block(cl_parse, "void CL_ParseGamestate")
	_assert_order(
		parse_gamestate,
		"CL_ClearState();",
		"clc.serverCommandSequence = MSG_ReadLong( msg );",
		"cl.gameState.dataCount = 1;",
		"cmd = MSG_ReadByte( msg );",
		"if ( cmd == svc_EOF ) {",
		"if ( cmd == svc_configstring ) {",
		"i = MSG_ReadShort( msg );",
		"s = MSG_ReadBigString( msg );",
		"cl.gameState.stringOffsets[ i ] = cl.gameState.dataCount;",
		"} else if ( cmd == svc_baseline ) {",
		"newnum = MSG_ReadBits( msg, GENTITYNUM_BITS );",
		"Com_Memset (&nullstate, 0, sizeof(nullstate));",
		"es = &cl.entityBaselines[ newnum ];",
		"MSG_ReadDeltaEntity( msg, &nullstate, es, newnum );",
		"clc.clientNum = MSG_ReadLong(msg);",
		"clc.checksumFeed = MSG_ReadLong( msg );",
		"CL_SystemInfoChanged();",
		"FS_ConditionalRestart( clc.checksumFeed );",
		"CL_InitDownloads();",
	)

	parse_snapshot = _function_block(cl_parse, "void CL_ParseSnapshot")
	_assert_order(
		parse_snapshot,
		"newSnap.serverCommandNum = clc.serverCommandSequence;",
		"newSnap.serverTime = MSG_ReadLong( msg );",
		"newSnap.messageNum = clc.serverMessageSequence;",
		"deltaNum = MSG_ReadByte( msg );",
		"if ( !deltaNum ) {",
		"newSnap.deltaNum = -1;",
		"newSnap.snapFlags = MSG_ReadByte( msg );",
		"if ( newSnap.deltaNum <= 0 ) {",
		"old = NULL;",
		"clc.demowaiting = qfalse;",
		"old = &cl.snapshots[newSnap.deltaNum & PACKET_MASK];",
		"if ( !old->valid ) {",
		"old->messageNum != newSnap.deltaNum",
		"cl.parseEntitiesNum - old->parseEntitiesNum > MAX_PARSE_ENTITIES-128",
		"len = MSG_ReadByte( msg );",
		"MSG_ReadData( msg, &newSnap.areamask, len);",
		"MSG_ReadDeltaPlayerstate( msg, &old->ps, &newSnap.ps );",
		"MSG_ReadDeltaPlayerstate( msg, NULL, &newSnap.ps );",
		"CL_ParsePacketEntities( msg, old, &newSnap );",
		"if ( !newSnap.valid ) {",
		"return;",
		"cl.snap = newSnap;",
		"cl.snapshots[cl.snap.messageNum & PACKET_MASK] = cl.snap;",
	)
	for expected in (
		"Delta from invalid frame (not supposed to happen!).\\n",
		"Delta frame too old.\\n",
		"Delta parseEntitiesNum too old.\\n",
	):
		assert expected in parse_snapshot

	delta_entity = _function_block(cl_parse, "void CL_DeltaEntity")
	_assert_order(
		delta_entity,
		"state = &cl.parseEntities[cl.parseEntitiesNum & (MAX_PARSE_ENTITIES-1)];",
		"if ( unchanged ) {",
		"*state = *old;",
		"MSG_ReadDeltaEntity( msg, old, state, newnum );",
		"if ( state->number == (MAX_GENTITIES-1) ) {",
		"return;",
		"cl.parseEntitiesNum++;",
		"frame->numEntities++;",
	)

	parse_entities = _function_block(cl_parse, "void CL_ParsePacketEntities")
	_assert_order(
		parse_entities,
		"newframe->parseEntitiesNum = cl.parseEntitiesNum;",
		"newnum = MSG_ReadBits( msg, GENTITYNUM_BITS );",
		"if ( newnum == (MAX_GENTITIES-1) ) {",
		"if ( msg->readcount > msg->cursize ) {",
		"while ( oldnum < newnum ) {",
		"CL_DeltaEntity( msg, newframe, oldnum, oldstate, qtrue );",
		"if (oldnum == newnum) {",
		"CL_DeltaEntity( msg, newframe, newnum, oldstate, qfalse );",
		"if ( oldnum > newnum ) {",
		"CL_DeltaEntity( msg, newframe, newnum, &cl.entityBaselines[newnum], qfalse );",
		"while ( oldnum != 99999 ) {",
		"CL_DeltaEntity( msg, newframe, oldnum, oldstate, qtrue );",
	)

	sv_emit = _function_block(sv_snapshot, "static void SV_EmitPacketEntities")
	_assert_order(
		sv_emit,
		"if ( !from ) {",
		"from_num_entities = 0;",
		"while ( newindex < to->num_entities || oldindex < from_num_entities ) {",
		"if ( newnum == oldnum ) {",
		"MSG_WriteDeltaEntity (msg, oldent, newent, qfalse );",
		"if ( newnum < oldnum ) {",
		"MSG_WriteDeltaEntity (msg, &sv.svEntities[newnum].baseline, newent, qtrue );",
		"if ( newnum > oldnum ) {",
		"MSG_WriteDeltaEntity (msg, oldent, NULL, qtrue );",
		"MSG_WriteBits( msg, (MAX_GENTITIES-1), GENTITYNUM_BITS );",
	)

	sv_write = _function_block(sv_snapshot, "static void SV_WriteSnapshotToClient")
	_assert_order(
		sv_write,
		"frame = &client->frames[ client->netchan.outgoingSequence & PACKET_MASK ];",
		"if ( client->deltaMessage <= 0 || client->state != CS_ACTIVE ) {",
		"oldframe = NULL;",
		"lastframe = 0;",
		"oldframe = &client->frames[ client->deltaMessage & PACKET_MASK ];",
		"lastframe = client->netchan.outgoingSequence - client->deltaMessage;",
		"MSG_WriteByte (msg, svc_snapshot);",
		"MSG_WriteLong (msg, svs.time);",
		"MSG_WriteByte (msg, lastframe);",
		"MSG_WriteByte (msg, snapFlags);",
		"MSG_WriteByte (msg, frame->areabytes);",
		"MSG_WriteData (msg, frame->areabits, frame->areabytes);",
		"MSG_WriteDeltaPlayerstate( msg, &oldframe->ps, &frame->ps );",
		"MSG_WriteDeltaPlayerstate( msg, NULL, &frame->ps );",
		"SV_EmitPacketEntities (oldframe, frame, msg);",
	)

	process = _function_block(net_chan, "qboolean Netchan_Process( netchan_t *chan, msg_t *msg )")
	_assert_order(
		process,
		"MSG_BeginReadingOOB( msg );",
		"sequence = MSG_ReadLong( msg );",
		"if ( sequence & FRAGMENT_BIT ) {",
		"sequence &= ~FRAGMENT_BIT;",
		"if ( chan->sock == NS_SERVER && NET_ProtocolUsesNetchanClientQport() ) {",
		"(void)MSG_ReadShort( msg );",
		"if ( fragmented ) {",
		"fragmentStart = MSG_ReadShort( msg );",
		"fragmentLength = MSG_ReadShort( msg );",
		"if ( sequence <= chan->incomingSequence ) {",
		"return qfalse;",
		"chan->dropped = sequence - (chan->incomingSequence+1);",
		"if ( fragmented ) {",
		"if ( sequence != chan->fragmentSequence ) {",
		"chan->fragmentSequence = sequence;",
		"chan->fragmentLength = 0;",
		"if ( fragmentStart != chan->fragmentLength ) {",
		"return qfalse;",
		"if ( fragmentLength < 0 || msg->readcount + fragmentLength > msg->cursize ||",
		"return qfalse;",
		"Com_Memcpy( chan->fragmentBuffer + chan->fragmentLength,",
		"chan->fragmentLength += fragmentLength;",
		"if ( fragmentLength == FRAGMENT_SIZE ) {",
		"return qfalse;",
		"*(int *)msg->data = LittleLong( sequence );",
		"Com_Memcpy( msg->data + 4, chan->fragmentBuffer, chan->fragmentLength );",
		"msg->cursize = chan->fragmentLength + 4;",
		"msg->readcount = 4;",
		"msg->bit = 32;",
		"chan->incomingSequence = sequence;",
		"return qtrue;",
	)

	sv_transmit = sv_net_chan.split("void SV_Netchan_Transmit( client_t *client, msg_t *msg)", 1)[1].split(
		"/*\n=================\nNetchan_SV_Process",
		1,
	)[0]
	_assert_order(
		sv_transmit,
		"MSG_WriteByte( msg, svc_EOF );",
		"if (client->netchan.unsentFragments) {",
		"MSG_Copy(&netbuf->msg, netbuf->msgBuffer, sizeof( netbuf->msgBuffer ), msg);",
		"*client->netchan_end_queue = netbuf;",
		"client->netchan_end_queue = &(*client->netchan_end_queue)->next;",
		"Netchan_TransmitNextFragment(&client->netchan);",
		"if ( NET_ProtocolUsesReliableXorCodec() ) {",
		"SV_Netchan_Encode( client, msg );",
		"Netchan_Transmit( &client->netchan, msg->cursize, msg->data );",
	)
	assert "we can't store it encoded, as the encoding depends on stuff we still have to finish sending" in sv_transmit

	sv_next_fragment = _function_block(sv_net_chan, "void SV_Netchan_TransmitNextFragment( client_t *client )")
	_assert_order(
		sv_next_fragment,
		"Netchan_TransmitNextFragment( &client->netchan );",
		"if (!client->netchan.unsentFragments)",
		"if (client->netchan_start_queue) {",
		"netbuf = client->netchan_start_queue;",
		"if ( NET_ProtocolUsesReliableXorCodec() ) {",
		"SV_Netchan_Encode( client, &netbuf->msg );",
		"Netchan_Transmit( &client->netchan, netbuf->msg.cursize, netbuf->msg.data );",
		"client->netchan_start_queue = netbuf->next;",
		"client->netchan_end_queue = &client->netchan_start_queue;",
		"Z_Free(netbuf);",
	)

	parse_entities_hlil = hlil_part04.split("004bd000    uint32_t sub_4bd000", 1)[1].split("004bd350", 1)[0]
	_assert_order(
		parse_entities_hlil,
		"uint32_t i = sub_4d4c70(esi, 0xa)",
		"if (i_4 != 0x3ff)",
		"CL_ParsePacketEntities: end of m",
		"\"%3i:  unchanged: %i\\n\"",
		"sub_4d5ac0(arg1, ebx, esi_5, i_4)",
		"\"%3i:  baseline: %i\\n\"",
		"sub_4d5ac0(arg1, i_4 * 0xec + &data_1477b74, esi_9, i_4)",
	)

	parse_snapshot_hlil = hlil_part04.split("004bd350    uint32_t sub_4bd350", 1)[1].split("004bd790", 1)[0]
	_assert_order(
		parse_snapshot_hlil,
		"uint32_t var_298 = sub_4d5020(arg1)",
		"uint32_t eax_4 = sub_4d4fc0(arg1)",
		"var_290 = eax_3 - eax_4",
		"Delta frame too old.\\n",
		"data_1471e98 - esi[0xa4] s<= 0x780",
		"Delta parseEntitiesNum too old.\\n",
		"sub_4d5160(arg1, &var_288, eax_7)",
		"sub_4d66c0(esi, arg1, var_2b0_4, var_2ac_8)",
		"uint32_t result = sub_4bd000(arg1, esi, &var_2a0)",
	)

	parse_gamestate_hlil = hlil_part04.split("004bd790    int32_t* sub_4bd790", 1)[1].split("004bda00", 1)[0]
	_assert_order(
		parse_gamestate_hlil,
		"sub_4b4930()",
		"sub_4b8920()",
		"data_1606b80 = sub_4d5020(arg1)",
		"for (uint32_t i = sub_4d4fc0(arg1); i != 8; i = sub_4d4fc0(arg1))",
		"CL_ParseGamestate: bad command b",
		"void* eax_9 = sub_4d4c70(arg1, 0xa)",
		"Baseline number out of range: %i",
		"memset(&var_174, 0, 0xec)",
		"sub_4d5ac0(arg1, &var_174, eax_9 * 0xec + &data_1477b74, eax_9)",
	)

	sv_emit_hlil = hlil_part05.split("004e4fc0    int32_t* sub_4e4fc0", 1)[1].split("004e50e0", 1)[0]
	_assert_order(
		sv_emit_hlil,
		"if (arg1 != 0)",
		"if (ecx_2 == eax_7)",
		"sub_4d5780(arg3, edi, esi, 0)",
		"else if (ecx_2 s< eax_7)",
		"sub_4d5780(arg3, ecx_2 * 0x148 + &data_12e176c, esi, 1)",
		"else if (ecx_2 s> eax_7)",
		"sub_4d5780(arg3, edi, nullptr, 1)",
	)
	assert "return sub_4d4af0(arg3, 0x3ff, 0xa)" in sv_emit_hlil

	sv_write_hlil = hlil_part05.split("004e50e0    void* __convention", 1)[1].split("004e5680", 1)[0]
	_assert_order(
		sv_write_hlil,
		"sub_4d4dc0(arg2, 7)",
		"sub_4d4e30(arg2, eax_6)",
		"sub_4d4dc0(arg2, var_8_1)",
		"sub_4d4dc0(arg2, eax_7)",
		"sub_4d4dc0(arg2, arg1[(eax & 0x1f) * 0xa2 + 0x4274])",
		"sub_4d4de0(arg2, &arg1[(eax & 0x1f) * 0xa2 + 0x4275], arg1[(eax & 0x1f) * 0xa2 + 0x4274])",
		"sub_4d5d50(arg2, var_1c_6, var_18_6)",
		"sub_4e4fc0(ebx, &arg1[(eax & 0x1f) * 0xa2 + 0x4274], arg2)",
	)

	process_hlil = hlil_part04.split("004d7640    int32_t sub_4d7640", 1)[1].split("004d7970", 1)[0]
	_assert_order(
		process_hlil,
		"sub_4d4a80(arg5)",
		"uint32_t ebx_1 = sub_4d5020(arg5)",
		"ebx_1 &= 0x7fffffff",
		"if (*esi == 1)",
		"var_c = sub_4d4ff0(arg5)",
		"eax_2 = sub_4d4ff0(arg5)",
		"if (ebx_1 s> ecx_2)",
		"if (var_c != ecx_7)",
		"\"%s:Dropped a message fragment\\n\"",
		"\"%s:illegal fragment length\\n\"",
		"sub_4cb7d0(ecx_7 + esi + 0x30, *(arg5 + 8) + *(arg5 + 0x14), eax_2)",
		"**(arg5 + 8) = ebx_1",
		"sub_4cb7d0(*(arg5 + 8) + 4, &esi[0xc], esi[0xb])",
		"*(arg5 + 0x10) = esi[0xb] + 4",
		"*(arg5 + 0x14) = 4",
		"*(arg5 + 0x18) = 0x20",
	)

	queue_next_hlil = hlil_part05.split("004e4e20    int32_t sub_4e4e20", 1)[1].split("004e4ee0", 1)[0]
	_assert_order(
		queue_next_hlil,
		"sub_4d7370(arg1 + 0x15ae4)",
		"if (*(arg1 + 0x1db14) == 0)",
		"if (*(arg1 + 0x25b20) != 0)",
		"char* esi_1 = *(arg1 + 0x25b20)",
		"sub_4e4cd0(esi_1, arg1)",
		"sub_4d74e0(arg1 + 0x15ae4, *(esi_1 + 0x10), *(esi_1 + 8))",
		"*(arg1 + 0x25b20) = eax_3",
	)

	queue_transmit_hlil = hlil_part05.split("004e4ee0    int32_t sub_4e4ee0", 1)[1].split("004e4f80", 1)[0]
	assert "sub_4d4dc0(arg2, 8)" in queue_transmit_hlil
	assert "sub_4e4cd0(arg2, arg1)" in queue_transmit_hlil
	assert "return sub_4d74e0(arg1 + 0x15ae4, arg2[4], arg2[2])" in queue_transmit_hlil
	assert "sub_4d4aa0(eax, eax + 0x1c, 0x8000, arg2)" in queue_transmit_hlil
	assert "return sub_4d7370(arg1 + 0x15ae4)" in queue_transmit_hlil

	anchors = {item["symbol"]: item for item in spec["retail_anchors"]}
	assert anchors["CL_ParsePacketEntities"]["address"] == "0x004BD000"
	assert anchors["CL_ParseSnapshot"]["address"] == "0x004BD350"
	assert anchors["CL_ParseGamestate"]["address"] == "0x004BD790"
	assert anchors["Netchan_Process"]["address"] == "0x004D7640"
	assert anchors["SV_Netchan_TransmitNextFragment"]["address"] == "0x004E4E20"
	assert anchors["SV_Netchan_Transmit"]["address"] == "0x004E4EE0"
	assert anchors["SV_EmitPacketEntities"]["address"] == "0x004E4FC0"
	assert anchors["SV_WriteSnapshotToClient"]["address"] == "0x004E50E0"

	capture_status = spec["capture_diff_status"]
	assert capture_status["status"] == "semantic_replay_contract_and_static_assertions_added"
	assert capture_status["external_retail_captures_available"] is False
	assert capture_status["byte_for_byte_replay_available"] is False
	assert capture_status["semantic_diff_report_ready"] is True
	known_fixtures = {fixture["fixture_id"]: fixture for fixture in capture_status["current_known_good_fixtures"]}
	assert set(known_fixtures) == {"retail_duel_semantic_netdump"}
	assert known_fixtures["retail_duel_semantic_netdump"] == {
		"fixture_id": "retail_duel_semantic_netdump",
		"fixture_type": "semantic_snapshot_netdump",
		"path": "tests/netdumps/retail_duel.snap.json",
		"baseline": "tools/tests/client_regression/retail_netdump_baseline.json",
		"source": "retail-qzdm6",
		"map": "tritoxin",
		"frame_count": 3,
		"coverage": [
			"ordered retail snapshot frames",
			"HUD hash replay",
			"usercmd hash replay",
		],
		"byte_for_byte_packet_fixture": False,
	}
	assert "fragmented server-message capture with a queued follow-up message" in capture_status["required_future_fixture_sources"]

	assert spec["completion_status"]["status"] == "completed_static_replay_contract_and_semantic_diff_ready"
	assert spec["completion_status"]["source_patch_required"] is False
	assert spec["completion_status"]["runtime_launch_required"] is False
	assert spec["completion_status"]["focused_task_parity_before_percent"] == 45
	assert spec["completion_status"]["focused_task_parity_after_percent"] == 78
	assert spec["completion_status"]["overall_network_protocol_parity_before_percent"] == 85
	assert spec["completion_status"]["overall_network_protocol_parity_after_percent"] == 86
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_demo_capture_replay_validation_contract_and_semantic_diff_lanes" in spec["assertion_tests"]

	assert "Network Demo/Capture Replay Validation" in audit_note
	assert "semantic diff lanes" in audit_note
	assert "`tests/netdumps/retail_duel.snap.json`" in audit_note
	assert "semantic snapshot evidence" in audit_note
	assert "Queued fragment send replay" in audit_note
	assert "Focused demo/capture replay validation slice: `45%` before, `78%` after." in audit_note
	assert "Build **demo/capture replay validation**" in plan
	assert "network-demo-capture-replay-validation-2026-06-05.json" in plan
	assert "focused demo/capture replay validation slice" in plan


def test_residual_policy_spot_check_guardrails_remain_manifest_backed() -> None:
	spec = _residual_policy_spot_check_spec()
	note = _read(RESIDUAL_POLICY_SPOT_CHECK_AUDIT_PATH)
	checklist = _read(OUTSTANDING_WORK_CHECKLIST_PATH)
	platform_config = _read(PLATFORM_CONFIG_PATH)
	platform_services = _read(PLATFORM_SERVICES_PATH)
	qcommon_h = _read(QCOMMON_H_PATH)
	cl_main = _read(CL_MAIN_PATH)
	sv_main = _read(SV_MAIN_PATH)
	ownerdraw_index = _read(UI_OWNERDRAWTYPE_PARITY_INDEX_PATH)
	platform_steamworks = _read(REPO_ROOT / "src/common/platform/platform_steamworks.c")
	backend_steamworks = _read(REPO_ROOT / "src/common/platform/backends/platform_backend_steamworks.c")
	backend_open_steam = _read(REPO_ROOT / "src/common/platform/backends/platform_backend_open_steam.c")
	cl_awesomium = _read(REPO_ROOT / "src/code/client/cl_awesomium_win32.cpp")
	awesomium_process = _read(REPO_ROOT / "src/code/win32/awesomium_process.cpp")
	cl_steam_resources = _read(REPO_ROOT / "src/code/client/cl_steam_resources.c")
	auth_credentials = _read(REPO_ROOT / "src/common/auth_credentials.c")
	backend_auth = _read(REPO_ROOT / "src/common/platform/platform_backend_auth.h")
	platform_steamworks_h = _read(REPO_ROOT / "src/common/platform/platform_steamworks.h")
	win_net = _read(WIN_NET_PATH)
	common_c = _read(COMMON_C_PATH)

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["scope"] == "residual_policy_and_planning_checks"
	assert spec["status"] == "dated_spot_check_complete_manifest_guard_added_policy_callsite_inventory_added"
	assert spec["runtime_launch_required"] is False
	assert spec["game_launch_required"] is False
	assert spec["source_files"] == [
		"docs/reverse-engineering/residual-policy-spot-check-2026-06-05.json",
		"docs/reverse-engineering/residual-policy-spot-check-2026-06-05.md",
		"docs/plans/2026-06-05-outstanding-work-checklist.md",
		"tests/test_netcode_parity_manifest.py",
	]

	online = spec["online_services"]
	assert online["spot_check_result"] == "No policy drift found in the default source path."
	assert online["observed_facts"] == [
		"src/common/platform/platform_config.h defaults QL_BUILD_ONLINE_SERVICES to 0.",
		"When QL_BUILD_ONLINE_SERVICES is false, platform_config.h forces QL_BUILD_STEAMWORKS and QL_BUILD_OPEN_STEAM to 0.",
		"QL_BuildServiceTable publishes Build-disabled (QL_BUILD_ONLINE_SERVICES=0) descriptors for auth, matchmaking, workshop, overlay, and stats in the default build.",
		"Legacy Q3 service calls remain guarded by QL_PLATFORM_HAS_ONLINE_SERVICES && QL_ENABLE_LEGACY_Q3_SERVICES.",
		"Known Steamworks, open-adapter, Awesomium, and Steam-resource bridge lanes are inventoried and guarded by compile-time or runtime policy checks.",
		"Online-service call sites in auth, common startup/frame, client Steam frame/init, and Windows net restart route through compile-time stubs or CL_SteamServicesEnabled runtime checks in the default build.",
	]
	_assert_order(
		platform_config,
		"#ifndef QL_BUILD_ONLINE_SERVICES",
		"#define QL_BUILD_ONLINE_SERVICES 0",
		"#if !QL_BUILD_ONLINE_SERVICES",
		"#undef QL_BUILD_STEAMWORKS",
		"#define QL_BUILD_STEAMWORKS 0",
		"#undef QL_BUILD_OPEN_STEAM",
		"#define QL_BUILD_OPEN_STEAM 0",
	)
	assert "#if !QL_PLATFORM_HAS_ONLINE_SERVICES" in platform_config
	assert "#undef QL_ENABLE_LEGACY_Q3_SERVICES" in platform_config
	assert "#define QL_ENABLE_LEGACY_Q3_SERVICES 0" in platform_config
	for feature in ("auth", "matchmaking", "workshop", "overlay", "stats"):
		assert f'table.{feature}.provider = "Build-disabled (QL_BUILD_ONLINE_SERVICES=0)";' in platform_services
	legacy_guard = "#if QL_PLATFORM_HAS_ONLINE_SERVICES && QL_ENABLE_LEGACY_Q3_SERVICES"
	assert legacy_guard in qcommon_h
	assert legacy_guard in cl_main
	assert legacy_guard in sv_main

	lane_inventory = {lane["lane_id"]: lane for lane in online["policy_lane_inventory"]}
	assert lane_inventory == {
		"steamworks_platform_wrapper": {
			"lane_id": "steamworks_platform_wrapper",
			"path": "src/common/platform/platform_steamworks.c",
			"gate": "#if QL_BUILD_STEAMWORKS",
			"classification": "opt-in compile-time Steamworks compatibility lane",
		},
		"steamworks_auth_backend": {
			"lane_id": "steamworks_auth_backend",
			"path": "src/common/platform/backends/platform_backend_steamworks.c",
			"gate": "#if QL_BUILD_STEAMWORKS",
			"classification": "opt-in compile-time Steamworks auth backend",
		},
		"open_steam_auth_backend": {
			"lane_id": "open_steam_auth_backend",
			"path": "src/common/platform/backends/platform_backend_open_steam.c",
			"gate": "#if QL_BUILD_OPEN_STEAM",
			"classification": "opt-in compile-time open-adapter auth backend",
		},
		"awesomium_host_adapter": {
			"lane_id": "awesomium_host_adapter",
			"path": "src/code/client/cl_awesomium_win32.cpp",
			"gate": "#if QL_BUILD_ONLINE_SERVICES",
			"classification": "opt-in compile-time Windows Awesomium compatibility lane",
		},
		"awesomium_child_process": {
			"lane_id": "awesomium_child_process",
			"path": "src/code/win32/awesomium_process.cpp",
			"gate": "#if QL_PLATFORM_HAS_ONLINE_SERVICES",
			"classification": "build-policy-gated Awesomium child-process lane",
		},
		"steam_resource_uri_bridge": {
			"lane_id": "steam_resource_uri_bridge",
			"path": "src/code/client/cl_steam_resources.c",
			"gate": "CL_SteamServicesEnabled runtime checks before live Steam avatar callbacks and requests",
			"classification": "compiled launcher fallback bridge with live Steam requests runtime-gated",
		},
	}
	assert "#if QL_BUILD_STEAMWORKS" in platform_steamworks
	assert "#if QL_BUILD_STEAMWORKS" in backend_steamworks
	assert "#if QL_BUILD_OPEN_STEAM" in backend_open_steam
	_assert_order(
		cl_awesomium,
		"#ifndef QL_BUILD_ONLINE_SERVICES",
		"#define QL_BUILD_ONLINE_SERVICES 0",
		"#if QL_BUILD_ONLINE_SERVICES",
	)
	_assert_order(
		awesomium_process,
		"#include \"platform/platform_config.h\"",
		"#ifndef QL_AWESOMIUM_USE_SDK",
		"#define QL_AWESOMIUM_USE_SDK 0",
		"#if QL_PLATFORM_HAS_ONLINE_SERVICES && QL_AWESOMIUM_USE_SDK",
		"#include <Awesomium/ChildProcess.h>",
		"#if QL_PLATFORM_HAS_ONLINE_SERVICES && !QL_AWESOMIUM_USE_SDK",
		"QLR_AWESOMIUM_CHILDPROCESSMAIN_DYNAMIC",
	)
	avatar_callbacks = _function_block(cl_steam_resources, "static void CL_SteamResources_RegisterAvatarCallbacks")
	_assert_order(
		avatar_callbacks,
		"if ( cl_steamAvatarCallbacksRegistered || !CL_SteamServicesEnabled() ) {",
		"return;",
		"QL_Steamworks_RegisterAvatarCallbacks( &bindings )",
	)
	steam_data_request = _function_block(cl_steam_resources, "static qboolean CL_SteamDataSource_Request")
	_assert_order(
		steam_data_request,
		"if ( CL_SteamResources_IsAvatarURL( url ) ) {",
		"if ( !CL_SteamServicesEnabled() ) {",
		"return qfalse;",
		"CL_SteamResources_RequestAvatarRGBA( url, &response->rgbaPixels, &response->width, &response->height )",
	)
	steam_register_shader = _function_block(cl_steam_resources, "qhandle_t CL_Steam_RegisterShader")
	_assert_order(
		steam_register_shader,
		"if ( CL_SteamResources_IsSteamURL( url ) ) {",
		"if ( !CL_SteamServicesEnabled() ) {",
		"return 0;",
		"CL_SteamResources_RequestAvatarRGBA( url, &rgbaPixels, &width, &height )",
	)
	callsite_inventory = {lane["lane_id"]: lane for lane in online["callsite_stub_inventory"]}
	assert callsite_inventory == {
		"auth_backend_dispatch_stubs": {
			"lane_id": "auth_backend_dispatch_stubs",
			"paths": [
				"src/common/auth_credentials.c",
				"src/common/platform/platform_backend_auth.h",
			],
			"callsite": "QL_Auth_ExecuteRequest tries Open Steam then Steamworks auth backends.",
			"default_policy_guard": "platform_backend_auth.h returns qfalse inline when QL_BUILD_OPEN_STEAM or QL_BUILD_STEAMWORKS are disabled.",
		},
		"steamworks_header_default_stubs": {
			"lane_id": "steamworks_header_default_stubs",
			"paths": ["src/common/platform/platform_steamworks.h"],
			"callsite": "Shared Steamworks wrapper declarations are only live under #if QL_BUILD_STEAMWORKS.",
			"default_policy_guard": "The #else surface returns qfalse for initialisation/server init and no-ops shutdown/callback calls.",
		},
		"common_steam_gameserver_bootstrap": {
			"lane_id": "common_steam_gameserver_bootstrap",
			"paths": ["src/code/qcommon/common.c"],
			"callsite": "Com_InitSteamGameServer is called from Com_Init and NET_Restart paths.",
			"default_policy_guard": "Com_InitSteamGameServer executes live Steam GameServer calls only inside #if QL_BUILD_STEAMWORKS.",
		},
		"client_steam_frame_and_init": {
			"lane_id": "client_steam_frame_and_init",
			"paths": ["src/code/client/cl_main.c"],
			"callsite": "SteamClient_Frame and SteamClient_Init own client Steam callbacks, voice, stats, lobby, and rich-presence bootstrap.",
			"default_policy_guard": "SteamClient_Frame returns unless CL_SteamServicesEnabled and the retained SteamClient_IsInitialized flag succeed; SteamClient_Init logs compatibility fallback when services are disabled.",
		},
		"windows_net_restart_steam_hooks": {
			"lane_id": "windows_net_restart_steam_hooks",
			"paths": ["src/code/win32/win_net.c"],
			"callsite": "NET_Restart calls QL_Steamworks_ServerShutdown and Com_InitSteamGameServer around socket reconfiguration.",
			"default_policy_guard": "The shutdown call resolves to the platform_steamworks.h no-op stub and the init call resolves to the #if QL_BUILD_STEAMWORKS bootstrap gate when online services are disabled.",
		},
	}
	assert online["source_scan"] == {
		"date": "2026-06-05",
		"paths": ["src/common", "src/code"],
		"patterns": [
			"QL_BUILD_ONLINE_SERVICES",
			"QL_PLATFORM_HAS_ONLINE_SERVICES",
			"QL_BUILD_STEAMWORKS",
			"QL_BUILD_OPEN_STEAM",
			"Awesomium",
			"Steam",
			"steam",
			"advert",
			"matchmaking",
			"workshop",
			"overlay",
			"stats",
		],
		"classification": "targeted policy drift scan; gameplay uses of stats/overlay words were treated as search noise unless they touched live service bridges",
		"result": "no new default-enabled Quake Live online-service lane found",
	}
	auth_request = _function_block(auth_credentials, "qboolean QL_Auth_ExecuteRequest")
	_assert_order(
		auth_request,
		"if ( QL_PlatformBackendOpenSteam_Authenticate( credential, response ) ) {",
		"return qtrue;",
		"if ( QL_PlatformBackendSteamworks_Authenticate( credential, response ) ) {",
		"return qtrue;",
		"No authentication backend is available.",
	)
	_assert_order(
		backend_auth,
		"#if QL_BUILD_STEAMWORKS",
		"qboolean QL_PlatformBackendSteamworks_Authenticate",
		"#else",
		"static inline qboolean QL_PlatformBackendSteamworks_Authenticate",
		"return qfalse;",
		"#if QL_BUILD_OPEN_STEAM",
		"qboolean QL_PlatformBackendOpenSteam_Authenticate",
		"#else",
		"static inline qboolean QL_PlatformBackendOpenSteam_Authenticate",
		"return qfalse;",
	)
	_assert_order(
		platform_steamworks_h,
		"#if QL_BUILD_STEAMWORKS",
		"qboolean QL_Steamworks_Init( void );",
		"qboolean QL_Steamworks_ServerInitWithVersion",
		"void QL_Steamworks_ServerShutdown( void );",
		"#else",
		"static inline qboolean QL_Steamworks_Init( void )",
		"return qfalse;",
		"static inline void QL_Steamworks_Shutdown( void )",
		"static inline void QL_Steamworks_RunCallbacks( void )",
		"static inline void QL_Steamworks_RunServerCallbacks( void )",
		"static inline qboolean QL_Steamworks_ServerInitWithVersion",
		"return qfalse;",
		"static inline void QL_Steamworks_ServerShutdown( void )",
	)
	steam_gameserver = _function_block(common_c, "void Com_InitSteamGameServer")
	_assert_order(
		steam_gameserver,
		"#if QL_BUILD_STEAMWORKS",
		"QL_Steamworks_ServerInitWithVersion",
		"QL_Steamworks_ServerLogOn",
		"QL_Steamworks_ServerEnableHeartbeats( qfalse );",
		"#elif QL_PLATFORM_HAS_STEAM_SERVICES",
		"Steam GameServer bootstrap unavailable",
	)
	steam_client_frame = _function_block(cl_main, "void SteamClient_Frame( void )")
	_assert_order(
		steam_client_frame,
		"services = QL_RefreshPlatformServices();",
		"SteamClient_SetInitializedState( services );",
		"if ( !SteamClient_IsInitialized() ) {",
		"return;",
		"QL_Steamworks_RunCallbacks();",
	)
	steam_client_init = _function_block(cl_main, "void SteamClient_Init( void )")
	_assert_order(
		steam_client_init,
		"SteamClient_SetInitializedState( services );",
		"if ( !SteamClient_IsInitialized() ) {",
		"CL_LogClientCallbackBootstrapFallback( \"online services disabled; keeping compatibility-only browser event fallback\" );",
		"} else {",
		"SteamCallbacks_Init();",
		"if ( SteamClient_IsInitialized() ) {",
		"QL_Steamworks_UnregisterClientCallbacks();",
	)
	net_restart = _function_block(win_net, "void NET_Restart( void )")
	_assert_order(
		net_restart,
		"QL_Steamworks_ServerShutdown();",
		"NET_Config( networkingEnabled );",
		"Com_InitSteamGameServer();",
	)

	ownerdraw = spec["ownerdraw"]
	assert ownerdraw["spot_check_result"] == "Index reviewed; no src/ui edits were made."
	assert ownerdraw["index"] == "docs/reverse-engineering/ui-ownerdrawtype-parity-index.md"
	assert ownerdraw["counts"] == {
		"checked": 36,
		"partial": 1,
		"needs_check": 0,
		"retail_noop_source_legacy": 8,
		"noop_missing": 1,
		"sentinel": 1,
	}
	assert ownerdraw["remaining_actions"] == [
		"Complete UI_KEYBINDSTATUS from partial coverage to full parity.",
		"Audit the retail no-op/source legacy set before any menu-owner changes.",
		"Confirm UI_VOTE_KICK has no shipped UI ownerdraw usage before marking it closed as a no-op.",
	]
	followup_lanes = {lane["lane_id"]: lane for lane in ownerdraw["followup_lane_inventory"]}
	assert followup_lanes == {
		"keybindstatus_full_parity_pass": {
			"lane_id": "keybindstatus_full_parity_pass",
			"ownerdraw_ids": ["542"],
			"ownerdraw_types": ["UI_KEYBINDSTATUS"],
			"current_index_state": "Partial",
			"index_evidence": "UI_DrawKeyBindStatus @ 0x100092F0; width helper participates; draw and width route wired.",
			"required_before_closure": [
				"Add the full normal/pending prompt parity pass called out by the index.",
				"Keep the retail UI_OwnerDraw and UI_OwnerDrawWidth control-flow evidence attached to the closure note.",
				"Do not mark the lane checked from count evidence alone.",
			],
		},
		"retail_noop_source_legacy_audit": {
			"lane_id": "retail_noop_source_legacy_audit",
			"ownerdraw_ids": ["521", "523", "524", "525", "526", "527", "543", "546"],
			"ownerdraw_types": [
				"UI_TIER",
				"UI_TIERMAP1",
				"UI_TIERMAP2",
				"UI_TIERMAP3",
				"UI_TIER_MAPNAME",
				"UI_TIER_GAMETYPE",
				"UI_CLANCINEMATIC",
				"UI_PREVIEWCINEMATIC",
			],
			"current_index_state": "Retail no-op/source legacy",
			"index_evidence": "Retail dispatcher falls through/defaults for these IDs while current source still has legacy draw or cinematic routes.",
			"required_before_closure": [
				"Confirm menu reachability or unused status for each ID.",
				"Document whether each legacy route stays as compatibility, is gated, or is removed for strict retail parity.",
				"Recheck UI_CLANCINEMATIC stop-cinematic handling before any source-owner change.",
			],
		},
		"vote_kick_noop_reachability": {
			"lane_id": "vote_kick_noop_reachability",
			"ownerdraw_ids": ["530"],
			"ownerdraw_types": ["UI_VOTE_KICK"],
			"current_index_state": "No-op/missing",
			"index_evidence": "Retail dispatcher default/no-op for this ID; no draw, key, or width route exists in current source.",
			"required_before_closure": [
				"Confirm no shipped menu depends on UI_VOTE_KICK as a UI ownerdraw.",
				"Document the menu-search evidence before marking it closed as a no-op.",
				"Keep closure documentation-first because src/ui is read-only for agents.",
			],
		},
	}
	assert ownerdraw["src_ui_read_only_respected"] is True
	for expected in (
		"| Partial | 1 | `542` |",
		"| Retail no-op/source legacy | 8 | `521`, `523`, `524`, `525`, `526`, `527`, `543`, `546` |",
		"| No-op/missing | 1 | `530` |",
		"| 542 | `UI_KEYBINDSTATUS` |",
		"| 530 | `UI_VOTE_KICK` |",
		"| 521 | `UI_TIER` |",
		"| 543 | `UI_CLANCINEMATIC` |",
		"| 546 | `UI_PREVIEWCINEMATIC` |",
		"Next practical sweep order:",
	):
		assert expected in ownerdraw_index

	guard = spec["guardrail_assertions"]
	assert guard["manifest_test"] == "tests/test_netcode_parity_manifest.py::test_residual_policy_spot_check_guardrails_remain_manifest_backed"
	assert guard["runtime_launch_required"] is False
	assert guard["game_launch_required"] is False
	assert guard["source_assertions"] == [
		"platform_config_default_offline_policy",
		"provider_specific_flags_forced_off_when_online_services_disabled",
		"default_service_descriptors_publish_build_disabled_labels",
		"legacy_q3_service_calls_remain_dual_gated",
		"online_service_lane_inventory_compile_and_runtime_gates",
		"online_service_callsite_stub_inventory_gates",
	]
	assert guard["ownerdraw_assertions"] == [
		"ownerdraw_index_counts_match_spot_check_manifest",
		"ownerdraw_followup_lane_inventory_matches_index_rows",
		"UI_KEYBINDSTATUS_remains_partial_documentation_first",
		"retail_noop_source_legacy_set_remains_documentation_first",
		"UI_VOTE_KICK_remains_noop_missing_documentation_first",
		"src_ui_tree_was_not_edited_for_this_guard_pass",
	]
	assert spec["checklist_effect"] == {
		"dated_online_services_spot_check_captured": True,
		"dated_online_service_lane_inventory_captured": True,
		"dated_online_service_callsite_stub_inventory_captured": True,
		"dated_ownerdraw_spot_check_captured": True,
		"dated_ownerdraw_followup_lane_inventory_captured": True,
		"dated_policy_manifest_guard_captured": True,
		"ongoing_guardrails_closed": False,
	}
	assert spec["assertion_tests"] == [
		"tests/test_netcode_parity_manifest.py::test_residual_policy_spot_check_guardrails_remain_manifest_backed"
	]
	assert spec["parity_estimate"]["repo_wide_before_percent"] == 99
	assert spec["parity_estimate"]["repo_wide_after_percent"] == 99

	assert "- [ ] Keep Quake Live-only online-service replacements behind" in checklist
	assert "- [x] 2026-06-05 spot-check: default online-service policy still routes through" in checklist
	assert "- [x] 2026-06-05 lane inventory: known Steamworks, open-adapter, Awesomium," in checklist
	assert "- [x] 2026-06-05 call-site/stub inventory: auth dispatch, Steamworks stubs," in checklist
	assert "- [x] 2026-06-05 manifest guard: residual policy spot-check is backed by" in checklist
	assert "- [ ] Check the ownerdraw parity indexes before starting new UI work" in checklist
	assert "- [x] 2026-06-05 spot-check: `ui-ownerdrawtype-parity-index.md` was reviewed" in checklist
	assert "- [x] 2026-06-05 ownerdraw follow-up inventory: `UI_KEYBINDSTATUS`, the" in checklist
	assert "Manifest Guard" in note
	assert "Policy lane inventory:" in note
	assert "Call-site/stub inventory:" in note
	assert "Targeted source scan:" in note
	assert "Follow-up lane inventory:" in note
	assert "Keybind status full parity pass" in note
	assert "Retail no-op/source legacy audit" in note
	assert "Vote-kick no-op reachability" in note
	assert "test_residual_policy_spot_check_guardrails_remain_manifest_backed" in note
	assert "No `src/ui/` files were edited for this guard pass." in note


def test_networking_2_residual_capture_blocker_audit_keeps_external_evidence_rows_open() -> None:
	spec = _networking_2_capture_blockers_spec()
	note = _read(NETWORKING_2_CAPTURE_BLOCKERS_AUDIT_PATH)
	checklist = _read(OUTSTANDING_WORK_CHECKLIST_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)
	replay_spec = _networking_2_replay_validation_spec()
	xor_spec = _networking_2_xor_codec_spec()
	huffman_spec = _networking_2_huffman_fixtures_spec()
	hardening_spec = _networking_2_hardening_spec()
	capture_bundle_spec = _networking_2_capture_evidence_bundle_validation_spec()
	fragment_timing_spec = _networking_2_fragment_queue_timing_validation_spec()
	invalid_lc_spec = _networking_2_invalid_lc_probe_validation_spec()
	snapshot_decode_spec = _networking_2_snapshot_field_decode_validation_spec()

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["runtime_launch_required"] is False
	assert spec["game_launch_required"] is False
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-xor-codec-parity-2026-06-05.json",
		"docs/reverse-engineering/network-adaptive-huffman-fixtures-2026-06-05.json",
		"docs/reverse-engineering/network-demo-capture-replay-validation-2026-06-05.json",
		"docs/reverse-engineering/network-oob-connect-auth-parity-2026-06-05.json",
		"docs/reverse-engineering/network-protocol-hardening-parity-2026-06-05.json",
		"docs/reverse-engineering/network-playerstate-fields-parity-2026-06-05.json",
		"docs/reverse-engineering/network-entitystate-fields-parity-2026-06-05.json",
		"docs/reverse-engineering/network-client-message-sideband-producers-2026-06-05.json",
		"docs/reverse-engineering/network-fragment-queue-timing-validation-2026-06-05.json",
		"docs/reverse-engineering/network-invalid-lc-probe-validation-2026-06-05.json",
		"docs/reverse-engineering/network-snapshot-field-decode-validation-2026-06-05.json",
		"docs/reverse-engineering/network-capture-evidence-bundle-validation-2026-06-05.json",
	]

	inventory = spec["evidence_inventory"]
	assert inventory["committed_byte_for_byte_retail_capture_available"] is False
	assert inventory["committed_protocol_91_demo_transcript_available"] is False
	assert inventory["demo_transcript_intake_ready"] is True
	assert inventory["demo_transcript_intake"]["tool"] == "tools/trace/demo_transcript.py"
	assert inventory["demo_transcript_intake"]["validator_audit"] == "docs/reverse-engineering/network-capture-fixture-validation-2026-06-05.md"
	assert inventory["demo_transcript_intake"]["capture_diff_audit"] == "docs/reverse-engineering/network-capture-diff-tooling-2026-06-05.md"
	assert inventory["demo_transcript_intake"]["retail_transcript_committed"] is False
	assert inventory["fragment_queue_timing_validation_ready"] is True
	assert inventory["fragment_queue_timing_validation"]["tool"] == "tools/trace/fragment_timing.py"
	assert inventory["fragment_queue_timing_validation"]["audit"] == "docs/reverse-engineering/network-fragment-queue-timing-validation-2026-06-05.md"
	assert inventory["fragment_queue_timing_validation"]["retail_fragment_queue_capture_committed"] is False
	assert inventory["invalid_lc_probe_validation_ready"] is True
	assert inventory["invalid_lc_probe_validation"]["tool"] == "tools/trace/invalid_lc_probe.py"
	assert inventory["invalid_lc_probe_validation"]["audit"] == "docs/reverse-engineering/network-invalid-lc-probe-validation-2026-06-05.md"
	assert inventory["invalid_lc_probe_validation"]["retail_invalid_lc_probe_committed"] is False
	assert inventory["snapshot_field_decode_validation_ready"] is True
	assert inventory["snapshot_field_decode_validation"]["tool"] == "tools/trace/snapshot_decode.py"
	assert inventory["snapshot_field_decode_validation"]["audit"] == "docs/reverse-engineering/network-snapshot-field-decode-validation-2026-06-05.md"
	assert inventory["snapshot_field_decode_validation"]["retail_snapshot_decode_report_committed"] is False
	assert inventory["capture_evidence_bundle_validation_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["tool"] == "tools/trace/capture_evidence.py"
	assert inventory["capture_evidence_bundle_validation"]["audit"] == "docs/reverse-engineering/network-capture-evidence-bundle-validation-2026-06-05.md"
	assert inventory["capture_evidence_bundle_validation"]["cli"] == "python -m tools.trace.capture_evidence"
	assert inventory["capture_evidence_bundle_validation"]["cli_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["required_closure_row_cli_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["required_closure_row_cli"] == "python -m tools.trace.capture_evidence <bundle.json> --require-closure-row <row_id>"
	assert inventory["capture_evidence_bundle_validation"]["all_closure_rows_cli_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["all_closure_rows_cli"] == "python -m tools.trace.capture_evidence <bundle.json> --require-all-closure-rows"
	assert inventory["capture_evidence_bundle_validation"]["strict_final_closure_cli_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["strict_final_closure_cli"] == "python -m tools.trace.capture_evidence <bundle.json> --strict-final-closure --artifact-root <repo_root>"
	assert inventory["capture_evidence_bundle_validation"]["row_contract_cli_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["row_contract_cli"] == "python -m tools.trace.capture_evidence --print-row-contracts --row-contract <row_id>"
	assert inventory["capture_evidence_bundle_validation"]["capture_plan_cli_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["capture_plan_cli"] == "python -m tools.trace.capture_evidence --print-capture-plan --capture-plan-row <row_id>"
	assert inventory["capture_evidence_bundle_validation"]["template_generation_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["template_cli"] == "python -m tools.trace.capture_evidence --print-template --template-row <row_id>"
	assert inventory["capture_evidence_bundle_validation"]["artifact_hash_generation_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["artifact_hash_cli"] == "python -m tools.trace.capture_evidence --hash-artifact <artifact_path> --artifact-root <repo_root>"
	assert inventory["capture_evidence_bundle_validation"]["artifact_file_verification_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["artifact_verification_cli"] == "python -m tools.trace.capture_evidence <bundle.json> --verify-artifact-files --artifact-root <repo_root>"
	assert inventory["capture_evidence_bundle_validation"]["artifact_text_policy_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["artifact_text_policy_cli"] == "python -m tools.trace.capture_evidence <bundle.json> --enforce-artifact-text-policy"
	assert inventory["capture_evidence_bundle_validation"]["artifact_path_policy_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["artifact_path_policy_cli"] == "python -m tools.trace.capture_evidence <bundle.json> --enforce-artifact-path-policy"
	assert inventory["capture_evidence_bundle_validation"]["artifact_uniqueness_policy_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["artifact_uniqueness_policy_cli"] == "python -m tools.trace.capture_evidence <bundle.json> --enforce-artifact-uniqueness-policy"
	assert inventory["capture_evidence_bundle_validation"]["closure_status_summary_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["closure_status_cli"] == "python -m tools.trace.capture_evidence <bundle.json> --print-closure-status"
	assert inventory["capture_evidence_bundle_validation"]["closure_blocker_summary_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["closure_blocker_cli"] == "python -m tools.trace.capture_evidence <bundle.json> --print-closure-blockers"
	assert inventory["capture_evidence_bundle_validation"]["closure_blocker_fail_gate_ready"] is True
	assert inventory["capture_evidence_bundle_validation"]["closure_blocker_fail_gate_cli"] == "python -m tools.trace.capture_evidence <bundle.json> --print-closure-blockers --fail-on-closure-blockers"
	assert inventory["capture_evidence_bundle_validation"]["retail_capture_evidence_bundle_committed"] is False
	assert inventory["committed_semantic_snapshot_fixture_available"] is True
	assert inventory["known_semantic_fixture"]["path"] == "tests/netdumps/retail_duel.snap.json"
	assert inventory["known_semantic_fixture"]["baseline"] == "tools/tests/client_regression/retail_netdump_baseline.json"
	assert "no original datagram bytes" in inventory["known_semantic_fixture"]["limits"]
	assert "no packet-entity byte stream for playerStateFields/entityStateFields decode comparison" in inventory["known_semantic_fixture"]["limits"]

	assert replay_spec["capture_diff_status"]["byte_for_byte_replay_available"] is False
	assert capture_bundle_spec["checklist_effect"]["external_evidence_rows_closed"] is False
	assert fragment_timing_spec["checklist_effect"]["fragmented_snapshot_queued_followup_row_closed"] is False
	assert xor_spec["capture_diff_status"]["external_retail_captures_available"] is False
	assert "compressed_connect_profile91_numeric_challenge" in {
		fixture["id"] for fixture in huffman_spec["fixtures"]
	}
	assert "controlled retail probing" in hardening_spec["completion_status"]["remaining_gaps"][1]
	assert invalid_lc_spec["checklist_effect"]["invalid_lc_retail_probe_row_closed"] is False
	assert snapshot_decode_spec["checklist_effect"]["snapshot_field_capture_decode_row_closed"] is False

	source_boundaries = {boundary["id"]: boundary for boundary in spec["source_complete_boundaries"]}
	assert source_boundaries["client_message_sideband_producers"]["status"] == "source_complete_capture_diff_pending"
	assert source_boundaries["xor_codec_static_datagrams"]["status"] == "static_wire_vectors_ready_capture_diff_pending"
	assert source_boundaries["compressed_connect_huffman_fixture"]["status"] == "deterministic_fixture_ready_capture_diff_pending"
	assert source_boundaries["snapshot_field_tables"]["status"] == "retail_table_parity_locked_capture_decode_pending"

	blocked_rows = {row["row_id"]: row for row in spec["blocked_checklist_rows"]}
	assert set(blocked_rows) == {
		"byte_for_byte_replay_fixture",
		"fragmented_snapshot_queued_followup",
		"xor_golden_datagrams",
		"compressed_connect_capture_diff",
		"invalid_lc_retail_probe",
		"snapshot_field_capture_decode",
	}
	assert blocked_rows["byte_for_byte_replay_fixture"]["status"] == "external_evidence_required"
	assert blocked_rows["fragmented_snapshot_queued_followup"]["status"] == "external_evidence_required"
	assert blocked_rows["invalid_lc_retail_probe"]["status"] == "external_runtime_probe_required"
	assert "tests/netdumps/retail_duel.snap.json is semantic snapshot evidence only." in blocked_rows["byte_for_byte_replay_fixture"]["current_repo_evidence"]
	assert "network-capture-evidence-bundle-validation-2026-06-05.json validates future evidence bundles, can require specific submitted closure rows or all residual rows, can run strict final closure with retail provenance plus artifact-file verification, can print row contract inventories, row-scoped capture plans, and row-scoped templates, can emit artifact hash inventories, can verify committed artifact files against declared SHA-256 values, can enforce reviewed JSON/text artifact paths, evidence-directory path scope, and artifact uniqueness, can summarize per-row closure status and blockers, and can fail CI/review jobs when blockers remain, but commits no retail capture bundle." in blocked_rows["byte_for_byte_replay_fixture"]["current_repo_evidence"]
	assert "network-fragment-queue-timing-validation-2026-06-05.json validates future timing reports but commits no retail capture." in blocked_rows["fragmented_snapshot_queued_followup"]["current_repo_evidence"]
	assert "retail packet traces exercising the committed XOR vector windows" in blocked_rows["xor_golden_datagrams"]["closure_requires"]
	assert "network-invalid-lc-probe-validation-2026-06-05.json validates future controlled probe reports but commits no retail probe." in blocked_rows["invalid_lc_retail_probe"]["current_repo_evidence"]
	assert "controlled retail invalid-lc probe" in blocked_rows["invalid_lc_retail_probe"]["closure_requires"]
	assert "network-snapshot-field-decode-validation-2026-06-05.json validates future player/entity decode reports but commits no retail packet/decode evidence." in blocked_rows["snapshot_field_capture_decode"]["current_repo_evidence"]
	assert "retail snapshot packet capture or protocol-91 transcript with playerstate and packet entities" in blocked_rows["snapshot_field_capture_decode"]["closure_requires"]

	assert spec["checklist_effect"] == {
		"new_checked_blocker_audit_row": True,
		"new_checked_demo_transcript_intake_row": True,
		"new_checked_fixture_validation_row": True,
		"new_checked_capture_diff_tooling_row": True,
		"new_checked_fragment_queue_timing_validation_row": True,
		"new_checked_invalid_lc_probe_validation_row": True,
		"new_checked_snapshot_field_decode_validation_row": True,
		"new_checked_capture_evidence_bundle_validation_row": True,
		"new_checked_capture_evidence_bundle_cli_row": True,
		"new_checked_capture_evidence_required_row_cli_row": True,
		"new_checked_capture_evidence_row_contract_cli_row": True,
		"new_checked_capture_evidence_capture_plan_cli_row": True,
		"new_checked_capture_evidence_bundle_template_row": True,
		"new_checked_capture_evidence_artifact_hash_generation_row": True,
		"new_checked_capture_evidence_bundle_artifact_hash_row": True,
		"new_checked_capture_evidence_artifact_text_policy_row": True,
		"new_checked_capture_evidence_artifact_path_policy_row": True,
		"new_checked_capture_evidence_artifact_uniqueness_policy_row": True,
		"new_checked_capture_evidence_closure_status_row": True,
		"new_checked_capture_evidence_all_rows_cli_row": True,
		"new_checked_capture_evidence_strict_final_closure_row": True,
		"new_checked_capture_evidence_closure_blockers_row": True,
		"new_checked_capture_evidence_blocker_fail_gate_row": True,
		"capture_rows_remain_open": True,
		"policy_rows_unchanged": True,
	}
	assert spec["parity_estimate"]["overall_network_protocol_before_percent"] == 90
	assert spec["parity_estimate"]["overall_network_protocol_after_percent"] == 90
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_before_percent"] == 0
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_after_percent"] == 0
	assert spec["parity_estimate"]["repo_wide_before_percent"] == 99
	assert spec["parity_estimate"]["repo_wide_after_percent"] == 99

	assert "- [x] 2026-06-05 residual capture-blocker audit: committed evidence inventory" in checklist
	assert "- [x] Add protocol-91 demo transcript intake tooling so future retail `.dm_91`" in checklist
	assert "- [x] Add protocol-91 transcript validation gates for hashes, offsets," in checklist
	assert "- [x] Add residual capture evidence bundle validation gates so future retail" in checklist
	assert "- [x] Add a command-line validator for residual capture evidence bundles so" in checklist
	assert "- [x] Add command-line residual capture evidence required-row checks so" in checklist
	assert "- [x] Add command-line residual capture evidence row contract output so" in checklist
	assert "- [x] Add command-line residual capture evidence capture-plan output so" in checklist
	assert "- [x] Add command-line residual capture evidence bundle template generation so" in checklist
	assert "- [x] Add command-line residual capture evidence artifact hash generation so" in checklist
	assert "- [x] Add command-line residual capture evidence artifact path/SHA-256" in checklist
	assert "- [x] Add command-line residual capture evidence artifact text-policy checks so" in checklist
	assert "- [x] Add command-line residual capture evidence artifact path-scope checks so" in checklist
	assert "- [x] Add command-line residual capture evidence artifact uniqueness checks so" in checklist
	assert "- [x] Add command-line residual capture evidence closure-status summaries so" in checklist
	assert "- [x] Add command-line residual capture evidence all-rows closure checks so" in checklist
	assert "- [x] Add command-line residual capture evidence strict final-closure checks so" in checklist
	assert "- [x] Add command-line residual capture evidence closure-blocker reports so" in checklist
	assert "- [x] Add command-line residual capture evidence blocker-fail gates so" in checklist
	assert "- [x] Add packet-byte capture-diff tooling for committed XOR datagram vectors" in checklist
	assert "- [x] Add fragmented snapshot/queued follow-up timing report validation gates" in checklist
	assert "- [x] Add invalid-`lc` controlled retail probe report validation gates" in checklist
	assert "- [x] Add snapshot field decode report validation gates for future" in checklist
	assert "- [ ] Commit at least one retail packet capture, protocol-91 demo transcript" in checklist
	assert "- [ ] Validate fragmented snapshot plus queued follow-up timing against a" in checklist
	assert "- [ ] Capture-diff the XOR golden datagrams against retail packet traces." in checklist
	assert "- [ ] Capture-diff the compressed `connect` request path against a retail trace." in checklist
	assert "- [ ] Probe invalid-`lc` malicious packet behavior against retail before" in checklist
	assert "- [ ] Verify end-to-end retail snapshot capture/decode parity for" in checklist
	assert "docs/reverse-engineering/network-residual-capture-blockers-2026-06-05.md" in checklist

	assert "Network Residual Capture Blockers" in note
	assert "checked transcript-intake, transcript-validation, and capture-diff" in note
	assert "checked fragment/queue timing-validation and invalid-`lc`" in note
	assert "checked snapshot field decode-validation" in note
	assert "capture evidence bundle-validation rows" in note
	assert "including CLI validation" in note
	assert "required-row closure checks" in note
	assert "all-rows closure checks" in note
	assert "strict final-closure checks" in note
	assert "row contract output" in note
	assert "non-claiming template generation" in note
	assert "artifact hash generation" in note
	assert "artifact path/SHA-256 verification" in note
	assert "artifact text-policy checks" in note
	assert "artifact path-scope checks" in note
	assert "artifact uniqueness checks" in note
	assert "closure-status summaries" in note
	assert "closure-blocker" in note
	assert "blocker-fail gates" in note
	assert "packet-byte and" in note
	assert "retail-probe rows remain unchecked" in note
	assert "unchecked" in note
	assert "Overall network-protocol source parity remains `90%` -> `90%`." in note
	assert "Residual capture-blocker audit, 2026-06-05:" in plan
	assert "byte-for-byte capture evidence remains" in plan
	assert "--require-all-closure-rows" in plan
	assert "--strict-final-closure --artifact-root <repo_root>" in plan
	assert "--enforce-artifact-text-policy" in plan
	assert "--enforce-artifact-path-policy" in plan
	assert "--enforce-artifact-uniqueness-policy" in plan
	assert "--print-closure-status" in plan
	assert "--print-closure-blockers" in plan
	assert "--fail-on-closure-blockers" in plan
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_residual_capture_blocker_audit_keeps_external_evidence_rows_open" in spec["assertion_tests"]


def test_networking_2_capture_diff_tooling_compares_xor_and_connect_datagrams() -> None:
	spec = _networking_2_capture_diff_tooling_spec()
	note = _read(NETWORKING_2_CAPTURE_DIFF_TOOLING_AUDIT_PATH)
	checklist = _read(OUTSTANDING_WORK_CHECKLIST_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)
	tool = _read(REPO_ROOT / "tools/trace/capture_diff.py")
	trace_init = _read(REPO_ROOT / "tools/trace/__init__.py")
	trace_tests = _read(REPO_ROOT / "tools/tests/test_trace_harness.py")
	xor_spec = _networking_2_xor_codec_spec()
	huffman_spec = _networking_2_huffman_fixtures_spec()

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["status"] == "completed_capture_diff_tooling_no_retail_capture_claimed"
	assert spec["runtime_launch_required"] is False
	assert spec["game_launch_required"] is False
	assert spec["source_files"] == [
		"tools/trace/capture_diff.py",
		"tools/trace/__init__.py",
		"tools/tests/test_trace_harness.py",
	]
	assert spec["supported_checklist_rows"] == [
		"Capture-diff the XOR golden datagrams against retail packet traces.",
		"Capture-diff the compressed connect request path against a retail trace.",
	]

	contract = spec["tool_contract"]
	assert contract["module"] == "tools.trace.capture_diff"
	assert contract["capture_format"] == "quake_live_packet_byte_capture"
	assert contract["report_format"] == "quake_live_capture_diff_report"
	assert contract["functions"] == [
		"validate_packet_capture_dict",
		"packet_expectations_from_xor_spec",
		"packet_expectations_from_huffman_spec",
		"diff_packet_capture",
	]
	assert contract["result_statuses"] == ["match", "missing", "mismatch"]
	assert contract["report_columns"] == [
		"fixture_id",
		"lane",
		"source",
		"status",
		"expected_size",
		"observed_size",
		"expected_sha256",
		"observed_sha256",
		"first_mismatch_offset",
	]
	assert contract["retail_provenance_required_for_closure"] is True

	sources = {source["lane"]: source for source in spec["expectation_sources"]}
	assert sources["xor_golden_datagram"]["field"] == "golden_vectors[].encoded_datagram_hex"
	assert sources["adaptive_huffman_datagram"]["field"] == "fixtures[].encoded_datagram_hex"
	assert any("encoded_datagram_hex" in vector for vector in xor_spec["golden_vectors"])
	assert any("encoded_datagram_hex" in fixture for fixture in huffman_spec["fixtures"])

	assert "class PacketExpectation" in tool
	assert "def validate_packet_capture_dict" in tool
	assert "def packet_expectations_from_xor_spec" in tool
	assert "def packet_expectations_from_huffman_spec" in tool
	assert "def diff_packet_capture" in tool
	assert "\"quake_live_capture_diff_report\"" in tool
	assert "\"first_mismatch_offset\"" in tool
	assert "packet_expectations_from_xor_spec" in trace_init
	assert "packet_expectations_from_huffman_spec" in trace_init
	assert "test_packet_capture_diff_matches_xor_and_huffman_fixture_bytes" in trace_tests
	assert "test_packet_capture_diff_reports_missing_and_mismatched_fixture_bytes" in trace_tests

	assert spec["checklist_effect"] == {
		"new_checked_capture_diff_tooling_row": True,
		"xor_capture_diff_row_closed": False,
		"compressed_connect_capture_diff_row_closed": False,
		"capture_rows_remain_open": True,
	}
	assert spec["parity_estimate"]["overall_network_protocol_before_percent"] == 90
	assert spec["parity_estimate"]["overall_network_protocol_after_percent"] == 90
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_before_percent"] == 0
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_after_percent"] == 0

	assert "- [x] Add packet-byte capture-diff tooling for committed XOR datagram vectors" in checklist
	assert "- [ ] Capture-diff the XOR golden datagrams against retail packet traces." in checklist
	assert "- [ ] Capture-diff the compressed `connect` request path against a retail trace." in checklist
	assert "docs/reverse-engineering/network-capture-diff-tooling-2026-06-05.md" in checklist
	assert "Network Capture Diff Tooling" in note
	assert "does not claim that a retail packet trace" in note
	assert "committed." in note
	assert "The actual XOR" in note
	assert "Residual capture-diff tooling update, 2026-06-05:" in plan
	assert "The XOR and compressed-`connect` capture" in plan
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_capture_diff_tooling_compares_xor_and_connect_datagrams" in spec["assertion_tests"]


def test_networking_2_capture_evidence_bundle_validation_gate_maps_residual_rows() -> None:
	spec = _networking_2_capture_evidence_bundle_validation_spec()
	note = _read(NETWORKING_2_CAPTURE_EVIDENCE_BUNDLE_VALIDATION_AUDIT_PATH)
	checklist = _read(OUTSTANDING_WORK_CHECKLIST_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)
	blockers = _networking_2_capture_blockers_spec()
	tool = _read(REPO_ROOT / "tools/trace/capture_evidence.py")
	trace_init = _read(REPO_ROOT / "tools/trace/__init__.py")
	trace_tests = _read(REPO_ROOT / "tools/tests/test_trace_harness.py")

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["status"] == "completed_capture_evidence_bundle_validation_gate_no_retail_evidence_claimed"
	assert spec["runtime_launch_required"] is False
	assert spec["game_launch_required"] is False
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-capture-fixture-validation-2026-06-05.json",
		"docs/reverse-engineering/network-capture-diff-tooling-2026-06-05.json",
		"docs/reverse-engineering/network-fragment-queue-timing-validation-2026-06-05.json",
		"docs/reverse-engineering/network-invalid-lc-probe-validation-2026-06-05.json",
		"docs/reverse-engineering/network-snapshot-field-decode-validation-2026-06-05.json",
		"docs/reverse-engineering/network-residual-capture-blockers-2026-06-05.json",
	]
	assert spec["source_files"] == [
		"tools/trace/capture_evidence.py",
		"tools/trace/__init__.py",
		"tools/tests/test_trace_harness.py",
	]
	assert spec["supported_checklist_rows"] == [
		"Commit at least one retail packet capture, protocol-91 demo transcript, or equivalent known-good capture fixture for byte-for-byte replay validation.",
		"Validate fragmented snapshot plus queued follow-up timing against a byte-for-byte retail capture.",
		"Capture-diff the XOR golden datagrams against retail packet traces.",
		"Capture-diff the compressed connect request path against a retail trace.",
		"Probe invalid-lc malicious packet behavior against retail before claiming exact crash/drop equivalence.",
		"Verify end-to-end retail snapshot capture/decode parity for playerStateFields and entityStateFields.",
	]

	contract = spec["tool_contract"]
	assert contract["module"] == "tools.trace.capture_evidence"
	assert contract["function"] == "validate_capture_evidence_bundle_dict"
	assert contract["row_contract_function"] == "capture_evidence_row_contracts"
	assert contract["capture_plan_function"] == "capture_evidence_capture_plan"
	assert contract["template_function"] == "capture_evidence_bundle_template"
	assert contract["artifact_hash_function"] == "hash_capture_evidence_artifacts"
	assert contract["artifact_verify_function"] == "verify_capture_evidence_artifact_files"
	assert contract["artifact_text_policy_function"] == "verify_capture_evidence_artifact_text_policy"
	assert contract["artifact_path_policy_function"] == "verify_capture_evidence_artifact_path_policy"
	assert contract["artifact_uniqueness_policy_function"] == "verify_capture_evidence_artifact_uniqueness_policy"
	assert contract["closure_row_require_function"] == "require_capture_evidence_closure_rows"
	assert contract["all_closure_rows_require_function"] == "require_all_capture_evidence_closure_rows"
	assert contract["closure_status_function"] == "summarize_capture_evidence_closure_status"
	assert contract["closure_blockers_function"] == "summarize_capture_evidence_closure_blockers"
	assert contract["closure_blocker_gate_function"] == "require_capture_evidence_no_closure_blockers"
	assert contract["format"] == "quake_live_capture_evidence_bundle"
	assert contract["protocol"] == 91
	assert contract["closure_target_statuses"] == [
		"submitted_for_closure",
		"supporting_evidence",
		"not_claimed",
	]
	assert contract["residual_row_ids"] == [
		"byte_for_byte_replay_fixture",
		"fragmented_snapshot_queued_followup",
		"xor_golden_datagrams",
		"compressed_connect_capture_diff",
		"invalid_lc_retail_probe",
		"snapshot_field_capture_decode",
	]
	assert contract["embedded_report_formats"] == [
		"quake_live_demo_message_transcript",
		"quake_live_packet_byte_capture",
		"quake_live_capture_diff_report",
		"quake_live_fragment_queue_timing",
		"quake_live_invalid_lc_probe",
		"quake_live_snapshot_field_decode",
	]
	assert "embedded reports are delegated to their row-specific validators" in contract["checks"]
	assert "closure capture-diff reports must have match status" in contract["checks"]
	assert "optional required closure row checks prove selected residual rows are submitted_for_closure" in contract["checks"]
	assert "all-rows closure checks require every residual row to be submitted_for_closure" in contract["checks"]
	assert "row contract output lists residual row IDs, checklist text, allowed formats, artifact types, and target statuses" in contract["checks"]
	assert "capture plan output lists required evidence, provenance keys, reviewed artifact paths, and row-scoped helper commands without claiming retail evidence" in contract["checks"]
	assert "template generation emits not_claimed targets until retail artifacts are filled" in contract["checks"]
	assert "artifact hash generation emits repo-relative path, byte size, and lowercase SHA-256 for future bundle entries" in contract["checks"]
	assert "optional artifact file verification confirms committed paths exist and match declared SHA-256 values" in contract["checks"]
	assert "optional artifact text-policy checks require reviewed .json, .md, or .txt paths and reject raw capture/demo/dump/archive suffixes" in contract["checks"]
	assert "optional artifact path-scope checks require reviewed evidence directories and reject assets, references, and source-tree paths" in contract["checks"]
	assert "optional artifact uniqueness checks reject repeated artifact IDs or paths across closure rows" in contract["checks"]
	assert "closure status output summarizes every residual row as submitted, supporting, not claimed, or missing" in contract["checks"]
	assert "closure blocker output lists blocked residual rows with accepted artifact formats and next actions" in contract["checks"]
	assert "closure blocker fail gate returns non-zero when required rows remain blocked" in contract["checks"]
	assert "strict final closure mode requires retail provenance, all residual rows, and verified artifact files" in contract["checks"]
	assert contract["retail_provenance_required_for_closure"] is True
	assert spec["cli_contract"] == {
		"entry_point": "python -m tools.trace.capture_evidence",
		"arguments": [
			"bundle",
			"--playerstate-spec",
			"--entitystate-spec",
			"--require-retail-provenance",
			"--require-closure-row",
			"--require-all-closure-rows",
			"--strict-final-closure",
			"--print-row-contracts",
			"--row-contract",
			"--print-capture-plan",
			"--capture-plan-row",
			"--print-template",
			"--template-row",
			"--hash-artifact",
			"--verify-artifact-files",
			"--enforce-artifact-text-policy",
			"--enforce-artifact-path-policy",
			"--enforce-artifact-uniqueness-policy",
			"--print-closure-status",
			"--print-closure-blockers",
			"--fail-on-closure-blockers",
			"--artifact-root",
		],
		"strict_final_closure_cli": "python -m tools.trace.capture_evidence <bundle.json> --strict-final-closure --artifact-root <repo_root>",
		"success_output": "JSON validation summary, row contract inventory, capture plan inventory, artifact hash inventory, artifact-file verification summary, strict final-closure summary, closure status summary, closure blocker summary, blocker-fail gate summary, or non-claiming bundle template",
		"failure_output": "non-zero exit with diagnostic on stderr",
	}

	assert "ROW_ALLOWED_FORMATS" in tool
	assert "\"byte_for_byte_replay_fixture\"" in tool
	assert "\"fragmented_snapshot_queued_followup\"" in tool
	assert "\"xor_golden_datagrams\"" in tool
	assert "\"compressed_connect_capture_diff\"" in tool
	assert "\"invalid_lc_retail_probe\"" in tool
	assert "\"snapshot_field_capture_decode\"" in tool
	assert "def validate_capture_evidence_bundle_dict" in tool
	assert "def capture_evidence_row_contracts" in tool
	assert "def capture_evidence_capture_plan" in tool
	assert "def capture_evidence_bundle_template" in tool
	assert "def hash_capture_evidence_artifacts" in tool
	assert "def verify_capture_evidence_artifact_files" in tool
	assert "def verify_capture_evidence_artifact_text_policy" in tool
	assert "def verify_capture_evidence_artifact_path_policy" in tool
	assert "def verify_capture_evidence_artifact_uniqueness_policy" in tool
	assert "def require_capture_evidence_closure_rows" in tool
	assert "def require_capture_evidence_no_closure_blockers" in tool
	assert "def require_all_capture_evidence_closure_rows" in tool
	assert "def summarize_capture_evidence_closure_status" in tool
	assert "def summarize_capture_evidence_closure_blockers" in tool
	assert "def main" in tool
	assert "\"quake_live_capture_evidence_bundle\"" in tool
	assert "python -m tools.trace.capture_evidence --print-template" in tool
	assert "closure capture diff reports must have match status" in tool
	assert "--require-retail-provenance" in tool
	assert "--require-closure-row" in tool
	assert "--require-all-closure-rows" in tool
	assert "--strict-final-closure" in tool
	assert "--print-row-contracts" in tool
	assert "--row-contract" in tool
	assert "--print-capture-plan" in tool
	assert "--capture-plan-row" in tool
	assert "--print-template" in tool
	assert "--template-row" in tool
	assert "--hash-artifact" in tool
	assert "--verify-artifact-files" in tool
	assert "--enforce-artifact-text-policy" in tool
	assert "--enforce-artifact-path-policy" in tool
	assert "--enforce-artifact-uniqueness-policy" in tool
	assert "--print-closure-status" in tool
	assert "--print-closure-blockers" in tool
	assert "--fail-on-closure-blockers" in tool
	assert "--artifact-root" in tool
	assert "validator(report, **kwargs)" in tool
	assert "CaptureEvidenceError" in trace_init
	assert "capture_evidence_capture_plan" in trace_init
	assert "capture_evidence_row_contracts" in trace_init
	assert "capture_evidence_bundle_template" in trace_init
	assert "hash_capture_evidence_artifacts" in trace_init
	assert "verify_capture_evidence_artifact_path_policy" in trace_init
	assert "verify_capture_evidence_artifact_text_policy" in trace_init
	assert "verify_capture_evidence_artifact_uniqueness_policy" in trace_init
	assert "require_capture_evidence_closure_rows" in trace_init
	assert "require_capture_evidence_no_closure_blockers" in trace_init
	assert "require_all_capture_evidence_closure_rows" in trace_init
	assert "summarize_capture_evidence_closure_status" in trace_init
	assert "summarize_capture_evidence_closure_blockers" in trace_init
	assert "validate_capture_evidence_bundle_dict" in trace_init
	assert "verify_capture_evidence_artifact_files" in trace_init
	assert "test_capture_evidence_bundle_validator_accepts_embedded_retail_reports" in trace_tests
	assert "test_capture_evidence_bundle_validator_rejects_wrong_row_format_and_diff_failures" in trace_tests
	assert "test_capture_evidence_bundle_cli_validates_json_file" in trace_tests
	assert "test_capture_evidence_bundle_cli_reports_validation_errors" in trace_tests
	assert "test_capture_evidence_bundle_cli_requires_specific_closure_rows" in trace_tests
	assert "test_capture_evidence_bundle_cli_requires_all_closure_rows" in trace_tests
	assert "test_capture_evidence_all_closure_row_requirement_rejects_missing_rows" in trace_tests
	assert "test_capture_evidence_closure_row_requirement_rejects_supporting_only_rows" in trace_tests
	assert "test_capture_evidence_closure_status_summarizes_all_residual_rows" in trace_tests
	assert "test_capture_evidence_bundle_cli_prints_closure_status" in trace_tests
	assert "test_capture_evidence_closure_blockers_summarize_blocked_residual_rows" in trace_tests
	assert "test_capture_evidence_bundle_cli_prints_closure_blockers" in trace_tests
	assert "test_capture_evidence_no_closure_blockers_rejects_blocked_rows" in trace_tests
	assert "test_capture_evidence_bundle_cli_fails_on_closure_blockers_after_printing_report" in trace_tests
	assert "test_capture_evidence_bundle_cli_prints_row_contracts" in trace_tests
	assert "test_capture_evidence_row_contracts_reject_unknown_rows" in trace_tests
	assert "test_capture_evidence_capture_plan_lists_row_scoped_collection_requirements" in trace_tests
	assert "test_capture_evidence_bundle_cli_prints_row_scoped_capture_plan" in trace_tests
	assert "test_capture_evidence_capture_plan_rejects_unknown_rows" in trace_tests
	assert "test_capture_evidence_bundle_template_is_non_claiming_and_row_scoped" in trace_tests
	assert "test_capture_evidence_bundle_cli_prints_row_scoped_template" in trace_tests
	assert "test_capture_evidence_bundle_cli_hashes_artifacts_for_bundle_population" in trace_tests
	assert "test_capture_evidence_artifact_hashing_rejects_root_escape" in trace_tests
	assert "test_capture_evidence_bundle_cli_verifies_artifact_files" in trace_tests
	assert "test_capture_evidence_artifact_text_policy_accepts_reviewed_text_paths" in trace_tests
	assert "test_capture_evidence_bundle_cli_enforces_artifact_text_policy" in trace_tests
	assert "test_capture_evidence_artifact_path_policy_accepts_reviewed_evidence_paths" in trace_tests
	assert "test_capture_evidence_bundle_cli_enforces_artifact_path_policy" in trace_tests
	assert "test_capture_evidence_artifact_uniqueness_policy_accepts_unique_artifacts" in trace_tests
	assert "test_capture_evidence_bundle_cli_enforces_artifact_uniqueness_policy" in trace_tests
	assert "test_capture_evidence_bundle_cli_strict_final_closure_requires_all_rows_and_artifacts" in trace_tests
	assert "test_capture_evidence_bundle_cli_strict_final_closure_rejects_missing_artifact_files" in trace_tests
	assert "test_capture_evidence_bundle_artifact_file_verification_rejects_hash_mismatch" in trace_tests

	assert spec["checklist_effect"] == {
		"new_checked_capture_evidence_bundle_validation_row": True,
		"new_checked_capture_evidence_bundle_cli_row": True,
		"new_checked_capture_evidence_required_row_cli_row": True,
		"new_checked_capture_evidence_row_contract_cli_row": True,
		"new_checked_capture_evidence_capture_plan_cli_row": True,
		"new_checked_capture_evidence_bundle_template_row": True,
		"new_checked_capture_evidence_artifact_hash_generation_row": True,
		"new_checked_capture_evidence_bundle_artifact_hash_row": True,
		"new_checked_capture_evidence_artifact_text_policy_row": True,
		"new_checked_capture_evidence_artifact_path_policy_row": True,
		"new_checked_capture_evidence_artifact_uniqueness_policy_row": True,
		"new_checked_capture_evidence_closure_status_row": True,
		"new_checked_capture_evidence_all_rows_cli_row": True,
		"new_checked_capture_evidence_strict_final_closure_row": True,
		"new_checked_capture_evidence_closure_blockers_row": True,
		"new_checked_capture_evidence_blocker_fail_gate_row": True,
		"external_evidence_rows_closed": False,
		"capture_rows_remain_open": True,
	}
	assert spec["parity_estimate"]["overall_network_protocol_before_percent"] == 90
	assert spec["parity_estimate"]["overall_network_protocol_after_percent"] == 90
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_before_percent"] == 0
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_after_percent"] == 0

	assert "- [x] Add residual capture evidence bundle validation gates so future retail" in checklist
	assert "- [x] Add a command-line validator for residual capture evidence bundles so" in checklist
	assert "- [x] Add command-line residual capture evidence required-row checks so" in checklist
	assert "- [x] Add command-line residual capture evidence row contract output so" in checklist
	assert "- [x] Add command-line residual capture evidence capture-plan output so" in checklist
	assert "- [x] Add command-line residual capture evidence bundle template generation so" in checklist
	assert "- [x] Add command-line residual capture evidence artifact hash generation so" in checklist
	assert "- [x] Add command-line residual capture evidence artifact path/SHA-256" in checklist
	assert "- [x] Add command-line residual capture evidence artifact text-policy checks so" in checklist
	assert "- [x] Add command-line residual capture evidence artifact path-scope checks so" in checklist
	assert "- [x] Add command-line residual capture evidence artifact uniqueness checks so" in checklist
	assert "- [x] Add command-line residual capture evidence closure-status summaries so" in checklist
	assert "- [x] Add command-line residual capture evidence all-rows closure checks so" in checklist
	assert "- [x] Add command-line residual capture evidence strict final-closure checks so" in checklist
	assert "- [x] Add command-line residual capture evidence closure-blocker reports so" in checklist
	assert "- [x] Add command-line residual capture evidence blocker-fail gates so" in checklist
	assert "- [ ] Commit at least one retail packet capture, protocol-91 demo transcript" in checklist
	assert "docs/reverse-engineering/network-capture-evidence-bundle-validation-2026-06-05.md" in checklist
	assert "Network Capture Evidence Bundle Validation" in note
	assert "No retail capture, probe, or decode" in note
	assert "Closure capture-diff reports must be full matches" in note
	assert "python -m tools.trace.capture_evidence" in note
	assert "--print-closure-status" in note
	assert "--print-closure-blockers" in note
	assert "--fail-on-closure-blockers" in note
	assert "--require-all-closure-rows" in note
	assert "--strict-final-closure" in note
	assert "--require-closure-row" in note
	assert "--print-row-contracts" in note
	assert "--print-capture-plan" in note
	assert "--print-template" in note
	assert "--hash-artifact" in note
	assert "--verify-artifact-files" in note
	assert "--enforce-artifact-text-policy" in note
	assert "--enforce-artifact-path-policy" in note
	assert "--enforce-artifact-uniqueness-policy" in note
	assert "not_claimed" in note
	assert "Residual capture evidence bundle validation update, 2026-06-05:" in plan
	assert "python -m tools.trace.capture_evidence" in plan
	assert "--require-closure-row <row_id>" in plan
	assert "--print-row-contracts --row-contract <row_id>" in plan
	assert "--print-capture-plan --capture-plan-row <row_id>" in plan
	assert "--print-template --template-row <row_id>" in plan
	assert "--hash-artifact <artifact_path> --artifact-root <repo_root>" in plan
	assert "--verify-artifact-files --artifact-root <repo_root>" in plan
	assert "--enforce-artifact-text-policy" in plan
	assert "--enforce-artifact-path-policy" in plan
	assert "--enforce-artifact-uniqueness-policy" in plan
	assert "--print-closure-status" in plan
	assert "--print-closure-blockers" in plan
	assert "--fail-on-closure-blockers" in plan
	assert "--require-all-closure-rows" in plan
	assert "--strict-final-closure --artifact-root <repo_root>" in plan
	assert "allowed artifact" in plan

	assert blockers["evidence_inventory"]["capture_evidence_bundle_validation_ready"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_bundle_validation_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_bundle_cli_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_required_row_cli_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_row_contract_cli_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_capture_plan_cli_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_bundle_template_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_artifact_hash_generation_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_bundle_artifact_hash_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_artifact_text_policy_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_artifact_path_policy_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_artifact_uniqueness_policy_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_closure_status_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_all_rows_cli_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_strict_final_closure_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_closure_blockers_row"] is True
	assert blockers["checklist_effect"]["new_checked_capture_evidence_blocker_fail_gate_row"] is True
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_capture_evidence_bundle_validation_gate_maps_residual_rows" in spec["assertion_tests"]


def test_networking_2_fragment_queue_timing_validation_gate_requires_retail_capture() -> None:
	spec = _networking_2_fragment_queue_timing_validation_spec()
	note = _read(NETWORKING_2_FRAGMENT_QUEUE_TIMING_VALIDATION_AUDIT_PATH)
	checklist = _read(OUTSTANDING_WORK_CHECKLIST_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)
	blockers = _networking_2_capture_blockers_spec()
	tool = _read(REPO_ROOT / "tools/trace/fragment_timing.py")
	trace_init = _read(REPO_ROOT / "tools/trace/__init__.py")
	trace_tests = _read(REPO_ROOT / "tools/tests/test_trace_harness.py")

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["status"] == "completed_fragment_queue_timing_validation_gate_no_retail_capture_claimed"
	assert spec["runtime_launch_required"] is False
	assert spec["game_launch_required"] is False
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-demo-capture-replay-validation-2026-06-05.json",
		"docs/reverse-engineering/network-residual-capture-blockers-2026-06-05.json",
	]
	assert spec["source_files"] == [
		"tools/trace/fragment_timing.py",
		"tools/trace/__init__.py",
		"tools/tests/test_trace_harness.py",
	]
	assert spec["supported_checklist_row"] == "Validate fragmented snapshot plus queued follow-up timing against a byte-for-byte retail capture."

	contract = spec["tool_contract"]
	assert contract["module"] == "tools.trace.fragment_timing"
	assert contract["function"] == "validate_fragment_queue_timing_dict"
	assert contract["format"] == "quake_live_fragment_queue_timing"
	assert contract["fragment_size"] == 1300
	assert contract["required_sections"] == ["fragment_reassembly", "queued_followup"]
	assert "at least one full FRAGMENT_SIZE fragment is present and not accepted" in contract["fragment_checks"]
	assert "at least one terminal short fragment is present and accepted" in contract["fragment_checks"]
	assert "storedEncoded is false" in contract["queued_followup_checks"]
	assert "encodedOnPop is true" in contract["queued_followup_checks"]
	assert "the final queued follow-up event has queueEmptyAfterPop true" in contract["queued_followup_checks"]
	assert contract["retail_provenance_required_for_closure"] is True
	assert spec["report_columns"] == [
		"sequence",
		"fragmentStart",
		"fragmentLength",
		"accumulatedLength",
		"accepted",
		"reassembledPayloadHash",
		"queuedMessageSequence",
		"storedEncoded",
		"encodedOnPop",
		"queueEmptyAfterPop",
		"datagramHash",
	]

	assert "FRAGMENT_SIZE = 1300" in tool
	assert "def validate_fragment_queue_timing_dict" in tool
	assert "\"quake_live_fragment_queue_timing\"" in tool
	assert "full FRAGMENT_SIZE fragments must not be accepted" in tool
	assert "terminal short fragments must be accepted" in tool
	assert "queued follow-up messages must be stored unencoded" in tool
	assert "queued follow-up messages must be encoded on pop" in tool
	assert "last queued follow-up event must empty the queue" in tool
	assert "validate_fragment_queue_timing_dict" in trace_init
	assert "FragmentTimingError" in trace_init
	assert "test_fragment_queue_timing_validator_accepts_retail_timing_report" in trace_tests
	assert "test_fragment_queue_timing_validator_requires_retail_provenance_for_closure" in trace_tests

	assert spec["checklist_effect"] == {
		"new_checked_fragment_queue_timing_validation_row": True,
		"fragmented_snapshot_queued_followup_row_closed": False,
		"capture_rows_remain_open": True,
	}
	assert spec["parity_estimate"]["overall_network_protocol_before_percent"] == 90
	assert spec["parity_estimate"]["overall_network_protocol_after_percent"] == 90
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_before_percent"] == 0
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_after_percent"] == 0

	assert "- [x] Add fragmented snapshot/queued follow-up timing report validation gates" in checklist
	assert "- [ ] Validate fragmented snapshot plus queued follow-up timing against a" in checklist
	assert "docs/reverse-engineering/network-fragment-queue-timing-validation-2026-06-05.md" in checklist
	assert "Network Fragment Queue Timing Validation" in note
	assert "No retail packet capture is claimed by" in note
	assert "The actual fragmented snapshot plus queued follow-up" in note
	assert "Residual fragment/queue timing validation update, 2026-06-05:" in plan
	assert "stored unencoded" in plan
	assert "encoded only when popped" in plan

	blocked_rows = {row["row_id"]: row for row in blockers["blocked_checklist_rows"]}
	assert blocked_rows["fragmented_snapshot_queued_followup"]["status"] == "external_evidence_required"
	assert blockers["checklist_effect"]["new_checked_fragment_queue_timing_validation_row"] is True
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_fragment_queue_timing_validation_gate_requires_retail_capture" in spec["assertion_tests"]


def test_networking_2_invalid_lc_probe_validation_gate_requires_retail_probe() -> None:
	spec = _networking_2_invalid_lc_probe_validation_spec()
	note = _read(NETWORKING_2_INVALID_LC_PROBE_VALIDATION_AUDIT_PATH)
	checklist = _read(OUTSTANDING_WORK_CHECKLIST_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)
	blockers = _networking_2_capture_blockers_spec()
	hardening = _networking_2_hardening_spec()
	tool = _read(REPO_ROOT / "tools/trace/invalid_lc_probe.py")
	trace_init = _read(REPO_ROOT / "tools/trace/__init__.py")
	trace_tests = _read(REPO_ROOT / "tools/tests/test_trace_harness.py")

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["status"] == "completed_invalid_lc_probe_validation_gate_no_retail_probe_claimed"
	assert spec["runtime_launch_required"] is False
	assert spec["game_launch_required"] is False
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-protocol-hardening-parity-2026-06-05.json",
		"docs/reverse-engineering/network-residual-capture-blockers-2026-06-05.json",
	]
	assert spec["source_files"] == [
		"tools/trace/invalid_lc_probe.py",
		"tools/trace/__init__.py",
		"tools/tests/test_trace_harness.py",
	]
	assert spec["supported_checklist_row"] == "Probe invalid-`lc` malicious packet behavior against retail before claiming exact crash/drop equivalence."

	contract = spec["tool_contract"]
	assert contract["module"] == "tools.trace.invalid_lc_probe"
	assert contract["function"] == "validate_invalid_lc_probe_dict"
	assert contract["format"] == "quake_live_invalid_lc_probe"
	assert contract["protocol"] == 91
	field_tables = {table["name"]: table for table in contract["field_tables"]}
	assert field_tables["entityStateFields"]["field_count"] == 58
	assert field_tables["entityStateFields"]["source_guard"] == "MSG_ReadDeltaEntity: invalid field count <lc>"
	assert field_tables["playerStateFields"]["field_count"] == 58
	assert field_tables["playerStateFields"]["source_guard"] == "MSG_ReadDeltaPlayerstate: invalid field count <lc>"
	assert "lc exceeds field_count" in contract["malicious_input_checks"]
	assert "closure mode requires at least one hashed artifact" in contract["retail_observation_checks"]
	assert "crash classification requires a crash_dump artifact" in contract["retail_observation_checks"]
	assert "classification is err_drop" in contract["source_observation_checks"]
	assert contract["accepted_capture_types"] == [
		"controlled_retail_probe",
		"known_good_byte_fixture",
		"protocol91_demo_transcript",
		"retail_packet_capture",
	]
	assert contract["retail_provenance_required_for_closure"] is True
	assert spec["report_columns"] == [
		"probe_id",
		"protocol",
		"field_table",
		"field_count",
		"lc",
		"packet_sha256",
		"retail_classification",
		"observed_message",
		"artifact_type",
		"artifact_sha256",
		"source_classification",
		"source_error_message",
	]

	assert "FIELD_TABLES" in tool
	assert "\"entityStateFields\"" in tool
	assert "\"playerStateFields\"" in tool
	assert "def validate_invalid_lc_probe_dict" in tool
	assert "\"quake_live_invalid_lc_probe\"" in tool
	assert "invalid-lc lc must exceed the retail field table count" in tool
	assert "retail invalid-lc closure requires at least one hashed artifact" in tool
	assert "retail crash classification requires a crash_dump artifact" in tool
	assert "source classification must be err_drop" in tool
	assert "validate_invalid_lc_probe_dict" in trace_init
	assert "InvalidLcProbeError" in trace_init
	assert "test_invalid_lc_probe_validator_accepts_controlled_retail_report" in trace_tests
	assert "test_invalid_lc_probe_validator_requires_retail_provenance_and_hashed_artifacts" in trace_tests

	assert spec["checklist_effect"] == {
		"new_checked_invalid_lc_probe_validation_row": True,
		"invalid_lc_retail_probe_row_closed": False,
		"capture_rows_remain_open": True,
	}
	assert spec["parity_estimate"]["overall_network_protocol_before_percent"] == 90
	assert spec["parity_estimate"]["overall_network_protocol_after_percent"] == 90
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_before_percent"] == 0
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_after_percent"] == 0

	assert "- [x] Add invalid-`lc` controlled retail probe report validation gates" in checklist
	assert "- [ ] Probe invalid-`lc` malicious packet behavior against retail before" in checklist
	assert "docs/reverse-engineering/network-invalid-lc-probe-validation-2026-06-05.md" in checklist
	assert "Network Invalid-lc Probe Validation" in note
	assert "No retail probe is claimed by" in note
	assert "source observation must be `err_drop`" in note
	assert "Residual invalid-`lc` probe validation update, 2026-06-05:" in plan
	assert "at least one hashed retail evidence" in plan

	assert hardening["completion_status"]["remaining_gaps"][1] == "Byte-for-byte malicious-packet behavior still needs external capture or controlled retail probing before claiming exact retail crash/drop equivalence."
	blocked_rows = {row["row_id"]: row for row in blockers["blocked_checklist_rows"]}
	assert blocked_rows["invalid_lc_retail_probe"]["status"] == "external_runtime_probe_required"
	assert blockers["checklist_effect"]["new_checked_invalid_lc_probe_validation_row"] is True
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_invalid_lc_probe_validation_gate_requires_retail_probe" in spec["assertion_tests"]


def test_networking_2_snapshot_field_decode_validation_gate_requires_retail_capture() -> None:
	spec = _networking_2_snapshot_field_decode_validation_spec()
	note = _read(NETWORKING_2_SNAPSHOT_FIELD_DECODE_VALIDATION_AUDIT_PATH)
	checklist = _read(OUTSTANDING_WORK_CHECKLIST_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)
	blockers = _networking_2_capture_blockers_spec()
	player_spec = _networking_2_playerstate_fields_spec()
	entity_spec = _networking_2_entitystate_fields_spec()
	tool = _read(REPO_ROOT / "tools/trace/snapshot_decode.py")
	trace_init = _read(REPO_ROOT / "tools/trace/__init__.py")
	trace_tests = _read(REPO_ROOT / "tools/tests/test_trace_harness.py")

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["status"] == "completed_snapshot_field_decode_validation_gate_no_retail_capture_claimed"
	assert spec["runtime_launch_required"] is False
	assert spec["game_launch_required"] is False
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-playerstate-fields-parity-2026-06-05.json",
		"docs/reverse-engineering/network-entitystate-fields-parity-2026-06-05.json",
		"docs/reverse-engineering/network-demo-capture-replay-validation-2026-06-05.json",
		"docs/reverse-engineering/network-residual-capture-blockers-2026-06-05.json",
	]
	assert spec["source_files"] == [
		"tools/trace/snapshot_decode.py",
		"tools/trace/__init__.py",
		"tools/tests/test_trace_harness.py",
	]
	assert spec["supported_checklist_row"] == "Verify end-to-end retail snapshot capture/decode parity for playerStateFields and entityStateFields."

	contract = spec["tool_contract"]
	assert contract["module"] == "tools.trace.snapshot_decode"
	assert contract["function"] == "validate_snapshot_field_decode_dict"
	assert contract["format"] == "quake_live_snapshot_field_decode"
	assert contract["protocol"] == 91
	field_tables = {table["name"]: table for table in contract["field_tables"]}
	assert field_tables["playerStateFields"] == {
		"name": "playerStateFields",
		"field_count": 58,
		"spec_source": "docs/reverse-engineering/network-playerstate-fields-parity-2026-06-05.json",
	}
	assert field_tables["entityStateFields"] == {
		"name": "entityStateFields",
		"field_count": 58,
		"spec_source": "docs/reverse-engineering/network-entitystate-fields-parity-2026-06-05.json",
	}
	assert "observed field indexes, bits, and wire_kind match the retail source-of-truth specs when supplied" in contract["field_decode_checks"]
	assert "entityStateFields source_alias entries such as retailEventData may validate against the retail generic1 slot" in contract["field_decode_checks"]
	assert "at least one decoded snapshot frame is present" in contract["snapshot_checks"]
	assert contract["retail_provenance_required_for_closure"] is True
	assert spec["report_columns"] == [
		"capture_id",
		"protocol",
		"field_table",
		"field_count",
		"decode_hash",
		"observed_field",
		"observed_index",
		"observed_bits",
		"observed_wire_kind",
		"value_hash",
		"messageNum",
		"serverTime",
		"deltaNum",
		"packetEntityCount",
		"playerStateHash",
		"entityStateHash",
		"packetEntitiesHash",
	]

	assert player_spec["retail_table"]["field_count"] == 58
	assert entity_spec["retail_table"]["field_count"] == 58
	assert player_spec["source_of_truth"]["entries"][49]["field"] == "jumpTime"
	assert entity_spec["source_of_truth"]["entries"][33]["source_alias"] == "retailEventData"

	assert "FIELD_TABLE_NAMES = (\"playerStateFields\", \"entityStateFields\")" in tool
	assert "EXPECTED_FIELD_COUNT = 58" in tool
	assert "def validate_snapshot_field_decode_dict" in tool
	assert "\"quake_live_snapshot_field_decode\"" in tool
	assert "field_count must be {EXPECTED_FIELD_COUNT}" in tool
	assert "wire_kind does not match spec" in tool
	assert "source_alias" in tool
	assert "snapshot decode snapshots must not be empty" in tool
	assert "validate_snapshot_field_decode_dict" in trace_init
	assert "SnapshotDecodeError" in trace_init
	assert "test_snapshot_field_decode_validator_accepts_player_and_entity_decode_report" in trace_tests
	assert "test_snapshot_field_decode_validator_rejects_field_table_drift" in trace_tests

	assert spec["checklist_effect"] == {
		"new_checked_snapshot_field_decode_validation_row": True,
		"snapshot_field_capture_decode_row_closed": False,
		"capture_rows_remain_open": True,
	}
	assert spec["parity_estimate"]["overall_network_protocol_before_percent"] == 90
	assert spec["parity_estimate"]["overall_network_protocol_after_percent"] == 90
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_before_percent"] == 0
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_after_percent"] == 0

	assert "- [x] Add snapshot field decode report validation gates for future" in checklist
	assert "- [ ] Verify end-to-end retail snapshot capture/decode parity for" in checklist
	assert "docs/reverse-engineering/network-snapshot-field-decode-validation-2026-06-05.md" in checklist
	assert "Network Snapshot Field Decode Validation" in note
	assert "No retail packet capture or protocol-91" in note
	assert "source aliases such as `retailEventData`" in note
	assert "Residual snapshot field decode validation update, 2026-06-05:" in plan
	assert "source-of-truth spec checks" in plan

	blocked_rows = {row["row_id"]: row for row in blockers["blocked_checklist_rows"]}
	assert blocked_rows["snapshot_field_capture_decode"]["status"] == "external_evidence_required"
	assert blockers["checklist_effect"]["new_checked_snapshot_field_decode_validation_row"] is True
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_snapshot_field_decode_validation_gate_requires_retail_capture" in spec["assertion_tests"]


def test_networking_2_capture_fixture_validation_gate_blocks_unproven_transcripts() -> None:
	spec = _networking_2_capture_fixture_validation_spec()
	note = _read(NETWORKING_2_CAPTURE_FIXTURE_VALIDATION_AUDIT_PATH)
	checklist = _read(OUTSTANDING_WORK_CHECKLIST_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)
	tool = _read(REPO_ROOT / "tools/trace/demo_transcript.py")
	trace_init = _read(REPO_ROOT / "tools/trace/__init__.py")
	trace_tests = _read(REPO_ROOT / "tools/tests/test_trace_harness.py")
	intake_spec = _networking_2_demo_transcript_intake_spec()

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["status"] == "completed_transcript_validation_gate_no_retail_fixture_claimed"
	assert spec["runtime_launch_required"] is False
	assert spec["game_launch_required"] is False
	assert spec["source_files"] == [
		"tools/trace/demo_transcript.py",
		"tools/trace/__init__.py",
		"tools/tests/test_trace_harness.py",
	]

	contract = spec["validator_contract"]
	assert contract["function"] == "tools.trace.demo_transcript.validate_demo_transcript_dict"
	assert contract["format"] == "quake_live_demo_message_transcript"
	assert contract["schema_version"] == 1
	for expected_check in (
		"message_count equals messages length",
		"source_size equals terminator_offset plus the -1/-1 terminator length",
		"message offsets are contiguous from zero",
		"per-message payload_sha256 matches payload_hex",
		"aggregate payload_sha256 matches concatenated payloads",
		"retail closure mode requires provenance metadata",
	):
		assert expected_check in contract["checks"]
	assert contract["retail_provenance_keys"] == [
		"source",
		"capture_type",
		"capture_date_utc",
		"retail_build",
	]
	assert contract["accepted_capture_types"] == [
		"retail_packet_capture",
		"protocol91_demo_transcript",
		"known_good_byte_fixture",
	]

	assert "RETAIL_CAPTURE_TYPES" in tool
	assert "RETAIL_PROVENANCE_KEYS" in tool
	assert "def validate_demo_transcript_dict" in tool
	assert "source_size != terminator_offset + 8" in tool
	assert "message_count != len(messages)" in tool
	assert "payload_sha256 mismatch" in tool
	assert "retail transcript requires provenance metadata" in tool
	assert "capture_type is not recognized" in tool
	assert "validate_demo_transcript_dict" in trace_init
	assert "test_demo_transcript_validator_requires_retail_provenance_for_closure" in trace_tests
	assert "test_demo_transcript_validator_rejects_corrupt_hashes_and_offsets" in trace_tests

	assert intake_spec["validation_gate"] == "docs/reverse-engineering/network-capture-fixture-validation-2026-06-05.md"
	assert "validate_demo_transcript_dict" in intake_spec["tool_contract"]["entry_points"]
	assert spec["checklist_effect"] == {
		"new_checked_fixture_validation_row": True,
		"byte_for_byte_replay_fixture_row_closed": False,
		"capture_rows_remain_open": True,
	}
	assert spec["parity_estimate"]["overall_network_protocol_before_percent"] == 90
	assert spec["parity_estimate"]["overall_network_protocol_after_percent"] == 90
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_before_percent"] == 0
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_after_percent"] == 0

	assert "- [x] Add protocol-91 transcript validation gates for hashes, offsets," in checklist
	assert "- [ ] Commit at least one retail packet capture, protocol-91 demo transcript" in checklist
	assert "docs/reverse-engineering/network-capture-fixture-validation-2026-06-05.md" in checklist
	assert "Network Capture Fixture Validation" in note
	assert "does not claim that retail packet or demo evidence is now committed" in note
	assert "The actual" in note
	assert "Residual capture-fixture validation update, 2026-06-05:" in plan
	assert "The actual" in plan
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_capture_fixture_validation_gate_blocks_unproven_transcripts" in spec["assertion_tests"]


def test_networking_2_demo_transcript_intake_supports_textual_byte_fixture_submission() -> None:
	spec = _networking_2_demo_transcript_intake_spec()
	note = _read(NETWORKING_2_DEMO_TRANSCRIPT_INTAKE_AUDIT_PATH)
	checklist = _read(OUTSTANDING_WORK_CHECKLIST_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)
	cl_main = _read(CL_MAIN_PATH)
	tool = _read(REPO_ROOT / "tools/trace/demo_transcript.py")
	trace_init = _read(REPO_ROOT / "tools/trace/__init__.py")
	trace_tests = _read(REPO_ROOT / "tools/tests/test_trace_harness.py")

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["status"] == "completed_transcript_intake_tooling_no_retail_transcript_claimed"
	assert spec["runtime_launch_required"] is False
	assert spec["game_launch_required"] is False
	assert spec["source_files"] == [
		"tools/trace/demo_transcript.py",
		"tools/trace/__init__.py",
		"tools/tests/test_trace_harness.py",
	]

	anchor = spec["retail_source_anchor"]
	assert anchor["writer"] == "CL_WriteDemoMessage"
	assert anchor["reader"] == "CL_ReadDemoMessage"
	assert anchor["terminator"] == "CL_StopRecord_f"
	assert "records begin with a little-endian int32 serverMessageSequence" in anchor["observed_contract"]
	assert "CL_StopRecord_f writes the -1/-1 terminator" in anchor["observed_contract"]

	write_demo = _function_block(cl_main, "void CL_WriteDemoMessage")
	_assert_order(
		write_demo,
		"len = clc.serverMessageSequence;",
		"swlen = LittleLong( len );",
		"FS_Write (&swlen, 4, clc.demofile);",
		"len = msg->cursize - headerBytes;",
		"swlen = LittleLong(len);",
		"FS_Write (&swlen, 4, clc.demofile);",
		"FS_Write ( msg->data + headerBytes, len, clc.demofile );",
	)
	read_demo = _function_block(cl_main, "void CL_ReadDemoMessage")
	_assert_order(
		read_demo,
		"r = FS_Read( &s, 4, clc.demofile);",
		"clc.serverMessageSequence = LittleLong( s );",
		"r = FS_Read (&buf.cursize, 4, clc.demofile);",
		"buf.cursize = LittleLong( buf.cursize );",
		"if ( buf.cursize == -1 ) {",
		"if ( buf.cursize > buf.maxsize ) {",
		"CL_ReadDemoMessage: demoMsglen > MAX_MSGLEN",
		"r = FS_Read( buf.data, buf.cursize, clc.demofile );",
	)
	stop_record = _function_block(cl_main, "void CL_StopRecord_f")
	assert "len = -1;" in stop_record
	assert "FS_Write (&len, 4, clc.demofile);" in stop_record

	assert "MAX_MSGLEN = 16384" in tool
	assert "struct.unpack_from(\"<ii\", data, offset)" in tool
	assert "payload.hex(\" \")" in tool
	assert "payload_sha256" in tool
	assert "demo file ended without a -1/-1 terminator" in tool
	assert "python -m tools.trace.demo_transcript" in spec["tool_contract"]["entry_points"]
	assert spec["tool_contract"]["output_format"] == "quake_live_demo_message_transcript"
	assert spec["tool_contract"]["payload_bytes_committed_as"] == "lowercase space-separated hex plus SHA-256"
	assert spec["tool_contract"]["provenance_required_for_retail_closure"] is True
	assert spec["local_artifact_inventory"]["classification"] == "local generated demos, not committed retail evidence"
	assert spec["checklist_effect"] == {
		"new_checked_intake_tooling_row": True,
		"byte_for_byte_replay_fixture_row_closed": False,
		"capture_rows_remain_open": True,
	}
	assert spec["parity_estimate"]["overall_network_protocol_before_percent"] == 90
	assert spec["parity_estimate"]["overall_network_protocol_after_percent"] == 90
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_before_percent"] == 0
	assert spec["parity_estimate"]["byte_for_byte_capture_evidence_after_percent"] == 0
	assert "parse_demo_bytes" in trace_init
	assert "test_demo_transcript_parses_quake_live_demo_envelope" in trace_tests
	assert "test_demo_transcript_rejects_invalid_envelopes" in trace_tests

	assert "- [x] Add protocol-91 demo transcript intake tooling so future retail `.dm_91`" in checklist
	assert "- [ ] Commit at least one retail packet capture, protocol-91 demo transcript" in checklist
	assert "docs/reverse-engineering/network-demo-transcript-intake-2026-06-05.md" in checklist
	assert "Network Demo Transcript Intake" in note
	assert "It does not claim that a retail" in note
	assert "is now committed." in note
	assert "The byte-for-byte replay fixture row and downstream capture-diff rows remain" in note
	assert "Residual demo-transcript intake update, 2026-06-05:" in plan
	assert "Local ignored `.dm_91`" in plan
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_demo_transcript_intake_supports_textual_byte_fixture_submission" in spec["assertion_tests"]


def test_networking_2_protocol_hardening_invalid_lc_fragments_rings_and_stale_deltas() -> None:
	spec = _networking_2_hardening_spec()
	msg_c = _read(MSG_C_PATH)
	net_chan = _read(NET_CHAN_PATH)
	cl_parse = _read(CL_PARSE_PATH)
	cl_net_chan = _read(CL_NET_CHAN_PATH)
	sv_client = _read(SV_CLIENT_PATH)
	sv_net_chan = _read(SV_NET_CHAN_PATH)
	sv_snapshot = _read(SV_SNAPSHOT_PATH)
	hlil_part04 = _read(HLIL_PART04_PATH)
	hlil_part05 = _read(HLIL_PART05_PATH)
	audit_note = _read(NETWORKING_2_HARDENING_AUDIT_PATH)
	plan = _read(NETWORKING_2_PLAN_PATH)

	assert spec["schema_version"] == 1
	assert spec["last_updated"] == "2026-06-05"
	assert spec["depends_on"] == [
		"docs/reverse-engineering/network-protocol-parity-ledger-2026-06-05.json",
		"docs/reverse-engineering/network-protocol-header-transport-spec-2026-06-05.json",
		"docs/reverse-engineering/network-client-message-parser-grammar-2026-06-05.json",
		"docs/reverse-engineering/network-xor-codec-parity-2026-06-05.json",
		"docs/reverse-engineering/network-usercmd-delta-parity-2026-06-05.json",
		"docs/reverse-engineering/network-playerstate-fields-parity-2026-06-05.json",
		"docs/reverse-engineering/network-entitystate-fields-parity-2026-06-05.json",
		"docs/reverse-engineering/network-oob-connect-auth-parity-2026-06-05.json",
		"docs/reverse-engineering/network-demo-capture-replay-validation-2026-06-05.json",
	]
	assert spec["owning_retail_binary"]["path"] == "assets/quakelive/quakelive_steam.exe"

	lanes = {lane["id"]: lane for lane in spec["hardening_lanes"]}
	assert set(lanes) == {
		"entity_delta_invalid_lc",
		"playerstate_delta_invalid_lc",
		"netchan_fragment_edge_cases",
		"client_server_command_ring_wraparound",
		"server_client_command_ring_wraparound",
		"reliable_acknowledge_bounds",
		"xor_command_ring_sanitized_wraparound",
		"stale_delta_frame_rejection",
		"server_snapshot_delta_source_aging",
		"usercmd_count_bounds",
		"bad_opcode_and_read_past_end",
	}
	assert lanes["entity_delta_invalid_lc"]["field_count"] == 58
	assert lanes["entity_delta_invalid_lc"]["source_patch"] is True
	assert lanes["entity_delta_invalid_lc"]["error_message"] == "MSG_ReadDeltaEntity: invalid field count %i"
	assert lanes["playerstate_delta_invalid_lc"]["field_count"] == 58
	assert lanes["playerstate_delta_invalid_lc"]["source_patch"] is True
	assert lanes["playerstate_delta_invalid_lc"]["error_message"] == "MSG_ReadDeltaPlayerstate: invalid field count %i"
	assert "no committed HLIL bounds guard" in lanes["entity_delta_invalid_lc"]["retail_observation"]
	assert lanes["netchan_fragment_edge_cases"]["source_patch"] is False
	assert lanes["stale_delta_frame_rejection"]["stale_parse_entities_threshold"] == 1920
	assert lanes["xor_command_ring_sanitized_wraparound"]["ring_mask"] == "MAX_RELIABLE_COMMANDS - 1"
	assert lanes["usercmd_count_bounds"]["diagnostics"] == [
		"cmdCount < 1",
		"cmdCount > MAX_PACKET_USERCMDS",
	]

	vectors = {vector["id"]: vector for vector in spec["negative_vectors"]}
	assert set(vectors) == {
		"entity_lc_above_field_count",
		"playerstate_lc_above_field_count",
		"fragment_start_gap",
		"fragment_negative_length",
		"reliable_ack_too_old",
		"snapshot_parse_entities_too_old",
		"cmd_count_too_large",
	}
	assert vectors["entity_lc_above_field_count"]["input"] == {"lc": 59, "field_count": 58}
	assert vectors["playerstate_lc_above_field_count"]["expected"] == "ERR_DROP before reading playerStateFields[59]"
	assert vectors["fragment_start_gap"]["expected"] == "return qfalse and preserve the accumulated fragment buffer"
	assert vectors["cmd_count_too_large"]["expected"] == "return before MSG_ReadDeltaUsercmdKey"

	read_entity = _function_block(msg_c, "void MSG_ReadDeltaEntity")
	_assert_order(
		read_entity,
		"numFields = sizeof(entityStateFields)/sizeof(entityStateFields[0]);",
		"lc = MSG_ReadByte(msg);",
		"if ( lc < 0 || lc > numFields ) {",
		"Com_Error( ERR_DROP, \"MSG_ReadDeltaEntity: invalid field count %i\", lc );",
		"for ( i = 0, field = entityStateFields ; i < lc ; i++, field++ ) {",
		"for ( i = lc, field = &entityStateFields[lc] ; i < numFields ; i++, field++ ) {",
	)
	assert read_entity.index("Com_Error( ERR_DROP, \"MSG_ReadDeltaEntity: invalid field count %i\", lc );") < read_entity.index(
		"field = &entityStateFields[lc]"
	)

	read_playerstate = _function_block(msg_c, "void MSG_ReadDeltaPlayerstate")
	_assert_order(
		read_playerstate,
		"numFields = sizeof( playerStateFields ) / sizeof( playerStateFields[0] );",
		"lc = MSG_ReadByte(msg);",
		"if ( lc < 0 || lc > numFields ) {",
		"Com_Error( ERR_DROP, \"MSG_ReadDeltaPlayerstate: invalid field count %i\", lc );",
		"for ( i = 0, field = playerStateFields ; i < lc ; i++, field++ ) {",
		"for ( i=lc,field = &playerStateFields[lc];i<numFields; i++, field++) {",
	)
	assert read_playerstate.index(
		"Com_Error( ERR_DROP, \"MSG_ReadDeltaPlayerstate: invalid field count %i\", lc );"
	) < read_playerstate.index("field = &playerStateFields[lc]")
	assert _netfield_count(msg_c, "entityStateFields") == lanes["entity_delta_invalid_lc"]["field_count"]
	assert _netfield_count(msg_c, "playerStateFields") == lanes["playerstate_delta_invalid_lc"]["field_count"]

	process = _function_block(net_chan, "qboolean Netchan_Process( netchan_t *chan, msg_t *msg )")
	_assert_order(
		process,
		"sequence = MSG_ReadLong( msg );",
		"if ( sequence & FRAGMENT_BIT ) {",
		"sequence &= ~FRAGMENT_BIT;",
		"if ( chan->sock == NS_SERVER && NET_ProtocolUsesNetchanClientQport() ) {",
		"(void)MSG_ReadShort( msg );",
		"if ( fragmented ) {",
		"fragmentStart = MSG_ReadShort( msg );",
		"fragmentLength = MSG_ReadShort( msg );",
		"if ( sequence <= chan->incomingSequence ) {",
		"return qfalse;",
		"if ( sequence != chan->fragmentSequence ) {",
		"chan->fragmentSequence = sequence;",
		"chan->fragmentLength = 0;",
		"if ( fragmentStart != chan->fragmentLength ) {",
		"Com_Printf( \"%s:Dropped a message fragment\\n\"",
		"return qfalse;",
		"if ( fragmentLength < 0 || msg->readcount + fragmentLength > msg->cursize ||",
		"chan->fragmentLength + fragmentLength > sizeof( chan->fragmentBuffer ) ) {",
		"Com_Printf (\"%s:illegal fragment length\\n\"",
		"return qfalse;",
		"if ( fragmentLength == FRAGMENT_SIZE ) {",
		"return qfalse;",
		"if ( chan->fragmentLength > msg->maxsize ) {",
		"return qfalse;",
		"msg->cursize = chan->fragmentLength + 4;",
		"msg->readcount = 4;",
		"msg->bit = 32;",
	)

	parse_command = _function_block(cl_parse, "void CL_ParseCommandString")
	_assert_order(
		parse_command,
		"seq = MSG_ReadLong( msg );",
		"s = MSG_ReadString( msg );",
		"if ( clc.serverCommandSequence >= seq ) {",
		"return;",
		"clc.serverCommandSequence = seq;",
		"index = seq & (MAX_RELIABLE_COMMANDS-1);",
		"Q_strncpyz( clc.serverCommands[ index ], s, sizeof( clc.serverCommands[ index ] ) );",
	)

	parse_server = _function_block(cl_parse, "void CL_ParseServerMessage")
	_assert_order(
		parse_server,
		"clc.reliableAcknowledge = MSG_ReadLong( msg );",
		"if ( clc.reliableAcknowledge < clc.reliableSequence - MAX_RELIABLE_COMMANDS ) {",
		"clc.reliableAcknowledge = clc.reliableSequence;",
		"if ( msg->readcount > msg->cursize ) {",
		"Com_Error (ERR_DROP,\"CL_ParseServerMessage: read past end of server message\");",
		"cmd = MSG_ReadByte( msg );",
		"default:",
		"Com_Error (ERR_DROP,\"CL_ParseServerMessage: Illegible server message %d\\n\", cmd);",
	)

	client_encode = _function_block(cl_net_chan, "static void CL_Netchan_Encode")
	client_decode = _function_block(cl_net_chan, "static void CL_Netchan_Decode")
	server_encode = _function_block(sv_net_chan, "static void SV_Netchan_Encode")
	server_decode = _function_block(sv_net_chan, "static void SV_Netchan_Decode")
	for block, ring_source in (
		(client_encode, "clc.serverCommands[ reliableAcknowledge & (MAX_RELIABLE_COMMANDS-1) ]"),
		(client_decode, "clc.reliableCommands[ reliableAcknowledge & (MAX_RELIABLE_COMMANDS-1) ]"),
		(server_encode, "client->lastClientCommandString"),
		(server_decode, "client->reliableCommands[ reliableAcknowledge & (MAX_RELIABLE_COMMANDS-1) ]"),
	):
		assert ring_source in block
		_assert_order(
			block,
			"index = 0;",
			"if (!string[index])",
			"index = 0;",
			"if (string[index] > 127 || string[index] == '%') {",
			"key ^= '.' << (i & 1);",
		)

	client_command = _function_block(sv_client, "static qboolean SV_ClientCommand")
	_assert_order(
		client_command,
		"seq = MSG_ReadLong( msg );",
		"s = MSG_ReadString( msg );",
		"if ( cl->lastClientCommand >= seq ) {",
		"return qtrue;",
		"if ( seq > cl->lastClientCommand + 1 ) {",
		"SV_DropClient( cl, \"Lost reliable commands\" );",
		"return qfalse;",
		"cl->lastClientCommand = seq;",
		"Com_sprintf(cl->lastClientCommandString, sizeof(cl->lastClientCommandString), \"%s\", s);",
	)

	user_move = _function_block(sv_client, "static void SV_UserMove")
	_assert_order(
		user_move,
		"cmdCount = MSG_ReadByte( msg );",
		"if ( cmdCount < 1 ) {",
		"Com_Printf( \"cmdCount < 1\\n\" );",
		"return;",
		"if ( cmdCount > MAX_PACKET_USERCMDS ) {",
		"Com_Printf( \"cmdCount > MAX_PACKET_USERCMDS\\n\" );",
		"return;",
		"key ^= Com_HashKey(cl->reliableCommands[ cl->reliableAcknowledge & (MAX_RELIABLE_COMMANDS-1) ], 32);",
		"MSG_ReadDeltaUsercmdKey( msg, key, oldcmd, cmd );",
	)

	execute = _function_block(sv_client, "void SV_ExecuteClientMessage")
	_assert_order(
		execute,
		"serverId = MSG_ReadLong( msg );",
		"cl->messageAcknowledge = MSG_ReadLong( msg );",
		"if (cl->messageAcknowledge < 0) {",
		"return;",
		"cl->reliableAcknowledge = MSG_ReadLong( msg );",
		"(void)MSG_ReadByte( msg );",
		"if (cl->reliableAcknowledge < cl->reliableSequence - MAX_RELIABLE_COMMANDS) {",
		"cl->reliableAcknowledge = cl->reliableSequence;",
		"return;",
		"if ( serverId != sv.serverId && !*cl->downloadName && !strstr(cl->lastClientCommandString, NET_GetDownloadNextCommand()) ) {",
		"SV_SendClientGameState( cl );",
		"return;",
		"if ( c == clc_move ) {",
		"SV_UserMove( cl, msg, qtrue );",
		"} else if ( c == clc_moveNoDelta ) {",
		"SV_UserMove( cl, msg, qfalse );",
		"Com_Printf( \"WARNING: bad command byte for client %i\\n\", cl - svs.clients );",
	)

	update_commands = _function_block(sv_snapshot, "void SV_UpdateServerCommandsToClient")
	_assert_order(
		update_commands,
		"for ( i = client->reliableAcknowledge + 1 ; i <= client->reliableSequence ; i++ ) {",
		"MSG_WriteByte( msg, svc_serverCommand );",
		"MSG_WriteLong( msg, i );",
		"MSG_WriteString( msg, client->reliableCommands[ i & (MAX_RELIABLE_COMMANDS-1) ] );",
	)

	parse_snapshot = _function_block(cl_parse, "void CL_ParseSnapshot")
	_assert_order(
		parse_snapshot,
		"old = &cl.snapshots[newSnap.deltaNum & PACKET_MASK];",
		"if ( !old->valid ) {",
		"Com_Printf (\"Delta from invalid frame (not supposed to happen!).\\n\");",
		"} else if ( old->messageNum != newSnap.deltaNum ) {",
		"Com_Printf (\"Delta frame too old.\\n\");",
		"} else if ( cl.parseEntitiesNum - old->parseEntitiesNum > MAX_PARSE_ENTITIES-128 ) {",
		"Com_Printf (\"Delta parseEntitiesNum too old.\\n\");",
		"} else {",
		"newSnap.valid = qtrue;",
		"if ( !newSnap.valid ) {",
		"return;",
	)

	write_snapshot = _function_block(sv_snapshot, "static void SV_WriteSnapshotToClient")
	_assert_order(
		write_snapshot,
		"if ( client->deltaMessage <= 0 || client->state != CS_ACTIVE ) {",
		"oldframe = NULL;",
		"lastframe = 0;",
		"} else if ( client->netchan.outgoingSequence - client->deltaMessage",
		">= (PACKET_BACKUP - 3) ) {",
		"oldframe = NULL;",
		"lastframe = 0;",
		"oldframe = &client->frames[ client->deltaMessage & PACKET_MASK ];",
		"if ( oldframe->first_entity <= svs.nextSnapshotEntities - svs.numSnapshotEntities ) {",
		"oldframe = NULL;",
		"lastframe = 0;",
	)

	read_entity_hlil = hlil_part04.split("004d5ac0    int32_t sub_4d5ac0", 1)[1].split("004d5d50", 1)[0]
	_assert_order(
		read_entity_hlil,
		"uint32_t i_4 = zx.d(sub_4d4c70(ebx, 8))",
		"if (i_4 s> 0)",
		"arg4 = &data_542228",
		"do",
		"arg4 += 0xc",
		"if (i_4 s< 0x3a)",
		"int32_t i_3 = 0x3a - i_4",
	)
	read_player_hlil = hlil_part04.split("004d66c0    uint32_t sub_4d66c0", 1)[1].split("004d6b80", 1)[0]
	_assert_order(
		read_player_hlil,
		"uint32_t i_12 = zx.d(sub_4d4c70(arg2, 8))",
		"if (i_12 s> 0)",
		"void* const edi_1 = &data_5424e0",
		"do",
		"edi_1 += 0xc",
		"if (i_12 s< 0x3a)",
		"int32_t i_11 = 0x3a - i_12",
	)
	process_hlil = hlil_part04.split("004d7640    int32_t sub_4d7640", 1)[1].split("004d7970", 1)[0]
	_assert_order(
		process_hlil,
		"ebx_1 &= 0x7fffffff",
		"if (ebx_1 s> ecx_2)",
		"if (var_c != ecx_7)",
		"\"%s:Dropped a message fragment\\n\"",
		"\"%s:illegal fragment length\\n\"",
		"*(arg5 + 0x10) = esi[0xb] + 4",
		"*(arg5 + 0x14) = 4",
		"*(arg5 + 0x18) = 0x20",
	)
	execute_hlil = hlil_part04.split("004e05c0    uint32_t sub_4e05c0", 1)[1].split("004e0750", 1)[0]
	_assert_order(
		execute_hlil,
		"uint32_t eax = sub_4d5020(arg2)",
		"uint32_t i = sub_4d5020(arg2)",
		"arg1[0x4102] = sub_4d5020(arg2)",
		"sub_4d4fc0(arg2)",
		"while (i == 4)",
		"if (i == 2)",
		"return sub_4e0320(arg2, 1)",
		"if (i == 3)",
		"return sub_4e0320(arg2, 0)",
	)
	snapshot_hlil = hlil_part04.split("004bd350    uint32_t sub_4bd350", 1)[1].split("004bd790", 1)[0]
	_assert_order(
		snapshot_hlil,
		"Delta frame too old.\\n",
		"data_1471e98 - esi[0xa4] s<= 0x780",
		"Delta parseEntitiesNum too old.\\n",
	)
	write_snapshot_hlil = hlil_part05.split("004e50e0    void* __convention", 1)[1].split("004e5680", 1)[0]
	_assert_order(
		write_snapshot_hlil,
		"if (ecx_3 s<= 0 || *arg1 != 4)",
		"var_8_1 = 0",
		"if (eax - ecx_3 s< 0x1d)",
		"Delta request from out of da",
		"ebx = nullptr",
		"var_8_1 = 0",
		"sub_4d4dc0(arg2, var_8_1)",
	)

	anchors = {item["symbol"]: item for item in spec["retail_anchors"]}
	assert anchors["MSG_ReadDeltaEntity"]["address"] == "0x004D5AC0"
	assert anchors["MSG_ReadDeltaPlayerstate"]["address"] == "0x004D66C0"
	assert anchors["Netchan_Process"]["address"] == "0x004D7640"
	assert anchors["CL_ParseSnapshot"]["address"] == "0x004BD350"
	assert anchors["SV_UserMove"]["address"] == "0x004E0320"
	assert anchors["SV_ExecuteClientMessage"]["address"] == "0x004E05C0"
	assert anchors["SV_WriteSnapshotToClient"]["address"] == "0x004E50E0"

	assert spec["completion_status"]["status"] == "completed_source_patch_and_static_hardening_assertions"
	assert spec["completion_status"]["source_patch_required"] is True
	assert spec["completion_status"]["runtime_launch_required"] is False
	assert spec["completion_status"]["focused_task_parity_before_percent"] == 58
	assert spec["completion_status"]["focused_task_parity_after_percent"] == 88
	assert spec["completion_status"]["overall_network_protocol_parity_before_percent"] == 86
	assert spec["completion_status"]["overall_network_protocol_parity_after_percent"] == 87
	assert "tests/test_netcode_parity_manifest.py::test_networking_2_protocol_hardening_invalid_lc_fragments_rings_and_stale_deltas" in spec["assertion_tests"]

	assert "Network Protocol Hardening Parity" in audit_note
	assert "Invalid entity `lc`" in audit_note
	assert "Focused protocol-hardening slice: `58%` before, `88%` after." in audit_note
	assert "Hardening pass: invalid `lc`, fragment edge cases, command-ring wraparound, stale delta frames" in plan
	assert "network-protocol-hardening-parity-2026-06-05.json" in plan
	assert "focused protocol-hardening slice" in plan
