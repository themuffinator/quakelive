#include "../code/game/g_local.h"
#include "g_config.h"

#define STRINGIZE_HELPER( x ) #x
#define STRINGIZE( x ) STRINGIZE_HELPER( x )

#ifndef ARRAY_LEN
#define ARRAY_LEN( x ) ( sizeof( x ) / sizeof( (x)[0] ) )
#endif

#define DEFAULT_STARTING_AMMO_BFG           10
#define DEFAULT_STARTING_AMMO_CG            100
#define DEFAULT_STARTING_AMMO_G             -1
#define DEFAULT_STARTING_AMMO_GH            -1
#define DEFAULT_STARTING_AMMO_GL            10
#define DEFAULT_STARTING_AMMO_HMG           50
#define DEFAULT_STARTING_AMMO_LG            100
#define DEFAULT_STARTING_AMMO_MG            100
#define DEFAULT_STARTING_AMMO_NG            10
#define DEFAULT_STARTING_AMMO_PG            50
#define DEFAULT_STARTING_AMMO_PL            5
#define DEFAULT_STARTING_AMMO_RG            5
#define DEFAULT_STARTING_AMMO_RL            5
#define DEFAULT_STARTING_AMMO_SG            10

#define DEFAULT_WEAPON_RELOAD_BFG           300
#define DEFAULT_WEAPON_RELOAD_CG            50
#define DEFAULT_WEAPON_RELOAD_GAUNTLET      400
#define DEFAULT_WEAPON_RELOAD_GH            100
#define DEFAULT_WEAPON_RELOAD_GL            800
#define DEFAULT_WEAPON_RELOAD_HMG           75
#define DEFAULT_WEAPON_RELOAD_HOOK          100
#define DEFAULT_WEAPON_RELOAD_LG            50
#define DEFAULT_WEAPON_RELOAD_MG            100
#define DEFAULT_WEAPON_RELOAD_NG            1000
#define DEFAULT_WEAPON_RELOAD_PG            100
#define DEFAULT_WEAPON_RELOAD_PROX          800
#define DEFAULT_WEAPON_RELOAD_RG            1500
#define DEFAULT_WEAPON_RELOAD_RL            800
#define DEFAULT_WEAPON_RELOAD_SG            1000

#define DEFAULT_KNOCKBACK_BFG               1.0f
#define DEFAULT_KNOCKBACK_CG                1.0f
#define DEFAULT_KNOCKBACK_G                 1.0f
#define DEFAULT_KNOCKBACK_GH                -5.0f
#define DEFAULT_KNOCKBACK_GL                1.10f
#define DEFAULT_KNOCKBACK_HMG               1.0f
#define DEFAULT_KNOCKBACK_LG                1.75f
#define DEFAULT_KNOCKBACK_MG                1.0f
#define DEFAULT_KNOCKBACK_NG                1.0f
#define DEFAULT_KNOCKBACK_PG                1.10f
#define DEFAULT_KNOCKBACK_PG_SELF           1.30f
#define DEFAULT_KNOCKBACK_PL                1.0f
#define DEFAULT_KNOCKBACK_RG                0.85f
#define DEFAULT_KNOCKBACK_RL                0.90f
#define DEFAULT_KNOCKBACK_RL_SELF           1.10f
#define DEFAULT_KNOCKBACK_SG                1.0f
#define DEFAULT_KNOCKBACK_VERTICAL          24.0f
#define DEFAULT_KNOCKBACK_VERTICAL_SELF     24.0f
#define DEFAULT_KNOCKBACK_CRIPPLE           0.0f

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

#define DEFAULT_STARTING_WEAPONS_MASK      ( ( 1 << ( WP_GAUNTLET - 1 ) ) | ( 1 << ( WP_MACHINEGUN - 1 ) ) )
#define DEFAULT_INFINITE_AMMO              0
#define DEFAULT_AMMO_PACK_TOGGLE           0
#define DEFAULT_AMMO_PACK_HACK             0
#define DEFAULT_AMMO_RESPAWN_SECONDS       40
#define DEFAULT_SUDDEN_DEATH_RESPAWN       0

