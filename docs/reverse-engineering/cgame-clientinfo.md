# cgame `clientInfo_t` Retail Map

This note records the current reverse-engineering map for Quake Live
`cgamex86.dll` clientinfo storage and the source reconstruction now present in
`src/code/cgame/cg_local.h`, `cg_players.c`, `cg_main.c`, and `cg_newdraw.c`.

## Evidence Base

- Retail cgame owner: `cgamex86.dll`.
- Canonical HLIL:
  `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`.
- Companion Ghidra:
  `references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c`.
- Retail qagame producer:
  `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`.
- Source reconstruction:
  `src/code/cgame/cg_local.h`, `src/code/cgame/cg_players.c`,
  `src/code/cgame/cg_main.c`, `src/code/cgame/cg_newdraw.c`, and
  `src/game/match_state_keys.h`.

## Hard Retail Facts

- Retail `clientInfo_t` stride is `0x738`.
- Retail `CG_NewClientInfo` at `0x1003E640` computes
  `clientNum * 0x738 + data_10a41cf0`, clears records with
  `memset(..., 0, 0x738)`, builds a temporary `0x738` stack record, and copies
  the finished record with `memcpy(..., 0x738)`.
- Retail custom sounds live at offset `0x690` and occupy `0x80` bytes
  (`32` handles).
- Retail player animations start at offset `0x318` and use `37` records of
  size `0x18`. Retail animation frame helpers use the same `arg2 * 0x18`
  scale, and retail custom sounds begin after the animation block at `0x690`.
- Source cgame now uses a local `cgAnimation_t` with six integer fields and no
  `flipflop`, matching the retail `0x18` record size. The shared GPL
  `animation_t` remains in `bg_public.h` and the UI player code.
- A local i686 record-layout probe after this pass reports
  `sizeof(cgAnimation_t) == 0x18` and `sizeof(clientInfo_t) == 0x738`. The
  strongest recovered internal anchors now line up in source: fixed animation
  metadata starts at `0x2E0`, model handles at `0x2FC`, animations at `0x318`,
  custom sounds at `0x690`, and the recovered identity/voice/avatar tail at
  `0x710..0x734`.
- Retail animation metadata and render handle slots are now pinned individually:
  `fixedlegs`/`fixedtorso` at `0x2E0..0x2E4`, animation.cfg `headOffset` at
  `0x2E8..0x2F0`, footsteps/gender at `0x2F4..0x2F8`, legs/torso/head
  model-skin handles at `0x2FC..0x310`, and the icon shader at `0x314`.
- Source-only compatibility fields before the animation band still prevent a
  full early-slot claim. In particular, the source keeps reconstructed color
  override, country, scoreboard/team-overlay, and model-override cache fields in
  the pre-animation region, so offsets before `0x2E0` remain a mixed retail and
  source-compatibility map until each slot is independently proven.
- `src/code/cgame/cg_local.h` now exposes
  `CG_CLIENTINFO_RETAIL_OFFSET_*` constants for the recovered retail map.
  These constants describe the retail byte map, not the current C `offsetof`
  for the source compatibility fields in the early region.
- Retail score parsing mirrors live scoreboard values into clientinfo offset
  `0x12C`, while the retail player-effect lane at `0x144..0x14C` is used by
  medkit and invulnerability visual timers. The remaining `0x150` word is the
  source-ordered breath-puff timer candidate, but no committed direct retail
  consumer has been promoted yet.
- Retail identity/voice/avatar tail:

| Offset | Retail Role | Strong Evidence |
| --- | --- | --- |
| `0x710` | Privilege / identity transport parsed from key `p` | `CG_CopyClientIdentity` copies `arg2[1] = *(client * 0x738 + 0x10a42400)`. |
| `0x714` | Duel pure-spectator flag parsed from key `so` | Duel spectator sort/build code reads the slot next to `pq`. |
| `0x718` | Duel spectator queue position parsed from key `pq` | Duel spectator sort/build code reads this after `so`. |
| `0x71C` | Speaking flag | `CG_SetClientSpeakingState` writes `*(base + 0x10a4240c)`. |
| `0x720` | Speaking timestamp | `CG_SetClientSpeakingState` writes current cgame time to `*(base + 0x10a42410)`. |
| `0x728` | Steam identity low word | `CG_CopyClientIdentity` copies `data_10a42418`; avatar and mute paths read it. |
| `0x72C` | Steam identity high word | Adjacent copy/avatar/mute paths read `0x10a4241c`. |
| `0x730` | Avatar image shader handle | Avatar path checks this before requesting the host avatar handle. |

## Early Retail Slot Map

The committed Ghidra `CG_NewClientInfo` body exposes the retail stack record as
four consecutive 64-byte strings followed by parser scalars. The table below
separates observed offsets from inferred meanings:

