from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _extract_function_block(text: str, signature: str) -> str:
	start = text.find(signature)
	if start == -1:
		raise AssertionError(f"function signature not found: {signature}")

	brace_start = text.find("{", start)
	if brace_start == -1:
		raise AssertionError(f"opening brace not found for: {signature}")

	depth = 0
	for index in range(brace_start, len(text)):
		char = text[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return text[start : index + 1]

	raise AssertionError(f"unterminated function block for: {signature}")


def test_cvar_set2_keeps_retail_console_write_guards_only() -> None:
	cvar = (REPO_ROOT / "src/code/qcommon/cvar.c").read_text(encoding="utf-8")
	block = _extract_function_block(cvar, "cvar_t *Cvar_Set2( const char *var_name, const char *value, qboolean force ) {")

	assert 'Com_DPrintf( "Cvar_Set2: %s (%s)\\n"' in block
	assert 'if ( var->flags & CVAR_ROM )' in block
	assert 'if ( var->flags & CVAR_INIT )' in block
	assert 'if ( var->flags & CVAR_LATCH )' in block
	assert 'if ( (var->flags & CVAR_CHEAT) && !cvar_cheats->integer )' in block
	assert 'Cvar_PublishChange( var );' in block
	assert 'if ( var->flags & CVAR_PROTECTED )' not in block
	assert 'if ( var->flags & CVAR_VM_CREATED )' not in block
	assert 'is protected and may only be set by the engine or VM' not in block
	assert 'is protected and may only be set by the VM' not in block


def test_cvar_set_helpers_account_for_full_token_length() -> None:
	cvar = (REPO_ROOT / "src/code/qcommon/cvar.c").read_text(encoding="utf-8")
	set_block = _extract_function_block(cvar, "void Cvar_Set_f( void ) {")
	setcloud_block = _extract_function_block(cvar, "void Cvar_SetCloud_f( void ) {")

	assert 'len = strlen( Cmd_Argv( i ) ) + 1;' in set_block
	assert 'len = strlen ( Cmd_Argv( i ) + 1 );' not in set_block
	assert 'len = strlen( Cmd_Argv( i ) ) + 1;' in setcloud_block
	assert 'len = strlen ( Cmd_Argv( i ) + 1 );' not in setcloud_block


def test_bounded_cvars_preserve_retail_discrete_endpoint_validation() -> None:
	cvar = (REPO_ROOT / "src/code/qcommon/cvar.c").read_text(encoding="utf-8")
	q_shared = (REPO_ROOT / "src/code/game/q_shared.h").read_text(encoding="utf-8")
	block = _extract_function_block(cvar, "static const char *Cvar_GetValidatedValueString( const cvar_t *var, const char *value, char *buffer, int bufferSize ) {")

	assert "#define CVAR_BOUNDED_DISCRETE\t0x2000" in q_shared
	assert "if ( var->flags & CVAR_BOUNDED_DISCRETE ) {" in block
	assert "if ( numericValue > var->min ) {" in block
	assert "return var->maxString;" in block
	assert 'Com_sprintf( buffer, bufferSize, "%g", var->max );' in block


def test_cvar_core_management_reconstructs_quake_live_wiring() -> None:
	cvar = (REPO_ROOT / "src/code/qcommon/cvar.c").read_text(encoding="utf-8")
	q_shared = (REPO_ROOT / "src/code/game/q_shared.h").read_text(encoding="utf-8")
	aliases = (REPO_ROOT / "references/analysis/quakelive_symbol_aliases.json").read_text(encoding="utf-8")
	hlil = (
		REPO_ROOT
		/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt"
	).read_text(encoding="utf-8")
	hlil_strings = (
		REPO_ROOT
		/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt"
	).read_text(encoding="utf-8")

	get_block = _extract_function_block(cvar, "cvar_t *Cvar_Get( const char *var_name, const char *var_value, int flags ) {")
	set_block = _extract_function_block(cvar, "void Cvar_Set_f( void ) {")
	publish_block = _extract_function_block(cvar, "static void Cvar_PublishChange( const cvar_t *var ) {")
	flag_block = _extract_function_block(cvar, "static void Cvar_UpdateFlagConflicts( cvar_t *var ) {")

	assert '"sub_4CCE90": "Cvar_Set2"' in aliases
	assert '"sub_4CE0D0": "Cvar_Get"' in aliases
	assert '"sub_4F3630": "QLWebView_PublishCvarChange"' in aliases
	assert "004ccf1c          void** eax_6 = sub_4ce0d0(arg1, arg3, ebx, 0x80)" in hlil
	assert "004ccf32              eax_6[7] = eax_7 | 0x800" in hlil
	assert "004cd777  if (data_145ca58 == 0 && *(data_1205e28 + 0x30) == 0)" in hlil
	assert "Cvar_Set2: %s (%s)\\n" in hlil_strings
	assert "%s will be changed to %s upon restarting.\\n" in hlil_strings
	assert "Refusing to set %s during initialization due to CVAR_GAMERULE\\n" in hlil_strings

	assert "#define\tMAX_CVARS\t2048" in cvar
	assert "#define CVAR_GAMERULE\t0x100000" in q_shared
	assert "var->flags |= CVAR_PROTECTED;" in cvar
	assert "Cvar_UpdateFlagConflicts( var );" in get_block
	assert "Warning: cvar \\\"%s\\\" cannot be both CVAR_CHEAT and CVAR_ARCHIVE - dropping CVAR_ARCHIVE\\n" in flag_block
	assert "Warning: cvar \\\"%s\\\" cannot be both CVAR_CHEAT and CVAR_REPLICATED - dropping CVAR_REPLICATED\\n" in flag_block
	assert 'if ( !com_fullyInitialized && !Cvar_VariableIntegerValue( "dedicated" ) ) {' in set_block
	assert "CVAR_GAMERULE" in set_block
	assert "CVAR_LATCH" in publish_block
	assert "var->latchedString" in publish_block


def test_cvar_integer_cache_uses_retail_hex_parser() -> None:
	cvar = (REPO_ROOT / "src/code/qcommon/cvar.c").read_text(encoding="utf-8")
	hlil = (
		REPO_ROOT
		/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt"
	).read_text(encoding="utf-8")
	hlil_strings = (
		REPO_ROOT
		/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt"
	).read_text(encoding="utf-8")

	parse_block = _extract_function_block(cvar, "static int Cvar_ParseInteger( const char *value ) {")
	get_block = _extract_function_block(cvar, "cvar_t *Cvar_Get( const char *var_name, const char *var_value, int flags ) {")
	set_block = _extract_function_block(cvar, "cvar_t *Cvar_Set2( const char *var_name, const char *value, qboolean force ) {")

	assert "004cccc0    int32_t __fastcall sub_4cccc0(int32_t arg1)" in hlil
	assert 'char const* const var_10_1 = "0x%08x"' in hlil
	assert 'char const data_540ecc[0x7] = "0x%08x", 0' in hlil_strings
	assert 'if ( strstr( value, "0x" ) ) {' in parse_block
	assert 'sscanf( value, "0x%08x", &integerValue );' in parse_block
	assert "return atoi( value );" in parse_block
	assert "var->integer = Cvar_ParseInteger( var->string );" in get_block
	assert "var->integer = Cvar_ParseInteger( var->string );" in set_block


def test_cvar_vm_bounded_registration_matches_retail_wrapper_and_layout() -> None:
	cvar = (REPO_ROOT / "src/code/qcommon/cvar.c").read_text(encoding="utf-8")
	qcommon = (REPO_ROOT / "src/code/qcommon/qcommon.h").read_text(encoding="utf-8")
	q_shared = (REPO_ROOT / "src/code/game/q_shared.h").read_text(encoding="utf-8")
	cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
	hlil = (
		REPO_ROOT
		/ "references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt"
	).read_text(encoding="utf-8")

	get_bounded_block = _extract_function_block(
		cvar,
		"cvar_t *Cvar_GetBounded( const char *var_name, const char *var_value, const char *minValue, const char *maxValue, int flags ) {",
	)
	register_block = _extract_function_block(
		cvar,
		"void\tCvar_Register( vmCvar_t *vmCvar, const char *varName, const char *defaultValue, int flags ) {",
	)
	register_bounded_block = _extract_function_block(
		cvar,
		"cvar_t\t*Cvar_RegisterBounded( vmCvar_t *vmCvar, const char *varName, const char *defaultValue, const char *minimumValue, const char *maximumValue, int flags ) {",
	)
	range_import_block = _extract_function_block(
		cl_cgame,
		"static void QDECL QL_CG_trap_Cvar_RegisterRange( vmCvar_t *vmCvar, const char *varName, const char *defaultValue, const char *minimumValue, const char *maximumValue, int flags ) {",
	)

	assert "004ce447  arg1[4] = result[7]" in hlil
	assert "004ce460    int32_t* sub_4ce460" in hlil
	assert "arg6 | 0x1000" in hlil
	assert "int\t\t\tinteger;\n\tint\t\t\tflags;\n\tchar\t\tstring[MAX_CVAR_VALUE_STRING];" in q_shared
	assert "cvar_t\t*Cvar_RegisterBounded(" in qcommon
	assert "flags |= CVAR_VM_CREATED;" in get_bounded_block
	assert 'Com_Error( ERR_FATAL, "Cvar_Get: NULL parameter" );' in get_bounded_block
	assert "vmCvar->flags = cv->flags;" in register_block
	assert "Cvar_GetBounded( varName, defaultValue, minimumValue, maximumValue, flags | CVAR_VM_CREATED );" in register_bounded_block
	assert "return cv;" in register_bounded_block
	assert "vmCvar->flags = cv->flags;" in register_bounded_block
	assert "Cvar_RegisterBounded( vmCvar, varName, defaultValue, minimumValue, maximumValue, flags );" in range_import_block
