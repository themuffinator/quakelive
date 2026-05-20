from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_qagame_exposes_retail_vote_state_helpers() -> None:
	local_h = _read("src/code/game/g_local.h")
	vote_c = _read("src/code/game/g_vote.c")

	assert "VOTE_STATE_NONE = 0," in local_h
	assert "VOTE_STATE_ELIGIBLE," in local_h
	assert "VOTE_STATE_YES," in local_h
	assert "VOTE_STATE_NO," in local_h
	assert "VOTE_STATE_FORCE_PASS," in local_h
	assert "VOTE_STATE_FORCE_VETO" in local_h
	assert "voteState;\t\t\t// retail-style per-client vote role/state latch" in local_h
	assert "int G_UpdateVoteCounts( void );" in local_h
	assert "qboolean G_TryExecuteVoteString( const char *voteString );" in local_h

	assert "int G_UpdateVoteCounts( void ) {" in vote_c
	assert "case VOTE_STATE_FORCE_PASS:" in vote_c
	assert "case VOTE_STATE_FORCE_VETO:" in vote_c
	assert 'trap_SendServerCommand( -1, va( "print \\"%s passed the vote.\\\\n\\"", client->pers.netname ) );' in vote_c
	assert 'trap_SendServerCommand( -1, va( "print \\"%s vetoed the vote.\\\\n\\"", client->pers.netname ) );' in vote_c
	assert 'return VOTE_RESULT_PASSED;' in vote_c
	assert 'return VOTE_RESULT_FAILED;' in vote_c


def test_vote_commands_seed_and_consume_per_client_vote_state() -> None:
	game_cmds = _read("src/code/game/g_cmds.c")

	assert "level.clients[voteSelection].pers.voteState = VOTE_STATE_NONE;" in game_cmds
	assert "level.clients[voteSelection].pers.voteState = VOTE_STATE_ELIGIBLE;" in game_cmds
	assert "client->pers.voteState = VOTE_STATE_YES;" in game_cmds
	assert "client->pers.voteState = voteState;" in game_cmds
	assert "voteState = VOTE_STATE_FORCE_PASS;" in game_cmds
	assert "voteState = VOTE_STATE_FORCE_VETO;" in game_cmds
	assert "G_UpdateVoteCounts();" in game_cmds
	assert 'ent->client->pers.voteState = VOTE_STATE_FORCE_PASS;' in game_cmds


def test_checkvote_uses_retail_vote_helpers_and_timeout_string() -> None:
	game_main = _read("src/code/game/g_main.c")
	vote_c = _read("src/code/game/g_vote.c")
	qagame_mapping = _read("docs/reverse-engineering/qagame-mapping.md")

	assert "if ( G_TryExecuteVoteString( level.voteString ) == qfalse ) {" in game_main
	assert "voteResult = G_UpdateVoteCounts();" in game_main
	assert "G_ClearVoteState();" in game_main
	assert 'trap_SendServerCommand( -1, "print \\"Voting time has expired.\\n\\"" );' in game_main
	assert 'trap_SendServerCommand( -1, "print \\"Vote passed.\\n\\"" );' in game_main
	assert 'trap_SendServerCommand( -1, "print \\"Vote failed.\\n\\"" );' in game_main
	assert "level.voteExecuteTime = level.time + 3000;" in game_main
	assert "`0x100588F0` | `G_UpdateVoteCounts` | `g_vote.c::G_UpdateVoteCounts`" in qagame_mapping
	assert "`0x10058AB0` | `G_TryExecuteVoteString` | `g_vote.c::G_TryExecuteVoteString`" in qagame_mapping
	assert "`0x10059130` | `G_ClearVoteState` | `g_vote.c::G_ClearVoteState`" in qagame_mapping
	assert "does not preserve these exact helpers as separate named functions" not in qagame_mapping

	assert "qboolean G_TryExecuteVoteString( const char *voteString ) {" in vote_c
	assert '!Q_stricmp( command, "cointoss" )' in vote_c
	assert '!Q_stricmp( command, "random" )' in vote_c
	assert '!Q_stricmp( command, "randommap" )' in vote_c
	assert '!Q_stricmp( command, "loadouts" )' in vote_c
	assert '!Q_stricmp( command, "ammo" )' in vote_c
	assert '!Q_stricmp( command, "shuffle" ) || !Q_stricmp( command, "shuffle_teams" )' in vote_c
	assert '!Q_stricmp( command, "teamsize" )' in vote_c
	assert '!Q_stricmp( command, "timers" )' in vote_c
	assert '!Q_stricmp( command, "weaprespawn" )' in vote_c
	assert 'trap_SendServerCommand( -1, "print \\"Usage: ^3\\\\callvote random <2 to 100>^7\\\\n\\"" );' in vote_c
	assert 'trap_SendServerCommand( -1, "print \\"       ^7Picks a number from 1 to <value>\\\\n\\"" );' in vote_c
	assert 'trap_SendServerCommand( -1, "print \\"       ^2callvote random 2 ^7mimics flipping a coin\\\\n\\"" );' in vote_c
	assert 'trap_SendServerCommand( -1, va( "print \\"^3Random number is: ^5%d^7\\\\n\\"", ( rand() % upperLimit ) + 1 ) );' in vote_c
	assert 'trap_SendServerCommand( -1, "print \\"^3Valid loadout options are:    ^5ON    ^5OFF^7\\\\n\\"" );' in vote_c
	assert 'trap_SendServerCommand( -1, "print \\"^3Valid ammo options are:    ^5GLOBAL    ^5WEAP^7\\\\n\\"" );' in vote_c
