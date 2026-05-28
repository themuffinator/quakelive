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
// client.h -- primary header for client

#include <stdint.h>

#include "../game/q_shared.h"
#include "../qcommon/qcommon.h"
#include "../renderer/tr_public.h"
#include "../ui/ui_public.h"
#include "keys.h"
#include "snd_public.h"
#include "../cgame/cg_public.h"
#include "../game/bg_public.h"

#define	RETRANSMIT_TIMEOUT	3000	// time between connection packet retransmits
#define KEYCATCH_RETAIL_MOUSEPASS	0x0010
#define KEYCATCH_BROWSER			0x0020


// snapshots are a view of the server at a given time
typedef struct {
	qboolean		valid;			// cleared if delta parsing was invalid
	int				snapFlags;		// rate delayed and dropped commands

	int				serverTime;		// server time the message is valid for (in msec)

	int				messageNum;		// copied from netchan->incoming_sequence
	int				deltaNum;		// messageNum the delta is from
	int				ping;			// time from when cmdNum-1 was sent to time packet was reeceived
	byte			areamask[MAX_MAP_AREA_BYTES];		// portalarea visibility bits

	int				cmdNum;			// the next cmdNum the server is expecting
	playerState_t	ps;						// complete information about the current player at this time

	int				numEntities;			// all of the entities that need to be presented
	int				parseEntitiesNum;		// at the time of this snapshot

	int				serverCommandNum;		// execute all commands up to this before
											// making the snapshot current
} clSnapshot_t;



/*
=============================================================================

the clientActive_t structure is wiped completely at every
new gamestate_t, potentially several times during an established connection

=============================================================================
*/

typedef struct {
	int		p_cmdNumber;		// cl.cmdNumber when packet was sent
	int		p_serverTime;		// usercmd->serverTime when packet was sent
	int		p_realtime;			// cls.realtime when packet was sent
} outPacket_t;

// the parseEntities array must be large enough to hold PACKET_BACKUP frames of
// entities, so that when a delta compressed message arives from the server
// it can be un-deltad from the original 
#define	MAX_PARSE_ENTITIES	2048

extern int g_console_field_width;

typedef struct {
	int			timeoutcount;		// it requres several frames in a timeout condition
									// to disconnect, preventing debugging breaks from
									// causing immediate disconnects on continue
	clSnapshot_t	snap;			// latest received from server

	int			serverTime;			// may be paused during play
	int			oldServerTime;		// to prevent time from flowing bakcwards
	int			oldFrameServerTime;	// to check tournament restarts
	int			serverTimeDelta;	// cl.serverTime = cls.realtime + cl.serverTimeDelta
									// this value changes as net lag varies
	qboolean	extrapolatedSnapshot;	// set if any cgame frame has been forced to extrapolate
									// cleared when CL_AdjustTimeDelta looks at it
	qboolean	newSnapshots;		// set on parse of any valid packet

	gameState_t	gameState;			// configstrings
	char		mapname[MAX_QPATH];	// extracted from CS_SERVERINFO

	int			parseEntitiesNum;	// index (not anded off) into cl_parse_entities[]

	int			mouseDx[2], mouseDy[2];	// added to by mouse events
	int			mouseIndex;
	int			joystickAxis[MAX_JOYSTICK_AXIS];	// set by joystick events

	// cgame communicates a few values to the client system
	int			cgameUserCmdValue;	// current weapon to add to usercmd_t
	int			cgameUserCmdPrimary;	// current queued primary weapon to add to usercmd_t
	int			cgameUserCmdFov;	// current fov byte to add to usercmd_t
	float		cgameSensitivity;

	// cmds[cmdNumber] is the predicted command, [cmdNumber-1] is the last
	// properly generated command
	usercmd_t	cmds[CMD_BACKUP];	// each mesage will send several old cmds
	int			cmdNumber;			// incremented each frame, because multiple
									// frames may need to be packed into a single packet

	outPacket_t	outPackets[PACKET_BACKUP];	// information about each packet we have sent out

	// the client maintains its own idea of view angles, which are
	// sent to the server each frame.  It is cleared to 0 upon entering each level.
	// the server sends a delta each frame which is added to the locally
	// tracked view angles to account for standing on rotating objects,
	// and teleport direction changes
	vec3_t		viewangles;

	int			serverId;			// included in each client message so the server
												// can tell if it is for a prior map_restart
	// big stuff at end of structure so most offsets are 15 bits or less
	clSnapshot_t	snapshots[PACKET_BACKUP];

	entityState_t	entityBaselines[MAX_GENTITIES];	// for delta compression when not in previous frame

	entityState_t	parseEntities[MAX_PARSE_ENTITIES];
} clientActive_t;

