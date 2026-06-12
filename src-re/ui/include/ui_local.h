/*
=============
src-re/ui/include/ui_local.h

Quake Live UI Module — reverse-engineered local declarations.

This header is part of the src-re/ui reconstruction workspace and pulls
together the function prototypes, key types, and syscall-table entry offsets
that were recovered from:

  references/symbol-maps/ui.json
  references/reverse-engineering/ghidra/uix86/
  references/hlil/quakelive/uix86.all/

It is separate from the read-only src/code/ui/ui_local.h.  Include that
header for the open-source Quake III Arena baseline; include this one for
Quake Live-specific reconstruction additions.

Binary reference: assets/quakelive/baseq3/uix86.dll
MD5: 64321E7C6357A59063AE8900E2A20732
=============
*/

#ifndef QLR_UI_LOCAL_H
#define QLR_UI_LOCAL_H

#include "../../../src/code/game/q_shared.h"
#include "../../../src/code/ui/ui_public.h"

/* -----------------------------------------------------------------------
   Retail native import-table layout (DAT_106b40a8 in Ghidra).
   Indices are 32-bit-pointer slots; slot i == table_base + i*4.
   This is distinct from the legacy source/QVM uiImport_t syscall ABI.
   ----------------------------------------------------------------------- */

#define QL_UITRAP_PRINT                         0x00	/* offset 0x000 */
#define QL_UITRAP_ERROR                         0x01	/* offset 0x004 */
#define QL_UITRAP_MILLISECONDS                  0x02	/* offset 0x008 */
#define QL_UITRAP_REAL_TIME                     0x03	/* offset 0x00C */
#define QL_UITRAP_CVAR_REGISTER                 0x04	/* offset 0x010 */
#define QL_UITRAP_CVAR_CREATE                   0x05	/* offset 0x014 */
#define QL_UITRAP_CVAR_UPDATE                   0x06	/* offset 0x018 */
#define QL_UITRAP_CVAR_SET                      0x07	/* offset 0x01C */
#define QL_UITRAP_CVAR_SET_VALUE                0x08	/* offset 0x020 */
#define QL_UITRAP_CVAR_VARIABLE_STRING_BUFFER   0x09	/* offset 0x024 */
#define QL_UITRAP_CVAR_VARIABLE_VALUE           0x0A	/* offset 0x028 */
#define QL_UITRAP_ARGC                          0x0B	/* offset 0x02C */
#define QL_UITRAP_ARGV                          0x0C	/* offset 0x030 */
#define QL_UITRAP_CMD_ARGS_BUFFER               0x0D	/* offset 0x034 */
#define QL_UITRAP_FS_FOPENFILE                  0x0E	/* offset 0x038 */
#define QL_UITRAP_FS_READ                       0x0F	/* offset 0x03C */
#define QL_UITRAP_FS_WRITE                      0x10	/* offset 0x040 */
#define QL_UITRAP_FS_FCLOSEFILE                 0x11	/* offset 0x044 */
#define QL_UITRAP_FS_SEEK                       0x12	/* offset 0x048 */
#define QL_UITRAP_FS_GETFILELIST                0x13	/* offset 0x04C */
#define QL_UITRAP_CMD_EXECUTETEXT               0x14	/* offset 0x050 */
#define QL_UITRAP_R_REGISTERMODEL               0x15	/* offset 0x054 */
#define QL_UITRAP_R_REGISTERSKIN                0x16	/* offset 0x058 */
#define QL_UITRAP_R_REGISTERSHADERNOMIP         0x17	/* offset 0x05C */
#define QL_UITRAP_R_CLEARSCENE                  0x18	/* offset 0x060 */
#define QL_UITRAP_R_ADDREFENTITYTOSCENE         0x19	/* offset 0x064 */
#define QL_UITRAP_R_ADDPOLYTOSCENE              0x1A	/* offset 0x068 */
#define QL_UITRAP_R_ADDLIGHTTOSCENE             0x1B	/* offset 0x06C */
#define QL_UITRAP_R_RENDERSCENE                 0x1C	/* offset 0x070 */
#define QL_UITRAP_R_SETCOLOR                    0x1D	/* offset 0x074 */
#define QL_UITRAP_R_DRAWSTRETCHPIC              0x1E	/* offset 0x078 */
#define QL_UITRAP_R_MODELBOUNDS                 0x1F	/* offset 0x07C */
#define QL_UITRAP_UPDATESCREEN                  0x20	/* offset 0x080 */
#define QL_UITRAP_CM_LERPTAG                    0x21	/* offset 0x084 */
#define QL_UITRAP_S_STARTLOCALSOUND             0x22	/* offset 0x088 */
#define QL_UITRAP_S_REGISTERSOUND               0x23	/* offset 0x08C */
#define QL_UITRAP_KEY_KEYNUMTOSTRINGBUF         0x24	/* offset 0x090 */
#define QL_UITRAP_KEY_GETBINDINGBUF             0x25	/* offset 0x094 */
#define QL_UITRAP_KEY_SETBINDING                0x26	/* offset 0x098 */
#define QL_UITRAP_KEY_ISDOWN                    0x27	/* offset 0x09C */
#define QL_UITRAP_KEY_GETOVERSTRIKEMODE         0x28	/* offset 0x0A0 */
#define QL_UITRAP_KEY_SETOVERSTRIKEMODE         0x29	/* offset 0x0A4 */
#define QL_UITRAP_KEY_CLEARSTATES               0x2A	/* offset 0x0A8 */
#define QL_UITRAP_KEY_GETCATCHER                0x2B	/* offset 0x0AC */
#define QL_UITRAP_KEY_SETCATCHER                0x2C	/* offset 0x0B0 */
#define QL_UITRAP_GETCLIPBOARDDATA              0x2D	/* offset 0x0B4 */
#define QL_UITRAP_GETCLIENTSTATE                0x2E	/* offset 0x0B8 */
#define QL_UITRAP_GETGLCONFIG                   0x2F	/* offset 0x0BC */
#define QL_UITRAP_GETCONFIGSTRING               0x30	/* offset 0x0C0 */
#define QL_UITRAP_LAN_GETSERVERCOUNT            0x31	/* offset 0x0C4 */
#define QL_UITRAP_LAN_GETSERVERADDRESSSTRING    0x32	/* offset 0x0C8 */
#define QL_UITRAP_LAN_GETSERVERINFO             0x33	/* offset 0x0CC */
#define QL_UITRAP_LAN_GETSERVERPING             0x34	/* offset 0x0D0 */
#define QL_UITRAP_LAN_GETPINGQUEUECOUNT         0x35	/* offset 0x0D4 */
#define QL_UITRAP_LAN_CLEARPING                 0x36	/* offset 0x0D8 */
#define QL_UITRAP_LAN_GETPING                   0x37	/* offset 0x0DC */
#define QL_UITRAP_LAN_GETPINGINFO               0x38	/* offset 0x0E0 */
#define QL_UITRAP_LAN_LOADCACHEDSERVERS         0x39	/* offset 0x0E4 */
#define QL_UITRAP_LAN_SAVECACHEDSERVERS         0x3A	/* offset 0x0E8 */
#define QL_UITRAP_LAN_MARKSERVERVISIBLE         0x3B	/* offset 0x0EC */
#define QL_UITRAP_LAN_SERVERISVISIBLE           0x3C	/* offset 0x0F0 */
#define QL_UITRAP_LAN_UPDATEVISIBLEPINGS        0x3D	/* offset 0x0F4 */
#define QL_UITRAP_LAN_ADDSERVER                 0x3E	/* offset 0x0F8 */
#define QL_UITRAP_LAN_REMOVESERVER              0x3F	/* offset 0x0FC */
#define QL_UITRAP_LAN_RESETPINGS                0x40	/* offset 0x100 */
#define QL_UITRAP_LAN_SERVERSTATUS              0x41	/* offset 0x104 */
#define QL_UITRAP_LAN_COMPARESERVERS            0x42	/* offset 0x108 */
#define QL_UITRAP_MEMORY_REMAINING              0x43	/* offset 0x10C */
#define QL_UITRAP_GET_CDKEY                     0x44	/* offset 0x110 */
#define QL_UITRAP_SET_CDKEY                     0x45	/* offset 0x114 */
#define QL_UITRAP_R_REGISTERFONT                0x46	/* offset 0x118 */
#define QL_UITRAP_S_STOPBACKGROUNDTRACK         0x47	/* offset 0x11C */
#define QL_UITRAP_S_STARTBACKGROUNDTRACK        0x48	/* offset 0x120 */
#define QL_UITRAP_CIN_PLAYCINEMATIC             0x49	/* offset 0x124 */
#define QL_UITRAP_CIN_STOPCINEMATIC             0x4A	/* offset 0x128 */
#define QL_UITRAP_CIN_DRAWCINEMATIC             0x4B	/* offset 0x12C */
#define QL_UITRAP_CIN_RUNCINEMATIC              0x4C	/* offset 0x130 */
#define QL_UITRAP_CIN_SETEXTENTS                0x4D	/* offset 0x134 */
#define QL_UITRAP_R_REMAP_SHADER                0x4E	/* offset 0x138 */
#define QL_UITRAP_VERIFY_CDKEY                  0x4F	/* offset 0x13C */
#define QL_UITRAP_SETUP_ADVERT_CELL_SHADER      0x50	/* offset 0x140 */
#define QL_UITRAP_REFRESH_ADVERT_CELL_SHADER    0x51	/* offset 0x144 */
#define QL_UITRAP_INIT_ADVERTISEMENT_BRIDGE     0x52	/* offset 0x148 */
#define QL_UITRAP_UNUSED_83                     0x53	/* offset 0x14C / update-advert callback */
#define QL_UITRAP_ACTIVATE_ADVERT               0x54	/* offset 0x150 */
#define QL_UITRAP_UNUSED_85                     0x55	/* offset 0x154 */
#define QL_UITRAP_SET_CURSOR_POS                0x56	/* offset 0x158 */
#define QL_UITRAP_GET_CURSOR_POS                0x57	/* offset 0x15C */
#define QL_UITRAP_PC_ADD_GLOBAL_DEFINE          0x58	/* offset 0x160 */
#define QL_UITRAP_PC_LOAD_SOURCE                0x59	/* offset 0x164 */
#define QL_UITRAP_PC_FREE_SOURCE                0x5A	/* offset 0x168 */
#define QL_UITRAP_PC_READ_TOKEN                 0x5B	/* offset 0x16C */
#define QL_UITRAP_PC_SOURCE_FILE_AND_LINE       0x5C	/* offset 0x170 */
#define QL_UITRAP_IS_SUBSCRIBED_APP             0x5D	/* offset 0x174 */
#define QL_UITRAP_DRAW_SCALED_TEXT              0x5E	/* offset 0x178 */
#define QL_UITRAP_MEASURE_TEXT                  0x5F	/* offset 0x17C */
#define QL_UITRAP_GET_ITEM_DOWNLOAD_INFO        0x60	/* offset 0x180 */

