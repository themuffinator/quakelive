/*
 * Quake Live UI Module -- Ghidra-readable reference header
 *
 * Binary  : uix86.dll
 * Sources : references/symbol-maps/ui.json
 *           references/reverse-engineering/ghidra/uix86/
 *           references/hlil/quakelive/uix86.all/
 *           src-re/ui/include/ui_local.h
 *           src-re/ui/ui_main.c
 *
 * This header is generated for Ghidra and machine-generated source exports.
 * It is not a production runtime header.
 *
 * Symbol coverage: 444 mapped functions
 * Generated from : ui.json
 *
 * Do NOT edit by hand -- regenerate by running:
 *   python3 scripts/ghidra/build_ui_ghidra_reference.py
 */

#ifndef QLR_UI_GHIDRA_REFERENCE_H
#define QLR_UI_GHIDRA_REFERENCE_H

typedef enum { qfalse = 0, qtrue = 1 } qboolean;
typedef int qhandle_t;
typedef int sfxHandle_t;
typedef int fileHandle_t;
typedef float vec_t;
typedef vec_t vec3_t[3];

typedef enum {
	UIMENU_NONE = 0,
	UIMENU_MAIN,
	UIMENU_INGAME,
	UIMENU_NEED_CD,
	UIMENU_BAD_CD_KEY,
	UIMENU_TEAM,
	UIMENU_POSTGAME
} uiMenuCommand_t;

/*
 * Retail syscall-table layout (DAT_106b40a8 in Ghidra).
 * Indices are 32-bit pointer slots.
 */

#define QL_UITRAP_CVAR_REGISTER            0x00	/* slot 0x00 */
#define QL_UITRAP_CVAR_UPDATE              0x01	/* slot 0x01 */
#define QL_UITRAP_CVAR_SET                 0x02	/* slot 0x02 */
#define QL_UITRAP_CVAR_VARIABLEVALUE       0x07	/* slot 0x07 */
#define QL_UITRAP_CVAR_SETVALUE            0x08	/* slot 0x08 */
#define QL_UITRAP_CVAR_INFOSTRINGBUFFER    0x0A	/* slot 0x0A */
#define QL_UITRAP_ARGC                     0x0B	/* slot 0x0B */
#define QL_UITRAP_ARGV                     0x0C	/* slot 0x0C */
#define QL_UITRAP_CMD_EXECUTETEXT          0x0D	/* slot 0x0D */
#define QL_UITRAP_FS_FOPENFILE             0x0F	/* slot 0x0F */
#define QL_UITRAP_FS_READ                  0x10	/* slot 0x10 */
#define QL_UITRAP_FS_WRITE                 0x11	/* slot 0x11 */
#define QL_UITRAP_FS_FCLOSEFILE            0x12	/* slot 0x12 */
#define QL_UITRAP_FS_GETFILELIST           0x13	/* slot 0x13 */
#define QL_UITRAP_R_REGISTERSHADERNOMIP    0x14	/* slot 0x14 */
#define QL_UITRAP_R_DRAWSTRETCHPIC         0x18	/* slot 0x18 */
#define QL_UITRAP_R_MODELBOUNDS            0x1C	/* slot 0x1C */
#define QL_UITRAP_R_REGISTERMODEL          0x1E	/* slot 0x1E */
#define QL_UITRAP_R_REGISTERFONT           0x20	/* slot 0x20 */
#define QL_UITRAP_R_SETCOLOR               0x22	/* slot 0x22 */
#define QL_UITRAP_UPDATESCREEN             0x23	/* slot 0x23 */
#define QL_UITRAP_CM_LERPTAG               0x24	/* slot 0x24 */
#define QL_UITRAP_S_REGISTERSOUND          0x27	/* slot 0x27 */
#define QL_UITRAP_S_STARTLOCALSOUND        0x28	/* slot 0x28 */
#define QL_UITRAP_KEY_KEYNUMTOSTRINGBUF    0x29	/* slot 0x29 */
#define QL_UITRAP_KEY_GETBINDINGBUF        0x2A	/* slot 0x2A */
#define QL_UITRAP_KEY_SETBINDING           0x2B	/* slot 0x2B */
#define QL_UITRAP_KEY_ISDOWN               0x2C	/* slot 0x2C */
#define QL_UITRAP_KEY_GETOVERSTRIKEMODE    0x2D	/* slot 0x2D */
#define QL_UITRAP_KEY_SETOVERSTRIKEMODE    0x2E	/* slot 0x2E */
#define QL_UITRAP_KEY_CLEARSTATES          0x2F	/* slot 0x2F */
#define QL_UITRAP_KEY_GETCATCHER           0x30	/* slot 0x30 */
#define QL_UITRAP_KEY_SETCATCHER           0x31	/* slot 0x31 */
#define QL_UITRAP_GETCLIPBOARDDATA         0x32	/* slot 0x32 */
#define QL_UITRAP_GETGLCONFIG              0x33	/* slot 0x33 */
#define QL_UITRAP_GETCLIENTSTATE           0x34	/* slot 0x34 */
#define QL_UITRAP_GETCONFIGSTRING          0x35	/* slot 0x35 */
#define QL_UITRAP_LAN_GETPINGINFO          0x36	/* slot 0x36 */
#define QL_UITRAP_LAN_GETPING              0x37	/* slot 0x37 */
#define QL_UITRAP_LAN_MARKSERVERVISIBLE    0x38	/* slot 0x38 */
#define QL_UITRAP_LAN_UPDATEVISIBLEPINGS   0x39	/* slot 0x39 */
#define QL_UITRAP_LAN_RESETPINGS           0x3A	/* slot 0x3A */
#define QL_UITRAP_LAN_LOADCACHEDSERVERS    0x3B	/* slot 0x3B */
#define QL_UITRAP_LAN_SAVECACHEDSERVERS    0x3C	/* slot 0x3C */
#define QL_UITRAP_LAN_ADDSERVER            0x3D	/* slot 0x3D */
#define QL_UITRAP_LAN_REMOVESERVER         0x3E	/* slot 0x3E */
#define QL_UITRAP_SNAPSHOTINFO             0x3F	/* slot 0x3F */
#define QL_UITRAP_SETPBCLSTATUS            0x40	/* slot 0x40 */
#define QL_UITRAP_GETSAVEDGAMES            0x41	/* slot 0x41 */
#define QL_UITRAP_LOADSAVEGAME             0x42	/* slot 0x42 */
#define QL_UITRAP_AUTOSAVE                 0x43	/* slot 0x43 */
#define QL_UITRAP_LAN_GETSERVERADDRESS     0x52	/* slot 0x52 */
#define QL_UITRAP_GETMAPNAME               0x53	/* slot 0x53 */
#define QL_UITRAP_GETSKILLRATING           0x54	/* slot 0x54 */
#define QL_UITRAP_GETMATCHSTARTTIME        0x55	/* slot 0x55 */

/* Curated exact prototypes recovered from committed UI reconstruction work. */
/* Ordinal 1 / dllEntry @ 0x10003970 */
void	dllEntry( void *syscallTable );

/* _UI_Init @ 0x1000FAB0 */
void	_UI_Init( int singlePlayerMenu );

/* _UI_Shutdown @ 0x100044E0 */
void	_UI_Shutdown( void );

/* _UI_KeyEvent @ 0x1000FF40 */
void	_UI_KeyEvent( int key, qboolean down );

/* _UI_MouseEvent @ 0x10010000 */
void	_UI_MouseEvent( int dx, int dy );

/* _UI_Refresh @ 0x10004390 */
void	_UI_Refresh( int realtime );

/* _UI_IsFullscreen @ 0x10010380 */
qboolean	_UI_IsFullscreen( void );

/* _UI_SetActiveMenu @ 0x100100D0 */
void	_UI_SetActiveMenu( uiMenuCommand_t menu );

/* UI_ConsoleCommand @ 0x10002AC0 */
qboolean	UI_ConsoleCommand( int realtime );

/* UI_DrawConnectScreen @ 0x10010E30 */
void	UI_DrawConnectScreen( qboolean overlay );

/* UI_RefreshDisplayContext @ 0x10003920 */
void	UI_RefreshDisplayContext( void );

/* UI_RefreshDisplayContextScale @ 0x1000F9F0 */
void	UI_RefreshDisplayContextScale( void );

/* UI_RegisterCvars @ 0x10011730 */
void	UI_RegisterCvars( void );

/* UI_GetCallvoteGametypeToken @ 0x10001000 */
const char *	UI_GetCallvoteGametypeToken( int gametype );

/* UI_StartingWeaponIndexFromToken @ 0x10001090 */
int	UI_StartingWeaponIndexFromToken( void );

/* AnglesToAxis @ 0x100010F0 */
void	AnglesToAxis( const vec3_t angles, vec3_t axis[3] );

/* AngleSubtract @ 0x10001140 */
void	AngleSubtract( float a1, float a2, float *out );

/* MatrixMultiply @ 0x100011C0 */
void	MatrixMultiply( float in1[3][3], float in2[3][3], float out[3][3] );

/* AngleVectors @ 0x100012A0 */
void	AngleVectors( const vec3_t angles, vec3_t forward, vec3_t right, vec3_t up );

/* COM_Compress @ 0x10001400 */
int	COM_Compress( char *data_p );

/* COM_ParseExt @ 0x10001500 */
char *	COM_ParseExt( char **data_p, qboolean allowLineBreaks );

/* String_IsNumeric @ 0x10001670 */
qboolean	String_IsNumeric( const char *s );

/* Q_stricmpn @ 0x100016C0 */
int	Q_stricmpn( const char *s1, const char *s2, int n );

/* Q_stricmp @ 0x10001730 */
int	Q_stricmp( const char *s1, const char *s2 );

/* Q_strncpyz @ 0x10001750 */
void	Q_strncpyz( char *dest, const char *src, int destsize );

/* Q_CleanStr @ 0x100017E0 */
void	Q_CleanStr( char *string );

/* Com_sprintf @ 0x10001830 */
void	Com_sprintf( char *dest, int size, const char *fmt, ... );

/* va @ 0x10001900 */
char *	va( const char *format, ... );

/*
 * Full mapped symbol-address catalog derived from references/symbol-maps/ui.json.
 * Comments are short summaries from the committed reverse-engineering notes.
 */
