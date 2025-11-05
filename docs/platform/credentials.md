# Credential persistence and migration

The client persists whatever credential is currently stored in `cl_cdkey`
inside `q3key` files that live next to the game data directories. Each
location that previously stored a 16-character CD-key (`baseq3/q3key`,
`<modname>/q3key`, etc.) still exists, but the payload is now structured as a
`<kind> <value>` pair written on the first line. The remainder of the file is
left untouched so legacy warning comments are preserved.

* `kind` uses the same labels exposed by `QL_GetCredentialLabel`: `legacy_cdkey`,
  `steam`, and `standalone`.
* `value` stores the raw credential text without any client-side decoration.
  For legacy CD-keys this is the 16-character alphanumeric value, while
  platform tokens keep their full body (Steam tickets, standalone launcher
  blobs, and so on).

When reading a file, the loader skips comment lines, trims whitespace, and
falls back to the historical "bare string" interpretation if no explicit kind
is present. This makes the migration transparent: existing installations that
only contain the legacy 16-byte blob are automatically ingested, formatted with
an explicit `legacy_cdkey` label on the next save, and continue to work without
user interaction.

Two buffers are maintained internally:

* `cl_cdkey` – the canonical credential that is sent during authorization and
  saved to `baseq3/q3key`.
* `cl_cdkey_mod` – a module-specific override used when `UI_usesUniqueCDKey`
  returns true. It is written to the current mod's `q3key` file when present,
  otherwise the base credential is reused as a fallback.

Because the UI helpers now operate on the full string instead of slicing
16-character segments, any credential retrieved from disk (Steam ticket,
standalone token, or sanitized CD-key) is surfaced verbatim through
`CLUI_GetCDKey`/`CLUI_SetCDKey` and serialized using the `<kind> <value>`
format. No manual migration steps are required for end users beyond launching a
build that contains these changes.
