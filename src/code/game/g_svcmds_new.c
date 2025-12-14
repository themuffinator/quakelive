
/*
=================
Cmd_ShuffleTeams_f
=================
*/
void Cmd_ShuffleTeams_f( void ) {
	if ( !Team_IsAutoShuffleArmed() ) {
		G_AutoShuffleCountdown_Arm( 5000 );
		Team_ClampWarmupToShuffleCountdown();
		trap_SendServerCommand( -1, "print \"Teams will be shuffled in 5 seconds.\n\"" );
	}
}

/*
=================
Cmd_CoinToss_f
=================
*/
void Cmd_CoinToss_f( void ) {
	int result = rand() % 2;
	trap_SendServerCommand( -1, va("cp \"Coin Toss: %s\n\"", result ? "HEADS" : "TAILS" ) );
	trap_SendServerCommand( -1, va("print \"Coin Toss: %s\n\"", result ? "HEADS" : "TAILS" ) );
}

/*
=================
Cmd_RandomMap_f
=================
*/
void Cmd_RandomMap_f( void ) {
	// For now, this just restarts the map as we don't have a map list loaded
	// Ideally this would pick from a map cycle
	trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
}
