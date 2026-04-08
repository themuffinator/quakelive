#ifndef QUAKE_LIVE_GAME_TYPES_H
#define QUAKE_LIVE_GAME_TYPES_H

#include <stddef.h>
#include <stdint.h>

// Mirror of the Sully-documented runtime shapes for gclient_t, gentity_t, and
// level_locals_t as they exist inside the Quake Live qagame module. These
// layouts capture the offsets that diverge from the GPL Quake III Arena
// sources so that gameplay reconstruction work can validate assumptions about
// Steam metadata, warmup bookkeeping, and command timing.

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ql_gclient_s ql_gclient_t;
typedef struct ql_gentity_s ql_gentity_t;
typedef struct ql_level_locals_s ql_level_locals_t;

typedef void (*ql_gentity_think_fn)(ql_gentity_t *self);
typedef void (*ql_gentity_touch_fn)(ql_gentity_t *self, ql_gentity_t *other, void *trace);
typedef void (*ql_gentity_use_fn)(ql_gentity_t *self, ql_gentity_t *other, ql_gentity_t *activator);
typedef void (*ql_gentity_blocked_fn)(ql_gentity_t *self, ql_gentity_t *other);
typedef void (*ql_gentity_pain_fn)(ql_gentity_t *self, ql_gentity_t *attacker, int32_t damage);
typedef void (*ql_gentity_die_fn)(ql_gentity_t *self, ql_gentity_t *inflictor, ql_gentity_t *attacker, int32_t damage, int32_t mod);

enum {
	QL_PLAYERTEAMSTATE_TEAM_BEGIN = 0,
	QL_PLAYERTEAMSTATE_TEAM_ACTIVE = 1,
	QL_MAX_NETNAME = 36,
	QL_WP_NUM_WEAPONS = 15,
	QL_TEAMSTAT_COUNT = 18,
	QL_SCORESTAT_PICKUP_COUNT = 4,
	QL_BODY_QUEUE_SIZE = 8,
	QL_MAX_SPAWN_VARS = 64,
	QL_MAX_SPAWN_VARS_CHARS = 4096
};

typedef int32_t playerTeamStateState_t;

typedef struct ql_playerTeamState_s {
	playerTeamStateState_t state;	// 0x00 (`TEAM_BEGIN` / `TEAM_ACTIVE` in the GPL tree)
	int32_t location;		// 0x04
	int32_t captures;		// 0x08
	int32_t basedefense;		// 0x0C
	int32_t carrierdefense;		// 0x10
	int32_t flagrecovery;		// 0x14
	int32_t fragcarrier;		// 0x18
	int32_t assists;		// 0x1C
	float lasthurtcarrier;		// 0x20
	float lastreturnedflag;		// 0x24
	float flagsince;		// 0x28
	float lastfraggedcarrier;	// 0x2C
} ql_playerTeamState_t;

// Retail Quake Live no longer exposes the GPL playerTeamState_t as a clean
// contiguous sub-struct inside gclient_t. The overlay below captures the
// evidence-backed teamplay block that survives at gclient + 0x2FC.
typedef struct ql_playerTeamState_runtime_s {
	int32_t captures;			// 0x00 (classic capture counter)
	int32_t basedefense;			// 0x04 (classic base-defense counter)
	int32_t carrierdefense;			// 0x08 (classic carrier-defense counter)
	int32_t flagrecovery;			// 0x0C (classic flag-return counter)
	int32_t fragcarrier;			// 0x10 (classic flag/skull-carrier frag counter)
	int32_t assists;			// 0x14 (classic capture-assist counter)
	int32_t field_18;			// 0x18 (retail-only accumulator reused by hold/race logic)
	int32_t field_1c;			// 0x1C (retail-only teamplay latch/counter still open)
	int32_t lasthurtcarrier_time;		// 0x20 (ms timestamp/reset marker)
	int32_t lastreturnedflag_time;		// 0x24 (ms timestamp)
	int32_t lastfraggedcarrier_time;	// 0x28 (ms timestamp)
	int32_t field_2c;			// 0x2C (retail-only tail slot still open)
} ql_playerTeamState_runtime_t;

typedef struct ql_usercmd_s {
	int32_t serverTime;			// 0x00
	int32_t angles[3];			// 0x04
	int32_t buttons;			// 0x10
	uint8_t weapon;				// 0x14
	int8_t forwardmove;			// 0x15
	int8_t rightmove;			// 0x16
	int8_t upmove;				// 0x17
} ql_usercmd_t;

// The GPL clientPersistant_t remains useful as a source-canonical reference
// even though retail Quake Live repurposes and reorders large parts of the
// persisted client block.
typedef struct ql_clientPersistant_source_s {
	int32_t connected;						// 0x000
	ql_usercmd_t cmd;						// 0x004
	int32_t localClient;						// 0x01C
	int32_t initialSpawn;						// 0x020
	int32_t predictItemPickup;					// 0x024
	int32_t pmoveFixed;						// 0x028
	char netname[QL_MAX_NETNAME];					// 0x02C
	int32_t maxHealth;						// 0x050
	int32_t enterTime;						// 0x054
	ql_playerTeamState_t teamState;					// 0x058
	int32_t voteCount;						// 0x088
	int32_t teamVoteCount;						// 0x08C
	int32_t teamInfo;						// 0x090
	int32_t voteDelayTime;						// 0x094
	int32_t voteLastSelection;					// 0x098
	int32_t voteLastEnableFrame;					// 0x09C
	int32_t killCommandTime;					// 0x0A0
	float ratingDamageScale;					// 0x0A4
	float ratingScoreScale;						// 0x0A8
	int32_t ratingMetadataLoaded;					// 0x0AC
	int32_t itemProgressionTier;					// 0x0B0
	uint32_t progressionFlags;					// 0x0B4
	uint32_t steamIdLow;						// 0x0B8
	uint32_t steamIdHigh;						// 0x0BC
	int32_t steamIdValid;						// 0x0C0
	int32_t damageGiven;						// 0x0C4
	int32_t damageReceived;						// 0x0C8
	int32_t weaponFrags[QL_WP_NUM_WEAPONS];				// 0x0CC
	int32_t weaponDamage[QL_WP_NUM_WEAPONS];			// 0x108
	int32_t accuracy_shots[QL_WP_NUM_WEAPONS];			// 0x144
	int32_t accuracy_hits[QL_WP_NUM_WEAPONS];			// 0x180
	int32_t teamScoreStats[QL_TEAMSTAT_COUNT];			// 0x1BC
	int32_t teamHoldStartTime[QL_TEAMSTAT_COUNT];			// 0x204
	int32_t pickupLastTime[QL_SCORESTAT_PICKUP_COUNT];		// 0x24C
	int32_t pickupIntervalTotalMs[QL_SCORESTAT_PICKUP_COUNT];	// 0x25C
	int32_t pickupIntervalCount[QL_SCORESTAT_PICKUP_COUNT];	// 0x26C
} ql_clientPersistant_source_t;

