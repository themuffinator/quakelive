#include <stdbool.h>
#include <stdint.h>

#include "client_math.h"
#include "client_offsets.h"
#include "client_types.h"

/*
 * Annotated extraction of CL_Frame from src/code/client/cl_main.c and
 * quakelive_steam.exe::sub_4BC3E0.  The retail frame owner relies on the
 * global cls/cl/clc singletons plus VM, renderer, and sound entry points.  This
 * reconstruction keeps those dependencies as hooks so the sequencing can be
 * reviewed without pulling in the full engine.
 */

enum {
	QLR_UIMENU_NONE = 0,
	QLR_UIMENU_MAIN = 1,
	QLR_UIMENU_NEED_CD = 3,
};

/*
=============
qlr_cvar_integer

Returns a captured cvar integer with a null-safe fallback.
=============
*/
static int qlr_cvar_integer(const qlr_cvar_shadow_t *cvar) {
	return cvar ? cvar->integer : 0;
}

/*
=============
qlr_cvar_value

Returns a captured cvar value with a null-safe fallback.
=============
*/
static float qlr_cvar_value(const qlr_cvar_shadow_t *cvar, float fallback) {
	return cvar ? cvar->value : fallback;
}

/*
=============
qlr_set_cvar_integer

Updates a cvar mirror when CL_Frame consumes a latch.
=============
*/
static void qlr_set_cvar_integer(qlr_cvar_shadow_t *cvar, int value) {
	if (!cvar) {
		return;
	}

	cvar->integer = value;
	cvar->value = (float)value;
}

/*
=============
qlr_apply_avidemo_latch

Mirrors the retail deferred avidemo activation gate.
=============
*/
static void qlr_apply_avidemo_latch(qlr_client_frame_context_t *ctx) {
	int latch;
	int minTime;

	if (!ctx || !ctx->cl) {
		return;
	}

	latch = qlr_cvar_integer(ctx->cvars.cl_avidemo_latch);
	if (!latch) {
		return;
	}

	minTime = qlr_cvar_integer(ctx->cvars.cl_avidemo_mintime);
	if (!minTime || ctx->cl->timing.serverTime > minTime) {
		qlr_set_cvar_integer(ctx->cvars.cl_avidemo, latch);
		qlr_set_cvar_integer(ctx->cvars.cl_avidemo_latch, 0);
	}
}

/*
=============
qlr_lock_to_avidemo_rate

Mirrors the screenshot/maxtime/fixed-step avidemo branch.
=============
*/
static bool qlr_lock_to_avidemo_rate(qlr_client_frame_context_t *ctx, int *msec) {
	int avidemo;
	int minTime;
	int maxTime;
	int serverTime;
	int targetFrame;

	if (!ctx || !ctx->cls || !ctx->cl || !msec || *msec == 0) {
		return true;
	}

	avidemo = qlr_cvar_integer(ctx->cvars.cl_avidemo);
	if (!avidemo) {
		return true;
	}

	minTime = qlr_cvar_integer(ctx->cvars.cl_avidemo_mintime);
	maxTime = qlr_cvar_integer(ctx->cvars.cl_avidemo_maxtime);
	serverTime = ctx->cl->timing.serverTime;
	if (ctx->cls->state == QLR_CA_ACTIVE || qlr_cvar_integer(ctx->cvars.cl_forceavidemo)) {
		if (maxTime && serverTime > maxTime) {
			if (ctx->hooks.disconnect) {
				ctx->hooks.disconnect();
			}
			return false;
		}
		if (!minTime || serverTime >= minTime) {
			if (ctx->hooks.executeText) {
				ctx->hooks.executeText("screenshot silent\n");
			}
		}
	}

	targetFrame = (int)((1000 / avidemo) * qlr_cvar_value(ctx->cvars.com_timescale, 1.0f));
	if (targetFrame == 0) {
		targetFrame = 1;
	}

	*msec = targetFrame;
	return true;
}