extern	clientActive_t		cl;

/*
=============================================================================

the clientConnection_t structure is wiped when disconnecting from a server,
either to go to a full screen console, play a demo, or connect to a different server

A connection can be to either a server through the network layer or a
demo through a file.

=============================================================================
*/


typedef struct {

	int			clientNum;
	int			lastPacketSentTime;			// for retransmits during connection
	int			lastPacketTime;				// for timeouts

	netadr_t	serverAddress;
	int			connectTime;				// for connection retransmits
	int			connectPacketCount;			// for display on connection dialog
	char		serverMessage[MAX_STRING_TOKENS];	// for display on connection dialog

	int			challenge;					// from the server to use for connecting
	int			checksumFeed;				// from the server for checksum calculations

	// these are our reliable messages that go to the server
	int			reliableSequence;
	int			reliableAcknowledge;		// the last one the server has executed
	char		reliableCommands[MAX_RELIABLE_COMMANDS][MAX_STRING_CHARS];

	// server message (unreliable) and command (reliable) sequence
	// numbers are NOT cleared at level changes, but continue to
	// increase as long as the connection is valid

	// message sequence is used by both the network layer and the
	// delta compression layer
	int			serverMessageSequence;

	// reliable messages received from server
	int			serverCommandSequence;
	int			lastExecutedServerCommand;		// last server command grabbed or executed with CL_GetServerCommand
	char		serverCommands[MAX_RELIABLE_COMMANDS][MAX_STRING_CHARS];

	// file transfer from server
	fileHandle_t download;
	char		downloadTempName[MAX_OSPATH];
	char		downloadName[MAX_OSPATH];
	int			downloadNumber;
	int			downloadBlock;	// block we are waiting for
	int			downloadCount;	// how many bytes we got
	int			downloadSize;	// how many bytes we got
	char		downloadList[MAX_INFO_STRING]; // list of paks we need to download
	qboolean	downloadRestart;	// if true, we need to do another FS_Restart because we downloaded a pak

	// demo information
	char		demoName[MAX_QPATH];
	qboolean	spDemoRecording;
	qboolean	demorecording;
	qboolean	demoplaying;
	qboolean	demowaiting;	// don't record until a non-delta message is received
	qboolean	firstDemoFrameSkipped;
	fileHandle_t	demofile;

	int			timeDemoFrames;		// counter of rendered frames
	int			timeDemoStart;		// cls.realtime before first frame
	int			timeDemoBaseTime;	// each frame will be at this time + frameNum * 50

	// big stuff at end of structure so most offsets are 15 bits or less
	netchan_t	netchan;
} clientConnection_t;

extern	clientConnection_t clc;

qboolean CL_IsSteamIdentityMuted( unsigned int identityLow, unsigned int identityHigh );

/*
==================================================================

the clientStatic_t structure is never wiped, and is used even when
no client connection is active at all

==================================================================
*/

typedef struct {
	netadr_t	adr;
	int			start;
	int			time;
	char		info[MAX_INFO_STRING];
} ping_t;

typedef struct {
	netadr_t	adr;
	char	  	hostName[MAX_NAME_LENGTH];
	char	  	mapName[MAX_NAME_LENGTH];
	char	  	game[MAX_NAME_LENGTH];
	int			netType;
	int			gameType;
	int		  	clients;
	int		  	maxClients;
	int			minPing;
	int			maxPing;
	int			ping;
	qboolean	visible;
	int			punkbuster;
} serverInfo_t;

typedef struct {
	byte	ip[4];
	unsigned short	port;
} serverAddress_t;

