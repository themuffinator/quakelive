# Credential persistence and migration

Quake Live keeps the active credential in the `cl_cdkey` cvar and writes it to
`q3key` files alongside the game data. The new helpers serialize both the
credential type and its value so the engine can distinguish between legacy
CD-keys and modern authorization tokens during subsequent boots.

## On-disk layout

The first non-comment line of every `q3key` now follows this structure:

```
<kind> <value>\n
```

* `kind` uses the labels returned by `QL_GetCredentialLabel`. The shipping
  helpers currently emit `legacy_cdkey`, `steam`, or `standalone`.
* `value` stores the canonical credential string exactly as it is forwarded to
  online services. Legacy CD-keys contain the traditional 16 alphanumeric
  characters, while Steam and standalone builds persist their opaque ticket
  blobs with the `steam:` or `standalone:` prefixes intact.

The remainder of the file remains untouched; the classic warning comments are
still appended verbatim.

## Loading behaviour and migration

The loader trims whitespace, skips comment lines, and looks for the `<kind>
<value>` tuple. If no kind is present it falls back to the historical
"single-string" interpretation and treats the whole line as the credential.
When that happens (or when the stored value is missing the expected prefix for
its declared kind) the helpers set `CVAR_ARCHIVE` so the next `Com_WriteConfig`
cycle rewrites the file using the typed layout. Legacy CD-key blobs pick up the
`legacy_cdkey` label automatically, while platform tokens are rewritten with
their prefixes attached.

Credential values that contain newline characters are rejected to avoid
inadvertently serializing multiple records inside a single file.

## Storage locations

Each writable game directory keeps its own credential file:

* `baseq3/q3key` mirrors the canonical credential stored in `cl_cdkey`.
* `<modname>/q3key` (created when `fs_game` is set) stores the override from
  `cl_cdkey_mod`. Mods that do not opt into a unique key simply reuse the base
  credential when saving.

Whenever either buffer changes—or a legacy format is detected during load—the
appropriate `q3key` is rewritten using the typed layout described above.
Launching a build that contains these helpers is enough to migrate older
plaintext CD-key files; no manual steps are required.

## Runtime buffers

The engine exposes the active credentials through two buffers:

* `cl_cdkey` – the canonical value forwarded during authorization and persisted
  to `baseq3/q3key`.
* `cl_cdkey_mod` – a per-mod override used when `UI_usesUniqueCDKey` reports
  that the current mod requires its own credential.

UI helpers now operate on the full credential string (including prefixes such as
`steam:`) so any token retrieved from disk is surfaced verbatim through
`CLUI_GetCDKey`/`CLUI_SetCDKey` and then rewritten in the `<kind> <value>`
format on disk.
