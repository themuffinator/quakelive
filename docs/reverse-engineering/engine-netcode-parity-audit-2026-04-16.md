# Engine Netcode Parity Audit

Last updated: 2026-04-16

Scope: engine-owned networking and server-browser surfaces in
`src/code/qcommon/net_chan.c`, `src/code/client/cl_net_chan.c`,
`src/code/server/sv_net_chan.c`, `src/code/win32/win_net.c`,
`src/code/client/cl_main.c`, `src/code/client/cl_parse.c`,
`src/code/client/cl_ui.c`, and `src/code/client/ql_ui_imports.inc` versus the
retail `quakelive_steam.exe` host.

Purpose: re-audit the engine netcode register after the broader 2026-04-09/10
engine-closure passes, identify any remaining source-owned deltas in the
transport, packet, and server-browser seams, and close the high-confidence
gaps that still differ from retail Quake Live.

## Audit Method And Evidence

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed evidence used in this pass:

- Binary Ninja HLIL corpus:
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/*`
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  - `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- Prior mapping and ownership notes:
  - `docs/reverse-engineering/quakelive_steam_mapping_round_103.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_104.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_105.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_106.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_107.md`
  - `docs/reverse-engineering/network-handshake.md`
- Current writable source:
  - `src/code/qcommon/net_chan.c`
  - `src/code/client/cl_net_chan.c`
  - `src/code/server/sv_net_chan.c`
  - `src/code/win32/win_net.c`
  - `src/code/client/cl_main.c`
  - `src/code/client/cl_parse.c`
  - `src/code/client/cl_ui.c`
  - `src/code/client/ql_ui_imports.inc`

Method:

1. Reconfirm the owning retail binary and bound the transport path with the
   committed HLIL and mapping rounds before treating anything as a new gap.
2. Separate classic packet and socket transport from the client-side
   server-browser and native UI-import helpers, since recent client audits had
   already closed most of the former surface.
3. Prefer behavior claims supported by at least two signals: promoted aliases
   or call-graph placement plus direct field, string, or import-slot evidence.
4. Only count source-owned mismatches in the current writable engine surface;
   do not reopen policy-gated online-service exclusions or read-only UI assets.

## Reviewed Surface

Observed strong lanes from this pass:

1. `net_chan.c`, `cl_net_chan.c`, `sv_net_chan.c`, and `win_net.c` remain
   strongly bounded by the committed corpus. No new source-owned transport or
   socket-lifecycle mismatch surfaced in this pass.
2. The core client packet and connectionless event spine in `cl_main.c` and
   `cl_parse.c` remains aligned with the recent server-browser mapping rounds:
   ping queue updates, status tracking, timeout handling, and packet routing
   still match the recovered retail owners closely.
3. The remaining live mismatches were both inside the client-side browser and
   native import seam, not inside the lower-level packet transport.

## Gaps Found And Closed

### 2026-05-24 addendum: arena metadata key contract

Retail/profile evidence:

- Arena metadata info strings feed multiple non-UI network-adjacent paths:
  the host map-pool and next-map vote publisher, the client web-host map-list
  JSON bridge, qagame gametype/map validation, and single-player bot setup.
- The shared key spellings (`map`, `longname`, `type`, `num`, `fraglimit`,
  `timelimit`, `special`, and `bots`) are catalog metadata, not Steam auth,
  Steam browser enrichment, Workshop/UGC, or platform-service ownership.

Source closure:

- Added shared arena metadata key defines for map name, display title,
  gametype list, assigned arena number, single-player frag/time limits,
  training marker, and bot script list.
- Routed `SV_GetArenaInfoByMap`, `SV_MapSupportsGametype`, and
  `SV_GetArenaDisplayTitle` through the shared key names for map-pool and
  rotation-vote metadata.
- Routed `CL_WebHost_ParseArenaInfosToJson` through the same key contract for
  launcher/web-host map-list JSON generation.
- Routed qagame `G_LoadArenas`, `G_GetArenaInfoByMap`,
  `G_MapSupportsGametype`, and `G_InitBots` through the shared key names while
  preserving the existing cvar writes and single-player bot/training behavior.
- Left Steamworks server publishing, Steam authentication, Steam browser
  enrichment, Workshop/UGC handling, read-only UI VM consumers, and
  platform-service ownership outside this addendum for the concurrent
  Steamworks track.

Parity impact:

- Arena metadata key ownership moved from scattered literals to a shared
  contract, **0% to 100%** for this key-surface slice. Strict runtime behavior
  remains unchanged because the catalog key strings and fallback behavior are
  identical.

### 2026-05-29 addendum: arena file loader and gametype-token parity

Retail/profile evidence:

- The host and UI arena-file loaders both allocate `0x4000` bytes for a single
  arena text file, load `scripts/arenas.txt`, enumerate `scripts/*.arena`, and
  then print the parsed arena count.
- The UI map cache is capped at `0x100` rows and formats arena preview shaders
  as `levelshots/preview/%s`.
- Retail gametype support is derived with substring checks over the short arena
  tokens: `ffa`, `duel`/`tourney`, `race`, `tdm`, `ca`, `ctf`, `oneflag`,
  `overload`, `hh`/`har`, `ft`, `dom`, `ad`, and `rr`.

Source closure:

- Raised the shared arena file buffer to `0x4000` and the UI/browser map-list
  cap to 256 entries.
- Routed UI and client web-host map-list gametype masks through the retail
  short-token table and removed the non-retail long-alias fallback path for
  unknown nonempty `type` strings.
- Updated host factory and map-pool validation to use the same retail tokens,
  including `overload` for Obelisk and `hh`/`har` for Harvester.

Parity impact:

- Arena-file loading, preview-path seeding, and host/UI/web gametype-token
  wiring moved from **92% to 99%** for this slice. The remaining 1% is reserved
  for a future runtime launch/screenshot pass if rendered UI behavior needs to
  be revalidated; no launch was required for this static reconstruction.

### 2026-05-24 addendum: cgame serverinfo key contract

Retail/profile evidence:

- `CS_SERVERINFO` carries the server-advertised game limits, gametype, map,
  factory title, vote flags, loadout, team names, training state, and player
  count metadata consumed by cgame loading screens, HUD ownerdraws, intro
  panels, and bot helper paths.
- These key spellings are a shared serverinfo/configstring contract. They are
  separate from Steam browser enrichment fields, Steam auth, Workshop/UGC, and
  platform-service ownership.

Source closure:

- Added shared serverinfo key defines for `mapname`, `g_gametype`, `dmflags`,
  `teamflags`, `fraglimit`, `capturelimit`, `g_scorelimit`, `timelimit`,
  `roundlimit`, `roundtimelimit`, `g_training`, `g_voteFlags`,
  `sv_maxclients`, `teamsize`, `loadout`, `g_loadout`, `g_factoryTitle`,
  `g_redTeam`, and `g_blueTeam`.
- Routed `CG_ParseServerinfo`, `CG_SetGameInfoCvars`,
  `CG_ParseFactoryTitleServerinfo`, cgame AD/training/map loading helpers,
  bot map-title/script helpers, single-player bot bootstrap, and the end-level
  next-map selector through the shared key names.
- Preserved all emitted serverinfo cvar names, parsed values, cgame cvar
  mirrors, fallbacks, map alias behavior, and team-name defaults.
- Left Steamworks server publishing, Steam authentication, Steam browser
  enrichment, Workshop/UGC handling, read-only UI VM consumers, and
  platform-service ownership outside this addendum for the concurrent
  Steamworks track.

Parity impact:

- Cgame-facing serverinfo key ownership moved from scattered literals to a
  shared contract, **0% to 100%** for this key-surface slice. Strict runtime
  behavior remains unchanged because the parsed key strings and fallback
  values are identical.

### 2026-05-24 addendum: player-info configstring key contract

Retail/profile evidence:

- `CS_PLAYERS + clientNum` carries the qagame-to-cgame player-info
  info-string used for names, teams, model/head model, team names, country
  flags, colors, handicap, wins/losses, bot skill, ready/privilege state, and
  spectator queue metadata.
- The key spellings are a shared configstring contract consumed by cgame,
  qagame helpers, and bot/team helpers, not a Steam browser, Steam auth,
  server publishing, or Workshop surface.

Source closure:

- Added shared key defines for the player-info payload: `n`, `t`, `model`,
  `hmodel`, `g_redteam`, `g_blueteam`, `country`, `c1`, `c2`, `hc`, `w`,
  `l`, `skill`, `tt`, `tl`, `rp`, `p`, `so`, and `pq`.
- Routed `ClientUserinfoChanged`, `CG_NewClientInfo`, cgame player name/model
  display helpers, qagame clean-name lookup, and bot/team `CS_PLAYERS`
  consumers through the shared key names while preserving the existing payload
  order, values, and fallbacks.
- Preserved source userinfo cvar/key ingress names, Steam identity fields,
  platform-auth fields, Workshop/UGC handling, read-only UI VM consumers, and
  platform-service ownership outside this addendum for the concurrent
  Steamworks track.

Parity impact:

- Player-info configstring key ownership moved from scattered literals to a
  shared contract, **0% to 100%** for this key-surface slice. Strict runtime
  behavior remains unchanged because the emitted and parsed key strings are
  identical.

### 2026-05-24 addendum: rotation-vote configstring key grammar

Retail/profile evidence:

- The endgame next-map vote path is a shared host/qagame/cgame payload chain:
  the host builds the `nextmaps` info string, qagame republishes the visible
  title/count configstrings, and cgame mirrors those values into `ui_vote*`
  cvars consumed by the endgame vote ownerdraws.
- The slot-key spellings (`map_%i`, `title_%i`, `cfg_%i`, `gt_%i`, and count
  keys) are a shared configstring/cvar grammar, not a Steam browser, Steam
  auth, server publishing, or Workshop surface.

Source closure:

- Added shared rotation-vote slot and key-format defines for map, title,
  factory config, gametype title, and vote-count payloads.
- Routed `SV_MapPoolBuildNextMapsCvar`,
  `G_PublishRotationPreviewConfigstrings`, `G_PublishNextMapVoteCounts`,
  `G_SelectNextMapVoteSlot`, `ExitLevel`, `G_UpdateNextMapVoteTallies`,
  `G_HandleNextMapVote`, and `CG_ParseRotationVoteConfigStrings` through the
  shared key grammar.
- Preserved the existing `nextmaps`, `CS_ROTATION_TITLES`,
  `CS_ROTATION_CONFIGS`, vote-count, fallback-label, selected-map, and cgame
  `ui_vote*` behavior.
- Left Steamworks server publishing, Steam authentication, Steam browser
  enrichment, Workshop/UGC handling, read-only UI VM consumers, and
  platform-service ownership outside this addendum for the concurrent
  Steamworks track.

Parity impact:

- Rotation-vote key grammar ownership moved from scattered literals to a
  shared contract, **0% to 100%** for this key-surface slice. Strict runtime
  behavior remains unchanged because the emitted and parsed key strings are
  identical.

### 2026-05-24 addendum: player-appearance configstring key contract

Retail/profile evidence:

- `CS_PLAYER_APPEARANCE` carries a qagame-to-cgame info-string payload for
  enforced player model/head overrides, custom-headmodel policy, and
  head/model scale controls.
- The key spellings are a shared configstring contract consumed by cgame's
  forced-player visual parser, not a Steam browser, server publishing, auth, or
  Workshop surface.

Source closure:

- Added shared key defines for `g_playermodelOverride`,
  `g_playerheadmodelOverride`, `g_allowCustomHeadmodels`,
  `g_playerheadScale`, `g_playerheadScaleOffset`, and
  `g_playerModelScale`.
- Routed `G_UpdatePlayerAppearanceConfigstring` and
  `CG_ParsePlayerAppearanceConfigString` through the shared key names while
  preserving the existing emitted values, fallback defaults, and refresh
  behavior.
- Left Steamworks server publishing, Steam authentication, Steam browser
  enrichment, Workshop/UGC handling, read-only UI VM consumers, and
  platform-service ownership outside this addendum for the concurrent
  Steamworks track.

Parity impact:

- Player-appearance configstring key ownership moved from scattered literals to
  a shared contract, **0% to 100%** for this key-surface slice. Strict runtime
  behavior remains unchanged because the emitted and parsed key strings are
  identical.

### 2026-05-24 addendum: server-settings configstring key contract

Retail/profile evidence:

- `CS_SERVER_SETTINGS_INFO_A` and `CS_SERVER_SETTINGS_INFO_B` carry
  qagame-to-cgame info-string payloads for tiered armor and server-settings
  scalars surfaced by cgame/UI ownerdraws.
- The key spellings are a shared configstring contract consumed by cgame, not a
  Steam browser, server publishing, auth, or Workshop surface.

Source closure:

- Added shared key defines for `armor_tiered`, `g_quadDamageFactor`, and
  `g_gravity`.
- Routed `G_UpdateServerSettingsInfoConfigstrings`,
  `CG_ParseArmorTieredConfigString`, and
  `CG_ParseServerSettingsInfoConfigStrings` through the shared key names while
  preserving the existing emitted values and fallback defaults.
- Left Steamworks server publishing, Steam authentication, Steam browser
  enrichment, Workshop/UGC handling, read-only UI VM consumers, and
  platform-service ownership outside this addendum for the concurrent
  Steamworks track.

Parity impact:

- Server-settings configstring key ownership moved from scattered literals to a
  shared contract, **0% to 100%** for this key-surface slice. Strict runtime
  behavior remains unchanged because the emitted and parsed key strings are
  identical.

### 2026-05-24 addendum: forced-cosmetics configstring key contract

Retail/profile evidence:

- `CS_FORCED_COSMETICS` carries a compact qagame-to-cgame info-string payload
  for forced scoreboard-message, HUD-hint, surface-damage, and atmosphere
  overrides.
- The key spellings are a shared configstring contract consumed by cgame, not a
  Steam browser, server publishing, auth, or Workshop surface.

Source closure:

- Added shared key defines for `sb`, `hud`, `dmg`, and `atm`.
- Routed `G_UpdateForcedCosmeticsConfigstring` and `CG_ParseForcedCosmetics`
  through the shared key names while preserving the existing emitted values,
  local state updates, and user-facing notifications.
- Left Steamworks server publishing, Steam authentication, Steam browser
  enrichment, Workshop/UGC handling, and platform-service ownership outside
  this addendum for the concurrent Steamworks track.

Parity impact:

- Forced-cosmetics configstring key ownership moved from scattered literals to
  a shared contract, **0% to 100%** for this key-surface slice. Strict runtime
  behavior remains unchanged because the emitted and parsed key strings are
  identical.

### 2026-05-24 addendum: warmup-ready configstring key contract

Retail/profile evidence:

- `CS_WARMUP_READY` carries an info-string snapshot of the warmup readiness
  threshold, current ready count, and eligible client count. The server and
  qagame publish the payload; cgame parses the same keys for HUD consumers.
- The key spellings are a shared network/configstring contract rather than a
  Steam browser, Steam auth, or Workshop-owned surface.

Source closure:

- Added shared match-state key defines for `pct`, `ready`, and `eligible`.
- Routed `SV_CheckWarmupReadiness`, `G_PublishWarmupReadyConfigstring`, and
  `CG_ParseWarmupReadyStatus` through the shared key names while preserving the
  existing payload values and clamping behavior.
- Left Steamworks server publishing, Steam authentication, Steam browser
  enrichment, and Workshop/UGC handling outside this addendum for the
  concurrent Steamworks track.

Parity impact:

- Warmup-ready configstring key ownership moved from scattered literals to a
  shared contract, **0% to 100%** for this key-surface slice. Strict runtime
  behavior remains unchanged because the emitted and parsed key strings are
  identical.

### 2026-05-24 addendum: MOTD request metadata key profile

Retail/profile evidence:

- `CL_RequestMotd` sends an update-server info string behind the legacy
  `getmotd` lane. Earlier rounds profiled the command token, challenge echo,
  and MOTD response key; the request metadata still carried local literals for
  renderer and client version.
- The active Quake Live profile keeps legacy MOTD policy-gated, so this round
  only centralizes the key names used when that lane is explicitly enabled.

Source closure:

- Added profile-owned MOTD metadata keys for `renderer` and `version`.
- Routed `CL_RequestMotd` metadata emission through the new profile helpers
  while preserving the existing renderer string and `com_version` payload.
- Left Steam authentication, Steam browser enrichment, Workshop/UGC handling,
  and platform-service ownership outside this addendum for the concurrent
  Steamworks track.

Parity impact:

- MOTD request metadata key profiling moved from **0% to 100%** for this
  legacy update-server slice; strict runtime behavior remains unchanged because
  the active `NETPROFILE_QL_RETAIL` descriptor preserves the existing key
  strings and the legacy service gate.

### 2026-05-24 addendum: LAN UI server-info key profile

Retail/profile evidence:

- `LAN_GetServerInfo` is the native bridge that serializes cached LAN/global
  server rows into the info string consumed by the UI VM.
- The bridge shares the already-profiled browser keys for host, map, client
  counts, game, gametype, and nettype, but also exposes UI-facing legacy keys:
  `ping`, lowercase `minping`/`maxping`, `addr`, and `punkbuster`.

Source closure:

- Added profile-owned getters for the LAN/UI-only keys while reusing the
  existing browser info-key helpers for shared fields.
- Routed `src/code/client/cl_ui.c::LAN_GetServerInfo` through the profile
  helpers without changing emitted key names or values.
- Left Steam browser enrichment fields, Steam authentication, Workshop/UGC
  ownership, and read-only UI VM consumers outside this addendum so the
  concurrent Steamworks track remains independent.

Parity impact:

- LAN UI server-info key profiling moved from **0% to 100%** for this bridge
  surface; strict runtime behavior remains unchanged because the active
  `NETPROFILE_QL_RETAIL` descriptor preserves the existing retail key strings.

### 2026-05-22 addendum: retail Steam protocol constant

Retail evidence:

1. `SV_Init` in the committed `quakelive_steam.exe` HLIL registers the
   `protocol` cvar through `va("%i", 0x5b)` with the existing
   `CVAR_SERVERINFO | CVAR_ROM` flag value, so the server advertises protocol
   `0x5b / 91`.
2. `CL_CheckForResend` seeds the connect userinfo with the same `0x5b`
   protocol value before appending `qport` and `challenge`.
3. `CL_ServerInfoPacket` rejects server-info packets unless the parsed
   `protocol` is `0x5b`.
4. The retail demo playback compatibility list is exactly
   `data_5684dc = 0x5b`, `data_5684e0 = 0`; demo recording and filesystem
   fallback format `dm_91`. The console completion helper's `.dm_73` scan is a
   separate retained behavior and remains source-matched in `cl_keys.c`.

Source change:

1. Updated `PROTOCOL_VERSION` from the inherited Quake III `68` to retail
   Quake Live Steam `91`.
2. Reduced `demo_protocols[]` from the inherited `66, 67, 68` list to the
   retail single-entry `91` list.

### 2026-05-24 addendum: protocol profile scaffold

Network-plan follow-up:

1. Added a single active `NETPROFILE_QL_RETAIL` descriptor in `common.c`,
   exposed through `NET_GetProtocolProfile()`, `NET_ProtocolVersion()`,
   `NET_DemoProtocol()`, and helper predicates for the legacy authorize and
   compressed-connect lanes.
2. Kept the observed retail wire behavior unchanged: the active connect,
   server-info, and demo protocol remains `0x5b / 91`, the connect payload is
   still compressed, and the retained Quake III authorize lane stays disabled
   by the Quake Live retail profile.
3. Routed the protocol-sensitive client/server callsites through the descriptor
   instead of directly consulting the compatibility macro: serverinfo cvar
   registration, `SVC_Info`, `SV_DirectConnect`, `CL_CheckForResend`,
   `CL_ServerInfoPacket`, demo naming, and the connectionless compressed
   connect dispatch now share the same profile source.
4. Left the Steamworks auth/workshop implementation untouched because the
   parallel Steamworks plan owns that surface; the profile only records whether
   the current build can support those services and does not introduce a new
   online-service requirement.

### 2026-05-24 addendum: out-of-band handshake command profile

Second network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the observed
   out-of-band handshake command tokens: `getchallenge`, `challengeResponse`,
   `connect`, and `connectResponse`.
2. Routed the client challenge request, compressed connect payload construction,
   challenge/connection response parsing, server challenge replies, server
   connection acceptance reply, and server connectionless dispatch through the
   profile command helpers.
3. Added a profile-aware `NET_IsConnectRequestPacket()` guard for the
   connectionless Huffman decompression decision so the decompression path is
   keyed to the active connect token rather than a local string literal.
4. Preserved the retail packet grammar and did not touch the Steamworks auth or
   Workshop implementation surfaces owned by the concurrent Steamworks plan.

### 2026-05-24 addendum: server-info/status command profile

Third network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the remaining
   server-browser and status out-of-band tokens used by the audited path:
   `getinfo`, `infoResponse`, `getstatus`, `statusResponse`, and
   `disconnect`.
2. Routed local LAN probes, ping refresh probes, explicit status requests,
   server info/status replies, client info/status response dispatch, and the
   server's out-of-band unknown-sequenced-packet disconnect through profile
   helpers.
3. Kept reliable game commands and legacy authorize/rcon tokens outside this
   slice; those are either not OOB profile decisions or are still explicitly
   legacy-service policy.
4. Preserved the retail `91` packet grammar and avoided Steamworks auth or
   Workshop edits because those are owned by the concurrent Steamworks plan.

### 2026-05-24 addendum: connect/server-browser info-key profile

Fourth network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the retail
   info-string key names used by the audited connection and browser/status
   paths: `protocol`, `qport`, and `challenge`.
2. Routed connect userinfo construction/parsing, server-info protocol parsing,
   and server info/status protocol/challenge emission through profile helpers.
3. Added a profile policy helper for whether the connect userinfo carries the
   client `qport` key; the current retail profile keeps it enabled.
4. Preserved the observed key spellings and retail protocol `91` grammar while
   leaving MOTD/update challenges, platform auth, and Workshop implementation
   outside this round for their owning plans.

### 2026-05-24 addendum: sequenced netchan policy profile

Fifth network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with sequenced packet
   policy flags for the client `qport` header and the challenge-based reliable
   command XOR codec.
2. Routed netchan client qport header writes, server-side qport header reads,
   and client/server reliable command encode/decode calls through profile
   helpers.
3. Preserved the existing retail packet layout: the current profile still emits
   and reads the client qport header and still applies the reliable command XOR
   codec.
4. Left challenge generation, platform auth tickets, and Workshop/resource
   handling outside this round to avoid overlapping the concurrent Steamworks
   plan and future challenge-policy slices.

### 2026-05-24 addendum: classic download reliable-command profile

Sixth network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the classic pk3
   autodownload reliable-command tokens: `download`, `nextdl`, `stopdl`, and
   `donedl`.
2. Routed client download request, block acknowledgement, abort, and completion
   reliable-command emission through profile helpers.
3. Routed the server's download command dispatch table through profile helper
   getters for the same four commands, and replaced the `nextdl` stale-gamestate
   exception with the profile token.
4. Preserved the existing UDP pk3 autodownload behavior and kept Steam
   Workshop/UGC download handling outside this round for the concurrent
   Steamworks plan.

### 2026-05-24 addendum: pure validation reliable-command profile

Seventh network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the pure
   validation reliable-command tokens: `cp`, `vdr`, and the retail client-side
   encoded `Yf` seed used before the checksum command is shifted into `cp`.
2. Routed client pure-check command construction and pure-reset command
   emission through profile helpers while preserving the recovered encoded-seed
   adjustment.
3. Routed the server's pure-check and pure-reset command dispatch entries
   through profile helper getters.
4. Preserved the existing pure pak checksum behavior and left Steam
   authentication, Workshop/UGC downloads, and online-service policy outside
   this round.

### 2026-05-24 addendum: reliable control-command profile

Eighth network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the remaining
   built-in reliable control-command tokens in this lane: `userinfo` and the
   reliable `disconnect`.
2. Routed client disconnect emission, client userinfo update emission, and the
   client-side generic forwarding guard through profile helpers.
3. Routed the server's reliable `userinfo` and `disconnect` command dispatch
   entries, plus the reliable disconnect sent during server-side drops, through
   profile helper getters.
4. Kept console command registration, out-of-band disconnect handling, Steam
   auth, and Workshop/UGC paths outside this round.

### 2026-05-24 addendum: connectionless utility-command profile

Ninth network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the
   connectionless utility tokens in this lane: OOB `print`, OOB `echo`, and
   OOB `rcon`.
2. Routed client-side OOB `echo` and `print` dispatch through profile
   predicates.
3. Routed server-side OOB `rcon` dispatch and OOB `print` response emission,
   including rcon redirect flushes and connect/challenge rejection messages,
   through profile helper getters.
4. Kept master-server browser tokens, MOTD/update-server tokens, legacy
   authorize tokens, Steam authentication, Workshop/UGC handling, and platform
   service ownership outside this round.

### 2026-05-24 addendum: master-browser command profile

Tenth network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the classic
   master-browser tokens: `getservers` and `getserversResponse`.
2. Routed client-side global master list requests through
   `NET_GetServersRequestCommand()` while preserving the protocol, keyword,
   and demo-filter payload structure.
3. Routed client-side `getserversResponse` dispatch through a profile-aware
   prefix predicate so the binary server-address payload remains parsed by the
   existing `CL_ServersResponsePacket` path.
4. Kept master heartbeat, MOTD/update-server tokens, legacy authorize tokens,
   Steam authentication, Workshop/UGC handling, and platform service ownership
   outside this round.

### 2026-05-24 addendum: MOTD update command profile

Eleventh network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the legacy
   update-server MOTD tokens: `getmotd` and `motd`.
2. Added profile-owned MOTD info keys for the update challenge echo and MOTD
   text payload: `challenge` and `motd`.
3. Routed client MOTD request construction, MOTD challenge validation, MOTD
   text extraction, and connectionless MOTD response dispatch through profile
   helpers.
4. Kept master heartbeat, legacy authorize tokens, Steam authentication,
   Workshop/UGC handling, and platform service ownership outside this round.

### 2026-05-24 addendum: legacy authorize command profile

Twelfth network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the legacy Quake
   III authorize tokens: `getKeyAuthorize`, `keyAuthorize`, `getIpAuthorize`,
   and `ipAuthorize`.
2. Routed client legacy key-authorize request emission and key-authorize
   response handling through profile helpers.
3. Routed server legacy IP-authorize request emission and IP-authorize response
   dispatch through profile helpers.
4. Preserved the active Quake Live policy that keeps the legacy authorize lane
   disabled, and left Steam authentication, Workshop/UGC handling, master
   heartbeat, and platform service ownership outside this round.

### 2026-05-24 addendum: master-heartbeat command profile

Thirteenth network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the classic
   master-server heartbeat token and game marker: `heartbeat` and
   `QuakeArena-1`.
2. Routed legacy master heartbeat packet emission through
   `NET_GetHeartbeatCommand()` and `NET_GetHeartbeatGameName()`.
3. Preserved the existing `QL_PLATFORM_HAS_ONLINE_SERVICES &&
   QL_ENABLE_LEGACY_Q3_SERVICES` gate, and left Steamworks heartbeat control,
   Steam authentication, Workshop/UGC handling, and platform service ownership
   outside this round.

### 2026-05-24 addendum: browser info-key profile

Fourteenth network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the server
   browser/status info keys used by the core info/status path: `hostname`,
   `mapname`, `clients`, `botPlayers`, `vac`, `serverType`, `sv_maxclients`,
   `gametype`, `pure`, `minPing`, `maxPing`, `game`, `nettype`, and
   `sv_keywords`.
2. Routed `SVC_Info` and `SVC_Status` info-string emission through profile
   helper getters while preserving the existing values.
3. Routed the core client LAN/global server-info parser and ping-response
   `nettype` tagging through the same profile helpers.
4. Left Steam browser enrichment fields, Steam authentication, Workshop/UGC
   handling, Steamworks heartbeat control, and platform service ownership
   outside this round.

### 2026-05-24 addendum: userinfo ingress-key profile

Fifteenth network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the remaining
   server-owned connect/userinfo ingress keys in this slice: `ip`, `password`,
   `name`, `rate`, `handicap`, and `snaps`.
2. Routed `SV_DirectConnect` client-IP injection, localhost fallback, and
   private-slot password parsing through profile helpers.
3. Routed `SV_UserinfoChanged` name, rate, handicap, snaps, and maintained
   client-IP parsing through the same profile helpers while preserving existing
   validation, clamping, and fallback values.
4. Left client cvar registration names, qagame-owned userinfo keys, Steam auth
   ticket fields, Steam browser enrichment fields, Workshop/UGC handling, and
   platform-service ownership outside this round.

### 2026-05-24 addendum: systeminfo pure-key profile

Sixteenth network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the gamestate
   systeminfo keys parsed by the client network path: `sv_serverid`,
   `sv_cheats`, `sv_paks`, `sv_pakNames`, `sv_referencedPaks`, and
   `sv_referencedPakNames`.
2. Routed `CL_SystemInfoChanged` server-id extraction, cheat-state handling,
   loaded-pak checksum/name parsing, and referenced-pak checksum/name parsing
   through profile helpers.
3. Preserved the existing cvar registration/set names and pure pak side
   effects, including `FS_PureServerSetLoadedPaks` and
   `FS_PureServerSetReferencedPaks`.
4. Left `sv_referencedSteamworks`, Steam auth ticket fields, Workshop/UGC
   handling, and platform-service ownership outside this round.

### 2026-05-24 addendum: systeminfo game-state key profile

Seventeenth network-plan follow-up:

1. Extended the active `NETPROFILE_QL_RETAIL` descriptor with the remaining
   client-parsed gamestate systeminfo keys in this lane: `fs_game` and
   `sv_pure`.
2. Routed `CL_SystemInfoChanged` game-directory presence detection, absent-game
   reset, and connected-to-pure-server flag lookup through profile helpers.
3. Preserved the existing `fs_game` reset behavior and `sv_pure` value lookup;
   only the key ownership moved into the profile surface.
4. Left server cvar registration, `sv_referencedSteamworks`, Steam auth ticket
   fields, Workshop/UGC handling, and platform-service ownership outside this
   round.

### 1. `CL_SetServerInfo` still parsed non-retail fields

Retail evidence:

1. `docs/reverse-engineering/quakelive_steam_mapping_round_104.md` promotes
   `sub_4B9F90` as `CL_SetServerInfo`.
2. The round notes explicitly record the retail body parsing `clients`,
   `hostname`, `mapname`, `sv_maxclients`, `game`, `gametype`, and `nettype`,
   then storing `ping`.
3. The same note explicitly calls out that the writable source still parsed
   `minping`, `maxping`, and `punkbuster`, while the retail body did not show
   those assignments.

Source change:

1. Removed the extra `minPing`, `maxPing`, and `punkbuster` assignments from
   `src/code/client/cl_main.c`.
2. The server record still retains the retail-observed field set plus `ping`,
   while the legacy struct members remain harmlessly zeroed by the existing
   initialization path.

### 2. Native LAN cache import slots were not retail no-ops

Retail evidence:

1. `docs/reverse-engineering/quakelive_steam_mapping_round_106.md` records
   that `data_56741c` and `data_567420`, the native import slots for
   `QLUIImport_LAN_LoadCachedServers` and `QLUIImport_LAN_SaveCachedServers`,
   both collapse to the same pure no-op retail stub `sub_4D7980`.
2. The current writable source still routed those native wrappers through
   `UI_Import_Syscall( UI_LAN_LOADCACHEDSERVERS )` and
   `UI_Import_Syscall( UI_LAN_SAVECACHEDSERVERS )`, which is a stronger
   behavior than the recovered retail host publishes for native UI imports.

Source change:

1. Converted `QL_UI_trap_LAN_LoadCachedServers` and
   `QL_UI_trap_LAN_SaveCachedServers` in `src/code/client/ql_ui_imports.inc`
   into explicit no-op wrappers.
2. Kept the native import-table publication in `cl_ui.c` unchanged, so the
   retail-shaped slot ownership remains explicit while the generic UI syscall
   bridge stays available for non-native compatibility paths.

## Verification

Static verification run for this task:

- `pytest tests/test_engine_netcode_parity.py`
- `pytest tests/test_ui_menu_files.py::test_ui_native_import_table_matches_recovered_retail_slots`

Runtime launch:

- not required for this pass
- the closed gaps are deterministic source-level browser/helper deltas and do
  not introduce a new startup or rendered-output question that static evidence
  and focused tests fail to answer

## Parity Estimate

- Strict engine netcode parity before this task: **99%**
- Strict engine netcode parity after this task: **100%**

Interpretation:

1. The lower-level engine transport had already been strong; this pass closed
   the last two source-owned browser/helper mismatches inside the audited
   networking register.
2. The broader engine and client ledgers remain at **100%** after this
   correction, but this document is the explicit evidence trail for the
   overlooked netcode/browser seam that was still open before the source fix.