| Offset | Retail Role | Confidence | Strong Evidence |
| --- | --- | --- | --- |
| `0x000` | `infoValid` | High | Empty configstring clears `0x738`; final copy sets the first word to `1`. |
| `0x004` | Ready flag | High | Parser writes the `rp` token into the second word before the final `0x738` copy. |
| `0x008` | Display name | High | `CG_CopyClientIdentity` copies `arg1 * 0x738 + 0x10a41cf8`; selected-player text also reads this slot. |
| `0x048` | Clean/native identity name | High | `CG_CopyClientIdentity` copies the second identity string from `0x10a41d38`. |
| `0x088` | Extended/alternate name | Medium | Placement/summary text copies `0x10a41d78` into a display buffer; this matches the consumed `xcn` lane. |
| `0x0C8` | Country code | High | The flag shader path formats `ui/assets/flags/%s.tga` from `0x10a41db8`. |
| `0x108` | Team | High | Team comparisons repeatedly read `data_10a41df8`; `CG_NewClientInfo` stores the parsed team token into `local_680`. |
| `0x10C` | Bot skill integer | High | `CG_NewClientInfo` stores the parsed `skill` integer into `local_67c`. |
| `0x110` | Bot skill float | High | The same `skill` token is parsed through `atof` into `local_678`. |
| `0x114` | Primary color vector | High | Palette index `c1` writes three floats at `local_674/local_670/local_66c`. |
| `0x120` | Secondary color vector | High | Palette index `c2` writes three floats at `local_668/local_664/local_660`. |
| `0x12C` | Score mirror | High | Retail score parsers write `0x10a41e1c` for each parsed client, and ownerdraw/score value helpers read the same slot. |
| `0x130` | Handicap | High | `CG_NewClientInfo` parses `hc`, and head/model scale helpers divide `0x10a41e20` by `100.0`. |
| `0x134` | Wins | High | Summary/profile code formats the value at `0x10a41e24` in a `%d/%d` pair. |
| `0x138` | Losses | High | The adjacent value at `0x10a41e28` is the other half of the `%d/%d` pair. |
| `0x13C` | Team task | High | Parser stores the `tt` token here; selected-player team-task setup reads `0x10a41e2c`. |
| `0x140` | Team-leader flag | Medium | Parser stores the `tl` token next to team task; this pass did not find a strong direct retail consumer. |
| `0x144` | Medkit usage time | High | The holdable-use path writes current cgame time to `0x10a41e34`, and player rendering gates the medkit sprite for `500` ms from that slot. |
| `0x148` | Invulnerability start time | High | Player rendering sets/clears `0x10a41e38` while `PW_INVULNERABILITY` is active and uses it for the `250` ms scale-in fade. |
| `0x14C` | Invulnerability stop time | High | Player rendering refreshes `0x10a41e3c` while invulnerability is active and uses it for the `250` ms scale-out fade. |
| `0x150` | Breath-puff time | Medium | This is the remaining single word before the proven model-name band and matches GPL source ordering, but no direct committed retail read/write has been promoted. |
| `0x154` | Body model name | High | `CG_NewClientInfo` writes `local_634`; `CG_LoadClientInfo` passes `client + 0x154` as the lower/upper model token and sound directory. |
| `0x194` | Body skin name | High | The retail skin normalizer writes `client + 0x194`; `CG_RegisterClientModelname` passes this as the body skin token. |
| `0x1D4` | Icon body model name | High | The loader formats `models/players/%s/icon_%s.tga` from `client + 0x1D4` and `client + 0x214`; default fallbacks overwrite this slot with `sarge`. |
| `0x214` | Icon body skin name | High | Adjacent icon-format argument; default fallbacks write `red`, `blue`, or `default` here. |
| `0x254` | Head model name | High | `CG_LoadClientInfo` passes `client + 0x254` as the head model token and the override helper rewrites this slot when head overrides apply. |
| `0x294` | Head skin name | High | Head-skin normalizer and skin loader compare/copy this slot beside the head model token. |
| `0x2D4` | Deferred-model flag | High | `CG_LoadClientInfo` clears this slot after a full load; deferred copy helpers set it when reusing another model. |
| `0x2D8` | Model bounding-box scale | High | `CG_UpdateClientHeadOffset` stores `(56 / totalHeight) * playerModelScale` here and the copy helper preserves it separately from the animation `headOffset` vector. |
| `0x2DC` | New-animation flag | High | `CG_LoadClientInfo` clears this slot, then sets it if `tag_flag` exists on the torso model. |
| `0x2E0` | Fixed-legs flag | High | `CG_ParseAnimationFile` sets this on the `fixedlegs` token; player-angle code reads the same flag to lock leg yaw/pitch/roll. |
| `0x2E4` | Fixed-torso flag | High | `CG_ParseAnimationFile` sets this on the `fixedtorso` token; player-angle code reads the same flag to zero torso pitch. |
| `0x2E8` | Head offset X | High | The `headoffset` parser writes three floats starting here, and deferred-copy code preserves this vector from `0x2E8..0x2F0`. |
| `0x2EC` | Head offset Y | High | Adjacent `headoffset` vector element copied by the retail model-cache reuse helper. |
| `0x2F0` | Head offset Z | High | Adjacent `headoffset` vector element copied by the retail model-cache reuse helper. |
| `0x2F4` | Footstep type | High | `CG_ParseAnimationFile` writes the `footsteps` selector values `0..4`; deferred-copy code preserves this word. |
| `0x2F8` | Gender | High | `CG_ParseAnimationFile` writes male/female/neuter values from the `sex` token; deferred-copy code preserves this word. |
| `0x2FC` | Legs model handle | High | `CG_RegisterClientModelname` writes the lower model here; render paths test/read this handle and tag-torso queries use it. |
| `0x300` | Legs skin handle | High | `CG_RegisterClientSkin` writes the lower skin here; player and preview render paths read it as the legs custom skin. |
| `0x304` | Torso model handle | High | `CG_RegisterClientModelname` writes the upper model here; render paths test/read it and tag-head/weapon queries use it. |
| `0x308` | Torso skin handle | High | `CG_RegisterClientSkin` writes the upper skin here; player and preview render paths read it as the torso custom skin. |
| `0x30C` | Head model handle | High | `CG_RegisterClientModelname` writes the head model here; render paths test/read it and model-scale bounds use it. |
| `0x310` | Head skin handle | High | `CG_RegisterClientSkin` writes the head skin here; player and preview render paths read it as the head custom skin. |
| `0x314` | Model icon shader | High | `CG_RegisterClientModelname` writes the icon shader here; profile/placement/head-icon paths read this slot. |

