
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
	fileHandle_t	f;
	int				len;
	char			*buf, *p, *next;
	char			*maps[1024];
	int				count;
	int				i;
	int				selection;

	// Try to load mapcycle.txt
	len = trap_FS_FOpenFile( "mapcycle.txt", &f, FS_READ );
	count = 0;

	if ( len > 0 ) {
		buf = G_Alloc( len + 1 );
		if ( !buf ) {
			trap_FS_FCloseFile( f );
			return;
		}
		trap_FS_Read( buf, len, f );
		buf[len] = 0;
		trap_FS_FCloseFile( f );

		p = buf;
		while ( *p ) {
			// skip whitespace
			while ( *p && *p <= ' ' ) {
				p++;
			}
			if ( !*p ) {
				break;
			}

			// find end of line
			next = p;
			while ( *next && *next != '\n' ) {
				next++;
			}
			if ( *next ) {
				*next++ = 0;
			}

			if ( count < 1024 ) {
				maps[count] = p;
				count++;
			}

			p = next;
		}
	}

	if ( count == 0 ) {
		// Fallback: list all maps
		char	fileList[16384];
		char	*file;
		int		numFiles;

		numFiles = trap_FS_GetFileList( "maps", ".bsp", fileList, sizeof( fileList ) );
		file = fileList;
		for ( i = 0; i < numFiles; i++, file += strlen(file) + 1 ) {
			if ( count < 1024 ) {
				char temp[MAX_QPATH];
				COM_StripExtension( file, temp );
				maps[count] = G_Alloc( strlen(temp) + 1 );
				if ( maps[count] ) {
					strcpy( maps[count], temp );
					count++;
				}
			}
		}
	}

	if ( count == 0 ) {
		trap_SendServerCommand( -1, "print \"No maps found.\n\"" );
		return;
	}

	selection = rand() % count;
	trap_SendConsoleCommand( EXEC_APPEND, va( "map %s\n", maps[selection] ) );
}