typedef struct {
	connstate_t	state;				// connection status
	int			keyCatchers;		// bit flags

	qboolean	cddialog;			// bring up the cd needed dialog next frame

	char		servername[MAX_OSPATH];		// name of server from original connect (used by reconnect)

	// when the server clears the hunk, all of these must be restarted
	qboolean	rendererStarted;
	qboolean	soundStarted;
	qboolean	soundRegistered;
	qboolean	uiStarted;
	qboolean	cgameStarted;

	int			framecount;
	int			frametime;			// msec since last frame

	int			realtime;			// ignores pause
	int			realFrametime;		// ignoring pause, so console always works

	int			numlocalservers;
	serverInfo_t	localServers[MAX_OTHER_SERVERS];

	int			numglobalservers;
	serverInfo_t  globalServers[MAX_GLOBAL_SERVERS];
	// additional global servers
	int			numGlobalServerAddresses;
	serverAddress_t		globalServerAddresses[MAX_GLOBAL_SERVERS];

	int			numfavoriteservers;
	serverInfo_t	favoriteServers[MAX_OTHER_SERVERS];

	int			nummplayerservers;
	serverInfo_t	mplayerServers[MAX_OTHER_SERVERS];

	int pingUpdateSource;		// source currently pinging or updating

	int masterNum;

	// update server info
	netadr_t	updateServer;
	char		updateChallenge[MAX_TOKEN_CHARS];
	char		updateInfoString[MAX_INFO_STRING];

	netadr_t	authorizeServer;

	// rendering info
	glconfig_t	glconfig;
	qhandle_t	charSetShader;
	qhandle_t	whiteShader;
	qhandle_t	recordShader;
	qhandle_t	consoleShader;
} clientStatic_t;

extern	clientStatic_t		cls;

//=============================================================================

extern	vm_t			*cgvm;	// interface to cgame dll or vm
extern	vm_t			*uivm;	// interface to ui dll or vm
extern	refexport_t		re;		// interface to refresh .dll


//
// cvars
//
extern	cvar_t	*cl_nodelta;
extern	cvar_t	*cl_debugMove;
extern	cvar_t	*cl_allowConsoleChat;
extern	cvar_t	*cl_timegraph;
extern	cvar_t	*cl_maxpackets;
extern	cvar_t	*cl_packetdup;
extern	cvar_t	*cl_shownet;
extern	cvar_t	*cl_showSend;
extern	cvar_t	*cl_timeNudge;
extern	cvar_t	*cl_showTimeDelta;
extern	cvar_t	*cl_freezeDemo;
extern	cvar_t	*cl_quitOnDemoCompleted;
extern	cvar_t	*cl_demoRecordMessage;
extern	cvar_t	*cl_avidemo_latch;
extern	cvar_t	*cl_avidemo_mintime;
extern	cvar_t	*cl_avidemo_maxtime;

extern	cvar_t	*cl_yawspeed;
extern	cvar_t	*cl_pitchspeed;
extern	cvar_t	*cl_run;
extern	cvar_t	*cl_anglespeedkey;
extern	cvar_t	*cl_viewAccel;

extern	cvar_t	*cl_sensitivity;
extern	cvar_t	*cl_freelook;

extern	cvar_t	*cl_mouseAccel;
extern	cvar_t	*cl_mouseAccelDebug;
extern	cvar_t	*cl_mouseAccelOffset;
extern	cvar_t	*cl_mouseAccelPower;
extern	cvar_t	*cl_mouseSensCap;

extern	cvar_t	*m_pitch;
extern	cvar_t	*m_yaw;
extern	cvar_t	*m_forward;
extern	cvar_t	*m_side;
extern	cvar_t	*m_filter;
extern	cvar_t	*m_cpi;

extern	cvar_t	*cl_timedemo;

extern	cvar_t	*cl_activeAction;
extern	cvar_t	*cl_platform;

extern	cvar_t	*cl_inGameVideo;

extern	cvar_t	*cl_autoTimeNudge;

//=================================================

//
// cl_main
//

void CL_Init (void);
void CL_FlushMemory(void);
void CL_ShutdownAll(void);
void CL_AddReliableCommand( const char *cmd );

void CL_StartHunkUsers( void );

void CL_Disconnect_f (void);
void CL_GetChallengePacket (void);
void CL_Vid_Restart_f( void );
void CL_Snd_Restart_f (void);
void CL_StartDemoLoop( void );
void CL_NextDemo( void );
void CL_ReadDemoMessage( void );

void CL_InitDownloads(void);
void CL_NextDownload(void);

void CL_GetPing( int n, char *buf, int buflen, int *pingtime );
void CL_GetPingInfo( int n, char *buf, int buflen );
void CL_ClearPing( int n );
int CL_GetPingQueueCount( void );

