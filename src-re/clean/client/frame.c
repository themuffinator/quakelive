#include "../include/qlr_client_frame.h"

static qlr_client_frame_context_t *qlr_client_frame_ctx = NULL;

/*
=============
qlr_client_cvar_true

Helper to test whether a captured cvar evaluates to true.
=============
*/
static bool qlr_client_cvar_true(const qlr_recon_cvar_t *cvar) {
	return cvar && cvar->integer != 0;
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
qlr_client_apply_avidemo_rate

Clamp the frame delta to the configured avidemo target.
=============
*/
static void qlr_client_apply_avidemo_rate(qlr_client_frame_context_t *ctx, int *msec) {
	if (!ctx || !ctx->cvars.cl_avidemo || !msec || *msec <= 0) {
		return;
	}

	if (!qlr_client_cvar_true(ctx->cvars.cl_avidemo)) {
		return;
	}

	float avidemo = (float)ctx->cvars.cl_avidemo->integer;
	if (avidemo <= 0.0f) {
		avidemo = 1.0f;
	}
	float timescale = 1.0f;
	if (ctx->cvars.com_timescale) {
		timescale = ctx->cvars.com_timescale->value;
		if (timescale <= 0.0f) {
			timescale = 1.0f;
		}
	}

	int target_frame = (int)(1000.0f / avidemo * timescale);
	if (target_frame <= 0) {
		target_frame = 1;
	}

	if (ctx->cvars.cl_forceavidemo && qlr_client_cvar_true(ctx->cvars.cl_forceavidemo)) {
		qlr_native_shim_logf("client", "CL_Frame", "forceavidemo target=%d", target_frame);
	}

	*msec = target_frame;
}

/*
=============
qlr_client_should_autopause

Check whether the clean harness should skip simulation while paused.
=============
*/
static bool qlr_client_should_autopause(const qlr_client_frame_context_t *ctx) {
	if (!ctx) {
		return false;
	}

	if (!qlr_client_cvar_true(ctx->cvars.cl_paused)) {
		return false;
	}

	if (!qlr_client_cvar_true(ctx->cvars.sv_paused)) {
		return false;
	}

	return qlr_client_cvar_true(ctx->cvars.com_sv_running);
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

	if (!qlr_client_cvar_true(ctx->cvars.com_cl_running)) {
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

	qlr_client_apply_avidemo_rate(ctx, &msec);

	if (ctx->cls) {
		ctx->cls->clock.previous = ctx->cls->clock.current;
		ctx->cls->clock.current += msec;
		ctx->cls->clock.delta = msec;
	}

	qlr_client_call_hook("check_userinfo", ctx->hooks.check_userinfo);
	qlr_client_call_timeout_hook(ctx);
	qlr_client_call_hook("read_packets", ctx->hooks.read_packets);

	if (qlr_client_should_autopause(ctx)) {
		qlr_native_shim_logf("client", "CL_Frame", "auto-paused");
	} else {
		qlr_client_call_hook("run_console", ctx->hooks.run_console);
		qlr_client_call_hook("predict_movement", ctx->hooks.predict_movement);
		qlr_client_call_hook("send_cmd", ctx->hooks.send_cmd);
		qlr_client_call_hook("check_for_resend", ctx->hooks.check_for_resend);
	}

	qlr_client_call_hook("set_cgame_time", ctx->hooks.set_cgame_time);
	qlr_client_call_hook("update_screen", ctx->hooks.update_screen);
	qlr_client_call_hook("sound_update", ctx->hooks.sound_update);
	qlr_client_call_hook("begin_profiling", ctx->hooks.begin_profiling);

	qlr_native_shim_logf("client", "CL_Frame", "end realtime=%d delta=%d",
				 ctx->cls ? ctx->cls->clock.current : -1,
				 ctx->cls ? ctx->cls->clock.delta : -1);
}
