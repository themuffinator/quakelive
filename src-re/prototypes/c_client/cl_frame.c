#include "frame.h"

#include <stddef.h>

static qlr_client_frame_context_t *qlr_client_frame_ctx = NULL;

enum {
	QLR_UIMENU_NONE = 0,
	QLR_UIMENU_MAIN = 1,
	QLR_UIMENU_NEED_CD = 3,
};

/*
=============
QLR_ClientFrame_BindContext

Bind the frame context so the shim can forward into the harness hooks.
=============
*/
void QLR_ClientFrame_BindContext(qlr_client_frame_context_t *ctx) {
	qlr_client_frame_ctx = ctx;
	if (ctx && ctx->cls) {
		qlr_native_shim_logf("client", "BindContext", "ctx=%p state=%d", (void *)ctx, ctx->cls->state);
	} else {
		qlr_native_shim_logf("client", "BindContext", "ctx=%p", (void *)ctx);
	}
}

/*
=============
QLR_ClientFrame_UnbindContext

Clear the bound frame context.
=============
*/
void QLR_ClientFrame_UnbindContext(void) {
	qlr_native_shim_logf("client", "UnbindContext", "ctx=%p", (void *)qlr_client_frame_ctx);
	qlr_client_frame_ctx = NULL;
}

/*
=============
qlr_lock_to_avidemo_rate

Clamp the frame time to the configured AVI demo rate while emitting screenshot logs.
=============
*/
static void qlr_lock_to_avidemo_rate(qlr_client_frame_context_t *ctx, int *msec) {
	if (!ctx || !ctx->cvars.cl_avidemo || ctx->cvars.cl_avidemo->integer == 0 || !msec || *msec == 0) {
		return;
	}

	if ((ctx->cls && ctx->cls->state == QLR_CA_ACTIVE) ||
	    (ctx->cvars.cl_forceavidemo && ctx->cvars.cl_forceavidemo->integer)) {
		qlr_native_shim_logf("client", "CL_Frame", "avidemo-screenshot");
	}

	if (!ctx->cvars.com_timescale) {
		return;
	}

	float avidemo = (float)ctx->cvars.cl_avidemo->integer;
	float timescale = ctx->cvars.com_timescale->value;
	int targetFrame = (int)(1000.0f / (avidemo > 0.0f ? avidemo : 1.0f) * timescale);
	if (targetFrame <= 0) {
		targetFrame = 1;
	}
	*msec = targetFrame;
}

/*
=============
qlr_should_autopause

Check whether the capture harness should skip send/predict while paused.
=============
*/
static bool qlr_should_autopause(const qlr_client_frame_context_t *ctx) {
	if (!ctx) {
		return false;
	}
	return ctx->cvars.cl_paused && ctx->cvars.sv_paused && ctx->cvars.com_sv_running &&
	       ctx->cvars.cl_paused->integer && ctx->cvars.sv_paused->integer && ctx->cvars.com_sv_running->integer;
}

/*
=============
qlr_client_call_hook

Log and invoke a parameterless hook.
=============
*/
static void qlr_client_call_hook(const char *name, void (*fn)(void)) {
	if (!fn) {
		return;
	}
	qlr_native_shim_logf("client", "hook", "%s()", name);
	fn();
}

/*
=============
qlr_client_call_timeout_hook

Log and invoke the timeout hook with the current client snapshots.
=============
*/
static void qlr_client_call_timeout_hook(void (*fn)(qlr_client_connection_shadow_t *,
					    qlr_client_static_shadow_t *,
					    qlr_client_active_shadow_t *),
				 qlr_client_frame_context_t *ctx) {
	if (!fn) {
		return;
	}
	qlr_native_shim_logf("client", "hook", "checkTimeout(timeoutcount=%d serverTime=%d)",
				 ctx->cl ? ctx->cl->timeoutcount : -1,
				 ctx->cl ? ctx->cl->timing.serverTime : -1);
	fn(ctx->clc, ctx->cls, ctx->cl);
}

/*
=============
qlr_client_call_menu_hook

Log and invoke the UI menu hook with the requested menu identifier.
=============
*/
static void qlr_client_call_menu_hook(void (*fn)(int), int menuId) {
	if (!fn) {
		return;
	}
	qlr_native_shim_logf("client", "hook", "setActiveMenu(%d)", menuId);
	fn(menuId);
}

/*
=============
CL_Frame

Top-level frame driver wired into the prototype harness.
=============
*/
void CL_Frame(int msec) {
	qlr_client_frame_context_t *ctx = qlr_client_frame_ctx;
	if (!ctx || !ctx->cls || !ctx->cvars.com_cl_running) {
		qlr_native_shim_logf("client", "CL_Frame", "unbound msec=%d", msec);
		return;
	}

	if (!ctx->cvars.com_cl_running->integer) {
		qlr_native_shim_logf("client", "CL_Frame", "com_cl_running=0 -> early exit");
		return;
	}

	qlr_native_shim_logf("client", "CL_Frame", "start msec=%d state=%d catchers=0x%X", msec, ctx->cls->state, ctx->cls->keyCatchers);

	if (ctx->cls->cddialog) {
		ctx->cls->cddialog = false;
		qlr_native_shim_logf("client", "CL_Frame", "clearing-cddialog");
		qlr_client_call_menu_hook(ctx->hooks.setActiveMenu, QLR_UIMENU_NEED_CD);
	} else if (ctx->cls->state == QLR_CA_DISCONNECTED && (ctx->cls->keyCatchers & 0x1) == 0 &&
	           ctx->cvars.com_sv_running && !ctx->cvars.com_sv_running->integer) {
		qlr_client_call_hook("stopAllSounds", ctx->hooks.stopAllSounds);
		qlr_client_call_menu_hook(ctx->hooks.setActiveMenu, QLR_UIMENU_MAIN);
	}

	qlr_lock_to_avidemo_rate(ctx, &msec);

	ctx->cls->realFrametime = msec;
	ctx->cls->frametime = msec;
	ctx->cls->realtime += msec;

	bool autopause = qlr_should_autopause(ctx);

	qlr_client_call_hook("checkUserinfo", ctx->hooks.checkUserinfo);
	qlr_client_call_timeout_hook(ctx->hooks.checkTimeout, ctx);
	qlr_client_call_hook("readPackets", ctx->hooks.readPackets);

	if (autopause) {
		qlr_native_shim_logf("client", "CL_Frame", "auto-paused");
	} else {
		qlr_client_call_hook("predictMovement", ctx->hooks.predictMovement);
		qlr_client_call_hook("sendCmd", ctx->hooks.sendCmd);
		qlr_client_call_hook("checkForResend", ctx->hooks.checkForResend);
	}

	qlr_client_call_hook("setCGameTime", ctx->hooks.setCGameTime);
	qlr_client_call_hook("updateScreen", ctx->hooks.updateScreen);
	qlr_client_call_hook("runCinematic", ctx->hooks.runCinematic);
	if (!autopause) {
		qlr_client_call_hook("runConsole", ctx->hooks.runConsole);
	}
	qlr_client_call_hook("beginProfiling", ctx->hooks.beginProfiling);

	qlr_native_shim_logf("client", "CL_Frame", "end realtime=%d frametime=%d", ctx->cls->realtime, ctx->cls->frametime);
}
