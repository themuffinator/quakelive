/*
===========================================================================
Copyright (C) 1999-2005 Id Software, Inc.

This file is part of Quake III Arena source code.

Quake III Arena source code is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Quake III Arena source code is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
===========================================================================
*/
// console.c

#include "client.h"


int g_console_field_width = 78;


#define	NUM_CON_TIMES 4

#define		CON_TEXTSIZE	32768
#define		CON_NOTIFY_TIME	3000
#define		CONSOLE_CHAR_WIDTH	12
#define		CONSOLE_CHAR_HEIGHT	24
#define		CONSOLE_HOST_FONT_MONO	2
#define		CONSOLE_HOST_SCALE_MULTIPLIER	2.1597f
typedef struct {
	qboolean	initialized;

	short	text[CON_TEXTSIZE];
	int		current;		// line where next message will be printed
	int		x;				// offset in current line for next print
	int		display;		// bottom of console displays this line

	int 	linewidth;		// characters across screen
	int		totallines;		// total lines in console scrollback

	float	xadjust;		// for wide aspect screens

	float	displayFrac;	// aproaches finalFrac at scr_conspeed
	float	finalFrac;		// 0.0 to 1.0 lines of console to display

	int		vislines;		// in scanlines

	int		times[NUM_CON_TIMES];	// cls.realtime time the line was generated
								// for transparent notify lines
	vec4_t	color;
} console_t;

extern	console_t	con;

console_t	con;

cvar_t		*con_background;
cvar_t		*con_height;
cvar_t		*con_matchlimit;
cvar_t		*con_noprint;
cvar_t		*con_opacity;
cvar_t		*con_scale;
cvar_t		*con_speed;
cvar_t		*con_timestamps;

#define	DEFAULT_CONSOLE_WIDTH	78

vec4_t	console_color = {1.0, 1.0, 1.0, 1.0};

/*
================
Con_GetScale
================
*/
static float Con_GetScale( void ) {
	float scale = 0.5f;

	if ( con_scale ) {
		scale = con_scale->value;
	}

	if ( scale <= 0.0f ) {
		scale = 0.5f;
	}

	return Com_Clamp( 0.5f, 1.0f, scale );
}

/*
================
Con_GetPixelScale
================
*/
static float Con_GetPixelScale( void ) {
	float pixelScale;

	pixelScale = Con_GetScale();
	if ( pixelScale <= 0.0f ) {
		pixelScale = 1.0f;
	}

	return pixelScale;
}

/*
================
Con_GetScaledSmallCharWidth
================
*/
static int Con_GetScaledSmallCharWidth( void ) {
	int width;

	width = (int)( CONSOLE_CHAR_WIDTH * Con_GetPixelScale() + 0.5f );
	if ( width < 1 ) {
		width = 1;
	}

	return width;
}

/*
================
Con_GetScaledSmallCharHeight
================
*/
static int Con_GetScaledSmallCharHeight( void ) {
	int height;

	height = (int)( CONSOLE_CHAR_HEIGHT * Con_GetPixelScale() + 0.5f );
	if ( height < 1 ) {
		height = 1;
	}

	return height;
}

/*
================
Con_GetHostTextScale
================
*/
static float Con_GetHostTextScale( int charWidth ) {
	return (float)charWidth * CONSOLE_HOST_SCALE_MULTIPLIER;
}

/*
================
Con_DrawHostText
================
*/
static void Con_DrawHostText( int x, int y, int charWidth, int charHeight, const char *text, const float *color, qboolean forceColor ) {
	float scale;
	const float *drawColor;

	if ( !text || !text[0] ) {
		return;
	}

	scale = Con_GetHostTextScale( charWidth );
	if ( scale <= 0.0f ) {
		return;
	}

	drawColor = color ? color : g_color_table[ColorIndex( COLOR_WHITE )];
	RE_DrawScaledText( x, y + charHeight, text, CONSOLE_HOST_FONT_MONO, scale, 0, NULL, forceColor, drawColor );
}

/*
================
Con_DrawHostChar
================
*/
static void Con_DrawHostChar( int x, int y, int charWidth, int charHeight, int ch, const float *color, qboolean forceColor ) {
	char text[2];

	if ( ch == ' ' ) {
		return;
	}

	text[0] = (char)ch;
	text[1] = '\0';
	Con_DrawHostText( x, y, charWidth, charHeight, text, color, forceColor );
}

/*
================
Con_IsUtf8ContinuationByte
================
*/
static qboolean Con_IsUtf8ContinuationByte( unsigned char ch ) {
	return ( ch & 0xC0 ) == 0x80;
}

/*
================
Con_ClampUtf8Boundary
================
*/
static int Con_ClampUtf8Boundary( const char *text, int index ) {
	int len;

	if ( !text ) {
		return 0;
	}

	len = strlen( text );
	if ( index < 0 ) {
		index = 0;
	} else if ( index > len ) {
		index = len;
	}

	while ( index > 0 && index < len && Con_IsUtf8ContinuationByte( (unsigned char)text[index] ) ) {
		index--;
	}

	return index;
}

