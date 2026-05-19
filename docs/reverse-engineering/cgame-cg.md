# cgame `cg_t` Layout Map

This note maps the retail-compatible x86 layout of `cg_t` used by
`cgamex86.dll` onto the current `src/code/cgame/cg_local.h` definition. The
goal is to separate the hard layout facts from the main ownership bands:
bootstrap and snapshot flow, local prediction and view state, scoreboard and
spectator HUD caches, buffered announcer and voice queues, and the combat
feedback tail that the draw and event code mutate every frame.

## Method

- Layout facts come from a local x86 record-layout dump of `cg_t` using
  `clang -target i686-pc-windows-msvc -DID_INLINE=__inline -Xclang -fdump-record-layouts`
  against `src/code/cgame/cg_local.h`.
- Member ownership was cross-checked against the main frame-state writers and
  consumers in `src/code/cgame/cg_main.c`, `cg_snapshot.c`, `cg_predict.c`,
  `cg_playerstate.c`, `cg_view.c`, `cg_draw.c`, `cg_scoreboard.c`,
  `cg_newdraw.c`, `cg_event.c`, `cg_servercmds.c`, `cg_screen.c`, and
  `cg_weapons.c`.
- Retail parity was anchored against the already-promoted `cgame` recoveries
  for `CG_Init`, `CG_UpdateCvars`, `CG_PredictPlayerState`,
  `CG_ProcessSnapshots`, `CG_DrawActiveFrame`, `CG_InitTeamChat`, and the
  recovered spectator-tracking and ownerdraw chains in
  `docs/reverse-engineering/cgame-mapping.md`.
- Nested payloads such as `playerState_t`, `centity_t`, `score_t`, and
  `clientInfo_t` keep their own ownership detail; this pass maps the top-level
  `cg_t` members and the strongest band-level semantics around them.

## Hard Layout Facts

- `sizeof(cg_t) = 0x2381C` (`145436`).
- The largest embedded slabs are:
  - `snapshot_t activeSnapshots[2]` at `0x0003C`
  - `playerState_t predictedPlayerState` at `0x1A544`
  - `centity_t predictedPlayerEntity` at `0x1A778`
  - `score_t scores[MAX_CLIENTS]` at `0x1B220`
  - `cgScoreStats_t scoreStats[MAX_CLIENTS]` at `0x1C320`
  - `skulltrail_t skulltrails[MAX_CLIENTS]` at `0x211B4`
  - `refEntity_t testModelEntity` at `0x23748`
- The top-level banding is:
  - bootstrap, snapshot ring, and prediction state at `0x00000-0x1AB23`
  - view, zoom, automation, and loading text at `0x1AB24-0x1B20B`
  - scoreboard, obituary, spectator, and tracking state at `0x1B20C-0x230B3`
  - HUD feedback, announcer/voice buffers, warmup, and pickup state at
    `0x230B4-0x2362B`
  - damage, view-kick, movement, predicted hitscan, and dev-tool state at
    `0x2362C-0x2381B`

## Bootstrap, Snapshot Ring, And Prediction State