void CL_ShutdownRef( void );
void CL_InitRef( void );
qboolean CL_CDKeyValidate( const char *key, const char *checksum );
int CL_ServerStatus( char *serverAddress, char *serverStatusString, int maxLen );


//
// cl_input
//
typedef struct {
	int			down[2];		// key nums holding it down
	unsigned	downtime;		// msec timestamp
	unsigned	msec;			// msec down this frame if both a down and up happened
	qboolean	active;			// current state
	qboolean	wasPressed;		// set when down, not cleared when up
} kbutton_t;

extern	kbutton_t	in_mlook, in_klook;
extern 	kbutton_t 	in_strafe;
extern 	kbutton_t 	in_speed;

void CL_InitInput (void);
void CL_SendCmd (void);
void CL_ClearState (void);
void CL_ReadPackets (void);

void CL_WritePacket( void );
void IN_CenterView (void);

void CL_VerifyCode( void );
qboolean CL_ShouldFilterConsoleText( const char *text );
qboolean CL_OnlineServicesEnabled( void );
qboolean CL_SteamServicesEnabled( void );
void CL_LogMatchmakingServiceIgnored( const char *commandName, const char *reason );
qboolean CL_Steam_OpenOverlayUrl( const char *url );
void CL_LocalServers_f( void );
void CL_GlobalServers_f( void );
qboolean CL_Steam_RequestServers( int requestMode );
qboolean CL_Steam_RequestServerDetails( unsigned int serverIp, unsigned short serverPort );
qboolean CL_Steam_RefreshServerList( void );
qboolean CL_Steam_CreateLobby( void );
qboolean CL_Steam_LeaveLobby( void );
qboolean CL_Steam_JoinLobby( const char *lobbyId );
qboolean CL_Steam_SetLobbyServer( unsigned int serverIp, unsigned short serverPort );
qboolean CL_Steam_ShowInviteOverlay( void );
qboolean CL_Steam_Invite( const char *steamId );
qboolean CL_Steam_SayLobby( const char *message );
qboolean CL_Steam_RequestAllUGC( int filter );
qboolean CL_Steam_RequestUserStats( const char *steamId );
qboolean CL_Steam_ActivateOverlayToUser( const char *dialog, const char *steamId );
void CL_Steam_OnRichPresenceJoinRequested( const char *command );
void CL_Steam_OnGameServerChangeRequested( const char *server, const char *password );
qboolean CL_GetWorkshopDownloadInfo( unsigned int itemIdLow, unsigned int itemIdHigh, unsigned long long *outDownloaded, unsigned long long *outTotal );

float CL_KeyState (kbutton_t *key);
char *Key_KeynumToString (int keynum);
void CL_ToggleMenu_f( void );

//
// cl_parse.c
//
extern int cl_connectedToPureServer;

void CL_SystemInfoChanged( void );
void CL_ParseServerMessage( msg_t *msg );

//====================================================================

void	CL_ServerInfoPacket( netadr_t from, msg_t *msg );
void	CL_FavoriteServers_f( void );
qboolean CL_UpdateVisiblePings_f( int source );


//
// console
//
void Con_DrawCharacter (int cx, int line, int num);

void Con_CheckResize (void);
int Con_GetLineWidthForCurrentResolution( void );
void Con_UpdateFieldWidth( void );
void Con_Init (void);
void Con_Clear_f (void);
void Con_ToggleConsole_f (void);
void Con_DrawNotify (void);
void Con_ClearNotify (void);
void Con_RunConsole (void);
void Con_DrawConsole (void);
void Con_PageUp( void );
void Con_PageDown( void );
void Con_Top( void );
void Con_Bottom( void );
void Con_Close( void );


//
// cl_scrn.c
//
void	SCR_Init (void);
void	SCR_UpdateScreen (void);

void	SCR_DebugGraph (float value, int color);

int		SCR_GetBigStringWidth( const char *str );	// returns in virtual 640x480 coordinates

void	SCR_AdjustFrom640( float *x, float *y, float *w, float *h );
void	SCR_FillRect( float x, float y, float width, float height, 
					 const float *color );
void	SCR_DrawPic( float x, float y, float width, float height, qhandle_t hShader );
void	SCR_DrawNamedPic( float x, float y, float width, float height, const char *picname );