// Retail Quake Live still keeps a contiguous persisted client block at
// gclient + 0x250, but the member order no longer matches the GPL
// clientPersistant_t one-for-one.
typedef struct ql_clientPersistant_s {
	int32_t connected;						// 0x00 (CON_CONNECTING / CON_CONNECTED)
	ql_usercmd_t cmd;						// 0x04 (source-compatible usercmd_t prefix)
	int32_t cmd_field_18;						// 0x1C (retail cmd/persist seam still open)
	int32_t localClient;						// 0x20 (`ip` == `localhost`)
	int32_t initialSpawn;						// 0x24 (first-spawn placement latch)
	int32_t predictItemPickup;					// 0x28 (`cg_predictItems` userinfo toggle)
	char netname[QL_MAX_NETNAME];					// 0x2C (cleaned player name)
	int32_t field_50;						// 0x50 (retail userinfo/configstring seam still open)
	char userinfo_c_string[0x18];					// 0x54 (short userinfo/configstring `\\c\\%s` tail)
	int32_t field_6c;						// 0x6C (retail userinfo seam still open)
	uint32_t steam_id_low;						// 0x70 (Steam64 low from engine callback)
	uint32_t steam_id_high;						// 0x74 (Steam64 high from engine callback)
	int32_t maxHealth;						// 0x78 (handicap-capped max health)
	int32_t voteCount;						// 0x7C (vote-call throttle count)
	int32_t voteState;						// 0x80 (retail per-client vote role/state slot)
	int32_t complaint_count;						// 0x84 (complaint strike count against this client)
	int32_t complaint_client;						// 0x88 (victim-side complaint target client index)
	int32_t complaint_end_time;					// 0x8C (victim-side complaint expiry time)
	int32_t complaint_damage_received;				// 0x90 (pending friendly-fire damage received toward a complaint prompt)
	int32_t complaint_damage_given;				// 0x94 (pending friendly-fire damage dealt toward a complaint prompt)
	int32_t ready_latch;						// 0x98 (dedicated Quake Live ready/continue latch)
	int32_t recording_preferences;					// 0x9C (auto-record / auto-screenshot bitfield)
	int32_t field_a0;						// 0xA0 (retail persisted timer/state still open)
	int32_t enterTime;						// 0xA4 (level.time when the client entered the match)
	playerTeamStateState_t team_state_state;			// 0xA8 (`TEAM_BEGIN` / `TEAM_ACTIVE` spawn-selection state)
	ql_playerTeamState_runtime_t team_state_runtime;		// 0xAC (retail teamplay counter/timer overlay)
	int32_t inactivity_accumulator_ms;				// 0xDC (idle time toward inactivity handling)
	int32_t inactivity_warning;					// 0xE0 (warning latch for inactivity centerprints)
	int32_t flood_last_time;					// 0xE4 (flood-decay timestamp)
	int32_t flood_count;						// 0xE8 (retail client-flood counter)
	uint8_t tail_pad[0x0C];						// 0xEC (remaining persisted/session-adjacent state)
} ql_clientPersistant_t;

// The reconstructed source clientSession_t remains useful as a
// source-canonical reference even though retail Quake Live repurposes several
// members differently inside the persisted session block.
typedef struct ql_clientSession_source_s {
	int32_t sessionTeam;			// 0x00
	int32_t spectatorTime;			// 0x04
	int32_t spectatorState;			// 0x08
	int32_t spectatorClient;		// 0x0C
	int32_t selectedSpawnWeapon;		// 0x10
	int32_t wins;				// 0x14
	int32_t losses;				// 0x18
	int32_t teamLeader;			// 0x1C
	int32_t privilege;			// 0x20
	int32_t spectateOnly;			// 0x24
	int32_t spectatorQueuePosition;		// 0x28
	int32_t spectatorQueuePositionDirty;	// 0x2C (skipped by the source serializer)
	int32_t muted;				// 0x30
	int32_t sessionField34;			// 0x34
	int32_t skill1;				// 0x38
	int32_t skill2;				// 0x3C
	int32_t skill3;				// 0x40
} ql_clientSession_source_t;

// Retail Quake Live still keeps a contiguous session-style block at
// gclient + 0x348, but the field meanings no longer match the GPL
// clientSession_t one-for-one.
typedef struct ql_clientSession_s {
	int32_t sessionTeam;			// 0x00 (persistent team)
	int32_t spectatorTime;			// 0x04 (queue-order timestamp)
	int32_t spectatorState;			// 0x08 (free/follow/scoreboard)
	int32_t spectatorClient;		// 0x0C (follow target)
	int32_t selected_spawn_weapon;		// 0x10 (persisted loadout/starting-weapon selection)
	int32_t wins;				// 0x14 (tournament wins)
	int32_t losses;				// 0x18 (tournament losses)
	int32_t teamLeader;			// 0x1C (team-leader latch)
	int32_t privilege;			// 0x20 (persistent admin tier)
	int32_t spectate_only;			// 0x24 (retail `so` latch)
	int32_t spectator_queue_position;	// 0x28 (retail `pq` slot)
	int32_t spectator_queue_position_dirty;	// 0x2C (live queue-dirty latch, skipped by session serializer)
	int32_t muted;				// 0x30 (persistent mute latch)
	int32_t field_34;			// 0x34 (serialized session tail still open)
} ql_clientSession_t;

typedef struct ql_gclient_s {
	uint8_t player_state_and_linkage[0x250];	// 0x000 (ps/entity linkage cleared on spawn)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41211-L41218】
	ql_clientPersistant_t pers;			// 0x250 retail clientPersistant_t overlay
	ql_clientSession_t sess;			// 0x348 retail clientSession_t overlay
	int32_t noclip;					// 0x380 (noclip cheat state toggled by the command path)
	uint8_t combat_state_pad[0x3B8 - 0x384];	// 0x384 active combat/session state still open
	int32_t last_hurt_client;			// 0x3B8 (victim-side last hurt/killer tracker)
	int32_t last_killed_client;			// 0x3BC (attacker-side last killed client tracker)
	uint8_t combat_tracker_pad[0x3E4 - 0x3C0];	// 0x3C0 remaining combat bookkeeping still open
	int32_t revenge_kill_streaks[64];		// 0x3E4 per-opponent revenge/kill-streak counters
	uint8_t award_and_stat_block0[0x504 - 0x4E4];	// 0x4E4 award trackers and timers still open
	int32_t factory_regen_armor_accumulator_ms;	// 0x504 (msec accumulated toward the next factory armor regen tick)
	int32_t factory_regen_health_accumulator_ms;	// 0x508 (msec accumulated toward the next factory health regen tick)
	uint8_t award_and_stat_block1[0x514 - 0x50C];	// 0x50C adjacent regen/combat state still open
	int32_t factory_regen_health_pending;		// 0x514 (latched once damage should restart delayed health regen)
	int32_t factory_regen_armor_pending;		// 0x518 (latched once damage should restart delayed armor regen)
	uint8_t award_and_stat_block2[0x568 - 0x51C];	// 0x51C remaining award/stat state still open
	int32_t command_time_seed;			// 0x568 (randomised command clock seed)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41126-L41132】
	int32_t command_time_base;			// 0x56C (level.time snapshot for command seed window)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41127-L41130】
	int32_t command_time_delta;			// 0x570 (delta between server time and last command)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41127-L41130】
	uint8_t roster_pad[0x578 - 0x574];		// 0x574 alignment gap for roster tracking
	int32_t restart_queue_position;		// 0x578 (queue slot assigned while rebuilding teams)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L12299-L12313】
	int32_t restart_queue_rejoin;		// 0x57C (flag noting reuse of prior slot)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L12305-L12313】
	int32_t team_seed_rank;			// 0x580 (per-team seed used when pairing same opponents)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L12314-L12329】
	int32_t team_seed_reused;			// 0x584 (whether the team seed came from a prior match)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L12320-L12329】
	int32_t kill_count;				// 0x588 (running kill total used by obituary/stat output)
	int32_t death_count;				// 0x58C (running death total used by obituary/stat output)
	uint8_t award_and_stat_block3[0x594 - 0x590];	// 0x590 adjacent stat slots still open
	int32_t team_damage_events_given;		// 0x594 (count of team-damage incidents inflicted)
	int32_t team_damage_events_received;		// 0x598 (count of team-damage incidents suffered)
	uint8_t weapon_and_award_stats[0xBD8 - 0x59C];	// 0x59C rolling weapon stats/awards (still mostly open)
} ql_gclient_t;

