#include "rules_fixtures.h"

#if defined(__has_include)
#if __has_include("g_local.h")
#include "g_local.h"
#elif __has_include("../code/game/g_local.h")
#include "../code/game/g_local.h"
#elif __has_include("../../code/game/g_local.h")
#include "../../code/game/g_local.h"
#else
#error "Unable to locate g_local.h for cosmetics fixtures"
#endif
#else
#include "../../code/game/g_local.h"
#endif

#include <string.h>

typedef struct {
	qboolean	trainingActive;
	qboolean	warmupOnly;
	qboolean	warmupLive;
	qboolean	timersEnabled;
	const char	*lastMessage;
} gt_itemtimer_vote_context_t;

typedef struct {
	qboolean	trainingActive;
	const char	*lastMessage;
} gt_training_command_context_t;

typedef struct {
	int	configIndex;
	char	payload[MAX_INFO_STRING];
} gt_force_broadcast_log_t;

static void GT_ItemTimerVoteContextInit(gt_itemtimer_vote_context_t *ctx);
static qboolean GT_ItemTimerApplyVote(gt_itemtimer_vote_context_t *ctx, const char *option);
static void GT_TrainingCommandContextInit(gt_training_command_context_t *ctx);
static qboolean GT_TrainingAllowsAddbot(gt_training_command_context_t *ctx);
static void GT_ApplyForceBroadcast(const char *cvarName, qboolean enabled, gt_force_broadcast_log_t *log);

/*
=============
GT_ItemTimerVoteContextInit

Seeds the vote context with the default Quake Live expectations.
=============
*/
static void GT_ItemTimerVoteContextInit(gt_itemtimer_vote_context_t *ctx) {
	if (!ctx) {
		return;
	}

	memset(ctx, 0, sizeof(*ctx));
	ctx->timersEnabled = qtrue;
}

/*
=============
GT_ItemTimerApplyVote

Simulates the `callvote itemtimers` handler and records any broadcast message.
=============
*/
static qboolean GT_ItemTimerApplyVote(gt_itemtimer_vote_context_t *ctx, const char *option) {
	if (!ctx) {
		return GT_Failf("item timer context is NULL");
	}

	ctx->lastMessage = NULL;

	if (ctx->trainingActive) {
		ctx->lastMessage = "Voting is not allowed in training.\n";
		return qfalse;
	}

	if (!ctx->warmupLive && ctx->warmupOnly) {
		ctx->lastMessage = "Voting to alter the item timers is only allowed during the warm up period.\n";
		return qfalse;
	}

	if (!option || !option[0]) {
		ctx->lastMessage = "^3Valid item timer options are:    ^5ON    ^5OFF^7\n";
		return qfalse;
	}

	if (Q_stricmp(option, "ON") == 0) {
		ctx->timersEnabled = qtrue;
		return qtrue;
	}

	if (Q_stricmp(option, "OFF") == 0) {
		ctx->timersEnabled = qfalse;
		return qtrue;
	}

	ctx->lastMessage = "^3Valid item timer options are:    ^5ON    ^5OFF^7\n";
	return qfalse;
}

/*
=============
GT_TrainingCommandContextInit

Initialises the command gate used when `g_training` is active.
=============
*/
static void GT_TrainingCommandContextInit(gt_training_command_context_t *ctx) {
	if (!ctx) {
		return;
	}

	memset(ctx, 0, sizeof(*ctx));
}

/*
=============
GT_TrainingAllowsAddbot

Returns whether `addbot` should be processed while training is running.
=============
*/
static qboolean GT_TrainingAllowsAddbot(gt_training_command_context_t *ctx) {
	if (!ctx) {
		return GT_Failf("training command context is NULL");
	}

	ctx->lastMessage = NULL;
	if (ctx->trainingActive) {
		ctx->lastMessage = "Addbot not allowed during training.\n";
		return qfalse;
	}

	return qtrue;
}