/* UI_GetCallvoteGametypeToken: Returns the short retail callvote gametype token for a gametype enum, such as `ffa`, `duel`, `race`, `tdm`, `ca`, `ctf`, `oneflag`, `har`, `ft`, `dom`, `ad`, and `rr`. */
#define QLR_UI_ADDR_UI_GETCALLVOTEGAMETYPETOKEN                  0x10001000u
/* UI_StartingWeaponIndexFromToken: Parses the queued primary-weapon token and returns the 1-based retail starting-weapons table index used by UI_DrawStartingWeapons. */
#define QLR_UI_ADDR_UI_STARTINGWEAPONINDEXFROMTOKEN              0x10001090u
/* AnglesToAxis: Builds a 3x3 axis matrix from Euler angles by calling AngleVectors and negating the intermediate right vector into axis[1]. */
#define QLR_UI_ADDR_ANGLESTOAXIS                                 0x100010F0u
/* AngleSubtract: Normalizes the angle delta a1 - a2 into the shared Quake range [-180, 180] for player animation and orientation code. */
#define QLR_UI_ADDR_ANGLESUBTRACT                                0x10001140u
/* MatrixMultiply: Multiplies two 3x3 axis matrices, exactly matching the shared tag-attachment and player-model composition helper. */
#define QLR_UI_ADDR_MATRIXMULTIPLY                               0x100011C0u
/* AngleVectors: Builds optional forward, right, and up vectors from Euler angles, matching the shared AngleVectors helper used by player preview code. */
#define QLR_UI_ADDR_ANGLEVECTORS                                 0x100012A0u
/* COM_Compress: In-place parser prepass that strips comments, collapses whitespace, and preserves quoted strings. */
#define QLR_UI_ADDR_COM_COMPRESS                                 0x10001400u
/* COM_ParseExt: Shared token parser with allowLineBreaks handling, comment skipping, quoted-string support, and the module-global token buffer. */
#define QLR_UI_ADDR_COM_PARSEEXT                                 0x10001500u
/* String_IsNumeric: Returns true when the inspected substring contains only digits with at most one decimal point, matching the retail choice-list formatting gate. */
#define QLR_UI_ADDR_STRING_ISNUMERIC                             0x10001670u
/* Q_stricmpn: Case-insensitive bounded compare with Quake-style null handling used across parser and command dispatch paths. */
#define QLR_UI_ADDR_Q_STRICMPN                                   0x100016C0u
/* Q_stricmp: Thin fixed-limit wrapper over Q_stricmpn that preserves the shared layer's null-sentinel return semantics. */
#define QLR_UI_ADDR_Q_STRICMP                                    0x10001730u
/* Q_strncpyz: Fatal-checking bounded string copy used throughout the retail UI utility layer. */
#define QLR_UI_ADDR_Q_STRNCPYZ                                   0x10001750u
/* Q_CleanStr: In-place shared string cleaner that strips Quake color escapes and non-printable bytes while preserving printable ASCII. */
#define QLR_UI_ADDR_Q_CLEANSTR                                   0x100017E0u
/* Com_sprintf: Formats into a large temporary buffer, reports overflow, then copies into the bounded destination. */
#define QLR_UI_ADDR_COM_SPRINTF                                  0x10001830u
/* va: Formats into the rotating two-buffer varargs scratch ring used across the UI module. */
#define QLR_UI_ADDR_VA                                           0x10001900u
/* Info_ValueForKey: Parses \\key\\value infostrings with alternating scratch buffers and returns the matched value. */
#define QLR_UI_ADDR_INFO_VALUEFORKEY                             0x10001940u
/* Info_RemoveKey: Removes a key and its paired value from a mutable info string after oversize validation. */
#define QLR_UI_ADDR_INFO_REMOVEKEY                               0x10001A60u
/* Info_SetValueForKey: Rejects illegal info-string characters, removes any prior key, and appends the new \\key\\value pair. */
#define QLR_UI_ADDR_INFO_SETVALUEFORKEY                          0x10001B80u
/* Color_LerpBytesToPacked: Blends two RGB byte triplets with a fractional weight, applies a final scalar, clamps each channel, and returns a packed 0xRRGGBBFF color. */
#define QLR_UI_ADDR_COLOR_LERPBYTESTOPACKED                      0x10001D60u
/* Color_PackedToScaledRGBA: Unpacks a packed RGBA word into destination bytes, scales RGB by an integer brightness factor, and preserves the packed alpha byte. */
#define QLR_UI_ADDR_COLOR_PACKEDTOSCALEDRGBA                     0x10001E20u
/* Com_Error: Formats a fatal message and forwards it through the UI syscall error slot. */
#define QLR_UI_ADDR_COM_ERROR                                    0x10001E70u
/* Com_Printf: Formats a message and forwards it through the UI syscall print slot. */
#define QLR_UI_ADDR_COM_PRINTF                                   0x10001EE0u
/* UI_Cvar_VariableString: Fetches a cvar string into the shared 0x400-byte UI scratch buffer and returns it. */
#define QLR_UI_ADDR_UI_CVAR_VARIABLESTRING                       0x10001F50u
/* UI_SetBestScores: Sets the postgame ui_score* cvars, including mirrored second-player score fields. */
#define QLR_UI_ADDR_UI_SETBESTSCORES                             0x10001F70u
/* UI_LoadBestScores: Loads saved score and demo metadata from the per-map postgame files. */
#define QLR_UI_ADDR_UI_LOADBESTSCORES                            0x10002350u
/* UI_ConsoleCommand_MenuClose: Retail-only console-command helper behind menu_close that reads argv(1), resolves the named menu, clears its open state, and runs the close path. */
#define QLR_UI_ADDR_UI_CONSOLECOMMAND_MENUCLOSE                  0x10002490u
/* UI_ConsoleCommand_MenuOpen: Retail-only console-command helper behind menu_open that reads argv(1) and forwards the requested menu name to Menus_ActivateByName. */
#define QLR_UI_ADDR_UI_CONSOLECOMMAND_MENUOPEN                   0x10002520u
/* UI_CalcPostGameStats: Retail postgame core. */
#define QLR_UI_ADDR_UI_CALCPOSTGAMESTATS                         0x10002550u
/* UI_ConsoleCommand: Dispatches the retail UI console commands, including listPlayerModels, ui_report, ui_load, postgame, ui_cache, menu_open, and menu_close. */
#define QLR_UI_ADDR_UI_CONSOLECOMMAND                            0x10002AC0u
/* UI_AdjustFrom640: Scales 640x480 UI coordinates through the current xscale, yscale, and widescreen bias. */
#define QLR_UI_ADDR_UI_ADJUSTFROM640                             0x10002BF0u
/* UI_DrawHandlePic: Draws a shader-backed picture rectangle and flips UVs when width or height are negative. */
#define QLR_UI_ADDR_UI_DRAWHANDLEPIC                             0x10002C50u
/* UI_FillRect: Fills a solid rectangle using the cached white shader and current color. */
#define QLR_UI_ADDR_UI_FILLRECT                                  0x10002D60u
/* UI_LoadArenasFromFile: Reads an arena script file, validates size, and parses arena info blocks into the arena list. */
#define QLR_UI_ADDR_UI_LOADARENASFROMFILE                        0x10002E20u
/* UI_ParseInfos: Reads arena or bot info files into info-string records while enforcing the retail brace and EOF parse guards. */
#define QLR_UI_ADDR_UI_PARSEINFOS                                0x10003070u
/* UI_LoadArenas: Loads the arena catalog via g_arenasFile and the scripts/arenas.txt fallback path. */
#define QLR_UI_ADDR_UI_LOADARENAS                                0x10003190u
/* UI_LoadBotsFromFile: Reads a bot script file, validates size, and parses bot info blocks. */
#define QLR_UI_ADDR_UI_LOADBOTSFROMFILE                          0x10003640u
/* UI_LoadBots: Loads the bot catalog via g_botsFile and scripts/*.bot fallback enumeration. */
#define QLR_UI_ADDR_UI_LOADBOTS                                  0x10003770u
/* UI_GetBotNameByNumber: Returns the cleaned bot name for a valid bot index and falls back to Sarge when no bot info is available. */
#define QLR_UI_ADDR_UI_GETBOTNAMEBYNUMBER                        0x100038C0u
/* UI_HasUniqueCDKey: Returns qtrue through the native export-table slot that replaces the old UI_HASUNIQUECDKEY vmMain case. */
#define QLR_UI_ADDR_UI_HASUNIQUECDKEY                            0x10003910u
/* UI_RefreshDisplayContext: Extended native export-table helper that refreshes the 640x480 UI scale state through UI_RefreshDisplayContextScale and republishes the retail uiDC pointer. */
#define QLR_UI_ADDR_UI_REFRESHDISPLAYCONTEXT                     0x10003920u
/* UI_ForEachArenaName: Extended native export-table helper that lazily loads arenas and invokes a caller-supplied callback for each non-null arena display-name pointer. */
#define QLR_UI_ADDR_UI_FOREACHARENANAME                          0x10003930u
/* dllEntry: Native module bootstrap that installs the export table and caches the syscall table pointer. */
#define QLR_UI_ADDR_DLLENTRY                                     0x10003970u
/* AssetCache: Registers gradient, FX art, scrollbars, slider art, and the crosshair shader set. */
#define QLR_UI_ADDR_ASSETCACHE                                   0x10003990u
/* _UI_DrawSides: Draws the left and right edges of the UI outline rectangle. */
#define QLR_UI_ADDR__UI_DRAWSIDES                                0x10003B30u
/* _UI_DrawTopBottom: Draws the top and bottom edges of the UI outline rectangle. */
#define QLR_UI_ADDR__UI_DRAWTOPBOTTOM                            0x10003C20u
/* Text_GetDimensions: Lower-level retail text-bounds helper that measures string width and height through out-parameters and sits underneath the Text_Width and Text_Height wrappers. */
#define QLR_UI_ADDR_TEXT_GETDIMENSIONS                           0x10003D90u
/* Text_Width: HLIL-only wrapper over the retail text-bounds helper that returns width and is assigned to uiDC.textWidth during _UI_Init. */
#define QLR_UI_ADDR_TEXT_WIDTH                                   0x10003E60u
/* Text_Height: HLIL-only wrapper over the retail text-bounds helper that returns height and is assigned to uiDC.textHeight during _UI_Init. */
#define QLR_UI_ADDR_TEXT_HEIGHT                                  0x10003E90u
/* Text_Paint: Font renderer assigned into uiDC.drawText during _UI_Init. */
#define QLR_UI_ADDR_TEXT_PAINT                                   0x10003EC0u
/* Text_PaintWithCursor: Paints text while drawing a blinking insert or overstrike cursor at the active position. */
#define QLR_UI_ADDR_TEXT_PAINTWITHCURSOR                         0x10004070u
/* Text_Paint_Limit: Scaled-text helper behind UI_DrawServerMOTD that clips text against *maxX, temporarily projects the out-parameter into screen space, and draws through the retail import[94] text path. */
#define QLR_UI_ADDR_TEXT_PAINT_LIMIT                             0x10004280u
/* _UI_Refresh: Advances UI realtime and FPS state, refreshes cvars, paints menus, ticks the browser refresh work, and draws the cursor. */
#define QLR_UI_ADDR__UI_REFRESH                                  0x10004390u
/* _UI_Shutdown: Tail-jumps through the syscall table to save cached LAN servers, matching the entire native shutdown entrypoint. */
#define QLR_UI_ADDR__UI_SHUTDOWN                                 0x100044E0u
/* GetMenuBuffer: Loads a menu script into the static buffer with default fallback and size guards. */
#define QLR_UI_ADDR_GETMENUBUFFER                                0x100044F0u
/* Asset_Parse: Parses assetGlobalDef menu blocks and populates shared UI asset definitions. */
#define QLR_UI_ADDR_ASSET_PARSE                                  0x100045B0u
/* UI_ParseMenu: Opens a menu file buffer and parses its top-level assetGlobalDef and menudef blocks. */
#define QLR_UI_ADDR_UI_PARSEMENU                                 0x10004B20u
/* UI_LoadMenus: Loads a menu set with fallback-to-default handling and optional display reset. */
#define QLR_UI_ADDR_UI_LOADMENUS                                 0x10004E10u
/* UI_Load: Reloads the active menu file set from ui_menuFiles and the ingame fallback file. */
#define QLR_UI_ADDR_UI_LOAD                                      0x10004FC0u
/* UI_DrawHandicap: Clamps the handicap cvar into the retail 5..100 range, indexes the handicap label table, and paints the selected value. */
#define QLR_UI_ADDR_UI_DRAWHANDICAP                              0x10005100u
/* UI_SetCapFragLimits: Computes the retail default capture and frag limits for the current gametype and writes either the ui_* preview cvars or the live gameplay cvars. */
#define QLR_UI_ADDR_UI_SETCAPFRAGLIMITS                          0x100051B0u
/* UI_DrawGameType: Paints the current single-player game-type label from the retail game-type table. */
#define QLR_UI_ADDR_UI_DRAWGAMETYPE                              0x10005220u
/* UI_DrawNetGameType: Validates ui_netGameType and ui_actualNetGameType against the retail bounds and paints the selected net game-type label. */
#define QLR_UI_ADDR_UI_DRAWNETGAMETYPE                           0x10005260u
/* UI_DrawJoinGameType: Validates ui_joinGameType against the retail join-game-type count and paints the selected join label. */
#define QLR_UI_ADDR_UI_DRAWJOINGAMETYPE                          0x100052E0u
/* UI_DrawSkill: Clamps g_spSkill into the retail 1..5 range and paints the matching skill-level string. */
#define QLR_UI_ADDR_UI_DRAWSKILL                                 0x10005350u
/* UI_DrawMapPreview: Validates the active map selector for the chosen preview path, caches the levelshot shader on first use, and falls back to `menu/art/unknownmap` when no preview is available. */
#define QLR_UI_ADDR_UI_DRAWMAPPREVIEW                            0x100053C0u
/* UI_DrawMapTimeToBeat: Resolves the active map's time-to-beat for the current gametype, formats it as `%02i:%02i`, and paints the result. */
#define QLR_UI_ADDR_UI_DRAWMAPTIMETOBEAT                         0x100054A0u
/* UI_DrawMapCinematic: Runs or lazily starts the selected map cinematic, then falls back to UI_DrawMapPreview when the ROQ is unavailable. */
#define QLR_UI_ADDR_UI_DRAWMAPCINEMATIC                          0x10005560u
/* UI_DrawPlayerModel: Refreshes the cached player preview model from the retail model and headmodel cvars, updates the playerInfo block, and renders it through UI_DrawPlayer. */
#define QLR_UI_ADDR_UI_DRAWPLAYERMODEL                           0x10005690u
/* UI_DrawTeamPlayerModel: Builds and renders the forced team-model preview using cg_forceTeamModel, cg_forceTeamSkin, and the team color cvars. */
#define QLR_UI_ADDR_UI_DRAWTEAMPLAYERMODEL                       0x10005850u
/* UI_DrawEnemyPlayerModel: Builds and renders the forced enemy-model preview using cg_forceEnemyModel, cg_forceEnemySkin, and the enemy color cvars. */
#define QLR_UI_ADDR_UI_DRAWENEMYPLAYERMODEL                      0x10005C20u
/* UI_DrawRedTeamModel: Builds and renders the forced red-team model preview using cg_forceRedTeamModel and the team color cvars. */
#define QLR_UI_ADDR_UI_DRAWREDTEAMMODEL                          0x10005FF0u
/* UI_DrawBlueTeamModel: Builds and renders the forced blue-team model preview using cg_forceBlueTeamModel and the enemy color cvars. */
#define QLR_UI_ADDR_UI_DRAWBLUETEAMMODEL                         0x100062A0u
/* UI_DrawNetSource: Formats and paints the current browser source label as `Source: %s`. */
#define QLR_UI_ADDR_UI_DRAWNETSOURCE                             0x10006550u
/* UI_DrawNetMapPreview: Draws the current server preview shader or falls back to `menu/art/unknownmap`. */
#define QLR_UI_ADDR_UI_DRAWNETMAPPREVIEW                         0x100065B0u
/* UI_DrawNetMapCinematic: Runs and draws the current server cinematic when available, then falls back to UI_DrawNetMapPreview. */
#define QLR_UI_ADDR_UI_DRAWNETMAPCINEMATIC                       0x10006600u
/* UI_DrawNetFilter: Formats and paints the current browser filter label as `Filter: %s`. */
#define QLR_UI_ADDR_UI_DRAWNETFILTER                             0x100066D0u
/* UI_DrawOpponent: Refreshes the cached opponent playerInfo from ui_opponentModel and renders the preview through UI_DrawPlayer. */
#define QLR_UI_ADDR_UI_DRAWOPPONENT                              0x10006730u
/* UI_DrawAllMapsSelection: Draws the current map or net-map display name for the shared all-maps ownerdraw path, with the final flag selecting the active selection slot. */
#define QLR_UI_ADDR_UI_DRAWALLMAPSSELECTION                      0x10006890u
/* UI_DrawOpponentName: Reads ui_opponentName into the shared UI cvar buffer and paints it directly. */
#define QLR_UI_ADDR_UI_DRAWOPPONENTNAME                          0x100068F0u
/* UI_DrawBotName: Resolves the active bot or character name, falls back to Sarge for invalid entries, and paints the resulting label. */
#define QLR_UI_ADDR_UI_DRAWBOTNAME                               0x10006B30u
/* UI_DrawBotSkill: Paints the selected bot skill label from the retail skill-level table. */
#define QLR_UI_ADDR_UI_DRAWBOTSKILL                              0x10006BC0u
/* UI_DrawRedBlue: Paints `Red` or `Blue` from the current redBlue toggle state. */
#define QLR_UI_ADDR_UI_DRAWREDBLUE                               0x10006C10u
/* UI_DrawCrosshair: Paints the current crosshair with the retail size, brightness, health-color, and palette-color handling before drawing the selected shader. */
#define QLR_UI_ADDR_UI_DRAWCROSSHAIR                             0x10006C60u
/* UI_OwnerDrawWidth: Computes rendered text widths for ownerdraw labels such as handicap, team names, skill, and selected-player text. */
#define QLR_UI_ADDR_UI_OWNERDRAWWIDTH                            0x10006950u
/* UI_DrawNextMap: Fetches the localized next-map text block from the string table and paints it into the target rect. */
#define QLR_UI_ADDR_UI_DRAWNEXTMAP                               0x10006EA0u
/* UI_DrawVoteString: Reads ui_votestring, centers it using the text-measure helper, and paints the current vote text. */
#define QLR_UI_ADDR_UI_DRAWVOTESTRING                            0x10006F30u
/* UI_DrawServerSettings: Renders the in-game server settings panel, including gametype limits, gameplay modifiers, and the modified-weapons icon list. */
#define QLR_UI_ADDR_UI_DRAWSERVERSETTINGS                        0x10007030u
/* UI_DrawStartingWeapons: Paints the starting-weapon icon row and the queued-primary label using the retail loadout mask and modified-weapon indicators. */
#define QLR_UI_ADDR_UI_DRAWSTARTINGWEAPONS                       0x10008730u
/* UI_BuildPlayerList: Builds the player and team name caches from player configstrings and refreshes the selected-player cvars. */
#define QLR_UI_ADDR_UI_BUILDPLAYERLIST                           0x10008B60u
/* UI_DrawSelectedPlayer: Refreshes the player cache on a timer and paints either the selected teammate name or the local player name. */
#define QLR_UI_ADDR_UI_DRAWSELECTEDPLAYER                        0x10008E90u
/* UI_DrawServerRefreshDate: Paints either the pulsing active-refresh message or the cached ui_lastServerRefresh timestamp. */
#define QLR_UI_ADDR_UI_DRAWSERVERREFRESHDATE                     0x10008F20u
/* UI_DrawServerMOTD: Scrolls the current server MOTD across the rectangle with the Welcome to Team Arena fallback and wraparound dual-paint handling. */
#define QLR_UI_ADDR_UI_DRAWSERVERMOTD                            0x10009080u
/* UI_DrawKeyBindStatus: Paints either the normal keybind hint or the pending-bind cancellation prompt based on the current keybind state. */
#define QLR_UI_ADDR_UI_DRAWKEYBINDSTATUS                         0x100092F0u
/* UI_DrawAdvert: Retail-only ownerdraw helper behind UI_ADVERT that tints, draws, and updates the current advertisement surface. */
#define QLR_UI_ADDR_UI_DRAWADVERT                                0x10009340u
/* UI_DrawGLInfo: Paints the GL vendor, version, renderer, and pixel-format diagnostics, then wraps the extension string into multiple lines across the available rect. */
#define QLR_UI_ADDR_UI_DRAWGLINFO                                0x100093B0u
/* UI_DrawCrosshairColor: Draws the retail crosshair-color selector bar and current swatch while honoring the crosshair-health color override. */
#define QLR_UI_ADDR_UI_DRAWCROSSHAIRCOLOR                        0x10009660u
/* UI_OwnerDraw: Large ownerdraw dispatcher assigned into uiDC.ownerDrawItem during _UI_Init. */
#define QLR_UI_ADDR_UI_OWNERDRAW                                 0x100097B0u
/* UI_OwnerDrawVisible: Evaluates the retail UI_SHOW_* visibility flags against gametype, leader, browser, and score-state conditions. */
#define QLR_UI_ADDR_UI_OWNERDRAWVISIBLE                          0x10009D30u
/* UI_Handicap_HandleKey: Cycles the handicap cvar in 5-point steps, clamps it to the retail 5..100 range, and wraps through the minimum and maximum values. */
#define QLR_UI_ADDR_UI_HANDICAP_HANDLEKEY                        0x1000A040u
/* UI_GameType_HandleKey: Advances the single-player gametype selector, refreshes cap and frag limits, reloads best scores, and resets the map feeder when the map count changes. */
#define QLR_UI_ADDR_UI_GAMETYPE_HANDLEKEY                        0x1000A110u
/* UI_NetGameType_HandleKey: Cycles the net gametype selection, skips the retail hidden enums, updates the visible and actual gametype cvars, resets the current net map, and refreshes the feeder. */
#define QLR_UI_ADDR_UI_NETGAMETYPE_HANDLEKEY                     0x1000A210u
/* UI_JoinGameType_HandleKey: Cycles the join-game gametype selector, updates ui_joinGameType, and rebuilds the visible server browser list. */
#define QLR_UI_ADDR_UI_JOINGAMETYPE_HANDLEKEY                    0x1000A300u
/* UI_Skill_HandleKey: Cycles g_spSkill through the retail one-to-five range and wraps at the ends. */
#define QLR_UI_ADDR_UI_SKILL_HANDLEKEY                           0x1000A390u
/* UI_NetSource_HandleKey: Cycles the network source selector, skips the unused Mplayer slot, rebuilds the server list, optionally starts a refresh, and writes ui_netSource. */
#define QLR_UI_ADDR_UI_NETSOURCE_HANDLEKEY                       0x1000A420u
/* UI_NetFilter_HandleKey: Cycles the active server filter index with wraparound and rebuilds the server display list. */
#define QLR_UI_ADDR_UI_NETFILTER_HANDLEKEY                       0x1000A4F0u
/* UI_BotName_HandleKey: Cycles the bot selection, switching between the retail character and bot-list bounds based on the active gametype. */
#define QLR_UI_ADDR_UI_BOTNAME_HANDLEKEY                         0x1000A570u
/* UI_BotSkill_HandleKey: Cycles the bot skill selector through the retail skill-level list with wraparound. */
#define QLR_UI_ADDR_UI_BOTSKILL_HANDLEKEY                        0x1000A5D0u
/* UI_Crosshair_HandleKey: Cycles cg_drawCrosshair through the retail crosshair set with wraparound and writes the updated cvar. */
#define QLR_UI_ADDR_UI_CROSSHAIR_HANDLEKEY                       0x1000A640u
/* UI_SelectedPlayer_HandleKey: Rebuilds the player list, cycles the selected player or Everyone entry for team leaders, and updates both selected-player cvars. */
#define QLR_UI_ADDR_UI_SELECTEDPLAYER_HANDLEKEY                  0x1000A6C0u
/* UI_CrosshairColor_HandleKey: Retail-only handler that cycles cg_crosshairColor through the numbered palette range and writes the wrapped result back to the cvar. */
#define QLR_UI_ADDR_UI_CROSSHAIRCOLOR_HANDLEKEY                  0x1000A790u
/* UI_OwnerDrawHandleKey: Routes ownerdraw key events to the retail per-widget handlers for handicap, gametype, team, bot, crosshair, and selected-player controls. */
#define QLR_UI_ADDR_UI_OWNERDRAWHANDLEKEY                        0x1000A820u
/* UI_GetValue: Stubbed display-context getValue callback currently returning 0 for retail ownerdraw value lookups. */
#define QLR_UI_ADDR_UI_GETVALUE                                  0x1000A980u
/* UI_LoadMods: Loads the retail $modlist pairs into the mod feeder, interns both mod names and descriptions, and stops at MAX_MODS. */
#define QLR_UI_ADDR_UI_LOADMODS                                  0x1000A9D0u
/* UI_LoadMovies: Enumerates .roq files from the video directory, strips the extension, uppercases the names, and interns the movie feeder entries. */
#define QLR_UI_ADDR_UI_LOADMOVIES                                0x1000AC00u
/* UI_LoadDemos: Builds the dm_<protocol> extension pair, enumerates demos, strips the protocol suffix, uppercases the names, and interns the demo feeder entries. */
#define QLR_UI_ADDR_UI_LOADDEMOS                                 0x1000ACF0u
/* UI_Update: Handles retail UI script-side cvar synchronization for name, rate, colorbits, and mouse-pitch updates, exactly matching the current UI_Update helper. */
#define QLR_UI_ADDR_UI_UPDATE                                    0x1000AE50u
/* UI_RunMenuScript: Runs menu-script commands including the retail callvote-map preview and submission branches, vote/admin handlers, favorite management, and model-color synchronization, then logs unknown UI script handlers. */
#define QLR_UI_ADDR_UI_RUNMENUSCRIPT                             0x1000B0E0u
/* UI_GetTeamColor: Stubbed display-context getTeamColor callback kept in the native callback table even though the retail body is presently empty. */
#define QLR_UI_ADDR_UI_GETTEAMCOLOR                              0x1000D2F0u
/* UI_CVMapCountByGameType: Marks maps active for the FEEDER_CVMAPS callvote filter using the active callvote-gametype state behind ui_cvGameType and returns the visible preview-row count. */
#define QLR_UI_ADDR_UI_CVMAPCOUNTBYGAMETYPE                      0x1000D300u
/* UI_MapCountByGameType: Marks maps active for the current gametype filter and returns the visible map count, with the single-player path requiring the extra GT_SINGLE_PLAYER bit. */
#define QLR_UI_ADDR_UI_MAPCOUNTBYGAMETYPE                        0x1000D3C0u
/* UI_PlayerModelEntryHasSkin: Builds models/players/%s/lower_%s.skin from the retail player-model table and returns whether that lower-skin file exists. */
#define QLR_UI_ADDR_UI_PLAYERMODELENTRYHASSKIN                   0x1000D490u
/* UI_CountPlayerModelEntries: Counts valid retail player-model entries, caching successful skin probes and skipping the team-color skin aliases for the FEEDER_Q3HEADS-style path. */
#define QLR_UI_ADDR_UI_COUNTPLAYERMODELENTRIES                   0x1000D530u
/* UI_InsertServerIntoDisplayList: Inserts a server index into the displayServers array at a validated position by shifting later entries upward. */
#define QLR_UI_ADDR_UI_INSERTSERVERINTODISPLAYLIST               0x1000D630u
/* UI_RemoveServerFromDisplayList: Removes the first matching server index from the displayServers array and compacts the remaining entries. */
#define QLR_UI_ADDR_UI_REMOVESERVERFROMDISPLAYLIST               0x1000D670u
/* UI_BinaryServerInsertion: Binary-searches the sorted display server list with trap_LAN_CompareServers and inserts the server at the resolved position. */
#define QLR_UI_ADDR_UI_BINARYSERVERINSERTION                     0x1000D6C0u
/* UI_BuildServerDisplayList: Rebuilds the visible server list, refreshes MOTD metadata, filters server rows, and updates the displayed server counters. */
#define QLR_UI_ADDR_UI_BUILDSERVERDISPLAYLIST                    0x1000D740u
/* UI_SortServerStatusInfo: Reorders named server-status cvars to the front of the table and translates Quake Live gametype numbers into display names. */
#define QLR_UI_ADDR_UI_SORTSERVERSTATUSINFO                      0x1000DA60u
/* UI_GetServerStatusInfo: Fetches server status text, tokenizes cvar and player lines in place, and populates the serverStatusInfo line table. */
#define QLR_UI_ADDR_UI_GETSERVERSTATUSINFO                       0x1000DB60u
/* stristr: Static UI-main helper that performs a case-insensitive substring search for the find-player browser path. */
#define QLR_UI_ADDR_STRISTR                                      0x1000DE40u
/* UI_BuildFindPlayerList: Drives the asynchronous find-player scan, harvesting matching names from server status replies and updating the found-server list. */
#define QLR_UI_ADDR_UI_BUILDFINDPLAYERLIST                       0x1000DEB0u
/* UI_BuildServerStatus: Refreshes the selected server's status table, resetting outstanding requests on forced rebuilds and retrying until data arrives. */
#define QLR_UI_ADDR_UI_BUILDSERVERSTATUS                         0x1000E3B0u
/* UI_FeederCount: Returns the active row count for the committed retail UI feeder set: heads, maps, servers, clans, player/team lists, mods, demos, cinematics, and the callvote-map filter. */
#define QLR_UI_ADDR_UI_FEEDERCOUNT                               0x1000E470u
/* UI_SelectedMap: Converts a visible feeder row into the backing active map index and returns that map's display name. */
#define QLR_UI_ADDR_UI_SELECTEDMAP                               0x1000E600u
/* UI_FeederItemImage: Resolves feeder row images such as character heads, map levelshots, callvote maps, and clan emblems. */
#define QLR_UI_ADDR_UI_FEEDERITEMIMAGE                           0x1000E640u
/* UI_FeederItemText: Returns feeder row text for the committed retail UI feeder set: heads, maps, server browser columns, mods, movies, demos, clans, and the older player/team list families. */
#define QLR_UI_ADDR_UI_FEEDERITEMTEXT                            0x1000EA80u
/* UI_FeederSelection: Applies feeder selection side effects such as model cvar writes, cinematic refresh, server-status selection, and the FEEDER_CVMAPS branch that rebuilds the visible callvote set through `UI_CVMapCountByGameType`, resolves the chosen row through `UI_SelectedMap`, and then refreshes `ui_currentNetMap` for the retail voteMap preview path. */
#define QLR_UI_ADDR_UI_FEEDERSELECTION                           0x1000EBA0u
/* Character_Parse: Parses one characters block from teaminfo into the retail model and skin table and builds each head icon path. */
#define QLR_UI_ADDR_CHARACTER_PARSE                              0x1000F140u
/* UI_ParseTeamInfo: Loads the retail teaminfo buffer and dispatches the top-level characters block into Character_Parse. */
#define QLR_UI_ADDR_UI_PARSETEAMINFO                             0x1000F2B0u
/* GameType_Parse: Parses gametype and joingametype blocks into the UI gametype tables. */
#define QLR_UI_ADDR_GAMETYPE_PARSE                               0x1000F340u
/* MapList_Parse: Parses map entries into uiInfo.mapList and replaces the last slot on overflow. */
#define QLR_UI_ADDR_MAPLIST_PARSE                                0x1000F4C0u
/* UI_ParseGameInfo: Dispatches gametypes, joingametypes, and maps blocks to the specific parsers. */
#define QLR_UI_ADDR_UI_PARSEGAMEINFO                             0x1000F6D0u
/* UI_Pause: Pauses or resumes the client while toggling KEYCATCH_UI and clearing key state on unpause. */
#define QLR_UI_ADDR_UI_PAUSE                                     0x1000F7B0u
/* UI_ListPlayerModels: Retail-only console-command helper behind listPlayerModels that prints the currently loaded model and skin entries. */
#define QLR_UI_ADDR_UI_LISTPLAYERMODELS                          0x1000F960u
/* UI_RefreshDisplayContextScale: Reads the renderer glconfig and rebuilds the 640x480 virtual-screen bias and scale values used by the retail UI drawing helpers. */
#define QLR_UI_ADDR_UI_REFRESHDISPLAYCONTEXTSCALE                0x1000F9F0u
/* _UI_Init: Full UI bootstrap: registers cvars, wires uiDC, loads menus, initializes scores, bots, and render assets, and seeds the retail `ui_cvGameType` callvote filter cvar to `-1` before menu scripts run. */
#define QLR_UI_ADDR__UI_INIT                                     0x1000FAB0u
/* _UI_KeyEvent: Routes key events to the focused menu, closes unfocused UI on ESC, and clears KEYCATCH_UI when no focused menu remains. */
#define QLR_UI_ADDR__UI_KEYEVENT                                 0x1000FF40u
/* _UI_MouseEvent: Accumulates cursor deltas, clamps them to the 640x480 UI bounds, and forwards movement into Display_MouseMove. */
#define QLR_UI_ADDR__UI_MOUSEEVENT                               0x10010000u
/* UI_LoadNonIngame: Loads the non-ingame menu set and clears the ingame-load state flag. */
#define QLR_UI_ADDR_UI_LOADNONINGAME                             0x10010080u
/* _UI_SetActiveMenu: Switches on the native UIMENU command, updates key catcher and pause state, reloads menu sets when needed, and activates the named retail menus. */
#define QLR_UI_ADDR__UI_SETACTIVEMENU                            0x100100D0u
/* _UI_IsFullscreen: Returns whether any visible fullscreen menu is active. */
#define QLR_UI_ADDR__UI_ISFULLSCREEN                             0x10010380u
/* Menus_AnyVisible: Extended native export-table predicate that scans the retail menu array and returns qtrue when any menu has WINDOW_VISIBLE set. */
#define QLR_UI_ADDR_MENUS_ANYVISIBLE                             0x100103C0u
/* UI_ReadableSize: Formats byte counts as bytes, KB, MB, or GB strings for the connect and download UI. */
#define QLR_UI_ADDR_UI_READABLESIZE                              0x100103F0u
/* UI_PrintTime: Formats millisecond durations into sec, min/sec, or hr/min strings for the connect and download UI. */
#define QLR_UI_ADDR_UI_PRINTTIME                                 0x10010540u
/* Text_PaintCenter: Measures text width and paints it centered around the supplied x coordinate. */
#define QLR_UI_ADDR_TEXT_PAINTCENTER                             0x100105F0u
/* Text_PaintCenter_AutoWrapped: Wraps text on spaces to fit a maximum width and paints each line centered. */
#define QLR_UI_ADDR_TEXT_PAINTCENTER_AUTOWRAPPED                 0x10010660u
/* UI_DisplayDownloadInfo: Formats download progress, transfer rate, and ETA strings for the connect screen. */
#define QLR_UI_ADDR_UI_DISPLAYDOWNLOADINFO                       0x100108D0u
/* UI_DrawConnectScreen: Draws the connection and download status screen, including abort and retry messaging. */
#define QLR_UI_ADDR_UI_DRAWCONNECTSCREEN                         0x10010E30u
/* UI_DrawAdvertisementWaitScreen: Extended native export-table drawer that optionally paints a named menu and then centers the retail 'Waiting on Advertisement' and 'Press ESC to cancel' prompts. */
#define QLR_UI_ADDR_UI_DRAWADVERTISEMENTWAITSCREEN               0x10011130u
/* UI_UpdateForceModelBrightness: Normalizes the current force-model and force-skin cvars to lowercase, checks for the bright skin token, and updates the paired UI bright-model toggle cvar. */
#define QLR_UI_ADDR_UI_UPDATEFORCEMODELBRIGHTNESS                0x10011510u
/* UI_UpdateForceTeamModelSettings: Refreshes the retail ui_forceTeamModelBright state from cg_forceTeamModel/cg_forceTeamSkin and marks the team-model preset state dirty. */
#define QLR_UI_ADDR_UI_UPDATEFORCETEAMMODELSETTINGS              0x10011630u
/* UI_UpdateForceEnemyModelSettings: Refreshes the retail ui_forceEnemyModelBright state from cg_forceEnemyModel/cg_forceEnemySkin and marks the enemy-model preset state dirty. */
#define QLR_UI_ADDR_UI_UPDATEFORCEENEMYMODELSETTINGS             0x10011660u
/* UI_UpdateAnnouncer: Plays the preview voice clip for the selected cg_announcer profile and mirrors the current selection into ui_announcer. */
#define QLR_UI_ADDR_UI_UPDATEANNOUNCER                           0x10011690u
/* UI_RegisterCvars: Registers the UI vmCvar table during startup. */
#define QLR_UI_ADDR_UI_REGISTERCVARS                             0x10011730u
/* UI_UpdateCvars: Updates the UI vmCvar table and runs any registered per-cvar change handlers. */
#define QLR_UI_ADDR_UI_UPDATECVARS                               0x100118A0u
/* UI_StopServerRefresh: Stops the server browser refresh pass and prints the listed-server and player summary. */
#define QLR_UI_ADDR_UI_STOPSERVERREFRESH                         0x100118F0u
/* UI_DoServerRefresh: Pumps visible server pings and finalizes the refresh when the scan completes. */
#define QLR_UI_ADDR_UI_DOSERVERREFRESH                           0x10011970u
/* UI_StartServerRefresh: Starts LAN or global server refresh commands and stamps the refresh time cvars. */
#define QLR_UI_ADDR_UI_STARTSERVERREFRESH                        0x10011A30u
/* UI_PlayerInfo_SetWeapon: Loads weapon, barrel, and flash assets for the UI player preview model. */
#define QLR_UI_ADDR_UI_PLAYERINFO_SETWEAPON                      0x10011C50u
/* UI_ForceLegsAnim: Toggles the legs animation state and primes the jump timer when LEGS_JUMP is selected. */
#define QLR_UI_ADDR_UI_FORCELEGSANIM                             0x10011F40u
/* UI_SetLegsAnim: Applies any pending legs animation override, then forces the resolved legs animation. */
#define QLR_UI_ADDR_UI_SETLEGSANIM                               0x10011F70u
/* UI_ForceTorsoAnim: Toggles the torso animation state and primes the gesture or attack timers for the selected sequence. */
#define QLR_UI_ADDR_UI_FORCETORSOANIM                            0x10011FC0u
/* UI_SetTorsoAnim: Applies any pending torso animation override, then forces the resolved torso animation. */
#define QLR_UI_ADDR_UI_SETTORSOANIM                              0x10012000u
/* UI_TorsoSequencing: Advances torso gesture, attack, and weapon-switch sequencing and triggers weapon model swaps. */
#define QLR_UI_ADDR_UI_TORSOSEQUENCING                           0x10012060u
/* UI_LegsSequencing: Advances jump and land leg sequencing while maintaining the shared preview jump-height state. */
#define QLR_UI_ADDR_UI_LEGSSEQUENCING                            0x10012100u
/* UI_PositionEntityOnTag: Lerps a parent tag, offsets origin through the parent axes, and copies backlerp onto the child entity. */
#define QLR_UI_ADDR_UI_POSITIONENTITYONTAG                       0x10012190u
/* UI_PositionRotatedEntityOnTag: Lerps a parent tag, composes child and parent axes, and positions the rotated entity on that tag. */
#define QLR_UI_ADDR_UI_POSITIONROTATEDENTITYONTAG                0x10012290u
/* UI_SetLerpFrameAnimation: Selects an animation record, validates the animation number, and primes the lerp-frame timing state. */
#define QLR_UI_ADDR_UI_SETLERPFRAMEANIMATION                     0x10012390u
/* UI_RunLerpFrame: Advances the current animation frames over time and computes the active backlerp value. */
#define QLR_UI_ADDR_UI_RUNLERPFRAME                              0x10012490u
/* UI_SwingAngles: Smoothly swings an angle toward a destination with tolerance-based speed scaling and clamp limits. */
#define QLR_UI_ADDR_UI_SWINGANGLES                               0x10012550u
/* UI_MovedirAdjustment: Converts view and move angle deltas into the fixed strafe yaw adjustments used by the preview model. */
#define QLR_UI_ADDR_UI_MOVEDIRADJUSTMENT                         0x10012760u
/* UI_PlayerAngles: Builds the preview legs, torso, and head axes from view angles, movement direction, and swing state. */
#define QLR_UI_ADDR_UI_PLAYERANGLES                              0x10012900u
/* UI_PlayerFloatSprite: Spawns and draws a sprite marker above the player preview origin. */
#define QLR_UI_ADDR_UI_PLAYERFLOATSPRITE                         0x10012C00u
/* UI_MachinegunSpinAngle: Updates the barrel spin or coast state from realtime and torso attack animation state. */
#define QLR_UI_ADDR_UI_MACHINEGUNSPINANGLE                       0x10012CA0u
/* UI_DrawPlayer: Full player preview renderer for legs, torso, head, weapon, barrel, muzzle flash, chat icon, and accent lights. */
#define QLR_UI_ADDR_UI_DRAWPLAYER                                0x10012D90u
/* UI_FindClientHeadFile: Resolves head skin and model file paths through the team, head, and fallback search variants. */
#define QLR_UI_ADDR_UI_FINDCLIENTHEADFILE                        0x10013850u
/* UI_RegisterClientSkin: Registers lower, upper, and head skins and falls back across model path variants. */
#define QLR_UI_ADDR_UI_REGISTERCLIENTSKIN                        0x100139A0u
/* UI_ParseAnimationFile: Parses animation.cfg content for UI player model animation state. */
#define QLR_UI_ADDR_UI_PARSEANIMATIONFILE                        0x10013BA0u
/* UI_RegisterClientModelname: Registers player model geometry, skins, and animation data for preview rendering. */
#define QLR_UI_ADDR_UI_REGISTERCLIENTMODELNAME                   0x10013E70u
/* UI_PlayerInfo_SetModel: Clears the preview struct, registers the requested model set, and seeds default machinegun state. */
#define QLR_UI_ADDR_UI_PLAYERINFO_SETMODEL                       0x10014250u
/* UI_PlayerInfo_SetInfo: Updates preview view and move angles, weapon transitions, animation sequencing, and chat state. */
#define QLR_UI_ADDR_UI_PLAYERINFO_SETINFO                        0x100142E0u
/* UI_Alloc: Allocates from the fixed UI memory pool with 16-byte alignment and emits the out-of-memory warning. */
#define QLR_UI_ADDR_UI_ALLOC                                     0x100144C0u
/* hashForString: Lowercases a string and accumulates the 2048-slot hash used by the interned string table. */
#define QLR_UI_ADDR_HASHFORSTRING                                0x10014510u
/* String_Alloc: Interns a string into the pooled string table and reuses existing entries by hash-chain lookup. */
#define QLR_UI_ADDR_STRING_ALLOC                                 0x10014560u
/* String_Report: Prints string-pool and UI memory-pool usage as percentages and byte totals. */
#define QLR_UI_ADDR_STRING_REPORT                                0x10014670u
/* PC_SourceError: Formats a parser error with source filename and line information and prints it as an ERROR. */
#define QLR_UI_ADDR_PC_SOURCEERROR                               0x10014710u
/* LerpColor: Interpolates each RGBA component between two colors and clamps the results into the 0..1 range. */
#define QLR_UI_ADDR_LERPCOLOR                                    0x100147A0u
/* Float_Parse: Reads one token from a script string and converts it to a float. */
#define QLR_UI_ADDR_FLOAT_PARSE                                  0x100148A0u
/* PC_Float_Parse: Reads one parser token, accepts an optional minus sign, validates TT_NUMBER, and returns a float. */
#define QLR_UI_ADDR_PC_FLOAT_PARSE                               0x100148D0u
/* Color_Parse: Parses four float components from a script string into a vec4 color. */
#define QLR_UI_ADDR_COLOR_PARSE                                  0x10014990u
/* PC_Color_Parse: Reads four numeric parser tokens into a vec4 color with parser-side error reporting. */
#define QLR_UI_ADDR_PC_COLOR_PARSE                               0x100149D0u
/* Int_Parse: Reads one token from a script string and converts it to an integer. */
#define QLR_UI_ADDR_INT_PARSE                                    0x10014AB0u
/* PC_Int_Parse: Reads one parser token, accepts an optional minus sign, validates TT_NUMBER, and returns an integer. */
#define QLR_UI_ADDR_PC_INT_PARSE                                 0x10014AE0u
/* Rect_Parse: Parses four float values from a script string into a rectangle definition. */
#define QLR_UI_ADDR_RECT_PARSE                                   0x10014BA0u
/* String_Parse: Reads one token from a script string and interns it through String_Alloc. */
#define QLR_UI_ADDR_STRING_PARSE                                 0x10014C30u
/* PC_String_Parse: Reads one parser token and interns the token text through String_Alloc. */
#define QLR_UI_ADDR_PC_STRING_PARSE                              0x10014C60u
/* PC_Script_Parse: Collects a brace-delimited parser script into a single interned command string. */
#define QLR_UI_ADDR_PC_SCRIPT_PARSE                              0x10014CF0u
/* GradientBar_Paint: Sets the draw color, paints the shared gradient bar shader, and then restores the draw color. */
#define QLR_UI_ADDR_GRADIENTBAR_PAINT                            0x10014E50u
/* Fade: Advances fade-in or fade-out alpha state using the next-time gate, clamp, and fade amount. */
#define QLR_UI_ADDR_FADE                                         0x10014EA0u
/* Window_Paint: Core window renderer handling filled, gradient, shader, team-color, and cinematic styles plus border variants. */
#define QLR_UI_ADDR_WINDOW_PAINT                                 0x10014F00u
/* Item_SetScreenCoords: Builds the item screen rectangle from parent offsets and rectClient while clearing cached text extents. */
#define QLR_UI_ADDR_ITEM_SETSCREENCOORDS                         0x10015410u
/* Item_UpdatePosition: Recomputes an item's screen-space rectangle from its parent menu and current border offsets. */
#define QLR_UI_ADDR_ITEM_UPDATEPOSITION                          0x10015470u
/* Menu_SetupAdvertCellShaders: Runs immediately after retail menu parse to walk advert items, compute their bounds, and seed each item background through the setup advert-cell-shader callback. */
#define QLR_UI_ADDR_MENU_SETUPADVERTCELLSHADERS                  0x100154E0u
/* Menu_RefreshAdvertCellShaders: Walks the same advert items during menu open, close, and refresh paths, recomputing each item background through the refresh advert-cell-shader callback. */
#define QLR_UI_ADDR_MENU_REFRESHADVERTCELLSHADERS                0x100155A0u
/* Menu_UpdatePresetLists: Scans retail preset-list items in a menu, compares their linked preset definitions against live cvar values, and forces the preset-list cvar to `Custom` when no named preset still matches. */
#define QLR_UI_ADDR_MENU_UPDATEPRESETLISTS                       0x100156B0u
/* Menu_UpdatePosition: Rebuilds each child item's screen-space rectangle from the menu's current screen origin and border offsets while clearing cached text extents. */
#define QLR_UI_ADDR_MENU_UPDATEPOSITION                          0x100159A0u
/* Menu_ClearFocus: Clears focus from every item in a menu, returns the previous focus item, and runs any leaveFocus scripts. */
#define QLR_UI_ADDR_MENU_CLEARFOCUS                              0x10015A80u
/* Menu_ItemsMatchingGroup: Counts menu items whose window name or group matches the requested token. */
#define QLR_UI_ADDR_MENU_ITEMSMATCHINGGROUP                      0x10015C50u
/* Menu_GetMatchingItemByNumber: Returns the Nth menu item whose window name or group matches the requested token. */
#define QLR_UI_ADDR_MENU_GETMATCHINGITEMBYNUMBER                 0x10015CC0u
/* Rect_ContainsPoint: Returns whether the supplied point lies strictly inside the given retail rect bounds, with a null-rect guard. */
#define QLR_UI_ADDR_RECT_CONTAINSPOINT                           0x10015C00u
/* Script_SetColor: Parses a target color slot plus four floats and writes backColor, foreColor, or borderColor on the current item. */
#define QLR_UI_ADDR_SCRIPT_SETCOLOR                              0x10015D50u
/* Script_SetAsset: Retail stub for the setasset command that parses and interns one asset token without further mutation. */
#define QLR_UI_ADDR_SCRIPT_SETASSET                              0x10015E30u
/* Script_SetBackground: Parses one asset token, registers it as a shader, and stores the handle in item->window.background. */
#define QLR_UI_ADDR_SCRIPT_SETBACKGROUND                         0x10015E60u
/* Menu_FindItemByName: Returns the first menu item whose window.name matches the requested item name. */
#define QLR_UI_ADDR_MENU_FINDITEMBYNAME                          0x10015EA0u
/* Script_SetTeamColor: Copies the display-context team color callback result into the current item's background color. */
#define QLR_UI_ADDR_SCRIPT_SETTEAMCOLOR                          0x10015F10u
/* Script_SetItemColor: Parses a target item/group name, a color field selector, and a vec4, then applies it across matching items. */
#define QLR_UI_ADDR_SCRIPT_SETITEMCOLOR                          0x10015F90u
/* Menu_ShowItemByName: Shows or hides all matching items by name or group and stops active cinematics when hiding. */
#define QLR_UI_ADDR_MENU_SHOWITEMBYNAME                          0x100160F0u
/* Menus_FindByName: Scans the global menu array and returns the menu whose window.name matches the requested token. */
#define QLR_UI_ADDR_MENUS_FINDBYNAME                             0x10016160u
/* Menus_CloseByName: Finds a named menu, runs its close script when visible, clears visibility and focus state, and refreshes the menu afterward. */
#define QLR_UI_ADDR_MENUS_CLOSEBYNAME                            0x100161B0u
/* Menus_CloseAll: Runs close scripts for all menus, clears visibility and focus state across the global menu array, and refreshes each menu afterward. */
#define QLR_UI_ADDR_MENUS_CLOSEALL                               0x10016220u
/* Script_Show: Parses one item or group token and forwards it to Menu_ShowItemByName with the show path enabled. */
#define QLR_UI_ADDR_SCRIPT_SHOW                                  0x100162C0u
/* Script_Hide: Parses one item or group token and forwards it to Menu_ShowItemByName with the hide path enabled. */
#define QLR_UI_ADDR_SCRIPT_HIDE                                  0x10016300u
/* Script_FadeIn: Parses one item/group token and marks matching items visible plus fading-in. */
#define QLR_UI_ADDR_SCRIPT_FADEIN                                0x10016340u
/* Script_FadeOut: Parses one item or group token and marks matching items visible plus fading-out. */
#define QLR_UI_ADDR_SCRIPT_FADEOUT                               0x100163B0u
/* Script_Open: Parses one menu name and routes it through the named-menu activation helper. */
#define QLR_UI_ADDR_SCRIPT_OPEN                                  0x10016420u
/* Script_ConditionalOpen: Reads a cvar and two menu names, then opens the zero or non-zero branch menu. */
#define QLR_UI_ADDR_SCRIPT_CONDITIONALOPEN                       0x10016450u
/* Script_Close: Parses one menu name and closes it through the named-menu close path, including the menu close script. */
#define QLR_UI_ADDR_SCRIPT_CLOSE                                 0x100164F0u
/* Script_Toggle: Retail-only menu toggle command that alternates a named menu between the open and close helpers. */
#define QLR_UI_ADDR_SCRIPT_TOGGLE                                0x10016580u
/* Menu_TransitionItemByName: Finds matching items by name or group, marks them visible plus in-transition, seeds rectClient and rectEffects state, and refreshes their screen coordinates. */
#define QLR_UI_ADDR_MENU_TRANSITIONITEMBYNAME                    0x100165E0u
/* Script_Transition: Parses a target name, source rect, destination rect, time, and step amount for transition setup. */
#define QLR_UI_ADDR_SCRIPT_TRANSITION                            0x100167B0u
/* Menu_OrbitItemByName: Finds matching items by name or group, marks them visible plus orbiting, seeds the orbit center and starting rectClient position, and refreshes their screen coordinates. */
#define QLR_UI_ADDR_MENU_ORBITITEMBYNAME                         0x100168A0u
/* Script_Orbit: Parses orbit target, x/y position, center, and time, then schedules orbit motion for matching items. */
#define QLR_UI_ADDR_SCRIPT_ORBIT                                 0x100169D0u
/* Script_ActivateAdvert: Retail-only advert command that parses one integer token, invokes the advert activation callback, and clears the current item's focus bit. */
#define QLR_UI_ADDR_SCRIPT_ACTIVATEADVERT                        0x10016AD0u
/* Script_SetFocus: Parses an item name, resolves it in the parent menu, clears prior focus, runs the new onFocus script, and plays the focus sound. */
#define QLR_UI_ADDR_SCRIPT_SETFOCUS                              0x10016B10u
/* Script_SetPlayerModel: Parses one model token and writes it into the retail player-model cvar through the display-context setCVar callback. */
#define QLR_UI_ADDR_SCRIPT_SETPLAYERMODEL                        0x10016BA0u
/* Script_SetPlayerHead: Parses one head model token and writes it into the retail player-head cvar through the display-context setCVar callback. */
#define QLR_UI_ADDR_SCRIPT_SETPLAYERHEAD                         0x10016BE0u
/* Script_SetCvar: Parses a cvar name/value pair and forwards it to the UI setCVar display callback. */
#define QLR_UI_ADDR_SCRIPT_SETCVAR                               0x10016C20u
/* Script_Exec: Parses one console command token, formats it as "%s ; ", and appends it through the executeText callback. */
#define QLR_UI_ADDR_SCRIPT_EXEC                                  0x10016C80u
/* Script_Play: Parses one sound token, registers it, and starts it on the local UI sound channel. */
#define QLR_UI_ADDR_SCRIPT_PLAY                                  0x10016CD0u
/* Script_playLooped: Parses one track token, stops the current background track, and restarts it as both intro and loop. */
#define QLR_UI_ADDR_SCRIPT_PLAYLOOPED                            0x10016D20u
/* Item_RunScript: Tokenizes a semicolon-delimited UI script, dispatches handlers from the retail command table, and falls back to executeText for unknown commands. */
#define QLR_UI_ADDR_ITEM_RUNSCRIPT                               0x10016D70u
/* Item_EnableShowViaCvar: Checks the item's enable/show cvar test lists against the current cvar string and returns the retail visibility/enabled decision for the requested flag. */
#define QLR_UI_ADDR_ITEM_ENABLESHOWVIACVAR                       0x10016E70u
/* Item_SetFocus: Rejects decorative or cvar-gated items, clears prior focus, runs the new onFocus path, and updates the parent menu cursor index. */
#define QLR_UI_ADDR_ITEM_SETFOCUS                                0x10016FC0u
/* Item_ListBox_MaxScroll: Computes the maximum listbox scroll position from feeder count, element size, and horizontal versus vertical layout. */
#define QLR_UI_ADDR_ITEM_LISTBOX_MAXSCROLL                       0x10017190u
/* Item_ListBox_ThumbPosition: Converts the listbox start position into the scrollbar thumb pixel position for the current orientation. */
#define QLR_UI_ADDR_ITEM_LISTBOX_THUMBPOSITION                   0x100171F0u
/* Item_ListBox_ThumbDrawPosition: Uses live cursor drag state to draw the thumb in motion and otherwise falls back to the normal thumb position helper. */
#define QLR_UI_ADDR_ITEM_LISTBOX_THUMBDRAWPOSITION               0x10017310u
/* Item_Slider_ThumbPosition: Reads the slider cvar, clamps it to the edit-field range, and maps the normalized value into the retail slider thumb x position. */
#define QLR_UI_ADDR_ITEM_SLIDER_THUMBPOSITION                    0x10017410u
/* Item_Slider_OverSlider: Builds the slider thumb hit rectangle around Item_Slider_ThumbPosition and returns the thumb-hover flag when the cursor overlaps it. */
#define QLR_UI_ADDR_ITEM_SLIDER_OVERSLIDER                       0x10017500u
/* Item_ListBox_OverLB: Tests the cursor against the retail listbox arrows, page regions, and thumb, returning the WINDOW_LB_* bitmask. */
#define QLR_UI_ADDR_ITEM_LISTBOX_OVERLB                          0x10017570u
/* Item_ListBox_MouseEnter: Refreshes listbox hover flags from Item_ListBox_OverLB and updates cursorPos when the pointer enters the selectable body region. */
#define QLR_UI_ADDR_ITEM_LISTBOX_MOUSEENTER                      0x10017880u
/* Item_MouseEnter: Applies cvar gating, drives mouseEnter and mouseEnterText scripts, and delegates listbox-specific hover handling when needed. */
#define QLR_UI_ADDR_ITEM_MOUSEENTER                              0x100179D0u
/* Item_MouseLeave: Runs the retail mouse-exit scripts and clears the text-hover and listbox arrow hover flags for the item. */
#define QLR_UI_ADDR_ITEM_MOUSELEAVE                              0x10017B50u
/* Item_ListBox_HandleKey: Implements the retail listbox keyboard, mouse click, paging, selection, and double-click handling paths. */
#define QLR_UI_ADDR_ITEM_LISTBOX_HANDLEKEY                       0x10017B90u
/* Item_YesNo_HandleKey: Handles focused yes-no activation by hit-testing the cursor inside the item and toggling the bound cvar on mouse or enter keys. */
#define QLR_UI_ADDR_ITEM_YESNO_HANDLEKEY                         0x100180A0u
/* Item_Multi_FindCvarByValue: Scans the current multi-choice cvar value and returns the matching option index, defaulting to `0` when retail finds no entry. */
#define QLR_UI_ADDR_ITEM_MULTI_FINDCVARBYVALUE                   0x100181A0u
/* Item_Multi_Setting: Returns the current display label for the bound multi-choice cvar, falling back to the retail empty string when no entry matches. */
#define QLR_UI_ADDR_ITEM_MULTI_SETTING                           0x10018280u
/* Item_Multi_HandleKey: Advances the current multi-choice selection on focused mouse or enter activation and writes the next string or numeric cvar value through the retail display context. */
#define QLR_UI_ADDR_ITEM_MULTI_HANDLEKEY                         0x10018370u
/* Item_PresetList_Setting: Returns the current display label for the bound preset-list cvar, falling back to the retail `Custom` string when no linked preset matches. */
#define QLR_UI_ADDR_ITEM_PRESETLIST_SETTING                      0x10018510u
/* Item_PresetList_FindCvarByValue: Scans the current preset-list cvar value and returns the matching option index, or `-1` when retail finds no named preset. */
#define QLR_UI_ADDR_ITEM_PRESETLIST_FINDCVARBYVALUE              0x100185D0u
/* Item_PresetList_HandleKey: Advances the focused preset-list selection, applies the linked hidden preset item's cvar set, and writes the selected preset name back through the retail display context. */
#define QLR_UI_ADDR_ITEM_PRESETLIST_HANDLEKEY                    0x10018680u
/* Item_TextField_HandleKey: Implements retail edit-field key handling, including cursor movement, insert and overwrite edits, numeric gating, and backspace or delete behavior on the active cvar buffer. */
#define QLR_UI_ADDR_ITEM_TEXTFIELD_HANDLEKEY                     0x10018870u
/* Scroll_ListBox_AutoFunc: Autorepeats listbox arrow scrolling by simulating repeated listbox handle-key calls while tightening the repeat interval. */
#define QLR_UI_ADDR_SCROLL_LISTBOX_AUTOFUNC                      0x10018C50u
/* Scroll_ListBox_ThumbFunc: Updates listbox startPos from thumb dragging and keeps the retail auto-scroll timing state in sync during capture. */
#define QLR_UI_ADDR_SCROLL_LISTBOX_THUMBFUNC                     0x10018CB0u
/* Scroll_Slider_ThumbFunc: Maps the captured cursor position across the slider track and writes the resulting value back through the UI setCVar callback. */
#define QLR_UI_ADDR_SCROLL_SLIDER_THUMBFUNC                      0x10018E60u
/* Item_StartCapture: Installs the retail capture callback and scroll state for listbox arrow repeat, listbox thumb drag, and slider thumb drag. */
#define QLR_UI_ADDR_ITEM_STARTCAPTURE                            0x10019000u
/* Item_Slider_HandleKey: Processes slider mouse and enter activation by mapping cursor position across the retail 96-pixel track and writing the resulting cvar value. */
#define QLR_UI_ADDR_ITEM_SLIDER_HANDLEKEY                        0x10019180u
/* Item_HandleKey: Clears or starts retail capture state, rejects key-up events, and dispatches item-type-specific key handling for listboxes, sliders, binds, ownerdraws, and choice widgets. */
#define QLR_UI_ADDR_ITEM_HANDLEKEY                               0x10019350u
/* Menu_SetPrevCursorItem: Walks backward through menu items with wraparound until Item_SetFocus accepts a candidate, then recenters mouse handling on that item. */
#define QLR_UI_ADDR_MENU_SETPREVCURSORITEM                       0x100194B0u
/* Menu_SetNextCursorItem: Walks forward through menu items with wraparound until Item_SetFocus accepts a candidate, then recenters mouse handling on that item. */
#define QLR_UI_ADDR_MENU_SETNEXTCURSORITEM                       0x100195B0u
/* Display_CloseCinematics: Walks the global menu array, stopping active window cinematics plus ownerdraw cinematics across every visible UI menu. */
#define QLR_UI_ADDR_DISPLAY_CLOSECINEMATICS                      0x100196B0u
/* Menus_HandleOOBClick: Implements out-of-bounds popup click routing by closing the current menu, activating the menu under the cursor, forwarding the key, and maintaining pause and cinematic state. */
#define QLR_UI_ADDR_MENUS_HANDLEOOBCLICK                         0x10019790u
/* Item_CorrectedTextRect: Builds the retail corrected text rectangle from item->textRect and shifts the y origin upward by the text height when the rect is active. */
#define QLR_UI_ADDR_ITEM_CORRECTEDTEXTRECT                       0x10019970u
/* Display_HandleKey: Routes retail UI key input across bind capture, edit capture, popup OOB clicks, focused-item dispatch, menu cursor navigation, and menu-level script or screenshot actions. */
#define QLR_UI_ADDR_DISPLAY_HANDLEKEY                            0x10019A10u
/* Item_SetTextExtents: Computes item->textRect dimensions and aligned origin from the current item text or cvar string using the retail text-metrics callbacks. */
#define QLR_UI_ADDR_ITEM_SETTEXTEXTENTS                          0x10019F10u
/* Item_TextColor: Builds the live item text color, including fade, focus pulse, blink, and disabled-color paths gated through Item_EnableShowViaCvar. */
#define QLR_UI_ADDR_ITEM_TEXTCOLOR                               0x1001A150u
/* Item_Text_AutoWrapped_Paint: Auto-wraps item text against the item width, updates retail textRect metrics per line, and paints each wrapped segment. */
#define QLR_UI_ADDR_ITEM_TEXT_AUTOWRAPPED_PAINT                  0x1001A3D0u
/* Item_Text_Wrapped_Paint: Walks carriage-return-delimited text lines, updates retail textRect metrics, and paints the wrapped text block line by line. */
#define QLR_UI_ADDR_ITEM_TEXT_WRAPPED_PAINT                      0x1001A630u
/* Item_Text_Paint: Dispatches retail wrapped and auto-wrapped text paths or computes aligned text metrics and color before drawing plain item text. */
#define QLR_UI_ADDR_ITEM_TEXT_PAINT                              0x1001A7E0u
/* Item_TextField_Paint: Paints the base item text plus the editable cvar string, including focus cursor rendering and paintOffset scrolling for active fields. */
#define QLR_UI_ADDR_ITEM_TEXTFIELD_PAINT                         0x1001A8E0u
/* Item_YesNo_Paint: Reads the bound cvar value, builds the standard focus pulse color, and paints the retail `Yes` or `No` label beside the item text. */
#define QLR_UI_ADDR_ITEM_YESNO_PAINT                             0x1001AB30u
/* Item_Multi_Paint: Resolves the current multi-choice display label through Item_Multi_Setting, then paints it with the standard text-item alignment and focus handling. */
#define QLR_UI_ADDR_ITEM_MULTI_PAINT                             0x1001AD40u
/* Item_PresetList_Paint: Resolves the current preset-list display label through Item_PresetList_Setting, then paints it with the standard text-item alignment and focus handling. */
#define QLR_UI_ADDR_ITEM_PRESETLIST_PAINT                        0x1001AF00u
/* Controls_GetConfig: Refreshes the retail binding table by querying the current two-key assignment for each command and storing bind1 and bind2 back into g_bindings. */
#define QLR_UI_ADDR_CONTROLS_GETCONFIG                           0x1001B0C0u
/* Controls_SetConfig: Writes the current retail binding table back through setBinding for both key slots and appends `in_restart` to refresh input. */
#define QLR_UI_ADDR_CONTROLS_SETCONFIG                           0x1001B1E0u
/* BindingIDFromName: Scans the retail binding-command table and returns the matching binding index or `-1` when the name is unknown. */
#define QLR_UI_ADDR_BINDINGIDFROMNAME                            0x1001B250u
/* BindingFromName: Builds the uppercase display string for the named command's primary and secondary bindings, joining them with ` or ` and falling back to `???`. */
#define QLR_UI_ADDR_BINDINGFROMNAME                              0x1001B2A0u
/* Item_Slider_Paint: Paints the retail slider bar and thumb, using Item_Slider_ThumbPosition to place the handle against the bound cvar value. */
#define QLR_UI_ADDR_ITEM_SLIDER_PAINT                            0x1001B3D0u
/* Item_SliderColor_Paint: Paints the retail slider-color bar and colorized thumb, reusing Item_Slider_ThumbPosition to place the handle against the bound cvar value. */
#define QLR_UI_ADDR_ITEM_SLIDERCOLOR_PAINT                       0x1001B5C0u
/* Item_Bind_Paint: Builds the current key-binding display string, applies the focused bind pulse, and paints the label plus bound-key text. */
#define QLR_UI_ADDR_ITEM_BIND_PAINT                              0x1001B7C0u
/* Item_Bind_HandleKey: Implements retail key-bind capture, cancellation, deletion, replacement, and Controls_SetConfig update behavior. */
#define QLR_UI_ADDR_ITEM_BIND_HANDLEKEY                          0x1001B9E0u
/* Item_Model_Paint: Builds the retail model-preview refdef and entity, advances model rotation when configured, and renders the item model inside the window rect. */
#define QLR_UI_ADDR_ITEM_MODEL_PAINT                             0x1001BC30u
/* Item_ListBox_Paint: Paints retail listbox contents, scrollbar arrows and thumb, selection highlighting, and feeder-driven image or text rows. */
#define QLR_UI_ADDR_ITEM_LISTBOX_PAINT                           0x1001BFB0u
/* Item_OwnerDraw_Paint: Computes ownerdraw color and optional text-label state, then calls the retail ownerdraw callback for the item. */
#define QLR_UI_ADDR_ITEM_OWNERDRAW_PAINT                         0x1001CA50u
/* Item_Paint: Performs retail orbit and transition updates, visibility and show or hide cvar gating, Window_Paint, and the per-item type dispatch chain. */
#define QLR_UI_ADDR_ITEM_PAINT                                   0x1001CED0u
/* Menu_GetFocused: Scans the global menu array and returns the first menu whose window carries both focus and visible flags. */
#define QLR_UI_ADDR_MENU_GETFOCUSED                              0x1001D390u
/* Menu_SetFeederSelection: Resolves the target menu by current focus or explicit name, resets listbox selection state for index zero, stores the new cursorPos, and fires the feederSelection callback. */
#define QLR_UI_ADDR_MENU_SETFEEDERSELECTION                      0x1001D3D0u
/* Menus_ActivateByName: Finds the named menu, clears focus on the rest, runs the activation onOpen and sound paths, pushes the previous focus onto the open-menu stack, and closes cinematics. */
#define QLR_UI_ADDR_MENUS_ACTIVATEBYNAME                         0x1001D4A0u
/* Menu_Paint: Paints one visible or forced menu, including fullscreen background handling, ownerdraw visibility gating, Window_Paint, per-item paint dispatch, and the debug rectangle. */
#define QLR_UI_ADDR_MENU_PAINT                                   0x1001D7B0u
/* Menu_HandleMouseMove: Runs the two-pass retail menu hover and focus update, including cvar gating, corrected-text hit testing, mouse enter and leave scripts, and focus assignment. */
#define QLR_UI_ADDR_MENU_HANDLEMOUSEMOVE                         0x1001D600u
/* Item_ValidateTypeData: Allocates and initializes retail listbox, edit, multi, or model typeData blocks according to item->type, including the default edit-field paint limit. */
#define QLR_UI_ADDR_ITEM_VALIDATETYPEDATA                        0x1001DA70u
/* Parse_name: Shared retail parser for the item and menu `name` keywords that interns the parsed string into window.name. */
#define QLR_UI_ADDR_PARSE_NAME                                   0x1001DB60u
/* ItemParse_focusSound: Parses a focus-sound token, registers it through the display context, and stores the resulting sound handle on the item. */
#define QLR_UI_ADDR_ITEMPARSE_FOCUSSOUND                         0x1001DC00u
/* ItemParse_group: Parses and interns item->window.group from the retail item keyword table. */
#define QLR_UI_ADDR_ITEMPARSE_GROUP                              0x1001DCB0u
/* ItemParse_asset_model: Validates model typeData, registers the item model asset, and seeds the preview angle with the retail rand()%360 path. */
#define QLR_UI_ADDR_ITEMPARSE_ASSET_MODEL                        0x1001DD50u
/* ItemParse_widescreen: Parses the retail item widescreen mode, rejects out-of-range values, and marks the item widescreen override as set. */
#define QLR_UI_ADDR_ITEMPARSE_WIDESCREEN                         0x1001DE20u
/* ItemParse_asset_shader: Parses a shader token and stores the registered no-mip shader handle in item->asset. */
#define QLR_UI_ADDR_ITEMPARSE_ASSET_SHADER                       0x1001DE60u
/* ItemParse_model_origin: Validates model typeData and parses three floats into the preview model origin vector. */
#define QLR_UI_ADDR_ITEMPARSE_MODEL_ORIGIN                       0x1001DF10u
/* Parse_model_fovx_or_elementwidth: Shared retail float parser reused by the item `model_fovx` and `elementwidth` keywords. */
#define QLR_UI_ADDR_PARSE_MODEL_FOVX_OR_ELEMENTWIDTH             0x1001DF70u
/* Parse_model_fovy_or_elementheight: Shared retail float parser reused by the item `model_fovy` and `elementheight` keywords. */
#define QLR_UI_ADDR_PARSE_MODEL_FOVY_OR_ELEMENTHEIGHT            0x1001DFA0u
/* ItemParse_model_rotation: Validates model typeData and parses the preview model rotation-speed integer. */
#define QLR_UI_ADDR_ITEMPARSE_MODEL_ROTATION                     0x1001DFD0u
/* ItemParse_model_angle: Validates model typeData and parses the preview model angle integer. */
#define QLR_UI_ADDR_ITEMPARSE_MODEL_ANGLE                        0x1001E000u
/* ItemParse_rect: Parses four floats into item->window.rectClient. */
#define QLR_UI_ADDR_ITEMPARSE_RECT                               0x1001E030u
/* ItemParse_decoration: Marks the item window with WINDOW_DECORATION. */
#define QLR_UI_ADDR_ITEMPARSE_DECORATION                         0x1001E090u
/* ItemParse_notselectable: Validates listbox typeData and marks the retail listbox as not selectable. */
#define QLR_UI_ADDR_ITEMPARSE_NOTSELECTABLE                      0x1001E0A0u
/* ItemParse_wrapped: Marks the item window with WINDOW_WRAPPED. */
#define QLR_UI_ADDR_ITEMPARSE_WRAPPED                            0x1001E0D0u
/* ItemParse_autowrapped: Marks the item window with WINDOW_AUTOWRAPPED. */
#define QLR_UI_ADDR_ITEMPARSE_AUTOWRAPPED                        0x1001E0F0u
/* ItemParse_horizontalscroll: Marks the item window with WINDOW_HORIZONTAL. */
#define QLR_UI_ADDR_ITEMPARSE_HORIZONTALSCROLL                   0x1001E110u
/* ItemParse_type: Parses item->type and immediately validates or allocates retail typeData for types that require it. */
#define QLR_UI_ADDR_ITEMPARSE_TYPE                               0x1001E130u
/* ItemParse_elementtype: Validates listbox typeData and parses the retail list element style. */
#define QLR_UI_ADDR_ITEMPARSE_ELEMENTTYPE                        0x1001E160u
/* ItemParse_columns: Validates listbox typeData, parses the column count plus per-column pos, width, and maxChars triples, and clamps to the retail maximum. */
#define QLR_UI_ADDR_ITEMPARSE_COLUMNS                            0x1001E190u
/* Parse_visible: Shared retail parser for the `visible` keyword; it parses an int and sets WINDOW_VISIBLE when non-zero. */
#define QLR_UI_ADDR_PARSE_VISIBLE                                0x1001E260u
/* ItemParse_ownerdraw: Parses item->window.ownerDraw and forces item->type to ITEM_TYPE_OWNERDRAW. */
#define QLR_UI_ADDR_ITEMPARSE_OWNERDRAW                          0x1001E290u
/* ItemParse_align: Parses item->alignment. */
#define QLR_UI_ADDR_ITEMPARSE_ALIGN                              0x1001E2C0u
/* Parse_textalign_or_fadeCycle: Shared retail int parser reused by item `textalign` and menu `fadeCycle`. */
#define QLR_UI_ADDR_PARSE_TEXTALIGN_OR_FADECYCLE                 0x1001E2E0u
/* Parse_textaligny_or_fadeAmount: Shared retail float parser reused by item `textaligny` and menu `fadeAmount`. */
#define QLR_UI_ADDR_PARSE_TEXTALIGNY_OR_FADEAMOUNT               0x1001E300u
/* ItemParse_font: Retail-only item parser that interns the item's font token. */
#define QLR_UI_ADDR_ITEMPARSE_FONT                               0x1001E320u
/* ItemParse_textscale: Parses item->textscale. */
#define QLR_UI_ADDR_ITEMPARSE_TEXTSCALE                          0x1001E340u
/* ItemParse_textstyle: Parses item->textStyle. */
#define QLR_UI_ADDR_ITEMPARSE_TEXTSTYLE                          0x1001E360u
/* Parse_backcolor: Shared retail four-float color parser for the `backcolor` keyword. */
#define QLR_UI_ADDR_PARSE_BACKCOLOR                              0x1001E380u
/* Parse_forecolor: Shared retail four-float color parser for the `forecolor` keyword that also marks WINDOW_FORECOLORSET. */
#define QLR_UI_ADDR_PARSE_FORECOLOR                              0x1001E470u
/* Parse_bordercolor: Shared retail four-float color parser for the `bordercolor` keyword. */
#define QLR_UI_ADDR_PARSE_BORDERCOLOR                            0x1001E570u
/* Parse_outlinecolor: Shared retail color parser for the `outlinecolor` keyword. */
#define QLR_UI_ADDR_PARSE_OUTLINECOLOR                           0x1001E660u
/* ItemParse_altrowcolor: Retail item-only color parser for the `altrowcolor` keyword. */
#define QLR_UI_ADDR_ITEMPARSE_ALTROWCOLOR                        0x1001E680u
/* ItemParse_elementcolor: Retail item-only color parser for the `elementcolor` keyword. */
#define QLR_UI_ADDR_ITEMPARSE_ELEMENTCOLOR                       0x1001E6A0u
/* ItemParse_selectedcolor: Retail item-only color parser for the `selectedcolor` keyword. */
#define QLR_UI_ADDR_ITEMPARSE_SELECTEDCOLOR                      0x1001E6C0u
/* ItemParse_outlineimage: Parses the retail outline-image shader token and stores the registered handle on the item. */
#define QLR_UI_ADDR_ITEMPARSE_OUTLINEIMAGE                       0x1001E6E0u
/* Parse_background: Shared retail parser for the `background` keyword that registers a no-mip shader and stores the handle. */
#define QLR_UI_ADDR_PARSE_BACKGROUND                             0x1001E790u
/* Parse_cinematic: Shared retail parser for the `cinematic` keyword that interns the cinematic name string. */
#define QLR_UI_ADDR_PARSE_CINEMATIC                              0x1001E840u
/* ItemParse_doubleClick: Validates listbox typeData and parses the `doubleclick` script into the retail listbox callback slot. */
#define QLR_UI_ADDR_ITEMPARSE_DOUBLECLICK                        0x1001E8E0u
/* ItemParse_cellId: Retail-only item parser for the integer `cellId` keyword. */
#define QLR_UI_ADDR_ITEMPARSE_CELLID                             0x1001E920u
/* ItemParse_defaultContent: Retail-only item parser that interns the `defaultContent` string. */
#define QLR_UI_ADDR_ITEMPARSE_DEFAULTCONTENT                     0x1001E940u
/* ItemParse_precision: Retail-only item parser for the integer `precision` keyword. */
#define QLR_UI_ADDR_ITEMPARSE_PRECISION                          0x1001E9E0u
/* ItemParse_onFocus: Parses the item `onFocus` script block. */
#define QLR_UI_ADDR_ITEMPARSE_ONFOCUS                            0x1001EA00u
/* ItemParse_leaveFocus: Parses the item `leaveFocus` script block. */
#define QLR_UI_ADDR_ITEMPARSE_LEAVEFOCUS                         0x1001EA20u
/* ItemParse_mouseEnter: Parses the item `mouseEnter` script block. */
#define QLR_UI_ADDR_ITEMPARSE_MOUSEENTER                         0x1001EA40u
/* ItemParse_mouseExit: Parses the item `mouseExit` script block. */
#define QLR_UI_ADDR_ITEMPARSE_MOUSEEXIT                          0x1001EA60u
/* ItemParse_mouseEnterText: Parses the item `mouseEnterText` script block. */
#define QLR_UI_ADDR_ITEMPARSE_MOUSEENTERTEXT                     0x1001EA80u
/* ItemParse_mouseExitText: Parses the item `mouseExitText` script block. */
#define QLR_UI_ADDR_ITEMPARSE_MOUSEEXITTEXT                      0x1001EAA0u
/* ItemParse_action: Parses the item `action` script block. */
#define QLR_UI_ADDR_ITEMPARSE_ACTION                             0x1001EAC0u
/* Parse_feeder_or_special: Shared retail float parser reused by the item `feeder` and `special` keywords. */
#define QLR_UI_ADDR_PARSE_FEEDER_OR_SPECIAL                      0x1001EAE0u
/* ItemParse_cvarTest: Parses the first retail cvar-test string slot. */
#define QLR_UI_ADDR_ITEMPARSE_CVARTEST                           0x1001EB00u
/* ItemParse_cvarTest2: Parses the second retail cvar-test string slot. */
#define QLR_UI_ADDR_ITEMPARSE_CVARTEST2                          0x1001EBA0u
/* ItemParse_cvarTest3: Parses the third retail cvar-test string slot. */
#define QLR_UI_ADDR_ITEMPARSE_CVARTEST3                          0x1001EC40u
/* ItemParse_cvarTest4: Parses the fourth retail cvar-test string slot. */
#define QLR_UI_ADDR_ITEMPARSE_CVARTEST4                          0x1001ECE0u
/* ItemParse_cvar: Validates the item edit or multi typeData, parses the backing cvar name, and resets the retail edit-field min, max, and default values when applicable. */
#define QLR_UI_ADDR_ITEMPARSE_CVAR                               0x1001ED80u
/* ItemParse_cvara: Retail-only item parser that reuses `ItemParse_cvar` and then seeds the parsed cvar through the display-context setter with the empty default string. */
#define QLR_UI_ADDR_ITEMPARSE_CVARA                              0x1001EE70u
/* ItemParse_maxChars: Validates edit typeData and parses the integer `maxChars` limit. */
#define QLR_UI_ADDR_ITEMPARSE_MAXCHARS                           0x1001EEC0u
/* ItemParse_maxPaintChars: Validates edit typeData and parses the integer `maxPaintChars` limit. */
#define QLR_UI_ADDR_ITEMPARSE_MAXPAINTCHARS                      0x1001EF30u
/* ItemParse_cvarFloat: Parses a cvar name plus default, min, and max floats into the edit-field range definition. */
#define QLR_UI_ADDR_ITEMPARSE_CVARFLOAT                          0x1001EFA0u
/* ItemParse_cvarFloatList: Parses a brace-delimited multi list of string and float pairs into the float-backed multi-selector table. */
#define QLR_UI_ADDR_ITEMPARSE_CVARFLOATLIST                      0x1001F010u
/* ItemParse_cvarInt: Retail-only integer variant of the cvar-range parser that reads the cvar plus default, min, and max values and marks integer mode. */
#define QLR_UI_ADDR_ITEMPARSE_CVARINT                            0x1001F150u
/* ItemParse_cvarPreset: Retail-only preset parser that reads brace-delimited preset labels plus numeric values into the multi-selector string and float tables. */
#define QLR_UI_ADDR_ITEMPARSE_CVARPRESET                         0x1001F1D0u
/* ItemParse_cvarStrList: Parses alternating brace-delimited string pairs into the string-backed multi-selector table; retail also reuses this handler for cvarPresetList. */
#define QLR_UI_ADDR_ITEMPARSE_CVARSTRLIST                        0x1001F370u
/* ItemParse_addColorRange: Parses low, high, and color triplets and appends them to the item's retail color-range array up to the fixed limit. */
#define QLR_UI_ADDR_ITEMPARSE_ADDCOLORRANGE                      0x1001F4C0u
/* Parse_ownerdrawFlag: Shared retail int parser for the `ownerdrawFlag` keyword. */
#define QLR_UI_ADDR_PARSE_OWNERDRAWFLAG                          0x1001F580u
/* Parse_ownerdrawFlag2: Shared retail int parser for the retail-only `ownerdrawFlag2` keyword. */
#define QLR_UI_ADDR_PARSE_OWNERDRAWFLAG2                         0x1001F5B0u
/* ItemParse_enableCvar: Parses the enable-cvar script and marks the item with CVAR_ENABLE gating. */
#define QLR_UI_ADDR_ITEMPARSE_ENABLECVAR                         0x1001F5E0u
/* ItemParse_disableCvar: Parses the disable-cvar script and marks the item with CVAR_DISABLE gating. */
#define QLR_UI_ADDR_ITEMPARSE_DISABLECVAR                        0x1001F610u
/* ItemParse_showCvar: Parses the show-cvar script and marks the item with CVAR_SHOW gating. */
#define QLR_UI_ADDR_ITEMPARSE_SHOWCVAR                           0x1001F650u
/* ItemParse_hideCvar: Parses the hide-cvar script and marks the item with CVAR_HIDE gating. */
#define QLR_UI_ADDR_ITEMPARSE_HIDECVAR                           0x1001F690u
/* Parse_showCvar2_or_hideCvar2: Shared retail script parser reused by the `showCvar2` and `hideCvar2` keywords. */
#define QLR_UI_ADDR_PARSE_SHOWCVAR2_OR_HIDECVAR2                 0x1001F6D0u
/* Parse_showCvar3_or_hideCvar3: Shared retail script parser reused by the `showCvar3` and `hideCvar3` keywords. */
#define QLR_UI_ADDR_PARSE_SHOWCVAR3_OR_HIDECVAR3                 0x1001F6F0u
/* Parse_showCvar4_or_hideCvar4: Shared retail script parser reused by the `showCvar4` and `hideCvar4` keywords. */
#define QLR_UI_ADDR_PARSE_SHOWCVAR4_OR_HIDECVAR4                 0x1001F710u
/* Item_SetupKeywordHash: Clears the retail item keyword-hash table and inserts every item parser keyword record from the static keyword array. */
#define QLR_UI_ADDR_ITEM_SETUPKEYWORDHASH                        0x1001F730u
/* Item_Parse: Parses an itemDef block, resolves tokens through the item keyword hash, and reports unknown or malformed retail item keywords. */
#define QLR_UI_ADDR_ITEM_PARSE                                   0x1001F7C0u
/* MenuParse_font: Normalizes the menu font path, registers the retail text, small, and big fonts on first use, and stores the resolved menu font token. */
#define QLR_UI_ADDR_MENUPARSE_FONT                               0x1001F9D0u
/* MenuParse_fullscreen: Parses the menu fullScreen flag. */
#define QLR_UI_ADDR_MENUPARSE_FULLSCREEN                         0x1001FAA0u
/* MenuParse_widescreen: Parses the retail menu widescreen mode and rejects out-of-range values. */
#define QLR_UI_ADDR_MENUPARSE_WIDESCREEN                         0x1001FAC0u
/* MenuParse_rect: Parses four floats into menu->window.rectClient. */
#define QLR_UI_ADDR_MENUPARSE_RECT                               0x1001FB00u
/* Parse_style: Shared retail int parser for the `style` keyword. */
#define QLR_UI_ADDR_PARSE_STYLE                                  0x1001FB60u
/* MenuParse_onOpen: Parses the menu `onOpen` script block. */
#define QLR_UI_ADDR_MENUPARSE_ONOPEN                             0x1001FB80u
/* MenuParse_onClose: Parses the menu `onClose` script block. */
#define QLR_UI_ADDR_MENUPARSE_ONCLOSE                            0x1001FBA0u
/* MenuParse_onESC: Parses the menu `onESC` script block. */
#define QLR_UI_ADDR_MENUPARSE_ONESC                              0x1001FBC0u
/* Parse_border: Shared retail int parser for the `border` keyword. */
#define QLR_UI_ADDR_PARSE_BORDER                                 0x1001FBE0u
/* Parse_borderSize: Shared retail float parser for the `borderSize` and `bordersize` keywords. */
#define QLR_UI_ADDR_PARSE_BORDERSIZE                             0x1001FC00u
/* MenuParse_focuscolor: Parses four floats into menu->focusColor. */
#define QLR_UI_ADDR_MENUPARSE_FOCUSCOLOR                         0x1001FC20u
/* MenuParse_disablecolor: Parses four floats into menu->disableColor. */
#define QLR_UI_ADDR_MENUPARSE_DISABLECOLOR                       0x1001FD10u
/* MenuParse_backgroundSize: Retail-only menu parser that reads the four-float `backgroundSize` value. */
#define QLR_UI_ADDR_MENUPARSE_BACKGROUNDSIZE                     0x1001FE00u
/* MenuParse_ownerdraw: Parses menu->window.ownerDraw. */
#define QLR_UI_ADDR_MENUPARSE_OWNERDRAW                          0x1001FE70u
/* MenuParse_popup: Marks the menu window with WINDOW_POPUP. */
#define QLR_UI_ADDR_MENUPARSE_POPUP                              0x1001FE90u
/* MenuParse_outOfBounds: Marks the menu window with WINDOW_OOB_CLICK. */
#define QLR_UI_ADDR_MENUPARSE_OUTOFBOUNDS                        0x1001FEB0u
/* Parse_text_or_soundLoop: Shared retail string parser reused by item `text` and menu `soundLoop`. */
#define QLR_UI_ADDR_PARSE_TEXT_OR_SOUNDLOOP                      0x1001FED0u
/* Parse_textalignx_or_fadeClamp: Shared retail float parser reused by item `textalignx` and menu `fadeClamp`. */
#define QLR_UI_ADDR_PARSE_TEXTALIGNX_OR_FADECLAMP                0x1001FF70u
/* MenuParse_itemDef: Allocates, initializes, parses, post-initializes, and parents a new menu item until the retail item limit is reached. */
#define QLR_UI_ADDR_MENUPARSE_ITEMDEF                            0x1001FF90u
/* Menu_SetupKeywordHash: Clears the retail menu keyword-hash table and inserts every menu parser keyword record from the static menu keyword array. */
#define QLR_UI_ADDR_MENU_SETUPKEYWORDHASH                        0x10020100u
/* Menu_Parse: Parses a menudef block, resolves tokens through the menu keyword hash, and reports unknown or malformed retail menu keywords. */
#define QLR_UI_ADDR_MENU_PARSE                                   0x10020190u
/* Menu_PaintAll: Runs any active capture callback, paints every menu, and draws the retail debug FPS overlay when debug mode is enabled. */
#define QLR_UI_ADDR_MENU_PAINTALL                                0x100203A0u
/* Display_MouseMove: Retail null-menu variant of Display_MouseMove that routes the current cursor position to the focused popup menu or to every menu and returns qtrue. */
#define QLR_UI_ADDR_DISPLAY_MOUSEMOVE                            0x10020740u
/* Display_CacheAll: Caches every menu's cinematic and sound dependencies by replaying the menu, item, and window content-cache walk behind the retail ui_cache command. */
#define QLR_UI_ADDR_DISPLAY_CACHEALL                             0x100207F0u
/* Menu_OverActiveItem: Returns whether the cursor is over any non-decoration active item in a visible menu, including corrected-text-rect handling for text items and cvar visibility gating. */
#define QLR_UI_ADDR_MENU_OVERACTIVEITEM                          0x100208F0u
/* __security_check_cookie: Exact MSVC GS cookie verifier used by the protected retail stack-frame epilog and wired into the EH4 exception path. */
#define QLR_UI_ADDR___SECURITY_CHECK_COOKIE                      0x100209E9u
/* __CRT_INIT@12: Runs the CRT process-attach and process-detach initializer, including constructor or destructor dispatch around the native DLL entrypoint. */
#define QLR_UI_ADDR___CRT_INIT_12                                0x10020A46u
/* ___DllMainCRTStartup: Exact MSVC DLL startup wrapper that initializes the CRT, forwards into _DllMain@12, and handles attach-failure unwind paths. */
#define QLR_UI_ADDR____DLLMAINCRTSTARTUP                         0x10020C50u
/* CRT_ResetNativeDllMainReason: Resets the cached DLL startup reason to -1 after ___DllMainCRTStartup finishes its attach or detach path. */
#define QLR_UI_ADDR_CRT_RESETNATIVEDLLMAINREASON                 0x10020D5Bu
/* _start: Module start stub that runs ___security_init_cookie on process attach and then tail-calls ___DllMainCRTStartup. */
#define QLR_UI_ADDR__START                                       0x10020D66u
/* ___report_gsfailure: GS failure reporter that captures processor state and terminates through the Windows unhandled-exception path. */
#define QLR_UI_ADDR____REPORT_GSFAILURE                          0x10020D89u
/* __onexit: Registers an atexit callback through the encoded CRT onexit tables, falling back to _onexit when the DLL CRT is not initialized. */
#define QLR_UI_ADDR___ONEXIT                                     0x10020E9Bu
/* CRT_UnlockOnExitTable: Tiny CRT cleanup stub that releases lock 8 after __dllonexit updates the encoded onexit tables. */
#define QLR_UI_ADDR_CRT_UNLOCKONEXITTABLE                        0x10020F33u
/* _atexit: Thin wrapper over __onexit that returns 0 on success and -1 on failure. */
#define QLR_UI_ADDR__ATEXIT                                      0x10020F3Cu
/* __ValidateImageBase: Checks the DOS and PE signatures for a candidate module image before CRT section scanning. */
#define QLR_UI_ADDR___VALIDATEIMAGEBASE                          0x10020FA0u
/* __FindPESection: Finds the PE section record that covers a candidate RVA inside the current image. */
#define QLR_UI_ADDR___FINDPESECTION                              0x10020FE0u
/* __IsNonwritableInCurrentImage: Uses __ValidateImageBase and __FindPESection to test whether a pointer lies in a non-writable section of the current module image. */
#define QLR_UI_ADDR___ISNONWRITABLEINCURRENTIMAGE                0x10021030u
/* initterm: CRT thunk that tail-calls the initterm constructor walker. */
#define QLR_UI_ADDR_INITTERM                                     0x100210ECu
/* initterm_e: CRT thunk that tail-calls the initterm_e constructor walker. */
#define QLR_UI_ADDR_INITTERM_E                                   0x100210F2u
/* _amsg_exit: CRT fatal-startup message exit thunk. */
#define QLR_UI_ADDR__AMSG_EXIT                                   0x100210F8u
/* _DllMain@12: Small DLL entry wrapper that tail-calls the module's exported dllEntry function. */
#define QLR_UI_ADDR__DLLMAIN_12                                  0x10021104u
/* __SEH_prolog4: Exact MSVC SEH frame prolog helper for GS-protected functions. */
#define QLR_UI_ADDR___SEH_PROLOG4                                0x10021130u
/* __SEH_epilog4: Exact MSVC SEH frame epilog helper for GS-protected functions. */
#define QLR_UI_ADDR___SEH_EPILOG4                                0x10021175u
/* __except_handler4: Exact EH4 exception handler wrapper that forwards into _except_handler4_common with the security-cookie callbacks. */
#define QLR_UI_ADDR___EXCEPT_HANDLER4                            0x10021189u
/* ___security_init_cookie: MSVC GS cookie initializer that seeds __security_cookie and its complement from time, pid, tid, tickcount, and performance-counter state. */
#define QLR_UI_ADDR____SECURITY_INIT_COOKIE                      0x100211AEu
/* _crt_debugger_hook: CRT debugger hook thunk. */
#define QLR_UI_ADDR__CRT_DEBUGGER_HOOK                           0x1002124Au
/* _unlock: CRT lock-release thunk. */
#define QLR_UI_ADDR__UNLOCK                                      0x10021256u
/* __dllonexit: CRT DLL onexit registration thunk. */
#define QLR_UI_ADDR___DLLONEXIT                                  0x1002125Cu
/* _lock: CRT lock-acquire thunk. */
#define QLR_UI_ADDR__LOCK                                        0x10021262u
/* except_handler4_common: CRT EH4 common-handler thunk. */
#define QLR_UI_ADDR_EXCEPT_HANDLER4_COMMON                       0x10021268u
/* __ftol2_sse: Compiler float-to-int helper that uses the SSE fast path when enabled and falls back to __ftol2 otherwise. */
#define QLR_UI_ADDR___FTOL2_SSE                                  0x10021270u
/* __ftol2: Compiler x87 long-double-to-int helper used by retail color, layout, and coordinate conversion code. */
#define QLR_UI_ADDR___FTOL2                                      0x100212A6u
/* memset: Imported memset thunk. */
#define QLR_UI_ADDR_MEMSET                                       0x1002131Cu
/* _CIcos: Compiler intrinsic cosine thunk. */
#define QLR_UI_ADDR__CICOS                                       0x10021322u
/* _CIsin: Compiler intrinsic sine thunk. */
#define QLR_UI_ADDR__CISIN                                       0x10021328u
/* __alloca_probe: Stack probing helper used before large local allocations. */
#define QLR_UI_ADDR___ALLOCA_PROBE                               0x10021330u
/* _CIatan2: Compiler intrinsic atan2 thunk. */
#define QLR_UI_ADDR__CIATAN2                                     0x1002135Cu
/* _CItan: Compiler intrinsic tangent thunk. */
#define QLR_UI_ADDR__CITAN                                       0x10021362u
/* __aulldiv: Compiler unsigned 64-bit division helper. */
#define QLR_UI_ADDR___AULLDIV                                    0x10021370u
/* __allmul: Compiler 64-bit multiply helper. */
#define QLR_UI_ADDR___ALLMUL                                     0x100213E0u

#endif /* QLR_UI_GHIDRA_REFERENCE_H */
