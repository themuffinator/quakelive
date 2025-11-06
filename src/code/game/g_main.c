/*
===========================================================================
Copyright (C) 1999-2005 Id Software, Inc.

This file is part of Quake III Arena source code.

Quake III Arena source code is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Quake III Arena source code is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
===========================================================================
*/
//

#include "g_local.h"
#include <time.h>

level_locals_t	level;
weaponConfig_t	g_weaponConfig;

weaponReloadConfig_t	g_weaponReloadConfig;
knockbackConfig_t	g_knockbackConfig;
startingAmmoConfig_t	g_startingAmmoConfig;
#define STRINGIZE_HELPER( x ) #x
#define STRINGIZE( x ) STRINGIZE_HELPER( x )

#define DEFAULT_STARTING_AMMO_BFG           10      // Quake Live default (data_1007e194 -> "10").
#define DEFAULT_STARTING_AMMO_CG            100     // Quake Live default (data_1007e154 -> "100").
#define DEFAULT_STARTING_AMMO_G             -1      // Quake Live default (data_100875ec -> "-1").
#define DEFAULT_STARTING_AMMO_GH            -1      // Quake Live default (data_100875ec -> "-1").
#define DEFAULT_STARTING_AMMO_GL            10      // Quake Live default (data_1007e194 -> "10").
#define DEFAULT_STARTING_AMMO_HMG           50      // Quake Live default (data_1007e1fc -> "50").
#define DEFAULT_STARTING_AMMO_LG            100     // Quake Live default (data_1007e154 -> "100").
#define DEFAULT_STARTING_AMMO_MG            100     // Quake Live default (data_1007e154 -> "100").
#define DEFAULT_STARTING_AMMO_NG            10      // Quake Live default (data_1007e194 -> "10").
#define DEFAULT_STARTING_AMMO_PG            50      // Quake Live default (data_1007e1fc -> "50").
#define DEFAULT_STARTING_AMMO_PL            5       // Quake Live default (data_10087340 -> "5").
#define DEFAULT_STARTING_AMMO_RG            5       // Quake Live default (data_10087340 -> "5").
#define DEFAULT_STARTING_AMMO_RL            5       // Quake Live default (data_10087340 -> "5").
#define DEFAULT_STARTING_AMMO_SG            10      // Quake Live default (data_1007e194 -> "10").

#define DEFAULT_WEAPON_RELOAD_BFG           300     // Quake Live default (data_10085968 -> "300").
#define DEFAULT_WEAPON_RELOAD_CG            50      // Quake Live default (data_1007e1fc -> "50").
#define DEFAULT_WEAPON_RELOAD_GAUNTLET      400     // Quake Live default (data_10087355 -> "400").
#define DEFAULT_WEAPON_RELOAD_GH            100     // Quake Live default (data_1007e154 -> "100").
#define DEFAULT_WEAPON_RELOAD_GL            800     // Quake Live default (data_10086cbc -> "800").
#define DEFAULT_WEAPON_RELOAD_HMG           75      // Quake Live default (data_100870d2 -> "75").
#define DEFAULT_WEAPON_RELOAD_HOOK          100     // Quake Live default (data_1007e154 -> "100").
#define DEFAULT_WEAPON_RELOAD_LG            50      // Quake Live default (data_1007e1fc -> "50").
#define DEFAULT_WEAPON_RELOAD_MG            100     // Quake Live default (data_1007e154 -> "100").
#define DEFAULT_WEAPON_RELOAD_NG            1000    // Quake Live default (data_1008747c -> "1000").
#define DEFAULT_WEAPON_RELOAD_PG            100     // Quake Live default (data_1007e154 -> "100").
#define DEFAULT_WEAPON_RELOAD_PROX          800     // Quake Live default (data_10086cbc -> "800").
#define DEFAULT_WEAPON_RELOAD_RG            1500    // Quake Live default (data_10086760 -> "1500").
#define DEFAULT_WEAPON_RELOAD_RL            800     // Quake Live default (data_10086cbc -> "800").
#define DEFAULT_WEAPON_RELOAD_SG            1000    // Quake Live default (data_1008747c -> "1000").

#define DEFAULT_KNOCKBACK_BFG               1.0     // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_1007d1d8 -> "1").
#define DEFAULT_KNOCKBACK_CG                1.0     // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_1007d1d8 -> "1").
#define DEFAULT_KNOCKBACK_G                 1.0     // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_1007d1d8 -> "1").
#define DEFAULT_KNOCKBACK_GH                -5.0    // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_10086b93 -> "-5").
#define DEFAULT_KNOCKBACK_GL                1.10    // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_10086b7c -> "1.10").
#define DEFAULT_KNOCKBACK_HMG               1.0     // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_1007d1d8 -> "1").
#define DEFAULT_KNOCKBACK_LG                1.75    // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_10086b54 -> "1.75").
#define DEFAULT_KNOCKBACK_MG                1.0     // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_1007d1d8 -> "1").
#define DEFAULT_KNOCKBACK_NG                1.0     // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_1007d1d8 -> "1").
#define DEFAULT_KNOCKBACK_PG                1.10    // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_10086b7c -> "1.10").
#define DEFAULT_KNOCKBACK_PG_SELF           1.30    // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_10086b1c -> "1.30").
#define DEFAULT_KNOCKBACK_PL                1.0     // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_1007d1d8 -> "1").
#define DEFAULT_KNOCKBACK_RG                0.85    // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_10086af4 -> "0.85").
#define DEFAULT_KNOCKBACK_RL                0.90    // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_10086adc -> "0.90").
#define DEFAULT_KNOCKBACK_RL_SELF           1.10    // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_10086b7c -> "1.10").
#define DEFAULT_KNOCKBACK_SG                1.0     // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_1007d1d8 -> "1").
#define DEFAULT_KNOCKBACK_VERTICAL          24.0    // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_10086ab7 -> "24").
#define DEFAULT_KNOCKBACK_VERTICAL_SELF     24.0    // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_10086ab7 -> "24").
#define DEFAULT_KNOCKBACK_CRIPPLE           0.0     // Quake Live default (references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_part02.txt data_1007d0a8 -> "0").

#define DEFAULT_AMMOPACK_BFG                15
#define DEFAULT_AMMOPACK_CG                 100
#define DEFAULT_AMMOPACK_GL                 5
#define DEFAULT_AMMOPACK_HMG                50
#define DEFAULT_AMMOPACK_LG                 60
#define DEFAULT_AMMOPACK_MG                 50
#define DEFAULT_AMMOPACK_NG                 20
#define DEFAULT_AMMOPACK_PG                 30
#define DEFAULT_AMMOPACK_PL                 10
#define DEFAULT_AMMOPACK_RG                 10
#define DEFAULT_AMMOPACK_RL                 5
#define DEFAULT_AMMOPACK_SG                 10

typedef struct {
	vmCvar_t	*vmCvar;
	char		*cvarName;
	char		*defaultString;
	int			cvarFlags;
	int			modificationCount;  // for tracking changes
	qboolean	trackChange;	    // track this variable, and announce if changed
	qboolean	teamShader;	    // track and if changed, update shader state
	const char	*helpString; // optional help text advertised alongside the cvar
} cvarTable_t;

gentity_t		g_entities[MAX_GENTITIES];
gclient_t		g_clients[MAX_CLIENTS];

vmCvar_t	g_gametype;
vmCvar_t	g_dmflags;
vmCvar_t	g_fraglimit;
vmCvar_t	g_timelimit;
vmCvar_t	g_capturelimit;
vmCvar_t	g_friendlyFire;
vmCvar_t	g_password;
vmCvar_t	g_needpass;
vmCvar_t	g_maxclients;
vmCvar_t	g_maxGameClients;
vmCvar_t	g_dedicated;
vmCvar_t	g_speed;
vmCvar_t	g_gravity;
vmCvar_t	g_cheats;
vmCvar_t	g_knockback;
vmCvar_t	g_knockback_g;
vmCvar_t	g_knockback_mg;
vmCvar_t	g_knockback_sg;
vmCvar_t	g_knockback_gl;
vmCvar_t	g_knockback_rl;
vmCvar_t	g_knockback_rl_self;
vmCvar_t	g_knockback_lg;
vmCvar_t	g_knockback_rg;
vmCvar_t	g_knockback_pg;
vmCvar_t	g_knockback_pg_self;
vmCvar_t	g_knockback_bfg;
vmCvar_t	g_knockback_gh;
vmCvar_t	g_knockback_ng;
vmCvar_t	g_knockback_pl;
vmCvar_t	g_knockback_cg;
vmCvar_t	g_knockback_hmg;
vmCvar_t	g_knockback_z;
vmCvar_t	g_knockback_z_self;
vmCvar_t	g_max_knockback;
vmCvar_t	g_knockback_cripple;
vmCvar_t	g_quadfactor;
vmCvar_t	g_forcerespawn;
vmCvar_t	g_inactivity;
vmCvar_t	g_debugMove;
vmCvar_t	g_debugDamage;
vmCvar_t	g_debugAlloc;
vmCvar_t	g_weaponRespawn;
vmCvar_t	g_weaponTeamRespawn;
vmCvar_t	g_motd;
vmCvar_t	g_synchronousClients;
vmCvar_t	g_warmup;
vmCvar_t	g_doWarmup;
vmCvar_t	g_restarted;
vmCvar_t	g_log;
vmCvar_t	g_logSync;
vmCvar_t	g_blood;
vmCvar_t	g_podiumDist;
vmCvar_t	g_podiumDrop;
vmCvar_t	g_allowVote;
vmCvar_t	g_teamAutoJoin;
vmCvar_t	g_teamForceBalance;
vmCvar_t	g_banIPs;
vmCvar_t	g_filterBan;
vmCvar_t	g_smoothClients;
vmCvar_t	pmove_fixed;
vmCvar_t	pmove_msec;
vmCvar_t	g_rankings;
vmCvar_t	g_listEntity;
vmCvar_t	g_damage_gauntlet;
vmCvar_t	g_damage_mg;
vmCvar_t	g_damage_mg_team;
vmCvar_t	g_damage_sg;
vmCvar_t	g_damage_gl;
vmCvar_t	g_splashDamage_gl;
vmCvar_t	g_splashRadius_gl;
vmCvar_t	g_damage_rl;
vmCvar_t	g_splashDamage_rl;
vmCvar_t	g_splashRadius_rl;
vmCvar_t	g_damage_pg;
vmCvar_t	g_splashDamage_pg;
vmCvar_t	g_splashRadius_pg;
vmCvar_t	g_damage_lg;
vmCvar_t	g_damage_rg;
vmCvar_t	g_damage_bfg;
vmCvar_t	g_splashDamage_bfg;
vmCvar_t	g_splashRadius_bfg;
vmCvar_t	weapon_reload_gauntlet;
vmCvar_t	weapon_reload_mg;
vmCvar_t	weapon_reload_sg;
vmCvar_t	weapon_reload_gl;
vmCvar_t	weapon_reload_rl;
vmCvar_t	weapon_reload_lg;
vmCvar_t	weapon_reload_rg;
vmCvar_t	weapon_reload_pg;
vmCvar_t	weapon_reload_bfg;
vmCvar_t	weapon_reload_gh;
vmCvar_t	weapon_reload_hook;
vmCvar_t	weapon_reload_ng;
vmCvar_t	weapon_reload_prox;
vmCvar_t	weapon_reload_cg;
vmCvar_t	weapon_reload_hmg;
vmCvar_t	g_ammoPack_bfg;
vmCvar_t	g_ammoPack_cg;
vmCvar_t	g_ammoPack_gl;
vmCvar_t	g_ammoPack_hmg;
vmCvar_t	g_ammoPack_lg;
vmCvar_t	g_ammoPack_mg;
vmCvar_t	g_ammoPack_ng;
vmCvar_t	g_ammoPack_pg;
vmCvar_t	g_ammoPack_pl;
vmCvar_t	g_ammoPack_rg;
vmCvar_t	g_ammoPack_rl;
vmCvar_t	g_ammoPack_sg;
vmCvar_t	g_startingAmmo_bfg;
vmCvar_t	g_startingAmmo_cg;
vmCvar_t	g_startingAmmo_g;
vmCvar_t	g_startingAmmo_gh;
vmCvar_t	g_startingAmmo_gl;
vmCvar_t	g_startingAmmo_hmg;
vmCvar_t	g_startingAmmo_lg;
vmCvar_t	g_startingAmmo_mg;
vmCvar_t	g_startingAmmo_ng;
vmCvar_t	g_startingAmmo_pg;
vmCvar_t	g_startingAmmo_pl;
vmCvar_t	g_startingAmmo_rg;
vmCvar_t	g_startingAmmo_rl;
vmCvar_t	g_startingAmmo_sg;
#ifdef MISSIONPACK
vmCvar_t	g_obeliskHealth;
vmCvar_t	g_obeliskRegenPeriod;
vmCvar_t	g_obeliskRegenAmount;
vmCvar_t	g_obeliskRespawnDelay;
vmCvar_t	g_cubeTimeout;
vmCvar_t	g_redteam;
vmCvar_t	g_blueteam;
vmCvar_t	g_singlePlayer;
vmCvar_t	g_enableDust;
vmCvar_t	g_enableBreath;
vmCvar_t	g_proxMineTimeout;
#endif

