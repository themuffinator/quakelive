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
	ql_gclient_t *	clients;		// 0x0000
	ql_gentity_t *	gentities;		// 0x0004
	int32_t gentity_size;			// 0x0008
	int32_t	gclient_size;		// 0x000C
	int32_t	maxclients;		// 0x0010
	int32_t	framenum;		// 0x0014
	int32_t	time;		// 0x0018
	int32_t	previousTime;		// 0x001C
	int32_t	field_0020;		// 0x0020
	int32_t	field_0024;		// 0x0024
	int32_t	field_0028;		// 0x0028
	int32_t	field_002c;		// 0x002C
	int32_t	field_0030;		// 0x0030
	uint8_t __pad0034[0x0004];
	int32_t	field_0038;		// 0x0038
	int32_t	field_003c;		// 0x003C
	int32_t	field_0040;		// 0x0040
	int32_t	field_0044;		// 0x0044
	int32_t	field_0048;		// 0x0048
	int32_t	field_004c;		// 0x004C
	int32_t	field_0050;		// 0x0050
	int32_t	field_0054;		// 0x0054
	int32_t	field_0058;		// 0x0058
	int32_t	field_005c;		// 0x005C
	int32_t	field_0060;		// 0x0060
	int32_t	field_0064;		// 0x0064
	int32_t	field_0068;		// 0x0068
	uint8_t __pad006c[0x00F8];
	int32_t	follow1;		// 0x0164
	int32_t	follow2;		// 0x0168
	int32_t	snd_fry;		// 0x016C
	int32_t	field_0170;		// 0x0170
	int32_t	field_0174;		// 0x0174
	uint8_t __pad0178[0x07FC];
	int32_t	field_0974;		// 0x0974
	int32_t	field_0978;		// 0x0978
	int32_t	field_097c;		// 0x097C
	int32_t	field_0980;		// 0x0980
	int32_t	field_0984;		// 0x0984
	int32_t	field_0988;		// 0x0988
	int32_t	field_098c;		// 0x098C
	int32_t	field_0990;		// 0x0990
	int32_t	field_0994;		// 0x0994
	uint8_t __pad0998[0x01F8];
	int32_t	field_0b90;		// 0x0B90
	uint8_t __pad0b94[0x1000];
	int32_t	field_1b94;		// 0x1B94
	int32_t	field_1b98;		// 0x1B98
	int32_t	field_1b9c;		// 0x1B9C
	int32_t	field_1ba0;		// 0x1BA0
	int32_t	field_1ba4;		// 0x1BA4
	int32_t	field_1ba8;		// 0x1BA8
	int32_t	field_1bac;		// 0x1BAC
	int32_t	field_1bb0;		// 0x1BB0
	int32_t	field_1bb4;		// 0x1BB4
	int32_t	field_1bb8;		// 0x1BB8
	int32_t	field_1bbc;		// 0x1BBC
	int32_t	field_1bc0;		// 0x1BC0
	int32_t	field_1bc4;		// 0x1BC4
	int32_t	field_1bc8;		// 0x1BC8
	int32_t	field_1bcc;		// 0x1BCC
	int32_t	field_1bd0;		// 0x1BD0
	int32_t	field_1bd4;		// 0x1BD4
	int32_t	field_1bd8;		// 0x1BD8
	int32_t	field_1bdc;		// 0x1BDC
	uint8_t __pad1be0[0x001C];
	int32_t	field_1bfc;		// 0x1BFC
	int32_t	field_1c00;		// 0x1C00
	int32_t	field_1c04;		// 0x1C04
	int32_t	field_1c08;		// 0x1C08
	int32_t	field_1c0c;		// 0x1C0C
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
	int32_t	field_4b84;		// 0x4B84
	int32_t	field_4b88;		// 0x4B88
	int32_t	field_4b8c;		// 0x4B8C
	int32_t	field_4b90;		// 0x4B90
	int32_t	field_4b94;		// 0x4B94
	int32_t	field_4b98;		// 0x4B98
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
QL_STATIC_ASSERT(sizeof(ql_level_locals_t) == 0x4B9C, "level_locals_t size");

#undef QL_STATIC_ASSERT

#ifdef __cplusplus
}
#endif

#endif // QUAKE_LIVE_GAME_TYPES_H