## Configstring Keys

The retail cgame string cluster includes these compact keys:

| Key | Observed Consumer |
| --- | --- |
| `cn` | Clean name string copied to the native identity sidecar. |
| `xcn` | Extended/alternate name string used by placement/profile text paths. |
| `c` | Country code, loaded into the flag shader path. |
| `c1`, `c2` | One-based `1..26` Quake Live color palette indices. |
| `skill` | Bot skill as both integer and float. |
| `hc` | Handicap. |
| `w`, `l` | Duel/tournament wins and losses. |
| `t` | Team. |
| `tt`, `tl` | Team task and team-leader flags. |
| `rp` | Ready flag. |
| `p` | Privilege / identity transport sidecar word. |
| `so` | Pure spectator flag. |
| `pq` | Spectator queue position. |
| `st` | SteamID64 split into low/high identity words. |
| `hmodel` | Head model token. |

The qagame retail producer proves the networked `ClientUserinfoChanged`
formats:

- Bot format:
  `n\%s\t\%i\model\%s\hmodel\%s\c1\%s\c2\%s\hc\%i\w\%i\l\%i\skill\%s\tt\%d\tl\%d\rp\%d\p\%d\so\%i\pq\%i`
- Real-client format:
  `n\%s\t\%i\model\%s\hmodel\%s\c1\%s\c2\%s\hc\%i\w\%i\l\%i\tt\%d\tl\%d\rp\%d\p\%d\so\%i\pq\%i\st\%llu\c\%s`

No committed qagame evidence currently shows `cn` or `xcn` being emitted by
`ClientUserinfoChanged`; the source therefore consumes those keys when present
but falls back to a locally cleaned `n` display name when absent.

## Source Reconstruction Status

The current source reconstructs the retail wiring, cgame animation record,
outer clientinfo stride, and strongest internal byte anchors without yet
claiming binary-exact early member offsets:

- `match_state_keys.h` now names `cn`, `xcn`, compact `c`, `st`, `rp`, `p`,
  `so`, and `pq`, with compatibility fallbacks for legacy `country` and
  `steamid`.
- `ClientUserinfoChanged` emits the retail qagame compact core for ready,
  privilege, duel spectator flags, SteamID, and country.
- `CG_NewClientInfo` now parses:
  - display name `n`
  - clean name `cn` with generated clean-name fallback
  - extended name `xcn`
  - `skill` as both integer and float
  - `rp` into `clientInfo_t.ready`
  - `p` into `clientInfo_t.privilege`
  - `so` and `pq`
  - compact `st` / legacy `steamid`
  - compact `c` / legacy `country`
- `CG_CopyClientIdentity` exports `clientNum`, `privilege`, identity low/high,
  display name, and cached clean name, matching the retail copy leaf more
  closely than the previous hard-coded zero transport word.
- `CG_SetClientSpeakingState` now writes `clientInfo_t.speaking` and
  `clientInfo_t.speakingTime`; scoreboard social icons consume those fields.
