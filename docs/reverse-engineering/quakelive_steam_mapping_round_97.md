# Quake Live Steam Host Mapping Round 97

## Scope

This round closes the `idZMQ` RCON peer-table seam that [Round 95](./quakelive_steam_mapping_round_95.md)
and [Round 96](./quakelive_steam_mapping_round_96.md) intentionally left
partially unnamed:

1. the exact-match lookup and insert path used when a new RCON peer first
   sends a command
2. the single-node erase, subtree free, full clear, and erase-range helpers
   used by broadcast disconnect handling and `idZMQ_Destroy`

The evidence order stayed the same:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`
- earlier ZMQ ownership notes in
  [Round 95](./quakelive_steam_mapping_round_95.md) and
  [Round 96](./quakelive_steam_mapping_round_96.md)

These helpers are still tree-management machinery rather than user-facing host
exports. The observed facts are the callers, the peer-identity string
comparisons, and the lifecycle effects on the retained tree at `this + 0x14`.
The `Find` / `Insert` / `Erase` / `Clear` verbs below are the narrow semantic
inference that fits those observations without claiming more source-level
intent than the retail evidence supports.

## `idZMQ` RCON Peer-Table Helpers

The retained peer-table ownership is now tight enough to name the whole seam.

The call relationships are compact and consistent:

- `sub_4F4ED0` logs `zmq RCON client connected: %s\n` only when
  `sub_4F4910(arg1 + 0x14, &var_10, &var_8)` returns the end sentinel at
  `this + 0x18`
- that same connect path immediately calls
  `sub_4F49C0(arg1 + 0x14, &var_14, sub_4F4640(arg1 + 0x14), nullptr)` to
  materialize the new peer entry
- `sub_4F4D40` logs `zmq RCON client disconnected: %s\n` and removes the dead
  node through `sub_4F46B0(arg1 + 0x14, &var_8, i)`
- `sub_4F5080` clears the table during object destruction via
  `sub_4F4FE0(&arg1[5], &var_18, *eax_3, eax_3)`
- `sub_4F4FE0` promotes full-range erasure into `sub_4F4E80(arg1)`, while
  `sub_4F4E80` recursively frees descendant nodes through `sub_4F4980(...)`
  and then resets the sentinel links and element count

That gives one stable ownership surface for the retained peer tree.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4F46B0` (`0x004F46B0`) | `idZMQ_EraseRconPeer` | Observed + inferred | Single-node peer-table erase helper. Removes one retained RCON peer node, rebalances the tree, updates the begin/end links, and decrements the peer count. |
| `sub_4F4910` (`0x004F4910`) | `idZMQ_FindRconPeer` | Observed + inferred | Exact-match lookup helper for the peer-identity string received from the RCON socket. Returns the end sentinel when the peer key is absent. |
| `sub_4F4980` (`0x004F4980`) | `idZMQ_FreeRconPeerSubtree` | Observed + inferred | Recursive subtree-free helper used only by the full peer-table clear path. Walks descendant nodes and releases them depth-first. |
| `sub_4F49C0` (`0x004F49C0`) | `idZMQ_InsertRconPeer` | Observed + inferred | Peer-table insert helper. Walks the retained tree by identity string, discards the newly allocated node on duplicate keys, and otherwise inserts it through the shared tree primitive. |
| `sub_4F4E80` (`0x004F4E80`) | `idZMQ_ClearRconPeers` | Observed + inferred | Full peer-table clear helper. Deletes all retained RCON peers, resets the sentinel/head links, and zeroes the stored peer count. |
| `sub_4F4FE0` (`0x004F4FE0`) | `idZMQ_EraseRconPeerRange` | Observed + inferred | Range-erase helper over the retained peer tree. Uses `idZMQ_ClearRconPeers` for full-table erasure and otherwise loops peer-by-peer through `idZMQ_EraseRconPeer`. |

Two practical takeaways from this pass:

- the retained `idZMQ` RCON peer table is now documented as a coherent
  ownership surface rather than a loose cluster of STL-looking helpers
- the disconnect and destroy paths now read cleanly: broadcast failures erase a
  single peer, while object destruction erases the full retained range

## New High-Confidence Aliases Added This Round

- `idZMQ` RCON peer-table helpers:
  - `sub_4F46B0`
  - `sub_4F4910`
  - `sub_4F4980`
  - `sub_4F49C0`
  - `sub_4F4E80`
  - `sub_4F4FE0`

## Open Questions

1. `sub_4F4640` still looks like the peer-node allocator / constructor, but the
   current decompiler signature hides the peer-identity argument behind a stack
   artifact, so I left it unnamed.
2. `sub_4F2900` remains the only small browser-input helper in this block that
   still needs one more pass before promotion.
3. The lower tree primitives under this seam (`sub_4F41B0`, `sub_4F4410`,
   rotations, and iterator helpers) still look more like compiler/STL
   machinery than stable host-owned behavior names.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `975` raw alias entries, `974` address-backed alias
  entries

## Completion Stats After Round 97

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `975` raw alias entries, `974` address-backed
  aliases
- Address-backed coverage: `17.796%` of `5473` functions
- Alias delta this round: `6`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes the retained `idZMQ` peer-table seam,
but it does not change the writable-source parity estimate by itself.
