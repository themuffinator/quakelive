#ifndef QLR_GAME_PMOVE_H
#define QLR_GAME_PMOVE_H

#include "qlr_recon_shared.h"

typedef struct qlr_pmove_s qlr_pmove_t;
typedef struct qlr_pmove_locals_s qlr_pmove_locals_t;

struct qlr_game_pmove_context_s;

typedef void (*qlr_game_pmove_event_hook_t)(struct qlr_game_pmove_context_s *ctx, int new_event);
typedef void (*qlr_game_pmove_touch_hook_t)(struct qlr_game_pmove_context_s *ctx, int entity_num);
typedef void (*qlr_game_pmove_step_hook_t)(struct qlr_game_pmove_context_s *ctx);
typedef bool (*qlr_game_pmove_check_jump_hook_t)(struct qlr_game_pmove_context_s *ctx, bool allowAirDoubleJump);
typedef void (*qlr_game_pmove_process_hook_t)(struct qlr_game_pmove_context_s *ctx, qlr_pmove_t *pmove);

typedef struct qlr_game_pmove_hooks_s {
	qlr_game_pmove_event_hook_t add_event;
	qlr_game_pmove_touch_hook_t add_touch_entity;
	qlr_game_pmove_step_hook_t air_move;
	qlr_game_pmove_step_hook_t water_move;
	qlr_game_pmove_step_hook_t walk_move;
	qlr_game_pmove_check_jump_hook_t check_jump;
	qlr_game_pmove_step_hook_t weapon;
	qlr_game_pmove_process_hook_t process_move;
} qlr_game_pmove_hooks_t;

typedef struct qlr_game_pmove_context_s {
	qlr_pmove_t *pm;
	qlr_pmove_locals_t *locals;
	qlr_game_pmove_hooks_t hooks;
} qlr_game_pmove_context_t;

void QLR_Game_BindPmoveContext(qlr_game_pmove_context_t *ctx);
void QLR_Game_UnbindPmoveContext(void);

void PM_AddEvent(int new_event);
void PM_AddTouchEnt(int entity_num);
void PM_AirMove(void);
void PM_WaterMove(void);
void PM_WalkMove(void);
bool PM_CheckJump(bool allowAirDoubleJump);
void PM_Weapon(void);
void Pmove(qlr_pmove_t *pmove);

#endif /* QLR_GAME_PMOVE_H */