/*
================
Con_PrevUtf8CharStart
================
*/
static int Con_PrevUtf8CharStart( const char *text, int index ) {
	if ( !text || index <= 0 ) {
		return 0;
	}

	index--;
	while ( index > 0 && Con_IsUtf8ContinuationByte( (unsigned char)text[index] ) ) {
		index--;
	}

	return index;
}

/*
================
Con_DrawHostField
================
*/
static void Con_DrawHostField( field_t *edit, int x, int y, int charWidth, int charHeight, qboolean showCursor ) {
	int		cursor;
	int		cursorX;
	int		drawBytes;
	int		end;
	int		len;
	int		prefixBytes;
	float	prefixWidth;
	int		start;
	int		visibleChars;
	char	drawText[MAX_STRING_CHARS];

	if ( !edit ) {
		return;
	}

	if ( edit->widthInChars <= 0 ) {
		return;
	}

	len = strlen( edit->buffer );
	cursor = Con_ClampUtf8Boundary( edit->buffer, edit->cursor );
	start = len;
	end = len;
	visibleChars = 0;

	while ( visibleChars < edit->widthInChars && start > 0 ) {
		start = Con_PrevUtf8CharStart( edit->buffer, start );
		visibleChars++;

		if ( visibleChars == edit->widthInChars && cursor < start ) {
			end = Con_PrevUtf8CharStart( edit->buffer, end );
			visibleChars--;
		}

		if ( start <= 0 ) {
			break;
		}
	}

	if ( end < start ) {
		end = start;
	}

	drawBytes = end - start;
	if ( drawBytes >= MAX_STRING_CHARS ) {
		Com_Error( ERR_DROP, "drawBytes >= MAX_STRING_CHARS" );
	}

	Com_Memcpy( drawText, edit->buffer + start, drawBytes );
	drawText[drawBytes] = '\0';

	Con_DrawHostText( x, y, charWidth, charHeight, drawText, g_color_table[ColorIndex( COLOR_WHITE )], qfalse );

	if ( !showCursor ) {
		return;
	}

	if ( (int)( cls.realtime >> 8 ) & 1 ) {
		return;
	}

	prefixBytes = cursor - start;
	if ( prefixBytes < 0 ) {
		prefixBytes = 0;
	} else if ( prefixBytes > drawBytes ) {
		prefixBytes = drawBytes;
	}

	prefixWidth = 0.0f;
	if ( prefixBytes > 0 ) {
		RE_MeasureScaledText( drawText, drawText + prefixBytes, CONSOLE_HOST_FONT_MONO, Con_GetHostTextScale( charWidth ), 0, &prefixWidth, NULL, NULL );
	}

	cursorX = x + (int)( prefixWidth + 0.5f );
	if ( !Key_GetOverstrikeMode() ) {
		cursorX -= charWidth / 2;
	}

	Con_DrawHostText( cursorX, y, charWidth, charHeight, Key_GetOverstrikeMode() ? "_" : "|", g_color_table[ColorIndex( COLOR_WHITE )], qtrue );
}

/*
================
Con_DrawScaledSmallChar
================
*/
static void Con_DrawScaledSmallChar( int x, int y, int width, int height, int ch ) {
	int		row;
	int		col;
	float	frow;
	float	fcol;
	float	size;

	ch &= 255;
	if ( ch == ' ' ) {
		return;
	}

	if ( y < -height ) {
		return;
	}

	row = ch >> 4;
	col = ch & 15;
	frow = row * 0.0625f;
	fcol = col * 0.0625f;
	size = 0.0625f;

	re.DrawStretchPic( x, y, width, height,
		fcol, frow,
		fcol + size, frow + size,
		cls.charSetShader );
}

/*
================
Con_DrawScaledSmallStringColor
================
*/
static void Con_DrawScaledSmallStringColor( int x, int y, int width, int height, const char *string, const vec4_t color ) {
	const char	*s;
	int			xx;

	if ( !string || !string[0] ) {
		return;
	}

	re.SetColor( color );
	s = string;
	xx = x;
	while ( *s ) {
		Con_DrawScaledSmallChar( xx, y, width, height, *s );
		xx += width;
		s++;
	}
	re.SetColor( NULL );
}

