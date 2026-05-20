# cgame `localEntity_t` Layout Map

This note maps the retail-compatible x86 layout of `localEntity_t` used by
`cgamex86.dll` onto the current `src/code/cgame/cg_local.h` definition. The
goal is to separate hard layout facts from the way retail reuses the same node
for fragments, smoke puffs, explosions, score plums, lightning beams, and the
kamikaze / invulnerability composites.

## Method

- Layout facts come from a local x86 record-layout dump of `localEntity_t`,
  `trajectory_t`, `refEntity_t`, and `leType_t` using
  `clang -target i686-pc-windows-msvc -DID_INLINE=__inline -Xclang -fdump-record-layouts`
  against `src/code/cgame/cg_local.h`.
- Member roles were cross-checked against the owning pool and dispatcher in
  `src/code/cgame/cg_localents.c`, plus the main producer sites in
  `src/code/cgame/cg_effects.c`, `src/code/cgame/cg_weapons.c`, and
  `src/code/cgame/cg_players.c`.
- Retail parity was cross-checked against the HLIL local-entity dispatcher at
  `0x10020790`, which matches the source-side `CG_AddLocalEntities` switch and
  confirms the same `leType_t` ordinal family.

## Hard Layout Facts

- `sizeof(trajectory_t) = 0x24` (`36`) in the current source tree. The shared
  `bg_misc` evaluator now recognizes retail type `6` (`TR_QL_ACCEL`) when a
  caller provides the extra scalar immediately after `trDelta`, while the
  local-entity source layout keeps that scalar in bridge fields below.
- `sizeof(refEntity_t) = 0x8C` (`140`).
- `sizeof(localEntity_t) = 0x12C` (`300`) in the recovered retail-compatible
  x86 layout.
- On retail-compatible x86, the high-level banding is:
  - list ownership at `0x000`
  - type / lifetime / fade metadata at `0x008`
  - motion trajectories at `0x020`
  - shared numeric effect payload at `0x068`
  - two unresolved dwords at `0x090`
  - retail fragment mark / trail-sound selectors at `0x098`
  - embedded render payload `refEntity` at `0x0A0`
- `localEntity_t` instances live in the fixed pool
  `cg_localEntities[MAX_LOCAL_ENTITIES]`, with `cg_activeLocalEntities` as a
  doubly linked sentinel head and `cg_freeLocalEntities` as a singly linked
  free list.

