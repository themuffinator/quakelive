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
qlr_client_cvar_integer

Return a captured cvar integer with null-safe fallback.
=============
*/
static int qlr_client_cvar_integer(const qlr_cvar_shadow_t *cvar) {
	return cvar ? cvar->integer : 0;
}

/*
=============
qlr_client_cvar_value

Return a captured cvar float with null-safe fallback.
=============
*/
static float qlr_client_cvar_value(const qlr_cvar_shadow_t *cvar, float fallback) {
	return cvar ? cvar->value : fallback;
}

/*
=============
qlr_client_set_cvar_integer

Update a captured cvar mirror when CL_Frame consumes a latch.
=============
*/
static void qlr_client_set_cvar_integer(qlr_cvar_shadow_t *cvar, int value) {
	if (!cvar) {
		return;
	}

	cvar->integer = value;
	cvar->value = (float)value;
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
qlr_client_apply_avidemo_latch

Apply the retained deferred AVI capture latch once demo time reaches mintime.
=============
*/
static void qlr_client_apply_avidemo_latch(qlr_client_frame_context_t *ctx) {
	int latch;
	int minTime;
	int serverTime;

	if (!ctx || !ctx->cl) {
		return;
	}

	latch = qlr_client_cvar_integer(ctx->cvars.cl_avidemo_latch);
	if (!latch) {
		return;
	}

	minTime = qlr_client_cvar_integer(ctx->cvars.cl_avidemo_mintime);
	serverTime = ctx->cl->timing.serverTime;
	if (!minTime || serverTime > minTime) {
		qlr_native_shim_logf("client", "CL_Frame", "avidemo latch=%d", latch);
		qlr_client_set_cvar_integer(ctx->cvars.cl_avidemo, latch);
		qlr_client_set_cvar_integer(ctx->cvars.cl_avidemo_latch, 0);
	}
}

/*
=============
qlr_client_lock_to_avidemo_rate

Clamp the frame time to the configured AVI demo rate while emitting screenshot logs.
=============
*/
static bool qlr_client_lock_to_avidemo_rate(qlr_client_frame_context_t *ctx, int *msec) {
	int avidemo;
	int minTime;
	int maxTime;
	int serverTime;
	int targetFrame;

	if (!ctx || !ctx->cl || !ctx->cls || !msec || *msec == 0) {
		return true;
	}

	avidemo = qlr_client_cvar_integer(ctx->cvars.cl_avidemo);
	if (!avidemo) {
		return true;
	}

	minTime = qlr_client_cvar_integer(ctx->cvars.cl_avidemo_mintime);
	maxTime = qlr_client_cvar_integer(ctx->cvars.cl_avidemo_maxtime);
	serverTime = ctx->cl->timing.serverTime;
	if (ctx->cls->state == QLR_CA_ACTIVE || qlr_client_cvar_integer(ctx->cvars.cl_forceavidemo)) {
		if (maxTime && serverTime > maxTime) {
			qlr_client_call_hook("disconnect", ctx->hooks.disconnect);
			return false;
		}
		if (!minTime || serverTime >= minTime) {
			qlr_native_shim_logf("client", "hook", "executeText(screenshot silent)");
			if (ctx->hooks.executeText) {
				ctx->hooks.executeText("screenshot silent\n");
			}
		}
	}

	targetFrame = (int)((1000 / avidemo) * qlr_client_cvar_value(ctx->cvars.com_timescale, 1.0f));
	if (targetFrame == 0) {
		targetFrame = 1;
	}
	*msec = targetFrame;
	return true;
}

/*
=============
qlr_client_run_release_marker_mutation

Mirror the retained first-frame release-marker reliable command mutation.
=============
*/
static void qlr_client_run_release_marker_mutation(qlr_client_frame_context_t *ctx) {
	float randomValue;
	int shouldMutate;

	if (!ctx || !ctx->cls || ctx->cls->framecount != 0 || !ctx->hooks.monkeyShouldBeSpanked) {
		return;
	}

	qlr_native_shim_logf("client", "hook", "monkeyShouldBeSpanked()");
	shouldMutate = ctx->hooks.monkeyShouldBeSpanked();
	if (!shouldMutate) {
		return;
	}

	randomValue = 1.0f;
	if (ctx->hooks.randomFloat) {
		randomValue = ctx->hooks.randomFloat();
		qlr_native_shim_logf("client", "hook", "randomFloat() -> %.2f", randomValue);
	}

	if (randomValue >= 0.1f) {
		qlr_client_call_hook("changeReliableCommand", ctx->hooks.changeReliableCommand);
	}
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

	if (!qlr_client_cvar_integer(ctx->cvars.com_cl_running)) {
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

	qlr_client_apply_avidemo_latch(ctx);
	if (!qlr_client_lock_to_avidemo_rate(ctx, &msec)) {
		return;
	}

	qlr_client_run_release_marker_mutation(ctx);

	ctx->cls->realFrametime = msec;

	if (ctx->clc && ctx->clc->demoplaying && qlr_client_cvar_integer(ctx->cvars.cl_freezeDemo)) {
		qlr_native_shim_logf("client", "CL_Frame", "freezeDemo -> frametime 0");
		msec = 0;
	}

	ctx->cls->frametime = msec;
	ctx->cls->realtime += msec;

	if (qlr_client_cvar_integer(ctx->cvars.cl_timegraph) && ctx->hooks.debugGraph) {
		qlr_native_shim_logf("client", "hook", "debugGraph(%.2f,0)", ctx->cls->realFrametime * 0.25f);
		ctx->hooks.debugGraph(ctx->cls->realFrametime * 0.25f, 0);
	}

	qlr_client_call_hook("checkUserinfo", ctx->hooks.checkUserinfo);
	qlr_client_call_timeout_hook(ctx->hooks.checkTimeout, ctx);
	qlr_client_call_hook("workshopFrame", ctx->hooks.workshopFrame);
	qlr_client_call_hook("sendCmd", ctx->hooks.sendCmd);
	qlr_client_call_hook("steamBrowserFrame", ctx->hooks.steamBrowserFrame);
	qlr_client_call_hook("checkForResend", ctx->hooks.checkForResend);
	qlr_client_call_hook("setCGameTime", ctx->hooks.setCGameTime);
	qlr_client_call_hook("updateScreen", ctx->hooks.updateScreen);
	qlr_client_call_hook("soundUpdate", ctx->hooks.soundUpdate);
	qlr_client_call_hook("runCinematic", ctx->hooks.runCinematic);
	qlr_client_call_hook("runConsole", ctx->hooks.runConsole);
	ctx->cls->framecount++;

	qlr_native_shim_logf("client", "CL_Frame", "end realtime=%d frametime=%d framecount=%d",
			 ctx->cls->realtime, ctx->cls->frametime, ctx->cls->framecount);
}