/*
================
Con_DrawConsoleLineText
================
*/
static void Con_DrawConsoleLineText( int x, int y, const short *text, int count ) {
	int		currentColor;
	int		charWidth;
	int		charHeight;
	int		i;
	int		bufferIndex;
	int		lastVisible;
	char	buffer[2048];

	if ( !text || count <= 0 ) {
		return;
	}

	charWidth = Con_GetScaledSmallCharWidth();
	charHeight = Con_GetScaledSmallCharHeight();
	currentColor = 7;

	bufferIndex = 0;
	lastVisible = 0;

	for ( i = 0 ; i < count && bufferIndex < (int)sizeof( buffer ) - 1 ; i++ ) {
		int colorIndex;
		int ch;

		ch = text[i] & 0xff;
		if ( ch == ' ' ) {
			buffer[bufferIndex++] = ' ';
			continue;
		}

		colorIndex = ( text[i] >> 8 ) & 7;
		if ( colorIndex != currentColor && bufferIndex < (int)sizeof( buffer ) - 3 ) {
			buffer[bufferIndex++] = '^';
			buffer[bufferIndex++] = (char)( '0' + colorIndex );
			currentColor = colorIndex;
		}

		buffer[bufferIndex++] = (char)ch;
		lastVisible = bufferIndex;
	}

	buffer[lastVisible] = '\0';
	Con_DrawHostText( x, y, charWidth, charHeight, buffer, g_color_table[ColorIndex( COLOR_WHITE )], qfalse );
}

/*
================
Con_GetChatFieldWidthInChars

Returns the retail chat-field width, including the team-chat reduction.
================
*/
static int Con_GetChatFieldWidthInChars( qboolean teamChat ) {
	int width = 73;

	if ( cgvm ) {
		int cgameWidth = VM_Call( cgvm, CG_GET_CHAT_FIELD_WIDTH_IN_CHARS );

		if ( cgameWidth > 0 ) {
			width = cgameWidth;
		}
	}

	if ( teamChat && width > 5 ) {
		width -= 5;
	}

	return width;
}

/*
================
Con_GetChatFieldY

Returns the retail 640-space Y origin for the live chat input field.
================
*/
static int Con_GetChatFieldY( void ) {
	int chatFieldY = 413;

	if ( cgvm ) {
		int cgameY = VM_Call( cgvm, CG_GET_CHAT_FIELD_Y );

		if ( cgameY > 0 ) {
			chatFieldY = cgameY;
		}
	}

	return chatFieldY;
}

/*
================
Con_GetChatFieldPixelWidth

Returns the retail 640-space width for the live chat input field.
================
*/
static int Con_GetChatFieldPixelWidth( void ) {
	int chatFieldWidth = 640;

	if ( cgvm ) {
		int cgameWidth = VM_Call( cgvm, CG_GET_CHAT_FIELD_PIXEL_WIDTH );

		if ( cgameWidth > 0 ) {
			chatFieldWidth = cgameWidth;
		}
	}

	return chatFieldWidth;
}

/*
================
Con_ResetChatField

Clears the live chat field using the retail cgame-selected width.
================
*/
static void Con_ResetChatField( qboolean teamChat ) {
	Field_Clear( &chatField );
	chatField.widthInChars = Con_GetChatFieldWidthInChars( teamChat );
}

/*
================
Con_GetTimestampTime

Returns the retail console timestamp source, preferring cgame physics time.
================
*/
static int Con_GetTimestampTime( void ) {
	int timestampTime;

	timestampTime = ( cls.state >= CA_CONNECTED ) ? cl.serverTime : cls.realtime;
	if ( cgvm && con_timestamps && con_timestamps->integer == 1 ) {
		int physicsTime = VM_Call( cgvm, CG_GET_PHYSICS_TIME );

		if ( physicsTime > 0 ) {
			timestampTime = physicsTime;
		}
	}

	if ( timestampTime < 0 ) {
		timestampTime = 0;
	}

	return timestampTime;
}

/*
================
Con_FormatTimestamp

Builds the retail `[m:ss.mmm]` notify/console prefix.
================
*/
static void Con_FormatTimestamp( char *buffer, int bufferSize ) {
	int timestampTime;
	int totalSeconds;
	int minutes;
	int seconds;
	int millis;

	if ( !buffer || bufferSize <= 0 ) {
		return;
	}

	timestampTime = Con_GetTimestampTime();
	totalSeconds = timestampTime / 1000;
	minutes = totalSeconds / 60;
	seconds = totalSeconds % 60;
	millis = timestampTime % 1000;

	Com_sprintf( buffer, bufferSize, "[%d:%02d.%03d] ", minutes, seconds, millis );
}

/*
================
Con_GetChatPrompt

Returns the retail live-chat prompt string and field skip width.
================
*/
static const char *Con_GetChatPrompt( int *skip ) {
	if ( chat_reply ) {
		if ( skip ) {
			*skip = 7;
		}
		return "reply:";
	}

	if ( chat_team ) {
		if ( skip ) {
			*skip = 11;
		}
		return "say team:";
	}

	if ( skip ) {
		*skip = 6;
	}
	return "say:";
}


/*
================
Con_ToggleConsole_f
================
*/
void Con_ToggleConsole_f (void) {
	if ( com_allowConsole && !com_allowConsole->integer ) {
		Com_Printf( "com_allowConsole won't allow toggleconsole command\n" );
		return;
	}

	// closing a full screen console restarts the demo loop
	if ( cls.state == CA_DISCONNECTED && cls.keyCatchers == KEYCATCH_CONSOLE ) {
		CL_StartDemoLoop();
		return;
	}

	Field_Clear( &g_consoleField );
	g_consoleField.widthInChars = g_console_field_width;

	Con_ClearNotify ();
	cls.keyCatchers ^= KEYCATCH_CONSOLE;
}