// Retail gentity_t is not a single constant delta from the GPL gentity_s
// layout. The client/inuse/classname block lines up at source+0x38, the
// target/callback block at source+0x48, wait/random at source+0x4c, and the
// item pointer at source+0x50.
enum {
	QL_GENTITY_OFFSET_R_SVFLAGS = 0x068,
	QL_GENTITY_OFFSET_SVFLAGS_EXT = 0x1E0,
	QL_GENTITY_OFFSET_CLIENT = 0x23C,
	QL_GENTITY_OFFSET_INUSE = 0x240,
	QL_GENTITY_OFFSET_CLASSNAME = 0x244,
	QL_GENTITY_OFFSET_SPAWNFLAGS = 0x248,
	QL_GENTITY_OFFSET_NEVER_FREE = 0x24C,
	QL_GENTITY_OFFSET_FLAGS = 0x250,
	QL_GENTITY_OFFSET_MODEL = 0x254,
	QL_GENTITY_OFFSET_MODEL2 = 0x258,
	QL_GENTITY_OFFSET_FREETIME = 0x25C,
	QL_GENTITY_OFFSET_EVENT_TIME = 0x260,
	QL_GENTITY_OFFSET_FREE_AFTER_EVENT = 0x264,
	QL_GENTITY_OFFSET_UNLINK_AFTER_EVENT = 0x268,
	QL_GENTITY_OFFSET_PHYSICS_OBJECT = 0x26C,
	QL_GENTITY_OFFSET_PHYSICS_BOUNCE = 0x270,
	QL_GENTITY_OFFSET_CLIPMASK = 0x274,
	QL_GENTITY_OFFSET_MOVER_STATE = 0x278,
	QL_GENTITY_OFFSET_SOUND_POS1 = 0x27C,
	QL_GENTITY_OFFSET_SOUND_1TO2 = 0x280,
	QL_GENTITY_OFFSET_SOUND_2TO1 = 0x284,
	QL_GENTITY_OFFSET_SOUND_POS2 = 0x288,
	QL_GENTITY_OFFSET_SOUND_LOOP = 0x28C,
	QL_GENTITY_OFFSET_PARENT = 0x290,
	QL_GENTITY_OFFSET_NEXTTRAIN = 0x294,
	QL_GENTITY_OFFSET_POS1 = 0x29C,
	QL_GENTITY_OFFSET_POS2 = 0x2A8,
	QL_GENTITY_OFFSET_SPEED = 0x2E4,
	QL_GENTITY_OFFSET_MOVEDIR = 0x2E8,
	QL_GENTITY_OFFSET_MESSAGE = 0x2B4,
	QL_GENTITY_OFFSET_TARGET = 0x2D0,
	QL_GENTITY_OFFSET_TARGETNAME = 0x2D4,
	QL_GENTITY_OFFSET_NEXTTHINK = 0x2F4,
	QL_GENTITY_OFFSET_THINK = 0x2F8,
	QL_GENTITY_OFFSET_REACHED = 0x300,
	QL_GENTITY_OFFSET_BLOCKED = 0x304,
	QL_GENTITY_OFFSET_TOUCH = 0x308,
	QL_GENTITY_OFFSET_USE = 0x30C,
	QL_GENTITY_OFFSET_PAIN = 0x310,
	QL_GENTITY_OFFSET_DIE = 0x314,
	QL_GENTITY_OFFSET_PAIN_DEBOUNCE_TIME = 0x318,
	QL_GENTITY_OFFSET_FLY_SOUND_DEBOUNCE_TIME = 0x31C,
	QL_GENTITY_OFFSET_HEALTH = 0x320,
	QL_GENTITY_OFFSET_TAKEDAMAGE = 0x324,
	QL_GENTITY_OFFSET_DAMAGE = 0x328,
	QL_GENTITY_OFFSET_SPLASH_DAMAGE = 0x330,
	QL_GENTITY_OFFSET_SPLASH_RADIUS = 0x334,
	QL_GENTITY_OFFSET_METHOD_OF_DEATH = 0x338,
	QL_GENTITY_OFFSET_SPLASH_METHOD_OF_DEATH = 0x33C,
	QL_GENTITY_OFFSET_COUNT = 0x340,
	QL_GENTITY_OFFSET_ENEMY = 0x344,
	QL_GENTITY_OFFSET_ACTIVATOR = 0x348,
	QL_GENTITY_OFFSET_TEAMMASTER = 0x350,
	QL_GENTITY_OFFSET_TEAMCHAIN = 0x354,
	QL_GENTITY_OFFSET_KAMIKAZE_TIME = 0x358,
	QL_GENTITY_OFFSET_KAMIKAZE_SHOCK_TIME = 0x35C,
	QL_GENTITY_OFFSET_WATERTYPE = 0x360,
	QL_GENTITY_OFFSET_WATERLEVEL = 0x364,
	QL_GENTITY_OFFSET_NOISE_INDEX = 0x368,
	QL_GENTITY_OFFSET_WAIT = 0x370,
	QL_GENTITY_OFFSET_RANDOM = 0x374,
	QL_GENTITY_OFFSET_ITEM_AVAILABLE_TIME = 0x378,
	QL_GENTITY_OFFSET_ITEM = 0x37C,
	QL_GENTITY_OFFSET_ITEM_PICKUP_COUNT = 0x380,
	QL_GENTITY_SIZE_BYTES = 0x384
};

