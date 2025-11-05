#ifndef QLR_CLIENT_TYPES_H
#define QLR_CLIENT_TYPES_H

#include <stdbool.h>
#include <stdint.h>

#include "client_offsets.h"

/*
 * Shared lightweight mirrors of the Quake Live client singletons.  These are
 * deliberately smaller than the real structs but preserve the fields touched by
 * CL_Frame, CL_SetCGameTime, and the HUD rendering entry points.
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

typedef struct {
    int integer;
    float value;
    const char *string;
} qlr_cvar_shadow_t;

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

typedef struct {
    int timeoutcount;
    qlr_client_timing_window_t timing;
} qlr_client_active_shadow_t;

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

#endif /* QLR_CLIENT_TYPES_H */