/*
================
Con_MessageMode_f
================
*/
void Con_MessageMode_f (void) {
	chat_playerNum = -1;
	chat_reply = qfalse;
	chat_team = qfalse;
	Con_ResetChatField( qfalse );

	cls.keyCatchers ^= KEYCATCH_MESSAGE;
	if ( cgvm ) {
		VM_Call( cgvm, CG_CHAT_DOWN );
	}
}

/*
================
Con_MessageMode2_f
================
*/
void Con_MessageMode2_f (void) {
	chat_playerNum = -1;
	chat_reply = qfalse;
	chat_team = qtrue;
	Con_ResetChatField( qtrue );
	cls.keyCatchers ^= KEYCATCH_MESSAGE;
	if ( cgvm ) {
		VM_Call( cgvm, CG_CHAT_DOWN );
	}
}

/*
================
Con_MessageMode3_f
================
*/
void Con_MessageMode3_f (void) {
	chat_playerNum = VM_Call( cgvm, CG_CROSSHAIR_PLAYER );
	if ( chat_playerNum < 0 || chat_playerNum >= MAX_CLIENTS ) {
		chat_playerNum = -1;
		return;
	}
	chat_reply = qfalse;
	chat_team = qfalse;
	Con_ResetChatField( qfalse );
	cls.keyCatchers ^= KEYCATCH_MESSAGE;
	if ( cgvm ) {
		VM_Call( cgvm, CG_CHAT_DOWN );
	}
}

/*
================
Con_MessageMode4_f
================
*/
void Con_MessageMode4_f (void) {
	chat_playerNum = VM_Call( cgvm, CG_LAST_ATTACKER );
	if ( chat_playerNum < 0 || chat_playerNum >= MAX_CLIENTS ) {
		chat_playerNum = -1;
		return;
	}
	chat_reply = qfalse;
	chat_team = qfalse;
	Con_ResetChatField( qfalse );
	cls.keyCatchers ^= KEYCATCH_MESSAGE;
	if ( cgvm ) {
		VM_Call( cgvm, CG_CHAT_DOWN );
	}
}

/*
================
Con_Clear_f
================
*/
void Con_Clear_f (void) {
	int		i;

	for ( i = 0 ; i < CON_TEXTSIZE ; i++ ) {
		con.text[i] = (ColorIndex(COLOR_WHITE)<<8) | ' ';
	}

	Con_Bottom();		// go to end
}

						
/*
================
Con_Dump_f

Save the console contents out to a file
================
*/
void Con_Dump_f (void)
{
	int		l, x, i;
	short	*line;
	fileHandle_t	f;
	char	buffer[1024];

	if (Cmd_Argc() != 2)
	{
		Com_Printf ("usage: condump <filename>\n");
		return;
	}

	Com_Printf ("Dumped console text to %s.\n", Cmd_Argv(1) );

	f = FS_FOpenFileWrite( Cmd_Argv( 1 ) );
	if (!f)
	{
		Com_Printf ("ERROR: couldn't open.\n");
		return;
	}

	// skip empty lines
	for (l = con.current - con.totallines + 1 ; l <= con.current ; l++)
	{
		line = con.text + (l%con.totallines)*con.linewidth;
		for (x=0 ; x<con.linewidth ; x++)
			if ((line[x] & 0xff) != ' ')
				break;
		if (x != con.linewidth)
			break;
	}

	// write the remaining lines
	buffer[con.linewidth] = 0;
	for ( ; l <= con.current ; l++)
	{
		line = con.text + (l%con.totallines)*con.linewidth;
		for(i=0; i<con.linewidth; i++)
			buffer[i] = line[i] & 0xff;
		for (x=con.linewidth-1 ; x>=0 ; x--)
		{
			if (buffer[x] == ' ')
				buffer[x] = 0;
			else
				break;
		}
		strcat( buffer, "\n" );
		FS_Write(buffer, strlen(buffer), f);
	}

	FS_FCloseFile( f );
}

