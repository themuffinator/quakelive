#include "../include/qlr_client_frame.h"

static qlr_client_frame_context_t *qlr_client_frame_ctx = NULL;

static void qlr_client_call_hook(const char *name, void (*fn)(void));

/*
=============
qlr_client_cvar_integer

Helper to test a captured cvar integer value.
=============
*/
static int qlr_client_cvar_integer(const qlr_recon_cvar_t *cvar) {
	return cvar ? cvar->integer : 0;
}

/*
=============
qlr_client_cvar_value

Helper to read a captured cvar float value.
=============
*/
static float qlr_client_cvar_value(const qlr_recon_cvar_t *cvar, float fallback) {
	return cvar ? cvar->value : fallback;
}

/*
=============
qlr_client_set_cvar_integer

Update a cvar mirror after CL_Frame consumes a latch.
=============
*/
static void qlr_client_set_cvar_integer(qlr_recon_cvar_t *cvar, int value) {
	if (!cvar) {
		return;
	}

	cvar->integer = value;
	cvar->value = (float)value;
}

/*
=============
QLR_ClientFrame_BindContext

Bind the frame context used by the clean harness shim.
=============
*/
void QLR_ClientFrame_BindContext(qlr_client_frame_context_t *ctx) {
	qlr_client_frame_ctx = ctx;
	qlr_native_shim_logf("client", "BindContext", "ctx=%p", (void *)ctx);
}

/*
=============
QLR_ClientFrame_UnbindContext

Clear the bound harness context pointer.
=============
*/
void QLR_ClientFrame_UnbindContext(void) {
	qlr_native_shim_logf("client", "UnbindContext", "ctx=%p", (void *)qlr_client_frame_ctx);
	qlr_client_frame_ctx = NULL;
}

/*
=============
qlr_client_apply_avidemo_latch

Apply the retained deferred AVI capture latch.
=============
*/
static void qlr_client_apply_avidemo_latch(qlr_client_frame_context_t *ctx) {
	int latch;
	int min_time;

	if (!ctx || !ctx->cl) {
		return;
	}

	latch = qlr_client_cvar_integer(ctx->cvars.cl_avidemo_latch);
	if (!latch) {
		return;
	}

	min_time = qlr_client_cvar_integer(ctx->cvars.cl_avidemo_mintime);
	if (!min_time || ctx->cl->server_time > min_time) {
		qlr_native_shim_logf("client", "CL_Frame", "avidemo latch=%d", latch);
		qlr_client_set_cvar_integer(ctx->cvars.cl_avidemo, latch);
		qlr_client_set_cvar_integer(ctx->cvars.cl_avidemo_latch, 0);
	}
}

/*
=============
qlr_client_apply_avidemo_rate

Clamp the frame delta to the configured avidemo target.
=============
*/
static bool qlr_client_apply_avidemo_rate(qlr_client_frame_context_t *ctx, int *msec) {
	int avidemo;
	int min_time;
	int max_time;
	int target_frame;

	if (!ctx || !ctx->cls || !ctx->cl || !msec || *msec == 0) {
		return true;
	}

	avidemo = qlr_client_cvar_integer(ctx->cvars.cl_avidemo);
	if (!avidemo) {
		return true;
	}

	min_time = qlr_client_cvar_integer(ctx->cvars.cl_avidemo_mintime);
	max_time = qlr_client_cvar_integer(ctx->cvars.cl_avidemo_maxtime);
	if (ctx->cls->state == QLR_CLIENT_STATE_ACTIVE || qlr_client_cvar_integer(ctx->cvars.cl_forceavidemo)) {
		if (max_time && ctx->cl->server_time > max_time) {
			qlr_client_call_hook("disconnect", ctx->hooks.disconnect);
			return false;
		}
		if (!min_time || ctx->cl->server_time >= min_time) {
			qlr_native_shim_logf("client", "hook", "execute_text(screenshot silent)");
			if (ctx->hooks.execute_text) {
				ctx->hooks.execute_text("screenshot silent\n");
			}
		}
	}

	target_frame = (int)((1000 / avidemo) * qlr_client_cvar_value(ctx->cvars.com_timescale, 1.0f));
	if (target_frame <= 0) {
		target_frame = 1;
	}

	*msec = target_frame;
	return true;
}

/*
=============
qlr_client_run_release_marker_mutation

Mirror the first-frame release-marker reliable command mutation.
=============
*/
static void qlr_client_run_release_marker_mutation(qlr_client_frame_context_t *ctx) {
	float random_value;
	int should_mutate;

	if (!ctx || !ctx->cls || ctx->cls->frame_count != 0 || !ctx->hooks.monkey_should_be_spanked) {
		return;
	}

	qlr_native_shim_logf("client", "hook", "monkey_should_be_spanked()");
	should_mutate = ctx->hooks.monkey_should_be_spanked();
	if (!should_mutate) {
		return;
	}

	random_value = 1.0f;
	if (ctx->hooks.random_float) {
		random_value = ctx->hooks.random_float();
		qlr_native_shim_logf("client", "hook", "random_float() -> %.2f", random_value);
	}

	if (random_value >= 0.1f) {
		qlr_client_call_hook("change_reliable_command", ctx->hooks.change_reliable_command);
	}
}