typedef struct ql_gentity_s {
	uint8_t s_and_r_head[QL_GENTITY_OFFSET_R_SVFLAGS];
	int32_t r_svFlags; // 0x068 (entityShared_t::svFlags)
	uint8_t r_after_svflags[QL_GENTITY_OFFSET_SVFLAGS_EXT -
		(QL_GENTITY_OFFSET_R_SVFLAGS + sizeof(int32_t))];
	int32_t svFlagsExt; // 0x1E0 (Quake Live-only entityShared extension word)
	uint8_t entity_runtime_pad[QL_GENTITY_OFFSET_CLIENT -
		(QL_GENTITY_OFFSET_SVFLAGS_EXT + sizeof(int32_t))];
	ql_gclient_t *client; // 0x23C
	int32_t inuse; // 0x240
	char *classname; // 0x244
	int32_t spawnflags; // 0x248
	int32_t neverFree; // 0x24C
	int32_t flags; // 0x250
	char *model; // 0x254
	char *model2; // 0x258
	uint8_t free_entity_pad[QL_GENTITY_OFFSET_FREETIME -
		(QL_GENTITY_OFFSET_MODEL2 + sizeof(char *))];
	int32_t freetime; // 0x25C
	int32_t eventTime; // 0x260
	int32_t freeAfterEvent; // 0x264
	int32_t unlinkAfterEvent; // 0x268 (post-event unlink latch)
	int32_t physicsObject; // 0x26C
	float physicsBounce; // 0x270
	int32_t clipmask; // 0x274
	int32_t moverState; // 0x278 (MOVER_POS1 / MOVER_POS2 / MOVER_1TO2 / MOVER_2TO1)
	int32_t soundPos1; // 0x27C
	int32_t sound1to2; // 0x280
	int32_t sound2to1; // 0x284
	int32_t soundPos2; // 0x288
	int32_t soundLoop; // 0x28C
	ql_gentity_t *parent; // 0x290
	ql_gentity_t *nextTrain; // 0x294
	uint8_t mover_link_pad[QL_GENTITY_OFFSET_POS1 -
		(QL_GENTITY_OFFSET_NEXTTRAIN + sizeof(ql_gentity_t *))];
	float pos1[3]; // 0x29C
	float pos2[3]; // 0x2A8
	uint8_t message_pad[QL_GENTITY_OFFSET_MESSAGE -
		(QL_GENTITY_OFFSET_POS2 + sizeof(float[3]))];
	char *message; // 0x2B4
	uint8_t target_pad[QL_GENTITY_OFFSET_TARGET -
		(QL_GENTITY_OFFSET_MESSAGE + sizeof(char *))];
	char *target; // 0x2D0
	char *targetname; // 0x2D4
	uint8_t target_runtime_pad[QL_GENTITY_OFFSET_SPEED -
		(QL_GENTITY_OFFSET_TARGETNAME + sizeof(char *))];
	float speed; // 0x2E4
	float movedir[3]; // 0x2E8
	uint8_t think_pad[QL_GENTITY_OFFSET_NEXTTHINK -
		(QL_GENTITY_OFFSET_MOVEDIR + sizeof(float[3]))];
	int32_t nextthink; // 0x2F4
	ql_gentity_think_fn think; // 0x2F8
	uint8_t reached_pad[QL_GENTITY_OFFSET_REACHED -
		(QL_GENTITY_OFFSET_THINK + sizeof(ql_gentity_think_fn))];
	ql_gentity_think_fn reached; // 0x300
	ql_gentity_blocked_fn blocked; // 0x304
	uint8_t callback_pad[QL_GENTITY_OFFSET_TOUCH -
		(QL_GENTITY_OFFSET_BLOCKED + sizeof(ql_gentity_blocked_fn))];
	ql_gentity_touch_fn touch; // 0x308
	ql_gentity_use_fn use; // 0x30C
	ql_gentity_pain_fn pain; // 0x310
	ql_gentity_die_fn die; // 0x314
	int32_t pain_debounce_time; // 0x318
	int32_t fly_sound_debounce_time; // 0x31C
	int32_t health; // 0x320
	int32_t takedamage; // 0x324 (qboolean in source; retail stores integer truth values)
	int32_t damage; // 0x328
	uint8_t gameplay_damage_pad[QL_GENTITY_OFFSET_SPLASH_DAMAGE -
		(QL_GENTITY_OFFSET_DAMAGE + sizeof(int32_t))];
	int32_t splashDamage; // 0x330
	int32_t splashRadius; // 0x334
	int32_t methodOfDeath; // 0x338
	int32_t splashMethodOfDeath; // 0x33C
	int32_t count; // 0x340
	ql_gentity_t *enemy; // 0x344
	ql_gentity_t *activator; // 0x348
	uint8_t team_link_pad[QL_GENTITY_OFFSET_TEAMMASTER -
		(QL_GENTITY_OFFSET_ACTIVATOR + sizeof(ql_gentity_t *))];
	ql_gentity_t *teammaster; // 0x350
	ql_gentity_t *teamchain; // 0x354
	int32_t kamikazeTime; // 0x358
	int32_t kamikazeShockTime; // 0x35C
	int32_t watertype; // 0x360
	int32_t waterlevel; // 0x364
	int32_t noise_index; // 0x368
	uint8_t item_pad[QL_GENTITY_OFFSET_WAIT -
		(QL_GENTITY_OFFSET_NOISE_INDEX + sizeof(int32_t))];
	float wait; // 0x370
	float random; // 0x374
	int32_t itemAvailableTime; // 0x378 (retail item-availability timestamp for pickup telemetry)
	void *item; // 0x37C (retail gitem_t*)
	int32_t itemPickupCount; // 0x380 (retail item pickup counter for repeated-pickup telemetry)
} ql_gentity_t;