Retail `CG_Init` seeds this whole front half, `CG_ProcessSnapshots` owns the
snapshot ring and interpolation pointers, and `CG_PredictPlayerState` owns the
predicted player block, event replay cache, and the local smoothing timers.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00000` | `clientFrame` | `int` | Rendered-frame counter incremented once per valid `CG_DrawActiveFrame`. |
| `0x00004` | `clientNum` | `int` | Local client index supplied by `CG_Init`. |
| `0x00008` | `demoPlayback` | `qboolean` | Frame-local demo/playback mode latch mirrored from the client system. |
| `0x0000C` | `levelShot` | `qboolean` | Suppresses the normal 2D HUD while the level-shot path is active. |
| `0x00010` | `deferredPlayerLoading` | `int` | Small scoreboard-side throttle used before `CG_LoadDeferredPlayers`. |
| `0x00014` | `loading` | `qboolean` | Startup latch that forces direct client loads during `CG_Init`. |
| `0x00018` | `competitiveHudLoaded` | `qboolean` | Retail HUD bootstrap result used by menu/feeder fallbacks. |
| `0x0001C` | `armorTieredEnabled` | `qboolean` | Cached `cg_armorTiered` state for ownerdraw and HUD logic. |
| `0x00020` | `voiceChatIndicatorEnabled` | `qboolean` | Cached voice-indicator enable state. |
| `0x00024` | `vignetteEnabled` | `qboolean` | Cached `cg_vignette` state for HUD scripting and draw gating. |
| `0x00028` | `intermissionStarted` | `qboolean` | Voice/reward gate set when the match is entering intermission. |
| `0x0002C` | `latestSnapshotNum` | `int` | Highest snapshot number reported by the engine. |
| `0x00030` | `latestSnapshotTime` | `int` | Latest engine-side snapshot time mirrored with `latestSnapshotNum`. |
| `0x00034` | `snap` | `snapshot_t *` | Current render snapshot pointer. |
| `0x00038` | `nextSnap` | `snapshot_t *` | Next interpolation target snapshot pointer. |
| `0x0003C` | `activeSnapshots[2]` | `snapshot_t[2]` | Double-buffered snapshot storage filled by `CG_ReadNextSnapshot`. |
| `0x1A514` | `frameInterpolation` | `float` | Snapshot interpolation fraction for entity lerp work. |
| `0x1A518` | `thisFrameTeleport` | `qboolean` | Prediction/snapshot teleport latch for the current frame. |
| `0x1A51C` | `nextFrameTeleport` | `qboolean` | Snapshot teleport latch for the upcoming frame. |
| `0x1A520` | `frametime` | `int` | Delta between `cg.time` and `cg.oldTime`. |
| `0x1A524` | `time` | `int` | Main render time for the current frame. |
| `0x1A528` | `oldTime` | `int` | Previous rendered frame time. |
| `0x1A52C` | `physicsTime` | `int` | Prediction-side time anchor taken from `snap` or `nextSnap`. |
| `0x1A530` | `timelimitWarnings` | `int` | One-minute/five-minute/overtime announcer latch bits. |
| `0x1A534` | `fraglimitWarnings` | `int` | Fraglimit countdown announcer latch bits. |
| `0x1A538` | `mapRestart` | `qboolean` | Set by `CG_MapRestart` so the next player-state transition respawns cleanly. |
| `0x1A53C` | `renderingThirdPerson` | `qboolean` | Resolved third-person camera mode for the current frame. |
| `0x1A540` | `hyperspace` | `qboolean` | Prediction/view flag raised by teleport trigger handling. |
| `0x1A544` | `predictedPlayerState` | `playerState_t` | Locally predicted or interpolated player state used by view, weapon, and HUD code. |
| `0x1A778` | `predictedPlayerEntity` | `centity_t` | Event/render entity mirror of `predictedPlayerState`. |
| `0x1AA50` | `validPPS` | `qboolean` | First-frame validity gate for `predictedPlayerState`. |
| `0x1AA54` | `predictedErrorTime` | `int` | Timestamp for prediction error decay. |
| `0x1AA58` | `predictedError` | `vec3_t` | Prediction error vector decayed into the camera origin. |
| `0x1AA64` | `eventSequence` | `int` | Local replay cursor for predictable player events. |
| `0x1AA68` | `predictableEvents[MAX_PREDICTED_EVENTS]` | `int[16]` | Rolling cache of emitted predictable events. |
| `0x1AAA8` | `stepChange` | `float` | Stair-step smoothing amount. |
| `0x1AAAC` | `stepTime` | `int` | Stair-step smoothing start time. |
| `0x1AAB0` | `duckChange` | `float` | Viewheight delta for duck smoothing. |
| `0x1AAB4` | `duckTime` | `int` | Duck smoothing start time. |
| `0x1AAB8` | `landChange` | `float` | Landing deflection amount. |
| `0x1AABC` | `landTime` | `int` | Landing deflection start time. |
| `0x1AAC0` | `weaponSelect` | `int` | Local desired weapon index sent through `trap_SetUserCmdValue`. |
| `0x1AAC4` | `autoAngles` | `vec3_t` | Slow auto-rotation angles for pickup/world-item renders. |
| `0x1AAD0` | `autoAxis[3]` | `vec3_t[3]` | Slow auto-rotation axis basis. |
| `0x1AAF4` | `autoAnglesFast` | `vec3_t` | Fast auto-rotation angles for pickup/world-item renders. |
| `0x1AB00` | `autoAxisFast[3]` | `vec3_t[3]` | Fast auto-rotation axis basis. |

## View, Zoom, Automation, And Loading

`CG_CalcViewValues`, `CG_CalcFov`, `CG_SetZoomState`, `CG_UpdateCvars`,
`CG_ClearAutomationState`, `CG_HandleAutoActionsIntermission`, and
`CG_RunQueuedAutoActions` own this band.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x1AB24` | `refdef` | `refdef_t` | Working render-definition block built each frame before scene submission. |
| `0x1AC94` | `refdefViewAngles` | `vec3_t` | View angles that back `refdef.viewaxis`. |
| `0x1ACA0` | `viewFilter` | `cgViewAngleFilter_t` | Spectator-camera angle smoothing ring and accumulator. |
| `0x1ADB0` | `zoomed` | `qboolean` | Current zoom state. |
| `0x1ADB4` | `zoomTime` | `int` | Last zoom transition timestamp. |
| `0x1ADB8` | `zoomSensitivity` | `float` | Usercmd sensitivity scale derived from the current zoom FOV. |
| `0x1ADBC` | `zoomToggle` | `qboolean` | Cached toggle-vs-hold zoom mode. |
| `0x1ADC0` | `zoomOutOnDeath` | `qboolean` | Cached zoom-release-on-death option. |
| `0x1ADC4` | `autoHopEnabled` | `qboolean` | Cached auto-hop option applied to local pmove settings. |
| `0x1ADC8` | `autoProjectileNudgeEnabled` | `qboolean` | Cached auto projectile-nudge option. |
| `0x1ADCC` | `projectileNudgeActive` | `qboolean` | Current frame's projectile-nudge active flag. |
| `0x1ADD0` | `projectileNudgeAmount` | `float` | Configured projectile nudge magnitude. |
| `0x1ADD4` | `projectileNudgeOffset` | `float` | Configured projectile nudge offset. |
| `0x1ADD8` | `predictLocalRailshots` | `qboolean` | Hitscan prediction enable flag used by rail/lightning helpers. |
| `0x1ADDC` | `autoActionFlags` | `int` | Cached `cg_autoAction` bitmask. |
| `0x1ADE0` | `autoActionFired` | `qboolean` | Guards the once-per-intermission auto-action trigger. |
| `0x1ADE4` | `autoActionScreenshotQueued` | `qboolean` | Delayed screenshot pending flag. |
| `0x1ADE8` | `autoActionStatsQueued` | `qboolean` | Delayed stats dump pending flag. |
| `0x1ADEC` | `autoActionScreenshotTime` | `int` | Scheduled screenshot time. |
| `0x1ADF0` | `autoActionStatsTime` | `int` | Scheduled stats dump time. |
| `0x1ADF4` | `autoActionDemoIndex` | `int` | Rotating demo index for auto-recording. |
| `0x1ADF8` | `deadBodyDarken` | `qboolean` | Cached corpse-darkening toggle. |
| `0x1ADFC` | `deadBodyColor` | `vec4_t` | Cached corpse palette color. |
| `0x1AE0C` | `infoScreenText` | `char[MAX_STRING_CHARS]` | Active loading/info screen text buffer. |