weaponReloadConfig_t    g_weaponReloadConfig;
knockbackConfig_t       g_knockbackConfig;
ammoPackConfig_t        g_ammoPackConfig;
factoryCvarConfig_t     g_factoryCvarConfig;
startingAmmoConfig_t    g_startingAmmoConfig;

vmCvar_t        weapon_reload_gauntlet;
vmCvar_t        weapon_reload_mg;
vmCvar_t        weapon_reload_sg;
vmCvar_t        weapon_reload_gl;
vmCvar_t        weapon_reload_rl;
vmCvar_t        weapon_reload_lg;
vmCvar_t        weapon_reload_rg;
vmCvar_t        weapon_reload_pg;
vmCvar_t        weapon_reload_bfg;
vmCvar_t        weapon_reload_gh;
vmCvar_t        weapon_reload_hook;
vmCvar_t        weapon_reload_ng;
vmCvar_t        weapon_reload_prox;
vmCvar_t        weapon_reload_cg;
vmCvar_t        weapon_reload_hmg;

vmCvar_t        g_startingWeapons;
vmCvar_t        g_infiniteAmmo;
vmCvar_t        g_ammoPack;
vmCvar_t        g_ammoPackHack;
vmCvar_t        g_ammoRespawn;
extern vmCvar_t g_suddenDeathRespawn;

vmCvar_t        g_ammoPack_bfg;
vmCvar_t        g_ammoPack_cg;
vmCvar_t        g_ammoPack_gl;
vmCvar_t        g_ammoPack_hmg;
vmCvar_t        g_ammoPack_lg;
vmCvar_t        g_ammoPack_mg;
vmCvar_t        g_ammoPack_ng;
vmCvar_t        g_ammoPack_pg;
vmCvar_t        g_ammoPack_pl;
vmCvar_t        g_ammoPack_rg;
vmCvar_t        g_ammoPack_rl;
vmCvar_t        g_ammoPack_sg;

vmCvar_t        g_startingAmmo_bfg;
vmCvar_t        g_startingAmmo_cg;
vmCvar_t        g_startingAmmo_g;
vmCvar_t        g_startingAmmo_gh;
vmCvar_t        g_startingAmmo_gl;
vmCvar_t        g_startingAmmo_hmg;
vmCvar_t        g_startingAmmo_lg;
vmCvar_t        g_startingAmmo_mg;
vmCvar_t        g_startingAmmo_ng;
vmCvar_t        g_startingAmmo_pg;
vmCvar_t        g_startingAmmo_pl;
vmCvar_t        g_startingAmmo_rg;
vmCvar_t        g_startingAmmo_rl;
vmCvar_t        g_startingAmmo_sg;

vmCvar_t        g_knockback_g;
vmCvar_t        g_knockback_mg;
vmCvar_t        g_knockback_sg;
vmCvar_t        g_knockback_gl;
vmCvar_t        g_knockback_rl;
vmCvar_t        g_knockback_rl_self;
vmCvar_t        g_knockback_lg;
vmCvar_t        g_knockback_rg;
vmCvar_t        g_knockback_pg;
vmCvar_t        g_knockback_pg_self;
vmCvar_t        g_knockback_bfg;
vmCvar_t        g_knockback_gh;
vmCvar_t        g_knockback_ng;
vmCvar_t        g_knockback_pl;
vmCvar_t        g_knockback_cg;
vmCvar_t        g_knockback_hmg;
vmCvar_t        g_knockback_z;
vmCvar_t        g_knockback_z_self;
vmCvar_t        g_max_knockback;
vmCvar_t        g_knockback_cripple;

typedef struct {
        vmCvar_t        *vmCvar;
        const char      *cvarName;
        const char      *defaultString;
        int             cvarFlags;
        const char      *helpString;
} configCvarTable_t;

