# Competitive ruleset + item timer comparison demos

The raw demo captures live on the QA share under `parity/competitive-rulesets/2024-11-05/` to avoid committing binary blobs to the
repo. The recordings were produced with the updated ruleset config parsing and item timer HUD overrides enabled.

## Captured sessions
- **standard-loadouts.dm_73** – Factory: `standard`, ruleset token `standard:rulesets/standard.cfg`, warmup item timers disabled by
default. Verified that switching factories kept the config path stable while the HUD timers remained off until explicitly
enabled through the client override.
- **pql-hud-training.dm_73** – Factory: `pql`, ruleset token `pql:rulesets/pql.cfg`, server broadcast `itemcfg 1 20`. Confirmed
that forced HUD timers appeared on all clients and respected the server height, with additional local toggles able to re-enable
when the server cleared the override mid-map.
- **classic-client-optin.dm_73** – Factory: `classic`, default ruleset fallback path `rulesets/classic.cfg`, server broadcast
`itemcfg 0 0`. Clients opted into timers with `cg_itemTimers 1`, and the HUD spacing defaulted to the Quake Live fallback height
(20) even without a server height present.

## Notes for QA
- Each demo pairs with the console log saved under `artifacts/tests/logs/competitive-rulesets/<demo>.log` so regression scripts can
cross-check the `itemcfg` servercommands and `ui_rulesets` feeder output.
- Use the scoreboard overlay at 00:15 in `pql-hud-training.dm_73` to validate that the server-enforced timers flag is displayed as
`Item timers on` regardless of the client preference toggle.
