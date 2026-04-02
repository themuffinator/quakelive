# Qagame Mapping Ledger

This ledger tracks recurring high-confidence passes over the retail
`qagamex86.dll` against `src/code/game/` using the committed Ghidra corpus in
`references/reverse-engineering/ghidra/qagamex86/` and the Binary Ninja HLIL
dump in `references/hlil/quakelive/qagamex86.dll/`.

Observed facts come from exports, `functions.csv`, native dispatch-table slots,
log strings, and call flow. Inferred names are only promoted when the retail
behavior and source analogue align cleanly.

## Latest Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: unchanged at `1128` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: unchanged at `1027/1027` mapped functions (`100.00%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+0` coverage, but `2` retained Json helpers were tightened from descriptive cleanup labels to source-faithful JsonCpp destructor identities.
- Note: curated overhang stays flat at `101`.
- Note: this was a mapping-only rename pass, so no source-side parity code changed; the embedded `qagame.json` stats block remains `1128/1128`.

## Newly Mapped In This Pass

| Area | Recovered functions |
| --- | --- |
| Source-faithful JsonCpp destructor rename | `JsonValueDestructor` and `JsonValueDestructorCleanup` |

This was another quality pass over the retained Json overhang after coverage had
already reached `1027/1027`. The old labels `JsonValueDestroy` and
`JsonValueDestroyCleanup` were behaviorally accurate, but the committed HLIL and
the surrounding unwind states show that they are specifically the old JsonCpp
`Json::Value::~Value()` body and its paired EH cleanup leaf.

At `0x100793A0` the helper switches on the tagged `Json::Value` kind, releases
allocator-owned strings through the default allocator vtable, recursively tears
down map-backed array/object storage, and frees the optional comment array. The
paired `0x1007B80C` funclet tailcalls that same body for the protected stack
`Json::Value` local used in the resolver seam, which pins it as destructor
cleanup rather than a generic destroy helper.

