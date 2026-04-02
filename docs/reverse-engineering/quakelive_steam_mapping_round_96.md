# Quake Live Steam Host Mapping Round 96

## Scope

This round closes two smaller but high-value seams that were still open after
[Round 95](./quakelive_steam_mapping_round_95.md):

1. the remaining browser runtime helper at `sub_4F2590`
2. the wrapper-versus-method split in the `idZMQ` startup and shutdown path

The evidence order stayed the same:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`
- earlier ZMQ notes in
  [Round 94](./quakelive_steam_mapping_round_94.md) and
  [Round 95](./quakelive_steam_mapping_round_95.md)

This pass adds six new aliases and corrects four earlier ZMQ names now that the
`idZMQ` field layout is explicit.

## Browser Runtime Helper

Round 94 left `sub_4F2590` unnamed because the body was only one vtable jump.
The ownership evidence is now stable enough to promote it:

- `sub_4F2D30` stores the result of `Awesomium::WebCore::Initialize(...)` in
  `data_12d304c`
- `004CC990` calls `sub_4F2590()` once per rendered client frame
- `sub_4F2590` reads `data_12d304c`, rearms the browser-input flag when needed,
  and tail-jumps through the `WebCore` vtable slot at `+0x18`

That is sufficient to treat the helper as the retained per-frame `WebCore`
update owner.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F2590` (`0x004F2590`) | `QLWebCore_Update` | Observed | Per-frame browser-core update wrapper; operates on the retained `Awesomium::WebCore` pointer in `data_12d304c` and executes its update slot once per rendered client frame. |

## `idZMQ` Wrapper Split

Round 94 named the ZMQ startup methods before the `idZMQ` RTTI anchor was used.
Round 95 then established that `data_5756FC` is an `idZMQ` instance. That
finally makes the internal/object split explicit:

- `data_5756fc` is typed as `idZMQ::vftable`
- `data_575700`, `data_575704`, `data_575708`, and `data_57570c` are object
  fields at `+0x4`, `+0x8`, `+0xc`, and `+0x10`
- `sub_4F4140`, `sub_4F4130`, and `sub_4F43A0` are thin global wrappers that
  tailcall the retained object methods with `&data_5756fc`

That means the earlier `Zmq_*` names on the object methods were one layer too
high. The corrected split is:

- `idZMQ_*` for retained object methods
- `Zmq_*` for the global wrappers and lifecycle helpers around `data_5756fc`

### Alias corrections

| Raw symbol | Previous alias | Corrected alias | Basis |
| --- | --- | --- | --- |
| `sub_4F3D70` (`0x004F3D70`) | `Zmq_ApplyPasswords` | `idZMQ_ApplyPasswords` | Operates directly on the `idZMQ` field at `this + 4`. |
| `sub_4F3F20` (`0x004F3F20`) | `Zmq_UpdatePasswords` | `idZMQ_UpdatePasswords` | Re-reads password cvars, reapplies them through the retained object fields, and logs from object context. |
| `sub_4F3F80` (`0x004F3F80`) | `Zmq_RegisterCvarsAndInitRcon` | `idZMQ_RegisterCvarsAndInitRcon` | Registers cvars and initializes the object-owned RCON/runtime fields at `+4`, `+0xc`, and `+0x10`. |
| `sub_4F4210` (`0x004F4210`) | `Zmq_InitStatsPublisher` | `idZMQ_InitStatsPublisher` | Initializes the object-owned stats publisher socket at `+8` and reuses the shared object state at `+4`. |

### New global wrappers and shutdown owners

The callsites and field usage now make six additional aliases stable.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F4130` (`0x004F4130`) | `Zmq_UpdatePasswords` | Observed | Global wrapper that forwards the password-refresh path into the retained `idZMQ` instance. The main frame loop calls it when password-cvar modification counts change. |
| `sub_4F4140` (`0x004F4140`) | `Zmq_RegisterCvarsAndInitRcon` | Observed | Global wrapper that initializes the retained `idZMQ` RCON/runtime state during host startup. |
| `sub_4F43A0` (`0x004F43A0`) | `Zmq_InitStatsPublisher` | Observed | Global wrapper that initializes the retained `idZMQ` stats publisher during server startup. |
| `sub_4F3DD0` (`0x004F3DD0`) | `Zmq_ShutdownStatsPublisher` | Observed | Server-shutdown helper; closes the `idZMQ` stats publisher socket at object field `+0x8`. `SV_Shutdown` calls it immediately after `game.end` publication and browser teardown. |
| `sub_4F3DF0` (`0x004F3DF0`) | `Zmq_ShutdownRuntime` | Observed | Process-shutdown helper; closes the object-owned RCON socket at `+0xc`, clears the runtime helper at `+0x10`, and tears down the shared actor/context at `+0x4`. |
| `sub_4F2590` (`0x004F2590`) | `QLWebCore_Update` | Observed | Included here for completeness as the other newly promoted runtime helper in this pass. |

Two practical takeaways from this split:

- the ZMQ host layer now reads cleanly as a retained `idZMQ` object with thin
  global wrappers, not as one flat procedural block
- the stats publisher and the broader RCON/runtime teardown really are separate
  lifecycle owners

## New High-Confidence Aliases Added This Round

- browser runtime:
  - `sub_4F2590`
- ZMQ wrappers and shutdown:
  - `sub_4F3DD0`
  - `sub_4F3DF0`
  - `sub_4F4130`
  - `sub_4F4140`
  - `sub_4F43A0`

## Open Questions

1. `sub_4F2900` remains the only small browser-input helper in this block that
   still needs one more pass before promotion.
2. The `idZMQ` peer-table helpers at `sub_4F4910`, `sub_4F49C0`, `sub_4F4E80`,
   and `sub_4F4FE0` are structurally bounded now, but they are still mostly
   ownership/tree machinery rather than user-facing subsystem behaviors.
3. The larger `0x004F46B0` tree-erase helper likely belongs to the same
   `idZMQ` peer-management surface, but this round did not need a stable
   semantic name for it.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `969` raw alias entries, `968` address-backed alias
  entries

## Completion Stats After Round 96

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `969` raw alias entries, `968` address-backed
  aliases
- Address-backed coverage: `17.687%` of `5473` functions
- Alias delta this round: `6`
- Alias corrections this round: `4`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes the remaining browser-core runtime
helper and clarifies the `idZMQ` lifecycle split, but it does not change the
writable-source parity estimate by itself.