typedef struct ql_level_locals_s {
	ql_gclient_t *	clients;		// 0x0000
	ql_gentity_t *	gentities;		// 0x0004
	int32_t	reserved_0008;		// 0x0008 (no stable retail reads promoted yet)
	int32_t	num_entities;		// 0x000C (spawned gentity count passed to trap_LocateGameData)
	int32_t	warmupTime;		// 0x0010 (set to -1/0 during worldspawn and countdown handling)
	int32_t	logFile;		// 0x0014 (fileHandle_t written by the logfile open callback)
	int32_t	maxclients;		// 0x0018 (sv_maxclients latched during G_InitGame)
	int32_t	time;		// 0x001C (current server time in msec)
	int32_t	msec;		// 0x0020 (delta from the prior G_RunFrame)
	int32_t	startTime;		// 0x0024 (level start time used by timelimit/mercy math)
	int32_t	teamScores[4];		// 0x0028 (TEAM_FREE/RED/BLUE/SPECTATOR score block)
	int32_t	lastTeamLocationTime;		// 0x0038 (team-overlay refresh timer)
	int32_t	newSession;		// 0x003C (gametype/session reset latch)
	int32_t	restarted;		// 0x0040 (map_restart/shutdown guard)
	uint8_t __pad0044[0x0008];
	int32_t	numConnectedClients;		// 0x004C (rebuilt by CalculateRanks)
	int32_t	numNonSpectatorClients;		// 0x0050 (connected clients not on TEAM_SPECTATOR)
	int32_t	numPlayingClients;		// 0x0054 (fully connected active players)
	int32_t	readyUpEligibleClients;		// 0x0058 (warmup-ready tally candidate count)
	int32_t	readyUpReadyClients;		// 0x005C (warmup-ready tally confirmed count)
	int32_t	reserved_0060;		// 0x0060 (adjacent sorted-client helper slot still open)
	int32_t	sortedClients[64];		// 0x0064 (rank-ordered client indices)
	int32_t	follow1;		// 0x0164
	int32_t	follow2;		// 0x0168
	int32_t	snd_fry;		// 0x016C
	int32_t	warmupModificationCount;		// 0x0170 (mirrors the tracked g_warmup modification count)
	char		voteString[0x400];		// 0x0174 (authoritative vote command string)
	char		voteDisplayString[0x400];	// 0x0574 (UI-facing vote text)
	int32_t	voteExecuteTime;		// 0x0974 (time when a queued vote command should execute)
	int32_t	voteTime;		// 0x0978 (level.time when the current vote was called)
	int32_t	voteYes;		// 0x097C (server-side yes tally)
	int32_t	voteNo;		// 0x0980 (server-side no tally)
	int32_t	pendingVoteClientNum;		// 0x0984 (pending caller client num for deferred vote activation/cancel)
	int32_t	spawning;		// 0x0988 (spawn parser active flag)
	int32_t	numSpawnVars;		// 0x098C (parsed key/value pair count for the current entity)
	char*		spawnVars[QL_MAX_SPAWN_VARS][2];	// 0x0990 (current entity spawn key/value pairs)
	int32_t	numSpawnVarChars;		// 0x0B90 (used bytes in spawnVarChars)
	char		spawnVarChars[QL_MAX_SPAWN_VARS_CHARS];	// 0x0B94 (token storage backing spawnVars)
	int32_t	intermissionQueued;		// 0x1B94 (time when CheckExitRules queued intermission)
	int32_t	intermissiontime;		// 0x1B98 (time when BeginIntermission started)
	int32_t	field_1b9c;		// 0x1B9C
	int32_t	intermissionExitStatusLatched;		// 0x1BA0 (descriptive retail-only latch backing the one-shot CS 0x2C3 intermission-exit status update)
	int32_t	field_1ba4;		// 0x1BA4
	float		intermission_origin[3];		// 0x1BA8 (captured intermission origin)
	float		intermission_angle[3];		// 0x1BB4 (captured intermission angles)
	int32_t	locationLinked;		// 0x1BC0 (target_location configstrings already linked)
	ql_gentity_t*	locationHead;		// 0x1BC4 (head of the linked target_location chain)
	int32_t	timeoutStartTime;		// 0x1BC8 (active timeout/pause start timestamp; retail also uses non-zero as the live timeout flag)
	int32_t	overtimeAccumulatedMsec;		// 0x1BCC (retail g_overtime extension added to clock-limit checks)
	int32_t	teamItemInitialSpawnDelaySeconds;		// 0x1BD0 (randomized initial IT_TEAM spawn delay in seconds)
	int32_t	powerupInitialSpawnDelaySeconds;		// 0x1BD4 (randomized initial IT_POWERUP spawn delay in seconds)
	int32_t	bodyQueIndex;		// 0x1BD8 (rotating body-queue cursor)
	ql_gentity_t*	bodyQue[QL_BODY_QUEUE_SIZE];		// 0x1BDC (queued corpse entities)
	int32_t	portalSequence;		// 0x1BFC (incrementing portal destination sequence)
	int32_t	postmatchSummaryLatched;		// 0x1C00 (descriptive retail-only one-shot LogExit postmatch summary/report latch)
	int32_t	trainingMapActive;		// 0x1C04 (worldspawn training/practice latch)
	int32_t	duelScoreboardLowClientNum;		// 0x1C08 (descriptive retail-only cached lower duel client num used when pairing scores_duel payloads)
	int32_t	duelScoreboardHighClientNum;		// 0x1C0C (descriptive retail-only cached higher duel client num used when pairing scores_duel payloads)
	uint8_t __pad1c10[0x03FF];
	uint8_t	field_200f;		// 0x200F
	uint8_t __pad2010[0x03FF];
	uint8_t	field_240f;		// 0x240F
	int32_t	field_2410;		// 0x2410
	uint8_t __pad2414[0x0024];
	int32_t	field_2438;		// 0x2438
	uint8_t __pad243c[0x0024];
	int32_t	field_2460;		// 0x2460
	uint8_t __pad2464[0x0024];
	int32_t	field_2488;		// 0x2488
	uint8_t __pad248c[0x0024];
	int32_t	field_24b0;		// 0x24B0
	int32_t	field_24b4;		// 0x24B4
	int32_t	field_24b8;		// 0x24B8
	int32_t	field_24bc;		// 0x24BC
	int32_t	field_24c0;		// 0x24C0
	int32_t	field_24c4;		// 0x24C4
	int32_t	field_24c8;		// 0x24C8
	int32_t	field_24cc;		// 0x24CC
	int32_t	field_24d0;		// 0x24D0
	int32_t	field_24d4;		// 0x24D4
	int32_t	field_24d8;		// 0x24D8
	int32_t	field_24dc;		// 0x24DC
	uint8_t __pad24e0[0x000C];
	int32_t	field_24ec;		// 0x24EC
	uint8_t __pad24f0[0x00EC];
	int32_t	field_25dc;		// 0x25DC
	int32_t	field_25e0;		// 0x25E0
	int32_t	field_25e4;		// 0x25E4
	int32_t	field_25e8;		// 0x25E8
	int32_t	field_25ec;		// 0x25EC
	uint8_t __pad25f0[0x0004];
	int32_t	field_25f4;		// 0x25F4
	int32_t	field_25f8;		// 0x25F8
	int32_t	field_25fc;		// 0x25FC
	uint8_t __pad2600[0x0004];
	int32_t	field_2604;		// 0x2604
	int32_t	field_2608;		// 0x2608
	int32_t	field_260c;		// 0x260C
	uint8_t __pad2610[0x0004];
	int32_t	field_2614;		// 0x2614
	int32_t	field_2618;		// 0x2618
	int32_t	field_261c;		// 0x261C
	uint8_t __pad2620[0x0004];
	int32_t	field_2624;		// 0x2624
	int32_t	field_2628;		// 0x2628
	int32_t	field_262c;		// 0x262C
	uint8_t __pad2630[0x0004];
	int32_t	field_2634;		// 0x2634
	int32_t	field_2638;		// 0x2638
	int32_t	field_263c;		// 0x263C
	uint8_t __pad2640[0x0004];
	int32_t	field_2644;		// 0x2644
	int32_t	field_2648;		// 0x2648
	int32_t	field_264c;		// 0x264C
	uint8_t __pad2650[0x0004];
	int32_t	field_2654;		// 0x2654
	int32_t	field_2658;		// 0x2658
	int32_t	field_265c;		// 0x265C
	uint8_t __pad2660[0x0004];
	int32_t	field_2664;		// 0x2664
	int32_t	field_2668;		// 0x2668
	int32_t	field_266c;		// 0x266C
	uint8_t __pad2670[0x0004];
	int32_t	field_2674;		// 0x2674
	int32_t	field_2678;		// 0x2678
	int32_t	field_267c;		// 0x267C
	uint8_t __pad2680[0x0004];
	int32_t	field_2684;		// 0x2684
	int32_t	field_2688;		// 0x2688
	int32_t	field_268c;		// 0x268C
	uint8_t __pad2690[0x0004];
	int32_t	field_2694;		// 0x2694
	int32_t	field_2698;		// 0x2698
	int32_t	field_269c;		// 0x269C
	uint8_t __pad26a0[0x0004];
	int32_t	field_26a4;		// 0x26A4
	int32_t	field_26a8;		// 0x26A8
	int32_t	field_26ac;		// 0x26AC
	uint8_t __pad26b0[0x0004];
	int32_t	field_26b4;		// 0x26B4
	int32_t	field_26b8;		// 0x26B8
	int32_t	field_26bc;		// 0x26BC
	uint8_t __pad26c0[0x0004];
	int32_t	field_26c4;		// 0x26C4
	int32_t	field_26c8;		// 0x26C8
	int32_t	field_26cc;		// 0x26CC
	uint8_t __pad26d0[0x0004];
	int32_t	field_26d4;		// 0x26D4
	int32_t	field_26d8;		// 0x26D8
	int32_t	field_26dc;		// 0x26DC
	uint8_t __pad26e0[0x0004];
	int32_t	field_26e4;		// 0x26E4
	int32_t	field_26e8;		// 0x26E8
	int32_t	field_26ec;		// 0x26EC
	uint8_t __pad26f0[0x0004];
	int32_t	field_26f4;		// 0x26F4
	uint8_t __pad26f8[0x0010];
	int32_t	field_2708;		// 0x2708
	int32_t	field_270c;		// 0x270C
	int32_t	field_2710;		// 0x2710
	int32_t	field_2714;		// 0x2714
	int32_t	field_2718;		// 0x2718
	uint8_t __pad271c[0x0004];
	int32_t	field_2720;		// 0x2720
	uint8_t __pad2724[0x0008];
	int32_t	field_272c;		// 0x272C
	int32_t	field_2730;		// 0x2730
	int32_t	field_2734;		// 0x2734
	int32_t	field_2738;		// 0x2738
	int32_t	field_273c;		// 0x273C
	int32_t	field_2740;		// 0x2740
	int32_t	field_2744;		// 0x2744
	int32_t	field_2748;		// 0x2748
	int32_t	field_274c;		// 0x274C
	int32_t	field_2750;		// 0x2750
	int32_t	field_2754;		// 0x2754
	int32_t	field_2758;		// 0x2758
	int32_t	field_275c;		// 0x275C
	int32_t	field_2760;		// 0x2760
	int32_t	field_2764;		// 0x2764
	int32_t	field_2768;		// 0x2768
	int32_t	field_276c;		// 0x276C
	int32_t	field_2770;		// 0x2770
	int32_t	field_2774;		// 0x2774
	int32_t	field_2778;		// 0x2778
	uint8_t __pad277c[0x03FC];
	int32_t	field_2b78;		// 0x2B78
	uint8_t __pad2b7c[0x1FF8];
	int32_t	field_4b74;		// 0x4B74
	int32_t	field_4b78;		// 0x4B78
	int32_t	field_4b7c;		// 0x4B7C
	int32_t	field_4b80;		// 0x4B80
	int32_t	matchForfeited;		// 0x4B84 (source-faithful G_ApplyForfeit / LogExit forfeit latch)
	int32_t	readyUpDelayDeadline;		// 0x4B88 (descriptive retail-only absolute deadline for g_warmupReadyDelayAction)
	int32_t	field_4b8c;		// 0x4B8C
	int32_t	field_4b90;		// 0x4B90
	int32_t	lastLeadChangeTime;		// 0x4B94 (descriptive retail-only timestamp exported as LAST_LEAD_CHANGE_TIME)
	int32_t	lastLeadToken;		// 0x4B98 (descriptive retail-only lead identity token: team lead enum or FFA client num)
} ql_level_locals_t;