## Immediate Previous Pass

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: unchanged at `1128` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: unchanged at `1027/1027` mapped functions (`100.00%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+0` coverage, but `4` retained Json helpers were tightened from descriptive labels to source-faithful JsonCpp method names.
- Note: curated overhang stays flat at `101`.
- Note: this was a mapping-only rename pass, so no source-side parity code changed; the embedded `qagame.json` stats block remains `1128/1128`.

## Newly Mapped In The Immediate Previous Pass

| Area | Recovered functions |
| --- | --- |
| Source-faithful JsonCpp method renames | `JsonValueOperatorAssign`, `JsonValueOperatorEquals`, `JsonValueOperatorIndexArrayIndex`, and `JsonValueOperatorIndexCString` |

This was a quality pass over the retained Json overhang after coverage had
already reached `1027/1027`. The old labels for these four entries were
behaviorally accurate but still descriptive. Cross-checking the committed HLIL
against the upstream `json_value.cpp` operator bodies shows that they match the
old JsonCpp source exactly: the assignment helper is the `Value temp(other);
swap(temp);` body of `Json::Value::operator=`, the equality predicate is
`Json::Value::operator==`, and the two resolver leaves are the non-const
`Json::Value::operator[]` overloads for `ArrayIndex` and `const char *`.

The CString member path deserves the extra note that retail optimization has
inlined the private `resolveReference( key, false )` helper into the emitted
`operator[]( const char * )` body. That leaves the compiled helper with the
full promotion/lower-bound/insert sequence rather than the tiny source wrapper,
but the source-level identity is still exact.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `1126` -> `1128` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `1025/1027` -> `1027/1027` mapped functions (`99.81%` -> `100.00%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+2` curated names, `+2` corpus-overlap matches, and `+0.19` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `101` because every promoted helper in this round already has a standalone `functions.csv` row.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `1128/1128`.

## Newly Mapped In The Previous Coverage Update

| Area | Recovered functions |
| --- | --- |
| Final Json resolver cleanup seam | `JsonValueResolveReferenceInsertPairKeyCleanup` and `JsonValueResolveReferenceInsertPairKeyTeardownCleanup` |

This pass closed the last two anonymous `functions.csv` rows in the embedded
JsonCpp resolver seam. The key evidence was the committed FuncInfo block at
`0x1008BD20`: its six-state unwind map shows `0x1007B81C`, `0x1007B824`, and
`0x1007B82C` all unwinding back to state `2`, with the middle state using the
already-mapped full pair destructor `JsonValueMapNodeDestroyCleanup`. That pins
the two remaining leaves as key-only cleanup states on the same stack
insertion-pair local rather than separate source-level helpers.

The stage split is explicit in HLIL. State `3` is active after the pair
`CZString` key has been copy-constructed but before the sibling `Json::Value`
payload is fully live, so `0x1007B81C` only destroys that pair key. State `5`
is set immediately before the explicit `JsonValueDestructor` teardown of the
stack pair payload after insertion returns, so `0x1007B82C` is the later
key-only cleanup that runs if that teardown path itself unwinds.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `1086` -> `1091` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `987/1027` -> `990/1027` mapped functions (`96.11%` -> `96.40%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+5` curated names, `+3` corpus-overlap matches, and `+0.29` percentage points on full-corpus parity.
- Note: curated overhang rose from `99` to `101` because the retained `g_inactivityWarning` and `g_instaGib` callback stubs do not have standalone rows in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `1091/1091`.

## Newly Mapped In This Pass

| Area | Recovered functions |
| --- | --- |
| Shared gameplay classifiers | `G_PowerupCarrierKillUsesWhitePrefix` and `G_RoundControllerGametypeEnabled` |
| Retained qagame cvar callbacks | `G_InactivityWarningCvarChanged`, `G_InstaGibCvarChanged`, and `G_PlayerScaleCvarsChanged` |

This sweep stayed on small gameplay and callback leaves where the owning seam is
already mapped. `G_RoundControllerGametypeEnabled` is exact: its truth table is
the same `CA` / `Attack & Defend` / `Freeze` / `Red Rover` classifier used by
the reconstructed round-controller source. `G_PowerupCarrierKillUsesWhitePrefix`
is a descriptive split helper under the already mapped carrier-kill announcer,
with the HLIL showing the dedicated objective-gametype branch that selects the
white versus fallback yellow prefix.

The other three promotions come directly from the retained cvar table in the
HLIL. `G_InactivityWarningCvarChanged` hangs off `g_inactivityWarning` and
immediately fans into the already mapped `G_ResetClientInactivityWarnings`.
`G_InstaGibCvarChanged` is the adjacent `g_instaGib` callback that refreshes
the live ammo slab through the nearby instagib/infinite-ammo sync helper.
`G_PlayerScaleCvarsChanged` is shared by `g_playerheadScale` and
`g_playerModelScale` and simply reruns `ClientUserinfoChanged` for connected
clients so forced-appearance state updates in-place.

I rechecked the neighboring player-appearance, Freeze, and startup/runtime
helpers in the same pass, but left them unnamed where the source analogue or
retained implementation boundary was still less explicit than the five entries
promoted here.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `1078` -> `1086` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `979/1027` -> `987/1027` mapped functions (`95.33%` -> `96.11%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+8` curated names, `+8` corpus-overlap matches, and `+0.78` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `99` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `1086/1086`.

## Newly Mapped In The Immediate Previous Pass

| Area | Recovered functions |
| --- | --- |
| Shared gameplay helper | `BG_PlayerCarryingFlag` |
| Json and MSVC EH funclets | `JsonValueMapNodeDestroyThunk`, `CatchAllStdStringGrow`, `CatchAllJsonValueClearMapRange`, `CatchAllJsonValueMapCloneSubtree`, `CatchAllJsonValueMapNodeConstruct`, `EhVectorDestructorIteratorCleanup`, and `EhVectorConstructorIteratorCleanup` |

This sweep stayed on high-confidence leaves only, but widened from the prior
runtime pass into two adjacent seams. The gameplay-side addition is exact:
`BG_PlayerCarryingFlag` is the same three-flag predicate still present as a
static helper in `bg_misc.c`, and the qagame callers pass the leading
`playerState_t` slab through client pointers exactly as the HLIL suggests.

The rest of the round promoted compiler-generated helpers whose owning
functions were already mapped. `CatchAllStdStringGrow`,
`CatchAllJsonValueClearMapRange`, `CatchAllJsonValueMapCloneSubtree`, and
`CatchAllJsonValueMapNodeConstruct` all preserve explicit cleanup-and-rethrow
behavior in HLIL, while `EhVectorDestructorIteratorCleanup` and
`EhVectorConstructorIteratorCleanup` are the paired MSVC `__ArrayUnwind`
cleanup funclets under the two previously landed EH vector iterators. I also
named the tiny `JsonValueMapNodeDestroyThunk` forwarder at `0x100797A0`
because it is a one-step regparm tailcall into the already mapped node
destructor.

I left the remaining `Catch_All@...`, `Unwind@...`, and gameplay-side `FUN_...`
rows untouched where the parent relationship or source analogue was still less
explicit than the entries promoted here.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `1019` -> `1025` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `922/1027` -> `928/1027` mapped functions (`89.78%` -> `90.36%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+6` curated names, `+6` corpus-overlap matches, and `+0.58` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `97` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `1025/1025`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Retained string assignment and growth seam | `StdStringAssignRange`, `StdStringAssignSubstr`, `StdStringGrow`, and `StdStringErase` |
| Json string and map-tail seam | `JsonValueSetCString` and `JsonValueMapSubtreeRightmost` |

This sweep stayed in the retained C++ runtime and the embedded JsonCpp support
layer that sits immediately beneath the already mapped Json value/object
helpers. The retail HLIL preserved the string length/capacity layout, the
small-string and growth rules, the alias-safe substring path, and the sentinel
tree footer handling strongly enough to promote these leaves without forcing
broader STL implementation guesses elsewhere in the runtime seam.

`StdStringAssignRange`, `StdStringAssignSubstr`, `StdStringGrow`, and
`StdStringErase` close the small retained-string corridor adjacent to the
already mapped Json string constructors and copy paths. Retail shows the exact
offset validation, self-alias fallback, 1.5x growth heuristic, suffix-preserve
copy, `memmove`-based erase path, and trailing-NUL maintenance expected from
the old MSVC string runtime used by the binary.

`JsonValueSetCString` and `JsonValueMapSubtreeRightmost` close two remaining
Json internals that were still unnamed beside the previously mapped string and
tree helpers. The first tags a value as an allocated string, clears the
optional comment pointer, duplicates the incoming C string, and returns the new
buffer. The second walks to the rightmost descendant of a map subtree and is
reused by the erase/relink corridor to rebuild the sentinel's cached end
predecessor.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `974` -> `976` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `878/1027` -> `880/1027` mapped functions (`85.49%` -> `85.69%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+2` curated names, `+2` corpus-overlap matches, and `+0.19` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `96` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `976/976`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Shared muzzle-point seam | `CalcMuzzlePoint` |
| Shared network snap seam | `SnapVectorTowards` |

This sweep focused on the remaining small `g_weapon` helpers adjacent to the
already-mapped projectile and muzzle corridors. Two exact source leaves cleared
the promotion bar; the nearby player-name and team-location wrappers were left
unmapped because they no longer match source signatures cleanly enough.

`CalcMuzzlePoint` is exact `g_weapon.c` recovery. HLIL preserves the forward
derivation from `client->ps.viewangles`, the `ent->s.pos.trBase` seed, the
`client->ps.viewheight` lift, and the crouched-versus-standing forward offset.
Retail folds the source-equivalent `CalcMuzzlePointOrigin` no-op variant into
the same leaf.

`SnapVectorTowards` is exact `g_weapon.c` recovery. The HLIL body matches the
three-component truncate-and-bias loop that snaps each coordinate toward the
reference vector so impact endpoints stay on the intended side for networked
missile events.

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `963` -> `964` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `867/1027` -> `868/1027` mapped functions (`84.42%` -> `84.52%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+1` curated name, `+1` corpus-overlap match, and `+0.10` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `96` because this promotion already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `964/964`.

## Newly Mapped In This Pass

| Area | Recovered functions |
| --- | --- |
| Team objective bonus seam | `Team_CheckHurtCarrier` |

This round spent most of its time sweeping adjacent unmapped `g_team`,
`g_items`, and cvar-callback leaves beneath already-mapped callers. Only one
candidate cleared the exact-match bar.

`Team_CheckHurtCarrier` is exact `g_team.c` recovery. HLIL preserves the null
client guards, the target-team switch that chooses the opposing flag powerup,
and the mirrored `lasthurtcarrier = level.time` stamp for both enemy flag
carriers and Harvester skull carriers.

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `960` -> `963` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `864/1027` -> `867/1027` mapped functions (`84.13%` -> `84.42%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+3` curated names, `+3` corpus-overlap matches, and `+0.29` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `96` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `963/963`.

## Newly Mapped In This Pass

| Area | Recovered functions |
| --- | --- |
| Warmup deadline seam | `G_SetWarmupTime` |
| Inactivity warning seam | `G_ResetClientInactivityWarnings` |
| Memory allocator seam | `G_Alloc` |

This pass focused on two small shared-state helpers in the match-state and
memory-management seam, plus one small cvar-driven client-state reset.
`G_SetWarmupTime` is intentionally descriptive rather than source-exact: HLIL
shows it writing the live warmup deadline, publishing `CS_WARMUP`, refreshing
the adjacent auto-record controller, and then deriving `g_gameState` from the
sign of that deadline.

`G_ResetClientInactivityWarnings` is likewise descriptive. The owning callback
table ties it directly to `g_inactivityWarning`, and the leaf itself only walks
connected clients to clear the per-client inactivity-warning latch so the
warning countdown can be reissued under the updated setting.

`G_Alloc` is exact `g_mem.c` recovery. The retained
`G_Alloc of %i bytes (%i left)\n` and allocation-failure diagnostics, together
with the shared 32-byte alignment math and the 4 MB slab cursor, make the
allocator boundary unambiguous even though retail folds `G_InitMemory` into the
larger init corridor.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `952` -> `960` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `859/1027` -> `864/1027` mapped functions (`83.64%` -> `84.13%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+8` curated names, `+5` corpus-overlap matches, and `+0.49` percentage points on full-corpus parity.
- Note: curated overhang rises from `93` to `96` because the retail rocket, plasma, and BFG acceleration think leaves promoted in this pass are folded into surrounding constructors in the committed `functions.csv` export rather than emitted as standalone rows.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `960/960`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Shared missile / acceleration seam | `G_SpawnConfiguredMissile`, `G_RunGuidedRocketThink`, `G_RunRocketAccelerationThink`, `G_RunPlasmaAccelerationThink`, and `G_RunBfgAccelerationThink` |
| Target use callbacks | `Use_Target_Give`, `Use_Target_RemoveKeys`, and `Use_target_remove_powerups` |

This pass focused on two small retail-only helper families that already had
their owning callers mapped. The missile batch closes the shared projectile
setup seam beneath `fire_grenade`, `fire_rocket`, `fire_plasma`, and `fire_bfg`,
plus the older think-driven guided-rocket and acceleration sidecars that the
current tree now expresses through `G_RunMissile` and inline helper calls.

The target batch is source-faithful recovery from `g_target.c`. HLIL preserves
the `target_give` loop that forwards matching item targets through `Touch_Item`
and then unlinks them, the key-removal callback that drops carried keys through
`G_ResetKeyItem`, and the powerup-removal callback that returns any carried CTF
flags before clearing the activator's powerup array.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `949` -> `952` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `856/1027` -> `859/1027` mapped functions (`83.35%` -> `83.64%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+3` curated names, `+3` corpus-overlap matches, and `+0.29` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `93` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `952/952`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Persistent-powerup flag-base seam | `G_FindPersistantPowerupFlagBaseByTeam` |
| CTF flag sanity seam | `Team_ReturnFlagIfMissing` |
| Round-results client-list seam | `G_CountAndSortConnectedClients` |

This pass focused on small remaining helpers whose ownership was already pinned
down by adjacent mapped callers. The persistent-powerup helper is a team-indexed
mirror of the existing string-keyed flag-base resolver and is only used to seed
the cached red and blue base origins in `G_InitItemPowerupState`.

The CTF helper is the per-frame flag-sanity guard reached from the `GT_CTF`
branch in `G_RunFrame`: it scans for a surviving dropped or visible flag entity,
falls back to a live enemy carrier with an active flag powerup, and auto-calls
`Team_ReturnFlag` only when the flag has vanished entirely. The client-list
helper closes a small round-results split under the Red Rover controller by
counting connected/non-spectator/playing clients, seeding the first two follow
slots, and sorting the emitted client list through the adjacent retail
team/score comparator.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `943` -> `949` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `850/1027` -> `856/1027` mapped functions (`82.77%` -> `83.35%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+6` curated names, `+6` corpus-overlap matches, and `+0.58` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `93` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `949/949`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| PMove tuning / wish-move seam | `PM_LoadMoveTuningConstants` and `PM_BuildWishMove3D` |
| Combat knockback seam | `G_KnockbackScaleForMOD` |
| Retail damage / award temp-entity seam | `G_AddDamagePlum`, `G_AddAwardEntity`, and `G_GrantPlayerReward` |

This pass focused on the remaining shared pmove sidecar leaves and the Quake
Live-only reward telemetry seam under `G_Damage` and the kill/round bonus
paths. The PMove pair is backed by the previously mapped cgame movement corridor:
the qagame bodies match the same retail constant-loader and 3D wish-vector
builder already recovered on the client binary.

The combat batch closes the next reward transport boundary. HLIL preserves the
weapon-specific `g_knockback_%s` selector used by `G_Damage`, the local-client
`EV_DAMAGEPLUM` emitter that stages damage and weapon payloads for cgame, the
paired `EV_AWARD` medal emitter used by the Quake Live award taxonomy, and the
small helper that increments medal counters while latching the corresponding
`EF_AWARD_*` display state.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `936` -> `943` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `843/1027` -> `850/1027` mapped functions (`82.08%` -> `82.77%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+7` curated names, `+7` corpus-overlap matches, and `+0.68` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `93` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `943/943`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| PMove jump / step-jump seam | `PM_ApplyJumpTakeoff`, `PM_CanCrouchStepJump`, and `PM_CanStepJump` |
| Domination capture / reward seam | `G_DominationRewardCaptureParticipants`, `G_DominationSelectPrimaryCapturer`, and `G_DominationCheckDefenseBonus` |
| Domination point bootstrap seam | `G_DominationPointActivate` |

This pass focused on the retail-only PMove step-jump split and the adjacent
Domination capture controller. The PMove trio remains descriptive because the
current tree expresses the same behavior across `PM_CheckJump` and the newer
`PM_ApplyStepJump` wrapper, while the retail binary keeps the step-jump gates
and jump takeoff body as separate adjacent leaves.

The Domination batch is likewise retail-only boundary recovery. HLIL preserves
the delayed point activation callback queued by `SP_team_dom_point`, the helper
that chooses the primary capturing client from the active participant lists, the
capture/assist reward fan-out, and the nearby defense-bonus checker called from
the team frag-reward path.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `932` -> `936` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `839/1027` -> `843/1027` mapped functions (`81.69%` -> `82.08%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+4` curated names, `+4` corpus-overlap matches, and `+0.39` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `93` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `936/936`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Spawn/filter parsing seam | `G_ParseDisableLoadoutString` and `G_ParseSpawnGametypeMask` |
| Shared `bg_` / item helpers | `BG_IsTeamFlagItem` |
| Combat spectator-warning seam | `G_WarnIfSpectatorShot` |

This pass focused on the remaining high-confidence helpers sitting between
`SP_worldspawn`, the item spawn filters, and the splash-damage trace seam. The
strongest exact recovery is `G_ParseDisableLoadoutString`, which the committed
source still exposes verbatim in `g_spawn.c`; the paired gametype parser and
flag-item predicate remain descriptive retail-only names because the current
tree keeps the same behavior inlined or expressed through different helper
boundaries.

`G_WarnIfSpectatorShot` is also intentionally descriptive rather than source
exact. HLIL shows a tiny standalone leaf that resolves an entity slot, checks
for a spectator client, and emits the preserved `A spectator has been shot!`
message from the splash/trace damage seam. The current GPL-derived tree keeps
that text inline under `G_Damage` instead of as a reusable helper.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `923` -> `932` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `830/1027` -> `839/1027` mapped functions (`80.82%` -> `81.69%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+9` curated names, `+9` corpus-overlap matches, and `+0.88` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `93` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `932/932`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| `g_cmds` and client-info seam | `Cmd_Kill_f` and `ClientNameAvailable` |
| Shared `bg_` / gameplay helpers | `BG_WeaponName`, `vtos`, `PM_TorsoAnimation`, and `G_DistanceToEntityBounds` |
| Freeze / Domination round helpers | `G_FreezeCheckExitRules`, `G_FreezeFindThawHelperByClientNum`, and `G_UpdateDominationPointCountConfigstrings` |

This pass closes a thin but high-confidence slab of pure helpers that the
retail binary keeps as standalone bodies even though the current source tree
either inlines the same behavior or has not split it back out yet. The new
names cover the missing `kill` command leaf in the `ClientCommand` ladder, the
client-name deconfliction helper under `ClientUserinfoChanged`, the shared
weapon-name / vector-print / torso-idle utilities, the splash-distance helper
under `G_RadiusDamage`, and two Freeze / one Domination controller sidecars.

The Freeze / Domination promotions are descriptive retail-only names rather
than exact source exports. HLIL and the committed corpus agree on the owning
controller paths and side effects, but the current GPL-derived tree does not
yet expose those helpers as identical standalone functions.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `918` -> `923` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `825/1027` -> `830/1027` mapped functions (`80.33%` -> `80.82%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+5` curated names, `+5` corpus-overlap matches, and `+0.49` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `93` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: the embedded `qagame.json` stats block is now realigned to the live curated total of `923/923`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Hidden lag-hax / rewind seam | `G_InitLagHaxHistory`, `G_StoreHistory`, `G_TimeShiftClient`, `G_TimeShiftAllClients`, and `G_UnTimeShiftAllClients` |
| Source-side parity | `src/code/game/g_main.c` now registers the hidden `g_lagHaxHistory=4` and `g_lagHaxMs=80` cvars, `src/code/game/g_active.c` reconstructs the retail rewind history ring and per-frame store/rewind flow, `src/code/game/g_weapon.c` brackets the retail hitscan weapon set with rewind restore calls, and `src/code/game/g_client.c` plus `src/code/game/g_misc.c` invalidate the current history head on spawn, disconnect, and teleport transitions |

This pass closes the hidden Quake Live lag-hax seam that sits between
`ClientEndFrame`, the hitscan weapon dispatcher, and the client collision
history used by rewind traces. The recovered set covers the per-client ring
allocator, the frame-tail history recorder, the single-client interpolating
rewind helper, the outer per-shot rewind pass, and the matching restore pass.

On the source side, the live code now follows the observed retail behavior more
closely. `ClientEndFrame` records the latest collision history, `FireWeapon`
rewinds and restores the retail hitscan set (`MG`, `HMG`, `SG`, `LG`, `RG`,
and `CG`) using the hidden `g_lagHaxHistory` / `g_lagHaxMs` cvars, and the
spawn/teleport/disconnect transitions now invalidate the current history head so
stale bounds are not reused across those state changes.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `893` -> `906` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `807/1027` -> `820/1027` mapped functions (`78.58%` -> `79.84%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+13` curated names, `+13` corpus-overlap matches, and `+1.27` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `86` because every recovered helper in this pass already has a standalone row in the committed `functions.csv` export.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Combat scoring and death-drop seam | `ScorePlum`, `AddScore`, `TossClientItems`, `RaySphereIntersections`, `G_InvulnerabilityEffect`, and `CheckArmor` |
| Shared `q_math` helper seam | `DirToByte`, `vectoangles`, `ProjectPointOnPlane`, `RadiusFromBounds`, `VectorNormalize`, `VectorNormalize2`, and `AngleVectors` |
| Source-side parity | `src/code/game/g_combat.c` now restores retail raw score application in `AddScore` and emits score plums unconditionally through `ScorePlum` instead of routing both behaviors through the non-retail `scoreModifier` / `g_damagePlums` gates |

This pass closes the next exact-name slab in the shared combat utilities and
the reused `q_math` layer. On the gameplay side, the recovered names cover the
score-plum emitter, the core score accumulator, the death-time item/powerup
drop helper, and the invulnerability collision/armor helpers that sit on the
main `G_Damage` path. On the shared-library side, the new names recover the
compact direction encoder plus the vector/angle projection and normalization
helpers that the gameplay, bot, and missile code all reuse.

On the source side, `src/code/game/g_combat.c` now matches the observed retail
scoring path more closely. `ScorePlum` no longer hides behind the built-source
`g_damagePlums` toggle, and `AddScore` now applies the incoming raw score delta
directly instead of running it through the non-retail per-client
`scoreModifier` scaler before the plum, team-score update, and rank refresh.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `756` -> `764` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `680/1027` -> `687/1027` mapped functions (`66.21%` -> `66.89%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `164/180` mapped functions (`91.11%`).
- Delta from this pass: `+8` curated names, `+7` corpus-overlap matches, `+0.68` percentage points on full-corpus parity, and `+0` matches on the top-decompiled slice.
- Note: curated overhang rises `76` -> `77` because retail keeps `BG_CanGrabHealthItem` as a standalone helper at `0x1002ce00`, but that entry is still absent from the committed `functions.csv` corpus.

## Newly Mapped In The Earlier Pass

| Area | Recovered functions |
| --- | --- |
| `bg_misc` item lookup and touch seam | `BG_FindItemByTypeAndTag`, `BG_FindItemForPowerup`, and `BG_PlayerTouchesItem` |
| Retail pickup and trajectory helpers | `BG_CanGrabHealthItem`, `BG_CanGrabWeaponItem`, `BG_EvaluateTrajectory`, `BG_EvaluateTrajectoryDelta`, and `BG_PlayerStateToEntityState` |
| Source-side pickup parity | `src/code/game/bg_misc.c` now mirrors the retail `BG_CanGrabWeaponItem` early rejection when `ps->pm_flags & PMF_IRONSIGHTS` is set |

This pass closes the next high-yield `bg_misc` seam around item lookup, item
touch tests, pickup gating, and the shared movement-state projection helpers.
The recovered names cover the standalone retail powerup lookup path, the
touch-bounds helper used by client prediction, the compiler-split health and
weapon pickup gates, the trajectory evaluators, and the playerstate-to-
entitystate bridge used throughout both gameplay and bot logic. On the source
side, `src/code/game/bg_misc.c` now follows the observed retail weapon-pickup
path more closely by rejecting pickups while the ironsights bit is active.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `751` -> `756` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `675/1027` -> `680/1027` mapped functions (`65.72%` -> `66.21%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `164/180` mapped functions (`91.11%`).
- Delta from this pass: `+5` curated names, `+5` corpus-overlap matches, `+0.49` percentage points on full-corpus parity, and `+0` matches on the top-decompiled slice.
- Note: curated overhang stays flat at `76` because every promoted helper in this batch is present in the committed `functions.csv` corpus.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Early `g_team` pure/helper seam | `TeamName`, `TeamColorString`, `OtherTeam`, `Team_ForceGesture`, and `Team_CheckDroppedItem` |
| Source-side team visibility/color parity | `src/code/game/g_team.c` now returns retail `^7` for non-red/non-blue `TeamColorString` cases and no longer gates Red Rover infected visibility on `level.roundState` |

This pass closes the next exact `g_team` helper slab that the retail binary
keeps as standalone bodies instead of inlining away. The recovered names cover
the classic team-string helpers, the red/blue swap helper, the dropped-flag
status updater, and the force-gesture broadcaster used by the team objective
announcements. On the source side, `src/code/game/g_team.c` now follows the
observed retail behavior more closely by treating every non-red/non-blue team
as white in `TeamColorString` and by enabling the Red Rover infected visibility
path whenever the gametype is `GT_RED_ROVER` and `g_rrInfected` is non-zero,
without the extra GPL-era `ROUNDSTATE_ACTIVE` gate.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `720` -> `727` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `652/1027` -> `659/1027` mapped functions (`63.49%` -> `64.17%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `160/180` -> `162/180` mapped functions (`88.89%` -> `90.00%`).
- Delta from this pass: `+7` curated names, `+7` corpus-overlap matches, `+0.68` percentage points on full-corpus parity, and `+2` matches on the top-decompiled slice.
- Note: curated overhang stays flat at `68` because every promoted helper in this batch is present in the committed `functions.csv` corpus; the top-slice gains are `BotFindInstaGibTarget` and `BotPublishDebugInfoString`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Instagib target-goal seam | `BotFindInstaGibTarget`, `BotRefreshInstaGibTargetGoal`, and `BotGetInstaGibTargetGoal` |
| `ai_main` retail telemetry | `BotPublishDebugInfoString`, `BotCanSpawnTourPoint`, `BotUpdateItemDelayTime`, and `BotAppendDynamicSkillSample` |
| Source-side frame correction | `BotAIStartFrame` now matches retail more closely by keeping `bot_report` updated without running the stale GPL `BotUpdateInfoConfigStrings()` / `CS_BOTINFO` publish loop |

This pass closes the next retail-only `ai_main` support seam around the
instagib tutorial node, the selected-bot debug publisher, and the training
tail that sits after `BotAIStartFrame`'s main bot-think loop. The instagib
cluster now has coherent target-finding and goal-refresh names, while the
later `ai_main` helpers cover the exact `bot_itemDelayTime` cvar writer, the
dynamic-skill sample recorder, and the tour-point spawn gate used by the
tutorial flow. On the source side, `src/code/game/ai_main.c` now drops the
stale GPL-era `bot_report` info-configstring publish branch that no longer
appears in the retail `BotAIStartFrame` body.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `594` -> `607` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `526/1027` -> `539/1027` mapped functions (`51.22%` -> `52.48%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `149/180` -> `152/180` mapped functions (`82.78%` -> `84.44%`).
- Delta from this pass: `+13` curated names, `+13` corpus-overlap matches, `+1.27` percentage points on full-corpus parity, and `+3` matches on the top-decompiled slice.
- Note: curated overhang stays flat at `68` because every promoted helper in this batch is present in the committed `functions.csv` corpus; only `BotUpdateInventory`, `BotUseKamikaze`, and `BotUseInvulnerability` land inside `decompile_top_functions.c`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Inventory and aggression seam | `BotUpdateInventory`, `BotUpdateBattleInventory`, `BotAggression`, `BotCanAndWantsToRocketJump`, and `BotHasPersistantPowerupAndWeapon` |
| Active battle item use | `BotUseKamikaze`, `BotUseInvulnerability`, `BotBattleUseItems`, and `BotIsObserver` |
| Camping and powerup flow | `BotGoCamp`, `BotWantsToCamp`, `BotDontAvoid`, and `BotGoForPowerups` |

This pass closes the next coherent `ai_dmq3.c` utility seam around bot
inventory refresh, consumable use, and long-term camp or powerup decisions. The
recovered set covers the live inventory snapshot, enemy-distance bookkeeping,
aggression scoring, kamikaze and invulnerability activation, and the full camp
spot plus avoid-goal helpers that feed higher-level long-term goal selection.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `374` -> `377` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `342/1027` -> `345/1027` mapped functions (`33.30%` -> `33.59%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `108/180` -> `110/180` mapped functions (`60.00%` -> `61.11%`).
- Delta from this pass: `+3` curated names, `+3` corpus-overlap matches, `+0.29` percentage points on full-corpus parity, and `+2` matches on the top-decompiled slice.
- Note: `32` curated helper names currently sit outside `functions.csv`, so curated symbol-map totals are tracked separately from corpus-overlap parity.

## Newly Reconstructed In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Spawn ranking seam | retail-only `G_SelectRankedSpawnPoint`, retail-only `G_SelectClientSpawnPoint`, and retail-only `Team_SelectDominationSpawnPoint` |
| Source-side spawn reconstruction | Domination now selects owned point-linked respawns instead of piggybacking entirely on the CTF path, and `ClientSpawn` now routes through the recovered retail helper split instead of keeping all gametype branching inline |

This pass closes the next high-yield qagame spawn-selection seam around the
ClientSpawn path. The remaining hidden debug-command tail still needs a cleaner
body-to-dispatch match before promotion, but the broader spawn-selection band
is now mapped through the Domination-specific path, the shared ranked picker,
and the ClientSpawn-side wrapper.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `362` -> `370` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `331/1027` -> `338/1027` mapped functions (`32.23%` -> `32.91%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `105/180` -> `105/180` mapped functions (`58.33%` -> `58.33%`).
- Delta from this pass: `+8` curated names, `+7` corpus-overlap matches, `+0.68` percentage points on full-corpus parity, and no change on the top-decompiled slice.
- Note: `32` curated helper names currently sit outside `functions.csv`, so curated symbol-map totals are tracked separately from corpus-overlap parity.

## Newly Mapped In The Earlier Pass

| Area | Recovered functions |
| --- | --- |
| Direct command surface | retail-only `Cmd_SetMatchTime_f` |
| Auto-record naming | retail-only `G_SanitizeFilenameToken`, retail-only `G_BuildAutoRecordBasename` |
| Match media automation | retail-only `G_StopAutoRecord`, retail-only `G_StartAutoRecordForClient`, retail-only `G_CheckAutoRecord` |
| Timeout state publication | retail-only `G_UpdateTimeoutConfigStrings` |
| Race respawn flow | retail-only `G_RaceResetClientAndSpawn` |

The remaining highest-yield unmapped seams now skew more toward the hidden
`markstate` / `diffstate` / `dumpentities` / `printentitystates` debug band
and the larger gameplay bootstrap and round-support bodies that still sit
outside the current curated map.

## Prior Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Before this pass: `147` curated mapped functions, `33/180` decompiled-top functions (`18.33%`).
- After this pass: `169` curated mapped functions, `55/180` decompiled-top functions (`30.56%`).
- Delta from this pass: `+22` curated mapped functions and `+12.23` percentage points on the top-decompiled slice.
- Curated string coverage was unchanged at `102/102`; that round widened function naming coverage rather than the string ledger.

## Previously Mapped In The Prior Sweep

| Area | Recovered functions |
| --- | --- |
| Bot chat and state nodes | `BotChatTest`, `BotGetLongTermGoal`, `AINode_Seek_NBG`, `AINode_Seek_LTG`, `AINode_Battle_Fight`, `AINode_Battle_Chase`, `AINode_Battle_Retreat`, `AINode_Battle_NBG` |
| Bot bootstrap and team control | `BotAI`, `BotAISetupClient`, `BotInitLibrary`, `BotSetupDeathmatchAI`, `BotTeamAI` |
| Bot spawn and writable gameplay helpers | `G_AddRandomBot`, `G_AddBot`, `RegisterItem`, `G_Say`, `Cmd_SetViewpos_f` |
| Gameplay utility and objective flow | `G_DroppedPowerupRunFrame`, `G_TryPushingEntity`, `Team_FragBonuses`, `Team_TouchOurFlag` |

The highest-yield remaining seams after that sweep skewed more toward
tutorial-specific bot flows, ranking/stat publishers, and other retail-only
utility helpers outside that widened control surface.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Before this pass: `169` curated mapped functions, `55/180` decompiled-top functions (`30.56%`).
- After this pass: `185` curated mapped functions, `71/180` decompiled-top functions (`39.44%`).
- Delta from this pass: `+16` curated mapped functions and `+8.89` percentage points on the top-decompiled slice.
- Curated string coverage was unchanged at `102/102`; that pass widened function naming coverage rather than the string ledger.
## Key Mappings

| Retail address | Recovered name | Closest source analogue | Evidence summary | Confidence |
| --- | --- | --- | --- | --- |
| `0x10023400` | `BotAIStartFrame` | `ai_main.c::BotAIStartFrame` | Native dispatch-table slot plus the `memorydump` / `bot_memorydump` bot-debug cvars and the per-bot frame/routing update loop match the source bot frame driver. | High |
| `0x10033800` | `P_DamageFeedback` | `g_active.c::P_DamageFeedback` | Aggregates `damage_blood` and `damage_armor`, emits EV_PAIN and damage yaw/pitch, and clears the damage totals exactly like the client damage-feedback path. | High |
| `0x10033950` | `P_WorldEffects` | `g_active.c::P_WorldEffects` | Anchored by `sound/player/gurp1.wav` / `sound/player/gurp2.wav` plus the drowning, battlesuit, lava, and slime control flow. | High |
| `0x10033B20` | `G_SetClientSound` | `g_active.c::G_SetClientSound` | Selects the proxmine ticking loop sound or the lava/slime fry loop on the outgoing playerstate, matching the source helper. | High |
| `0x10033B80` | `ClientImpacts` | `g_active.c::ClientImpacts` | Walks unique pmove touchents and dispatches bot self-touch plus touched-entity callbacks exactly like the source post-pmove impact helper. | High |
| `0x10033C00` | `G_TouchTriggers` | `g_active.c::G_TouchTriggers` | Uses the `40,40,52` trigger range box, spectator teleporter gating, ET_ITEM proximity checks, and jump-pad frame reset logic from the source trigger-touch path. | High |
| `0x10033E30` | `SpectatorThink` | `g_active.c::SpectatorThink` | Sets `PM_SPECTATOR`, unlinks before `pmove`, relinks for `G_TouchTriggers`, and handles the attack-button follow cycle via `Cmd_FollowCycle_f`, matching the source spectator think flow. | High |
| `0x10033FD0` | `ClientInactivityTimer` | `g_active.c::ClientInactivityTimer` | Anchored by `Dropped due to inactivity`, the inactivity warning centerprint, and the `client:%i inactivity:%i` debug line. | High |
| `0x100341E0` | `G_CheckClientFlood` | Retail-only descriptive helper adjacent to `g_active.c::ClientThink_real` | Reads the client `floodCount` / `floodLastTime` state, decays it against the retail flood-protection cvars, and drops the offender with `Dropped for flooding the server` once the limit is exceeded. | High |
| `0x10034260` | `G_RunFactoryHealthRegen` | Retail-only split of `g_active.c::G_RunFactoryRegen` | Per-frame health regen sidecar tailcalled from `ClientTimerActions`; it waits out the last-damage delay, accumulates the configured regen tick interval, stops once health reaches the target, and applies whole-point health increases to the entity. | High |
| `0x100342F0` | `G_RunFactoryArmorRegen` | Retail-only split of `g_active.c::G_RunFactoryRegen` | Per-frame armor regen sidecar tailcalled after the health helper; it waits out the armor delay, honors the `regenArmorAfterHealth` gate, accumulates the regen tick interval, and applies whole-point armor increases to `ps.stats[STAT_ARMOR]`. | High |
| `0x100343E0` | `ClientTimerActions` | `g_active.c::ClientTimerActions` | Accumulates `timeResidual`, applies once-per-second regeneration and armor decay, and emits the regen event through adjacent Quake Live subhelpers in the same place the source calls `ClientTimerActions`. | High |
| `0x10034860` | `ClientEvents` | `g_active.c::ClientEvents` | Walks the recent playerstate event ring, applies fall damage, fires weapons, and handles teleporter, medkit, kamikaze, portal, invulnerability, and Harvester skull-drop item-use side effects exactly where the source server event switch sits. | High |
| `0x10034B50` | `StuckInOtherClient` | `g_active.c::StuckInOtherClient` | Scans live client entities for AABB overlap against the candidate player's expanded bounds and returns true once invulnerability expansion would still intersect another client. | High |
| `0x10034C00` | `SendPendingPredictableEvents` | `g_active.c::SendPendingPredictableEvents` | Creates temporary ET_EVENTS entities from pending playerstate events, clears/restores `externalEvent`, and targets all clients except the originator. | High |
| `0x10034C90` | `ClientThink_real` | `g_active.c::ClientThink_real` | Driven by the outer `ClientThink` export plus command-time clamping, spectator/inactivity gating, pmove, event dispatch, trigger touch, client impacts, respawn, and timer actions. | High |
| `0x10035410` | `ClientThink` | `g_active.c::ClientThink` | Native dispatch-table slot plus `trap_GetUsercmd`, the `lastCmdTime` write, and the bot-gated tailcall into the deeper think path align with the source export wrapper. | High |
| `0x10035470` | `SpectatorClientEndFrame` | `g_active.c::SpectatorClientEndFrame` | The body handles spectator follow targets, `follow1` / `follow2`, POI camera branches, `ClientBegin` fallback, and scoreboard flag toggling exactly like the source spectator end-frame routine. | High |
| `0x10035600` | `ClientEndFrame` | `g_active.c::ClientEndFrame` | Spectator short-circuit into `SpectatorClientEndFrame`, expired powerup cleanup, world/damage end-frame helpers, EF_CONNECTION handling, and final entity-state sync match the source end-frame path. | High |
| `0x10035960` | `G_CAADRespawnAsSpectator` | Retail-only shared Clan Arena / Attack and Defend respawn helper | Reached from the dead-client respawn gate once those modes push a player back into spectator follow; it copies the corpse into the body queue, forces `PM_SPECTATOR`, reruns `ClientSpawn`, and enters follow mode when both teams still have active players. | High |
| `0x100359E0` | `G_ADShouldTimeoutActiveRound` | Retail-only Attack and Defend timeout helper | Returns true once both sides still have active players, no objective winner is already latched, and the active-round elapsed time has reached `roundtimelimit`. | High |
| `0x10035780` | `G_ADResolveRoundState` | Retail-only Attack and Defend controller helper | Resolves expired deferred `AD_RoundStateTransition` work and returns the current A/D round-state latch used by damage, objective, and HUD callers. | High |
| `0x100357D0` | `G_ADHandleDamageScore` | Retail-only Attack and Defend damage helper | Reached from the main damage path; it applies the A/D self/team-damage suppression flags, resolves pending round-state work, and converts active-phase enemy damage into score once the accumulated threshold reaches 100. | High |
| `0x10035A20` | `G_ADCheckExitRules` | Retail-only Attack and Defend exit helper | Tie-aware A/D limit checker covering timelimit, side-specific scorelimit, and late mercylimit, with the matching retail print/log side effects. | High |
| `0x10035B70` | `AD_RoundStateTransition` | Retail-only Attack and Defend round-state controller | Anchored by `AD_RoundStateTransition: invalid state`; it updates the A/D match-state configstrings, respawns or releases participants, settles round winners, rotates turns, and schedules the next countdown/restart transition. | High |
| `0x10036300` | `G_ADNotifyLastAlivePlayer` | Retail-only Attack and Defend round alert helper | Services deferred `AD_RoundStateTransition` work, counts live players by team during the active round, and when the queried side is down to one survivor triggers the shared last-alive notification path. | High |
| `0x100363E0` | `G_ADResolveAttackingTeam` | Retail-only Attack and Defend side helper | Resolves expired deferred `AD_RoundStateTransition` work and returns the currently attacking side during the active A/D phase. | High |
| `0x10036440` | `G_ADResolveDefendingTeam` | Retail-only Attack and Defend side helper | Resolves expired deferred `AD_RoundStateTransition` work and returns the currently defending side; the defense-award path calls it directly before incrementing `DEFENSE` credit. | High |
| `0x100364A0` | `G_ADResetScoreHistory` | Retail-only Attack and Defend scoreboard helper | Clears the retained A/D round-delta history and publishes the baseline `scores_ad` payload with current team totals and empty history slots. | High |
| `0x100365F0` | `G_ADUpdateScoreHistory` | Retail-only Attack and Defend scoreboard helper | Records the latest per-turn A/D score delta into the 20-entry circular history, rebuilds the ordered history window, and republishes `scores_ad`. | High |
| `0x100367C0` | `G_ParseInfos` | `g_bot.c::G_ParseInfos` | Exact info-block parser that requires leading `{` tokens, copies each parsed info string into the output table, and emits the preserved malformed-file diagnostics. | High |
| `0x100378E0` | `G_AddTrainerBot` | Retail-only training bootstrap helper | Enqueues the fixed `Trainer` bot through `G_AddBot` with a 5000 ms delay, then issues the usual `loaddeferred` media warmup command. | High |
| `0x10037F80` | `G_CAResolveRoundState` | Retail-only Clan Arena controller helper | Resolves expired deferred `CA_RoundStateTransition` work and returns the current Clan Arena round-state latch used by HUD and end-frame callers. | High |
| `0x10037FD0` | `G_CAHandleDamageScore` | Retail-only Clan Arena damage helper | Reached from the main damage path; it applies the Clan Arena self/team-damage suppression flags, resolves pending CA round-state work, and during the live round converts damage dealt into the retail 100-point score buckets. | High |
| `0x10038160` | `G_CAADResetClientForRound` | Retail-only shared Clan Arena / Attack and Defend round helper | Reused from both `ClientBegin` and the delayed respawn path for GT_CLAN_ARENA and GT_ATTACK_DEFEND; it respawns immediately in the live release state, respawns into the holding state during the pre-release countdown, and otherwise falls back to the spectator-follow reset path used after round loss. | High |
| `0x100389F0` | `G_CANotifyLastAlivePlayer` | Retail-only Clan Arena round alert helper | Services deferred `CA_RoundStateTransition` work, counts live players by team during the active round, and triggers the shared last-alive notification path when the queried side is down to one survivor. | High |
| `0x10038B60` | `Team_SelectDominationSpawnPoint` | Retail-only Domination spawn helper / `g_team.c` analogue | Reached from the ClientSpawn-side spawn wrapper only for active GT_DOMINATION respawns; it walks `team_dom_point` entities, collects linked `info_player_deathmatch` targets for the owning team, ranks them against live players, and writes the chosen origin/angles. | High |
| `0x10039080` | `G_SelectRankedSpawnPoint` | Retail-only shared spawn helper spanning `g_client.c::SelectRandomFurthestSpawnPoint` and `g_team.c::SelectCTFSpawnPoint` | Anchored by the `info_player_deathmatch`, `team_CTF_redspawn`, `team_CTF_bluespawn`, `team_CTF_redplayer`, and `team_CTF_blueplayer` classnames plus the `FindIntermissionPoint` fallback; it filters telefragging candidates, ranks them against live players, and picks from the best-ranked subset. | High |
| `0x10039730` | `G_SelectClientSpawnPoint` | Retail-only ClientSpawn-side spawn wrapper | Called directly from `ClientSpawn` before the respawn bootstrap continues; it chooses between domination-linked spawns, team/base spawn classes, and the initial non-team spawn path, then falls back through the shared ranked spawn picker. | High |
| `0x1003A270` | `G_UpdateTournamentQueuePositions` | Retail-only duel queue helper | Sorts eligible waiting spectators by the stored queue timestamp, assigns one-based `pq` queue positions, and marks changed entries dirty for the follow-on userinfo republish pass. | High |
| `0x1003A450` | `ClientUserinfoChanged` | `g_client.c::ClientUserinfoChanged` | Native dispatch-table slot plus `ClientUserinfoChanged: %i %s` log string and matching configstring rebuild flow. | High |
| `0x1003AC10` | `ClientConnect` | `g_client.c::ClientConnect` | `ClientConnect: %i` log string, bot masking, session init/read, and platform auth checks match the source connect routine. | High |
| `0x1003B030` | `ClientBegin` | `g_client.c::ClientBegin` | `ClientBegin: %i` log string and the post-connect spawn/bootstrap path align with the source begin routine. | High |
| `0x1003B5A0` | `G_FinalizeSpawnLoadout` | Retail-only spawn/loadout helper | Post-`ClientSpawn` finalizer that honors `selected_spawn_weapon`, parses the configured spawn-grant tokens, seeds the starting ammo and weapon masks through the deeper helper at `0x1003B2A0`, and applies the remaining intermission and live-weapon cleanup for the spawned client. | High |
| `0x1003BC30` | `ClientSpawn` | `g_client.c::ClientSpawn` | Full retail spawn/bootstrap boundary that selects the spawn point, preserves the respawn-persistent client/session state, rebuilds the playerstate/entity defaults for the new life, and then tails into the deeper post-spawn finalization helper. | High |
| `0x1003C7E0` | `ClientDisconnect` | `g_client.c::ClientDisconnect` | Present in `functions.csv`, referenced by the native export table, and anchored by `ClientDisconnect: %i`. | High |
| `0x1003CBF0` | `DeathmatchScoreboardMessage` | `g_cmds.c::DeathmatchScoreboardMessage` | Retail scoreboard sender that dispatches through per-gametype builders, falls back to a compact `smscores` serializer when needed, sends the resulting payload to one client, and during intermission fans into the extra mode-specific stat publishers. | High |
| `0x1003CD70` | `G_BuildCompactScoreboardMessage` | Retail-only compact scoreboard helper | Emits the reduced `smscores` payload that `DeathmatchScoreboardMessage` uses when the richer per-mode payload would exceed the server-command limit or the compact-scoreboard gate is active. | High |
| `0x1003CEC0` | `G_BuildObeliskScoreboardMessage` | Retail-only Overload scoreboard helper | GT_OBELISK/default scoreboard serializer that emits the generic `scores` payload with the extra objective columns preserved in the retail build. | High |
| `0x1003D090` | `G_BuildFFAScoreboardMessage` | Retail-only FFA scoreboard helper | Emits `scores_ffa` with the expanded Quake Live FFA per-client stat block. | High |
| `0x1003D2B0` | `G_BuildDuelScoreboardMessage` | Retail-only duel scoreboard helper | Caches the lower and higher duel client numbers into the `level` tail, builds the viewer-facing weapon/timing summaries, and emits the appropriate `scores_duel` payload shape for one or two players. | High |
| `0x1003DBB0` | `G_BuildRaceScoreboardMessage` | Retail-only Race scoreboard helper / `g_race.c` analogue | Emits the `scores_race` payload with the sorted racer list and timing columns. | High |
| `0x1003DD20` | `G_BuildTeamScoreboardMessage` | Retail-only GT_TEAM scoreboard helper | Emits `scores_tdm` with the red/blue team totals plus the retail TDM per-client stat block. | High |
| `0x1003E1B0` | `G_SendTDMStatsMessage` | Retail-only postgame stats helper | Intermission-only `tdmstats` publisher reused by the TDM and Freeze scoreboard families. | High |
| `0x1003E300` | `G_BuildClanArenaScoreboardMessage` | Retail-only Clan Arena scoreboard helper | Emits the `scores_ca` payload with the retail CA per-client stat block. | High |
| `0x1003E510` | `G_SendCAStatsMessage` | Retail-only postgame stats helper | Intermission-only `castats` publisher for the Clan Arena scoreboard family. | High |
| `0x1003E6D0` | `G_BuildCTFStyleScoreboardMessage` | Retail-only shared CTF-style scoreboard helper | Shared serializer for CTF, One Flag, Harvester, Domination, and Attack and Defend. It emits the `scores_ctf` payload and hides the opposing-team detail block from live viewers when the retail policy requires it. | High |
| `0x1003EC40` | `G_SendCTFStatsMessage` | Retail-only postgame stats helper | Intermission-only `ctfstats` publisher reused by the CTF-style scoreboard families. | High |
| `0x1003EDA0` | `G_BuildFreezeScoreboardMessage` | Retail-only Freeze scoreboard helper | Emits the `scores_ft` payload with the Freeze-specific per-client stat block. | High |
| `0x1003F260` | `G_BuildRedRoverScoreboardMessage` | Retail-only Red Rover scoreboard helper | Emits the `scores_rr` payload with the Red Rover per-client stat block. | High |
| `0x100400F0` | `Cmd_TeamTask_f` | `g_cmds.c::Cmd_TeamTask_f` | Exact `Argc == 2` / `teamtask` userinfo rewrite flow from the stock command handler, ending in `ClientUserinfoChanged`. | High |
| `0x100406D0` | `SetTeam` | `g_cmds.c::SetTeam` | Outer team-change parser that handles `follow1`, `follow2`, spectator/team requests, duel-only spectate enforcement, and then forwards into the deeper retail execution helper. | High |
| `0x100423A0` | `Cmd_CallVote_f` | `g_cmds.c::Cmd_CallVote_f` | Vote-limit enforcement plus the `You have called the maximum number of votes` and `^3Callvote commands` strings. | High |
| `0x10044270` | `Cmd_Vote_f` | `g_cmds.c::Cmd_Vote_f` | Uses the `No vote in progress`, `Vote cast`, and `disable_vote_ui` strings in the source-equivalent vote-cast flow. | High |
| `0x100456B0` | `Cmd_Forfeit_f` | `g_cmds.c::Cmd_Forfeit_f` | Thin forfeit-command wrapper identified by the local pause/timeout and round-countdown rejection strings before the tailcall into the deeper retail forfeit helpers. | High |
| `0x10045BD0` | `Cmd_ReadyUp_f` | `g_cmds.c::Cmd_ReadyUp_f` | Retail ready-up command helper that toggles the per-client ready latch, enforces the minimum-player and team-presence gates, and prints the `Ready` / `Not Ready` warmup centerprint. | High |
| `0x10045DD0` | `ClientCommand` | `g_cmds.c::ClientCommand` | HLIL-visible command dispatch over `say_team`, `vsay_team`, `vosay_team`, `callvote`, `give`, `follow`, `team`, and other retail client commands matches the source dispatcher. | High |
| `0x10046970` | `TossClientCubes` | `g_combat.c::TossClientCubes` | Harvester skull-drop helper backed by the carried-skull count, the `Red Skull` / `Blue Skull` item lookups, and the death-path call that ejects the cubes before corpse cleanup. | High |
| `0x1004BC30` | `G_FreezeResolveRoundState` | Retail-only Freeze controller helper | Resolves any expired deferred round-state transition through `Freeze_RoundStateTransition` and returns the current Freeze controller state for HUD/end-frame callers. | High |
| `0x1004BC80` | `G_FreezeSetClientFrozenState` | Retail-only shared Freeze helper spanning `g_freeze.c::G_FreezeApplyFreezeState` and `g_freeze.c::G_FreezeThawClient` | Shared retail-only mutator that applies frozen or thawed client state, emits the corresponding temp-entity/event path, and refreshes the active-player tally used by the surrounding round controller. | High |
| `0x1004BDE0` | `G_FreezeResetClientForRound` | Retail-only per-client Freeze helper / `g_active.c::G_FreezeResetClientsForRound` analogue | Reused from `ClientBegin` and the delayed active-client reset path; restores clients for warmup or active-round starts and pushes them into the holding state when the controller is not ready to release them. | High |
| `0x1004BF10` | `G_FreezeTeamIsFullyFrozen` | Retail-only Freeze winner predicate | Hidden register-passed team scan used by `G_FreezeEvaluateRoundWinner`; it returns true once no connected members of that team remain unfrozen, letting the outer winner helper distinguish win versus draw. | High |
| `0x1004BF60` | `G_FreezeEvaluateRoundWinner` | Retail-only Freeze result helper / `g_active.c::G_FreezeEvaluateRoundWinner` analogue | Compares the PM_NORMAL living-player tallies and, once the configured draw-delay path is active, the corresponding living-health totals before storing the winning team latch consumed by the adjacent Freeze controller. | High |
| `0x1004C1B0` | `Freeze_RoundStateTransition` | Retail-only Freeze round-state controller | Anchored by `Freeze_RoundStateTransition: invalid state`; it resolves pending transition timers, updates `CS_MATCH_STATE`, resets clients for warmup and active states, and applies the Freeze round-complete transition. | High |
| `0x1004CB80` | `G_FreezeRunFrame` | `g_active.c::G_FreezeRunFrame` | Source-faithful Freeze outer frame boundary. Retail keeps the round-state readback and winner-selection pieces in adjacent helpers, but this function still performs the per-frame freeze update and round-end dispatch. | High |
| `0x1004CC20` | `G_FreezeNotifyLastAlivePlayer` | Retail-only Freeze round alert helper | Services deferred `Freeze_RoundStateTransition` work, counts thawed live players by team during the active round, and triggers the shared last-alive notification path when the queried side is down to one survivor. | High |
| `0x1004CD40` | `G_FreezeClientEndFrame` | `g_client.c::G_FreezeClientEndFrame` | Tracks thaw progress, nearby allies, LOS and distance gates, and the auto-thaw timer before fanning into the shared retail Freeze state mutator. | High |
| `0x1004EE20` | `RespawnItem` | `g_items.c::RespawnItem` | Anchored by `RespawnItem: bad teammaster`; it restores grouped item spawns through the teammaster path, reenables item contents and visibility, emits the respawn event, and selects the retail powerup or kamikaze respawn sound. | High |
| `0x1004F020` | `Touch_Item` | `g_items.c::Touch_Item` | Anchored by `Item: %i %s\n`; it validates the touching client, routes by `item->giType` into the deeper pickup helpers, applies the pickup event/sound path, and updates retail per-item pickup telemetry. | High |
| `0x1004FD20` | `Use_Item` | `g_items.c::Use_Item` | Tiny HLIL-visible retail trampoline that preserves the classic use-to-respawn boundary by tailcalling `RespawnItem(ent)`. | High |
| `0x1004FD30` | `G_CheckTeamItems` | `g_items.c::G_CheckTeamItems` | Anchored by the missing red/blue/neutral flag and obelisk warnings; it verifies the active gametype has the required team objective entities in the map. | High |
| `0x100503F0` | `FinishSpawningItem` | `g_items.c::FinishSpawningItem` | Anchored by `FinishSpawningItem: %s startsolid at %s`; it sets ET_ITEM, model indices, touch/use callbacks, the drop-to-floor path, and the delayed powerup spawn gate before linking the entity. | High |
| `0x100507E0` | `G_SpawnItem` | `g_items.c::G_SpawnItem` | Source-faithful outer item spawn helper. It stores the `gitem_t`, parses retail `wait` / `random` overrides, registers assets, seeds persistent-powerup and global-sound flags, and schedules `FinishSpawningItem`. | High |
| `0x10052DC0` | `G_CanClientSeeClient` | Retail-only native export helper | Snapshot-side client-visibility predicate used for client entities: spectators, same-team viewers, the active Red Rover infection phase, and the One Flag bot special case all return true even when the stock PVS path would be the normal gate. | High |
| `0x10052E40` | `G_AreEnemyClients` | Retail-only native export helper | Validates two client slots and returns true only when they are distinct, non-spectators, and not on the same team. | High |
| `0x10052E90` | `G_ShouldSuppressVoiceToClient` | Retail-only native export helper | Steam-voice relay filter that returns true when delivery should be blocked for the candidate recipient, including bots, muted senders, and non-tell self echo; open/all-talk cases return false, otherwise the team/spectator policy falls through `OnSameTeam`. | High |
| `0x10052F40` | `G_IsObjectiveEntity` | Retail-only native export helper | Gametype-aware objective classifier that recognizes CTF/Attack-Defend flag items, One Flag targets, Overload obelisks, and the Quake Live extended item-objective flag path. | High |
| `0x10053020` | `G_FreezeCanSeeThawProgressEvent` | Retail-only Freeze native export helper | Freeze-only visibility predicate for thaw-progress temp entity event `0x58`; it checks the linked entity/player and returns true only for teammates of that linked target. | High |
| `0x100530C0` | `G_IsClientAdmin` | Retail-only native export helper | Native export-tail predicate that validates the client slot and returns true only when `sess.privilege == PRIV_ADMIN`. | High |
| `0x100530F0` | `G_GetClientScore` | Retail-only native export helper | Validates the client slot and returns `gclient->ps.persistant[PERS_SCORE]` from offset `0x100`. | High |
| `0x10053120` | `dllEntry` | Native qagame interface / `g_syscalls.c::dllEntry` analogue | Named export in HLIL and Ghidra. Retail stores the import table pointer, returns the direct-export table, and writes API version `10` through the third out-parameter. | High |
| `0x10053290` | `G_FindTeams` | `g_main.c::G_FindTeams` | Groups entities with matching `team` keys and ends with `%i teams with %i entities`. | High |
| `0x10053400` | `G_UpdateCustomSettingsMaskForCvar` | Retail-only cvar-table helper | Reused from both `G_RegisterCvars` and `G_UpdateCvars`; it recognizes custom-setting CVars such as `weapon_reload_gauntlet` and `g_damage_sg_outer`, then sets or clears the corresponding bits in the published `g_customSettings` mask. | High |
| `0x10054920` | `G_RegisterCvars` | `g_main.c::G_RegisterCvars` | Walks the main game cvar table, tracks `g_customSettings`, clamps `g_gametype`, and explicitly registers `g_version`, matching the retail registration pass. | High |
| `0x100549E0` | `G_InitPublishedCvarState` | Retail-only `G_InitGame` sidecar | Called immediately after `G_RegisterCvars`; it seeds the published factory/custom/loadout configstring slab plus the retail Domination/Red Rover numeric configstrings and snapshots the related cvar mirrors used later in gameplay. | High |
| `0x10054DD0` | `G_UpdateCvars` | `g_main.c::G_UpdateCvars` | Walks the same cvar table with modification-count tracking, refreshes `g_customSettings`, and fans into follow-on update handlers just like the retail cvar update pass. | High |
| `0x10054F00` | `FindIntermissionPoint` | `g_main.c::FindIntermissionPoint` | Anchored by `info_player_intermission` plus the warning fallback and the target-facing intermission-angle adjustment. | High |
| `0x10055000` | `G_CountSpawnPoints` | Retail-only descriptive helper inside `g_main.c::G_InitGame` | Clears the cached spawn counters, then scans all entities for `info_player_deathmatch`, `team_CTF_redspawn`, and `team_CTF_bluespawn` before the rest of `G_InitGame` continues. | High |
| `0x10055110` | `G_InitGame` | `g_main.c::G_InitGame` | `InitGame: %s` log line, cvar/bootstrap flow, entity/client initialization, and the inlined session/spawn setup all match. | High |
| `0x10055610` | `G_ShutdownGame` | `g_main.c::G_ShutdownGame` | `==== ShutdownGame ====` and `ShutdownGame:` strings plus session persistence on teardown. | High |
| `0x10055710` | `G_FindNextTournamentPlayer` | Retail-only descriptive helper split from `g_main.c::AddTournamentPlayer` | Returns the oldest waiting spectator while excluding scoreboard spectators and invalid follow states, matching the inner duel queue selector that the source keeps inline. | High |
| `0x10055780` | `AddTournamentPlayer` | `g_main.c::AddTournamentPlayer` | Duel-only queue promotion path that counts active players, chooses the oldest waiting spectator, calls `SetTeam(..., "f")`, and resets warmup/game-state latches when the second player joins. | High |
| `0x10055900` | `RemoveTournamentLoser` | `g_main.c::RemoveTournamentLoser` | Duel-only queue demotion path that selects `level.sortedClients[1]` when two players are active and calls `SetTeam(..., "s")` to send the loser back to spectator. | High |
| `0x10055950` | `AdjustTournamentScores` | `g_main.c::AdjustTournamentScores` | Tournament intermission helper that increments the winner's wins and loser's losses via `level.sortedClients`, then refreshes both configstrings through `ClientUserinfoChanged`. | High |
| `0x100559E0` | `G_UpdateAwardConfigstrings` | Retail-only award publisher appended to `g_main.c::CalculateRanks` | Tailcalled from both `SendScoreboardMessageToAllClients` and `CalculateRanks`; it selects winning clients for the legacy retail award configstrings at `0x2B4`, `0x2B5`, and `0x2B8-0x2BB` and publishes them through the shared `%i` formatter. | High |
| `0x10055E50` | `SendScoreboardMessageToAllClients` | `g_main.c::SendScoreboardMessageToAllClients` | Loops connected clients through the scoreboard sender exactly like the source wrapper, then falls through into the shared retail award-configstring refresh at `0x100559E0`. | High |
| `0x10055EB0` | `SortRanks` | `g_main.c::SortRanks` | The qsort comparator keeps scoreboard/follow spectators last and otherwise sorts active clients by session/score state exactly like the source rank-ordering helper. | High |
| `0x10056070` | `CalculateRanks` | `g_main.c::CalculateRanks` | Rebuilds connected/non-spectator counts, sorts `level.sortedClients`, assigns rank/tie state, updates score and leader configstrings, resends scoreboards during intermission, and then tails into the shared retail award-configstring refresh. | High |
| `0x10056B30` | `MoveClientToIntermission` | `g_main.c::MoveClientToIntermission` | Moves a client to the intermission origin and angles, switches to `PM_INTERMISSION`, and clears powerups plus transient entity/playerstate flags. | High |
| `0x10056CB0` | `BeginIntermission` | `g_main.c::BeginIntermission` | Intermission bootstrap that latches intermission time, runs tournament score adjustment, walks `MoveClientToIntermission`, and then extends the stock GPL flow with vote clearing and `nextmaps` setup. | High |
| `0x10057000` | `ExitLevel` | `g_main.c::ExitLevel` | Match-end exit path that triggers autoactions, removes the duel loser on tournament restarts, resolves the `nextmaps` or `map_restart` path, writes session data, and pushes connected clients back to `CON_CONNECTING`. | High |
| `0x100573F0` | `G_LogPrintf` | `g_main.c::G_LogPrintf` | Timestamped logfile writer used by init/shutdown, connect/disconnect, and other game log traffic. | High |
| `0x10057510` | `LogExit` | `g_main.c::LogExit` | Anchored by `Exit: %s`, `red:%i  blue:%i`, and the per-client `score:` log line while queueing intermission and single-player win/loss follow-ons. | High |
| `0x10057AD0` | `CheckIntermissionExit` | `g_main.c::CheckIntermissionExit` | Tailcalled from `CheckExitRules` during intermission; the body rebuilds the client ready bitmask, honors the `nextmaps`-extended wait, and exits through `ExitLevel` after the grace window. | High |
| `0x10057C60` | `ScoreIsTied` | `g_main.c::ScoreIsTied` | The body compares either the current duel leaders or the red/blue team scores by gametype and is queried directly from `CheckExitRules` before sudden-death exit handling. | High |
| `0x10057CD0` | `G_CanForfeit` | Retail-only shared helper spanning `g_cmds.c::Cmd_Forfeit_f` and `g_main.c::CheckExitRules` | Anchored by the forfeit rejection strings and used from both the client forfeit command and the automatic missing-player forfeit checks. | High |
| `0x10057F10` | `G_ApplyForfeit` | `g_main.c::G_ApplyForfeit` analogue | Forces the losing side into the forfeited score state, sets the forfeiture latch, prints `Game has been forfeited.`, and logs `Players have forfeited.` | High |
| `0x10058030` | `CheckExitRules` | `g_main.c::CheckExitRules` | Anchored by `Timelimit hit.`, `Fraglimit hit.`, and `Capturelimit hit.` strings. | High |
| `0x10058410` | `G_SyncTournamentQueueTeamTasks` | Retail-only duel queue helper | Watches for dirty queue-position updates, mirrors the one-based `pq` slot back into each waiting spectator's `teamtask` userinfo key, and republishes the affected clients through `ClientUserinfoChanged`. | High |
| `0x10058580` | `G_CheckReadyUpDelayAction` | Retail-only duel warmup helper | Arms `CS_READYUP_STATUS` from `g_warmupReadyDelay`, then applies `g_warmupReadyDelayAction` by forcing players ready or moving unready players to spectate-only when the deadline expires. | High |
| `0x100586E0` | `CheckTournament` | `g_main.c::CheckTournament` | Warmup/game-state transition logic plus the `Warmup:` log line. | High |
| `0x100588F0` | `G_UpdateVoteCounts` | Retail-only vote helper | Walks per-client vote states, updates the public yes/no vote configstrings, and short-circuits explicit player pass/veto outcomes via `%s passed the vote.` and `%s vetoed the vote.` | High |
| `0x10058AB0` | `G_TryExecuteVoteString` | Retail-only vote helper | Parses and executes Quake Live-specific vote strings such as `cointoss`, `random`, `loadouts`, `timers`, `shuffle`, `teamsize`, and `weaprespawn`, then reports whether the string was consumed. | High |
| `0x10059130` | `G_ClearVoteState` | Retail-only vote helper | Clears vote configstrings and each client's vote-status field; this helper is called from both `CheckVote` and the intermission bootstrap. | High |
| `0x100591B0` | `CheckVote` | `g_main.c::CheckVote` | Handles delayed vote execution plus the `Vote passed.`, `Vote failed.`, and Quake Live-specific `Voting time has expired.` outcomes before clearing vote state. | High |
| `0x100592C0` | `CheckCvars` | `g_main.c::CheckCvars` | Watches `g_password` changes, recomputes `g_needpass`, and republishes the paired server configstrings exactly like the source cvar watcher. | High |
| `0x10059370` | `G_RunThink` | `g_main.c::G_RunThink` | Preserves the classic `nextthink` / `ent->think` gate and `NULL ent->think` error while also servicing a neighboring retail callback slot ahead of the think dispatch. | High |
| `0x100593E0` | `G_UpdateTeamCountConfigstrings` | Retail-only HUD/configstring helper | Periodically refreshes the auxiliary team-count configstrings at `0x297` and `0x298`, using raw team rosters in ordinary team states and the active-player counter during round-controller states. | High |
| `0x100594D0` | `G_RunFrame` | `g_main.c::G_RunFrame` | Main frame loop advancing time, stepping entities, and running exit/team/vote helpers. | High |
| `0x10061800` | `Cmd_AllReady_f` | `g_cmds.c::Cmd_AllReady_f` | HLIL-visible admin helper for the `allready` command table entry; it validates access, enforces the duel two-player restriction, and sets every connected client's retail ready latch. | High |
| `0x10064280` | `G_RRResolveRoundState` | Retail-only Red Rover controller helper | Freeze-style pending-transition resolver that advances deferred `RR_RoundStateTransition` work and returns the current Red Rover round state. | High |
| `0x10064380` | `G_RRFinalizeSpawnLoadout` | Retail-only Red Rover spawn helper | Reached from `ClientSpawn` before the generic loadout finalizer; survivors fall through to `G_FinalizeSpawnLoadout`, while infected clients are forced onto the zombie role loadout by seeding the reduced weapon mask, selected weapon, and health/maxHealth directly. | High |
| `0x100643E0` | `G_RRHandleDamageScore` | Retail-only Red Rover infection damage helper / `g_client.c::G_RRHandleDamageScore` analogue | Called from the main damage path after armor resolution; it applies the shared self/team damage suppression policy, clamps survivor-vs-infected damage during the active infection state, accumulates threshold credit on the attacker, and pays out score increments through `CalculateRanks`. | High |
| `0x100645A0` | `G_RRResetClientForRound` | Retail-only Red Rover per-client round helper | Reused from both `ClientBegin` and the delayed respawn path; it reruns `ClientSpawn`, reapplies the Red Rover role-aware spawn finalizer, and pushes the client into the holding state while the round controller is still in its pre-release phase. | High |
| `0x100645E0` | `G_RRInitClient` | `g_client.c::G_RRInitClient` analogue | Spawn/bootstrap helper that seeds the infection-role flags from `sess.sessionTeam`, clears them for survivors when the RR toggles are disabled, and forces the holding-state bit while warmup or the pre-active controller state is still in effect. | High |
| `0x10064670` | `G_RRCheckRoundCompletion` | Retail-only Red Rover completion helper / `g_client.c::G_RRCheckRoundCompletion` analogue | Evaluates connected-team counts, applies the draw-delay gate, and latches the last infected client when infection mode leaves exactly one zombie standing. | High |
| `0x10064710` | `G_RRCheckExitRules` | Retail-only Red Rover exit helper | Suppresses exit while `ScoreIsTied()` is true, otherwise checks timelimit/roundlimit and optionally prints/logs the corresponding match-end messages. | High |
| `0x100647C0` | `G_RRResolveAutoJoinTeam` | Retail-only Red Rover infection helper | Reached from the autojoin path in `SetTeam` when infection mode is active; it resolves any pending controller transition and returns `TEAM_RED` for the preserved or newly selected infected slots and `TEAM_BLUE` for every other client. | High |
| `0x10064820` | `G_RRSeedInfectionTeams` | Retail-only Red Rover infection helper | Reached from the infection branch of `G_RRTrackRoundActivity`; it moves everyone back to `TEAM_BLUE`, restores the latched infected client when one exists, otherwise selects a random connected client from `level.sortedClients`, stores that slot, and returns the chosen infected client number. | High |
| `0x100649F0` | `RR_RoundStateTransition` | Retail-only Red Rover round-state controller | Anchored by `RR_RoundStateTransition: invalid state`; it resolves pending transition timers, updates the match-state configstrings, resets active participants, and drives the Red Rover active, complete, and restart phases. | High |
| `0x100652B0` | `G_RRApplySurvivalBonus` | Retail-only Red Rover infection helper | Anchored by `Survival Bonus! +%i`; when the infection ruleset is active it checks the survival-bonus timer, awards the configured score delta to the connected team-2 participants, emits the matching temp-entity event, and refreshes ranks. | High |
| `0x10065410` | `G_RRCheckInfectionSpread` | Retail-only Red Rover infection helper | Anchored by `Infection spreads in %i second%s!`; it announces the next spread window and, when the timer expires, converts the next eligible connected participant through the deeper team/state mutation helper before rearming the timer. | High |
| `0x100655A0` | `G_RRTrackRoundActivity` | `g_client.c::G_RRTrackRoundActivity` | Source-faithful outer Red Rover per-frame activity monitor; it refreshes the controller state, applies the survival-bonus and infection-spread helpers, evaluates round completion, and advances the controller when the round ends. | High |
| `0x10065680` | `G_RRInitRoundController` | Retail-only Red Rover init helper | Reached from `G_InitGame`; it clears the infection-selection trackers, seeds the first pending controller state, and primes the Red Rover state machine for either normal or infection-enabled starts. | High |
| `0x10065700` | `G_RRHandlePlayerDeath` | `g_client.c::G_RRHandlePlayerDeath` analogue | Retail death-path helper that flips the victim between Red Rover teams, refreshes userinfo, emits the infection temp-entity when applicable, updates infection timers/bonus state, and reevaluates round completion. | High |
| `0x10065F30` | `G_SpawnClassExemptFromSpawnFilter` | Retail-only `g_spawn.c` helper (no direct GPL analogue) | Anchored by `item_armor_shard`, `team_redobelisk`, and `team_blueobelisk`, then used inside `G_SpawnGEntityFromSpawnVars` to bypass the normal `notfree` / `notteam` / `gametype` / `not_gametype` rejection path for specific classes. | High |
| `0x10066230` | `G_ParseSpawnVars` | `g_spawn.c::G_ParseSpawnVars` | Parse/error strings match the brace-bounded entity parser. Retail inlines `G_AddSpawnVarToken` here. | High |
| `0x10066440` | `SP_worldspawn` | `g_spawn.c::SP_worldspawn` | `SP_worldspawn: The first entity isn't 'worldspawn'` string, world metadata parsing, and warmup/configstring setup. | High |
| `0x10066B90` | `ConsoleCommand` | `g_svcmds.c::ConsoleCommand` | HLIL-only boundary dispatching `entitylist`, `forceteam`, `game_memory`, `addbot`, `botlist`, `game_crash`, `forceshuffle`, `dumpvars`, and `reload_access` before the remaining hidden debug/admin fallthrough. | High |
| `0x10067EC0` | `G_ClientsOnSameTeam` | Retail-only native export helper wrapping `g_team.c::OnSameTeam` | Compares two `gclient_t` session teams directly and keeps the retail spectator-equality allowance that survives below `GT_TEAM`. | High |
| `0x10067F00` | `G_ClientNumsOnSameTeam` | Retail-only native export helper wrapping `g_team.c::OnSameTeam` | Validates two client numbers against `level.clients` and then tails into `G_ClientsOnSameTeam`. | High |
| `0x10067F30` | `OnSameTeam` | `g_team.c::OnSameTeam` | Entity-level same-team predicate used across combat, chat, and objective logic; retail keeps the classic client/sessionTeam comparison but treats matching spectators as same-team even outside team gametypes. | High |
| `0x10067F70` | `G_IsClientSpectator` | Retail-only native export helper | Validates the client slot and returns whether `sess.sessionTeam == TEAM_SPECTATOR`. | High |
| `0x100680C0` | `TeamCount` | `g_client.c::TeamCount` | HLIL preserves the classic ignore-client, connected-state, and `sess.sessionTeam` loop even though the committed decomp still drops one register-passed argument. | High |
| `0x10068100` | `Team_CountsBalanced` | Retail-only `g_teamForceBalance` helper | Extracted boolean helper that returns true when the current red/blue spread is at most one player; retail reuses it from both `SetTeam` and `Cmd_ReadyUp_f` before their stricter join/ready gates. | High |
| `0x10068140` | `Team_HasMinimumPlayersForWarmup` | `g_team.c::Team_HasMinimumPlayersForWarmup` | Warmup gate that checks the duel/team minimum-player requirements and the stronger both-teams-present rule used by the retail ready-up flow. | High |
| `0x10068490` | `TeamplayInfoMessage` | `g_team.c::TeamplayInfoMessage` | Uses the `tinfo %i %s` payload while building team overlay info for clients. | High |
| `0x1006AAF0` | `SpawnObelisk` | `g_team.c::SpawnObelisk` | `SpawnObelisk: %s startsolid at %s` diagnostic and the matching overload spawn flow. | High |
| `0x1006B110` | `G_TotalLivingHealthByTeam` | Retail-only Freeze tally helper | Sums entity health for the connected `PM_NORMAL` clients grouped by `sess.sessionTeam`, feeding the freeze round-end health summary and tiebreak path. | High |
| `0x1006B170` | `G_CountActivePlayersByTeam` | Retail-only shared team counter | Counts connected clients whose `ps.pm_type == PM_NORMAL`, grouped by `sess.sessionTeam`; retail reuses it for Freeze, Red Rover, teamsize validation, and the auxiliary team-count configstrings. | High |
| `0x1006B1C0` | `G_CountConnectedClientsByTeam` | Retail-only shared roster counter | Counts all connected clients by `sess.sessionTeam` without the `PM_NORMAL` filter used by `G_CountActivePlayersByTeam`. | High |
| `0x1006B210` | `G_NotifyLastAlivePlayer` | Retail-only shared round alert helper | Locates the sole surviving `PM_NORMAL` client on the selected team, emits the paired temp-entity/event, and sends that client the preserved centerprint notification reused by A/D, Clan Arena, Freeze, and Red Rover. | High |

## Supporting Helper Aliases Added In The Same Pass

- Active-client helpers: `P_DamageFeedback`, `P_WorldEffects`, `G_SetClientSound`, `ClientImpacts`, `G_TouchTriggers`, `SpectatorThink`, `ClientInactivityTimer`, `G_CheckClientFlood`, `G_RunFactoryHealthRegen`, `G_RunFactoryArmorRegen`, `ClientTimerActions`, `ClientEvents`, `StuckInOtherClient`, `SendPendingPredictableEvents`, `ClientThink_real`, `ClientSpawn`.
- Bot and training helpers: `G_ParseInfos`, `G_AddTrainerBot`.
- Spawn/reset helpers: `G_CAADRespawnAsSpectator`, `G_CAADResetClientForRound`, `G_FinalizeSpawnLoadout`, `G_RRFinalizeSpawnLoadout`, `G_RRResetClientForRound`.
- Item lifecycle helpers: `RespawnItem`, `Touch_Item`, `Use_Item`, `G_CheckTeamItems`, `FinishSpawningItem`, `G_SpawnItem`.
- Attack and Defend controller helpers: `G_ADShouldTimeoutActiveRound`, `G_ADResolveRoundState`, `G_ADResolveAttackingTeam`, `G_ADResolveDefendingTeam`, `G_ADHandleDamageScore`, `G_ADCheckExitRules`, `AD_RoundStateTransition`, `G_ADNotifyLastAlivePlayer`, `G_ADResetScoreHistory`, `G_ADUpdateScoreHistory`.
- Clan Arena round helpers: `G_CAResolveRoundState`, `G_CAHandleDamageScore`, `G_CANotifyLastAlivePlayer`.
- Freeze and round-controller helpers: `G_FreezeResolveRoundState`, `G_FreezeSetClientFrozenState`, `G_FreezeResetClientForRound`, `G_FreezeTeamIsFullyFrozen`, `G_FreezeEvaluateRoundWinner`, `Freeze_RoundStateTransition`, `G_FreezeRunFrame`, `G_FreezeNotifyLastAlivePlayer`, `G_FreezeClientEndFrame`, `G_NotifyLastAlivePlayer`, `RR_RoundStateTransition`, `G_UpdateTeamCountConfigstrings`, `G_TotalLivingHealthByTeam`, `G_CountActivePlayersByTeam`, `G_CountConnectedClientsByTeam`.
- Red Rover controller helpers: `G_RRResolveRoundState`, `G_RRHandleDamageScore`, `G_RRInitClient`, `G_RRCheckRoundCompletion`, `G_RRCheckExitRules`, `G_RRResolveAutoJoinTeam`, `G_RRSeedInfectionTeams`, `G_RRApplySurvivalBonus`, `G_RRCheckInfectionSpread`, `G_RRTrackRoundActivity`, `G_RRInitRoundController`, `G_RRHandlePlayerDeath`.
- Ready/warmup helpers: `Cmd_ReadyUp_f`, `Cmd_AllReady_f`, `G_CheckReadyUpDelayAction`, `Team_HasMinimumPlayersForWarmup`.
- Command/tournament queue helpers: `Cmd_TeamTask_f`, `SetTeam`, `G_UpdateTournamentQueuePositions`, `G_SyncTournamentQueueTeamTasks`.
- Scoreboard helpers: `DeathmatchScoreboardMessage`, `G_BuildCompactScoreboardMessage`, `G_BuildObeliskScoreboardMessage`, `G_BuildFFAScoreboardMessage`, `G_BuildDuelScoreboardMessage`, `G_BuildRaceScoreboardMessage`, `G_BuildTeamScoreboardMessage`, `G_SendTDMStatsMessage`, `G_BuildClanArenaScoreboardMessage`, `G_SendCAStatsMessage`, `G_BuildCTFStyleScoreboardMessage`, `G_SendCTFStatsMessage`, `G_BuildFreezeScoreboardMessage`, `G_BuildRedRoverScoreboardMessage`.
- Session helpers: `G_WriteClientSessionData`, `G_ReadSessionData`, `G_InitSessionData`, `G_WriteSessionData`.
- Intermission/rank helpers: `FindIntermissionPoint`, `G_CountSpawnPoints`, `G_FindNextTournamentPlayer`, `AddTournamentPlayer`, `RemoveTournamentLoser`, `AdjustTournamentScores`, `G_UpdateAwardConfigstrings`, `SendScoreboardMessageToAllClients`, `SortRanks`, `CalculateRanks`, `MoveClientToIntermission`, `BeginIntermission`, `ExitLevel`.
- Spawn helpers: `G_SpawnString`, `G_NewString`, `G_ParseField`, `G_CallSpawn`, `G_SpawnGEntityFromSpawnVars`.
- Server console helpers: `ClientForString`, `Svcmd_ForceTeam_f`.
- Team helpers: `G_ClientsOnSameTeam`, `G_ClientNumsOnSameTeam`, `OnSameTeam`, `G_IsClientSpectator`, `TeamCount`, `Team_CountsBalanced`, `Team_HasMinimumPlayersForWarmup`, `CheckTeamStatus`, `Team_ReturnFlagSound`, `Team_TakeFlagSound`, `Team_CaptureFlagSound`.
- Retail-only vote/forfeit helpers: `G_CanForfeit`, `G_ApplyForfeit`, `G_UpdateVoteCounts`, `G_TryExecuteVoteString`, `G_ClearVoteState`.
- Native export-tail helpers: `G_AreEnemyClients`, `G_IsObjectiveEntity`, `G_FreezeCanSeeThawProgressEvent`, `G_IsClientAdmin`, `G_GetClientScore`.
- Core wrappers: `G_Printf`, `G_Error`.

## Important Disagreements And Split Paths

- `dllEntry` writes `0xA` through its third out-parameter. In the native Quake Live loader contract this is an API-version handoff, not a reliable export-count field; the returned qagame export table continues past the 10 `VM_CallNativeExports` slots used by the current engine call switch.
- `ClientThink` at `0x10035410` is visible in HLIL and in the native export table, but the committed `functions.csv` still does not emit that function start.
- `G_CheckClientFlood` at `0x100341E0` is a descriptive retail-only split from the broader `ClientThink_real` path. It shares the same `floodCount` / `floodLastTime` state used by the current source tree, but unlike `g_cmds.c::G_FloodLimited` it drops over-limit clients directly from the active-client path instead of only rate-limiting commands.
- `ClientThink_real` is a clean retail boundary at `0x10034C90`, and the surrounding `ClientEvents` (`0x10034860`) plus `StuckInOtherClient` (`0x10034B50`) splits are now settled.
- `G_RunFactoryHealthRegen` at `0x10034260` and `G_RunFactoryArmorRegen` at `0x100342F0` are descriptive retail-only helpers factored out of the current source tree's broader `G_RunFactoryRegen`. Retail keeps separate per-frame health and armor regen timers keyed off the last-damage timestamp and the client-side accumulator/latch fields, while the reconstructed GPL-derived tree currently models the same policy in one helper.
- `ClientSpawn` at `0x1003BC30` is source-faithful on its outer boundary, but retail factors the post-spawn loadout/finalization work into the deeper helper at `0x1003B5A0` instead of keeping the whole spawn bootstrap inside one GPL-shaped function.
- `DeathmatchScoreboardMessage` at `0x1003CBF0` is still source-faithful on its public role, but the retail build factors almost all payload formatting into a helper family: compact fallback, duel, Race, TDM, Clan Arena, shared CTF-style, Freeze, Red Rover, and Overload serializers, plus the intermission-only `tdmstats` / `castats` / `ctfstats` publishers. The duel serializer also caches the lower/higher live duel client numbers in `level + 0x1C08/+0x1C0C` instead of keeping that ordering entirely local.
- `G_CAADRespawnAsSpectator` at `0x10035960` and `G_CAADResetClientForRound` at `0x10038160` are descriptive retail-only shared Clan Arena / Attack and Defend helpers. Retail keeps the per-client round reset and dead-player spectator-follow fallback in standalone helpers that the GPL-derived tree does not preserve with these exact boundaries.
- `G_FinalizeSpawnLoadout` at `0x1003B5A0` is a descriptive retail-only recovery name. The current GPL-derived tree spreads the same selected-weapon, grant-script, and starting-ammo/item work across `ClientSpawn`, `G_GrantConfiguredItems`, and adjacent spawn helpers instead of preserving a standalone post-spawn finalizer.
- Retail keeps the item lifecycle split cleanly across `G_SpawnItem -> FinishSpawningItem -> Touch_Item` with the optional `Use_Item -> RespawnItem` trampoline, while `G_CheckTeamItems` remains a separate objective-validator pass. The current GPL-derived tree preserves the same core behavior, but some map bootstrap and spawn-side item setup is easier to read inline than in this retail helper chain.
- `G_ADResolveRoundState`, `G_ADResolveAttackingTeam`, `G_ADResolveDefendingTeam`, `G_ADHandleDamageScore`, `G_ADCheckExitRules`, `G_ADResetScoreHistory`, and `G_ADUpdateScoreHistory` are descriptive retail-only helper names. The current GPL-derived tree keeps Attack and Defend round-state reads, side selection, damage-credit thresholds, and `scores_ad` publishing distributed across broader mode logic rather than exposing these exact standalone boundaries.
- `G_ADShouldTimeoutActiveRound`, `G_ADNotifyLastAlivePlayer`, `G_CAResolveRoundState`, `G_CAHandleDamageScore`, `G_CANotifyLastAlivePlayer`, `G_FreezeNotifyLastAlivePlayer`, and `G_NotifyLastAlivePlayer` are likewise descriptive retail-only helper names. The current GPL-derived tree keeps the active-round timeout and last-survivor alert logic folded into broader round-controller code instead of preserving these exact standalone boundaries.
- `AD_RoundStateTransition` at `0x10035B70` is a retail-only controller name recovered directly from the preserved invalid-state diagnostic. The current GPL-derived tree does not preserve an exact standalone Attack and Defend controller with this boundary or the adjacent side-resolver and score-history publisher split.
- `G_AddTrainerBot` at `0x100378E0` is a descriptive retail-only training helper name. The current GPL-derived tree keeps training-map bootstrap logic in broader init/setup flows instead of preserving a dedicated wrapper that only spawns the fixed `Trainer` bot and immediately issues `loaddeferred`.
- `G_InitWorldSession` is inlined into retail `G_InitGame`. The `session` cvar read and the `Gametype changed, clearing session data.` print occur inside `G_InitGame`, not a separate helper boundary.
- The outer `G_SpawnEntitiesFromString` loop is likewise inlined into `G_InitGame`: retail parses the first entity, runs `SP_worldspawn`, then loops `G_SpawnGEntityFromSpawnVars` until `G_ParseSpawnVars` returns false.
- `G_CountSpawnPoints` at `0x10055000` is a descriptive recovery name. The source tree keeps the spawn counter reset and entity scan inside the broader `G_InitGame` setup instead of exposing a standalone helper.
- `G_FindNextTournamentPlayer` at `0x10055710` is also descriptive: the current source keeps the queue-selection logic inline inside `AddTournamentPlayer`, but retail split it into a stable callable helper.
- `G_UpdateAwardConfigstrings` at `0x100559E0` is a descriptive retail-only recovery name. The helper publishes winning client numbers into a legacy award configstring block (`0x2B4`, `0x2B5`, `0x2B8-0x2BB`) that the current source tree no longer preserves as standalone server-side state.
- `SendScoreboardMessageToAllClients` at `0x10055E50` is source-faithful on its outer boundary, but retail makes it slightly fatter by tailcalling `G_UpdateAwardConfigstrings` instead of returning immediately after the scoreboard loop.
- `CalculateRanks` at `0x10056070` is a clean outer boundary, but the retail body appends the same shared `G_UpdateAwardConfigstrings` tail path after the main rank and score-configstring work.
- `G_AddSpawnVarToken` is inlined into `G_ParseSpawnVars`; the error string survives, but the helper body does not exist as a stable standalone function in the current retail build.
- Retail `G_SpawnGEntityFromSpawnVars` also adds a classname-based exemption helper plus a `not_gametype` path around the source-equivalent gametype filters. That logic does not survive as a direct GPL helper name, so `G_SpawnClassExemptFromSpawnFilter` is a descriptive recovery name for the observed retail behavior.
- `ConsoleCommand` at `0x10066B90` is visible in HLIL and in the native export table, but the committed `functions.csv` does not currently list that function start.
- `ClientCommand` at `0x10045DD0` is in the same situation: it is visible in HLIL and the native export table, but not currently emitted as a function start in the committed `functions.csv`.
- `Use_Item` at `0x1004FD20` is also HLIL-visible as a stable standalone thunk, but the committed `functions.csv` does not currently emit that function start.
- `Cmd_AllReady_f` at `0x10061800` is likewise HLIL-visible via the `allready` command table entry, but the committed `functions.csv` does not currently emit that function start.
- `G_FreezeEvaluateRoundWinner` at `0x1004BF60` is a descriptive retail-only helper name. The current source keeps the same winner-selection role inside a simpler `team_t` helper backed by cached level tallies, while retail passes explicit count/health arrays and stores the resolved winner in `data_105df598`.
- `G_FreezeResolveRoundState` at `0x1004BC30` and `G_RRResolveRoundState` at `0x10064280` are descriptive retail-only controller read helpers. The current GPL-derived tree reads `level.roundState` and its timers directly instead of routing callers through standalone pending-transition resolvers.
- `G_FreezeSetClientFrozenState` at `0x1004BC80` is a descriptive retail-only shared helper name. Retail folds the current source tree's separate `G_FreezeApplyFreezeState` and `G_FreezeThawClient` responsibilities into one callable state mutator.
- `G_FreezeResetClientForRound` at `0x1004BDE0` is likewise descriptive. Retail factors a per-client reset helper out of the broader GPL-style `G_FreezeResetClientsForRound` loop and reuses it from both bootstrap and delayed active-client reset paths.
- `G_FreezeTeamIsFullyFrozen` at `0x1004BF10` is a descriptive retail-only helper name. The committed decomp still hides the register-passed team argument, but HLIL shows the connected-client scan that `G_FreezeEvaluateRoundWinner` uses to detect when one side has no unfrozen members left.
- `G_FreezeRunFrame` at `0x1004CB80` is source-faithful on its outer boundary, but retail delegates the detailed round-state transition and winner-selection work to neighboring helpers instead of keeping the whole flow inside one GPL-shaped function.
- `G_FreezeClientEndFrame` at `0x1004CD40` is source-faithful on its outer boundary, but retail delegates the actual freeze/thaw mutation into the shared helper at `0x1004BC80` instead of keeping the whole flow inside one GPL-shaped function.
- `G_CanClientSeeClient` at `0x10052DC0` is a descriptive retail-only native export helper. The current GPL tree does not expose a standalone client-visibility predicate for the snapshot builder, while retail uses this slot from `SV_AddEntitiesVisibleFromPoint` to force-include spectator, teammate, and Red Rover infection client entities outside the ordinary PVS-only path.
- `G_AreEnemyClients` at `0x10052E40` is a descriptive retail-only native export helper. The current source tree does not expose a standalone client-number predicate for "distinct non-spectator opponents", so the recovered name reflects the exact HLIL gate rather than a GPL symbol.
- `G_ShouldSuppressVoiceToClient` at `0x10052E90` is a descriptive retail-only native export helper. The host calls it from the Steam voice relay loop and forwards the packet only when this predicate returns false, so the recovered name follows the real suppression semantics instead of pretending the GPL chat/voice helpers expose an equivalent standalone filter.
- `G_IsObjectiveEntity` at `0x10052F40` is likewise descriptive. Retail centralizes gametype-specific objective detection for flag items, obelisks, and extended Quake Live objective items in this export-tail helper instead of leaving that policy scattered through UI- or engine-facing call sites.
- `G_FreezeCanSeeThawProgressEvent` at `0x10053020` is a descriptive retail-only helper name. The stock GPL tree does not expose a standalone Freeze event-visibility predicate; retail split out the thaw-progress temp-entity filter keyed by event `0x58` and the linked teammate entity.
- The current source bridge still surfaces thaw-complete visuals through `EV_PLAYER_TELEPORT_IN` plus `QL_EVENTPARM_FREEZE_THAW` rather than the raw retail thaw event ordinal. That compatibility marker exists only because the shared GPL event enum has not yet been realigned to the retail `0x57` / `0x58` Freeze temp-entity band recovered from qagame/cgame.
- `G_RunFrame` at `0x100594D0` does not appear to call a standalone `G_RunClient` helper in the current retail build. The entity loop walks client slots inline and dispatches `ClientThink_real` directly, so the classic thin wrapper appears to be inlined or absent.
- `OnSameTeam` at `0x10067F30` is source-faithful on its outer boundary, but retail broadens the non-team-gametype case: matching spectators are treated as same-team instead of immediately returning false whenever `g_gametype < GT_TEAM`.
- `G_GetClientScore` at `0x100530F0` is a synthetic recovery name for a stable retail helper boundary. The body is just a validated getter for `gclient->ps.persistant[PERS_SCORE]`, and the GPL-derived tree does not preserve it as a standalone named function.
- The native export table tail beyond the public `GAME_*` slots now appears fully settled. `G_CanClientSeeClient`, `G_AreEnemyClients`, `G_ShouldSuppressVoiceToClient`, `G_IsObjectiveEntity`, `G_FreezeCanSeeThawProgressEvent`, `G_GetClientScore`, `G_IsClientAdmin`, `G_ClientsOnSameTeam`, `G_ClientNumsOnSameTeam`, `OnSameTeam`, and `G_IsClientSpectator` all have stable HLIL bodies plus host-side consumers.
- `Freeze_RoundStateTransition` at `0x1004C1B0` and `RR_RoundStateTransition` at `0x100649F0` are retail-only controller names recovered directly from preserved invalid-state diagnostics. The current GPL-derived tree spreads the equivalent behavior across `G_Frame_UpdateRoundController`, `G_FreezeResetClientsForRound`, `G_FreezeHandleRoundEnd`, and the Red Rover round helpers instead of preserving these exact standalone boundaries.
- `SetTeam` at `0x100406D0` is source-faithful on its outer boundary, but retail splits the actual session/team mutation and respawn execution into the deeper helper at `0x10040440` instead of keeping the entire flow inside one GPL-shaped function.
- `TeamCount` at `0x100680C0` is source-faithful on its outer boundary, but the committed decomp still drops the register-passed `ignoreClientNum` argument even though HLIL preserves the comparison against the skipped client slot.
- `Team_CountsBalanced` at `0x10068100` is a descriptive retail-only helper name. The underlying logic is the extracted `g_teamForceBalance` spread check, which the GPL-derived tree keeps inline inside `SetTeam` instead of exposing as a stable callable boundary.
- `G_UpdateTeamCountConfigstrings` at `0x100593E0` is a descriptive retail-only helper name. The current GPL-derived tree does not preserve standalone configstring slots at `0x297` and `0x298`, so the best evidence-backed recovery is the observed periodic per-team count publisher rather than a stock source symbol.
- `G_CountActivePlayersByTeam`, `G_TotalLivingHealthByTeam`, and `G_CountConnectedClientsByTeam` are descriptive retail-only helper names. The current GPL-derived tree keeps the same counting logic inside larger Freeze, Red Rover, and match-state routines instead of preserving these standalone helpers.
- `G_RRCheckRoundCompletion` at `0x10064670` is a descriptive retail-only helper name. Retail passes explicit connected-team counts and preserves a separate last-infected latch for infection mode, while the current GPL-derived tree keeps simpler winner logic inline in `G_RRTrackRoundActivity`.
- `G_RRCheckExitRules` at `0x10064710` is a descriptive retail-only helper name. The stock tree keeps Red Rover's time/round limit handling inside broader round-flow code, while retail split the tie-aware RR timelimit and roundlimit gate into a standalone check.
- `G_RRHandleDamageScore` at `0x100643E0` is a descriptive retail-only helper name. The current GPL-derived tree keeps Red Rover's survivor scoring logic in `g_client.c::G_RRHandleDamageScore`, but retail folds the friendly-fire policy, infection-only damage clamping, and threshold score payout into one deeper damage-path helper.
- `G_RRFinalizeSpawnLoadout` at `0x10064380` and `G_RRResetClientForRound` at `0x100645A0` are descriptive retail-only Red Rover spawn helpers. Retail layers an infection-role loadout override and a separate per-client round reset wrapper around `ClientSpawn`, while the GPL-derived tree keeps the corresponding RR spawn/bootstrap work distributed across `ClientSpawn`, `G_RRInitClient`, and adjacent mode helpers.
- `G_RRInitClient` at `0x100645E0` is source-faithful on role but not on exact state shape. The current GPL-derived tree stores richer `rrInfectionState` and timer fields, while the retail helper mostly seeds the infection-role flag bits and the temporary holding-state latch during spawn/bootstrap.
- `G_RRResolveAutoJoinTeam` at `0x100647C0` and `G_RRSeedInfectionTeams` at `0x10064820` are descriptive retail-only infection helpers. The current GPL-derived tree does not preserve these standalone team-seeding boundaries or the latched infected-slot handoff through `SetTeam`; retail keeps both the autojoin resolver and the round-start infected reseed as explicit callable helpers.
- `G_RRApplySurvivalBonus` at `0x100652B0` and `G_RRCheckInfectionSpread` at `0x10065410` are descriptive retail-only Red Rover infection helper names. The current GPL-derived tree does not preserve these standalone timer-driven helpers or their exact score/countdown flow.
- `G_RRTrackRoundActivity` at `0x100655A0` is source-faithful on its outer boundary, but retail folds the round-completion, infection-spread, and controller-transition work into a denser helper chain than the current GPL-derived implementation.
- `G_RRInitRoundController` at `0x10065680` is a descriptive retail-only init helper. The current GPL-derived code seeds Red Rover round and infection state inline during setup instead of preserving a dedicated controller bootstrap boundary.
- `G_RRHandlePlayerDeath` at `0x10065700` is source-faithful on role but not on exact interface. Retail receives the victim's pre-mutation team and means-of-death from the death path, then performs the team swap or infection mutation inside this deeper helper instead of keeping the whole flow inline.
- `Cmd_ReadyUp_f` and `Cmd_AllReady_f` are source-faithful outer command boundaries, but retail toggles and serializes a dedicated Quake Live ready-state field at `client + 0x2E8` rather than relying only on the current source tree's `EF_READY` bit.
- `AddTournamentPlayer` and `RemoveTournamentLoser` are source-faithful queue boundaries, but the surrounding retail tournament flow is still split more aggressively than GPL, including the descriptive selector/helper layer around them and the retail-only award publisher at `0x100559E0`.
- `G_UpdateTournamentQueuePositions` and `G_SyncTournamentQueueTeamTasks` are descriptive retail-only queue helpers. Retail serializes extra duel queue fields (`so` / `pq`) through `ClientUserinfoChanged` and then mirrors queue order back through `teamtask` for HUD/UI compatibility; the GPL-derived tree does not preserve these helpers or fields.
- `G_CheckReadyUpDelayAction` at `0x10058580` is a descriptive retail-only helper. The current GPL-derived tree preserves `CS_READYUP_STATUS` publishing, ready commands, and warmup countdown logic, but not this standalone `g_warmupReadyDelay` / `g_warmupReadyDelayAction` controller that can force-ready players or push unready duel players into spectate-only state after a delay.
- `BeginIntermission` at `0x10056CB0` is broader than the stock GPL helper: in the retail build it also clears vote state through `G_ClearVoteState` and bundles extra `nextmaps` setup/configstring work after the core intermission transition.
- `ExitLevel` at `0x10057000` is likewise broader than the stock GPL helper: the retail build resolves `nextmaps`, falls back to `map_restart 0` when needed, clears extra match-award/intermission state, and still preserves the stock tournament-loser restart path.
- `Cmd_Forfeit_f` at `0x100456B0` is only a thin client-facing gate. Retail keeps the deeper eligibility checks and final forfeit state mutation in the separate helper pair `G_CanForfeit` / `G_ApplyForfeit`, so the current source's `Cmd_Forfeit_f` / `G_HandleForfeit` structure is only an approximate analogue.
- `G_CanForfeit`, `G_UpdateVoteCounts`, `G_TryExecuteVoteString`, and `G_ClearVoteState` are descriptive recovery names for stable retail-only helper boundaries. The current GPL-derived tree does not preserve these exact helpers as separate named functions.
- `CheckVote` at `0x100591B0` is a clean outer boundary, but retail keeps the tally, special-vote execution, and vote-state clearing work split into the adjacent helper trio rather than inlining it all into one GPL-shaped body.
- `G_RunThink` at `0x10059370` is slightly fatter than the stock GPL helper because it services an additional callback slot at `ent + 0x2FC` before the usual `nextthink` / `ent->think` dispatch.
- `Team_HasMinimumPlayersForWarmup` at `0x10068140` is source-faithful on its outer boundary. Retail feeds it through the same `TeamCount` primitive used by `SetTeam`, but the committed decomp still obscures the low-level register-passed ignore-client argument on that helper.

## Open Questions

- No high-confidence unresolved function seams remain in the current curated qagame control surface. The remaining reverse-engineering work is now mostly type/data recovery, especially the client-side regen accumulator/latch fields consumed by `G_RunFactoryHealthRegen` and `G_RunFactoryArmorRegen`.
