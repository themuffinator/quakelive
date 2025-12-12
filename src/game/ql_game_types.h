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

typedef struct ql_gclient_s {
	uint8_t player_state_and_linkage[0x250];	// 0x000 (ps/entity linkage cleared on spawn)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41211-L41218】
	int32_t pers_connected;				// 0x250 (connection state initialised in ClientConnect/Begin)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41117-L41124】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41211-L41213】
	uint8_t pers_block[0x2C0 - 0x254];		// 0x254 persistent fields preserved across warmup
	uint32_t steam_id_low;				// 0x2C0 (Steam64 low from engine callback)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41118-L41123】
	uint32_t steam_id_high;			// 0x2C4 (Steam64 high from engine callback)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41118-L41123】
	int32_t pers_max_health;			// 0x2C8 (handicap-capped max health mirrored into ps stats)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L40982-L41003】
	uint8_t pers_pad[0x2D8 - 0x2CC];		// 0x2CC reserved pers/session fields
	int32_t session_restart_bookmark0;		// 0x2D8 (rejoin bookmark reset to -1 on spawn)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41219-L41224】
	int32_t session_restart_bookmark1;		// 0x2DC (paired bookmark cleared with session reset)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41219-L41224】
	uint8_t session_pad[0x2F4 - 0x2E0];		// 0x2E0 session state carried between restarts
	int32_t session_enter_time;			// 0x2F4 (level time stamped during ClientBegin)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41211-L41215】
	int32_t timeout_reset_time;			// 0x2F8 (vote/timeout window cleared when spawning)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41213-L41216】
	uint8_t timeout_pad[0x32C - 0x2FC];	// 0x2FC placeholders for mirrored ps values
	int32_t timeout_throttle;			// 0x32C (timeout/invite throttle zeroed on Begin)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41213-L41216】
	uint8_t session_state_pad[0x348 - 0x330];	// 0x330 transition bookkeeping
	int32_t session_team;				// 0x348 (sess.team inspected for reconnect handling)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41216-L41221】
	uint8_t ban_pad[0x368 - 0x34C];		// 0x34C punishment/session metadata (_time64 when absent)
	int64_t ban_timestamp;			// 0x368 (ban expiry stored for localhost bypass)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41155-L41159】
	uint8_t warmup_pad[0x3B8 - 0x370];		// 0x370 match timing mirrors updated on Begin
	int32_t award_restart_marker0;		// 0x3B8 (award/stat reset marker set to -1)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41221-L41224】
	int32_t award_restart_marker1;		// 0x3BC (paired marker cleared with session reset)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41221-L41224】
	uint8_t award_and_stat_block[0x568 - 0x3C0];	// 0x3C0 award trackers and stat mirrors (cleared during ClientConnect)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41124-L41131】
	int32_t command_time_seed;			// 0x568 (randomised command clock seed)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41126-L41132】
	int32_t command_time_base;			// 0x56C (level.time snapshot for command seed window)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41127-L41130】
	int32_t command_time_delta;			// 0x570 (delta between server time and last command)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41127-L41130】
	uint8_t roster_pad[0x578 - 0x574];		// 0x574 alignment gap for roster tracking
	int32_t restart_queue_position;		// 0x578 (queue slot assigned while rebuilding teams)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L12299-L12313】
	int32_t restart_queue_rejoin;		// 0x57C (flag noting reuse of prior slot)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L12305-L12313】
	int32_t team_seed_rank;			// 0x580 (per-team seed used when pairing same opponents)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L12314-L12329】
	int32_t team_seed_reused;			// 0x584 (whether the team seed came from a prior match)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L12320-L12329】
	uint8_t weapon_and_award_stats[0xBD8 - 0x588];	// 0x588 rolling weapon stats/awards (zeroed on connect)【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41124-L41131】
} ql_gclient_t;

// Documented offsets lifted from references/hlil/quakelive/qagamex86.dll/
// sully_interpreted/structs/gentity_t.md so that this mirror stays aligned with
// the Sully interpretation of the retail qagame binary.
enum {
    QL_GENTITY_OFFSET_R_SVFLAGS      = 0x068,
    QL_GENTITY_OFFSET_SVFLAGS_EXT    = 0x1E0,
    QL_GENTITY_OFFSET_CLIENT         = 0x23C,
    QL_GENTITY_OFFSET_CONNECTED      = 0x240,
    QL_GENTITY_OFFSET_COMMAND_TIME   = 0x27C,
    QL_GENTITY_OFFSET_WARMUP_TIMEOUT = 0x32C,
    QL_GENTITY_SIZE_BYTES            = 0x384
};

typedef struct ql_gentity_s {
    uint8_t __pad0[QL_GENTITY_OFFSET_R_SVFLAGS];
    int32_t r_svFlags;                 // 0x068
    uint8_t __pad1[QL_GENTITY_OFFSET_SVFLAGS_EXT -
                   (QL_GENTITY_OFFSET_R_SVFLAGS + sizeof(int32_t))];
    int32_t svFlagsExt;                // 0x1E0
    uint8_t __pad2[QL_GENTITY_OFFSET_CLIENT -
                   (QL_GENTITY_OFFSET_SVFLAGS_EXT + sizeof(int32_t))];
    ql_gclient_t *client;              // 0x23C
    int32_t connected;                 // 0x240
    uint8_t __pad3[QL_GENTITY_OFFSET_COMMAND_TIME -
                   (QL_GENTITY_OFFSET_CONNECTED + sizeof(int32_t))];
    int32_t command_time_mirror;       // 0x27C
    uint8_t __pad4[QL_GENTITY_OFFSET_WARMUP_TIMEOUT -
                   (QL_GENTITY_OFFSET_COMMAND_TIME + sizeof(int32_t))];
    int32_t warmup_timeout_state;      // 0x32C
    uint8_t __pad5[QL_GENTITY_SIZE_BYTES -
                   (QL_GENTITY_OFFSET_WARMUP_TIMEOUT + sizeof(int32_t))];
} ql_gentity_t;

