#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "client_math.h"
#include "client_offsets.h"
#include "client_types.h"

/*
 * Annotated versions of CL_AdjustTimeDelta, CL_FirstSnapshot, and
 * CL_SetCGameTime from src/code/client/cl_cgame.c.  These routines manage the
 * timing window that snapshot interpolation relies on.
 */

typedef struct {
    void (*errorDrop)(const char *reason);
    void (*print)(const char *text);
    void (*readDemoMessage)(void);
    void (*cbufAddText)(const char *text);
    void (*cvarSet)(const char *name, const char *value);
    void (*beginProfiling)(void);
} qlr_snapshot_hooks_t;

typedef struct {
    qlr_client_static_shadow_t *cls;
    qlr_client_active_shadow_t *cl;
    qlr_client_connection_shadow_t *clc;
    qlr_client_frame_cvars_t cvars;
    qlr_snapshot_hooks_t hooks;
} qlr_snapshot_context_t;

#define QLR_RESET_TIME 500

void QLR_CL_AdjustTimeDelta(qlr_snapshot_context_t *ctx) {
    qlr_client_timing_window_t *timing = &ctx->cl->timing;

    timing->newSnapshots = false;

    if (ctx->clc->demoplaying) {
        return;
    }

    int resetTime = ctx->cvars.com_sv_running && ctx->cvars.com_sv_running->integer ? 100 : QLR_RESET_TIME;
    int newDelta = timing->latest.serverTime - ctx->cls->realtime;
    int deltaDelta = abs(newDelta - timing->serverTimeDelta);

    if (deltaDelta > resetTime) {
        timing->serverTimeDelta = newDelta;
        timing->oldServerTime = timing->latest.serverTime;
        timing->serverTime = timing->latest.serverTime;
        if (ctx->cvars.cl_showTimeDelta && ctx->cvars.cl_showTimeDelta->integer && ctx->hooks.print) {
            ctx->hooks.print("<RESET> ");
        }
    } else if (deltaDelta > 100) {
        if (ctx->cvars.cl_showTimeDelta && ctx->cvars.cl_showTimeDelta->integer && ctx->hooks.print) {
            ctx->hooks.print("<FAST> ");
        }
        timing->serverTimeDelta = (timing->serverTimeDelta + newDelta) >> 1;
    } else {
        if (!ctx->cvars.com_timescale || ctx->cvars.com_timescale->value == 0.0f ||
            ctx->cvars.com_timescale->value == 1.0f) {
            if (timing->extrapolatedSnapshot) {
                timing->extrapolatedSnapshot = false;
                timing->serverTimeDelta -= 2;
            } else {
                timing->serverTimeDelta += 1;
            }
        }
    }

    if (ctx->cvars.cl_showTimeDelta && ctx->cvars.cl_showTimeDelta->integer && ctx->hooks.print) {
        char buffer[32];
        (void)snprintf(buffer, sizeof(buffer), "%d ", timing->serverTimeDelta);
        ctx->hooks.print(buffer);
    }
}

void QLR_CL_FirstSnapshot(qlr_snapshot_context_t *ctx) {
    if (ctx->cl->timing.latest.snapFlags & QLR_SNAPFLAG_NOT_ACTIVE) {
        return;
    }

    ctx->cls->state = QLR_CA_ACTIVE;
    ctx->cl->timing.serverTimeDelta = ctx->cl->timing.latest.serverTime - ctx->cls->realtime;
    ctx->cl->timing.oldServerTime = ctx->cl->timing.latest.serverTime;
    ctx->clc->timeDemoBaseTime = ctx->cl->timing.latest.serverTime;

    if (ctx->cvars.cl_activeAction && ctx->cvars.cl_activeAction->string &&
        ctx->cvars.cl_activeAction->string[0] && ctx->hooks.cbufAddText && ctx->hooks.cvarSet) {
        ctx->hooks.cbufAddText(ctx->cvars.cl_activeAction->string);
        ctx->hooks.cvarSet("activeAction", "");
    }

    if (ctx->hooks.beginProfiling) {
        ctx->hooks.beginProfiling();
    }
}

void QLR_CL_SetCGameTime(qlr_snapshot_context_t *ctx) {
    qlr_client_timing_window_t *timing = &ctx->cl->timing;

    if (ctx->cls->state != QLR_CA_ACTIVE) {
        if (ctx->cls->state != QLR_CA_PRIMED) {
            return;
        }
        if (ctx->clc->demoplaying) {
            if (!ctx->clc->firstDemoFrameSkipped) {
                ctx->clc->firstDemoFrameSkipped = true;
                return;
            }
            if (ctx->hooks.readDemoMessage) {
                ctx->hooks.readDemoMessage();
            }
        }
        if (timing->newSnapshots) {
            timing->newSnapshots = false;
            QLR_CL_FirstSnapshot(ctx);
        }
        if (ctx->cls->state != QLR_CA_ACTIVE) {
            return;
        }
    }

    if (!timing->latest.valid) {
        if (ctx->hooks.errorDrop) {
            ctx->hooks.errorDrop("CL_SetCGameTime: !cl.snap.valid");
        }
        return;
    }

    if (ctx->cvars.sv_paused && ctx->cvars.sv_paused->integer &&
        ctx->cvars.cl_paused && ctx->cvars.cl_paused->integer &&
        ctx->cvars.com_sv_running && ctx->cvars.com_sv_running->integer) {
        return;
    }

    if (timing->latest.serverTime < timing->oldFrameServerTime) {
        if (ctx->hooks.errorDrop) {
            ctx->hooks.errorDrop("cl.snap.serverTime < cl.oldFrameServerTime");
        }
        return;
    }
    timing->oldFrameServerTime = timing->latest.serverTime;

    if (!(ctx->clc->demoplaying && ctx->cvars.cl_freezeDemo && ctx->cvars.cl_freezeDemo->integer)) {
        int tn = ctx->cvars.cl_timeNudge ? ctx->cvars.cl_timeNudge->integer : 0;
        if (tn < -30) tn = -30;
        if (tn > 30) tn = 30;

        timing->serverTime = ctx->cls->realtime + timing->serverTimeDelta - tn;
        if (timing->serverTime < timing->oldServerTime) {
            timing->serverTime = timing->oldServerTime;
        }
        timing->oldServerTime = timing->serverTime;

        if (ctx->cls->realtime + timing->serverTimeDelta >= timing->latest.serverTime - 5) {
            timing->extrapolatedSnapshot = true;
        }
    }

    if (timing->newSnapshots) {
        QLR_CL_AdjustTimeDelta(ctx);
    }

    if (!ctx->clc->demoplaying) {
        return;
    }

    if (ctx->cvars.cl_timedemo && ctx->cvars.cl_timedemo->integer) {
        if (!ctx->clc->timeDemoStart) {
            ctx->clc->timeDemoStart = ctx->cls->realtime;
        }
        ctx->clc->timeDemoFrames++;
        timing->serverTime = ctx->clc->timeDemoBaseTime + ctx->clc->timeDemoFrames * 50;
    }

    while (timing->serverTime >= timing->latest.serverTime) {
        if (ctx->hooks.readDemoMessage) {
            ctx->hooks.readDemoMessage();
        }
        if (ctx->cls->state != QLR_CA_ACTIVE) {
            return;
        }
    }
}

/*
 * Rendering code uses GL calls exposed through the renderer DLL.  Prototype
 * harnesses must provide stubs for:
 *  - Com_Printf / Com_Error style logging wired through hooks.print/errorDrop
 *  - Demo playback routines (readDemoMessage)
 *  - Cvar manipulation for activeAction scripting
 */
