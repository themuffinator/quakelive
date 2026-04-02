#ifndef QLR_PROTO_CLIENT_FRAME_H
#define QLR_PROTO_CLIENT_FRAME_H

#include "../common/native_shim.h"

#include "../../include/ql_types.h"

void QLR_ClientFrame_BindContext(qlr_client_frame_context_t *ctx);
void QLR_ClientFrame_UnbindContext(void);
void CL_Frame(int msec);

#endif /* QLR_PROTO_CLIENT_FRAME_H */