/* -----------------------------------------------------------------------
   Retail display-context scale state (recovered from UI_RefreshDisplayContextScale).
   ----------------------------------------------------------------------- */

typedef struct {
	float	xscale;		/* pixel-width  / 640.0 */
	float	yscale;		/* pixel-height / 480.0 */
	float	xbias;		/* horizontal letter-box offset */
	float	ybias;		/* vertical letter-box offset */
	int		width;		/* current renderer width  (glconfig.vidWidth)  */
	int		height;		/* current renderer height (glconfig.vidHeight) */
} qlr_ui_scale_t;

/* -----------------------------------------------------------------------
   Key entry-point prototypes — exported from uix86.dll and recovered from
   references/reverse-engineering/ghidra/uix86/decompile_annotated.c.
   ----------------------------------------------------------------------- */

/* Module bootstrap — Ordinal 1 / dllEntry @ 0x10003970 */
void	dllEntry( void *syscallTable );

/* Secondary entry point @ 0x10020d66 (CRT init, not a UI API function) */
/* void	entry( void ); */

/* -----------------------------------------------------------------------
   Native UI API dispatch — _UI_* functions are the engine-facing entry
   points called via the DLL export table set up in dllEntry.
   ----------------------------------------------------------------------- */

void	_UI_Init( int singlePlayerMenu );
void	_UI_Shutdown( void );
void	_UI_KeyEvent( int key, qboolean down );
void	_UI_MouseEvent( int dx, int dy );
void	_UI_Refresh( int realtime );
qboolean _UI_IsFullscreen( void );
void	_UI_SetActiveMenu( uiMenuCommand_t menu );
qboolean _UI_ConsoleCommand( int realtime );
void	UI_DrawConnectScreen( qboolean overlay );

