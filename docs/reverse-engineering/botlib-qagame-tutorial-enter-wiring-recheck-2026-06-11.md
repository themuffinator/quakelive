# Botlib Qagame Tutorial Enter Wiring Recheck - 2026-06-11

## Scope

This pass rechecks the small qagame tutorial enter helpers in the mapped
`ai_dmnet.c` retail tail:

- `0x1000F880` / `AIEnter_Lead_Teammate`
- `0x10011900` / `AIEnter_Torment_Human`
- `0x10012430` / `AIEnter_Lead_Teammate_FragBait`

The owning retail binary is `qagamex86.dll`. Binary Ninja HLIL is the canonical
control-flow source; the Ghidra `functions.csv` and decompile hints are the
companion evidence.

## Evidence

- Binary Ninja HLIL pins `AIEnter_Lead_Teammate` setting `ltg_time` to
  `FloatTime()+99999`, assigning LTG value `0x12`, installing
  `AINode_Lead_Teammate`, applying tutorial bot-state bits, resolving the
  local client, and recording the `lead teammate` node label.
- Binary Ninja HLIL pins `AIEnter_Torment_Human` setting `ltg_time` to
  `FloatTime()+99999`, assigning LTG value `0x13`, installing
  `AINode_Torment_Human`, clearing the cached enemy, clearing the `+0x2498`
  torment retry/stall counter, applying the training entity flag bit, and
  recording the `torment human` node label.
- Binary Ninja HLIL pins `AIEnter_Lead_Teammate_FragBait` clearing the late
  tutorial scratch fields, setting `ltg_time` to `FloatTime()+99999`, setting
  the `+0x2444` timer to `FloatTime()+10`, assigning LTG value `0x14`,
  installing `AINode_Lead_Teammate_FragBait`, reapplying tutorial bot-state
  bits, and recording the `lead teammate` node label.
- `ai_main.c::BotDebugLTGTypeName` already names the same raw values as
  following, training, touring, tormenting, and target.

## Reconstruction

- Added source constants `LTG_FOLLOWING`, `LTG_TRAINING`, `LTG_TOURING`,
  `LTG_TORMENT_HUMAN`, and `LTG_TARGET` in `ai_main.h`.
- Replaced the raw `0x10..0x14` cases in `BotDebugLTGTypeName` with those
  named constants.
- Strengthened `tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py`
  around the enter-helper LTG writes, adjacent node-pointer writes, cached
  enemy reset, scratch counter/timer resets, and tutorial bot-state flag write.
- Updated the qagame symbol map comments for the three enter helpers so their
  mapped-only status and remaining scratch-tail dependency are explicit.

## Open Boundary

The small enter helpers are not added as standalone compiled functions yet.
`AIEnter_Torment_Human` must install `AINode_Torment_Human`, and adding that
entry without the real node body would either fail to link or create a
misleading fallback. The next source-coded step should be a dedicated layout
pass for the `0x241c..0x2500` tutorial tail, then reconstruction of
`AINode_Torment_Human` or the lead/fragbait nodes as complete state machines.

## Confidence

High for the LTG values, node labels, adjacent node assignments, cached enemy
reset, torment retry/stall counter reset, fragbait timer seed, and tutorial
bot-state flag application. Medium for the descriptive meaning of individual
scratch-tail fields until the full retail `bot_state_t` tail layout is
promoted into source.

## Validation

```text
python -m pytest tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py -q --tb=short
3 passed in 0.14s

python -m pytest tests -k botlib -q --tb=short
205 passed, 1864 deselected in 4.12s
```
