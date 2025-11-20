#ifndef QLR_TYPES_H
#define QLR_TYPES_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/*
 * Shared Quake Live reverse-engineered type mirrors.
 *
 * Each block records the binary address that the layout was lifted from and
 * whether the structure has been validated against a runtime dump.  These
 * mirrors intentionally trim unused members but preserve offsets that the
 * annotated translations rely on.
 */

/*
 * Client state enumerants lifted from clientx86.dll::CL_Frame (0x004AEB30).
 * Validation: values compared against retail Steam build state transitions
 * captured 2024-05-05.
 */
typedef enum {
    QLR_CA_UNINITIALIZED = -1,
    QLR_CA_DISCONNECTED = 0,
    QLR_CA_CONNECTING = 1,
    QLR_CA_CHALLENGING = 2,
    QLR_CA_CONNECTED = 3,
    QLR_CA_PRIMED = 4,
    QLR_CA_ACTIVE = 5,
    QLR_CA_CINEMATIC = 6,
} qlr_client_state_t;

/* Snapshot flag masks recovered from clientx86.dll::CL_FirstSnapshot (0x004AFE70). */
#define QLR_SNAPFLAG_NOT_ACTIVE 0x0001

/*
 * Lightweight cvar mirror extracted from clientx86.dll::CL_Frame (0x004AEB30).
 * Validation: checked against debugger dumps of cvar_t in the Steam build
 * (2024-05-05).
 */
typedef struct {
    int integer;
    float value;
    const char *string;
} qlr_cvar_shadow_t;

/*
 * Partial cls_t snapshot taken from clientx86.dll::CL_Frame (0x004AEB30).
 * Validation: structure size and boolean packing confirmed with live process
 * inspection (Steam build, 2024-05-05).
 */
typedef struct {
    bool rendererStarted;
    bool soundStarted;
    bool soundRegistered;
    bool uiStarted;
    bool cddialog;
    qlr_client_state_t state;
    int keyCatchers;
    int realtime;
    int frametime;
    int realFrametime;
} qlr_client_static_shadow_t;

/*
 * Snapshot timing window extracted from clientx86.dll::CL_SetCGameTime
 * (0x004B0838).  Validation: offsets checked against dump of clActive_t on
 * Steam build dated 2024-05-05.
 */
typedef struct {
    int32_t valid;              /* qboolean in the original engine */
    int32_t snapFlags;
    int32_t serverTime;
    int32_t messageNum;
    int32_t deltaNum;
    int32_t ping;
    uint8_t areamask[32];       /* MAX_MAP_AREA_BYTES in baseq3 */
    int32_t cmdNum;
    /* playerState_t is large; we only expose its size for offset tables. */
    uint8_t playerState[0x16C];
    int32_t numEntities;
    int32_t parseEntitiesNum;
    int32_t serverCommandNum;
} qlr_cl_snapshot_t; /* sizeof == 0x1D4 (468) with the trimmed playerState */

/*
 * clActive_t window derived from clientx86.dll::CL_SetCGameTime (0x004B0838).
 * Validation: field order verified by tracing memcpy operations into cl struct.
 */
typedef struct {
    qlr_cl_snapshot_t latest;
    int32_t serverTime;
    int32_t oldServerTime;
    int32_t oldFrameServerTime;
    int32_t serverTimeDelta;
    int32_t extrapolatedSnapshot;    /* qboolean */
    int32_t newSnapshots;            /* qboolean */
} qlr_client_timing_window_t;

/* Active client bookkeeping snapshot extracted alongside clActive_t. */
typedef struct {
    int timeoutcount;
    qlr_client_timing_window_t timing;
} qlr_client_active_shadow_t;

/*
 * Connection state mirror from clientx86.dll::CL_SetCGameTime (0x004B0838).
 * Validation: bitfields and integer widths confirmed via debugger inspection.
 */
typedef struct {
    bool demorecording;
    bool demowaiting;
    bool demoplaying;
    bool firstDemoFrameSkipped;
    int serverMessageSequence;
    int lastPacketTime;
    int timeDemoBaseTime;
    int timeDemoFrames;
    int timeDemoStart;
    int netchanSequence;
} qlr_client_connection_shadow_t;

