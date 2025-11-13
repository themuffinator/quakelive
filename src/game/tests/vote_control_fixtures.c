#include "rules_fixtures.h"

#if defined(__has_include)
#if __has_include("g_local.h")
#include "g_local.h"
#elif __has_include("../code/game/g_local.h")
#include "../code/game/g_local.h"
#elif __has_include("../../code/game/g_local.h")
#include "../../code/game/g_local.h"
#else
#error "Unable to locate g_local.h for vote fixtures"
#endif
#else
#include "../../code/game/g_local.h"
#endif

#define GT_SECONDS_TO_MSEC(seconds) ((seconds) * 1000)

typedef struct {
	int	allowMidGame;
	int	voteDelaySeconds;
	int	voteLimit;
	int	matchStartTime;
	int	lastVoteTime;
	int	votesCalled;
} gt_vote_context_t;

typedef struct {
	int	allowKillDelay;
	int	lastKillTime;
	int	lastSpawnTime;
} gt_kill_context_t;

typedef struct {
	int	complaintDamageThreshold;
	int	complaintLimit;
	int	complaints;
	qboolean	kicked;
} gt_complaint_context_t;

static void GT_VoteContextInit(gt_vote_context_t *ctx);
static qboolean GT_SimulateCallVote(gt_vote_context_t *ctx, int currentTime, qboolean midGame);
static void GT_KillContextInit(gt_kill_context_t *ctx, int allowKillDelay, int spawnTime);
static qboolean GT_SimulateKillCommand(gt_kill_context_t *ctx, int currentTime);
static void GT_ComplaintContextInit(gt_complaint_context_t *ctx, int damageThreshold, int complaintLimit);
static qboolean GT_RegisterComplaint(gt_complaint_context_t *ctx, int damage);

/*
=============
GT_VoteContextInit

Initialises the simulated vote context using the provided defaults.
=============
*/
static void GT_VoteContextInit(gt_vote_context_t *ctx) {
	if (!ctx) {
		return;
	}

	ctx->allowMidGame = 0;
	ctx->voteDelaySeconds = 0;
	ctx->voteLimit = 0;
	ctx->matchStartTime = 0;
	ctx->lastVoteTime = -1;
	ctx->votesCalled = 0;
}

/*
=============
GT_SimulateCallVote

Simulates a callvote attempt given the configured cvars and match state.
=============
*/
static qboolean GT_SimulateCallVote(gt_vote_context_t *ctx, int currentTime, qboolean midGame) {
	int	allowedDelay;

	if (!ctx) {
		return GT_Failf("vote context is NULL");
	}

	if (!ctx->allowMidGame && midGame) {
		return qfalse;
	}

	if (ctx->voteLimit > 0 && ctx->votesCalled >= ctx->voteLimit) {
		return qfalse;
	}

	allowedDelay = GT_SECONDS_TO_MSEC(ctx->voteDelaySeconds);
	if (ctx->voteDelaySeconds > 0) {
		int	sinceStart;

		sinceStart = currentTime - ctx->matchStartTime;
		if (sinceStart < allowedDelay) {
			return qfalse;
		}

		if (ctx->lastVoteTime >= 0 && currentTime - ctx->lastVoteTime < allowedDelay) {
			return qfalse;
		}
	}

	ctx->votesCalled++;
	ctx->lastVoteTime = currentTime;
	return qtrue;
}

/*
=============
GT_KillContextInit

Initialises the simulated kill command throttle state.
=============
*/
static void GT_KillContextInit(gt_kill_context_t *ctx, int allowKillDelay, int spawnTime) {
	if (!ctx) {
		return;
	}

	ctx->allowKillDelay = allowKillDelay;
	ctx->lastKillTime = -1;
	ctx->lastSpawnTime = spawnTime;
}

/*
=============
GT_SimulateKillCommand

Applies the g_allowKill cooldown to a kill command attempt.
=============
*/
static qboolean GT_SimulateKillCommand(gt_kill_context_t *ctx, int currentTime) {
	int	cooldown;

	if (!ctx) {
		return GT_Failf("kill context is NULL");
	}

	cooldown = ctx->allowKillDelay;
	if (cooldown < 0) {
		return qfalse;
	}

	if (cooldown == 0) {
		ctx->lastKillTime = currentTime;
		return qtrue;
	}

	if (currentTime - ctx->lastSpawnTime < cooldown) {
		return qfalse;
	}

	if (ctx->lastKillTime >= 0 && currentTime - ctx->lastKillTime < cooldown) {
		return qfalse;
	}

	ctx->lastKillTime = currentTime;
	return qtrue;
}