- Profile and placement avatar draws prefer `clientInfo_t.avatarImageHandle`,
  then fall back to the host avatar import when the cached handle is still zero.
- Cgame-only animation parsing and lerp-frame consumers now use
  `cgAnimation_t`, preserving the retail `0x18` record and removing the
  source-only `flipflop` branch from cgame animation playback.
- Shared `animation_t` remains unchanged for `bg_public.h` and UI code, keeping
  the compatibility surface outside cgame intact.
- `clientInfo_t` carries named retail gap pads so the cgame x86 source stride
  matches the retail `0x738` slab size while the recovered anchor fields occupy
  their observed offsets.
- The six 64-byte retail model strings are now named in the byte map:
  body model/skin at `0x154..0x1D3`, icon body model/skin at `0x1D4..0x253`,
  and head model/skin at `0x254..0x2D3`.
- Source reconstruction now separates the retail `0x2D8` model bounding-box
  scale scalar from the animation.cfg `headOffset` vector at `0x2E8..0x2F0`.
  `CG_PlayerModelBoundingBoxScale` and the browser model preview consume
  `clientInfo_t.modelScale`, while head icon drawing continues to apply
  `clientInfo_t.headOffset` as a vector.
- The animation metadata and render-handle band is now named slot-by-slot:
  `fixedlegs`, `fixedtorso`, `headOffset`, `footsteps`, `gender`, model/skin
  handles, `modelIcon`, `animations`, and `sounds` line up with retail
  `0x2E0..0x690` anchors. Retail `CG_CopyClientInfoModel` starts its metadata
  copy at `0x2E8`, so the reconstruction intentionally does not copy
  `fixedlegs` or `fixedtorso` through deferred asset reuse.
- `CG_ParseTeamInfo` accepts the retail compact `tinfo` command shape: count
  plus client numbers. The retail `tinfo` parser only rebuilds
  `sortedTeamPlayers`, and the reconstructed qagame `TeamplayInfoMessage`
  producer now emits that compact shape.
- Source-compatible six-field `tinfo` rows are still accepted for older/source
  servers, but retail-style teammate overlay vitals now arrive through
  `entityState_t` snapshot fields. Cgame mirrors those replicated health,
  armor, current weapon, location, and powerup bits into source compatibility
  `clientInfo_t` sidecars for menu-HUD and legacy overlay consumers.
- Retail cgame does not expose the source-era lowercase `"teamoverlay"`
  userinfo cvar. `cg_drawTeamOverlay` and its size/opacity/offset cvars remain
  local HUD controls; qagame owns the compact row-list refresh cadence.
- `cg_local.h` now names the recovered retail byte map with
  `CG_CLIENTINFO_RETAIL_OFFSET_*` constants. The early constants are evidence
  markers for future repacking, not claims that every current source member has
  the same `offsetof`.
- The cgame source layout now moves the recovered native tail behind
  `sounds[MAX_CUSTOM_SOUNDS]`: `privilege` at `0x710`, `spectateOnly` at
  `0x714`, `spectatorQueuePosition` at `0x718`, speaking state at
  `0x71C..0x720`, Steam identity at `0x728..0x72C`, and cached avatar handle at
  `0x730`.
- `retailIdentityPad` and `retailLayoutPad` reserve the currently observed
  retail gaps at `0x724` and `0x734` respectively.

## Remaining Layout Work

The cgame animation-record split, strongest internal anchor repack, score
mirror, compact team-info client list, entity-state team-overlay vitals,
medkit/invulnerability timer lanes, and the post-scalar animation
metadata/model-handle band are now complete. The next binary-layout pass should:

1. Resolve the remaining early-slot medium-confidence semantics, especially the
   `teamLeader` consumer set and the unobserved `0x150` breath-puff timer
   candidate.
2. Decide which source-only compatibility fields should remain in the retail
   slab and which deserve sidecar storage once stronger evidence separates
   retail fields from reconstruction conveniences.
3. Audit remaining consumers of the source-compatibility teammate vital fields
   before a future clientinfo repack; those fields are fed by entity-state
   snapshots and legacy six-field `tinfo` rows, not proven retail clientinfo
   offsets.
4. Replace the remaining named retail pads with recovered fields if later
   evidence identifies their roles.
5. Regenerate top-level `cgs_t` offsets after any future size-affecting
   clientinfo or media repack.

Confidence is high for the key names, qagame producer formats, identity tail,
speaking tail, avatar tail, score mirror, compact team-info client list,
medkit/invulnerability effect timers, retail model-string band, pre-animation
model-scale lanes, animation metadata, render handles, and `0x738` stride.
Confidence remains medium for
`teamLeader`, the `0x150` breath-puff timer candidate, and the exact retail
transport/storage used by teammate location, health, armor, weapon, and powerup
overlay values.
