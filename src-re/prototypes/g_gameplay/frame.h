#ifndef QLR_PROTO_GAME_FRAME_H
#define QLR_PROTO_GAME_FRAME_H

#include "../common/native_shim.h"

#include "../include/ql_types.h"

void QLR_Game_BindFrameContext(qlr_game_frame_context_t *ctx);
void QLR_Game_UnbindFrameContext(void);
void G_RunFrame(int levelTime);

#endif /* QLR_PROTO_GAME_FRAME_H */