static configCvarTable_t s_configCvarTable[] = {
        { &weapon_reload_gauntlet, "weapon_reload_gauntlet", "0", 0, "Gauntlet refire delay override in milliseconds; 0 preserves the compiled behaviour." },
        { &weapon_reload_mg,       "weapon_reload_mg",       "0", 0, "Machinegun refire delay override in milliseconds; 0 keeps the built-in rate." },
        { &weapon_reload_sg,       "weapon_reload_sg",       "0", 0, "Shotgun refire delay override in milliseconds; 0 leaves the default timing." },
        { &weapon_reload_gl,       "weapon_reload_gl",       "0", 0, "Grenade Launcher refire delay override in milliseconds." },
        { &weapon_reload_rl,       "weapon_reload_rl",       "0", 0, "Rocket Launcher refire delay override in milliseconds." },
        { &weapon_reload_lg,       "weapon_reload_lg",       "0", 0, "Lightning Gun refire delay override in milliseconds." },
        { &weapon_reload_rg,       "weapon_reload_rg",       "0", 0, "Railgun refire delay override in milliseconds." },
        { &weapon_reload_pg,       "weapon_reload_pg",       "0", 0, "Plasma Gun refire delay override in milliseconds." },
        { &weapon_reload_bfg,      "weapon_reload_bfg",      "0", 0, "BFG refire delay override in milliseconds." },
        { &weapon_reload_gh,       "weapon_reload_gh",       "0", 0, "Grappling Hook refire delay override in milliseconds." },
        { &weapon_reload_hook,     "weapon_reload_hook",     "0", 0, "Hook pull refire delay override in milliseconds." },
        { &weapon_reload_ng,       "weapon_reload_ng",       "0", 0, "Nailgun refire delay override in milliseconds." },
        { &weapon_reload_prox,     "weapon_reload_prox",     "0", 0, "Proximity Launcher refire delay override in milliseconds." },
        { &weapon_reload_cg,       "weapon_reload_cg",       "0", 0, "Chaingun refire delay override in milliseconds." },
        { &weapon_reload_hmg,      "weapon_reload_hmg",      "0", 0, "Heavy Machinegun refire delay override in milliseconds." },

        { &g_startingWeapons,      "g_startingWeapons",      STRINGIZE( DEFAULT_STARTING_WEAPONS_MASK ), CVAR_ARCHIVE, "Bitmask describing which weapons players spawn with; bit (weapon-1) matches the WP_* enum used by Quake Live factories." },
        { &g_infiniteAmmo,         "g_infiniteAmmo",         STRINGIZE( DEFAULT_INFINITE_AMMO ), CVAR_ARCHIVE, "When non-zero, spawn loadouts grant infinite ammunition mirroring Quake Live practice factories." },
        { &g_ammoPack,             "g_ammoPack",             STRINGIZE( DEFAULT_AMMO_PACK_TOGGLE ), CVAR_ARCHIVE, "Enable Quake Live ammo pack sizing so pickups follow factory scripts instead of compiled defaults." },
        { &g_ammoPackHack,         "g_ammoPackHack",         STRINGIZE( DEFAULT_AMMO_PACK_HACK ), CVAR_ARCHIVE, "Legacy Quake Live ammo pack override used by classic map factories." },
        { &g_ammoRespawn,          "g_ammoRespawn",          STRINGIZE( DEFAULT_AMMO_RESPAWN_SECONDS ), CVAR_ARCHIVE, "Seconds before ammo entities respawn; Quake Live factories reduce this for faster loops." },
        { &g_suddenDeathRespawn,   "g_suddenDeathRespawn",   STRINGIZE( DEFAULT_SUDDEN_DEATH_RESPAWN ), CVAR_ARCHIVE, "Allow ammo to continue respawning during sudden death when set to 1." },

        { &g_ammoPack_bfg,         "g_ammoPack_bfg",         STRINGIZE( DEFAULT_AMMOPACK_BFG ), CVAR_ARCHIVE, "Cells granted when picking up a BFG ammo pack, matching Quake Live's default drop." },
        { &g_ammoPack_cg,          "g_ammoPack_cg",          STRINGIZE( DEFAULT_AMMOPACK_CG ), CVAR_ARCHIVE, "Chaingun bullets restored per ammo belt pickup." },
        { &g_ammoPack_gl,          "g_ammoPack_gl",          STRINGIZE( DEFAULT_AMMOPACK_GL ), CVAR_ARCHIVE, "Grenade Launcher rounds provided by grenade ammo packs." },
        { &g_ammoPack_hmg,         "g_ammoPack_hmg",         STRINGIZE( DEFAULT_AMMOPACK_HMG ), CVAR_ARCHIVE, "Heavy Machinegun bullets added from heavy ammo packs." },
        { &g_ammoPack_lg,          "g_ammoPack_lg",          STRINGIZE( DEFAULT_AMMOPACK_LG ), CVAR_ARCHIVE, "Lightning Gun cells awarded from lightning ammo pickups." },
        { &g_ammoPack_mg,          "g_ammoPack_mg",          STRINGIZE( DEFAULT_AMMOPACK_MG ), CVAR_ARCHIVE, "Machinegun bullets restored by standard bullet boxes." },
        { &g_ammoPack_ng,          "g_ammoPack_ng",          STRINGIZE( DEFAULT_AMMOPACK_NG ), CVAR_ARCHIVE, "Nailgun spikes issued from nail ammo packs." },
        { &g_ammoPack_pg,          "g_ammoPack_pg",          STRINGIZE( DEFAULT_AMMOPACK_PG ), CVAR_ARCHIVE, "Plasmagun cells delivered with plasma ammo pickups." },
        { &g_ammoPack_pl,          "g_ammoPack_pl",          STRINGIZE( DEFAULT_AMMOPACK_PL ), CVAR_ARCHIVE, "Proximity Launcher mines granted from proximity ammo packs." },
        { &g_ammoPack_rg,          "g_ammoPack_rg",          STRINGIZE( DEFAULT_AMMOPACK_RG ), CVAR_ARCHIVE, "Railgun slugs provided whenever a rail ammo pack is collected." },
        { &g_ammoPack_rl,          "g_ammoPack_rl",          STRINGIZE( DEFAULT_AMMOPACK_RL ), CVAR_ARCHIVE, "Rockets granted per rocket ammo box pickup." },
        { &g_ammoPack_sg,          "g_ammoPack_sg",          STRINGIZE( DEFAULT_AMMOPACK_SG ), CVAR_ARCHIVE, "Shotgun shells restored with shell ammo packs." },

        { &g_startingAmmo_bfg,     "g_startingAmmo_bfg",     STRINGIZE( DEFAULT_STARTING_AMMO_BFG ), CVAR_ARCHIVE, "Cells granted for the BFG whenever spawn loadouts (g_startingWeapons, factories, scripts) include it." },
        { &g_startingAmmo_cg,      "g_startingAmmo_cg",      STRINGIZE( DEFAULT_STARTING_AMMO_CG ), CVAR_ARCHIVE, "Chaingun bullets provided on spawn when the weapon is part of the configured loadout." },
        { &g_startingAmmo_g,       "g_startingAmmo_g",       STRINGIZE( DEFAULT_STARTING_AMMO_G ), CVAR_ARCHIVE, "Gauntlet swings granted on spawn; -1 mirrors Quake Live's infinite melee behaviour." },
        { &g_startingAmmo_gh,      "g_startingAmmo_gh",      STRINGIZE( DEFAULT_STARTING_AMMO_GH ), CVAR_ARCHIVE, "Grappling Hook ammo applied to players when scripts or factories grant the hook; -1 keeps it unlimited." },
        { &g_startingAmmo_gl,      "g_startingAmmo_gl",      STRINGIZE( DEFAULT_STARTING_AMMO_GL ), CVAR_ARCHIVE, "Grenade Launcher rounds distributed at spawn when the launcher is granted via loadouts." },
        { &g_startingAmmo_hmg,     "g_startingAmmo_hmg",     STRINGIZE( DEFAULT_STARTING_AMMO_HMG ), CVAR_ARCHIVE, "Heavy Machinegun bullets issued alongside spawn loadouts that include the weapon." },
        { &g_startingAmmo_lg,      "g_startingAmmo_lg",      STRINGIZE( DEFAULT_STARTING_AMMO_LG ), CVAR_ARCHIVE, "Lightning Gun cells assigned when loadouts or scripts give the Lightning Gun on spawn." },
        { &g_startingAmmo_mg,      "g_startingAmmo_mg",      STRINGIZE( DEFAULT_STARTING_AMMO_MG ), CVAR_ARCHIVE, "Machinegun bullets supplied on spawn for any loadout that awards the Machinegun." },
        { &g_startingAmmo_ng,      "g_startingAmmo_ng",      STRINGIZE( DEFAULT_STARTING_AMMO_NG ), CVAR_ARCHIVE, "Nailgun spikes given to players when factories or scripts seed the Nailgun." },
        { &g_startingAmmo_pg,      "g_startingAmmo_pg",      STRINGIZE( DEFAULT_STARTING_AMMO_PG ), CVAR_ARCHIVE, "Plasmagun cells granted at spawn when the Plasmagun is included in the starting set." },
        { &g_startingAmmo_pl,      "g_startingAmmo_pl",      STRINGIZE( DEFAULT_STARTING_AMMO_PL ), CVAR_ARCHIVE, "Proximity Launcher mines provided to players when loadouts grant the launcher." },
        { &g_startingAmmo_rg,      "g_startingAmmo_rg",      STRINGIZE( DEFAULT_STARTING_AMMO_RG ), CVAR_ARCHIVE, "Railgun slugs applied on spawn when the Railgun is part of the configured loadout." },
        { &g_startingAmmo_rl,      "g_startingAmmo_rl",      STRINGIZE( DEFAULT_STARTING_AMMO_RL ), CVAR_ARCHIVE, "Rockets handed out whenever spawn loadouts include the Rocket Launcher." },
        { &g_startingAmmo_sg,      "g_startingAmmo_sg",      STRINGIZE( DEFAULT_STARTING_AMMO_SG ), CVAR_ARCHIVE, "Shotgun shells distributed when the Shotgun is in the spawn weapon set." },

        { &g_knockback_g,          "g_knockback_g",          STRINGIZE( DEFAULT_KNOCKBACK_G ), 0, "Gauntlet knockback scalar applied when striking other players." },
        { &g_knockback_mg,         "g_knockback_mg",         STRINGIZE( DEFAULT_KNOCKBACK_MG ), 0, "Machinegun knockback scalar applied to outgoing hits." },
        { &g_knockback_sg,         "g_knockback_sg",         STRINGIZE( DEFAULT_KNOCKBACK_SG ), 0, "Shotgun knockback scalar for pellets that land on opponents." },
        { &g_knockback_gl,         "g_knockback_gl",         STRINGIZE( DEFAULT_KNOCKBACK_GL ), 0, "Grenade Launcher knockback scalar applied to direct and splash damage." },
        { &g_knockback_rl,         "g_knockback_rl",         STRINGIZE( DEFAULT_KNOCKBACK_RL ), 0, "Rocket Launcher knockback scalar for enemies struck by rockets." },
        { &g_knockback_rl_self,    "g_knockback_rl_self",    STRINGIZE( DEFAULT_KNOCKBACK_RL_SELF ), 0, "Self-inflicted rocket knockback scalar used for rocket jumps." },
        { &g_knockback_lg,         "g_knockback_lg",         STRINGIZE( DEFAULT_KNOCKBACK_LG ), 0, "Lightning Gun knockback scalar." },
        { &g_knockback_rg,         "g_knockback_rg",         STRINGIZE( DEFAULT_KNOCKBACK_RG ), 0, "Railgun knockback scalar." },
        { &g_knockback_pg,         "g_knockback_pg",         STRINGIZE( DEFAULT_KNOCKBACK_PG ), 0, "Plasmagun knockback scalar for opponents." },
        { &g_knockback_pg_self,    "g_knockback_pg_self",    STRINGIZE( DEFAULT_KNOCKBACK_PG_SELF ), 0, "Self-inflicted plasmagun knockback scalar." },
        { &g_knockback_bfg,        "g_knockback_bfg",        STRINGIZE( DEFAULT_KNOCKBACK_BFG ), 0, "BFG knockback scalar." },
        { &g_knockback_gh,         "g_knockback_gh",         STRINGIZE( DEFAULT_KNOCKBACK_GH ), 0, "Grappling Hook knockback scalar." },
        { &g_knockback_ng,         "g_knockback_ng",         STRINGIZE( DEFAULT_KNOCKBACK_NG ), 0, "Nailgun knockback scalar." },
        { &g_knockback_pl,         "g_knockback_pl",         STRINGIZE( DEFAULT_KNOCKBACK_PL ), 0, "Proximity Launcher knockback scalar." },
        { &g_knockback_cg,         "g_knockback_cg",         STRINGIZE( DEFAULT_KNOCKBACK_CG ), 0, "Chaingun knockback scalar." },
        { &g_knockback_hmg,        "g_knockback_hmg",        STRINGIZE( DEFAULT_KNOCKBACK_HMG ), 0, "Heavy Machinegun knockback scalar." },
        { &g_knockback_z,          "g_knockback_z",          STRINGIZE( DEFAULT_KNOCKBACK_VERTICAL ), 0, "Vertical knockback boost added after weapon scaling." },
        { &g_knockback_z_self,     "g_knockback_z_self",     STRINGIZE( DEFAULT_KNOCKBACK_VERTICAL_SELF ), 0, "Vertical knockback boost when you knock yourself back." },
        { &g_max_knockback,        "g_max_knockback",        "200", 0, "Upper clamp applied to computed knockback force." },
        { &g_knockback_cripple,    "g_knockback_cripple",    STRINGIZE( DEFAULT_KNOCKBACK_CRIPPLE ), 0, "Additional knockback scalar consumed by cripple modifiers." },
};

