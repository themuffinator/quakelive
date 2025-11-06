# Credential Menu Updates

## Overview
- Added a "Credentials" navigation button to the in-game options bar so players can reach the credential management screen without leaving the main menu.
- Credential UI now exposes a credential type selector (Legacy CD Key, Steam Ticket, Standalone Token) and automatically disables manual entry when a platform-managed credential is detected.
- Updated user-facing strings to replace "CD Key" terminology with the broader "Credential" nomenclature across dialogs and status prompts.

## Interaction Notes
- Selecting **Legacy CD Key** unlocks the manual entry field with validation that enforces 16 permitted characters.
- Selecting **Steam Ticket** or **Standalone Token** hides the manual input when an auto-provisioned token exists, surfacing guidance text explaining that the linked platform refreshes the credential.
- The Accept button gracefully closes the menu if manual entry is disabled (auto-provisioned credentials), preventing the user from seeing stale values.
- New `uiScript openCredentials` handler opens the credential menu from scriptable menus, enabling reuse for future navigation links.
- Runtime now mirrors the `ui_credentialPreview` cvar so menu authors can confirm the text box content inside the standalone template without building the VM.

## Layout Considerations
- Credential type selector is positioned above the credential field (y ≈ 196) with the text field at y ≈ 252 for parity with the original frame.
- Highlight styling mirrors existing navigation buttons: the active tab glows (0.964, 0.815, 0) while inactive buttons reset on close.
- Further visual polish (spacing fine-tuning, iconography) can be captured after we run an in-engine pass.

## Template Reference
- Added `ui/credential.menu` as a light-weight template that mirrors the runtime layout from `ui_cdkey.c`. The script reacts to `ui_credentialKind`, `ui_credentialManualHidden`, `ui_credentialPrompt`, `ui_credentialAutoMessage`, and related helper cvars so artists can preview the credential experience in the menu compiler without loading the VM.
- `ui_credentialManualHidden` flips to `1` whenever the engine detects an auto-provisioned Steam or standalone token, hiding the manual entry `itemDef` and revealing the platform guidance copy instead.
- Prompt, status, and auto-provision guidance strings flow through the shared cvars so localization sweeps can validate the new flows directly inside the template without editing the script.
- Intro helper copy (`Choose how you want to manage your account credential.`) sits above the selector to reinforce that players can switch credential kinds even when manual entry is hidden.

## Design Snapshot
- **State A – Manual entry enabled:** Legacy CD Key selected, text box visible, prompt (`Enter the 16-character key…`) rendered above the field, and status copy responding live to validation.
- **State B – Steam auto-provisioned:** Steam Ticket selected with `ui_credentialManualHidden=1`, credential field hidden, banner copy swapped to the Steam automation notice, and the refresh hint updated to `Launch through Steam to refresh or repair the linked credential.`
- **State C – Standalone auto-provisioned:** Standalone Token selected with manual entry hidden, auto message explains launcher ownership while the hint line reads `Launch from the standalone client to refresh or revoke the cached token.`

> Screenshot capture is still pending; use the notes above to stage reference shots once the menu renders in engine.

## Localization Handoff
- All runtime/UI copy for the credential menu has been catalogued in `docs/ui/localization/credential-menu_strings.md` so translators can batch the new text alongside other Quake Live menu updates.