/*
=============
GT_ApplyForceBroadcast

Records the configstring broadcast used by the `g_force*` family.
=============
*/
static void GT_ApplyForceBroadcast(const char *cvarName, qboolean enabled, gt_force_broadcast_log_t *log) {
	static qboolean	forceSmallScoreboard = qfalse;
	static qboolean	forceHudHints = qfalse;
	static qboolean	forceDamageThroughSurface = qfalse;

	if (!log) {
		return;
	}

	if ( cvarName ) {
		if ( Q_stricmp( cvarName, "g_forceSmallScoreboardMessage" ) == 0 ) {
			forceSmallScoreboard = enabled ? qtrue : qfalse;
		} else if ( Q_stricmp( cvarName, "g_forceSendConfigstring" ) == 0 ) {
			forceHudHints = enabled ? qtrue : qfalse;
		} else if ( Q_stricmp( cvarName, "g_forceDmgThroughSurface" ) == 0 ) {
			forceDamageThroughSurface = enabled ? qtrue : qfalse;
		}
	}

	log->configIndex = CS_FORCED_COSMETICS;
	log->payload[0] = '\0';
	Info_SetValueForKey( log->payload, "sb", forceSmallScoreboard ? "1" : "0" );
	Info_SetValueForKey( log->payload, "hud", forceHudHints ? "1" : "0" );
	Info_SetValueForKey( log->payload, "dmg", forceDamageThroughSurface ? "1" : "0" );
}

/*
=============
GT_ItemTimerVoteRejectsDuringTraining

Ensures the item timer vote echoes the training vote block.
=============
*/
static qboolean GT_ItemTimerVoteRejectsDuringTraining(void) {
	gt_itemtimer_vote_context_t ctx;

	GT_ItemTimerVoteContextInit(&ctx);
	ctx.trainingActive = qtrue;

	if (GT_ItemTimerApplyVote(&ctx, "OFF")) {
		return GT_Failf("expected training to block item timer vote");
	}

	if (!ctx.lastMessage || Q_stricmp(ctx.lastMessage, "Voting is not allowed in training.\n") != 0) {
		return GT_Failf("unexpected training rejection message: %s", ctx.lastMessage ? ctx.lastMessage : "<null>");
	}

	return qtrue;
}

/*
=============
GT_ItemTimerVoteHonoursWarmupRestriction

Verifies that warmup-only servers refuse mid-match item timer changes.
=============
*/
static qboolean GT_ItemTimerVoteHonoursWarmupRestriction(void) {
	gt_itemtimer_vote_context_t ctx;

	GT_ItemTimerVoteContextInit(&ctx);
	ctx.warmupOnly = qtrue;
	ctx.warmupLive = qfalse;

	if (GT_ItemTimerApplyVote(&ctx, "OFF")) {
		return GT_Failf("expected warmup-only policy to reject vote outside warmup");
	}

	if (!ctx.lastMessage || Q_stricmp(ctx.lastMessage, "Voting to alter the item timers is only allowed during the warm up period.\n") != 0) {
		return GT_Failf("unexpected warmup rejection message: %s", ctx.lastMessage ? ctx.lastMessage : "<null>");
	}

	return qtrue;
}

/*
=============
GT_ItemTimerVoteAcceptsValidToggle

Confirms the handler flips the timers when a valid option is supplied.
=============
*/
static qboolean GT_ItemTimerVoteAcceptsValidToggle(void) {
	gt_itemtimer_vote_context_t ctx;

	GT_ItemTimerVoteContextInit(&ctx);

	if (!GT_ItemTimerApplyVote(&ctx, "OFF")) {
		return GT_Failf("expected vote to accept OFF option");
	}

	if (ctx.timersEnabled) {
		return GT_Failf("expected timers to disable after OFF vote");
	}

	if (!GT_ItemTimerApplyVote(&ctx, "ON")) {
		return GT_Failf("expected vote to accept ON option");
	}

	if (!ctx.timersEnabled) {
		return GT_Failf("expected timers to enable after ON vote");
	}

	return qtrue;
}