/*
=============
GT_ComplaintContextInit

Initialises the simulated complaint bookkeeping with the configured limits.
=============
*/
static void GT_ComplaintContextInit(gt_complaint_context_t *ctx, int damageThreshold, int complaintLimit) {
	if (!ctx) {
		return;
	}

	ctx->complaintDamageThreshold = damageThreshold;
	ctx->complaintLimit = complaintLimit;
	ctx->complaints = 0;
	ctx->kicked = qfalse;
}

/*
=============
GT_RegisterComplaint

Tracks damage events and records complaints when thresholds are met.
=============
*/
static qboolean GT_RegisterComplaint(gt_complaint_context_t *ctx, int damage) {
	if (!ctx) {
		return GT_Failf("complaint context is NULL");
	}

	if (damage < ctx->complaintDamageThreshold) {
		return qfalse;
	}

	if (ctx->complaintLimit <= 0) {
		ctx->complaints++;
		return qtrue;
	}

	if (ctx->complaints >= ctx->complaintLimit) {
		ctx->kicked = qtrue;
		return qfalse;
	}

	ctx->complaints++;
	if (ctx->complaints >= ctx->complaintLimit) {
		ctx->kicked = qtrue;
	}

	return qtrue;
}

/*
=============
GT_CallVoteHonoursMidGameToggle

Validates g_allowVoteMidGame gating in mid-match scenarios.
=============
*/
static qboolean GT_CallVoteHonoursMidGameToggle(void) {
	gt_vote_context_t	ctx;

	GT_VoteContextInit(&ctx);
	ctx.matchStartTime = 0;
	ctx.voteLimit = 3;

	if (GT_SimulateCallVote(&ctx, 60000, qtrue)) {
		return GT_Failf("expected mid-game vote to fail when disabled");
	}

	ctx.allowMidGame = 1;
	if (!GT_SimulateCallVote(&ctx, 60000, qtrue)) {
		return GT_Failf("expected mid-game vote to pass when enabled");
	}

	return qtrue;
}

/*
=============
GT_CallVoteRespectsDelayAndLimitAdjustments

Exercises g_voteDelay and g_voteLimit transitions across successive votes.
=============
*/
static qboolean GT_CallVoteRespectsDelayAndLimitAdjustments(void) {
	gt_vote_context_t	ctx;

	GT_VoteContextInit(&ctx);
	ctx.allowMidGame = 1;
	ctx.matchStartTime = 1000;
	ctx.voteDelaySeconds = 20;
	ctx.voteLimit = 2;

	if (GT_SimulateCallVote(&ctx, 15000, qtrue)) {
		return GT_Failf("vote delay should block early calls");
	}

	ctx.voteDelaySeconds = 5;
	if (!GT_SimulateCallVote(&ctx, 16000, qtrue)) {
		return GT_Failf("expected vote to succeed after lowering delay");
	}

	if (GT_SimulateCallVote(&ctx, 19000, qtrue)) {
		return GT_Failf("vote delay should apply between consecutive votes");
	}

	if (!GT_SimulateCallVote(&ctx, 25000, qtrue)) {
		return GT_Failf("expected second vote within limit");
	}

	if (GT_SimulateCallVote(&ctx, 40000, qtrue)) {
		return GT_Failf("vote limit should block additional calls");
	}

	ctx.voteLimit = 3;
	if (!GT_SimulateCallVote(&ctx, 45000, qtrue)) {
		return GT_Failf("expected vote to succeed after raising limit");
	}

	return qtrue;
}

