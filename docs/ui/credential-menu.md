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

## Layout Considerations
- Credential type selector is positioned above the credential field (y ≈ 196) with the text field at y ≈ 252 for parity with the original frame.
- Highlight styling mirrors existing navigation buttons: the active tab glows (0.964, 0.815, 0) while inactive buttons reset on close.
- Further visual polish (spacing fine-tuning, iconography) can be captured after we run an in-engine pass.

## Screenshot Status
- No screenshot captured in this environment; verify spacing and palette in a local build before final sign-off.
