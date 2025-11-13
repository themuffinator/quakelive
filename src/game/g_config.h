#ifndef G_CONFIG_H
#define G_CONFIG_H

#include "../code/game/q_shared.h"

extern vmCvar_t g_startingWeapons;
extern vmCvar_t g_infiniteAmmo;
extern vmCvar_t g_ammoPack;
extern vmCvar_t g_ammoPackHack;
extern vmCvar_t g_ammoRespawn;
extern vmCvar_t g_startingHealth;
extern vmCvar_t g_startingHealthBonus;
extern vmCvar_t g_startingArmor;

extern vmCvar_t g_ammoPack_bfg;
extern vmCvar_t g_ammoPack_cg;
extern vmCvar_t g_ammoPack_gl;
extern vmCvar_t g_ammoPack_hmg;
extern vmCvar_t g_ammoPack_lg;
extern vmCvar_t g_ammoPack_mg;
extern vmCvar_t g_ammoPack_ng;
extern vmCvar_t g_ammoPack_pg;
extern vmCvar_t g_ammoPack_pl;
extern vmCvar_t g_ammoPack_rg;
extern vmCvar_t g_ammoPack_rl;
extern vmCvar_t g_ammoPack_sg;

extern vmCvar_t g_startingAmmo_bfg;
extern vmCvar_t g_startingAmmo_cg;
extern vmCvar_t g_startingAmmo_g;
extern vmCvar_t g_startingAmmo_gh;
extern vmCvar_t g_startingAmmo_gl;
extern vmCvar_t g_startingAmmo_hmg;
extern vmCvar_t g_startingAmmo_lg;
extern vmCvar_t g_startingAmmo_mg;
extern vmCvar_t g_startingAmmo_ng;
extern vmCvar_t g_startingAmmo_pg;
extern vmCvar_t g_startingAmmo_pl;
extern vmCvar_t g_startingAmmo_rg;
extern vmCvar_t g_startingAmmo_rl;
extern vmCvar_t g_startingAmmo_sg;

extern vmCvar_t g_timeoutLen;
extern vmCvar_t g_timeoutCount;
extern vmCvar_t g_overtime;
extern vmCvar_t g_suddenDeathRespawn;
extern vmCvar_t g_suddenDeathRespawnStart;
extern vmCvar_t g_suddenDeathRespawnTick;
extern vmCvar_t g_suddenDeathRespawnMax;
extern vmCvar_t g_suddenDeathRespawnIncrement;
extern vmCvar_t g_suddenDeathRespawnPrint;

typedef struct matchFactoryConfig_s {
	int		timeoutLengthSeconds;
	int		timeoutCountPerTeam;
	int		overtimeLengthSeconds;
	qboolean	suddenDeathRespawnsEnabled;
	int		suddenDeathStartSeconds;
	int		suddenDeathTickSeconds;
	int		suddenDeathMaxSeconds;
	int		suddenDeathIncrementSeconds;
	qboolean	suddenDeathPrintAnnouncements;
	qboolean	suddenDeathSpawnDelayActive;
} matchFactoryConfig_t;

void G_Config_RegisterCvars( void );
void G_Config_UpdateCvars( void );

#endif // G_CONFIG_H