typedef ql_gclient_t gclient_t;
typedef ql_gentity_t gentity_t;
typedef ql_level_locals_t level_locals_t;
typedef ql_playerTeamState_t playerTeamState_t;


#if defined(__cplusplus)
#define QL_STATIC_ASSERT(cond, msg) static_assert(cond, msg)
#elif defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
#define QL_STATIC_ASSERT(cond, msg) _Static_assert(cond, msg)
#else
#define QL_STATIC_ASSERT(cond, msg) typedef char static_assertion_##__LINE__[(cond) ? 1 : -1]
#endif

QL_STATIC_ASSERT(offsetof(ql_gclient_t, player_state_and_linkage) == 0x000, "gclient_t.player_state_and_linkage offset");
QL_STATIC_ASSERT(sizeof(ql_usercmd_t) == 0x18, "usercmd_t size");
QL_STATIC_ASSERT(offsetof(ql_usercmd_t, serverTime) == 0x00, "usercmd_t.serverTime offset");
QL_STATIC_ASSERT(offsetof(ql_usercmd_t, angles) == 0x04, "usercmd_t.angles offset");
QL_STATIC_ASSERT(offsetof(ql_usercmd_t, buttons) == 0x10, "usercmd_t.buttons offset");
QL_STATIC_ASSERT(offsetof(ql_usercmd_t, weapon) == 0x14, "usercmd_t.weapon offset");
QL_STATIC_ASSERT(offsetof(ql_usercmd_t, forwardmove) == 0x15, "usercmd_t.forwardmove offset");
QL_STATIC_ASSERT(offsetof(ql_usercmd_t, rightmove) == 0x16, "usercmd_t.rightmove offset");
QL_STATIC_ASSERT(offsetof(ql_usercmd_t, upmove) == 0x17, "usercmd_t.upmove offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_t, state) == 0x00, "playerTeamState_t.state offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_t, location) == 0x04, "playerTeamState_t.location offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_t, captures) == 0x08, "playerTeamState_t.captures offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_t, basedefense) == 0x0C, "playerTeamState_t.basedefense offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_t, carrierdefense) == 0x10, "playerTeamState_t.carrierdefense offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_t, flagrecovery) == 0x14, "playerTeamState_t.flagrecovery offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_t, fragcarrier) == 0x18, "playerTeamState_t.fragcarrier offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_t, assists) == 0x1C, "playerTeamState_t.assists offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_t, lasthurtcarrier) == 0x20, "playerTeamState_t.lasthurtcarrier offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_t, lastreturnedflag) == 0x24, "playerTeamState_t.lastreturnedflag offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_t, flagsince) == 0x28, "playerTeamState_t.flagsince offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_t, lastfraggedcarrier) == 0x2C, "playerTeamState_t.lastfraggedcarrier offset");
QL_STATIC_ASSERT(sizeof(ql_playerTeamState_t) == 0x30, "playerTeamState_t size");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_runtime_t, captures) == 0x00, "playerTeamState_runtime_t.captures offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_runtime_t, basedefense) == 0x04, "playerTeamState_runtime_t.basedefense offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_runtime_t, carrierdefense) == 0x08, "playerTeamState_runtime_t.carrierdefense offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_runtime_t, flagrecovery) == 0x0C, "playerTeamState_runtime_t.flagrecovery offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_runtime_t, fragcarrier) == 0x10, "playerTeamState_runtime_t.fragcarrier offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_runtime_t, assists) == 0x14, "playerTeamState_runtime_t.assists offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_runtime_t, field_18) == 0x18, "playerTeamState_runtime_t.field_18 offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_runtime_t, field_1c) == 0x1C, "playerTeamState_runtime_t.field_1c offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_runtime_t, lasthurtcarrier_time) == 0x20, "playerTeamState_runtime_t.lasthurtcarrier_time offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_runtime_t, lastreturnedflag_time) == 0x24, "playerTeamState_runtime_t.lastreturnedflag_time offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_runtime_t, lastfraggedcarrier_time) == 0x28, "playerTeamState_runtime_t.lastfraggedcarrier_time offset");
QL_STATIC_ASSERT(offsetof(ql_playerTeamState_runtime_t, field_2c) == 0x2C, "playerTeamState_runtime_t.field_2c offset");
QL_STATIC_ASSERT(sizeof(ql_playerTeamState_runtime_t) == 0x30, "playerTeamState_runtime_t size");
QL_STATIC_ASSERT(sizeof(ql_clientPersistant_source_t) == 0x27C, "clientPersistant_source_t size");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_source_t, cmd) == 0x004, "clientPersistant_source_t.cmd offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_source_t, localClient) == 0x01C, "clientPersistant_source_t.localClient offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_source_t, netname) == 0x02C, "clientPersistant_source_t.netname offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_source_t, maxHealth) == 0x050, "clientPersistant_source_t.maxHealth offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_source_t, enterTime) == 0x054, "clientPersistant_source_t.enterTime offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_source_t, teamState) == 0x058, "clientPersistant_source_t.teamState offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_source_t, voteCount) == 0x088, "clientPersistant_source_t.voteCount offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_source_t, steamIdLow) == 0x0B8, "clientPersistant_source_t.steamIdLow offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_source_t, damageGiven) == 0x0C4, "clientPersistant_source_t.damageGiven offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_source_t, pickupIntervalCount) == 0x26C, "clientPersistant_source_t.pickupIntervalCount offset");
QL_STATIC_ASSERT(sizeof(ql_clientPersistant_t) == 0x0F8, "clientPersistant_t size");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, cmd) == 0x004, "clientPersistant_t.cmd offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, cmd_field_18) == 0x01C, "clientPersistant_t.cmd_field_18 offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, localClient) == 0x020, "clientPersistant_t.localClient offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, initialSpawn) == 0x024, "clientPersistant_t.initialSpawn offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, predictItemPickup) == 0x028, "clientPersistant_t.predictItemPickup offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, netname) == 0x02C, "clientPersistant_t.netname offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, userinfo_c_string) == 0x054, "clientPersistant_t.userinfo_c_string offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, steam_id_low) == 0x070, "clientPersistant_t.steam_id_low offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, steam_id_high) == 0x074, "clientPersistant_t.steam_id_high offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, maxHealth) == 0x078, "clientPersistant_t.maxHealth offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, voteCount) == 0x07C, "clientPersistant_t.voteCount offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, complaint_client) == 0x088, "clientPersistant_t.complaint_client offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, complaint_end_time) == 0x08C, "clientPersistant_t.complaint_end_time offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, complaint_damage_received) == 0x090, "clientPersistant_t.complaint_damage_received offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, complaint_damage_given) == 0x094, "clientPersistant_t.complaint_damage_given offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, ready_latch) == 0x098, "clientPersistant_t.ready_latch offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, recording_preferences) == 0x09C, "clientPersistant_t.recording_preferences offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, enterTime) == 0x0A4, "clientPersistant_t.enterTime offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, team_state_state) == 0x0A8, "clientPersistant_t.team_state_state offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, team_state_runtime) == 0x0AC, "clientPersistant_t.team_state_runtime offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, inactivity_accumulator_ms) == 0x0DC, "clientPersistant_t.inactivity_accumulator_ms offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, inactivity_warning) == 0x0E0, "clientPersistant_t.inactivity_warning offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, flood_last_time) == 0x0E4, "clientPersistant_t.flood_last_time offset");
QL_STATIC_ASSERT(offsetof(ql_clientPersistant_t, flood_count) == 0x0E8, "clientPersistant_t.flood_count offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, pers) == 0x250, "gclient_t.pers offset");
QL_STATIC_ASSERT(sizeof(ql_clientSession_source_t) == 0x44, "clientSession_source_t size");
QL_STATIC_ASSERT(offsetof(ql_clientSession_source_t, selectedSpawnWeapon) == 0x10, "clientSession_source_t.selectedSpawnWeapon offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_source_t, wins) == 0x14, "clientSession_source_t.wins offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_source_t, privilege) == 0x20, "clientSession_source_t.privilege offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_source_t, spectateOnly) == 0x24, "clientSession_source_t.spectateOnly offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_source_t, spectatorQueuePosition) == 0x28, "clientSession_source_t.spectatorQueuePosition offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_source_t, spectatorQueuePositionDirty) == 0x2C, "clientSession_source_t.spectatorQueuePositionDirty offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_source_t, muted) == 0x30, "clientSession_source_t.muted offset");
QL_STATIC_ASSERT(sizeof(ql_clientSession_t) == 0x38, "clientSession_t size");
QL_STATIC_ASSERT(offsetof(ql_clientSession_t, selected_spawn_weapon) == 0x10, "clientSession_t.selected_spawn_weapon offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_t, wins) == 0x14, "clientSession_t.wins offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_t, losses) == 0x18, "clientSession_t.losses offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_t, teamLeader) == 0x1C, "clientSession_t.teamLeader offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_t, privilege) == 0x20, "clientSession_t.privilege offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_t, spectate_only) == 0x24, "clientSession_t.spectate_only offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_t, spectator_queue_position) == 0x28, "clientSession_t.spectator_queue_position offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_t, spectator_queue_position_dirty) == 0x2C, "clientSession_t.spectator_queue_position_dirty offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_t, muted) == 0x30, "clientSession_t.muted offset");
QL_STATIC_ASSERT(offsetof(ql_clientSession_t, field_34) == 0x34, "clientSession_t.field_34 offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, sess) == 0x348, "gclient_t.sess offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, noclip) == 0x380, "gclient_t.noclip offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, last_hurt_client) == 0x3B8, "gclient_t.last_hurt_client offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, last_killed_client) == 0x3BC, "gclient_t.last_killed_client offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, revenge_kill_streaks) == 0x3E4, "gclient_t.revenge_kill_streaks offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, factory_regen_armor_accumulator_ms) == 0x504, "gclient_t.factory_regen_armor_accumulator_ms offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, factory_regen_health_accumulator_ms) == 0x508, "gclient_t.factory_regen_health_accumulator_ms offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, factory_regen_health_pending) == 0x514, "gclient_t.factory_regen_health_pending offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, factory_regen_armor_pending) == 0x518, "gclient_t.factory_regen_armor_pending offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, command_time_seed) == 0x568, "gclient_t.command_time_seed offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, command_time_base) == 0x56C, "gclient_t.command_time_base offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, command_time_delta) == 0x570, "gclient_t.command_time_delta offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, restart_queue_position) == 0x578, "gclient_t.restart_queue_position offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, restart_queue_rejoin) == 0x57C, "gclient_t.restart_queue_rejoin offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, team_seed_rank) == 0x580, "gclient_t.team_seed_rank offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, kill_count) == 0x588, "gclient_t.kill_count offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, death_count) == 0x58C, "gclient_t.death_count offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, team_damage_events_given) == 0x594, "gclient_t.team_damage_events_given offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, team_damage_events_received) == 0x598, "gclient_t.team_damage_events_received offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, weapon_and_award_stats) == 0x59C, "gclient_t.weapon_and_award_stats offset");
QL_STATIC_ASSERT(sizeof(ql_gclient_t) == 0x0BD8, "gclient_t size");

