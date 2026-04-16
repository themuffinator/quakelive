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

	assert 'if ( var->flags & CVAR_ROM )' in block
	assert 'if ( var->flags & CVAR_INIT )' in block
	assert 'if ( var->flags & CVAR_LATCH )' in block
	assert 'if ( (var->flags & CVAR_CHEAT) && !cvar_cheats->integer )' in block
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