typedef struct ql_level_locals_s {
    ql_gclient_t *clients;             // 0x0000
    ql_gentity_t *gentities;           // 0x0004
    int32_t gentity_size;              // 0x0008
    int32_t gclient_size;              // 0x000C
    int32_t maxclients;                // 0x0010
    int32_t framenum;                  // 0x0014
    int32_t time;                      // 0x0018
    int32_t previousTime;              // 0x001C
    uint8_t __pad0[0x134 - 0x020];
    int32_t logFile;                   // 0x0134
    uint8_t __pad1[0x1C0 - 0x138];
    int32_t warmup_restart_latch;      // 0x01C0
    uint8_t __pad2[0x4B9C - 0x1C4];
} ql_level_locals_t;

typedef ql_gclient_t gclient_t;
typedef ql_gentity_t gentity_t;
typedef ql_level_locals_t level_locals_t;


#if defined(__cplusplus)
#define QL_STATIC_ASSERT(cond, msg) static_assert(cond, msg)
#elif defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
#define QL_STATIC_ASSERT(cond, msg) _Static_assert(cond, msg)
#else
#define QL_STATIC_ASSERT(cond, msg) typedef char static_assertion_##__LINE__[(cond) ? 1 : -1]
#endif

QL_STATIC_ASSERT(offsetof(ql_gclient_t, player_state_and_linkage) == 0x000, "gclient_t.player_state_and_linkage offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, pers_connected) == 0x250, "gclient_t.pers_connected offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, steam_id_low) == 0x2C0, "gclient_t.steam_id_low offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, steam_id_high) == 0x2C4, "gclient_t.steam_id_high offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, pers_max_health) == 0x2C8, "gclient_t.pers_max_health offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, session_restart_bookmark0) == 0x2D8, "gclient_t.session_restart_bookmark0 offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, session_restart_bookmark1) == 0x2DC, "gclient_t.session_restart_bookmark1 offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, session_enter_time) == 0x2F4, "gclient_t.session_enter_time offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, timeout_reset_time) == 0x2F8, "gclient_t.timeout_reset_time offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, timeout_throttle) == 0x32C, "gclient_t.timeout_throttle offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, session_team) == 0x348, "gclient_t.session_team offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, ban_timestamp) == 0x368, "gclient_t.ban_timestamp offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, award_restart_marker0) == 0x3B8, "gclient_t.award_restart_marker0 offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, command_time_seed) == 0x568, "gclient_t.command_time_seed offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, command_time_base) == 0x56C, "gclient_t.command_time_base offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, command_time_delta) == 0x570, "gclient_t.command_time_delta offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, restart_queue_position) == 0x578, "gclient_t.restart_queue_position offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, restart_queue_rejoin) == 0x57C, "gclient_t.restart_queue_rejoin offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, team_seed_rank) == 0x580, "gclient_t.team_seed_rank offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, weapon_and_award_stats) == 0x588, "gclient_t.weapon_and_award_stats offset");
QL_STATIC_ASSERT(sizeof(ql_gclient_t) == 0x0BD8, "gclient_t size");

QL_STATIC_ASSERT(offsetof(ql_gentity_t, r_svFlags) == 0x068, "gentity_t.r_svFlags offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, svFlagsExt) == 0x1E0, "gentity_t.svFlagsExt offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, client) == 0x23C, "gentity_t.client offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, connected) == 0x240, "gentity_t.connected offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, command_time_mirror) == 0x27C, "gentity_t.command_time_mirror offset");
QL_STATIC_ASSERT(offsetof(ql_gentity_t, warmup_timeout_state) == 0x32C, "gentity_t.warmup_timeout_state offset");
QL_STATIC_ASSERT(sizeof(ql_gentity_t) == 0x0384, "gentity_t size");

QL_STATIC_ASSERT(offsetof(ql_level_locals_t, clients) == 0x0000, "level_locals_t.clients offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, gentities) == 0x0004, "level_locals_t.gentities offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, gentity_size) == 0x0008, "level_locals_t.gentity_size offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, gclient_size) == 0x000C, "level_locals_t.gclient_size offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, maxclients) == 0x0010, "level_locals_t.maxclients offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, framenum) == 0x0014, "level_locals_t.framenum offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, time) == 0x0018, "level_locals_t.time offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, previousTime) == 0x001C, "level_locals_t.previousTime offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, logFile) == 0x0134, "level_locals_t.logFile offset");
QL_STATIC_ASSERT(offsetof(ql_level_locals_t, warmup_restart_latch) == 0x01C0, "level_locals_t.warmup_restart_latch offset");
QL_STATIC_ASSERT(sizeof(ql_level_locals_t) == 0x4B9C, "level_locals_t size");

#undef QL_STATIC_ASSERT

#ifdef __cplusplus
}
#endif

#endif // QUAKE_LIVE_GAME_TYPES_H
