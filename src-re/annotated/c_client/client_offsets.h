#ifndef QLR_CLIENT_OFFSETS_H
#define QLR_CLIENT_OFFSETS_H

#include <stddef.h>

#include "../include/ql_types.h"

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
