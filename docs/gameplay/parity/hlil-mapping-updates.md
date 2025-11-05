# HLIL Mapping Updates

This log captures notable updates to the High Level Intermediate Language (HLIL) mapping used when translating Quake Live gameplay code into the active source tree. Cross-referencing these changes ensures that gameplay engineers, UI maintainers, and QA can rely on the same canonical references when validating behaviour.

## Recent Updates

### May 2024
- **Rebuilt weapon handling signatures** – Normalised function names for the `FireWeapon` family to follow the HLIL split naming scheme (`FireWeapon_Rocket`, `FireWeapon_Rail`, etc.) and updated the ledger to point at the new files. Owner: Modes (@mutator-crew).
- **Synced movement helper functions** – Added explicit mapping between `PmoveSingle` helpers in `bg_pmove.c` and the HLIL files within `qagamex86.dll_split/PmoveSingle_*.md` to prevent drift when reviewing air-control patches. Owner: Movement (@physics-guild).
- **UI feeder indices audit** – Documented the relationship between `UI_FeederSelection` HLIL dumps and the Quake Live ruleset toggles exposed in `ui_gameinfo.c`. Owner: Rulesets (@ui-systems).

### April 2024
- **Scoreboard timing probes** – Linked `CG_DrawScoreboard` HLIL outputs to the race/CTF timer work-in-progress branch, enabling HUD maintainers to benchmark parity before merging. Owner: HUD (@hud-taskforce).
- **Backend handshake review** – Captured the mapping between `ClientBegin` HLIL analysis and `g_client.c` initialisation order, highlighting hook points needed by the services team. Owner: Backend Integrations (@services-team).

## Coordination Checklist
- [ ] Confirm that any new HLIL exports are added to `references/hlil/quakelive/` with consistent naming.
- [ ] Ping the listed code owner in `#gameplay-parity` once an HLIL update lands so they can validate assumptions.
- [ ] Mirror changes in the Gameplay Parity Ledger to keep reference pointers in sync.

## Contacts
- **Documentation Steward:** @analysis-ops
- **HLIL Export Maintainer:** @reverse-core