// bk001129 - made static to avoid aliasing
static cvarTable_t		gameCvarTable[] = {
	// don't override the cheat state set by the system
	{ &g_cheats, "sv_cheats", "", 0, 0, qfalse },

	// noset vars
	{ NULL, "gamename", GAMEVERSION , CVAR_SERVERINFO | CVAR_ROM, 0, qfalse  },
	{ NULL, "gamedate", __DATE__ , CVAR_ROM, 0, qfalse  },
	{ &g_restarted, "g_restarted", "0", CVAR_ROM, 0, qfalse  },
	{ NULL, "sv_mapname", "", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse  },

	// latched vars
	{ &g_gametype, "g_gametype", "0", CVAR_SERVERINFO | CVAR_USERINFO | CVAR_LATCH, 0, qfalse  },

	{ &g_maxclients, "sv_maxclients", "8", CVAR_SERVERINFO | CVAR_LATCH | CVAR_ARCHIVE, 0, qfalse  },
	{ &g_maxGameClients, "g_maxGameClients", "0", CVAR_SERVERINFO | CVAR_LATCH | CVAR_ARCHIVE, 0, qfalse  },

	// change anytime vars
	{ &g_dmflags, "dmflags", "0", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qtrue  },
	{ &g_fraglimit, "fraglimit", "20", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },
	{ &g_timelimit, "timelimit", "0", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },
	{ &g_capturelimit, "capturelimit", "8", CVAR_SERVERINFO | CVAR_ARCHIVE | CVAR_NORESTART, 0, qtrue },

	{ &g_synchronousClients, "g_synchronousClients", "0", CVAR_SYSTEMINFO, 0, qfalse  },

	{ &g_friendlyFire, "g_friendlyFire", "0", CVAR_ARCHIVE, 0, qtrue  },

	{ &g_teamAutoJoin, "g_teamAutoJoin", "0", CVAR_ARCHIVE  },
	{ &g_teamForceBalance, "g_teamForceBalance", "0", CVAR_ARCHIVE  },

	{ &g_warmup, "g_warmup", "20", CVAR_ARCHIVE, 0, qtrue  },
	{ &g_doWarmup, "g_doWarmup", "0", 0, 0, qtrue  },
	{ &g_log, "g_log", "games.log", CVAR_ARCHIVE, 0, qfalse  },
	{ &g_logSync, "g_logSync", "0", CVAR_ARCHIVE, 0, qfalse  },

	{ &g_password, "g_password", "", CVAR_USERINFO, 0, qfalse  },

	{ &g_banIPs, "g_banIPs", "", CVAR_ARCHIVE, 0, qfalse  },
	{ &g_filterBan, "g_filterBan", "1", CVAR_ARCHIVE, 0, qfalse  },

	{ &g_needpass, "g_needpass", "0", CVAR_SERVERINFO | CVAR_ROM, 0, qfalse },

	{ &g_dedicated, "dedicated", "0", 0, 0, qfalse  },

	{ &g_speed, "g_speed", "320", 0, 0, qtrue  },
	{ &g_gravity, "g_gravity", "800", 0, 0, qtrue  },
	{ &g_knockback, "g_knockback", "1000", 0, 0, qtrue  },
	{ &g_knockback_g, "g_knockback_g", STRINGIZE( DEFAULT_KNOCKBACK_G ), 0, 0, qfalse, qfalse, "Gauntlet knockback scalar applied when striking other players." },
	{ &g_knockback_mg, "g_knockback_mg", STRINGIZE( DEFAULT_KNOCKBACK_MG ), 0, 0, qfalse, qfalse, "Machinegun knockback scalar applied to outgoing hits." },
	{ &g_knockback_sg, "g_knockback_sg", STRINGIZE( DEFAULT_KNOCKBACK_SG ), 0, 0, qfalse, qfalse, "Shotgun knockback scalar for pellets that land on opponents." },
	{ &g_knockback_gl, "g_knockback_gl", STRINGIZE( DEFAULT_KNOCKBACK_GL ), 0, 0, qfalse, qfalse, "Grenade Launcher knockback scalar applied to direct and splash damage." },
	{ &g_knockback_rl, "g_knockback_rl", STRINGIZE( DEFAULT_KNOCKBACK_RL ), 0, 0, qfalse, qfalse, "Rocket Launcher knockback scalar for enemies struck by rockets." },
	{ &g_knockback_rl_self, "g_knockback_rl_self", STRINGIZE( DEFAULT_KNOCKBACK_RL_SELF ), 0, 0, qfalse, qfalse, "Self-inflicted rocket knockback scalar used for rocket jumps." },
	{ &g_knockback_lg, "g_knockback_lg", STRINGIZE( DEFAULT_KNOCKBACK_LG ), 0, 0, qfalse, qfalse, "Lightning Gun knockback scalar." },
	{ &g_knockback_rg, "g_knockback_rg", STRINGIZE( DEFAULT_KNOCKBACK_RG ), 0, 0, qfalse, qfalse, "Railgun knockback scalar." },
	{ &g_knockback_pg, "g_knockback_pg", STRINGIZE( DEFAULT_KNOCKBACK_PG ), 0, 0, qfalse, qfalse, "Plasmagun knockback scalar for opponents." },
	{ &g_knockback_pg_self, "g_knockback_pg_self", STRINGIZE( DEFAULT_KNOCKBACK_PG_SELF ), 0, 0, qfalse, qfalse, "Self-inflicted plasmagun knockback scalar." },
	{ &g_knockback_bfg, "g_knockback_bfg", STRINGIZE( DEFAULT_KNOCKBACK_BFG ), 0, 0, qfalse, qfalse, "BFG knockback scalar." },
	{ &g_knockback_gh, "g_knockback_gh", STRINGIZE( DEFAULT_KNOCKBACK_GH ), 0, 0, qfalse, qfalse, "Grappling Hook knockback scalar." },
	{ &g_knockback_ng, "g_knockback_ng", STRINGIZE( DEFAULT_KNOCKBACK_NG ), 0, 0, qfalse, qfalse, "Nailgun knockback scalar." },
	{ &g_knockback_pl, "g_knockback_pl", STRINGIZE( DEFAULT_KNOCKBACK_PL ), 0, 0, qfalse, qfalse, "Proximity Launcher knockback scalar." },
	{ &g_knockback_cg, "g_knockback_cg", STRINGIZE( DEFAULT_KNOCKBACK_CG ), 0, 0, qfalse, qfalse, "Chaingun knockback scalar." },
	{ &g_knockback_hmg, "g_knockback_hmg", STRINGIZE( DEFAULT_KNOCKBACK_HMG ), 0, 0, qfalse, qfalse, "Heavy Machinegun knockback scalar." },
	{ &g_knockback_z, "g_knockback_z", STRINGIZE( DEFAULT_KNOCKBACK_VERTICAL ), 0, 0, qfalse, qfalse, "Vertical knockback boost added after weapon scaling." },
	{ &g_knockback_z_self, "g_knockback_z_self", STRINGIZE( DEFAULT_KNOCKBACK_VERTICAL_SELF ), 0, 0, qfalse, qfalse, "Vertical knockback boost when you knock yourself back." },
	{ &g_max_knockback, "g_max_knockback", "200", 0, 0, qfalse, qfalse, "Upper clamp applied to computed knockback force." },
	{ &g_knockback_cripple, "g_knockback_cripple", STRINGIZE( DEFAULT_KNOCKBACK_CRIPPLE ), 0, 0, qfalse, qfalse, "Additional knockback scalar consumed by cripple modifiers." },
	{ &g_quadfactor, "g_quadfactor", "3", 0, 0, qtrue  },
	{ &g_weaponRespawn, "g_weaponrespawn", "5", 0, 0, qtrue  },
	{ &g_weaponTeamRespawn, "g_weaponTeamRespawn", "30", 0, 0, qtrue },
	{ &g_forcerespawn, "g_forcerespawn", "20", 0, 0, qtrue },
	{ &g_inactivity, "g_inactivity", "0", 0, 0, qtrue },
	{ &g_debugMove, "g_debugMove", "0", 0, 0, qfalse },
	{ &g_debugDamage, "g_debugDamage", "0", 0, 0, qfalse },
	{ &g_debugAlloc, "g_debugAlloc", "0", 0, 0, qfalse },
	{ &g_motd, "g_motd", "", 0, 0, qfalse },
	{ &g_blood, "com_blood", "1", 0, 0, qfalse },

	{ &g_podiumDist, "g_podiumDist", "80", 0, 0, qfalse },
	{ &g_podiumDrop, "g_podiumDrop", "70", 0, 0, qfalse },

	{ &g_allowVote, "g_allowVote", "1", CVAR_ARCHIVE, 0, qfalse },
	{ &g_listEntity, "g_listEntity", "0", 0, 0, qfalse },
	{ &g_damage_gauntlet, "g_damage_gauntlet", "50", 0, 0, qtrue },
	{ &g_damage_mg, "g_damage_mg", "7", 0, 0, qtrue },
	{ &g_damage_mg_team, "g_damage_mg_team", "5", 0, 0, qtrue },
	{ &g_damage_sg, "g_damage_sg", "10", 0, 0, qtrue },
	{ &g_damage_gl, "g_damage_gl", "100", 0, 0, qtrue },
	{ &g_splashDamage_gl, "g_splashDamage_gl", "100", 0, 0, qtrue },
	{ &g_splashRadius_gl, "g_splashRadius_gl", "150", 0, 0, qtrue },
	{ &g_damage_rl, "g_damage_rl", "100", 0, 0, qtrue },
	{ &g_splashDamage_rl, "g_splashDamage_rl", "100", 0, 0, qtrue },
	{ &g_splashRadius_rl, "g_splashRadius_rl", "120", 0, 0, qtrue },
	{ &g_damage_pg, "g_damage_pg", "20", 0, 0, qtrue },
	{ &g_splashDamage_pg, "g_splashDamage_pg", "15", 0, 0, qtrue },
	{ &g_splashRadius_pg, "g_splashRadius_pg", "20", 0, 0, qtrue },
	{ &g_damage_lg, "g_damage_lg", "8", 0, 0, qtrue },
	{ &g_damage_rg, "g_damage_rg", "100", 0, 0, qtrue },
	{ &g_damage_bfg, "g_damage_bfg", "100", 0, 0, qtrue },
	{ &g_splashDamage_bfg, "g_splashDamage_bfg", "100", 0, 0, qtrue },
	{ &g_splashRadius_bfg, "g_splashRadius_bfg", "120", 0, 0, qtrue },

	{ &weapon_reload_gauntlet, "weapon_reload_gauntlet", "0", 0, 0, qfalse, qfalse, "Gauntlet refire delay override in milliseconds; 0 preserves the compiled behaviour." },
	{ &weapon_reload_mg, "weapon_reload_mg", "0", 0, 0, qfalse, qfalse, "Machinegun refire delay override in milliseconds; 0 keeps the built-in rate." },
	{ &weapon_reload_sg, "weapon_reload_sg", "0", 0, 0, qfalse, qfalse, "Shotgun refire delay override in milliseconds; 0 leaves the default timing." },
	{ &weapon_reload_gl, "weapon_reload_gl", "0", 0, 0, qfalse, qfalse, "Grenade Launcher refire delay override in milliseconds." },
	{ &weapon_reload_rl, "weapon_reload_rl", "0", 0, 0, qfalse, qfalse, "Rocket Launcher refire delay override in milliseconds." },
	{ &weapon_reload_lg, "weapon_reload_lg", "0", 0, 0, qfalse, qfalse, "Lightning Gun refire delay override in milliseconds." },
	{ &weapon_reload_rg, "weapon_reload_rg", "0", 0, 0, qfalse, qfalse, "Railgun refire delay override in milliseconds." },
	{ &weapon_reload_pg, "weapon_reload_pg", "0", 0, 0, qfalse, qfalse, "Plasma Gun refire delay override in milliseconds." },
	{ &weapon_reload_bfg, "weapon_reload_bfg", "0", 0, 0, qfalse, qfalse, "BFG refire delay override in milliseconds." },
	{ &weapon_reload_gh, "weapon_reload_gh", "0", 0, 0, qfalse, qfalse, "Grappling Hook refire delay override in milliseconds." },
	{ &weapon_reload_hook, "weapon_reload_hook", "0", 0, 0, qfalse, qfalse, "Hook pull refire delay override in milliseconds." },
	{ &weapon_reload_ng, "weapon_reload_ng", "0", 0, 0, qfalse, qfalse, "Nailgun refire delay override in milliseconds." },
	{ &weapon_reload_prox, "weapon_reload_prox", "0", 0, 0, qfalse, qfalse, "Proximity Launcher refire delay override in milliseconds." },
        { &weapon_reload_cg, "weapon_reload_cg", "0", 0, 0, qfalse, qfalse, "Chaingun refire delay override in milliseconds." },
        { &weapon_reload_hmg, "weapon_reload_hmg", "0", 0, 0, qfalse, qfalse, "Heavy Machinegun refire delay override in milliseconds." },

        { &g_ammoPack_bfg, "g_ammoPack_bfg", STRINGIZE( DEFAULT_AMMOPACK_BFG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Cells granted when picking up a BFG ammo pack, matching Quake Live's default drop." },
        { &g_ammoPack_cg, "g_ammoPack_cg", STRINGIZE( DEFAULT_AMMOPACK_CG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Chaingun bullets restored per ammo belt pickup." },
        { &g_ammoPack_gl, "g_ammoPack_gl", STRINGIZE( DEFAULT_AMMOPACK_GL ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Grenade Launcher rounds provided by grenade ammo packs." },
        { &g_ammoPack_hmg, "g_ammoPack_hmg", STRINGIZE( DEFAULT_AMMOPACK_HMG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Heavy Machinegun bullets added from heavy ammo packs." },
        { &g_ammoPack_lg, "g_ammoPack_lg", STRINGIZE( DEFAULT_AMMOPACK_LG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Lightning Gun cells awarded from lightning ammo pickups." },
        { &g_ammoPack_mg, "g_ammoPack_mg", STRINGIZE( DEFAULT_AMMOPACK_MG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Machinegun bullets restored by standard bullet boxes." },
        { &g_ammoPack_ng, "g_ammoPack_ng", STRINGIZE( DEFAULT_AMMOPACK_NG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Nailgun spikes issued from nail ammo packs." },
        { &g_ammoPack_pg, "g_ammoPack_pg", STRINGIZE( DEFAULT_AMMOPACK_PG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Plasmagun cells delivered with plasma ammo pickups." },
        { &g_ammoPack_pl, "g_ammoPack_pl", STRINGIZE( DEFAULT_AMMOPACK_PL ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Proximity Launcher mines granted from proximity ammo packs." },
        { &g_ammoPack_rg, "g_ammoPack_rg", STRINGIZE( DEFAULT_AMMOPACK_RG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Railgun slugs provided whenever a rail ammo pack is collected." },
        { &g_ammoPack_rl, "g_ammoPack_rl", STRINGIZE( DEFAULT_AMMOPACK_RL ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Rockets granted per rocket ammo box pickup." },
        { &g_ammoPack_sg, "g_ammoPack_sg", STRINGIZE( DEFAULT_AMMOPACK_SG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Shotgun shells restored with shell ammo packs." },

        { &g_startingAmmo_bfg, "g_startingAmmo_bfg", STRINGIZE( DEFAULT_STARTING_AMMO_BFG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Cells granted for the BFG whenever spawn loadouts (g_startingWeapons, factories, scripts) include it." },
	{ &g_startingAmmo_cg, "g_startingAmmo_cg", STRINGIZE( DEFAULT_STARTING_AMMO_CG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Chaingun bullets provided on spawn when the weapon is part of the configured loadout." },
	{ &g_startingAmmo_g, "g_startingAmmo_g", STRINGIZE( DEFAULT_STARTING_AMMO_G ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Gauntlet swings granted on spawn; -1 mirrors Quake Live's infinite melee behaviour." },
	{ &g_startingAmmo_gh, "g_startingAmmo_gh", STRINGIZE( DEFAULT_STARTING_AMMO_GH ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Grappling Hook ammo applied to players when scripts or factories grant the hook; -1 keeps it unlimited." },
	{ &g_startingAmmo_gl, "g_startingAmmo_gl", STRINGIZE( DEFAULT_STARTING_AMMO_GL ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Grenade Launcher rounds distributed at spawn when the launcher is granted via loadouts." },
	{ &g_startingAmmo_hmg, "g_startingAmmo_hmg", STRINGIZE( DEFAULT_STARTING_AMMO_HMG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Heavy Machinegun bullets issued alongside spawn loadouts that include the weapon." },
	{ &g_startingAmmo_lg, "g_startingAmmo_lg", STRINGIZE( DEFAULT_STARTING_AMMO_LG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Lightning Gun cells assigned when loadouts or scripts give the Lightning Gun on spawn." },
	{ &g_startingAmmo_mg, "g_startingAmmo_mg", STRINGIZE( DEFAULT_STARTING_AMMO_MG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Machinegun bullets supplied on spawn for any loadout that awards the Machinegun." },
	{ &g_startingAmmo_ng, "g_startingAmmo_ng", STRINGIZE( DEFAULT_STARTING_AMMO_NG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Nailgun spikes given to players when factories or scripts seed the Nailgun." },
	{ &g_startingAmmo_pg, "g_startingAmmo_pg", STRINGIZE( DEFAULT_STARTING_AMMO_PG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Plasmagun cells granted at spawn when the Plasmagun is included in the starting set." },
	{ &g_startingAmmo_pl, "g_startingAmmo_pl", STRINGIZE( DEFAULT_STARTING_AMMO_PL ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Proximity Launcher mines provided to players when loadouts grant the launcher." },
	{ &g_startingAmmo_rg, "g_startingAmmo_rg", STRINGIZE( DEFAULT_STARTING_AMMO_RG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Railgun slugs applied on spawn when the Railgun is part of the configured loadout." },
	{ &g_startingAmmo_rl, "g_startingAmmo_rl", STRINGIZE( DEFAULT_STARTING_AMMO_RL ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Rockets handed out whenever spawn loadouts include the Rocket Launcher." },
	{ &g_startingAmmo_sg, "g_startingAmmo_sg", STRINGIZE( DEFAULT_STARTING_AMMO_SG ), CVAR_ARCHIVE, 0, qfalse, qfalse, "Shotgun shells distributed when the Shotgun is in the spawn weapon set." },

#ifdef MISSIONPACK
	{ &g_obeliskHealth, "g_obeliskHealth", "2500", 0, 0, qfalse },
	{ &g_obeliskRegenPeriod, "g_obeliskRegenPeriod", "1", 0, 0, qfalse },
	{ &g_obeliskRegenAmount, "g_obeliskRegenAmount", "15", 0, 0, qfalse },
	{ &g_obeliskRespawnDelay, "g_obeliskRespawnDelay", "10", CVAR_SERVERINFO, 0, qfalse },

	{ &g_cubeTimeout, "g_cubeTimeout", "30", 0, 0, qfalse },
	{ &g_redteam, "g_redteam", "Stroggs", CVAR_ARCHIVE | CVAR_SERVERINFO | CVAR_USERINFO , 0, qtrue, qtrue },
	{ &g_blueteam, "g_blueteam", "Pagans", CVAR_ARCHIVE | CVAR_SERVERINFO | CVAR_USERINFO , 0, qtrue, qtrue  },
	{ &g_singlePlayer, "ui_singlePlayerActive", "", 0, 0, qfalse, qfalse  },

	{ &g_enableDust, "g_enableDust", "0", CVAR_SERVERINFO, 0, qtrue, qfalse },
	{ &g_enableBreath, "g_enableBreath", "0", CVAR_SERVERINFO, 0, qtrue, qfalse },
	{ &g_proxMineTimeout, "g_proxMineTimeout", "20000", 0, 0, qfalse },
#endif
	{ &g_smoothClients, "g_smoothClients", "1", 0, 0, qfalse},
	{ &pmove_fixed, "pmove_fixed", "0", CVAR_SYSTEMINFO, 0, qfalse},
	{ &pmove_msec, "pmove_msec", "8", CVAR_SYSTEMINFO, 0, qfalse},

	{ &g_rankings, "g_rankings", "0", 0, 0, qfalse}

};

// bk001129 - made static to avoid aliasing
static int gameCvarTableSize = sizeof( gameCvarTable ) / sizeof( gameCvarTable[0] );

static void G_RegisterCvarHelp( const cvarTable_t *cv ) {
	char helpName[MAX_CVAR_VALUE_STRING];

	if ( !cv->helpString || !cv->helpString[0] || !cv->cvarName ) {
		return;
	}

	Com_sprintf( helpName, sizeof( helpName ), "helptext_%s", cv->cvarName );
	trap_Cvar_Register( NULL, helpName, cv->helpString, CVAR_ROM );
}

static void G_ReportMissingCvar( const char *cvarName ) {
        if ( !cvarName || !cvarName[0] ) {
                return;
        }

        G_Printf( "WARNING: gameplay config cvar %s is unavailable; using fallback value\n", cvarName );
}

static int G_ReadWeaponCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
        if ( !cvar ) {
                G_ReportMissingCvar( cvarName );
                return fallback;
        }

        if ( cvar->integer <= 0 ) {
                return fallback;
        }

        return cvar->integer;
}

void G_InitWeaponConfig( void ) {
	g_weaponConfig.gauntletDamage = G_ReadWeaponCvar( &g_damage_gauntlet, 50, "g_damage_gauntlet" );
	g_weaponConfig.machinegunDamage = G_ReadWeaponCvar( &g_damage_mg, 7, "g_damage_mg" );
	g_weaponConfig.machinegunTeamDamage = G_ReadWeaponCvar( &g_damage_mg_team, 5, "g_damage_mg_team" );
	g_weaponConfig.shotgunDamage = G_ReadWeaponCvar( &g_damage_sg, 10, "g_damage_sg" );
	g_weaponConfig.grenadeDamage = G_ReadWeaponCvar( &g_damage_gl, 100, "g_damage_gl" );
	g_weaponConfig.grenadeSplashDamage = G_ReadWeaponCvar( &g_splashDamage_gl, 100, "g_splashDamage_gl" );
	g_weaponConfig.grenadeSplashRadius = G_ReadWeaponCvar( &g_splashRadius_gl, 150, "g_splashRadius_gl" );
	g_weaponConfig.rocketDamage = G_ReadWeaponCvar( &g_damage_rl, 100, "g_damage_rl" );
	g_weaponConfig.rocketSplashDamage = G_ReadWeaponCvar( &g_splashDamage_rl, 100, "g_splashDamage_rl" );
	g_weaponConfig.rocketSplashRadius = G_ReadWeaponCvar( &g_splashRadius_rl, 120, "g_splashRadius_rl" );
	g_weaponConfig.plasmaDamage = G_ReadWeaponCvar( &g_damage_pg, 20, "g_damage_pg" );
	g_weaponConfig.plasmaSplashDamage = G_ReadWeaponCvar( &g_splashDamage_pg, 15, "g_splashDamage_pg" );
	g_weaponConfig.plasmaSplashRadius = G_ReadWeaponCvar( &g_splashRadius_pg, 20, "g_splashRadius_pg" );
	g_weaponConfig.lightningDamage = G_ReadWeaponCvar( &g_damage_lg, 8, "g_damage_lg" );
	g_weaponConfig.railgunDamage = G_ReadWeaponCvar( &g_damage_rg, 100, "g_damage_rg" );
	g_weaponConfig.bfgDamage = G_ReadWeaponCvar( &g_damage_bfg, 100, "g_damage_bfg" );
	g_weaponConfig.bfgSplashDamage = G_ReadWeaponCvar( &g_splashDamage_bfg, 100, "g_splashDamage_bfg" );
	g_weaponConfig.bfgSplashRadius = G_ReadWeaponCvar( &g_splashRadius_bfg, 120, "g_splashRadius_bfg" );
}

void G_UpdateWeaponConfig( void ) {
	G_InitWeaponConfig();
}

static int G_ReadWeaponReloadCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
        if ( !cvar ) {
                G_ReportMissingCvar( cvarName );
                return fallback;
        }

        if ( cvar->integer <= 0 ) {
                return fallback;
        }

        return cvar->integer;
}

static void G_BroadcastWeaponReloadConfig( void ) {
	static char lastBroadcast[MAX_STRING_CHARS];
	char buffer[MAX_STRING_CHARS];

	Com_sprintf( buffer, sizeof( buffer ), "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d",
		g_weaponReloadConfig.gauntlet,
		g_weaponReloadConfig.machinegun,
		g_weaponReloadConfig.shotgun,
		g_weaponReloadConfig.grenadeLauncher,
		g_weaponReloadConfig.rocketLauncher,
		g_weaponReloadConfig.lightningGun,
		g_weaponReloadConfig.railgun,
		g_weaponReloadConfig.plasmagun,
		g_weaponReloadConfig.bfg,
		g_weaponReloadConfig.grapplingHook,
		g_weaponReloadConfig.hook,
		g_weaponReloadConfig.nailgun,
		g_weaponReloadConfig.proximityLauncher,
		g_weaponReloadConfig.chaingun,
		g_weaponReloadConfig.heavyMachinegun );

	BG_SetWeaponReloadConfig( &g_weaponReloadConfig );

	if ( !Q_stricmp( buffer, lastBroadcast ) ) {
		return;
	}

	Q_strncpyz( lastBroadcast, buffer, sizeof( lastBroadcast ) );
	trap_SetConfigstring( CS_WEAPONRELOADS, buffer );
}


void G_InitWeaponReloadConfig( void ) {
        g_weaponReloadConfig.gauntlet = G_ReadWeaponReloadCvar( &weapon_reload_gauntlet, DEFAULT_WEAPON_RELOAD_GAUNTLET, "weapon_reload_gauntlet" );
        g_weaponReloadConfig.machinegun = G_ReadWeaponReloadCvar( &weapon_reload_mg, DEFAULT_WEAPON_RELOAD_MG, "weapon_reload_mg" );
        g_weaponReloadConfig.shotgun = G_ReadWeaponReloadCvar( &weapon_reload_sg, DEFAULT_WEAPON_RELOAD_SG, "weapon_reload_sg" );
        g_weaponReloadConfig.grenadeLauncher = G_ReadWeaponReloadCvar( &weapon_reload_gl, DEFAULT_WEAPON_RELOAD_GL, "weapon_reload_gl" );
        g_weaponReloadConfig.rocketLauncher = G_ReadWeaponReloadCvar( &weapon_reload_rl, DEFAULT_WEAPON_RELOAD_RL, "weapon_reload_rl" );
        g_weaponReloadConfig.lightningGun = G_ReadWeaponReloadCvar( &weapon_reload_lg, DEFAULT_WEAPON_RELOAD_LG, "weapon_reload_lg" );
        g_weaponReloadConfig.railgun = G_ReadWeaponReloadCvar( &weapon_reload_rg, DEFAULT_WEAPON_RELOAD_RG, "weapon_reload_rg" );
        g_weaponReloadConfig.plasmagun = G_ReadWeaponReloadCvar( &weapon_reload_pg, DEFAULT_WEAPON_RELOAD_PG, "weapon_reload_pg" );
        g_weaponReloadConfig.bfg = G_ReadWeaponReloadCvar( &weapon_reload_bfg, DEFAULT_WEAPON_RELOAD_BFG, "weapon_reload_bfg" );
        g_weaponReloadConfig.grapplingHook = G_ReadWeaponReloadCvar( &weapon_reload_gh, DEFAULT_WEAPON_RELOAD_GH, "weapon_reload_gh" );
        g_weaponReloadConfig.hook = G_ReadWeaponReloadCvar( &weapon_reload_hook, DEFAULT_WEAPON_RELOAD_HOOK, "weapon_reload_hook" );
        g_weaponReloadConfig.nailgun = G_ReadWeaponReloadCvar( &weapon_reload_ng, DEFAULT_WEAPON_RELOAD_NG, "weapon_reload_ng" );
        g_weaponReloadConfig.proximityLauncher = G_ReadWeaponReloadCvar( &weapon_reload_prox, DEFAULT_WEAPON_RELOAD_PROX, "weapon_reload_prox" );
        g_weaponReloadConfig.chaingun = G_ReadWeaponReloadCvar( &weapon_reload_cg, DEFAULT_WEAPON_RELOAD_CG, "weapon_reload_cg" );
        g_weaponReloadConfig.heavyMachinegun = G_ReadWeaponReloadCvar( &weapon_reload_hmg, DEFAULT_WEAPON_RELOAD_HMG, "weapon_reload_hmg" );

        // Share the resolved weapon_reload_* CVars with both prediction paths.
        G_BroadcastWeaponReloadConfig();
}

void G_UpdateWeaponReloadConfig( void ) {
	G_InitWeaponReloadConfig();
}

static int G_ReadStartingAmmoCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
        if ( !cvar ) {
                G_ReportMissingCvar( cvarName );
                return fallback;
        }

        return cvar->integer;
}

void G_InitStartingAmmoConfig( void ) {
	g_startingAmmoConfig.bfg = G_ReadStartingAmmoCvar( &g_startingAmmo_bfg, DEFAULT_STARTING_AMMO_BFG, "g_startingAmmo_bfg" );
	g_startingAmmoConfig.chaingun = G_ReadStartingAmmoCvar( &g_startingAmmo_cg, DEFAULT_STARTING_AMMO_CG, "g_startingAmmo_cg" );
	g_startingAmmoConfig.gauntlet = G_ReadStartingAmmoCvar( &g_startingAmmo_g, DEFAULT_STARTING_AMMO_G, "g_startingAmmo_g" );
	g_startingAmmoConfig.grapplingHook = G_ReadStartingAmmoCvar( &g_startingAmmo_gh, DEFAULT_STARTING_AMMO_GH, "g_startingAmmo_gh" );
	g_startingAmmoConfig.grenadeLauncher = G_ReadStartingAmmoCvar( &g_startingAmmo_gl, DEFAULT_STARTING_AMMO_GL, "g_startingAmmo_gl" );
	g_startingAmmoConfig.heavyMachinegun = G_ReadStartingAmmoCvar( &g_startingAmmo_hmg, DEFAULT_STARTING_AMMO_HMG, "g_startingAmmo_hmg" );
	g_startingAmmoConfig.lightningGun = G_ReadStartingAmmoCvar( &g_startingAmmo_lg, DEFAULT_STARTING_AMMO_LG, "g_startingAmmo_lg" );
	g_startingAmmoConfig.machinegun = G_ReadStartingAmmoCvar( &g_startingAmmo_mg, DEFAULT_STARTING_AMMO_MG, "g_startingAmmo_mg" );
	g_startingAmmoConfig.nailgun = G_ReadStartingAmmoCvar( &g_startingAmmo_ng, DEFAULT_STARTING_AMMO_NG, "g_startingAmmo_ng" );
	g_startingAmmoConfig.plasmagun = G_ReadStartingAmmoCvar( &g_startingAmmo_pg, DEFAULT_STARTING_AMMO_PG, "g_startingAmmo_pg" );
	g_startingAmmoConfig.proximityLauncher = G_ReadStartingAmmoCvar( &g_startingAmmo_pl, DEFAULT_STARTING_AMMO_PL, "g_startingAmmo_pl" );
	g_startingAmmoConfig.railgun = G_ReadStartingAmmoCvar( &g_startingAmmo_rg, DEFAULT_STARTING_AMMO_RG, "g_startingAmmo_rg" );
	g_startingAmmoConfig.rocketLauncher = G_ReadStartingAmmoCvar( &g_startingAmmo_rl, DEFAULT_STARTING_AMMO_RL, "g_startingAmmo_rl" );
	g_startingAmmoConfig.shotgun = G_ReadStartingAmmoCvar( &g_startingAmmo_sg, DEFAULT_STARTING_AMMO_SG, "g_startingAmmo_sg" );
}

void G_UpdateStartingAmmoConfig( void ) {
	G_InitStartingAmmoConfig();
}

static float G_ReadKnockbackCvar( const vmCvar_t *cvar, float fallback, const char *cvarName ) {
        if ( !cvar ) {
                G_ReportMissingCvar( cvarName );
                return fallback;
        }

        return cvar->value;
}

void G_InitKnockbackConfig( void ) {
        g_knockbackConfig.gauntlet = G_ReadKnockbackCvar( &g_knockback_g, DEFAULT_KNOCKBACK_G, "g_knockback_g" );
        g_knockbackConfig.machinegun = G_ReadKnockbackCvar( &g_knockback_mg, DEFAULT_KNOCKBACK_MG, "g_knockback_mg" );
        g_knockbackConfig.shotgun = G_ReadKnockbackCvar( &g_knockback_sg, DEFAULT_KNOCKBACK_SG, "g_knockback_sg" );
        g_knockbackConfig.grenadeLauncher = G_ReadKnockbackCvar( &g_knockback_gl, DEFAULT_KNOCKBACK_GL, "g_knockback_gl" );
        g_knockbackConfig.rocketLauncher = G_ReadKnockbackCvar( &g_knockback_rl, DEFAULT_KNOCKBACK_RL, "g_knockback_rl" );
        g_knockbackConfig.rocketLauncherSelf = G_ReadKnockbackCvar( &g_knockback_rl_self, DEFAULT_KNOCKBACK_RL_SELF, "g_knockback_rl_self" );
        g_knockbackConfig.lightningGun = G_ReadKnockbackCvar( &g_knockback_lg, DEFAULT_KNOCKBACK_LG, "g_knockback_lg" );
        g_knockbackConfig.railgun = G_ReadKnockbackCvar( &g_knockback_rg, DEFAULT_KNOCKBACK_RG, "g_knockback_rg" );
        g_knockbackConfig.plasmagun = G_ReadKnockbackCvar( &g_knockback_pg, DEFAULT_KNOCKBACK_PG, "g_knockback_pg" );
        g_knockbackConfig.plasmagunSelf = G_ReadKnockbackCvar( &g_knockback_pg_self, DEFAULT_KNOCKBACK_PG_SELF, "g_knockback_pg_self" );
        g_knockbackConfig.bfg = G_ReadKnockbackCvar( &g_knockback_bfg, DEFAULT_KNOCKBACK_BFG, "g_knockback_bfg" );
        g_knockbackConfig.grapplingHook = G_ReadKnockbackCvar( &g_knockback_gh, DEFAULT_KNOCKBACK_GH, "g_knockback_gh" );
        g_knockbackConfig.nailgun = G_ReadKnockbackCvar( &g_knockback_ng, DEFAULT_KNOCKBACK_NG, "g_knockback_ng" );
        g_knockbackConfig.proximityLauncher = G_ReadKnockbackCvar( &g_knockback_pl, DEFAULT_KNOCKBACK_PL, "g_knockback_pl" );
        g_knockbackConfig.chaingun = G_ReadKnockbackCvar( &g_knockback_cg, DEFAULT_KNOCKBACK_CG, "g_knockback_cg" );
        g_knockbackConfig.heavyMachinegun = G_ReadKnockbackCvar( &g_knockback_hmg, DEFAULT_KNOCKBACK_HMG, "g_knockback_hmg" );
        g_knockbackConfig.vertical = G_ReadKnockbackCvar( &g_knockback_z, DEFAULT_KNOCKBACK_VERTICAL, "g_knockback_z" );
        g_knockbackConfig.verticalSelf = G_ReadKnockbackCvar( &g_knockback_z_self, DEFAULT_KNOCKBACK_VERTICAL_SELF, "g_knockback_z_self" );

        {
                float maxKnockback = G_ReadKnockbackCvar( &g_max_knockback, 200.0f, "g_max_knockback" );

                if ( maxKnockback <= 0.0f ) {
                        maxKnockback = 200.0f;
                }

                g_knockbackConfig.maxKnockback = maxKnockback;
        }

        g_knockbackConfig.cripple = G_ReadKnockbackCvar( &g_knockback_cripple, DEFAULT_KNOCKBACK_CRIPPLE, "g_knockback_cripple" );
}

void G_UpdateKnockbackConfig( void ) {
        G_InitKnockbackConfig();
}


void G_InitGame( int levelTime, int randomSeed, int restart );
void G_RunFrame( int levelTime );
void G_ShutdownGame( int restart );
void CheckExitRules( void );


/*
================
vmMain

This is the only way control passes into the module.
This must be the very first function compiled into the .q3vm file
================
*/
int vmMain( int command, int arg0, int arg1, int arg2, int arg3, int arg4, int arg5, int arg6, int arg7, int arg8, int arg9, int arg10, int arg11  ) {
	switch ( command ) {
	case GAME_INIT:
		G_InitGame( arg0, arg1, arg2 );
		return 0;
	case GAME_SHUTDOWN:
		G_ShutdownGame( arg0 );
		return 0;
	case GAME_CLIENT_CONNECT:
		return (int)ClientConnect( arg0, arg1, arg2 );
	case GAME_CLIENT_THINK:
		ClientThink( arg0 );
		return 0;
	case GAME_CLIENT_USERINFO_CHANGED:
		ClientUserinfoChanged( arg0 );
		return 0;
	case GAME_CLIENT_DISCONNECT:
		ClientDisconnect( arg0 );
		return 0;
	case GAME_CLIENT_BEGIN:
		ClientBegin( arg0 );
		return 0;
	case GAME_CLIENT_COMMAND:
		ClientCommand( arg0 );
		return 0;
	case GAME_RUN_FRAME:
		G_RunFrame( arg0 );
		return 0;
	case GAME_CONSOLE_COMMAND:
		return ConsoleCommand();
	case BOTAI_START_FRAME:
		return BotAIStartFrame( arg0 );
	}

	return -1;
}


void QDECL G_Printf( const char *fmt, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, fmt);
	vsprintf (text, fmt, argptr);
	va_end (argptr);

	trap_Printf( text );
}

void QDECL G_Error( const char *fmt, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, fmt);
	vsprintf (text, fmt, argptr);
	va_end (argptr);

	trap_Error( text );
}

/*
================
G_FindTeams

Chain together all entities with a matching team field.
Entity teams are used for item groups and multi-entity mover groups.

All but the first will have the FL_TEAMSLAVE flag set and teammaster field set
All but the last will have the teamchain field set to the next one
================
*/
void G_FindTeams( void ) {
	gentity_t	*e, *e2;
	int		i, j;
	int		c, c2;

	c = 0;
	c2 = 0;
	for ( i=1, e=g_entities+i ; i < level.num_entities ; i++,e++ ){
		if (!e->inuse)
			continue;
		if (!e->team)
			continue;
		if (e->flags & FL_TEAMSLAVE)
			continue;
		e->teammaster = e;
		c++;
		c2++;
		for (j=i+1, e2=e+1 ; j < level.num_entities ; j++,e2++)
		{
			if (!e2->inuse)
				continue;
			if (!e2->team)
				continue;
			if (e2->flags & FL_TEAMSLAVE)
				continue;
			if (!strcmp(e->team, e2->team))
			{
				c2++;
				e2->teamchain = e->teamchain;
				e->teamchain = e2;
				e2->teammaster = e;
				e2->flags |= FL_TEAMSLAVE;

				// make sure that targets only point at the master
				if ( e2->targetname ) {
					e->targetname = e2->targetname;
					e2->targetname = NULL;
				}
			}
		}
	}

	G_Printf ("%i teams with %i entities\n", c, c2);
}

void G_RemapTeamShaders() {
#ifdef MISSIONPACK
	char string[1024];
	float f = level.time * 0.001;
	Com_sprintf( string, sizeof(string), "team_icon/%s_red", g_redteam.string );
	AddRemap("textures/ctf2/redteam01", string, f); 
	AddRemap("textures/ctf2/redteam02", string, f); 
	Com_sprintf( string, sizeof(string), "team_icon/%s_blue", g_blueteam.string );
	AddRemap("textures/ctf2/blueteam01", string, f); 
	AddRemap("textures/ctf2/blueteam02", string, f); 
	trap_SetConfigstring(CS_SHADERSTATE, BuildShaderStateConfig());
#endif
}


/*
=================
G_RegisterCvars
=================
*/
void G_RegisterCvars( void ) {
	int                     i;
	cvarTable_t     *cv;
	qboolean remapped = qfalse;

	for ( i = 0, cv = gameCvarTable ; i < gameCvarTableSize ; i++, cv++ ) {
		trap_Cvar_Register( cv->vmCvar, cv->cvarName,
		        cv->defaultString, cv->cvarFlags );
		G_RegisterCvarHelp( cv );
		if ( cv->vmCvar ) {
		        cv->modificationCount = cv->vmCvar->modificationCount;
		}

		if (cv->teamShader) {
		        remapped = qtrue;
		}
	}

	if (remapped) {
		G_RemapTeamShaders();
	}

	// check some things
	if ( g_gametype.integer < 0 || g_gametype.integer >= GT_MAX_GAME_TYPE ) {
		G_Printf( "g_gametype %i is out of range, defaulting to 0\n", g_gametype.integer );
		trap_Cvar_Set( "g_gametype", "0" );
	}

	level.warmupModificationCount = g_warmup.modificationCount;
	G_InitWeaponConfig();
	G_InitWeaponReloadConfig();
	G_InitKnockbackConfig();
	G_InitStartingAmmoConfig();
}

void G_UpdateCvars( void ) {
	int			i;
	cvarTable_t	*cv;
	qboolean remapped = qfalse;

	for ( i = 0, cv = gameCvarTable ; i < gameCvarTableSize ; i++, cv++ ) {
		if ( cv->vmCvar ) {
			trap_Cvar_Update( cv->vmCvar );

			if ( cv->modificationCount != cv->vmCvar->modificationCount ) {
				cv->modificationCount = cv->vmCvar->modificationCount;

				if ( cv->trackChange ) {
					trap_SendServerCommand( -1, va("print \"Server: %s changed to %s\n\"", 
						cv->cvarName, cv->vmCvar->string ) );
				}

				if (cv->teamShader) {
					remapped = qtrue;
				}
			}
		}
	}

	if (remapped) {
		G_RemapTeamShaders();
	}

	G_UpdateWeaponConfig();
	G_UpdateWeaponReloadConfig();
	G_UpdateKnockbackConfig();
	G_UpdateStartingAmmoConfig();
}

/*
============
G_InitGame

============
*/
void G_InitGame( int levelTime, int randomSeed, int restart ) {
	int					i;

	G_Printf ("------- Game Initialization -------\n");
	G_Printf ("gamename: %s\n", GAMEVERSION);
	G_Printf ("gamedate: %s\n", __DATE__);

	srand( randomSeed );
	{
		time_t levelStart = time( NULL );
		char startTimeBuffer[32];
		Com_sprintf( startTimeBuffer, sizeof( startTimeBuffer ), "%u", (unsigned int)levelStart );
		trap_Cvar_Set( "g_levelStartTime", startTimeBuffer );
	}


	G_RegisterCvars();

	G_ProcessIPBans();

	G_InitMemory();

	// set some level globals
	memset( &level, 0, sizeof( level ) );
	level.time = levelTime;
	level.startTime = levelTime;

	level.snd_fry = G_SoundIndex("sound/player/fry.wav");	// FIXME standing in lava / slime

	if ( g_gametype.integer != GT_SINGLE_PLAYER && g_log.string[0] ) {
		if ( g_logSync.integer ) {
			trap_FS_FOpenFile( g_log.string, &level.logFile, FS_APPEND_SYNC );
		} else {
			trap_FS_FOpenFile( g_log.string, &level.logFile, FS_APPEND );
		}
		if ( !level.logFile ) {
			G_Printf( "WARNING: Couldn't open logfile: %s\n", g_log.string );
		} else {
			char	serverinfo[MAX_INFO_STRING];

			trap_GetServerinfo( serverinfo, sizeof( serverinfo ) );

			G_LogPrintf("------------------------------------------------------------\n" );
			G_LogPrintf("InitGame: %s\n", serverinfo );
		}
	} else {
		G_Printf( "Not logging to disk.\n" );
	}

	G_InitWorldSession();

	// initialize all entities for this game
	memset( g_entities, 0, MAX_GENTITIES * sizeof(g_entities[0]) );
	level.gentities = g_entities;

	// initialize all clients for this game
	level.maxclients = g_maxclients.integer;
	memset( g_clients, 0, MAX_CLIENTS * sizeof(g_clients[0]) );
	level.clients = g_clients;

	// set client fields on player ents
	for ( i=0 ; i<level.maxclients ; i++ ) {
		g_entities[i].client = level.clients + i;
	}

	// always leave room for the max number of clients,
	// even if they aren't all used, so numbers inside that
	// range are NEVER anything but clients
	level.num_entities = MAX_CLIENTS;

	// let the server system know where the entites are
	trap_LocateGameData( level.gentities, level.num_entities, sizeof( gentity_t ), 
		&level.clients[0].ps, sizeof( level.clients[0] ) );

	// reserve some spots for dead player bodies
	InitBodyQue();

	ClearRegisteredItems();

	// parse the key/value pairs and spawn gentities
	G_SpawnEntitiesFromString();

	// general initialization
	G_FindTeams();

	// make sure we have flags for CTF, etc
	if( g_gametype.integer >= GT_TEAM ) {
		G_CheckTeamItems();
	}

	SaveRegisteredItems();

	G_Printf ("-----------------------------------\n");

	if( g_gametype.integer == GT_SINGLE_PLAYER || trap_Cvar_VariableIntegerValue( "com_buildScript" ) ) {
		G_ModelIndex( SP_PODIUM_MODEL );
		G_SoundIndex( "sound/player/gurp1.wav" );
		G_SoundIndex( "sound/player/gurp2.wav" );
	}

	if ( trap_Cvar_VariableIntegerValue( "bot_enable" ) ) {
		BotAISetup( restart );
		BotAILoadMap( restart );
		G_InitBots( restart );
	}

	G_RemapTeamShaders();

}



/*
=================
G_ShutdownGame
=================
*/
void G_ShutdownGame( int restart ) {
	G_Printf ("==== ShutdownGame ====\n");

	if ( level.logFile ) {
		G_LogPrintf("ShutdownGame:\n" );
		G_LogPrintf("------------------------------------------------------------\n" );
		trap_FS_FCloseFile( level.logFile );
	}

	// write all the client session data so we can get it back
	G_WriteSessionData();

	if ( trap_Cvar_VariableIntegerValue( "bot_enable" ) ) {
		BotAIShutdown( restart );
	}
}



//===================================================================

#ifndef GAME_HARD_LINKED
// this is only here so the functions in q_shared.c and bg_*.c can link

void QDECL Com_Error ( int level, const char *error, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, error);
	vsprintf (text, error, argptr);
	va_end (argptr);

	G_Error( "%s", text);
}

void QDECL Com_Printf( const char *msg, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, msg);
	vsprintf (text, msg, argptr);
	va_end (argptr);

	G_Printf ("%s", text);
}

#endif

/*
========================================================================

PLAYER COUNTING / SCORE SORTING

========================================================================
*/

/*
=============
AddTournamentPlayer

If there are less than two tournament players, put a
spectator in the game and restart
=============
*/
void AddTournamentPlayer( void ) {
	int			i;
	gclient_t	*client;
	gclient_t	*nextInLine;

	if ( level.numPlayingClients >= 2 ) {
		return;
	}

	// never change during intermission
	if ( level.intermissiontime ) {
		return;
	}

	nextInLine = NULL;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		client = &level.clients[i];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( client->sess.sessionTeam != TEAM_SPECTATOR ) {
			continue;
		}
		// never select the dedicated follow or scoreboard clients
		if ( client->sess.spectatorState == SPECTATOR_SCOREBOARD || 
			client->sess.spectatorClient < 0  ) {
			continue;
		}

		if ( !nextInLine || client->sess.spectatorTime < nextInLine->sess.spectatorTime ) {
			nextInLine = client;
		}
	}

	if ( !nextInLine ) {
		return;
	}

	level.warmupTime = -1;

	// set them to free-for-all team
	SetTeam( &g_entities[ nextInLine - level.clients ], "f" );
}

/*
=======================
RemoveTournamentLoser

Make the loser a spectator at the back of the line
=======================
*/
void RemoveTournamentLoser( void ) {
	int			clientNum;

	if ( level.numPlayingClients != 2 ) {
		return;
	}

	clientNum = level.sortedClients[1];

	if ( level.clients[ clientNum ].pers.connected != CON_CONNECTED ) {
		return;
	}

	// make them a spectator
	SetTeam( &g_entities[ clientNum ], "s" );
}

/*
=======================
RemoveTournamentWinner
=======================
*/
void RemoveTournamentWinner( void ) {
	int			clientNum;

	if ( level.numPlayingClients != 2 ) {
		return;
	}

	clientNum = level.sortedClients[0];

	if ( level.clients[ clientNum ].pers.connected != CON_CONNECTED ) {
		return;
	}

	// make them a spectator
	SetTeam( &g_entities[ clientNum ], "s" );
}

/*
=======================
AdjustTournamentScores
=======================
*/
void AdjustTournamentScores( void ) {
	int			clientNum;

	clientNum = level.sortedClients[0];
	if ( level.clients[ clientNum ].pers.connected == CON_CONNECTED ) {
		level.clients[ clientNum ].sess.wins++;
		ClientUserinfoChanged( clientNum );
	}

	clientNum = level.sortedClients[1];
	if ( level.clients[ clientNum ].pers.connected == CON_CONNECTED ) {
		level.clients[ clientNum ].sess.losses++;
		ClientUserinfoChanged( clientNum );
	}

}

/*
=============
SortRanks

=============
*/
int QDECL SortRanks( const void *a, const void *b ) {
	gclient_t	*ca, *cb;

	ca = &level.clients[*(int *)a];
	cb = &level.clients[*(int *)b];

	// sort special clients last
	if ( ca->sess.spectatorState == SPECTATOR_SCOREBOARD || ca->sess.spectatorClient < 0 ) {
		return 1;
	}
	if ( cb->sess.spectatorState == SPECTATOR_SCOREBOARD || cb->sess.spectatorClient < 0  ) {
		return -1;
	}

	// then connecting clients
	if ( ca->pers.connected == CON_CONNECTING ) {
		return 1;
	}
	if ( cb->pers.connected == CON_CONNECTING ) {
		return -1;
	}


	// then spectators
	if ( ca->sess.sessionTeam == TEAM_SPECTATOR && cb->sess.sessionTeam == TEAM_SPECTATOR ) {
		if ( ca->sess.spectatorTime < cb->sess.spectatorTime ) {
			return -1;
		}
		if ( ca->sess.spectatorTime > cb->sess.spectatorTime ) {
			return 1;
		}
		return 0;
	}
	if ( ca->sess.sessionTeam == TEAM_SPECTATOR ) {
		return 1;
	}
	if ( cb->sess.sessionTeam == TEAM_SPECTATOR ) {
		return -1;
	}

	// then sort by score
	if ( ca->ps.persistant[PERS_SCORE]
		> cb->ps.persistant[PERS_SCORE] ) {
		return -1;
	}
	if ( ca->ps.persistant[PERS_SCORE]
		< cb->ps.persistant[PERS_SCORE] ) {
		return 1;
	}
	return 0;
}

/*
============
CalculateRanks

Recalculates the score ranks of all players
This will be called on every client connect, begin, disconnect, death,
and team change.
============
*/
void CalculateRanks( void ) {
	int		i;
	int		rank;
	int		score;
	int		newScore;
	gclient_t	*cl;

	level.follow1 = -1;
	level.follow2 = -1;
	level.numConnectedClients = 0;
	level.numNonSpectatorClients = 0;
	level.numPlayingClients = 0;
	level.numVotingClients = 0;		// don't count bots
	for ( i = 0; i < TEAM_NUM_TEAMS; i++ ) {
		level.numteamVotingClients[i] = 0;
	}
	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( level.clients[i].pers.connected != CON_DISCONNECTED ) {
			level.sortedClients[level.numConnectedClients] = i;
			level.numConnectedClients++;

			if ( level.clients[i].sess.sessionTeam != TEAM_SPECTATOR ) {
				level.numNonSpectatorClients++;
			
				// decide if this should be auto-followed
				if ( level.clients[i].pers.connected == CON_CONNECTED ) {
					level.numPlayingClients++;
					if ( !(g_entities[i].r.svFlags & SVF_BOT) ) {
						level.numVotingClients++;
						if ( level.clients[i].sess.sessionTeam == TEAM_RED )
							level.numteamVotingClients[0]++;
						else if ( level.clients[i].sess.sessionTeam == TEAM_BLUE )
							level.numteamVotingClients[1]++;
					}
					if ( level.follow1 == -1 ) {
						level.follow1 = i;
					} else if ( level.follow2 == -1 ) {
						level.follow2 = i;
					}
				}
			}
		}
	}

	qsort( level.sortedClients, level.numConnectedClients, 
		sizeof(level.sortedClients[0]), SortRanks );

	// set the rank value for all clients that are connected and not spectators
	if ( g_gametype.integer >= GT_TEAM ) {
		// in team games, rank is just the order of the teams, 0=red, 1=blue, 2=tied
		for ( i = 0;  i < level.numConnectedClients; i++ ) {
			cl = &level.clients[ level.sortedClients[i] ];
			if ( level.teamScores[TEAM_RED] == level.teamScores[TEAM_BLUE] ) {
				cl->ps.persistant[PERS_RANK] = 2;
			} else if ( level.teamScores[TEAM_RED] > level.teamScores[TEAM_BLUE] ) {
				cl->ps.persistant[PERS_RANK] = 0;
			} else {
				cl->ps.persistant[PERS_RANK] = 1;
			}
		}
	} else {	
		rank = -1;
		score = 0;
		for ( i = 0;  i < level.numPlayingClients; i++ ) {
			cl = &level.clients[ level.sortedClients[i] ];
			newScore = cl->ps.persistant[PERS_SCORE];
			if ( i == 0 || newScore != score ) {
				rank = i;
				// assume we aren't tied until the next client is checked
				level.clients[ level.sortedClients[i] ].ps.persistant[PERS_RANK] = rank;
			} else {
				// we are tied with the previous client
				level.clients[ level.sortedClients[i-1] ].ps.persistant[PERS_RANK] = rank | RANK_TIED_FLAG;
				level.clients[ level.sortedClients[i] ].ps.persistant[PERS_RANK] = rank | RANK_TIED_FLAG;
			}
			score = newScore;
			if ( g_gametype.integer == GT_SINGLE_PLAYER && level.numPlayingClients == 1 ) {
				level.clients[ level.sortedClients[i] ].ps.persistant[PERS_RANK] = rank | RANK_TIED_FLAG;
			}
		}
	}

	// set the CS_SCORES1/2 configstrings, which will be visible to everyone
	if ( g_gametype.integer >= GT_TEAM ) {
		trap_SetConfigstring( CS_SCORES1, va("%i", level.teamScores[TEAM_RED] ) );
		trap_SetConfigstring( CS_SCORES2, va("%i", level.teamScores[TEAM_BLUE] ) );
	} else {
		if ( level.numConnectedClients == 0 ) {
			trap_SetConfigstring( CS_SCORES1, va("%i", SCORE_NOT_PRESENT) );
			trap_SetConfigstring( CS_SCORES2, va("%i", SCORE_NOT_PRESENT) );
		} else if ( level.numConnectedClients == 1 ) {
			trap_SetConfigstring( CS_SCORES1, va("%i", level.clients[ level.sortedClients[0] ].ps.persistant[PERS_SCORE] ) );
			trap_SetConfigstring( CS_SCORES2, va("%i", SCORE_NOT_PRESENT) );
		} else {
			trap_SetConfigstring( CS_SCORES1, va("%i", level.clients[ level.sortedClients[0] ].ps.persistant[PERS_SCORE] ) );
			trap_SetConfigstring( CS_SCORES2, va("%i", level.clients[ level.sortedClients[1] ].ps.persistant[PERS_SCORE] ) );
		}
	}

	// see if it is time to end the level
	CheckExitRules();

	// if we are at the intermission, send the new info to everyone
	if ( level.intermissiontime ) {
		SendScoreboardMessageToAllClients();
	}
}


/*
========================================================================

MAP CHANGING

========================================================================
*/

/*
========================
SendScoreboardMessageToAllClients

Do this at BeginIntermission time and whenever ranks are recalculated
due to enters/exits/forced team changes
========================
*/
void SendScoreboardMessageToAllClients( void ) {
	int		i;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if ( level.clients[ i ].pers.connected == CON_CONNECTED ) {
			DeathmatchScoreboardMessage( g_entities + i );
		}
	}
}

/*
========================
MoveClientToIntermission

When the intermission starts, this will be called for all players.
If a new client connects, this will be called after the spawn function.
========================
*/
void MoveClientToIntermission( gentity_t *ent ) {
	// take out of follow mode if needed
	if ( ent->client->sess.spectatorState == SPECTATOR_FOLLOW ) {
		StopFollowing( ent );
	}


	// move to the spot
	VectorCopy( level.intermission_origin, ent->s.origin );
	VectorCopy( level.intermission_origin, ent->client->ps.origin );
	VectorCopy (level.intermission_angle, ent->client->ps.viewangles);
	ent->client->ps.pm_type = PM_INTERMISSION;

	// clean up powerup info
	memset( ent->client->ps.powerups, 0, sizeof(ent->client->ps.powerups) );

	ent->client->ps.eFlags = 0;
	ent->s.eFlags = 0;
	ent->s.eType = ET_GENERAL;
	ent->s.modelindex = 0;
	ent->s.loopSound = 0;
	ent->s.event = 0;
	ent->r.contents = 0;
}

/*
==================
FindIntermissionPoint

This is also used for spectator spawns
==================
*/
void FindIntermissionPoint( void ) {
	gentity_t	*ent, *target;
	vec3_t		dir;

	// find the intermission spot
	ent = G_Find (NULL, FOFS(classname), "info_player_intermission");
	if ( !ent ) {	// the map creator forgot to put in an intermission point...
		SelectSpawnPoint ( vec3_origin, level.intermission_origin, level.intermission_angle );
	} else {
		VectorCopy (ent->s.origin, level.intermission_origin);
		VectorCopy (ent->s.angles, level.intermission_angle);
		// if it has a target, look towards it
		if ( ent->target ) {
			target = G_PickTarget( ent->target );
			if ( target ) {
				VectorSubtract( target->s.origin, level.intermission_origin, dir );
				vectoangles( dir, level.intermission_angle );
			}
		}
	}

}

/*
==================
BeginIntermission
==================
*/
void BeginIntermission( void ) {
	int			i;
	gentity_t	*client;

	if ( level.intermissiontime ) {
		return;		// already active
	}

	// if in tournement mode, change the wins / losses
	if ( g_gametype.integer == GT_TOURNAMENT ) {
		AdjustTournamentScores();
	}

	level.intermissiontime = level.time;
	FindIntermissionPoint();

#ifdef MISSIONPACK
	if (g_singlePlayer.integer) {
		trap_Cvar_Set("ui_singlePlayerActive", "0");
		UpdateTournamentInfo();
	}
#else
	// if single player game
	if ( g_gametype.integer == GT_SINGLE_PLAYER ) {
		UpdateTournamentInfo();
		SpawnModelsOnVictoryPads();
	}
#endif

	// move all clients to the intermission point
	for (i=0 ; i< level.maxclients ; i++) {
		client = g_entities + i;
		if (!client->inuse)
			continue;
		// respawn if dead
		if (client->health <= 0) {
			respawn(client);
		}
		MoveClientToIntermission( client );
	}

	// send the current scoring to all clients
	SendScoreboardMessageToAllClients();

}


/*
=============
ExitLevel

When the intermission has been exited, the server is either killed
or moved to a new level based on the "nextmap" cvar 

=============
*/
void ExitLevel (void) {
	int		i;
	gclient_t *cl;

	//bot interbreeding
	BotInterbreedEndMatch();

	// if we are running a tournement map, kick the loser to spectator status,
	// which will automatically grab the next spectator and restart
	if ( g_gametype.integer == GT_TOURNAMENT  ) {
		if ( !level.restarted ) {
			RemoveTournamentLoser();
			trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
			level.restarted = qtrue;
			level.changemap = NULL;
			level.intermissiontime = 0;
		}
		return;	
	}


	trap_SendConsoleCommand( EXEC_APPEND, "vstr nextmap\n" );
	level.changemap = NULL;
	level.intermissiontime = 0;

	// reset all the scores so we don't enter the intermission again
	level.teamScores[TEAM_RED] = 0;
	level.teamScores[TEAM_BLUE] = 0;
	for ( i=0 ; i< g_maxclients.integer ; i++ ) {
		cl = level.clients + i;
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		cl->ps.persistant[PERS_SCORE] = 0;
	}

	// we need to do this here before chaning to CON_CONNECTING
	G_WriteSessionData();

	// change all client states to connecting, so the early players into the
	// next level will know the others aren't done reconnecting
	for (i=0 ; i< g_maxclients.integer ; i++) {
		if ( level.clients[i].pers.connected == CON_CONNECTED ) {
			level.clients[i].pers.connected = CON_CONNECTING;
		}
	}

}

/*
=================
G_LogPrintf

Print to the logfile with a time stamp if it is open
=================
*/
void QDECL G_LogPrintf( const char *fmt, ... ) {
	va_list		argptr;
	char		string[1024];
	int			min, tens, sec;

	sec = level.time / 1000;

	min = sec / 60;
	sec -= min * 60;
	tens = sec / 10;
	sec -= tens * 10;

	Com_sprintf( string, sizeof(string), "%3i:%i%i ", min, tens, sec );

	va_start( argptr, fmt );
	vsprintf( string +7 , fmt,argptr );
	va_end( argptr );

	if ( g_dedicated.integer ) {
		G_Printf( "%s", string + 7 );
	}

	if ( !level.logFile ) {
		return;
	}

	trap_FS_Write( string, strlen( string ), level.logFile );
}

/*
================
LogExit

Append information about this game to the log file
================
*/
void LogExit( const char *string ) {
	int				i, numSorted;
	gclient_t		*cl;
#ifdef MISSIONPACK // bk001205
	qboolean won = qtrue;
#endif
	G_LogPrintf( "Exit: %s\n", string );

	level.intermissionQueued = level.time;

	// this will keep the clients from playing any voice sounds
	// that will get cut off when the queued intermission starts
	trap_SetConfigstring( CS_INTERMISSION, "1" );

	// don't send more than 32 scores (FIXME?)
	numSorted = level.numConnectedClients;
	if ( numSorted > 32 ) {
		numSorted = 32;
	}

	if ( g_gametype.integer >= GT_TEAM ) {
		G_LogPrintf( "red:%i  blue:%i\n",
			level.teamScores[TEAM_RED], level.teamScores[TEAM_BLUE] );
	}

	for (i=0 ; i < numSorted ; i++) {
		int		ping;

		cl = &level.clients[level.sortedClients[i]];

		if ( cl->sess.sessionTeam == TEAM_SPECTATOR ) {
			continue;
		}
		if ( cl->pers.connected == CON_CONNECTING ) {
			continue;
		}

		ping = cl->ps.ping < 999 ? cl->ps.ping : 999;

		G_LogPrintf( "score: %i  ping: %i  client: %i %s\n", cl->ps.persistant[PERS_SCORE], ping, level.sortedClients[i],	cl->pers.netname );
#ifdef MISSIONPACK
		if (g_singlePlayer.integer && g_gametype.integer == GT_TOURNAMENT) {
			if (g_entities[cl - level.clients].r.svFlags & SVF_BOT && cl->ps.persistant[PERS_RANK] == 0) {
				won = qfalse;
			}
		}
#endif

	}

#ifdef MISSIONPACK
	if (g_singlePlayer.integer) {
		if (g_gametype.integer >= GT_CTF) {
			won = level.teamScores[TEAM_RED] > level.teamScores[TEAM_BLUE];
		}
		trap_SendConsoleCommand( EXEC_APPEND, (won) ? "spWin\n" : "spLose\n" );
	}
#endif


}


/*
=================
CheckIntermissionExit

The level will stay at the intermission for a minimum of 5 seconds
If all players wish to continue, the level will then exit.
If one or more players have not acknowledged the continue, the game will
wait 10 seconds before going on.
=================
*/
void CheckIntermissionExit( void ) {
	int			ready, notReady;
	int			i;
	gclient_t	*cl;
	int			readyMask;

	if ( g_gametype.integer == GT_SINGLE_PLAYER ) {
		return;
	}

	// see which players are ready
	ready = 0;
	notReady = 0;
	readyMask = 0;
	for (i=0 ; i< g_maxclients.integer ; i++) {
		cl = level.clients + i;
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( g_entities[cl->ps.clientNum].r.svFlags & SVF_BOT ) {
			continue;
		}

		if ( cl->readyToExit ) {
			ready++;
			if ( i < 16 ) {
				readyMask |= 1 << i;
			}
		} else {
			notReady++;
		}
	}

	// copy the readyMask to each player's stats so
	// it can be displayed on the scoreboard
	for (i=0 ; i< g_maxclients.integer ; i++) {
		cl = level.clients + i;
		if ( cl->pers.connected != CON_CONNECTED ) {
			continue;
		}
		cl->ps.stats[STAT_CLIENTS_READY] = readyMask;
	}

	// never exit in less than five seconds
	if ( level.time < level.intermissiontime + 5000 ) {
		return;
	}

	// if nobody wants to go, clear timer
	if ( !ready ) {
		level.readyToExit = qfalse;
		return;
	}

	// if everyone wants to go, go now
	if ( !notReady ) {
		ExitLevel();
		return;
	}

	// the first person to ready starts the ten second timeout
	if ( !level.readyToExit ) {
		level.readyToExit = qtrue;
		level.exitTime = level.time;
	}

	// if we have waited ten seconds since at least one player
	// wanted to exit, go ahead
	if ( level.time < level.exitTime + 10000 ) {
		return;
	}

	ExitLevel();
}

/*
=============
ScoreIsTied
=============
*/
qboolean ScoreIsTied( void ) {
	int		a, b;

	if ( level.numPlayingClients < 2 ) {
		return qfalse;
	}
	
	if ( g_gametype.integer >= GT_TEAM ) {
		return level.teamScores[TEAM_RED] == level.teamScores[TEAM_BLUE];
	}

	a = level.clients[level.sortedClients[0]].ps.persistant[PERS_SCORE];
	b = level.clients[level.sortedClients[1]].ps.persistant[PERS_SCORE];

	return a == b;
}

/*
=================
CheckExitRules

There will be a delay between the time the exit is qualified for
and the time everyone is moved to the intermission spot, so you
can see the last frag.
=================
*/
void CheckExitRules( void ) {
 	int			i;
	gclient_t	*cl;
	// if at the intermission, wait for all non-bots to
	// signal ready, then go to next level
	if ( level.intermissiontime ) {
		CheckIntermissionExit ();
		return;
	}

	if ( level.intermissionQueued ) {
#ifdef MISSIONPACK
		int time = (g_singlePlayer.integer) ? SP_INTERMISSION_DELAY_TIME : INTERMISSION_DELAY_TIME;
		if ( level.time - level.intermissionQueued >= time ) {
			level.intermissionQueued = 0;
			BeginIntermission();
		}
#else
		if ( level.time - level.intermissionQueued >= INTERMISSION_DELAY_TIME ) {
			level.intermissionQueued = 0;
			BeginIntermission();
		}
#endif
		return;
	}

	// check for sudden death
	if ( ScoreIsTied() ) {
		// always wait for sudden death
		return;
	}

	if ( g_timelimit.integer && !level.warmupTime ) {
		if ( level.time - level.startTime >= g_timelimit.integer*60000 ) {
			trap_SendServerCommand( -1, "print \"Timelimit hit.\n\"");
			LogExit( "Timelimit hit." );
			return;
		}
	}

	if ( level.numPlayingClients < 2 ) {
		return;
	}

	if ( g_gametype.integer < GT_CTF && g_fraglimit.integer ) {
		if ( level.teamScores[TEAM_RED] >= g_fraglimit.integer ) {
			trap_SendServerCommand( -1, "print \"Red hit the fraglimit.\n\"" );
			LogExit( "Fraglimit hit." );
			return;
		}

		if ( level.teamScores[TEAM_BLUE] >= g_fraglimit.integer ) {
			trap_SendServerCommand( -1, "print \"Blue hit the fraglimit.\n\"" );
			LogExit( "Fraglimit hit." );
			return;
		}

		for ( i=0 ; i< g_maxclients.integer ; i++ ) {
			cl = level.clients + i;
			if ( cl->pers.connected != CON_CONNECTED ) {
				continue;
			}
			if ( cl->sess.sessionTeam != TEAM_FREE ) {
				continue;
			}

			if ( cl->ps.persistant[PERS_SCORE] >= g_fraglimit.integer ) {
				LogExit( "Fraglimit hit." );
				trap_SendServerCommand( -1, va("print \"%s" S_COLOR_WHITE " hit the fraglimit.\n\"",
					cl->pers.netname ) );
				return;
			}
		}
	}

	if ( g_gametype.integer >= GT_CTF && g_capturelimit.integer ) {

		if ( level.teamScores[TEAM_RED] >= g_capturelimit.integer ) {
			trap_SendServerCommand( -1, "print \"Red hit the capturelimit.\n\"" );
			LogExit( "Capturelimit hit." );
			return;
		}

		if ( level.teamScores[TEAM_BLUE] >= g_capturelimit.integer ) {
			trap_SendServerCommand( -1, "print \"Blue hit the capturelimit.\n\"" );
			LogExit( "Capturelimit hit." );
			return;
		}
	}
}



/*
========================================================================

FUNCTIONS CALLED EVERY FRAME

========================================================================
*/


/*
=============
CheckTournament

Once a frame, check for changes in tournement player state
=============
*/
void CheckTournament( void ) {
	// check because we run 3 game frames before calling Connect and/or ClientBegin
	// for clients on a map_restart
	if ( level.numPlayingClients == 0 ) {
		return;
	}

	if ( g_gametype.integer == GT_TOURNAMENT ) {

		// pull in a spectator if needed
		if ( level.numPlayingClients < 2 ) {
			AddTournamentPlayer();
		}

		// if we don't have two players, go back to "waiting for players"
		if ( level.numPlayingClients != 2 ) {
			if ( level.warmupTime != -1 ) {
				level.warmupTime = -1;
				trap_SetConfigstring( CS_WARMUP, va("%i", level.warmupTime) );
				G_LogPrintf( "Warmup:\n" );
			}
			return;
		}

		if ( level.warmupTime == 0 ) {
			return;
		}

		// if the warmup is changed at the console, restart it
		if ( g_warmup.modificationCount != level.warmupModificationCount ) {
			level.warmupModificationCount = g_warmup.modificationCount;
			level.warmupTime = -1;
			G_InitWeaponConfig();
		}

		// if all players have arrived, start the countdown
		if ( level.warmupTime < 0 ) {
			if ( level.numPlayingClients == 2 ) {
				// fudge by -1 to account for extra delays
				level.warmupTime = level.time + ( g_warmup.integer - 1 ) * 1000;
				trap_SetConfigstring( CS_WARMUP, va("%i", level.warmupTime) );
			}
			return;
		}

		// if the warmup time has counted down, restart
		if ( level.time > level.warmupTime ) {
			level.warmupTime += 10000;
			trap_Cvar_Set( "g_restarted", "1" );
			trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
			level.restarted = qtrue;
			return;
		}
	} else if ( g_gametype.integer != GT_SINGLE_PLAYER && level.warmupTime != 0 ) {
		int		counts[TEAM_NUM_TEAMS];
		qboolean	notEnough = qfalse;

		if ( g_gametype.integer > GT_TEAM ) {
			counts[TEAM_BLUE] = TeamCount( -1, TEAM_BLUE );
			counts[TEAM_RED] = TeamCount( -1, TEAM_RED );

			if (counts[TEAM_RED] < 1 || counts[TEAM_BLUE] < 1) {
				notEnough = qtrue;
			}
		} else if ( level.numPlayingClients < 2 ) {
			notEnough = qtrue;
		}

		if ( notEnough ) {
			if ( level.warmupTime != -1 ) {
				level.warmupTime = -1;
				trap_SetConfigstring( CS_WARMUP, va("%i", level.warmupTime) );
				G_LogPrintf( "Warmup:\n" );
			}
			return; // still waiting for team members
		}

		if ( level.warmupTime == 0 ) {
			return;
		}

		// if the warmup is changed at the console, restart it
		if ( g_warmup.modificationCount != level.warmupModificationCount ) {
			level.warmupModificationCount = g_warmup.modificationCount;
			level.warmupTime = -1;
			G_InitWeaponConfig();
		}

		// if all players have arrived, start the countdown
		if ( level.warmupTime < 0 ) {
			// fudge by -1 to account for extra delays
			level.warmupTime = level.time + ( g_warmup.integer - 1 ) * 1000;
			trap_SetConfigstring( CS_WARMUP, va("%i", level.warmupTime) );
			return;
		}

		// if the warmup time has counted down, restart
		if ( level.time > level.warmupTime ) {
			level.warmupTime += 10000;
			trap_Cvar_Set( "g_restarted", "1" );
			trap_SendConsoleCommand( EXEC_APPEND, "map_restart 0\n" );
			level.restarted = qtrue;
			return;
		}
	}
}


/*
==================
CheckVote
==================
*/
void CheckVote( void ) {
	if ( level.voteExecuteTime && level.voteExecuteTime < level.time ) {
		level.voteExecuteTime = 0;
		trap_SendConsoleCommand( EXEC_APPEND, va("%s\n", level.voteString ) );
	}
	if ( !level.voteTime ) {
		return;
	}
	if ( level.time - level.voteTime >= VOTE_TIME ) {
		trap_SendServerCommand( -1, "print \"Vote failed.\n\"" );
	} else {
		// ATVI Q3 1.32 Patch #9, WNF
		if ( level.voteYes > level.numVotingClients/2 ) {
			// execute the command, then remove the vote
			trap_SendServerCommand( -1, "print \"Vote passed.\n\"" );
			level.voteExecuteTime = level.time + 3000;
		} else if ( level.voteNo >= level.numVotingClients/2 ) {
			// same behavior as a timeout
			trap_SendServerCommand( -1, "print \"Vote failed.\n\"" );
		} else {
			// still waiting for a majority
			return;
		}
	}
	level.voteTime = 0;
	trap_SetConfigstring( CS_VOTE_TIME, "" );

}

/*
==================
PrintTeam
==================
*/
void PrintTeam(int team, char *message) {
	int i;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if (level.clients[i].sess.sessionTeam != team)
			continue;
		trap_SendServerCommand( i, message );
	}
}

/*
==================
SetLeader
==================
*/
void SetLeader(int team, int client) {
	int i;

	if ( level.clients[client].pers.connected == CON_DISCONNECTED ) {
		PrintTeam(team, va("print \"%s is not connected\n\"", level.clients[client].pers.netname) );
		return;
	}
	if (level.clients[client].sess.sessionTeam != team) {
		PrintTeam(team, va("print \"%s is not on the team anymore\n\"", level.clients[client].pers.netname) );
		return;
	}
	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if (level.clients[i].sess.sessionTeam != team)
			continue;
		if (level.clients[i].sess.teamLeader) {
			level.clients[i].sess.teamLeader = qfalse;
			ClientUserinfoChanged(i);
		}
	}
	level.clients[client].sess.teamLeader = qtrue;
	ClientUserinfoChanged( client );
	PrintTeam(team, va("print \"%s is the new team leader\n\"", level.clients[client].pers.netname) );
}

/*
==================
CheckTeamLeader
==================
*/
void CheckTeamLeader( int team ) {
	int i;

	for ( i = 0 ; i < level.maxclients ; i++ ) {
		if (level.clients[i].sess.sessionTeam != team)
			continue;
		if (level.clients[i].sess.teamLeader)
			break;
	}
	if (i >= level.maxclients) {
		for ( i = 0 ; i < level.maxclients ; i++ ) {
			if (level.clients[i].sess.sessionTeam != team)
				continue;
			if (!(g_entities[i].r.svFlags & SVF_BOT)) {
				level.clients[i].sess.teamLeader = qtrue;
				break;
			}
		}
		for ( i = 0 ; i < level.maxclients ; i++ ) {
			if (level.clients[i].sess.sessionTeam != team)
				continue;
			level.clients[i].sess.teamLeader = qtrue;
			break;
		}
	}
}

/*
==================
CheckTeamVote
==================
*/
void CheckTeamVote( int team ) {
	int cs_offset;

	if ( team == TEAM_RED )
		cs_offset = 0;
	else if ( team == TEAM_BLUE )
		cs_offset = 1;
	else
		return;

	if ( !level.teamVoteTime[cs_offset] ) {
		return;
	}
	if ( level.time - level.teamVoteTime[cs_offset] >= VOTE_TIME ) {
		trap_SendServerCommand( -1, "print \"Team vote failed.\n\"" );
	} else {
		if ( level.teamVoteYes[cs_offset] > level.numteamVotingClients[cs_offset]/2 ) {
			// execute the command, then remove the vote
			trap_SendServerCommand( -1, "print \"Team vote passed.\n\"" );
			//
			if ( !Q_strncmp( "leader", level.teamVoteString[cs_offset], 6) ) {
				//set the team leader
				SetLeader(team, atoi(level.teamVoteString[cs_offset] + 7));
			}
			else {
				trap_SendConsoleCommand( EXEC_APPEND, va("%s\n", level.teamVoteString[cs_offset] ) );
			}
		} else if ( level.teamVoteNo[cs_offset] >= level.numteamVotingClients[cs_offset]/2 ) {
			// same behavior as a timeout
			trap_SendServerCommand( -1, "print \"Team vote failed.\n\"" );
		} else {
			// still waiting for a majority
			return;
		}
	}
	level.teamVoteTime[cs_offset] = 0;
	trap_SetConfigstring( CS_TEAMVOTE_TIME + cs_offset, "" );

}


/*
==================
CheckCvars
==================
*/
void CheckCvars( void ) {
	static int lastMod = -1;

	if ( g_password.modificationCount != lastMod ) {
		lastMod = g_password.modificationCount;
		if ( *g_password.string && Q_stricmp( g_password.string, "none" ) ) {
			trap_Cvar_Set( "g_needpass", "1" );
		} else {
			trap_Cvar_Set( "g_needpass", "0" );
		}
	}
}

/*
=============
G_RunThink

Runs thinking code for this frame if necessary
=============
*/
void G_RunThink (gentity_t *ent) {
	float	thinktime;

	thinktime = ent->nextthink;
	if (thinktime <= 0) {
		return;
	}
	if (thinktime > level.time) {
		return;
	}
	
	ent->nextthink = 0;
	if (!ent->think) {
		G_Error ( "NULL ent->think");
	}
	ent->think (ent);
}

/*
================
G_RunFrame

Advances the non-player objects in the world
================
*/
void G_RunFrame( int levelTime ) {
	int			i;
	gentity_t	*ent;
	int			msec;
int start, end;

	// if we are waiting for the level to restart, do nothing
	if ( level.restarted ) {
		return;
	}

	level.framenum++;
	level.previousTime = level.time;
	level.time = levelTime;
	msec = level.time - level.previousTime;

	// get any cvar changes
	G_UpdateCvars();

	//
	// go through all allocated objects
	//
	start = trap_Milliseconds();
	ent = &g_entities[0];
	for (i=0 ; i<level.num_entities ; i++, ent++) {
		if ( !ent->inuse ) {
			continue;
		}

		// clear events that are too old
		if ( level.time - ent->eventTime > EVENT_VALID_MSEC ) {
			if ( ent->s.event ) {
				ent->s.event = 0;	// &= EV_EVENT_BITS;
				if ( ent->client ) {
					ent->client->ps.externalEvent = 0;
					// predicted events should never be set to zero
					//ent->client->ps.events[0] = 0;
					//ent->client->ps.events[1] = 0;
				}
			}
			if ( ent->freeAfterEvent ) {
				// tempEntities or dropped items completely go away after their event
				G_FreeEntity( ent );
				continue;
			} else if ( ent->unlinkAfterEvent ) {
				// items that will respawn will hide themselves after their pickup event
				ent->unlinkAfterEvent = qfalse;
				trap_UnlinkEntity( ent );
			}
		}

		// temporary entities don't think
		if ( ent->freeAfterEvent ) {
			continue;
		}

		if ( !ent->r.linked && ent->neverFree ) {
			continue;
		}

		if ( ent->s.eType == ET_MISSILE ) {
			G_RunMissile( ent );
			continue;
		}

		if ( ent->s.eType == ET_ITEM || ent->physicsObject ) {
			G_RunItem( ent );
			continue;
		}

		if ( ent->s.eType == ET_MOVER ) {
			G_RunMover( ent );
			continue;
		}

		if ( i < MAX_CLIENTS ) {
			G_RunClient( ent );
			continue;
		}

		G_RunThink( ent );
	}
end = trap_Milliseconds();

start = trap_Milliseconds();
	// perform final fixups on the players
	ent = &g_entities[0];
	for (i=0 ; i < level.maxclients ; i++, ent++ ) {
		if ( ent->inuse ) {
			ClientEndFrame( ent );
		}
	}
end = trap_Milliseconds();

	// see if it is time to do a tournement restart
	CheckTournament();

	// see if it is time to end the level
	CheckExitRules();

	// update to team status?
	CheckTeamStatus();

	// cancel vote if timed out
	CheckVote();

	// check team votes
	CheckTeamVote( TEAM_RED );
	CheckTeamVote( TEAM_BLUE );

	// for tracking changes
	CheckCvars();

	if (g_listEntity.integer) {
		for (i = 0; i < MAX_GENTITIES; i++) {
			G_Printf("%4i: %s\n", i, g_entities[i].classname);
		}
		trap_Cvar_Set("g_listEntity", "0");
	}
}