/*
================
Con_Find_f
================
*/
void Con_Find_f( void ) {
	int			lineNum;
	int			x;
	int			matches;
	int			limit;
	short		*line;
	const char	*needle;
	char		buffer[1024];

	if ( Cmd_Argc() != 2 ) {
		Com_Printf( "usage: find <substring>  ; This is a case sensitive search of the console history.\n" );
		return;
	}

	needle = Cmd_Argv( 1 );
	limit = ( con_matchlimit && con_matchlimit->integer > 0 ) ? con_matchlimit->integer : 16;
	matches = 0;

	for ( lineNum = con.current - con.totallines + 1 ; lineNum <= con.current ; lineNum++ ) {
		int copyWidth;

		line = con.text + ( lineNum % con.totallines ) * con.linewidth;
		copyWidth = con.linewidth;
		if ( copyWidth >= (int)sizeof( buffer ) ) {
			copyWidth = sizeof( buffer ) - 1;
		}

		for ( x = 0 ; x < copyWidth ; x++ ) {
			buffer[x] = line[x] & 0xff;
		}
		buffer[copyWidth] = '\0';

		for ( x = copyWidth - 1 ; x >= 0 ; x-- ) {
			if ( buffer[x] == ' ' ) {
				buffer[x] = '\0';
				continue;
			}
			break;
		}

		if ( !buffer[0] ) {
			continue;
		}

		if ( strstr( buffer, needle ) && !strstr( buffer, "\\find" ) && !strstr( buffer, "usage: find " ) ) {
			matches++;
			if ( matches <= limit ) {
				if ( matches == 1 ) {
					Com_Printf( "\n## MATCH LIST:\n" );
				}
				Com_Printf( "\n## %s\n", buffer );
			}
		}
	}

	if ( matches >= limit ) {
		Com_Printf( "%d matches found. (Displaying the first %d)\n", matches, limit );
		return;
	}

	Com_Printf( "%d %s found.\n", matches, matches == 1 ? "match" : "matches" );
}

						
/*
================
Con_ClearNotify
================
*/
void Con_ClearNotify( void ) {
	int		i;
	
	for ( i = 0 ; i < NUM_CON_TIMES ; i++ ) {
		con.times[i] = 0;
	}
}

						

/*
================
Con_CheckResize

If the line width has changed, reformat the buffer.
================
*/
void Con_CheckResize (void)
{
	float	scale;
	int		i, j, width, oldwidth, oldtotallines, numlines, numchars;
	MAC_STATIC short	tbuf[CON_TEXTSIZE];

	scale = Con_GetScale();
	width = (int)( (float)cls.glconfig.vidWidth / ( scale * CONSOLE_CHAR_WIDTH ) - 2.0f );

	if (width == con.linewidth)
		return;

	if (width < 1)			// video hasn't been initialized yet
	{
		width = DEFAULT_CONSOLE_WIDTH;
		con.linewidth = width;
		con.totallines = CON_TEXTSIZE / con.linewidth;
		for(i=0; i<CON_TEXTSIZE; i++)

			con.text[i] = (ColorIndex(COLOR_WHITE)<<8) | ' ';
	}
	else
	{
		oldwidth = con.linewidth;
		con.linewidth = width;
		oldtotallines = con.totallines;
		con.totallines = CON_TEXTSIZE / con.linewidth;
		numlines = oldtotallines;

		if (con.totallines < numlines)
			numlines = con.totallines;

		numchars = oldwidth;
	
		if (con.linewidth < numchars)
			numchars = con.linewidth;

		Com_Memcpy (tbuf, con.text, CON_TEXTSIZE * sizeof(short));
		for(i=0; i<CON_TEXTSIZE; i++)

			con.text[i] = (ColorIndex(COLOR_WHITE)<<8) | ' ';


		for (i=0 ; i<numlines ; i++)
		{
			for (j=0 ; j<numchars ; j++)
			{
				con.text[(con.totallines - 1 - i) * con.linewidth + j] =
						tbuf[((con.current - i + oldtotallines) %
							  oldtotallines) * oldwidth + j];
			}
		}

		Con_ClearNotify ();
	}

	con.current = con.totallines - 1;
	con.display = con.current;
	g_console_field_width = con.linewidth;
	g_consoleField.widthInChars = g_console_field_width;
	for ( i = 0 ; i < COMMAND_HISTORY ; i++ ) {
		historyEditLines[i].widthInChars = g_console_field_width;
	}
}