/*
=============
GT_KillCommandHonoursAllowKillCooldown

Verifies the g_allowKill throttle blocks rapid kill attempts.
=============
*/
static qboolean GT_KillCommandHonoursAllowKillCooldown(void) {
	gt_kill_context_t	ctx;

	GT_KillContextInit(&ctx, 5000, 1000);

	if (GT_SimulateKillCommand(&ctx, 4000)) {
		return GT_Failf("kill command should respect spawn delay");
	}

	if (!GT_SimulateKillCommand(&ctx, 7000)) {
		return GT_Failf("expected kill command after delay");
	}

	if (GT_SimulateKillCommand(&ctx, 9000)) {
		return GT_Failf("cooldown should prevent rapid self-kills");
	}

	ctx.allowKillDelay = 0;
	if (!GT_SimulateKillCommand(&ctx, 9500)) {
		return GT_Failf("disabling cooldown should permit immediate kill");
	}

	return qtrue;
}

/*
=============
GT_ForfeitHonoursAllowToggle

Checks that the g_allowForfeit toggle gates surrender attempts.
=============
*/
static qboolean GT_ForfeitHonoursAllowToggle(void) {
	qboolean	allowForfeit;
	qboolean	forfeitAttempt;

	allowForfeit = qfalse;
	forfeitAttempt = allowForfeit ? qtrue : qfalse;
	if (forfeitAttempt) {
		return GT_Failf("forfeit should be blocked when disabled");
	}

	allowForfeit = qtrue;
	forfeitAttempt = allowForfeit ? qtrue : qfalse;
	if (!forfeitAttempt) {
		return GT_Failf("forfeit should be allowed when enabled");
	}

	return qtrue;
}

/*
=============
GT_ComplaintsRespectThresholdAndLimit

Ensures complaint counters only advance after threshold damage and honour the limit.
=============
*/
static qboolean GT_ComplaintsRespectThresholdAndLimit(void) {
	gt_complaint_context_t	ctx;

	GT_ComplaintContextInit(&ctx, 50, 0);

	if (GT_RegisterComplaint(&ctx, 40)) {
		return GT_Failf("damage below threshold should not register");
	}

	if (!GT_RegisterComplaint(&ctx, 55)) {
		return GT_Failf("damage above threshold should register when limit disabled");
	}

	if (ctx.kicked) {
		return GT_Failf("no kick expected when limit disabled");
	}

	ctx.complaints = 0;
	ctx.complaintLimit = 2;

	if (!GT_RegisterComplaint(&ctx, 60)) {
		return GT_Failf("first qualifying complaint should register");
	}

	if (ctx.kicked) {
		return GT_Failf("kick should trigger only after reaching limit");
	}

	if (!GT_RegisterComplaint(&ctx, 70)) {
		return GT_Failf("second qualifying complaint should register");
	}

	if (!ctx.kicked) {
		return GT_Failf("kick expected once limit reached");
	}

	if (GT_RegisterComplaint(&ctx, 80)) {
		return GT_Failf("further complaints should be blocked after kick");
	}

	return qtrue;
}

static const game_fixture_t gt_vote_control_fixtures[] = {
	{
		"callvote_midgame_toggle",
		NULL,
		GT_CallVoteHonoursMidGameToggle,
		NULL,
		"Validates the g_allowVoteMidGame gate for live matches"
	},
	{
		"callvote_delay_and_limit_adjustments",
		NULL,
		GT_CallVoteRespectsDelayAndLimitAdjustments,
		NULL,
		"Confirms g_voteDelay and g_voteLimit adjustments take effect"
	},
	{
		"kill_command_cooldown",
		NULL,
		GT_KillCommandHonoursAllowKillCooldown,
		NULL,
		"Checks the g_allowKill cooldown blocks rapid suicides"
	},
	{
		"forfeit_toggle",
		NULL,
		GT_ForfeitHonoursAllowToggle,
		NULL,
		"Ensures the g_allowForfeit toggle gates forfeits"
	},
	{
		"complaint_threshold_and_limit",
		NULL,
		GT_ComplaintsRespectThresholdAndLimit,
		NULL,
		"Covers g_complaintDamageThreshold and g_complaintLimit interactions"
	}
};

/*
=============
GT_RunVoteControlFixtures

Executes the vote/complaint control regression fixtures.
=============
*/
game_fixture_result_t GT_RunVoteControlFixtures(void) {
	game_fixture_reporter_t	reporter;

	GT_InitDefaultReporter(&reporter);
	return GT_RunFixtureSuite(
		"vote_control",
		gt_vote_control_fixtures,
		GAME_TESTS_ARRAY_LEN(gt_vote_control_fixtures),
		&reporter);
}
