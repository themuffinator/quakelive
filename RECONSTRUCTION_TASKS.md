# Reconstruction Tasks

1.  **Implement `randommap` logic**
    - **File:** `src/code/game/g_svcmds_new.c`
    - **Description:** Replace the placeholder `Cmd_RandomMap_f` with logic that loads `mapcycle.txt` (or scans `maps/` if missing) and selects a random map to restart the server with.

2.  **Remove "Attacker Protect" bonus**
    - **File:** `src/code/game/g_team.c`
    - **Description:** Remove the `CTF_CARRIER_DANGER_PROTECT_BONUS` logic in `Team_FragBonuses` to match Quake Live parity, which removed this mechanic.

3.  **Reverse `cg_localents.c`**
    - **File:** `src/code/cgame/cg_localents.c`
    - **Description:** Fully reverse the `CG_AddType10` function (marked with TODO) to implement the missing local entity visual effect (likely a specific explosion or impact effect).

4.  **Investigate "priv" handshake**
    - **File:** `src/code/game/g_client.c`
    - **Description:** Investigate the TODO in `ClientConnect` regarding whether Quake Live's native code sends an additional "priv" handshake message for private clients.

5.  **Implement Air Control Physics**
    - **File:** `src/code/game/bg_pmove.c`
    - **Description:** Implement CPMA-style air control logic in `PM_AirMove` when `pm_aircontrol` is non-zero, allowing tighter turning in mid-air.

6.  **Implement Ramp Jump Physics**
    - **File:** `src/code/game/bg_pmove.c`
    - **Description:** Verify and implement `PM_RampJump` to scale jump velocity when jumping off ramps if `PMF_RAMP_JUMP` is active.

7.  **Implement Double Jump Physics**
    - **File:** `src/code/game/bg_pmove.c`
    - **Description:** Verify and implement `PM_DoubleJump` to allow a second jump in mid-air if `PMF_DOUBLE_JUMP` is active (e.g. in specific gametypes or with powerups).

8.  **Implement Step Jump Physics**
    - **File:** `src/code/game/bg_pmove.c`
    - **Description:** Verify and implement `PM_StepJump` logic to allow jumping while stepping up without losing velocity.

9.  **Enhance `target_give`**
    - **File:** `src/code/game/g_target.c`
    - **Description:** Modify `target_give` to support a "give" spawn key that accepts a string of item names (e.g. "weapon_rocketlauncher ammo_rockets"), allowing mappers to grant items without pointing to entities.

10. **Implement `callvote teamsize` validation**
    - **File:** `src/code/game/g_svcmds.c`
    - **Description:** Add validation to `Svcmd_TeamSize_f` (and potentially `Cmd_CallVote_f` handling) to ensure the requested team size is valid for the current `g_maxclients` and doesn't break the active match state.
