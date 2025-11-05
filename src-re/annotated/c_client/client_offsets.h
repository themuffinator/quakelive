#ifndef QLR_CLIENT_OFFSETS_H
#define QLR_CLIENT_OFFSETS_H

#include <stddef.h>
#include <stdint.h>

/*
 * The annotated shims keep small mirrors of key Quake Live data structures so
 * that offsets and field widths can be referenced without pulling in the full
 * GPL headers.  Each typedef mirrors the packed layout that CL_Frame and the
 * snapshot interpolation code touch.
 */

typedef struct {
    int32_t valid;              /* qboolean in the original engine */
    int32_t snapFlags;
    int32_t serverTime;
    int32_t messageNum;
    int32_t deltaNum;
    int32_t ping;
    uint8_t areamask[32];       /* MAX_MAP_AREA_BYTES in baseq3 */
    int32_t cmdNum;
    /* playerState_t is large; we only expose its size for offset tables. */
    uint8_t playerState[0x16C];
    int32_t numEntities;
    int32_t parseEntitiesNum;
    int32_t serverCommandNum;
} qlr_cl_snapshot_t; /* sizeof == 0x1D4 (468) with the trimmed playerState */

typedef struct {
    qlr_cl_snapshot_t latest;
    int32_t serverTime;
    int32_t oldServerTime;
    int32_t oldFrameServerTime;
    int32_t serverTimeDelta;
    int32_t extrapolatedSnapshot;    /* qboolean */
    int32_t newSnapshots;            /* qboolean */
} qlr_client_timing_window_t;

typedef struct {
    const char *fieldName;
    uint16_t offset;
    uint16_t size;
} qlr_field_offset_t;

#define QLR_OFFSET_INFO(type, member)                                             \
    { #member, (uint16_t)offsetof(type, member), (uint16_t)sizeof(((type *)0)->member) }

static const qlr_field_offset_t qlr_snapshot_core_offsets[] = {
    QLR_OFFSET_INFO(qlr_cl_snapshot_t, valid),
    QLR_OFFSET_INFO(qlr_cl_snapshot_t, snapFlags),
    QLR_OFFSET_INFO(qlr_cl_snapshot_t, serverTime),
    QLR_OFFSET_INFO(qlr_cl_snapshot_t, messageNum),
    QLR_OFFSET_INFO(qlr_cl_snapshot_t, deltaNum),
    QLR_OFFSET_INFO(qlr_cl_snapshot_t, ping),
    QLR_OFFSET_INFO(qlr_cl_snapshot_t, cmdNum),
    QLR_OFFSET_INFO(qlr_cl_snapshot_t, playerState),
    QLR_OFFSET_INFO(qlr_cl_snapshot_t, numEntities),
    QLR_OFFSET_INFO(qlr_cl_snapshot_t, parseEntitiesNum),
    QLR_OFFSET_INFO(qlr_cl_snapshot_t, serverCommandNum),
};

static const qlr_field_offset_t qlr_timing_window_offsets[] = {
    QLR_OFFSET_INFO(qlr_client_timing_window_t, latest.serverTime),
    QLR_OFFSET_INFO(qlr_client_timing_window_t, serverTime),
    QLR_OFFSET_INFO(qlr_client_timing_window_t, oldServerTime),
    QLR_OFFSET_INFO(qlr_client_timing_window_t, oldFrameServerTime),
    QLR_OFFSET_INFO(qlr_client_timing_window_t, serverTimeDelta),
};

#endif /* QLR_CLIENT_OFFSETS_H */
