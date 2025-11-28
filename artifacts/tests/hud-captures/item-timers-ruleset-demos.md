# Item timer and ruleset demo captures (2025-01-09)

- **Standard ruleset (default factory fallback)**
  - Server started with `g_ruleset` left at the default and `g_factory` unset; the game latched the ruleset token into `g_factory` before broadcasting server info so factory-driven HUD assets follow the competitive defaults.
  - `g_itemTimers` remained enabled with the clamped `g_itemHeight` default of `20`, and clients received the `itemcfg 1 20` broadcast on connect. Demo: `timers-standard.dm_73` (reverse build) paired against `ql-standard-refs.dm_73` (reference) showing matching HUD timer spacing.
- **PQL ruleset**
  - `g_ruleset pql` with an empty `g_factory` seeded the same PQL token into the factory selector, keeping the competitive config paths aligned while the custom-settings digest captured the non-standard ruleset.
  - Item timers stayed on with the default height; demo pair `timers-pql.dm_73` (reverse build) vs `ql-pql-refs.dm_73` confirms the HUD countdown rows match Quake Live timing and layout.

Both capture pairs were recorded from fresh sessions after map load, immediately after the server broadcasted the item timer config to late joiners. QA retains the demo files alongside the referenced command lines.
