# Quake Live Steam Mapping Round 517: Cgame Voice-Chat Sound Queue

## Scope

This round maps and hardens the cgame voice-chat sound queue that feeds local
voice playback through `CHAN_VOICE`. The pass focuses on the retail
`cgamex86.dll` helper band at `0x1004A560..0x1004AC90` and its source-side
counterparts in `cg_servercmds.c`.

## Evidence

Observed retail facts:

- Ghidra `cgamex86/functions.csv` has stable rows for:
  `FUN_1004a560` size `314`, `FUN_1004a6a0` size `156`,
  `FUN_1004a740` size `872`, `FUN_1004aac0` size `250`,
  `FUN_1004abc0` size `97`, `FUN_1004ac30` size `95`, and
  `FUN_1004ac90` size `241`.
- The cgame symbol map already identifies the same helpers as
  `CG_HeadModelVoiceChats`, `CG_GetVoiceChat`,
  `CG_VoiceChatListForClient`, `CG_PlayVoiceChat`,
  `CG_PlayBufferedVoiceChats`, `CG_AddBufferedVoiceChat`, and
  `CG_VoiceChatLocal`.
- Binary Ninja HLIL shows `sub_1004a560` opening/reading voice-chat mapping
  files through cgame file imports and emitting the retail
  `"voice chat file too large"` diagnostic before returning `-1`.
- HLIL for `sub_1004aac0` starts the local sound through import offset `0x9c`
  with channel `3`, validates order commands, opens `"voiceMenu"`, echoes
  voice text through the team-chat/print path when allowed, and clears the
  consumed queue slot's sound handle.
- HLIL for `sub_1004abc0` drains one buffered voice chat when
  `voiceChatTime < cg.time`, wraps the output cursor with modulo `32`, and
  delays the next playback by `1000` milliseconds.
- HLIL for `sub_1004ac30` copies `0x138` bytes into the write slot, wraps the
  input cursor with modulo `32`, and when the write cursor catches the read
  cursor it plays the oldest entry and advances the read cursor with a plain
  increment.

Inferred meaning:

- The current source queue contract is retail-aligned, including the unusual
  overflow behavior where `CG_AddBufferedVoiceChat()` uses
  `cg.voiceChatBufferOut++` after forced playback instead of immediately
  applying the modulo expression used by `CG_PlayBufferedVoiceChats()`.
- The `sub_...` names are stable enough to promote alongside the existing
  `FUN_...` aliases because Ghidra rows, symbol-map names, HLIL callsites, and
  source counterparts all agree.
- The `CG_VoiceChatLocal` message-format body is not rewritten in this round:
  the HLIL evidence is useful for queue handoff and source ownership, but its
  calling convention view is too compressed to justify changing source message
  mode formatting without a deeper dedicated pass.

## Reconstruction

- Promoted the missing cgame `sub_1004a560`, `sub_1004a6a0`,
  `sub_1004a740`, `sub_1004aac0`, `sub_1004abc0`, `sub_1004ac30`, and
  `sub_1004ac90` aliases in `references/analysis/quakelive_symbol_aliases.json`.
- Extended `tests/test_cgame_sound_wiring_parity.py` so the cgame sound helper
  gate verifies both `FUN_...` and `sub_...` aliases plus Ghidra function sizes
  for the voice-chat helper band.
- Added a retail voice-chat queue parity test that pins the Binary Ninja HLIL
  anchors and source behavior for head-model voice lookup, random sound/chat
  selection, voice-list fallback, local voice playback, order prompt wiring,
  queued playback timing, and overflow cursor behavior.
- Left C source unchanged because the reviewed queue/playback implementation
  already matches the observed retail contract.

## Remaining Boundary

A future voice-chat formatting pass can re-open `CG_VoiceChatLocal` with a
more detailed decompiler/HLIL walk if the SAY_ALL/SAY_TEAM/SAY_TELL formatting
split needs to be proven instruction by instruction. This round deliberately
does not infer a source rewrite from the compressed retail call signature.

## Validation

Static checks run:

- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_sound_helper_aliases_and_function_table_match_retail_offsets -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py::test_cgame_voice_chat_sound_queue_matches_retail_ring_contract -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py -q --tb=short`
- `python -m pytest tests\test_cgame_console_surface_parity.py::test_voice_menu_timer_uses_retail_separate_latch -q --tb=short`
- `python -m pytest tests\test_cgame_displaycontext_parity.py::test_cgame_true_useitem_view_vignette_voice_water_and_zoom_cvars_match_retail_table_and_wiring tests\test_cgame_displaycontext_parity.py::test_cgame_use_item_and_voice_indicator_cvars_keep_retail_runtime_wiring -q --tb=short`
- `python -m pytest tests\test_cgame_snapshot_parity.py -q --tb=short`
- `python -m pytest tests\test_client_sound_voice_parity.py -q --tb=short`
- `python -m pytest tests\test_client_sound_playback_parity.py -q --tb=short`
- `python -m pytest tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`

Results: all selected checks passed (`1`, `1`, `8`, `1`, `2`, and
`16` tests for the focused cgame/voice gates, plus `11`, `10`, and `6` tests
for the broader client sound/native cgame suites). No runtime launch is
required for this mapping-only pass.

## Parity Estimate

Focused cgame voice-chat sound queue mapping confidence:
**before 86% -> after 97%**.

Focused cgame voice-chat helper alias coverage:
**before 72% -> after 98%**.

Overall sound-system wiring reconstruction parity:
**92.8% -> 92.9%**.