## Scoreboard, Obituary, Spectator, And Tracking State

The score and spectator half is shared between `cg_servercmds.c`,
`cg_scoreboard.c`, `cg_draw.c`, and `cg_newdraw.c`. The key retail owners are
the score parsers, `CG_DrawScoreboard`, the ownerdraw feeder helpers, and the
tracked spectator flow that updates `cg_trackPlayer`.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x1B20C` | `scoresRequestTime` | `int` | Throttle timer for `score` console-command requests. |
| `0x1B210` | `numScores` | `int` | Number of valid entries in `scores[]`. |
| `0x1B214` | `selectedScore` | `int` | Current scoreboard selection index. |
| `0x1B218` | `teamScores[2]` | `int[2]` | Cached red/blue scoreboard totals. |
| `0x1B220` | `scores[MAX_CLIENTS]` | `score_t[64]` | Flat score table consumed by both classic and menu-driven scoreboards. |
| `0x1C320` | `scoreStats[MAX_CLIENTS]` | `cgScoreStats_t[64]` | Expanded per-client HUD/scoreboard stat cache. |
| `0x20A20` | `teamScoreStats` | `cgTeamScoreStats_t` | Team-level stat summary for HUD scoreboxes. |
| `0x20AB4` | `clientKeyMask[MAX_CLIENTS]` | `int[64]` | Per-client carried-key bitmask mirrored from server commands. |
| `0x20BB4` | `showScores` | `qboolean` | User/requested scoreboard visibility latch. |
| `0x20BB8` | `scoreBoardShowing` | `qboolean` | Actual draw-result latch for the active scoreboard implementation. |
| `0x20BBC` | `scoreboardTimerRunning` | `qboolean` | Running-state latch for the match scoreboard timer. |
| `0x20BC0` | `scoreboardTimerStartTime` | `int` | Match scoreboard timer start anchor. |
| `0x20BC4` | `scoreboardTimerStopTime` | `int` | Last frozen scoreboard timer anchor. |
| `0x20BC8` | `scoreFadeTime` | `int` | Fade-out start time for transient scoreboard display. |
| `0x20BCC` | `killerName` | `char[MAX_NAME_LENGTH]` | Cached killer name used by death/scoreboard messaging. |
| `0x20BEC` | `obituaries[MAX_OBITUARIES]` | `cgObituary_t[8]` | Ring of recent obituary entries. |
| `0x20C6C` | `obituaryIndex` | `int` | Current write cursor into `obituaries[]`. |
| `0x20C70` | `spectatorList` | `char[MAX_STRING_CHARS]` | Concatenated spectator name string built from `cgs.clientinfo[]`. |
| `0x21070` | `spectatorLen` | `int` | Cached spectator string length. |
| `0x21074` | `spectatorWidth` | `float` | Cached spectator string width; reset when the list changes. |
| `0x21078` | `spectatorTime` | `int` | Legacy spectator ticker timing field retained in the layout. |
| `0x2107C` | `spectatorPaintX` | `int` | Legacy spectator ticker X cursor retained in the layout. |
| `0x21080` | `spectatorPaintX2` | `int` | Legacy second spectator ticker X cursor retained in the layout. |
| `0x21084` | `spectatorOffset` | `int` | Legacy spectator ticker string offset retained in the layout. |
| `0x21088` | `spectatorPaintLen` | `int` | Legacy spectator ticker paint length retained in the layout. |
| `0x2108C` | `spectatorPrimaryClient` | `int` | Primary spectator follow-card target. |
| `0x21090` | `spectatorSecondaryClient` | `int` | Secondary spectator follow-card target. |
| `0x21094` | `spectatorFollowClient` | `int` | Current followed client, or `-1` when not following. |
| `0x21098` | `spectatorClientOrder[MAX_CLIENTS]` | `int[64]` | Sorted follow-target order built from score state and valid clients. |
| `0x21198` | `spectatorClientCount` | `int` | Number of valid entries in `spectatorClientOrder[]`. |
| `0x2119C` | `spectatorTargetUpdateTime` | `int` | Last spectator target refresh time. |
| `0x211A0` | `spectatorTrackedClient` | `int` | Current tracked spectator client mirrored into `cg_trackPlayer`. |
| `0x211A4` | `spectatorCameraLocked` | `qboolean` | Lock that prevents spectator follow changes. |
| `0x211A8` | `trackedPlayerClientNum` | `int` | Pending auto-track target selected by events. |
| `0x211AC` | `trackedPlayerExpireTime` | `int` | Auto-track expiry time. |
| `0x211B0` | `trackedPlayerPriority` | `cgSpectatorTrackType_t` | Auto-track priority enum. |
| `0x211B4` | `skulltrails[MAX_CLIENTS]` | `skulltrail_t[64]` | Harvester skull trail history for each client. |

## HUD Feedback, Buffered Audio, Warmup, And Pickup State

This band is fed mainly by `CG_CenterPrint`, `CG_DrawReward`,
`CG_AddBufferedSound`, `CG_PlayBufferedVoiceChats`, `CG_ParseWarmup`, the
scoreboard draw code, and the item/powerup event handlers.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x230B4` | `centerPrintTime` | `int` | Centerprint start time. |
| `0x230B8` | `centerPrintScale` | `float` | Retail centerprint text scale stored by `CG_CenterPrint` and consumed by `CG_DrawCenterString`. |
| `0x230BC` | `centerPrintY` | `int` | Centerprint vertical anchor. |
| `0x230C0` | `centerPrint` | `char[1024]` | Active centerprint text buffer. |
| `0x234C0` | `centerPrintLines` | `int` | Cached centerprint line count. |
| `0x234C4` | `lowAmmoWarning` | `int` | Low-ammo warning state used by local sound and HUD feedback. |
| `0x234C8` | `lowAmmoWarningPercentile` | `float` | Cached low-ammo threshold value from the cvar path. |
| `0x234CC` | `weaponBarGrenadeColor` | `vec4_t` | Cached grenade color for HUD weapon-bar styling. |
| `0x234DC` | `lastKillTime` | `int` | Last local kill time used by reward/carnage timing. |
| `0x234E0` | `crosshairClientNum` | `int` | Client currently under the crosshair. |
| `0x234E4` | `crosshairClientTime` | `int` | Timestamp for crosshair-name fading. |
| `0x234E8` | `crosshairColor` | `vec4_t` | Cached base crosshair color. |
| `0x234F8` | `crosshairHitColor` | `vec4_t` | Cached hit-feedback crosshair color. |
| `0x23508` | `crosshairPulseEnabled` | `qboolean` | Cached item-pulse crosshair toggle. |
| `0x2350C` | `crosshairHitStyle` | `int` | Cached crosshair-hit style selector. |
| `0x23510` | `crosshairHitTime` | `int` | Cached crosshair-hit feedback duration. |
| `0x23514` | `powerupActive` | `int` | Last activated major powerup id. |
| `0x23518` | `powerupTime` | `int` | Last major powerup activation time. |
| `0x2351C` | `attackerTime` | `int` | Damage-feedback attacker banner timer. |
| `0x23520` | `voiceTime` | `int` | Voice menu visibility timer. |
| `0x23524` | `rewardStack` | `int` | Count of queued reward entries. |
| `0x23528` | `rewardTime` | `int` | Current reward display timer. |
| `0x2352C` | `rewardCount[MAX_REWARDSTACK]` | `int[10]` | Reward counts paired with the queued medal entries. |
| `0x23554` | `rewardShader[MAX_REWARDSTACK]` | `qhandle_t[10]` | Queued reward medal shaders. |
| `0x2357C` | `rewardSound[MAX_REWARDSTACK]` | `qhandle_t[10]` | Queued reward announcer sounds. |
| `0x235A4` | `soundBufferIn` | `int` | Announcer sound queue write cursor. |
| `0x235A8` | `soundBufferOut` | `int` | Announcer sound queue read cursor. |
| `0x235AC` | `soundTime` | `int` | Next announcer sound playback time. |
| `0x235B0` | `soundBuffer[MAX_SOUNDBUFFER]` | `qhandle_t[20]` | Buffered announcer sound ring. |
| `0x23600` | `voiceChatTime` | `int` | Next buffered voice-chat playback time. |
| `0x23604` | `voiceChatBufferIn` | `int` | Voice-chat queue write cursor. |
| `0x23608` | `voiceChatBufferOut` | `int` | Voice-chat queue read cursor. |
| `0x2360C` | `warmup` | `int` | Current warmup timer/configstring mirror. |
| `0x23610` | `warmupCount` | `int` | Last announced warmup countdown second. |
| `0x23614` | `itemPickup` | `int` | Last picked-up item id. |
| `0x23618` | `itemPickupTime` | `int` | Last item pickup time. |
| `0x2361C` | `itemPickupBlendTime` | `int` | Crosshair pulse timer for item pickup feedback. |
| `0x23620` | `weaponSelectTime` | `int` | Weapon selection UI timer. |
| `0x23624` | `weaponAnimation` | `int` | Active weapon animation index. |
| `0x23628` | `weaponAnimationTime` | `int` | Weapon animation timer. |