static void G_Config_RegisterCvarHelp( const configCvarTable_t *cv ) {
        char helpName[MAX_CVAR_VALUE_STRING];

        if ( !cv || !cv->helpString || !cv->helpString[0] || !cv->cvarName || !cv->cvarName[0] ) {
                return;
        }

        Com_sprintf( helpName, sizeof( helpName ), "helptext_%s", cv->cvarName );
        trap_Cvar_Register( NULL, helpName, cv->helpString, CVAR_ROM );
}

void G_Config_RegisterCvars( void ) {
        size_t i;

        for ( i = 0; i < ARRAY_LEN( s_configCvarTable ); ++i ) {
                const configCvarTable_t *cv = &s_configCvarTable[i];

                trap_Cvar_Register( cv->vmCvar, cv->cvarName, cv->defaultString, cv->cvarFlags );
                G_Config_RegisterCvarHelp( cv );
        }

        G_Config_UpdateCvars();
}

void G_Config_UpdateCvars( void ) {
        size_t i;

        for ( i = 0; i < ARRAY_LEN( s_configCvarTable ); ++i ) {
                if ( s_configCvarTable[i].vmCvar ) {
                        trap_Cvar_Update( s_configCvarTable[i].vmCvar );
                }
        }
}

static void G_Config_ReportMissingCvar( const char *cvarName ) {
        if ( !cvarName || !cvarName[0] ) {
                return;
        }

        G_Printf( "WARNING: gameplay config cvar %s is unavailable; using fallback value\n", cvarName );
}

