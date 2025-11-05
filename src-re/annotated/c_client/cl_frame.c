#include <stdbool.h>
#include <stdint.h>

#include "client_math.h"
#include "client_offsets.h"
#include "client_types.h"

/*
 * Annotated extraction of CL_Frame from src/code/client/cl_main.c.
 * The real engine relies on the global cls/cl/clc singletons, VM entry points,
 * and renderer/sound DLL exports.  We fold the call graph that touches timing
 * and snapshot management into a compact structure so the sequencing can be
 * reasoned about without pulling in the original headers.
 */

typedef struct {
    void (*stopAllSounds)(void);                       /* S_StopAllSounds */
    void (*setActiveMenu)(int menuId);                 /* VM_Call(uivm, UI_SET_ACTIVE_MENU, ...) */
    void (*writeDemoMessage)(void *msg, int header);   /* CL_WriteDemoMessage */
    void (*checkTimeout)(qlr_client_connection_shadow_t *clc,
                         qlr_client_static_shadow_t *cls,
                         qlr_client_active_shadow_t *cl);
    void (*checkUserinfo)(void);
    void (*readPackets)(void);
    void (*sendCmd)(void);
    void (*predictMovement)(void);
    void (*runConsole)(void);
    void (*updateScreen)(void);
    void (*setCGameTime)(void);
    void (*firstSnapshot)(void);
    void (*beginProfiling)(void);
} qlr_client_frame_hooks_t;

typedef struct {
    qlr_client_static_shadow_t *cls;
    qlr_client_active_shadow_t *cl;
    qlr_client_connection_shadow_t *clc;
    qlr_client_frame_cvars_t cvars;
    qlr_client_frame_hooks_t hooks;
} qlr_client_frame_context_t;

/*
 * UI enumerants used by the frame bootstrap.  Keeping the values inline makes
 * it obvious to downstream prototype code which stubs need to match the real
 * menu IDs exposed by ui_public.h.
 */
enum {
    QLR_UIMENU_NONE = 0,
    QLR_UIMENU_MAIN = 1,
    QLR_UIMENU_NEED_CD = 3,
};

static void qlr_lock_to_avidemo_rate(qlr_client_frame_context_t *ctx, int *msec) {
    if (!ctx->cvars.cl_avidemo->integer || *msec == 0) {
        return;
    }

    if (ctx->cls->state == QLR_CA_ACTIVE || ctx->cvars.cl_forceavidemo->integer) {
        /* The original takes a silent screenshot each frame to build the AVI. */
        /* Cbuf_ExecuteText(EXEC_NOW, "screenshot silent\n"); */
    }

    int targetFrame = (int)(1000.0f / ctx->cvars.cl_avidemo->integer * ctx->cvars.com_timescale->value);
    if (targetFrame <= 0) {
        targetFrame = 1;
    }
    *msec = targetFrame;
}

static bool qlr_should_autopause(const qlr_client_frame_context_t *ctx) {
    return ctx->cvars.cl_paused->integer && ctx->cvars.sv_paused->integer && ctx->cvars.com_sv_running->integer;
}

void QLR_CL_Frame(qlr_client_frame_context_t *ctx, int msec) {
    if (!ctx->cvars.com_cl_running->integer) {
        return;
    }

    if (ctx->cls->cddialog) {
        ctx->cls->cddialog = false;
        if (ctx->hooks.setActiveMenu) {
            ctx->hooks.setActiveMenu(QLR_UIMENU_NEED_CD);
        }
    } else if (ctx->cls->state == QLR_CA_DISCONNECTED && (ctx->cls->keyCatchers & 0x1) == 0 &&
               !ctx->cvars.com_sv_running->integer) {
        if (ctx->hooks.stopAllSounds) {
            ctx->hooks.stopAllSounds();
        }
        if (ctx->hooks.setActiveMenu) {
            ctx->hooks.setActiveMenu(QLR_UIMENU_MAIN);
        }
    }

    qlr_lock_to_avidemo_rate(ctx, &msec);

    ctx->cls->realFrametime = msec;
    ctx->cls->frametime = msec;
    ctx->cls->realtime += msec;

    if (ctx->hooks.checkTimeout) {
        ctx->hooks.checkTimeout(ctx->clc, ctx->cls, ctx->cl);
    }

    if (ctx->hooks.checkUserinfo) {
        ctx->hooks.checkUserinfo();
    }

    if (ctx->hooks.readPackets) {
        ctx->hooks.readPackets();
    }

    if (ctx->hooks.setCGameTime) {
        ctx->hooks.setCGameTime();
    }

    if (qlr_should_autopause(ctx)) {
        goto finalize_frame;
    }

    if (ctx->hooks.runConsole) {
        ctx->hooks.runConsole();
    }

    if (ctx->hooks.predictMovement) {
        ctx->hooks.predictMovement();
    }

    if (ctx->hooks.sendCmd) {
        ctx->hooks.sendCmd();
    }

finalize_frame:
    if (ctx->hooks.updateScreen) {
        ctx->hooks.updateScreen();
    }

    if (ctx->hooks.beginProfiling) {
        ctx->hooks.beginProfiling();
    }
}

/*
 * External dependencies summary for prototype scaffolding:
 *  - UI DLL via setActiveMenu (maps to uivm->UI_SET_ACTIVE_MENU)
 *  - Renderer DLL for screenshot capture inside the AVI path
 *  - OpenGL entry points exposed through the renderer (DrawStretchPic, etc.)
 *  - Sound system DLL for S_StopAllSounds
 *  - Demo writer hooks (CL_WriteDemoMessage) if demorecording is enabled
 */
