#include <stddef.h>

#include "../../src-re/include/ql_types.h"

_Static_assert(sizeof(qlr_cl_snapshot_t) == 0x1B4, "qlr_cl_snapshot_t size drift");
_Static_assert(_Alignof(qlr_cl_snapshot_t) == 4, "qlr_cl_snapshot_t alignment");
_Static_assert(offsetof(qlr_cl_snapshot_t, playerState) == 0x3C, "playerState offset");
_Static_assert(offsetof(qlr_cl_snapshot_t, numEntities) == 0x1A8, "numEntities offset");

_Static_assert(sizeof(qlr_client_timing_window_t) == 0x1CC,
               "qlr_client_timing_window_t size drift");
_Static_assert(_Alignof(qlr_client_timing_window_t) == 4,
               "qlr_client_timing_window_t alignment");
_Static_assert(offsetof(qlr_client_timing_window_t, serverTimeDelta) == 0x1C0,
               "serverTimeDelta offset");

_Static_assert(sizeof(qlr_client_static_shadow_t) == 32,
               "client_static_shadow size drift");
_Static_assert(_Alignof(qlr_client_static_shadow_t) == 4,
               "client_static_shadow alignment");
_Static_assert(offsetof(qlr_client_static_shadow_t, state) == 8,
               "client_static_shadow state offset");

_Static_assert(sizeof(qlr_client_connection_shadow_t) == 28,
               "client_connection_shadow size drift");
_Static_assert(_Alignof(qlr_client_connection_shadow_t) == 4,
               "client_connection_shadow alignment");

_Static_assert(sizeof(qlr_client_frame_cvars_t) ==
                   16 * sizeof(qlr_cvar_shadow_t *),
               "client_frame_cvars pointer packing");

_Static_assert(offsetof(qlr_client_frame_context_t, hooks) ==
                   offsetof(qlr_client_frame_context_t, cvars) +
                       sizeof(qlr_client_frame_cvars_t),
               "client_frame_context layout");

_Static_assert(sizeof(qlr_gentity_t) >= sizeof(bool) + 3 * sizeof(void *) +
                                         2 * sizeof(int),
               "gentity trimmed size drift");
_Static_assert(_Alignof(qlr_gentity_t) == _Alignof(void *),
               "gentity alignment");

_Static_assert(_Alignof(qlr_game_frame_context_t) == _Alignof(void *),
               "game_frame_context alignment");
_Static_assert(offsetof(qlr_game_frame_context_t, hooks) ==
                   offsetof(qlr_game_frame_context_t, entity_count) +
                       sizeof(size_t),
               "game_frame_context hooks offset");
