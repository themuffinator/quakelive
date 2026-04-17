#include "../include/qlr_game_pmove.h"

static qlr_game_pmove_context_t *qlr_game_pmove_ctx = NULL;

/*
=============
QLR_Game_BindPmoveContext

Binds the pmove shim context so gameplay helpers can dispatch into the
reverse-engineered Quake Live runtime.
=============
*/
void QLR_Game_BindPmoveContext(qlr_game_pmove_context_t *ctx) {
	qlr_game_pmove_ctx = ctx;
	qlr_native_shim_logf(
	"game",
	"BindPmoveContext",
	"ctx=%p pm=%p locals=%p",
	(void *)ctx,
	ctx ? (void *)ctx->pm : NULL,
	ctx ? (void *)ctx->locals : NULL);
}

/*
=============
QLR_Game_UnbindPmoveContext

Clears the active pmove shim context and releases any bound state pointers.
=============
*/
void QLR_Game_UnbindPmoveContext(void) {
	qlr_native_shim_logf(
	"game",
	"UnbindPmoveContext",
	"ctx=%p",
	(void *)qlr_game_pmove_ctx);
	qlr_game_pmove_ctx = NULL;
}

/*
=============
PM_AddEvent

Bridges predictable event queueing to the backing Quake Live hook.
=============
*/
void PM_AddEvent(int new_event) {
	qlr_game_pmove_context_t *ctx = qlr_game_pmove_ctx;
	if (!ctx || !ctx->hooks.add_event) {
		qlr_native_shim_logf(
		"game",
		"PM_AddEvent",
		"missing-hook ctx=%p event=%d",
		(void *)ctx,
		new_event);
		return;
	}

	ctx->hooks.add_event(ctx, new_event);
}

/*
=============
PM_AddTouchEnt

Forwards touch list bookkeeping to the Quake Live movement import layer.
=============
*/
void PM_AddTouchEnt(int entity_num) {
	qlr_game_pmove_context_t *ctx = qlr_game_pmove_ctx;
	if (!ctx || !ctx->hooks.add_touch_entity) {
		qlr_native_shim_logf(
		"game",
		"PM_AddTouchEnt",
		"missing-hook ctx=%p ent=%d",
		(void *)ctx,
		entity_num);
		return;
	}

	ctx->hooks.add_touch_entity(ctx, entity_num);
}

/*
=============
PM_AirMove

Delegates air-movement integration to the bound Quake Live implementation.
=============
*/
void PM_AirMove(void) {
	qlr_game_pmove_context_t *ctx = qlr_game_pmove_ctx;
	if (!ctx || !ctx->hooks.air_move) {
		qlr_native_shim_logf(
		"game",
		"PM_AirMove",
		"missing-hook ctx=%p",
		(void *)ctx);
		return;
	}

	ctx->hooks.air_move(ctx);
}

/*
=============
PM_WaterMove

Delegates aquatic movement to the Quake Live pmove hook.
=============
*/
void PM_WaterMove(void) {
	qlr_game_pmove_context_t *ctx = qlr_game_pmove_ctx;
	if (!ctx || !ctx->hooks.water_move) {
		qlr_native_shim_logf(
		"game",
		"PM_WaterMove",
		"missing-hook ctx=%p",
		(void *)ctx);
		return;
	}

	ctx->hooks.water_move(ctx);
}

/*
=============
PM_WalkMove

Passes on grounded movement handling to the Quake Live pmove hook.
=============
*/
void PM_WalkMove(void) {
	qlr_game_pmove_context_t *ctx = qlr_game_pmove_ctx;
	if (!ctx || !ctx->hooks.walk_move) {
		qlr_native_shim_logf(
		"game",
		"PM_WalkMove",
		"missing-hook ctx=%p",
		(void *)ctx);
		return;
	}

	ctx->hooks.walk_move(ctx);
}

/*
=============
PM_CheckJump

Queries the Quake Live pmove hook to decide if a jump should trigger, while
preserving the retail air-double-jump gate used by PM_AirMove versus
PM_WalkMove.
=============
*/
bool PM_CheckJump(bool allowAirDoubleJump) {
	qlr_game_pmove_context_t *ctx = qlr_game_pmove_ctx;
	if (!ctx || !ctx->hooks.check_jump) {
		qlr_native_shim_logf(
		"game",
		"PM_CheckJump",
		"missing-hook ctx=%p allowAirDoubleJump=%d",
		(void *)ctx,
		allowAirDoubleJump ? 1 : 0);
		return false;
	}

	return ctx->hooks.check_jump(ctx, allowAirDoubleJump);
}

/*
=============
PM_Weapon

Routes weapon timer updates through the Quake Live backing implementation.
=============
*/
void PM_Weapon(void) {
	qlr_game_pmove_context_t *ctx = qlr_game_pmove_ctx;
	if (!ctx || !ctx->hooks.weapon) {
		qlr_native_shim_logf(
		"game",
		"PM_Weapon",
		"missing-hook ctx=%p",
		(void *)ctx);
		return;
	}

	ctx->hooks.weapon(ctx);
}

/*
=============
Pmove

Entry point that binds the working pmove pointer before dispatching to the
reverse-engineered Quake Live routine.
=============
*/
void Pmove(qlr_pmove_t *pmove) {
	qlr_game_pmove_context_t *ctx = qlr_game_pmove_ctx;
	if (!ctx) {
		qlr_native_shim_logf(
		"game",
		"Pmove",
		"no-context pm=%p",
		(void *)pmove);
		return;
	}

	ctx->pm = pmove ? pmove : ctx->pm;
	if (!ctx->hooks.process_move) {
		qlr_native_shim_logf(
		"game",
		"Pmove",
		"missing-hook ctx=%p pm=%p",
		(void *)ctx,
		(void *)pmove);
		return;
	}

	ctx->hooks.process_move(ctx, pmove);
}