## Damage, View Kick, Movement, Predicted Hitscan, And Dev Tail

`CG_DamageFeedback`, the first-person view offset code, `CG_UpdateCvars`,
speedometer helpers, local rail/lightning prediction, and the test-model
console commands own this tail.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x2362C` | `damageTime` | `float` | Damage feedback start time used by the blend and head wobble paths. |
| `0x23630` | `damageX` | `float` | Damage direction X component in view space. |
| `0x23634` | `damageY` | `float` | Damage direction Y component in view space. |
| `0x23638` | `damageValue` | `float` | Current damage blend intensity. |
| `0x2363C` | `damagePlumPreset` | `damagePlumPreset_t` | Cached damage-plum preset mode. |
| `0x23640` | `damagePlumWeaponBits` | `unsigned int` | Cached enabled-weapon mask for damage plums. |
| `0x23644` | `damagePlumColorStyle` | `damagePlumColorStyle_t` | Cached damage-plum color style. |
| `0x23648` | `screenDamageColor` | `vec4_t` | Active screen-damage tint used by the `cg_screen.c` first-person damage blend. |
| `0x23658` | `screenDamageSelfColor` | `vec4_t` | Cached self-damage tint variant, including the packed alpha byte. |
| `0x23668` | `screenDamageTeamColor` | `vec4_t` | Cached team-damage tint variant. |
| `0x23678` | `screenDamageAlpha` | `float` | Active non-self screen-damage alpha byte. |
| `0x2367C` | `screenDamageAlphaTeam` | `float` | Cached team-damage alpha byte. |
| `0x23680` | `headYaw` | `float` | Legacy head-animation scratch field retained in the layout. |
| `0x23684` | `headEndPitch` | `float` | Target head pitch for the HUD head wobble animation. |
| `0x23688` | `headEndYaw` | `float` | Target head yaw for the HUD head wobble animation. |
| `0x2368C` | `headEndTime` | `int` | End time for the current HUD head wobble segment. |
| `0x23690` | `headStartPitch` | `float` | Start head pitch for the current HUD head wobble segment. |
| `0x23694` | `headStartYaw` | `float` | Start head yaw for the current HUD head wobble segment. |
| `0x23698` | `headStartTime` | `int` | Start time for the current HUD head wobble segment. |
| `0x2369C` | `v_dmg_time` | `float` | View-kick timer end for damage feedback. |
| `0x236A0` | `v_dmg_pitch` | `float` | Damage pitch kick amount. |
| `0x236A4` | `v_dmg_roll` | `float` | Damage roll kick amount. |
| `0x236A8` | `kickScale` | `float` | Cached `cg_kickScale` value. |
| `0x236AC` | `bobScale` | `float` | Cached `cg_bob` value. |
| `0x236B0` | `simpleItemsHeightOffset` | `float` | Cached simple-items height offset. |
| `0x236B4` | `simpleItemsRadius` | `float` | Cached simple-items radius. |
| `0x236B8` | `simpleItemsBob` | `float` | Cached simple-items bob amplitude. |
| `0x236BC` | `kick_angles` | `vec3_t` | Weapon/view kick angles. |
| `0x236C8` | `kick_origin` | `vec3_t` | Weapon/view kick positional offset. |
| `0x236D4` | `projectileNudgeCommandTime` | `int` | Command time tied to the last local projectile nudge. |
| `0x236D8` | `projectileNudgeMsec` | `int` | Effective nudge delta in milliseconds. |
| `0x236DC` | `projectileNudgeOrigin` | `vec3_t` | Local projectile-nudge origin scratch. |
| `0x236E8` | `bobfracsin` | `float` | Current bobbing sine factor. |
| `0x236EC` | `bobcycle` | `int` | Current bob-cycle parity/state. |
| `0x236F0` | `xyspeed` | `float` | Current horizontal player speed. |
| `0x236F4` | `speedometerSample` | `float` | Cached speedometer sample for the current frame. |
| `0x236F8` | `speedometerSampleTime` | `int` | Timestamp for `speedometerSample`. |
| `0x236FC` | `predictedLocalRailTime` | `int` | Timestamp for the cached predicted rail trace. |
| `0x23700` | `predictedLocalLightningTime` | `int` | Timestamp for the cached predicted lightning trace. |
| `0x23704` | `predictedLocalRailValid` | `qboolean` | Validity latch for the cached predicted rail trace. |
| `0x23708` | `predictedLocalLightningValid` | `qboolean` | Validity latch for the cached predicted lightning trace. |
| `0x2370C` | `predictedLocalRailHit` | `qboolean` | Cached predicted rail hit-world result. |
| `0x23710` | `predictedLocalLightningHit` | `qboolean` | Cached predicted lightning hit-world result. |
| `0x23714` | `predictedLocalRailStart` | `vec3_t` | Cached predicted rail trace start. |
| `0x23720` | `predictedLocalRailEnd` | `vec3_t` | Cached predicted rail trace end. |
| `0x2372C` | `predictedLocalLightningStart` | `vec3_t` | Cached predicted lightning trace start. |
| `0x23738` | `predictedLocalLightningEnd` | `vec3_t` | Cached predicted lightning trace end. |
| `0x23744` | `nextOrbitTime` | `int` | Next camera-orbit update time. |
| `0x23748` | `testModelEntity` | `refEntity_t` | Live development test-model entity submitted by the view debug commands. |
| `0x237D4` | `testModelName` | `char[MAX_QPATH]` | Registered name of the active development test model. |
| `0x23814` | `testGun` | `qboolean` | Development flag that renders the test model like a gun. |
| `0x23818` | `rageQuitTime` | `int` | Countdown latch before the queued `quit` command fires. |

## Ownership Notes

### Snapshot And Prediction Flow

- `CG_DrawActiveFrame` seeds `cg.time`, `cg.demoPlayback`, updates cvars,
  calls `CG_ProcessSnapshots`, bumps `clientFrame`, runs
  `CG_PredictPlayerState`, resolves `renderingThirdPerson`, builds `refdef`,
  and then drains the buffered sound and voice queues.
- `CG_ProcessSnapshots` owns `latestSnapshotNum`, `latestSnapshotTime`, `snap`,
  `nextSnap`, `activeSnapshots`, `thisFrameTeleport`, and `nextFrameTeleport`.
- `CG_PredictPlayerState` owns `validPPS`, `predictedPlayerState`,
  `predictedPlayerEntity`, `physicsTime`, `predictedErrorTime`,
  `predictedError`, the predictable-event cache, and the projectile-nudge
  scratch members.
- `CG_TransitionPlayerState` owns `duckChange` / `duckTime`, toggles
  `thisFrameTeleport` on follow changes, and calls the local feedback helpers.

### View And Automation

- `CG_CalcViewValues` owns `refdef`, `refdefViewAngles`, `bobfracsin`,
  `bobcycle`, `xyspeed`, `renderingThirdPerson`, `nextOrbitTime`, and the
  application of `predictedError`.
- `CG_SetZoomState`, `CG_HandleZoomOutOnDeath`, and `CG_CalcFov` own
  `zoomed`, `zoomTime`, and `zoomSensitivity`.
- `CG_FilterViewAngles` owns the `viewFilter` ring.
- `CG_UpdateCvars` owns the cached cvar mirrors:
  `armorTieredEnabled`, `voiceChatIndicatorEnabled`, `vignetteEnabled`,
  `kickScale`, `bobScale`, simple-items tuning, dead-body palette fields,
  screen-damage customization, crosshair customization, and auto-action flags.
- `CG_ClearAutomationState`, `CG_HandleAutoActionsIntermission`, and
  `CG_RunQueuedAutoActions` own `autoActionFlags`,
  `autoActionFired`, `autoActionScreenshotQueued`,
  `autoActionStatsQueued`, `autoActionScreenshotTime`,
  `autoActionStatsTime`, and `autoActionDemoIndex`.

### Scoreboard And Spectator State

- Score parsing and scoreboard feed helpers own `numScores`, `selectedScore`,
  `teamScores`, `scores[]`, `scoreStats[]`, `teamScoreStats`, and
  `scoresRequestTime`.
- `CG_DrawScoreboard` owns the `deferredPlayerLoading` cadence and writes
  `scoreBoardShowing`.
- `CG_BuildSpectatorString` owns `spectatorList`, `spectatorLen`, and resets
  `spectatorWidth`.
- The retail spectator-tracking chain in `cg_newdraw.c` owns
  `spectatorPrimaryClient`, `spectatorSecondaryClient`,
  `spectatorFollowClient`, `spectatorClientOrder`,
  `spectatorClientCount`, `spectatorTargetUpdateTime`,
  `spectatorTrackedClient`, `spectatorCameraLocked`,
  `trackedPlayerClientNum`, `trackedPlayerExpireTime`, and
  `trackedPlayerPriority`.
- `cg_servercmds.c` owns `clientKeyMask[]` through the key-status mirrors.
- `cg_event.c` owns `killerName`, `obituaries[]`, `obituaryIndex`, and the
  scoreboard timer triplet.

### Feedback, Queues, And Combat Tail

- `CG_CenterPrint` and `CG_DrawCenterString` own the centerprint block.
- `CG_CheckAmmo`, `CG_DamageFeedback`, `CG_CheckLocalSounds`,
  `CG_DrawCrosshair`, `CG_ScanForCrosshairEntity`, `CG_DrawReward`,
  `CG_AddBufferedSound`, and `CG_PlayBufferedVoiceChats` own most of the HUD
  feedback and queue fields.
- Retail HLIL shows the screen-damage tail feeding view kick plus
  `cg_screen.c::CG_DamageBlendBlob`; the current tree now keeps
  `CG_DrawScreenDamage` empty because there is no second retail 2D damage
  overlay consumer in the committed corpus.
- The packed-color branch recorded in retail damage feedback uses the self
  color as full RGBA, but replaces the alpha byte for default or team damage
  from `screenDamageAlpha` or `screenDamageAlphaTeam` before the blob draw
  consumes it.
- Retail graphics registration only loads `viewBloodBlend` when the
  `dlc_gibs/bloodspray1.tga` asset probe succeeds, so the blob path keys off
  the registered shader handle instead of a live blood cvar.
- The committed retail cgame corpus exposes `cg_blood` but no `cg_gibs`
  registration or consumer string, so the reconstructed gib fallback paths
  should key off blood plus DLC-gib availability rather than a separate gib
  toggle.
- `CG_ParseWarmup` and the warmup draw paths own `warmup` and `warmupCount`.
- `CG_DrawPlayerHead` owns the head wobble interpolation fields
  (`headStart*`, `headEnd*`, `headEndTime`).
- Local rail/lightning prediction in `cg_weapons.c` owns the
  `predictedLocal*` cache.
- The test-model console commands in `cg_view.c` own `testModelEntity`,
  `testModelName`, and `testGun`.

## Field-Strength Notes

### Strongly Owned Fields

The highest-confidence live fields are:

- the snapshot and prediction spine:
  `snap`, `nextSnap`, `activeSnapshots`, `frameInterpolation`,
  `thisFrameTeleport`, `nextFrameTeleport`, `predictedPlayerState`,
  `predictedPlayerEntity`, `validPPS`, `predictedErrorTime`,
  `predictedError`, `eventSequence`, `predictableEvents`
- view and zoom state:
  `refdef`, `refdefViewAngles`, `viewFilter`, `zoomed`, `zoomTime`,
  `zoomSensitivity`, `renderingThirdPerson`
- scoreboard and spectator state:
  `scoresRequestTime`, `numScores`, `selectedScore`, `teamScores`, `scores`,
  `scoreStats`, `teamScoreStats`, `showScores`, `scoreBoardShowing`,
  `killerName`, `obituaries`, the tracked spectator fields, and `skulltrails`
- combat feedback and queues:
  `lowAmmoWarning`, `crosshairClientNum`, `crosshairClientTime`,
  `crosshairColor`, `crosshairHitColor`, `rewardStack`, `rewardTime`,
  `rewardCount`, `rewardShader`, `rewardSound`, `soundBuffer*`,
  `voiceChatTime`, `voiceChatBufferIn`, `voiceChatBufferOut`, `warmup`,
  `itemPickupBlendTime`, `damageTime`, `damageX`, `damageY`, `damageValue`,
  `screenDamageColor`, `screenDamageAlpha`, `v_dmg_*`, `kick_angles`,
  `kick_origin`, `bobfracsin`, `bobcycle`, `xyspeed`, and the
  `predictedLocal*` hitscan cache

### Weaker Or Carry-Over Fields

- `spectatorTime`, `spectatorPaintX`, `spectatorPaintX2`, `spectatorOffset`,
  and `spectatorPaintLen` are still present in the retail-compatible layout,
  but the current tree no longer uses the old GPL scrolling spectator ticker
  that consumed them.
- `powerupActive` and `powerupTime` are still written by the major powerup
  event path, but the legacy HUD pulse consumer is gone from the current tree.
- `headYaw` remains in the layout, but the current HUD head wobble uses the
  start/end yaw fields instead.
- `crosshairHitStyle`, `lowAmmoWarningPercentile`, and
  `weaponBarGrenadeColor` remain cached customization fields whose read-side
  consumers are weak or absent in the current tree.
- `screenDamageSelfColor`, `screenDamageTeamColor`, and
  `screenDamageAlphaTeam` are now consumed by `cg_screen.c` when the live
  attacker context identifies self-damage or friendly-fire damage, which lines
  up with the retail cvar surface recovered from the committed `cgame` and UI
  HLIL.

## Open Questions

1. Recheck the weak cached customization fields against the remaining retail
   HLIL draw-side code to see whether any current-tree consumers are still
   missing for `crosshairHitStyle` and the grenade bar color.
2. Recover the exact retail function boundaries for the spectator panel helpers
   around the `cg_trackPlayer` / tracked-client flow so the struct note can
   cite stabilized addresses in addition to the current source-side anchors.