void	SCR_DrawBigString( int x, int y, const char *s, float alpha );			// draws host text with embedded color control characters with fade
void	SCR_DrawBigStringColor( int x, int y, const char *s, vec4_t color );	// draws fixed-color host text
void	SCR_DrawSmallStringExt( int x, int y, const char *string, float *setColor, qboolean forceColor );
void	SCR_DrawSmallChar( int x, int y, int ch );


//
// cl_cin.c
//

void CL_PlayCinematic_f( void );
void SCR_DrawCinematic (void);
void SCR_RunCinematic (void);
void SCR_StopCinematic (void);
int CIN_PlayCinematic( const char *arg0, int xpos, int ypos, int width, int height, int bits);
e_status CIN_StopCinematic(int handle);
e_status CIN_RunCinematic (int handle);
void CIN_DrawCinematic (int handle);
void CIN_SetExtents (int handle, int x, int y, int w, int h);
void CIN_SetLooping (int handle, qboolean loop);
void CIN_UploadCinematic(int handle);
void CIN_CloseAllVideos(void);

//
// cl_cgame.c
//
void CL_InitCGame( void );
void CL_ShutdownCGame( void );
qboolean CL_GameCommand( void );
void CL_CGameRendering( stereoFrame_t stereo );
void CL_SetCGameTime( void );
void CL_FirstSnapshot( void );
void CL_ShaderStateChanged(void);
void CL_WebPak_Init( void );
void CL_WebPak_Shutdown( void );
qboolean CL_WebPak_Available( void );
qboolean CL_WebPak_Fetch( const char *virtualPath, void **outBuffer, int *outLength );
int CL_WebPak_GetFileList( const char *path, const char *extension, char *listbuf, int bufsize );
qboolean CL_WebRequestResolve( const char *virtualPath, void **outBuffer, int *outLength );
qboolean CL_LauncherRequestData( const char *virtualPath, void **outBuffer, int *outLength );
void CL_RegisterFont( const char *fontName, int pointSize, fontInfo_t *font );
void RE_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor, const float *baseColor );
void RE_MeasureScaledText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outWidth, float *outHeight, float *outLeft );
qboolean RE_GetScaledFontMetrics( int fontHandle, float scale, float *outAscent, float *outDescent, float *outLineHeight );
qhandle_t CL_RegisterShaderFromRGBA( const char *name, const byte *pic, int width, int height, qboolean mipRawImage );
qhandle_t CL_RegisterShaderFromMemory( const char *name, const byte *buffer, int bufferLength, qboolean mipRawImage );
void CL_RefreshOnlineServicesBridgeState( void );
void QLWebHost_RegisterCommands( void );
void CL_WebHost_Init( void );
void CL_WebHost_Shutdown( void );
void CL_WebHost_Frame( void );
void CL_WebHost_BootstrapAwesomiumMenu( void );
qboolean CL_WebHost_HasLiveView( void );
qboolean CL_WebHost_HasBoundWindowObject( void );
qboolean CL_WebHost_HasDrawableSurface( void );
void CL_WebHost_DrawBrowserSurface( void );
void *CL_WebHost_GetCursorHandle( void );
void CL_WebHost_HideBrowser( void );
void CL_WebHost_NotifyAppActivation( qboolean active );
void CL_WebView_PublishEvent( const char *name, const char *payload );
void CL_WebView_InvokeCommNotice( const char *message );
void CL_WebView_PublishTaggedInfoString( const char *messageType, const char *infoString );
void CL_WebView_PublishGameError( const char *message );
void CL_WebView_PublishGameEnd( void );
void CL_WebView_PublishCvarChange( const char *name, const char *value, qboolean replicate );
void CL_WebView_PublishBindChanged( const char *name, const char *value );
void CL_WebView_PublishGameStart( void );
void CL_WebView_PublishGameDemo( const char *id, const char *name );
void CL_WebView_PublishGameScreenshot( const char *id, const char *name );
void CL_WebView_OnMouseMove( int x, int y );
void CL_WebView_OnMouseButtonEvent( int key, qboolean down );
void CL_WebView_OnMouseWheelEvent( int direction );
void CL_WebView_OnKeyEvent( int key, qboolean down );
qboolean CL_Awesomium_Startup( const char *runtimePath, const char *basePath, const char *playerName, unsigned int appId, unsigned int steamIdLow, unsigned int steamIdHigh, int width, int height );
qboolean CL_Awesomium_OpenURL( const char *url );
void CL_Awesomium_Update( void );
qboolean CL_Awesomium_Resize( int width, int height );
int CL_Awesomium_SurfaceWidth( void );
int CL_Awesomium_SurfaceHeight( void );
qboolean CL_Awesomium_SurfaceDirty( void );
qboolean CL_Awesomium_IsLoading( void );
qboolean CL_Awesomium_IsCrashed( void );
int CL_Awesomium_LastErrorCode( void );
qboolean CL_Awesomium_ExecuteJavascript( const char *script, const char *frame );
qboolean CL_Awesomium_SetZoom( int zoomPercent );
void CL_Awesomium_PauseRendering( void );
void CL_Awesomium_Unfocus( void );
qboolean CL_Awesomium_CopySurface( byte *destination, int width, int height, int rowSpan );
void CL_Awesomium_InjectMouseMove( int x, int y );
void CL_Awesomium_InjectMouseDown( int button );
void CL_Awesomium_InjectMouseUp( int button );
void CL_Awesomium_InjectMouseWheel( int direction );
void CL_Awesomium_InjectKeyboardEvent( unsigned int eventType, unsigned int virtualKeyCode, long nativeKeyCode );
void CL_Awesomium_Stop( void );
void CL_Awesomium_ClearCache( void );
void CL_Awesomium_Reload( qboolean ignoreCache );
void CL_Awesomium_Shutdown( void );
const char *CL_Awesomium_LastError( void );
qboolean CL_AdvertisementBridge_IsDelayElapsed( void );
void CL_AdvertisementBridge_ClearDelay( void );
void CL_AdvertisementBridge_RefreshLoadingViewParameters( void );
void CL_AdvertisementBridge_UpdateLoadingViewParameters( void );
void CL_AdvertisementBridge_InitUI( void );
void CL_AdvertisementBridge_ActivateAdvert( int cellId );
void CL_AdvertisementBridge_SetActiveAdvert( int cellId );
int CL_AdvertisementBridge_GetCellDisplayState( int cellId );
void CL_AdvertisementBridge_GetCellLabel( int cellId, char *buffer, int bufferSize );
int CL_AdvertisementBridge_GetLabelList1Count( void );
void CL_AdvertisementBridge_GetLabelList1Entry( int index, char *buffer, int bufferSize );
int CL_AdvertisementBridge_GetLabelList2Count( void );
void CL_AdvertisementBridge_GetLabelList2Entry( int index, char *buffer, int bufferSize );
qhandle_t CL_AdvertisementBridge_SetupUIAdvertCellShader( const char *defaultContent, const void *rect, int cellId );
qhandle_t CL_AdvertisementBridge_RefreshUIAdvertCellShader( const char *defaultContent, const void *rect, int cellId );
qhandle_t CL_AdvertisementBridge_SetupAdvertCellShader( const char *defaultContent, const void *rect, int cellId );
qhandle_t CL_AdvertisementBridge_RefreshAdvertCellShader( const char *defaultContent, const void *rect, int cellId );

//
// cl_ui.c
//
void CL_InitUI( void );
void CL_ShutdownUI( void );
qboolean UI_GameCommand( void );
int Key_GetCatcher( void );
void Key_SetCatcher( int catcher );
void LAN_LoadCachedServers();
void LAN_SaveServersToCache();
qhandle_t CL_Steam_RegisterShader( const char *url );
void CL_InitSteamResources( void );
void CL_ShutdownSteamResources( void );
void CL_ClearSteamResourceCache( qboolean clearPersisted );
void QL_ClientAuth_CancelSteamTicket( void );
qboolean QL_ClientAuth_RequestSteamChallengeTicket( byte *ticketBuffer, int ticketBufferSize, int *ticketLength, uint32_t *steamIdLow, uint32_t *steamIdHigh );
int CL_MenuReadScreenshot( const char *requestedName, byte *buffer, int bufferSize );


//
// cl_net_chan.c
//
void CL_Netchan_Transmit( netchan_t *chan, msg_t* msg);	//int length, const byte *data );
void CL_Netchan_TransmitNextFragment( netchan_t *chan );
qboolean CL_Netchan_Process( netchan_t *chan, msg_t *msg );