static int G_ReadWeaponReloadCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
        if ( !cvar ) {
                G_Config_ReportMissingCvar( cvarName );
                return fallback;
        }

        if ( cvar->integer <= 0 ) {
                return fallback;
        }

        return cvar->integer;
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

        G_PmoveStoreWeaponReloads( &g_weaponReloadConfig );
}

void G_UpdateWeaponReloadConfig( void ) {
        G_InitWeaponReloadConfig();
}

static int G_ReadAmmoPackCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
        int value;

        if ( !cvar ) {
                G_Config_ReportMissingCvar( cvarName );
                return fallback;
        }

        value = cvar->integer;

        if ( value <= 0 ) {
                return fallback;
        }

        return value;
}

static void G_AssignAmmoPackEntry( weapon_t weapon, const vmCvar_t *cvar, int fallback, const char *cvarName ) {
        int pickup = G_ReadAmmoPackCvar( cvar, fallback, cvarName );

        g_ammoPackConfig.weaponPickup[weapon] = pickup;
        if ( pickup > 0 ) {
                g_ammoPackConfig.weaponMax[weapon] = pickup * 4;
        } else {
                g_ammoPackConfig.weaponMax[weapon] = 0;
        }
}

void G_InitAmmoPackConfig( void ) {
        int weapon;

        for ( weapon = WP_NONE; weapon < WP_NUM_WEAPONS; ++weapon ) {
                g_ammoPackConfig.weaponPickup[weapon] = 0;
                g_ammoPackConfig.weaponMax[weapon] = 0;
        }

        G_AssignAmmoPackEntry( WP_MACHINEGUN, &g_ammoPack_mg, DEFAULT_AMMOPACK_MG, "g_ammoPack_mg" );
        G_AssignAmmoPackEntry( WP_SHOTGUN, &g_ammoPack_sg, DEFAULT_AMMOPACK_SG, "g_ammoPack_sg" );
        G_AssignAmmoPackEntry( WP_GRENADE_LAUNCHER, &g_ammoPack_gl, DEFAULT_AMMOPACK_GL, "g_ammoPack_gl" );
        G_AssignAmmoPackEntry( WP_ROCKET_LAUNCHER, &g_ammoPack_rl, DEFAULT_AMMOPACK_RL, "g_ammoPack_rl" );
        G_AssignAmmoPackEntry( WP_LIGHTNING, &g_ammoPack_lg, DEFAULT_AMMOPACK_LG, "g_ammoPack_lg" );
        G_AssignAmmoPackEntry( WP_RAILGUN, &g_ammoPack_rg, DEFAULT_AMMOPACK_RG, "g_ammoPack_rg" );
        G_AssignAmmoPackEntry( WP_PLASMAGUN, &g_ammoPack_pg, DEFAULT_AMMOPACK_PG, "g_ammoPack_pg" );
        G_AssignAmmoPackEntry( WP_BFG, &g_ammoPack_bfg, DEFAULT_AMMOPACK_BFG, "g_ammoPack_bfg" );

        G_AssignAmmoPackEntry( WP_HEAVY_MACHINEGUN, &g_ammoPack_hmg, DEFAULT_AMMOPACK_HMG, "g_ammoPack_hmg" );
#ifdef MISSIONPACK
        G_AssignAmmoPackEntry( WP_NAILGUN, &g_ammoPack_ng, DEFAULT_AMMOPACK_NG, "g_ammoPack_ng" );
        G_AssignAmmoPackEntry( WP_PROX_LAUNCHER, &g_ammoPack_pl, DEFAULT_AMMOPACK_PL, "g_ammoPack_pl" );
        G_AssignAmmoPackEntry( WP_CHAINGUN, &g_ammoPack_cg, DEFAULT_AMMOPACK_CG, "g_ammoPack_cg" );
#endif
}

