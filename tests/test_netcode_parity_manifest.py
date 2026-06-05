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
NETWORKING_2_USERCMD_DELTA_PATH = REPO_ROOT / "docs/reverse-engineering/network-usercmd-delta-parity-2026-06-05.json"
NETWORKING_2_USERCMD_DELTA_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-usercmd-delta-parity-2026-06-05.md"
NETWORKING_2_PLAYERSTATE_FIELDS_PATH = REPO_ROOT / "docs/reverse-engineering/network-playerstate-fields-parity-2026-06-05.json"
NETWORKING_2_PLAYERSTATE_FIELDS_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-playerstate-fields-parity-2026-06-05.md"
NETWORKING_2_ENTITYSTATE_FIELDS_PATH = REPO_ROOT / "docs/reverse-engineering/network-entitystate-fields-parity-2026-06-05.json"
NETWORKING_2_ENTITYSTATE_FIELDS_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-entitystate-fields-parity-2026-06-05.md"
NETWORKING_2_OOB_CONNECT_AUTH_PATH = REPO_ROOT / "docs/reverse-engineering/network-oob-connect-auth-parity-2026-06-05.json"
NETWORKING_2_OOB_CONNECT_AUTH_AUDIT_PATH = REPO_ROOT / "docs/reverse-engineering/network-oob-connect-auth-parity-2026-06-05.md"
NETWORKING_2_PLAN_PATH = REPO_ROOT / "docs/plans/2026-06-05-networking-2.md"
QCOMMON_H_PATH = REPO_ROOT / "src/code/qcommon/qcommon.h"
Q_SHARED_PATH = REPO_ROOT / "src/code/game/q_shared.h"
HUFFMAN_C_PATH = REPO_ROOT / "src/code/qcommon/huffman.c"
MSG_C_PATH = REPO_ROOT / "src/code/qcommon/msg.c"
SV_SNAPSHOT_PATH = REPO_ROOT / "src/code/server/sv_snapshot.c"
SV_MAIN_PATH = REPO_ROOT / "src/code/server/sv_main.c"
CL_INPUT_PATH = REPO_ROOT / "src/code/client/cl_input.c"
CL_MAIN_PATH = REPO_ROOT / "src/code/client/cl_main.c"
CLIENT_H_PATH = REPO_ROOT / "src/code/client/client.h"
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


def _networking_2_usercmd_delta_spec() -> dict:
	return json.loads(_read(NETWORKING_2_USERCMD_DELTA_PATH))


def _networking_2_playerstate_fields_spec() -> dict:
	return json.loads(_read(NETWORKING_2_PLAYERSTATE_FIELDS_PATH))


def _networking_2_entitystate_fields_spec() -> dict:
	return json.loads(_read(NETWORKING_2_ENTITYSTATE_FIELDS_PATH))


def _networking_2_oob_connect_auth_spec() -> dict:
	return json.loads(_read(NETWORKING_2_OOB_CONNECT_AUTH_PATH))


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
		"iVar3 = FUN_004d9060(uVar1,\"connectResponse\");",
		"FUN_004d6d00(0,&DAT_01617bfc,local_1c,local_18,local_14,local_10,local_c,uVar1);",
	):
		assert expected in ghidra_decompile

	for expected in (
		"004b9150    int32_t sub_4b9150(int32_t arg1 @ esi)",
		"004b9182      if (eax_1 == 3 || eax_1 == 4)",
		"004b91c1                      sub_4c9b60(0, \"CL_CheckForResend: bad cls.state\")",
		"004b9221                  sub_4d9620(&var_808, \"protocol\", sub_4d9220(&data_52e930))",
		"004b928b                  __builtin_strncpy(dest: &var_408, src: \"connect \", n: 9)",
		"004b9386              __builtin_strncpy(dest: &var_9804, src: \"getchallenge \", n: 0xd)",
		"004b9418              eax_1 = sub_4d6fd0(0, eax_13 + 0x19, &var_9808, data_15f6750, data_15f6754,",
		"004bbbe0    void* sub_4bbbe0",
		"004bbc7d  if (sub_4d9060(eax_4, \"challengeResponse\") == 0)",
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
	check_resend = _function_block(cl_main, "void CL_CheckForResend( void ) {")
	connectionless = _function_block(cl_main, "void CL_ConnectionlessPacket( netadr_t from, msg_t *msg )")
	packet_event = _function_block(cl_main, "void CL_PacketEvent( netadr_t from, msg_t *msg )")

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
	assert "classic UDP pk3 autodownload lane" in " ".join(entries["ClassicUdpAutodownloadCompatibility"]["compatibility_notes"])
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
	assert "compatibility_notes" in send_snapshot_entry
	assert "classic SV_WriteDownloadToClient" in " ".join(send_snapshot_entry["compatibility_notes"])

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
		"SV_WriteDownloadToClient( client, &msg );",
		"if ( msg.overflowed ) {",
		"MSG_Clear (&msg);",
		"SV_SendMessageToClient( &msg, client );",
	)

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


def test_networking_2_focused_parity_ledger_maps_first_plan_entry() -> None:
	ledger = _networking_2_ledger()
	msg_source = _read(MSG_C_PATH)
	qcommon_h = _read(QCOMMON_H_PATH)
	aliases = json.loads(_read(REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json"))["quakelive_steam"]
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
		"return 0;",
	)

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
	assert anchors["CL_RetailClientMessageFlags_source_stub"]["address"] is None

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
