# Credential Menu Localization Strings

| Identifier | English Text | Notes |
| --- | --- | --- |
| credential_menu.banner | ACCOUNT CREDENTIAL | Banner shared by runtime and template for consistency. |
| credential_menu.intro | Choose how you want to manage your account credential. | Intro helper to remind players they can toggle credential types. |
| credential_menu.type_label | Credential Type | Label for the credential kind selector. |
| credential_menu.kind_legacy | Legacy CD Key | Selector option for the classic CD key flow. |
| credential_menu.kind_steam | Steam Ticket | Selector option for Steam-provided credentials. |
| credential_menu.kind_standalone | Standalone Token | Selector option for launcher-provided credentials. |
| credential_menu.prompt_legacy | Enter the 16-character key from your retail copy. | Displayed when Legacy CD Key is active. |
| credential_menu.prompt_steam | Paste the Steam session ticket provided by the platform. | Manual entry guidance for Steam credentials. |
| credential_menu.prompt_standalone | Paste the launcher-issued standalone token for this device. | Manual entry guidance for standalone tokens. |
| credential_menu.success_legacy | Key format looks valid. Save to apply. | Success copy after validation passes. |
| credential_menu.success_token | Token captured. Save to apply. | Shared by Steam/standalone tokens. |
| credential_menu.error_legacy | Key must contain 16 valid characters (no spaces or dashes). | Error state for legacy keys. |
| credential_menu.error_token | Token cannot be blank. | Error state for token-based credentials. |
| credential_menu.auto_legacy | This credential must be managed manually. | Automatic credential notice for legacy keys (rare edge cases). |
| credential_menu.auto_steam | Steam automatically provisions this credential while you're signed in, so manual entry stays disabled until the ticket expires. | Auto-provision messaging for Steam. |
| credential_menu.auto_standalone | The standalone launcher provisions this token for you on launch, so manual entry stays disabled until the cached token clears. | Auto-provision messaging for standalone tokens. |
| credential_menu.auto_hint_steam | Launch through Steam to refresh or repair the linked credential. | Refresh hint when Steam hides manual entry. |
| credential_menu.auto_hint_standalone | Launch from the standalone client to refresh or revoke the cached token. | Refresh hint when standalone hides manual entry. |
| credential_menu.accept_disabled | Automatic credentials close the menu when you press Accept. | Supplemental QA note for tooltip/screenshot staging. |

> The localization table mirrors the runtime string arrays in `src/code/q3_ui/ui_cdkey.c`. Translators should keep the guidance tone consistent and ensure "Steam" and "Standalone" product names remain unaltered.