## Top-Level Member Map

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x000` | `prev` | `localEntity_t *` | Previous node in the active doubly linked list; unset for free-list nodes. |
| `0x004` | `next` | `localEntity_t *` | Next node in the active list and the only link used by the free list. |
| `0x008` | `leType` | `leType_t` | Dispatcher key consumed by `CG_AddLocalEntities` and the retail `0x10020790` switch. |
| `0x00C` | `leFlags` | `int` | Per-type behavior flags such as no-scale puffs, fragment tumble, and kamikaze sound latches. |
| `0x010` | `startTime` | `int` | Spawn time anchor used by fade, animation, and time-window logic. |
| `0x014` | `endTime` | `int` | Expiry time checked by the dispatcher before any type-specific add path runs. |
| `0x018` | `fadeInTime` | `int` | Optional secondary timing anchor used by fade-in puffs; otherwise often left at zero. |
| `0x01C` | `lifeRate` | `float` | Precomputed reciprocal lifetime scale, typically `1.0 / (endTime - startTime)` or the fade-in adjusted variant. |
| `0x020` | `pos` | `trajectory_t` | Translational motion state for fragments, puffs, and other moving local entities. |
| `0x044` | `angles` | `trajectory_t` | Angular motion state for tumbling fragments and a scratch rotation source for the kamikaze second shockwave. |
| `0x068` | `bounceFactor` | `float` | Reflection damping factor applied by `CG_ReflectVelocity`. |
| `0x06C` | `color[4]` | `float[4]` | Normalized RGBA baseline reused by fade and composite-light paths. |
| `0x07C` | `radius` | `float` | Shared scalar payload: puff radius, fade baseline, or score storage for `LE_SCOREPLUM`. |
| `0x080` | `light` | `float` | Dynamic-light intensity baseline for explosion-style effects. |
| `0x084` | `lightColor` | `vec3_t` | Dynamic-light RGB for explosion-style effects. |
| `0x090` | `posTrajExtra` | `float` | Source-side bridge for the retail `pos` trajectory extension dword (`trajectory_t[9]`), consumed by the cgame-only type-`6` evaluator used by `LE_05` tracer shells and `LE_FRAGMENT_14` sphere shards. |
| `0x094` | `anglesTrajExtra` | `float` | Source-side bridge for the matching retail `angles` trajectory extension dword. No strongly owned producer is recovered for it yet, but the local layout keeps the companion slot. |
| `0x098` | `fragmentMarkType` | `leFragmentMarkType_t` | Retail fragment-only selector for impact-mark families: burn, smaller burn, DLC blood spray, ice mark, or none. |
| `0x09C` | `fragmentBounceSoundType` | `leFragmentBounceSoundType_t` | Retail fragment-only selector for both impact bounce sounds and the blood / ice in-flight trail hooks. |
| `0x0A0` | `refEntity` | `refEntity_t` | Embedded renderer-facing payload submitted by the add paths. |

Retail `CG_LightningBoltBeam` uses this embedded `refEntity` as a short-lived
`RT_LIGHTNING` wrapper with `customShader` selected from the active
`lightningStyleShaders[]` slot and `radius = 256.0f`.

## Embedded `trajectory_t`

Both `pos` and `angles` are full `trajectory_t` records:

| Offset in `trajectory_t` | Member | Type | Role in `localEntity_t` |
| --- | --- | --- | --- |
| `0x00` | `trType` | `trType_t` | Motion mode such as `TR_LINEAR`, `TR_GRAVITY`, `TR_STATIONARY`, or the retail cgame-only extension value `6`. |
| `0x04` | `trTime` | `int` | Start time for trajectory evaluation and bounce resets. |
| `0x08` | `trDuration` | `int` | Structurally present, but not strongly owned by the current local-entity producer set. |
| `0x0C` | `trBase` | `vec3_t` | Base position or base angles. |
| `0x18` | `trDelta` | `vec3_t` | Velocity or angular velocity; also rewritten by bounce reflection. |

Retail `cgamex86.dll` extends the local-entity trajectory contract with a
companion scalar at `trajectory_t[9]` for type `6`, evaluated as:

- `x = base.x + delta.x * t`
- `y = base.y + delta.y * t`
- `z = base.z + delta.z * t - 0.5 * extra * t^2`
- `delta.z = trDelta.z - extra * t`

## Hot `refEntity_t` Members

`refEntity_t` is embedded whole, but the local-entity paths strongly exercise a
smaller hot subset rather than every render field uniformly.

| Offset in `refEntity` | Member | Type | Role in `localEntity_t` paths |
| --- | --- | --- | --- |
| `0x00` | `reType` | `refEntityType_t` | Distinguishes models, sprites, lightning, rail core, and similar render forms. |
| `0x04` | `renderfx` | `int` | Used for flags like `RF_LIGHTING_ORIGIN` and `RF_THIRD_PERSON`. |
| `0x08` | `hModel` | `qhandle_t` | Model handle for fragments, explosions, kamikaze, and invulnerability effects. |
| `0x0C` | `lightingOrigin` | `vec3_t` | Set for sinking stationary fragments so lighting survives when the origin goes below the floor. |
| `0x18` | `shadowPlane` | `float` | Structurally present, but not a strongly revalidated local-entity field in this pass. |
| `0x1C` | `axis[3]` | `vec3_t[3]` | Orientation basis for fragments, explosions, and composite effects. |
| `0x40` | `nonNormalizedAxes` | `qboolean` | Marks scaled axes for shockwave and boomsphere composites. |
| `0x44` | `origin` | `vec3_t` | Current render origin and collision start point for fragments. |
| `0x50` | `frame` | `int` | Structurally present, but not a strongly revalidated local-entity field in this pass. |
| `0x54` | `oldorigin` | `vec3_t` | End point for beam-like effects and explosion origin mirroring. |
| `0x60` | `oldframe` | `int` | Structurally present, but not a strongly revalidated local-entity field in this pass. |
| `0x64` | `backlerp` | `float` | Structurally present, but not a strongly revalidated local-entity field in this pass. |
| `0x68` | `skinNum` | `int` | Structurally present, but not a strongly revalidated local-entity field in this pass. |
| `0x6C` | `customSkin` | `qhandle_t` | Structurally present, but not a strongly revalidated local-entity field in this pass. |
| `0x70` | `customShader` | `qhandle_t` | Shader handle for sprites, rail cores, beams, and explosion shells. |
| `0x74` | `shaderRGBA[4]` | `byte[4]` | Per-frame fade output written by the add paths. |
| `0x78` | `shaderTexCoord[2]` | `float[2]` | Structurally present, but not a strongly revalidated local-entity field in this pass. |
| `0x80` | `shaderTime` | `float` | Spawn-time shader baseline for explosion and composite effects. |
| `0x84` | `radius` | `float` | Renderer-side sprite/model scale; separate from the overloaded top-level `localEntity_t::radius`. |
| `0x88` | `rotation` | `float` | Sprite rotation for puffs, blood bursts, and similar billboard effects. |

## Ownership Notes

### Pool And List Ownership

- `CG_InitLocalEntities` zeroes the backing pool, self-links the active
  sentinel, and chains the pool through `next` as a singly linked free list.
- `CG_AllocLocalEntity` always succeeds: if the free list is empty, it frees the
  oldest active node at the tail before reusing it.
- `CG_FreeLocalEntity` removes a node from the active list and pushes it back to
  the free list without preserving any effect payload.
- `CG_AddLocalEntities` walks the active list backwards, freeing nodes whose
  `endTime` has expired before dispatching on `leType`.

### Type, Timing, And Fade Metadata

- `leType` selects the add path. See
  `docs/reverse-engineering/cgame-letype.md` for the full retail ordinal map.
- `leFlags` is intentionally shared across unrelated effects:
  - `LEF_PUFF_DONT_SCALE` suppresses puff growth in `CG_AddMoveScaleFade`
  - `LEF_TUMBLE` enables angular trajectory evaluation in `CG_AddFragment`
  - `LEF_SOUND1` / `LEF_SOUND2` latch the two kamikaze local sounds
- `startTime`, `endTime`, and `lifeRate` are the common timing contract across
  nearly all local-entity types.
- `fadeInTime` has strong live ownership in the move-scale-fade path and the
  retail `0x05` / `0x0F` RGB-light fade paths, where smoke-style producers can
  request an initial fade-in period before normal lifetime decay begins.

### Motion And Collision Payload

- `pos` is the primary motion payload for puffs and fragments. The current
  source still routes local-entity evaluation through a cgame-side bridge so
  `posTrajExtra` can feed the retail type-`6` path without expanding
  `trajectory_t` globally.
- `CG_ReflectVelocity` rewrites `pos.trDelta`, `pos.trBase`, `pos.trTime`, and
  sometimes `pos.trType` when a fragment collides.
- `angles` has two strong roles:
  - tumbling fragment orientation via `BG_EvaluateTrajectory`
  - random-axis scratch storage for the `LE_KAMIKAZE` / `LE_10` second
    shockwave phase
- `bounceFactor` is only meaningful for bounce-capable fragment-like entries.

### Shared Numeric Payload

- `color[4]` is the normalized float baseline reused by
  `CG_AddFadeRGB`, `CG_AddType05`, `CG_AddType0F`, the scale-fade family,
  `CG_AddKamikaze`, `CG_AddType10`, and similar composite paths.
- `radius` is deliberately overloaded:
  - puff families use it as a fade/scale baseline
  - `LE_SCOREPLUM` stores the integer score in this float slot
  - retail `CG_ScorePlum` only applies its 20-unit vertical de-stack when the
    new plum is at or below the previous plum height
  - the renderer still has its own separate `refEntity.radius`
- `light` and `lightColor` are strong for explosion-style effects and the
  retail `0x0F` fade handler; they are consumed by
  `CG_AddExplosion`, `CG_AddSpriteExplosion`, and `CG_AddType0F`.

### Fragment-Only Extensions

- `fragmentMarkType` at `0x098` selects the recovered retail impact-mark
  family:
  medium burn marks, the smaller burn-mark variant used by the no-DLC sphere
  fragments, DLC blood-spray marks, `iceMark`, or no mark at all.
- `fragmentBounceSoundType` at `0x09C` is broader than the older Quake III
  name suggests. In retail it selects both the post-impact sound family and,
  for some moving fragment families, the in-flight trail hook:
  blood gibs use the DLC blood-spray trail and gib impact sounds, brass uses
  the dormant no-op slot, the sphere fragments use the odd retail
  electrogib-bounce branch, and thaw shards use the `iceTrail` puff family
  before settling.
- The two dwords at `0x090` and `0x094` are now strongly owned as the
  source-side bridge for the retail extra trajectory scalar slots. This keeps
  `refEntity` at the recovered x86 offset while avoiding a global shared
  `trajectory_t` expansion.
- These recovered selector fields are meaningful for fragment-family entries
  and generally irrelevant for puff, score, beam, or composite local
  entities.

### Embedded `refEntity_t`

- `refEntity` is the authoritative render payload submitted to the renderer.
  The rest of `localEntity_t` mostly acts as control state for evolving this
  embedded render object over time.
- Many producer functions initialize both top-level fields and `refEntity`
  fields together:
  - `CG_SmokePuff` seeds timing/color at the top level and sprite state inside
    `refEntity`
  - retail `CG_Bleed` seeds through the same smoke-puff helper with one of the
    four DLC-gated `bloodSpray` shaders, then overrides `leType` to
    `LE_FALL_SCALE_FADE` and writes `pos.trDelta[2] = 40` for the short
    downward blood-hit drift
  - retail `CG_BigExplode` seeds a `LE_0F` `deathEffect` shell, a matching
    `LE_05` tracer cloud, and ten `LE_FRAGMENT_14` sphere shards whose
    velocities come from a downward 10-step ring basis; the `deathEffect`
    shell itself stays fixed-size via `LEF_PUFF_DONT_SCALE`, carries the same
    short 400-unit orange fading light used by the retail helper, and seeds
    `pos.trBase` so the shared `LE_0F` add path resolves to the correct
    origin; the tracer cloud and sphere shards both use the retail custom
    trajectory type `6`, with `posTrajExtra = -240` for the tracer shell and
    `posTrajExtra = 425` for the sphere fragments; the invulnerability timeout
    variant elevates the shell/tracer pair and shifts the fragment basis origin
    upward before applying the same downward launch; unlike the older source-era
    gib path, this no-DLC fallback is not gated by `cg_blood`
  - retail `EV_JUICED` only instantiates `LE_INVULJUICED` when DLC gib media is
    present; otherwise it skips the long-lived local entity and fires the
    immediate no-DLC `CG_BigExplode` fallback instead
  - `CG_MakeExplosion` seeds lifetime/light/color at the top level and model /
    shader / origin inside `refEntity`
  - fragment producers seed bounce/tumble state at the top level and model /
    origin / axis inside `refEntity`
- Retail also uses `refEntity` itself as scratch state in a few places, such as
  sinking stationary fragments and inflating invulnerability or kamikaze axes.

## Practical Reading Guide

- If the question is "who owns and recycles these transient effects?", start at
  `prev`, `next`, and the `cg_localEntities` / `cg_activeLocalEntities` /
  `cg_freeLocalEntities` pool.
- If the question is "why did this effect disappear or fade?", start at
  `startTime`, `endTime`, `fadeInTime`, and `lifeRate`.
- If the question is "why did this thing move, bounce, or tumble?", start at
  `pos`, `angles`, `bounceFactor`, `fragmentMarkType`, and
  `fragmentBounceSoundType`.
- If the question is "what actually gets rendered?", start at `refEntity`.
- If the question is "why does this struct have both `radius` and
  `refEntity.radius`?", check whether the effect uses the top-level slot as
  control data rather than as the live renderer scale.

## Open Questions

1. Revalidate whether retail meaningfully uses any of the colder embedded
   `refEntity_t` fields (`shadowPlane`, `skinNum`, `customSkin`,
   `shaderTexCoord`, and similar) in local-entity-only paths, or whether they
   are simply carried through because the whole render struct is embedded.
2. Revalidate whether any recovered retail producer meaningfully exercises the
   `anglesTrajExtra` bridge, or whether the companion slot is only carried
   through for structural parity with the extended retail trajectory contract.
3. Recover the remaining retail producer sites for the colder `leType_t`
   value `LE_FRAGMENT_16` to determine which parts of the shared payload it
   still exercises beyond the now-recovered `LE_10` / `LE_05` /
   `LE_FRAGMENT_14` / `LE_0F` fallback coverage.
4. Expand `trajectory_t` and `refEntity_t` as dedicated reverse-engineering
   notes if future work needs field-level documentation outside the
   `localEntity_t` context.