void G_UpdateAmmoPackConfig( void ) {
        G_InitAmmoPackConfig();
}

static int G_ReadFactoryIntCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
        if ( !cvar ) {
                G_Config_ReportMissingCvar( cvarName );
                return fallback;
        }

        return cvar->integer;
}

static qboolean G_ReadFactoryBoolCvar( const vmCvar_t *cvar, qboolean fallback, const char *cvarName ) {
        int value = G_ReadFactoryIntCvar( cvar, fallback ? 1 : 0, cvarName );

        return value ? qtrue : qfalse;
}

static int G_ReadStartingWeaponsMaskCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
        int mask = G_ReadFactoryIntCvar( cvar, fallback, cvarName );

        if ( mask < 0 ) {
                mask = 0;
        }

        return mask;
}

static unsigned int G_ComputeStartingWeaponsStatMask( int mask ) {
        unsigned int statMask = 0;
        weapon_t weapon;

        if ( mask <= 0 ) {
                return 0;
        }

        for ( weapon = WP_GAUNTLET; weapon < WP_NUM_WEAPONS; ++weapon ) {
                int cvarBit = 1 << ( weapon - 1 );

                if ( mask & cvarBit ) {
                        statMask |= 1u << weapon;
                }
        }

        return statMask;
}

static factoryCvarConfig_t G_LoadFactoryCvarConfig( void ) {
        factoryCvarConfig_t config;

        config.startingWeaponsMask = G_ReadStartingWeaponsMaskCvar( &g_startingWeapons, DEFAULT_STARTING_WEAPONS_MASK, "g_startingWeapons" );
        config.startingWeaponsStatMask = G_ComputeStartingWeaponsStatMask( config.startingWeaponsMask );
        if ( config.startingWeaponsStatMask == 0 ) {
                config.startingWeaponsMask = DEFAULT_STARTING_WEAPONS_MASK;
                config.startingWeaponsStatMask = G_ComputeStartingWeaponsStatMask( config.startingWeaponsMask );
        }

        config.infiniteAmmo = G_ReadFactoryBoolCvar( &g_infiniteAmmo, DEFAULT_INFINITE_AMMO, "g_infiniteAmmo" );
        config.ammoPackEnabled = G_ReadFactoryBoolCvar( &g_ammoPack, DEFAULT_AMMO_PACK_TOGGLE, "g_ammoPack" );
        config.ammoPackHackEnabled = G_ReadFactoryBoolCvar( &g_ammoPackHack, DEFAULT_AMMO_PACK_HACK, "g_ammoPackHack" );
        config.ammoRespawnSeconds = G_ReadFactoryIntCvar( &g_ammoRespawn, DEFAULT_AMMO_RESPAWN_SECONDS, "g_ammoRespawn" );
        if ( config.ammoRespawnSeconds <= 0 ) {
                config.ammoRespawnSeconds = DEFAULT_AMMO_RESPAWN_SECONDS;
        }

        config.suddenDeathRespawn = G_ReadFactoryBoolCvar( &g_suddenDeathRespawn, DEFAULT_SUDDEN_DEATH_RESPAWN, "g_suddenDeathRespawn" );

        return config;
}