QL_STATIC_ASSERT(offsetof(ql_gentity_t, r_svFlags) == 0x068, "gentity_t.r_svFlags offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, svFlagsExt) == 0x1E0, "gentity_t.svFlagsExt offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, client) == 0x23C, "gentity_t.client offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, inuse) == 0x240, "gentity_t.inuse offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, classname) == 0x244, "gentity_t.classname offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, spawnflags) == 0x248, "gentity_t.spawnflags offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, neverFree) == 0x24C, "gentity_t.neverFree offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, flags) == 0x250, "gentity_t.flags offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, model) == 0x254, "gentity_t.model offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, model2) == 0x258, "gentity_t.model2 offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, freetime) == 0x25C, "gentity_t.freetime offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, eventTime) == 0x260, "gentity_t.eventTime offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, freeAfterEvent) == 0x264, "gentity_t.freeAfterEvent offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, unlinkAfterEvent) == 0x268, "gentity_t.unlinkAfterEvent offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, physicsObject) == 0x26C, "gentity_t.physicsObject offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, physicsBounce) == 0x270, "gentity_t.physicsBounce offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, clipmask) == 0x274, "gentity_t.clipmask offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, moverState) == 0x278, "gentity_t.moverState offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, soundPos1) == 0x27C, "gentity_t.soundPos1 offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, sound1to2) == 0x280, "gentity_t.sound1to2 offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, sound2to1) == 0x284, "gentity_t.sound2to1 offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, soundPos2) == 0x288, "gentity_t.soundPos2 offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, soundLoop) == 0x28C, "gentity_t.soundLoop offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, parent) == 0x290, "gentity_t.parent offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, nextTrain) == 0x294, "gentity_t.nextTrain offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, pos1) == 0x29C, "gentity_t.pos1 offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, pos2) == 0x2A8, "gentity_t.pos2 offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, message) == 0x2B4, "gentity_t.message offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, target) == 0x2D0, "gentity_t.target offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, targetname) == 0x2D4, "gentity_t.targetname offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, speed) == 0x2E4, "gentity_t.speed offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, movedir) == 0x2E8, "gentity_t.movedir offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, nextthink) == 0x2F4, "gentity_t.nextthink offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, think) == 0x2F8, "gentity_t.think offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, reached) == 0x300, "gentity_t.reached offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, blocked) == 0x304, "gentity_t.blocked offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, touch) == 0x308, "gentity_t.touch offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, use) == 0x30C, "gentity_t.use offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, pain) == 0x310, "gentity_t.pain offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, die) == 0x314, "gentity_t.die offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, pain_debounce_time) == 0x318, "gentity_t.pain_debounce_time offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, fly_sound_debounce_time) == 0x31C, "gentity_t.fly_sound_debounce_time offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, health) == 0x320, "gentity_t.health offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, takedamage) == 0x324, "gentity_t.takedamage offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, damage) == 0x328, "gentity_t.damage offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, splashDamage) == 0x330, "gentity_t.splashDamage offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, splashRadius) == 0x334, "gentity_t.splashRadius offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, methodOfDeath) == 0x338, "gentity_t.methodOfDeath offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, splashMethodOfDeath) == 0x33C, "gentity_t.splashMethodOfDeath offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, count) == 0x340, "gentity_t.count offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, enemy) == 0x344, "gentity_t.enemy offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, activator) == 0x348, "gentity_t.activator offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, teammaster) == 0x350, "gentity_t.teammaster offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, teamchain) == 0x354, "gentity_t.teamchain offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, kamikazeTime) == 0x358, "gentity_t.kamikazeTime offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, kamikazeShockTime) == 0x35C, "gentity_t.kamikazeShockTime offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, watertype) == 0x360, "gentity_t.watertype offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, waterlevel) == 0x364, "gentity_t.waterlevel offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, noise_index) == 0x368, "gentity_t.noise_index offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, wait) == 0x370, "gentity_t.wait offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, random) == 0x374, "gentity_t.random offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, itemAvailableTime) == 0x378, "gentity_t.itemAvailableTime offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, item) == 0x37C, "gentity_t.item offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, itemPickupCount) == 0x380, "gentity_t.itemPickupCount offset");
QL_STATIC_ASSERT(sizeof(ql_gentity_t) == 0x0384, "gentity_t size");