/* -----------------------------------------------------------------------
   Display-context refresh helpers.
   ----------------------------------------------------------------------- */

void	UI_RefreshDisplayContext( void );
void	UI_RefreshDisplayContextScale( void );
void	UI_RegisterCvars( void );

/* -----------------------------------------------------------------------
   Gametype / callvote helpers (recovered from UI_GetCallvoteGametypeToken).
   ----------------------------------------------------------------------- */

const char	*UI_GetCallvoteGametypeToken( int gametype );
int	UI_StartingWeaponIndexFromToken( void );

/* -----------------------------------------------------------------------
   Math utilities — thin wrappers that mirror the cgame/game copies.
   ----------------------------------------------------------------------- */

void	AnglesToAxis( const vec3_t angles, vec3_t axis[3] );
void	AngleSubtract( float a1, float a2, float *out );
void	MatrixMultiply( float in1[3][3], float in2[3][3], float out[3][3] );
void	AngleVectors( const vec3_t angles, vec3_t forward, vec3_t right, vec3_t up );

/* -----------------------------------------------------------------------
   String / parse utilities.
   ----------------------------------------------------------------------- */

int	COM_Compress( char *data_p );
char	*COM_ParseExt( char **data_p, qboolean allowLineBreaks );
qboolean String_IsNumeric( const char *s );
int	Q_stricmpn( const char *s1, const char *s2, int n );
int	Q_stricmp( const char *s1, const char *s2 );
void	Q_strncpyz( char *dest, const char *src, int destsize );
void	Q_CleanStr( char *string );
void	Com_sprintf( char *dest, int size, const char *fmt, ... );
char	*va( const char *format, ... );

#endif /* QLR_UI_LOCAL_H */