static void G_LogFactoryLoadoutState( const char *reason, const factoryCvarConfig_t *config ) {
        if ( !reason || !config ) {
                return;
        }

        G_Printf( "Factory loadout (%s): mask=%i statMask=0x%X infiniteAmmo=%i ammoPack=%i hack=%i ammoRespawn=%i suddenDeathRespawn=%i\n",
                reason,
                config->startingWeaponsMask,
                config->startingWeaponsStatMask,
                config->infiniteAmmo,
                config->ammoPackEnabled,
                config->ammoPackHackEnabled,
                config->ammoRespawnSeconds,
                config->suddenDeathRespawn );
}

static factoryCvarConfig_t s_reportedFactoryConfig;

void G_InitFactoryCvarConfig( void ) {
        g_factoryCvarConfig = G_LoadFactoryCvarConfig();
        s_reportedFactoryConfig = g_factoryCvarConfig;
        G_LogFactoryLoadoutState( "init", &g_factoryCvarConfig );
}

void G_UpdateFactoryCvarConfig( void ) {
        factoryCvarConfig_t config = G_LoadFactoryCvarConfig();

        if ( config.startingWeaponsMask != s_reportedFactoryConfig.startingWeaponsMask
                || config.startingWeaponsStatMask != s_reportedFactoryConfig.startingWeaponsStatMask
                || config.infiniteAmmo != s_reportedFactoryConfig.infiniteAmmo
                || config.ammoPackEnabled != s_reportedFactoryConfig.ammoPackEnabled
                || config.ammoPackHackEnabled != s_reportedFactoryConfig.ammoPackHackEnabled
                || config.ammoRespawnSeconds != s_reportedFactoryConfig.ammoRespawnSeconds
                || config.suddenDeathRespawn != s_reportedFactoryConfig.suddenDeathRespawn ) {
                G_LogFactoryLoadoutState( "update", &config );
                s_reportedFactoryConfig = config;
        }

        g_factoryCvarConfig = config;
}

static int G_ReadStartingAmmoCvar( const vmCvar_t *cvar, int fallback, const char *cvarName ) {
        if ( !cvar ) {
                G_Config_ReportMissingCvar( cvarName );
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
                G_Config_ReportMissingCvar( cvarName );
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