/*
=============
qlr_client_call_hook

Log and invoke a parameterless clean shim hook.
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
qlr_client_call_menu_hook

Log and invoke a menu hook in the clean shim.
=============
*/
static void qlr_client_call_menu_hook(void (*fn)(int), int menu_id) {
	if (!fn) {
		return;
	}

	qlr_native_shim_logf("client", "hook", "set_active_menu(%d)", menu_id);
	fn(menu_id);
}

/*
=============
qlr_client_call_timeout_hook

Log and invoke the timeout hook with captured state.
=============
*/
static void qlr_client_call_timeout_hook(qlr_client_frame_context_t *ctx) {
	if (!ctx || !ctx->hooks.check_timeout) {
		return;
	}

	qlr_native_shim_logf("client", "hook", "check_timeout(timeout=%d server=%d)",
				 ctx->cl ? ctx->cl->timeout_count : -1,
				 ctx->cl ? ctx->cl->server_time : -1);
	ctx->hooks.check_timeout(ctx->clc, ctx->cls, ctx->cl);
}

/*
=============
CL_Frame

Frame driver mirrored for the clean harness.
=============
*/
void CL_Frame(int msec) {
	qlr_client_frame_context_t *ctx = qlr_client_frame_ctx;
	if (!ctx || !ctx->cls || !ctx->cvars.com_cl_running) {
		qlr_native_shim_logf("client", "CL_Frame", "unbound msec=%d", msec);
		return;
	}

	if (!qlr_client_cvar_integer(ctx->cvars.com_cl_running)) {
		qlr_native_shim_logf("client", "CL_Frame", "com_cl_running disabled");
		return;
	}

	enum {
		QLR_MENU_MAIN = 1,
		QLR_MENU_NEED_CD = 3
	};

	qlr_native_shim_logf("client", "CL_Frame", "start msec=%d state=%d catchers=0x%X",
			 msec,
			 ctx->cls->state,
			 ctx->cls->key_catchers);

	if (ctx->cls->cd_dialog) {
		ctx->cls->cd_dialog = false;
		qlr_client_call_menu_hook(ctx->hooks.set_active_menu, QLR_MENU_NEED_CD);
	} else if (ctx->cls->state == QLR_CLIENT_STATE_DISCONNECTED &&
		   (ctx->cls->key_catchers & 0x1) == 0 &&
		   ctx->cvars.com_sv_running && !ctx->cvars.com_sv_running->integer) {
		qlr_client_call_hook("stop_all_sounds", ctx->hooks.stop_all_sounds);
		qlr_client_call_menu_hook(ctx->hooks.set_active_menu, QLR_MENU_MAIN);
	}

	qlr_client_apply_avidemo_latch(ctx);
	if (!qlr_client_apply_avidemo_rate(ctx, &msec)) {
		return;
	}

	qlr_client_run_release_marker_mutation(ctx);

	ctx->cls->real_frametime = msec;
	if (ctx->clc && ctx->clc->demo_playing && qlr_client_cvar_integer(ctx->cvars.cl_freezeDemo)) {
		qlr_native_shim_logf("client", "CL_Frame", "freezeDemo -> frame delta 0");
		msec = 0;
	}

	ctx->cls->clock.previous = ctx->cls->clock.current;
	ctx->cls->clock.current += msec;
	ctx->cls->clock.delta = msec;

	if (qlr_client_cvar_integer(ctx->cvars.cl_timegraph) && ctx->hooks.debug_graph) {
		qlr_native_shim_logf("client", "hook", "debug_graph(%.2f,0)", ctx->cls->real_frametime * 0.25f);
		ctx->hooks.debug_graph(ctx->cls->real_frametime * 0.25f, 0);
	}

	qlr_client_call_hook("check_userinfo", ctx->hooks.check_userinfo);
	qlr_client_call_timeout_hook(ctx);
	qlr_client_call_hook("workshop_frame", ctx->hooks.workshop_frame);
	qlr_client_call_hook("send_cmd", ctx->hooks.send_cmd);
	qlr_client_call_hook("steam_browser_frame", ctx->hooks.steam_browser_frame);
	qlr_client_call_hook("check_for_resend", ctx->hooks.check_for_resend);
	qlr_client_call_hook("set_cgame_time", ctx->hooks.set_cgame_time);
	qlr_client_call_hook("update_screen", ctx->hooks.update_screen);
	qlr_client_call_hook("sound_update", ctx->hooks.sound_update);
	qlr_client_call_hook("run_cinematic", ctx->hooks.run_cinematic);
	qlr_client_call_hook("run_console", ctx->hooks.run_console);
	ctx->cls->frame_count++;

	qlr_native_shim_logf("client", "CL_Frame", "end realtime=%d delta=%d framecount=%d",
			 ctx->cls->clock.current,
			 ctx->cls->clock.delta,
			 ctx->cls->frame_count);
}
