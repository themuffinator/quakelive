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
    uint8_t __pad0[0x2C0];
    uint32_t steam_id_low;             // 0x2C0
    uint32_t steam_id_high;            // 0x2C4
    int32_t pers_max_health;           // 0x2C8
    uint8_t __pad1[0x2D8 - 0x2CC];
    int32_t session_restart_bookmark0; // 0x2D8
    int32_t session_restart_bookmark1; // 0x2DC
    uint8_t __pad2[0x32C - 0x2E0];
    int32_t timeout_throttle;          // 0x32C
    uint8_t __pad3[0x348 - 0x330];
    int32_t session_team;              // 0x348
    uint8_t __pad4[0x368 - 0x34C];
    int64_t ban_timestamp;             // 0x368
    uint8_t __pad5[0x568 - 0x370];
    int32_t command_time_seed;         // 0x568
    uint8_t __pad6[0xBD8 - 0x56C];
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

QL_STATIC_ASSERT(offsetof(ql_gclient_t, steam_id_low) == 0x2C0, "gclient_t.steam_id_low offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, steam_id_high) == 0x2C4, "gclient_t.steam_id_high offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, pers_max_health) == 0x2C8, "gclient_t.pers_max_health offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, session_restart_bookmark0) == 0x2D8, "gclient_t.session_restart_bookmark0 offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, session_restart_bookmark1) == 0x2DC, "gclient_t.session_restart_bookmark1 offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, timeout_throttle) == 0x32C, "gclient_t.timeout_throttle offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, session_team) == 0x348, "gclient_t.session_team offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, ban_timestamp) == 0x368, "gclient_t.ban_timestamp offset");
QL_STATIC_ASSERT(offsetof(ql_gclient_t, command_time_seed) == 0x568, "gclient_t.command_time_seed offset");
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