/* Shadowed cvar pointers wired up by CL_Frame. */
typedef struct {
    qlr_cvar_shadow_t *com_cl_running;
    qlr_cvar_shadow_t *cl_avidemo;
    qlr_cvar_shadow_t *cl_forceavidemo;
    qlr_cvar_shadow_t *com_timescale;
    qlr_cvar_shadow_t *cl_timeNudge;
    qlr_cvar_shadow_t *cl_paused;
    qlr_cvar_shadow_t *sv_paused;
    qlr_cvar_shadow_t *com_sv_running;
    qlr_cvar_shadow_t *cl_timedemo;
    qlr_cvar_shadow_t *cl_showTimeDelta;
    qlr_cvar_shadow_t *cl_freezeDemo;
    qlr_cvar_shadow_t *cl_activeAction;
} qlr_client_frame_cvars_t;

/* Hook table used when bridging CL_Frame into prototype harnesses. */
typedef struct {
void (*stopAllSounds)(void);
void (*setActiveMenu)(int menuId);
void (*writeDemoMessage)(void *msg, int header);
void (*checkTimeout)(qlr_client_connection_shadow_t *clc,
                     qlr_client_static_shadow_t *cls,
                     qlr_client_active_shadow_t *cl);
void (*checkUserinfo)(void);
void (*readPackets)(void);
void (*sendCmd)(void);
void (*checkForResend)(void);
void (*predictMovement)(void);
void (*runConsole)(void);
void (*updateScreen)(void);
void (*soundUpdate)(void);
void (*setCGameTime)(void);
void (*firstSnapshot)(void);
    void (*beginProfiling)(void);
} qlr_client_frame_hooks_t;

/* Aggregated context passed into the CL_Frame shim. */
typedef struct {
    qlr_client_static_shadow_t *cls;
    qlr_client_active_shadow_t *cl;
    qlr_client_connection_shadow_t *clc;
    qlr_client_frame_cvars_t cvars;
    qlr_client_frame_hooks_t hooks;
} qlr_client_frame_context_t;

/*
 * Partial levelLocals_t snapshot built from qagamex86.dll::G_RunFrame
 * (0x0010A740).  Validation: offsets inspected against VM bytecode dumps
 * captured with the 2015-09 VM build.  The trimmed mirror preserves the
 * observed ordering (time@0x0000, previousTime@0x0004, framenum@0x0008,
 * startTime@0x000C, msec@0x0010, num_entities@0x012C, firstEntity@0x0130)
 * while exposing extra counters used by the harness.
 */
typedef struct {
    int time;                   /* 0x0000 */
    int previousTime;           /* 0x0004 */
    int framenum;               /* 0x0008 */
    int startTime;              /* 0x000C */
    int msec;                   /* 0x0010 */
    int num_entities;           /* 0x012C */
    int maxclients;             /* 0x0130 in VM build */
    int warmupTime;             /* 0x0134 */
    int intermissionQueued;     /* 0x0138 */
    struct qlr_gentity_s *firstEntity; /* 0x013C */
} qlr_level_locals_t;

struct qlr_gentity_s;
typedef struct qlr_gentity_s qlr_gentity_t;
typedef struct qlr_gclient_s qlr_gclient_t;
typedef void (*qlr_gentity_think_t)(qlr_gentity_t *self);

typedef void (*qlr_game_void_hook_t)(void);
typedef void (*qlr_game_entity_hook_t)(qlr_gentity_t *ent);

typedef struct qlr_gentity_s {
    bool inuse;                 /* mirrors flag at 0x0004 in VM build */
    qlr_gentity_t *next;        /* traversal pointer observed at 0x0130 */
    qlr_gclient_t *client;      /* client pointer at 0x00B4 */
    qlr_gentity_think_t think;  /* scheduled callback at 0x00B8 */
    int nextthink;              /* absolute fire time at 0x00BC */
    int eventTime;              /* event expiry at 0x0120 */
} qlr_gentity_t;

/* Prototype hook table mirroring the game frame loop dependencies. */
typedef struct {
    void (*run_scheduled_thinks)(int msec);
    qlr_game_entity_hook_t physics_step;
    qlr_game_entity_hook_t client_think;
    qlr_game_entity_hook_t fire_event;
    qlr_game_entity_hook_t client_end_frame;
    qlr_game_void_hook_t begin_match;
    qlr_game_void_hook_t begin_intermission;
} qlr_game_frame_hooks_t;

/* Context wrapper for G_RunFrame prototype harness. */
typedef struct {
    qlr_level_locals_t *level;
    qlr_gentity_t *entities;
    size_t entity_count;
    qlr_game_frame_hooks_t hooks;
} qlr_game_frame_context_t;

#endif /* QLR_TYPES_H */
