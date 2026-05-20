# Quake Live Reverse Engineering Mapping Round 273

## Scope

- Continued the `src/code/cgame/cg_main.c` native export reconstruction around the helper leaves adjacent to the export table.
- Focused on chat-field geometry, physics time, tracked-player notifications, client identity copying, and client speaking state.

## Evidence

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
  - `0x1004E4D0` returns the retail physics timestamp word.
  - `0x100209E0`, `0x10020A00`, and `0x10020A20` return the chat-input Y, pixel width, and character width families keyed by the retail match-summary layout flag.
  - `0x10029FF0` and `0x1002A060` arm the two tracked-player notification timers for `cg.time + 0xBB8` and replay `cg_lastmsg`.
  - `0x10020910` copies the fixed 64-client identity slab into the caller buffer, including two `0x27`-byte name copies.
  - `0x10020A40` writes the speaking flag and timestamp into the per-client sidecar and returns the client block pointer.
- `src/code/cgame/cg_public.h`
  - `cgameClientIdentity_t` keeps the recovered 40-byte display and clean-name buffers, matching the `0x27` copy plus terminator pattern.

## Source Notes

- `CG_CopyClientIdentity` now bounds against `MAX_CLIENTS` instead of `cgs.maxclients`, matching the fixed retail 64-client identity slab before the `infoValid` gate.
- `CG_SetClientSpeakingState` now uses the same fixed sidecar array bound.
- No online-service behavior was introduced; the identity transport word remains the documented zero fallback until a committed retail producer is recovered.

## Guardrail

- `tests/test_cgame_displaycontext_parity.py::test_display_context_uses_named_cvar_string_and_native_chat_helpers` now cross-checks the physics/chat helpers against their committed HLIL leafs.
- `tests/test_cgame_displaycontext_parity.py::test_cgame_native_sidecar_helpers_match_retail_export_leafs` now pins:
  - tracked-slot hold/replay behavior to `0x10029FF0` / `0x1002A060`;
  - identity copy bounds, sidecar words, and name-buffer sizes to `0x10020910`;
  - speaking-state timestamp/write behavior to `0x10020A40`.

## Parity Estimate

- Before: native sidecar helper parity was mostly reconstructed but only partially evidence-guarded, about 97%.
- After: helper semantics and bounds are now tied to the committed HLIL leaves, about 98%.