QL_STATIC_ASSERT(offsetof(ql_level_locals_t, clients) == 0x0000, "level_locals_t.clients offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, gentities) == 0x0004, "level_locals_t.gentities offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, reserved_0008) == 0x0008, "level_locals_t.reserved_0008 offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, num_entities) == 0x000C, "level_locals_t.num_entities offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, warmupTime) == 0x0010, "level_locals_t.warmupTime offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, logFile) == 0x0014, "level_locals_t.logFile offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, maxclients) == 0x0018, "level_locals_t.maxclients offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, time) == 0x001C, "level_locals_t.time offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, msec) == 0x0020, "level_locals_t.msec offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, startTime) == 0x0024, "level_locals_t.startTime offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, teamScores) == 0x0028, "level_locals_t.teamScores offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, lastTeamLocationTime) == 0x0038, "level_locals_t.lastTeamLocationTime offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, newSession) == 0x003C, "level_locals_t.newSession offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, restarted) == 0x0040, "level_locals_t.restarted offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, numConnectedClients) == 0x004C, "level_locals_t.numConnectedClients offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, numNonSpectatorClients) == 0x0050, "level_locals_t.numNonSpectatorClients offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, numPlayingClients) == 0x0054, "level_locals_t.numPlayingClients offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, readyUpEligibleClients) == 0x0058, "level_locals_t.readyUpEligibleClients offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, readyUpReadyClients) == 0x005C, "level_locals_t.readyUpReadyClients offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, sortedClients) == 0x0064, "level_locals_t.sortedClients offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, follow1) == 0x0164, "level_locals_t.follow1 offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, follow2) == 0x0168, "level_locals_t.follow2 offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, snd_fry) == 0x016C, "level_locals_t.snd_fry offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, warmupModificationCount) == 0x0170, "level_locals_t.warmupModificationCount offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, voteString) == 0x0174, "level_locals_t.voteString offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, voteDisplayString) == 0x0574, "level_locals_t.voteDisplayString offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, voteExecuteTime) == 0x0974, "level_locals_t.voteExecuteTime offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, voteTime) == 0x0978, "level_locals_t.voteTime offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, voteYes) == 0x097C, "level_locals_t.voteYes offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, voteNo) == 0x0980, "level_locals_t.voteNo offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, pendingVoteClientNum) == 0x0984, "level_locals_t.pendingVoteClientNum offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, spawning) == 0x0988, "level_locals_t.spawning offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, numSpawnVars) == 0x098C, "level_locals_t.numSpawnVars offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, spawnVars) == 0x0990, "level_locals_t.spawnVars offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, numSpawnVarChars) == 0x0B90, "level_locals_t.numSpawnVarChars offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, spawnVarChars) == 0x0B94, "level_locals_t.spawnVarChars offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, intermissionQueued) == 0x1B94, "level_locals_t.intermissionQueued offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, intermissiontime) == 0x1B98, "level_locals_t.intermissiontime offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, intermissionExitStatusLatched) == 0x1BA0, "level_locals_t.intermissionExitStatusLatched offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, intermission_origin) == 0x1BA8, "level_locals_t.intermission_origin offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, intermission_angle) == 0x1BB4, "level_locals_t.intermission_angle offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, locationLinked) == 0x1BC0, "level_locals_t.locationLinked offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, locationHead) == 0x1BC4, "level_locals_t.locationHead offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, timeoutStartTime) == 0x1BC8, "level_locals_t.timeoutStartTime offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, overtimeAccumulatedMsec) == 0x1BCC, "level_locals_t.overtimeAccumulatedMsec offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, teamItemInitialSpawnDelaySeconds) == 0x1BD0, "level_locals_t.teamItemInitialSpawnDelaySeconds offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, powerupInitialSpawnDelaySeconds) == 0x1BD4, "level_locals_t.powerupInitialSpawnDelaySeconds offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, bodyQueIndex) == 0x1BD8, "level_locals_t.bodyQueIndex offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, bodyQue) == 0x1BDC, "level_locals_t.bodyQue offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, portalSequence) == 0x1BFC, "level_locals_t.portalSequence offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, postmatchSummaryLatched) == 0x1C00, "level_locals_t.postmatchSummaryLatched offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, trainingMapActive) == 0x1C04, "level_locals_t.trainingMapActive offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, duelScoreboardLowClientNum) == 0x1C08, "level_locals_t.duelScoreboardLowClientNum offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, duelScoreboardHighClientNum) == 0x1C0C, "level_locals_t.duelScoreboardHighClientNum offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, matchForfeited) == 0x4B84, "level_locals_t.matchForfeited offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, readyUpDelayDeadline) == 0x4B88, "level_locals_t.readyUpDelayDeadline offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, lastLeadChangeTime) == 0x4B94, "level_locals_t.lastLeadChangeTime offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, lastLeadToken) == 0x4B98, "level_locals_t.lastLeadToken offset");
QL_STATIC_ASSERT(sizeof(ql_level_locals_t) == 0x4B9C, "level_locals_t size");

#undef QL_STATIC_ASSERT

#ifdef __cplusplus
}
#endif

#endif // QUAKE_LIVE_GAME_TYPES_H