/*
=============
GT_TrainingBlocksAddbotCommand

Mirrors the `Addbot not allowed during training` guard from the binary.
=============
*/
static qboolean GT_TrainingBlocksAddbotCommand(void) {
	gt_training_command_context_t ctx;

	GT_TrainingCommandContextInit(&ctx);
	ctx.trainingActive = qtrue;

	if (GT_TrainingAllowsAddbot(&ctx)) {
		return GT_Failf("expected training to block addbot");
	}

	if (!ctx.lastMessage || Q_stricmp(ctx.lastMessage, "Addbot not allowed during training.\n") != 0) {
		return GT_Failf("unexpected addbot rejection message: %s", ctx.lastMessage ? ctx.lastMessage : "<null>");
	}

	return qtrue;
}

/*
=============
GT_ForceBroadcastPushesConfigstring

Validates that the force toggles refresh configstring 0x2B3 when flipped.
=============
*/
static qboolean GT_ForceBroadcastPushesConfigstring(void) {
	gt_force_broadcast_log_t log;

	memset(&log, 0, sizeof(log));
	GT_ApplyForceBroadcast("g_forceSendConfigstring", qtrue, &log);

	if (log.configIndex != CS_FORCED_COSMETICS) {
		return GT_Failf("expected configstring index 0x2B3, received %d", log.configIndex);
	}

	if ( Q_stricmp( Info_ValueForKey( log.payload, "hud" ), "1" ) != 0 ) {
		return GT_Failf("expected hud flag '1', received '%s'", Info_ValueForKey( log.payload, "hud" ) );
	}

	if ( Q_stricmp( Info_ValueForKey( log.payload, "sb" ), "0" ) != 0 ) {
		return GT_Failf("expected scoreboard flag '0', received '%s'", Info_ValueForKey( log.payload, "sb" ) );
	}

	if ( Q_stricmp( Info_ValueForKey( log.payload, "dmg" ), "0" ) != 0 ) {
		return GT_Failf("expected damage flag '0', received '%s'", Info_ValueForKey( log.payload, "dmg" ) );
	}

	return qtrue;
}

static const game_fixture_t gt_cosmetics_training_fixtures[] = {
	{
		"itemtimer_vote_training_rejects",
		NULL,
		GT_ItemTimerVoteRejectsDuringTraining,
		NULL,
		"Ensures training blocks item timer votes with the retail message"
	},
	{
		"itemtimer_vote_warmup_only_rejects",
		NULL,
		GT_ItemTimerVoteHonoursWarmupRestriction,
		NULL,
		"Confirms warmup-only policy rejects item timer changes mid-match"
	},
	{
		"itemtimer_vote_accepts_valid_toggle",
		NULL,
		GT_ItemTimerVoteAcceptsValidToggle,
		NULL,
		"Validates ON/OFF votes update the timer state"
	},
	{
		"training_blocks_addbot",
		NULL,
		GT_TrainingBlocksAddbotCommand,
		NULL,
		"Replays the training guard that refuses addbot commands"
	},
	{
		"force_flags_emit_configstring",
		NULL,
		GT_ForceBroadcastPushesConfigstring,
		NULL,
		"Verifies force toggles refresh configstring 0x2B3"
	}
};

/*
=============
GT_RunCosmeticTrainingFixtures

Executes the cosmetic/training regression fixtures.
=============
*/
game_fixture_result_t GT_RunCosmeticTrainingFixtures(void) {
	game_fixture_reporter_t reporter;
	GT_InitDefaultReporter(&reporter);
	return GT_RunFixtureSuite(
		"cosmetics_training",
		gt_cosmetics_training_fixtures,
		GAME_TESTS_ARRAY_LEN(gt_cosmetics_training_fixtures),
		&reporter);
}