/*
=============
qlr_run_release_marker_mutation

Mirrors the one-shot release-marker reliable command mutation in retail CL_Frame.
=============
*/
static void qlr_run_release_marker_mutation(qlr_client_frame_context_t *ctx) {
	float randomValue;

	if (!ctx || !ctx->cls || ctx->cls->framecount != 0 || !ctx->hooks.monkeyShouldBeSpanked) {
		return;
	}

	if (!ctx->hooks.monkeyShouldBeSpanked()) {
		return;
	}

	randomValue = ctx->hooks.randomFloat ? ctx->hooks.randomFloat() : 1.0f;
	if (randomValue >= 0.1f && ctx->hooks.changeReliableCommand) {
		ctx->hooks.changeReliableCommand();
	}
}

/*
=============
QLR_CL_Frame

Retail client-frame sequence with global engine work routed through hooks.
=============
*/
void QLR_CL_Frame(qlr_client_frame_context_t *ctx, int msec) {
	if (!ctx || !ctx->cls || !qlr_cvar_integer(ctx->cvars.com_cl_running)) {
		return;
	}

	if (ctx->cls->cddialog) {
		ctx->cls->cddialog = false;
		if (ctx->hooks.setActiveMenu) {
			ctx->hooks.setActiveMenu(QLR_UIMENU_NEED_CD);
		}
	} else if (ctx->cls->state == QLR_CA_DISCONNECTED && (ctx->cls->keyCatchers & 0x1) == 0 &&
	           ctx->cvars.com_sv_running && !ctx->cvars.com_sv_running->integer) {
		if (ctx->hooks.stopAllSounds) {
			ctx->hooks.stopAllSounds();
		}
		if (ctx->hooks.setActiveMenu) {
			ctx->hooks.setActiveMenu(QLR_UIMENU_MAIN);
		}
	}

	qlr_apply_avidemo_latch(ctx);
	if (!qlr_lock_to_avidemo_rate(ctx, &msec)) {
		return;
	}

	qlr_run_release_marker_mutation(ctx);

	ctx->cls->realFrametime = msec;

	if (ctx->clc && ctx->clc->demoplaying && qlr_cvar_integer(ctx->cvars.cl_freezeDemo)) {
		msec = 0;
	}

	ctx->cls->frametime = msec;
	ctx->cls->realtime += msec;

	if (qlr_cvar_integer(ctx->cvars.cl_timegraph) && ctx->hooks.debugGraph) {
		ctx->hooks.debugGraph(ctx->cls->realFrametime * 0.25f, 0);
	}

	if (ctx->hooks.checkUserinfo) {
		ctx->hooks.checkUserinfo();
	}
	if (ctx->hooks.checkTimeout) {
		ctx->hooks.checkTimeout(ctx->clc, ctx->cls, ctx->cl);
	}
	if (ctx->hooks.workshopFrame) {
		ctx->hooks.workshopFrame();
	}
	if (ctx->hooks.sendCmd) {
		ctx->hooks.sendCmd();
	}
	if (ctx->hooks.steamBrowserFrame) {
		ctx->hooks.steamBrowserFrame();
	}
	if (ctx->hooks.checkForResend) {
		ctx->hooks.checkForResend();
	}
	if (ctx->hooks.setCGameTime) {
		ctx->hooks.setCGameTime();
	}
	if (ctx->hooks.updateScreen) {
		ctx->hooks.updateScreen();
	}
	if (ctx->hooks.soundUpdate) {
		ctx->hooks.soundUpdate();
	}
	if (ctx->hooks.runCinematic) {
		ctx->hooks.runCinematic();
	}
	if (ctx->hooks.runConsole) {
		ctx->hooks.runConsole();
	}

	ctx->cls->framecount++;
}

/*
 * External dependencies summary for prototype scaffolding:
 *  - UI DLL via setActiveMenu (uivm -> UI_SET_ACTIVE_MENU)
 *  - Workshop/download completion helper adjacent to CL_Frame
 *  - Command send and connect resend helpers in cl_main.c
 *  - Cgame timing, screen, sound, cinematic, and console frame owners
 */
