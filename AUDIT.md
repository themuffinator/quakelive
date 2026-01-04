# Quake Live Parity Audit

This document outlines the current state of the codebase relative to the retail Quake Live version, based on HLIL references and source code inspection.

## 1. Physics & Movement (`bg_pmove.c`)
**Status:** High Parity
**Gap:** Low

*   **Air Control**: `PM_AirControl` is implemented in `bg_pmove.c`, mirroring the CPMA/PQL logic. `PM_AirMove` correctly prioritizes or integrates this logic when `pm_aircontrol` is non-zero.
*   **Settings**: `pm_defaultSettings` correctly includes `airControl`, `airAccel`, and strafe settings, matching QL defaults.
*   **Race**: `G_RaceInitLevel` and `SP_race_point` are present in `g_race.c`, ensuring server-side Race logic is robust. Physics interactions rely on standard triggers, which is generally correct for Q3A-based Race.

## 2. Game Logic (`qagamex86`)
**Status:** High Parity
**Gap:** Low

*   **Auth & Admin**: `ClientConnect` correctly implements `trap_GetSteamId` and calls `G_RunPlatformAuthChecks`. The Admin system (`Cmd_Admin_f`) supports `invite`, `revoke`, `mute`, `lock`, `putteam`, and `allready`, matching QL functionality.
*   **Gametypes**:
    *   **Red Rover**: `G_RRIsActive` and infection logic present in `g_client.c`.
    *   **Domination**: `Team_InitDomination` and scoring present.
    *   **Freeze Tag**: `G_FreezeGametypeEnabled` and thaw logic present.
    *   **Race**: Fully implemented in `g_race.c`.
*   **Weapons**: HMG, Chaingun, Nailgun, Prox Mine are implemented. `G_InitWeaponConfig` correctly reads `g_damage_*` CVars.
*   **factories**: The Factory system (`G_FactoryRegistry_Init`) is present to handle match presets.

## 3. User Interface (`ui`)
**Status:** Mixed
**Gap:** Medium

*   **Menus**: The legacy Quake III "Start Server" menu has been removed (`ui_quakelive_bridge.c` mentions using QL menus). Since Quake Live used a web-based launcher/menu (CEF), a native in-game "Create Match" menu is missing in the `src/ui` tree.
*   **Bridge**: `ui_quakelive_bridge.c` exists to bridge UI calls, but without the web assets, the "Start Game" flow relies on the console (`map` command).
*   **Constraints**: The `src/ui/` directory is read-only, preventing the addition of new `.menu` files to restore a native "Start Match" UI.

## 4. Bots & AI
**Status:** Functional
**Gap:** Low

*   **Weights**: `trap_BotLoadItemWeights` is called, implying support for external QL weight files.
*   **Logic**: Standard AAS interaction is preserved.

## 5. Summary of Outstanding Work

1.  **UI**: **WARNING**. Provide a mechanism or documentation for starting matches, as the native UI is stripped. (Mitigated by console commands).
2.  **Verification**: Ongoing regression testing.