/*
================
Con_Init
================
*/
void Con_Init (void) {
	int		i;

	con_background = Cvar_GetBounded( "con_background", "0", "0", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	con_height = Cvar_GetBounded( "con_height", "0.5", "0.1", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	con_matchlimit = Cvar_Get( "con_matchlimit", "16", 0 );
	con_noprint = Cvar_Get( "con_noprint", "0", 0 );
	con_opacity = Cvar_GetBounded( "con_opacity", "0.9", "0.1", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	con_scale = Cvar_GetBounded( "con_scale", "0.5", "0.5", "1", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	con_speed = Cvar_GetBounded( "con_speed", "3", "0.1", "1000", CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );
	con_timestamps = Cvar_Get( "con_timestamps", "0", CVAR_PROTECTED | CVAR_CLOUD );

	Field_Clear( &g_consoleField );
	g_consoleField.widthInChars = g_console_field_width;
	for ( i = 0 ; i < COMMAND_HISTORY ; i++ ) {
		Field_Clear( &historyEditLines[i] );
		historyEditLines[i].widthInChars = g_console_field_width;
	}

	Cmd_AddCommand ("toggleconsole", Con_ToggleConsole_f);
	Cmd_AddCommand ("messagemode", Con_MessageMode_f);
	Cmd_AddCommand ("messagemode2", Con_MessageMode2_f);
	Cmd_AddCommand ("messagemode3", Con_MessageMode3_f);
	Cmd_AddCommand ("messagemode4", Con_MessageMode4_f);
	Cmd_AddCommand ("clear", Con_Clear_f);
	Cmd_AddCommand ("condump", Con_Dump_f);
	Cmd_AddCommand( "find", Con_Find_f );
}


/*
===============
Con_Linefeed
===============
*/
void Con_Linefeed (qboolean skipnotify)
{
	int		i;

	// mark time for transparent overlay
	if (con.current >= 0)
	{
    if (skipnotify)
		  con.times[con.current % NUM_CON_TIMES] = 0;
    else
		  con.times[con.current % NUM_CON_TIMES] = cls.realtime;
	}

	con.x = 0;
	if (con.display == con.current)
		con.display++;
	con.current++;
	for(i=0; i<con.linewidth; i++)
		con.text[(con.current%con.totallines)*con.linewidth+i] = (ColorIndex(COLOR_WHITE)<<8) | ' ';
}

/*
================
CL_ConsolePrint

Handles cursor positioning, line wrapping, etc
All console printing must go through this in order to be logged to disk
If no console is visible, the text will appear at the top of the game window
================
*/
void CL_ConsolePrint( char *txt ) {
	int		y;
	int		c, l;
	int		color;
	qboolean skipnotify = qfalse;		// NERVE - SMF
	int prev;							// NERVE - SMF
	char	timestamp[32];
	qboolean	timestampPrinted = qfalse;
	int		timestampMode;

	// TTimo - prefix for text that shows up in console but not in notify
	// backported from RTCW
	if ( !Q_strncmp( txt, "[skipnotify]", 12 ) ) {
		skipnotify = qtrue;
		txt += 12;
	}
	
	// for some demos we don't want to ever show anything on the console
	if ( con_noprint && con_noprint->integer ) {
		return;
	}
	
	if (!con.initialized) {
		con.color[0] = 
		con.color[1] = 
		con.color[2] =
		con.color[3] = 1.0f;
		con.linewidth = -1;
		Con_CheckResize ();
		con.initialized = qtrue;
	}

	color = ColorIndex(COLOR_WHITE);

	timestampMode = 0;
	if ( con_timestamps ) {
		timestampMode = con_timestamps->integer;
	}

	if ( timestampMode ) {
		Con_FormatTimestamp( timestamp, sizeof( timestamp ) );
	}

	while ( (c = *txt) != 0 ) {
		if ( !timestampPrinted && timestampMode && con.x == 0 ) {
			// Print timestamp at start of line
			int ts_len = strlen(timestamp);
			int i;
			timestampPrinted = qtrue;

			for ( i = 0; i < ts_len; i++ ) {
				if ( Q_IsColorString( &timestamp[i] ) ) {
					color = ColorIndex( timestamp[i+1] );
					i++;
					continue;
				}
				con.text[(con.current % con.totallines)*con.linewidth+con.x] = (color << 8) | timestamp[i];
				con.x++;
				if (con.x >= con.linewidth) {
					Con_Linefeed(skipnotify);
					con.x = 0;
					// If we wrap inside the timestamp, we do NOT want to print the timestamp again immediately
					// because we are technically still on the same "logical" line or at least we are in the middle of a print.
					// However, if we wrap, we are on a new line.
					// But usually timestamps are short. If they wrap, it's weird.
					// But if they wrap, the next char will trigger this block again if we reset timestampPrinted.
					// If we don't reset it, we continue printing the rest of timestamp.
					// But if we wrap, we are at x=0.
					// If we set timestampPrinted = qtrue, the check !timestampPrinted fails, so we won't recurse.
					// But if we wrap during normal text, we set x=0.
					// Then for next char, check !timestampPrinted.
					// We need to ensure that when we wrap due to normal text, we DO print timestamp on next line if desired?
					// Usually console wrapping implies continuation of same line. Timestamps usually only on new messages (start of print).
					// CL_ConsolePrint handles a string. If the string contains \n, we reset.
					// If the string is long and wraps, it is a continuation. We should NOT print timestamp again.
					// So if we wrap here, we don't change timestampPrinted.
					// Wait, if we wrap inside timestamp, we are still printing timestamp.
					// The issue in previous code was: `timestampPrinted = qfalse;` inside the loop.
					// If I remove that line, then `timestampPrinted` remains true until `\n`.
					// This means wrapped lines (continuations) will NOT have timestamps.
					// This is standard behavior (timestamp only at start of message).
				}
			}
		}

		if ( c == '\n' ) {
			timestampPrinted = qfalse; // reset for next line
		}

		if ( Q_IsColorString( txt ) ) {
			color = ColorIndex( *(txt+1) );
			txt += 2;
			continue;
		}

		// count word length
		for (l=0 ; l< con.linewidth ; l++) {
			if ( txt[l] <= ' ') {
				break;
			}

		}

		// word wrap
		if (l != con.linewidth && (con.x + l >= con.linewidth) ) {
			Con_Linefeed(skipnotify);

		}

		txt++;

		switch (c)
		{
		case '\n':
			Con_Linefeed (skipnotify);
			break;
		case '\r':
			con.x = 0;
			break;
		default:	// display character and advance
			y = con.current % con.totallines;
			con.text[y*con.linewidth+con.x] = (color << 8) | c;
			con.x++;
			if (con.x >= con.linewidth) {
				Con_Linefeed(skipnotify);
				con.x = 0;
			}
			break;
		}
	}


	// mark time for transparent overlay
	if (con.current >= 0) {
		// NERVE - SMF
		if ( skipnotify ) {
			prev = con.current % NUM_CON_TIMES - 1;
			if ( prev < 0 )
				prev = NUM_CON_TIMES - 1;
			con.times[prev] = 0;
		}
		else
		// -NERVE - SMF
			con.times[con.current % NUM_CON_TIMES] = cls.realtime;
	}
}


/*
==============================================================================

DRAWING

==============================================================================
*/


/*
================
Con_DrawInput

Draw the editline after a ] prompt
================
*/
void Con_DrawInput (void) {
	int		charHeight;
	int		charWidth;
	int		y;

	if ( cls.state != CA_DISCONNECTED && !(cls.keyCatchers & KEYCATCH_CONSOLE ) ) {
		return;
	}

	charWidth = Con_GetScaledSmallCharWidth();
	charHeight = Con_GetScaledSmallCharHeight();
	y = con.vislines - ( charHeight * 2 );

	Con_DrawHostChar( con.xadjust + charWidth, y, charWidth, charHeight, ']', con.color, qtrue );
	Con_DrawHostField( &g_consoleField, con.xadjust + 2 * charWidth, y, charWidth, charHeight, qtrue );
}


/*
================
Con_DrawNotify

Draws the last few lines of output transparently over the game top
================
*/
void Con_DrawNotify (void)
{
	int		charHeight;
	int		charWidth;
	int		v;
	short	*text;
	int		i;
	int		time;
	int		skip;
	charWidth = Con_GetScaledSmallCharWidth();
	charHeight = Con_GetScaledSmallCharHeight();

	v = 0;
	for (i= con.current-NUM_CON_TIMES+1 ; i<=con.current ; i++)
	{
		if (i < 0)
			continue;
		time = con.times[i % NUM_CON_TIMES];
		if (time == 0)
			continue;
		time = cls.realtime - time;
		if (time > CON_NOTIFY_TIME)
			continue;
		text = con.text + (i % con.totallines)*con.linewidth;

		if (cl.snap.ps.pm_type != PM_INTERMISSION && cls.keyCatchers & (KEYCATCH_UI | KEYCATCH_CGAME) ) {
			continue;
		}

		Con_DrawConsoleLineText( cl_conXOffset->integer + con.xadjust + charWidth, v, text, con.linewidth );

		v += charHeight;
	}

	re.SetColor( NULL );

	if (cls.keyCatchers & (KEYCATCH_UI | KEYCATCH_CGAME) ) {
		return;
	}

	// draw the chat line
	if ( cls.keyCatchers & KEYCATCH_MESSAGE )
	{
		const char *prompt;
		int chatFieldY;
		float screenX;
		float screenY;
		int promptX;
		int promptY;
		int fieldX;

		prompt = Con_GetChatPrompt( &skip );
		chatFieldY = Con_GetChatFieldY();
		screenX = 8.0f;
		screenY = (float)chatFieldY;
		SCR_AdjustFrom640( &screenX, &screenY, NULL, NULL );
		promptX = (int)( screenX + 0.5f );
		promptY = (int)( screenY + 0.5f );
		fieldX = promptX + skip * charWidth;

		Con_DrawHostText( promptX, promptY, charWidth, charHeight, prompt, g_color_table[ColorIndex( COLOR_WHITE )], qtrue );
		Con_DrawHostField( &chatField, fieldX, promptY, charWidth, charHeight, qtrue );
	}

}

/*
================
Con_DrawSolidConsole

Draws the console with the solid background
================
*/
void Con_DrawSolidConsole( float frac ) {
	int				charHeight;
	int				charWidth;
	int				i, x, y;
	int				rows;
	short			*text;
	int				row;
	int				lines;
//	qhandle_t		conShader;
	vec4_t			color;

	lines = cls.glconfig.vidHeight * frac;
	if (lines <= 0)
		return;

	if (lines > cls.glconfig.vidHeight )
		lines = cls.glconfig.vidHeight;

	// Retail Quake Live keeps the console anchored to the full screen width.
	con.xadjust = 0;
	charWidth = Con_GetScaledSmallCharWidth();
	charHeight = Con_GetScaledSmallCharHeight();

	// draw the background
	y = frac * SCREEN_HEIGHT - 2;
	if ( y < 1 ) {
		y = 0;
	}
	else if ( con_background && con_background->integer > 0 && cls.consoleShader ) {
		SCR_DrawPic( 0, 0, SCREEN_WIDTH, y, cls.consoleShader );
	} else {
		color[0] = 0.0f;
		color[1] = 0.0f;
		color[2] = 0.0f;
		color[3] = con_opacity ? Com_Clamp( 0.1f, 1.0f, con_opacity->value ) : 0.9f;
		SCR_FillRect( 0, 0, SCREEN_WIDTH, y, color );
	}

	color[0] = 1;
	color[1] = 0;
	color[2] = 0;
	color[3] = 1;
	SCR_FillRect( 0, y, SCREEN_WIDTH, 2, color );


	// draw the version number
	i = strlen( Q3_VERSION );
	Con_DrawHostText( cls.glconfig.vidWidth - i * charWidth,
		lines - ( charHeight + charHeight / 2 ),
		charWidth, charHeight, Q3_VERSION, g_color_table[ColorIndex( COLOR_RED )], qtrue );


	// draw the text
	con.vislines = lines;
	rows = ( lines - charHeight ) / charHeight;		// rows of text to draw

	y = lines - ( charHeight * 3 );

	// draw from the bottom up
	if (con.display != con.current)
	{
	// draw arrows to show the buffer is backscrolled
		for (x=0 ; x<con.linewidth ; x+=4)
			Con_DrawHostChar( con.xadjust + ( x + 1 ) * charWidth, y, charWidth, charHeight, '^', g_color_table[ColorIndex( COLOR_RED )], qtrue );
		y -= charHeight;
		rows--;
	}
	
	row = con.display;

	if ( con.x == 0 ) {
		row--;
	}

	for (i=0 ; i<rows ; i++, y -= charHeight, row--)
	{
		if (row < 0)
			break;
		if (con.current - row >= con.totallines) {
			// past scrollback wrap point
			continue;	
		}

		text = con.text + (row % con.totallines)*con.linewidth;
		Con_DrawConsoleLineText( con.xadjust + charWidth, y, text, con.linewidth );
	}

	// draw the input prompt, user text, and cursor if desired
	Con_DrawInput ();

	re.SetColor( NULL );
}



/*
==================
Con_DrawConsole
==================
*/
void Con_DrawConsole( void ) {
	// check for console width changes from a vid mode change
	Con_CheckResize ();

	// if disconnected, render console full screen
	if ( cls.state == CA_DISCONNECTED ) {
		if ( !( cls.keyCatchers & (KEYCATCH_UI | KEYCATCH_CGAME)) ) {
			Con_DrawSolidConsole( 1.0 );
			return;
		}
	}

	if ( con.displayFrac ) {
		Con_DrawSolidConsole( con.displayFrac );
	} else {
		// draw notify lines
		if ( cls.state == CA_ACTIVE ) {
			Con_DrawNotify ();
		}
	}
}

//================================================================

/*
==================
Con_RunConsole

Scroll it up or down
==================
*/
void Con_RunConsole (void) {
	// decide on the destination height of the console
	if ( cls.keyCatchers & KEYCATCH_CONSOLE )
		con.finalFrac = con_height ? Com_Clamp( 0.1f, 1.0f, con_height->value ) : 0.5f;
	else
		con.finalFrac = 0;				// none visible
	
	// scroll towards the destination height
	if (con.finalFrac < con.displayFrac)
	{
		con.displayFrac -= ( con_speed ? Com_Clamp( 0.1f, 1000.0f, con_speed->value ) : 3.0f ) * cls.realFrametime * 0.001f;
		if (con.finalFrac > con.displayFrac)
			con.displayFrac = con.finalFrac;

	}
	else if (con.finalFrac > con.displayFrac)
	{
		con.displayFrac += ( con_speed ? Com_Clamp( 0.1f, 1000.0f, con_speed->value ) : 3.0f ) * cls.realFrametime * 0.001f;
		if (con.finalFrac < con.displayFrac)
			con.displayFrac = con.finalFrac;
	}

}


void Con_PageUp( void ) {
	con.display -= 2;
	if ( con.current - con.display >= con.totallines ) {
		con.display = con.current - con.totallines + 1;
	}
}

void Con_PageDown( void ) {
	con.display += 2;
	if (con.display > con.current) {
		con.display = con.current;
	}
}

void Con_Top( void ) {
	con.display = con.totallines;
	if ( con.current - con.display >= con.totallines ) {
		con.display = con.current - con.totallines + 1;
	}
}

void Con_Bottom( void ) {
	con.display = con.current;
}


void Con_Close( void ) {
	if ( !com_cl_running->integer ) {
		return;
	}
	Field_Clear( &g_consoleField );
	Con_ClearNotify ();
	cls.keyCatchers &= ~KEYCATCH_CONSOLE;
	con.finalFrac = 0;				// none visible
	con.displayFrac = 0;
}
