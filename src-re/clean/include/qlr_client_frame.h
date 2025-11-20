#ifndef QLR_CLIENT_FRAME_H
#define QLR_CLIENT_FRAME_H

#include "qlr_recon_shared.h"

typedef enum {
    QLR_CLIENT_STATE_UNINITIALIZED = -1,
    QLR_CLIENT_STATE_DISCONNECTED = 0,
    QLR_CLIENT_STATE_CONNECTING = 1,
    QLR_CLIENT_STATE_CHALLENGING = 2,
    QLR_CLIENT_STATE_CONNECTED = 3,
    QLR_CLIENT_STATE_PRIMED = 4,
    QLR_CLIENT_STATE_ACTIVE = 5,
    QLR_CLIENT_STATE_CINEMATIC = 6
} qlr_client_state_t;

typedef struct qlr_client_static_s {
    bool renderer_started;
    bool sound_started;
    bool sound_registered;
    bool ui_started;
    bool cd_dialog;
    qlr_client_state_t state;
    int key_catchers;
    qlr_recon_timer_t clock;
} qlr_client_static_t;

typedef struct qlr_client_active_s {
    int timeout_count;
    int server_time;
} qlr_client_active_t;

typedef struct qlr_client_connection_s {
    bool demo_recording;
    bool demo_waiting;
    bool demo_playing;
    int last_packet_time;
    int time_demo_start;
    int time_demo_frames;
} qlr_client_connection_t;

typedef struct qlr_client_frame_cvars_s {
    qlr_recon_cvar_t *com_cl_running;
    qlr_recon_cvar_t *cl_avidemo;
    qlr_recon_cvar_t *cl_forceavidemo;
    qlr_recon_cvar_t *com_timescale;
    qlr_recon_cvar_t *cl_paused;
    qlr_recon_cvar_t *sv_paused;
    qlr_recon_cvar_t *com_sv_running;
} qlr_client_frame_cvars_t;

typedef struct qlr_client_frame_hooks_s {
void (*stop_all_sounds)(void);
void (*set_active_menu)(int menu_id);
void (*check_timeout)(qlr_client_connection_t *clc, qlr_client_static_t *cls, qlr_client_active_t *cl);
void (*check_userinfo)(void);
void (*read_packets)(void);
void (*send_cmd)(void);
void (*check_for_resend)(void);
void (*predict_movement)(void);
void (*run_console)(void);
void (*update_screen)(void);
void (*sound_update)(void);
void (*set_cgame_time)(void);
void (*begin_profiling)(void);
} qlr_client_frame_hooks_t;

typedef struct qlr_client_frame_context_s {
	qlr_client_static_t *cls;
	qlr_client_active_t *cl;
	qlr_client_connection_t *clc;
	qlr_client_frame_cvars_t cvars;
	qlr_client_frame_hooks_t hooks;
} qlr_client_frame_context_t;

void QLR_ClientFrame_BindContext(qlr_client_frame_context_t *ctx);
void QLR_ClientFrame_UnbindContext(void);
void CL_Frame(int msec);

#endif /* QLR_CLIENT_FRAME_H */
