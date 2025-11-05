# HLIL Comparison: Quake III Arena vs. Quake Live

This document summarizes notable differences between the available High Level Intermediate Language (HLIL) exports for Quake III Arena (`quake3.exe`) and Quake Live (`qagamex86.dll`). The goal is to provide quick reference points when porting behaviour or validating divergences between the two code bases.

## Binary metadata

| Aspect | Quake III Arena (`quake3.exe`) | Quake Live (`qagamex86.dll`)
| --- | --- | --- |
| Imported libraries | `ADVAPI32`, `WINMM`, `WSOCK32`, `KERNEL32`, `USER32`, `GDI32`, `ole32` | `MSVCR100`, `MSVCP100`, `KERNEL32` |
| Toolchain signatures | Predominantly Visual C++ 6.0/Visual Studio 98 era, mixed with MASM objects | Visual Studio 2010 SP1 with minor VS2008/VS2002 artefacts |
| Primary code range | `0x00401000-0x004b0c22` | `0x10001000-0x1007b9bb` |
| Writable data range | `0x004b5000-0x007d7140` | `0x1008d000-0x105e9ee0` |

The metadata highlights Quake III Arena's legacy Visual C++ 6.0 toolchain, compared to Quake Live's Visual Studio 2010 runtime dependencies and slimmer import table, reflecting the move to a modernized standalone DLL.【F:references/hlil/quake3/quake3.exe/quake3.exe_hlil_split/quake3.exe_hlil_part01.txt†L1-L46】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt†L1-L41】

## Module loading architecture

*Quake III Arena* delegates gameplay to loadable VMs: `VM_Create` is invoked with the `qagame` identifier and the current `vm_game` setting. Failure aborts the process, underscoring the runtime separation between the engine and the game code.【F:references/hlil/quake3/quake3.exe/quake3.exe_hlil_split/quake3.exe_hlil_part01.txt†L48990-L49007】

*Quake Live* ships a native `qagamex86.dll`, so the gameplay logic executes directly inside the DLL. The HLIL shows in-place CVar registrations and configuration parsing (e.g., `sub_10053400`) instead of VM dispatch, reinforcing that the module already contains the full ruleset implementation.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L9150-L9235】

## Platform and authentication differences

*CD verification vs. Steam auth*: Quake III Arena enforces optical media checks; the engine exits through `sub_41a0a0` when `fs_restrict` indicates a missing game CD.【F:references/hlil/quake3/quake3.exe/quake3.exe_hlil_split/quake3.exe_hlil_part01.txt†L45510-L45534】 Quake Live replaces this with online platform integration—`ClientConnect` contains explicit Steam token validation, prints per-connection status, and formats Steam IDs for logging.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt†L41140-L41199】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L43542-L43569】

## Gameplay configuration surface

Quake Live expands the tunable gameplay surface considerably:

- **Per-weapon starting ammo CVars** – The DLL allocates and references a matrix of `g_startingAmmo_*` strings, exposing loadout tweaking not visible in the Quake III engine binary.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt†L41330-L41420】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L43562-L43575】
- **Weapon behaviour knobs** – `sub_10053400` scans for configuration keys such as `weapon_reload_<weapon>`, `g_damage_g`, and `g_knockback_g`, indicating script-driven weapon tuning hooks that Quake III lacks in its shipped executable.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L9150-L9235】

By contrast, the Quake III metadata sampled in the same region of the HLIL focuses on registering classic bot-related CVars (`bot_*`), underlining the older feature set.【F:references/hlil/quake3/quake3.exe/quake3.exe_hlil_split/quake3.exe_hlil_part01.txt†L45510-L45519】

## Client management updates

The Quake Live `ClientConnect` path performs additional bookkeeping compared to the Quake III engine-side dispatcher:

- It masks client flags when the server marks a connecting player as a bot and gracefully exits with a bot failure token if validation fails.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt†L41142-L41155】
- Successful human connections trigger multiple callbacks (`priv %i`, formatted `print` messages) and optionally broadcast Steam identifiers, implying hooks for spectator messaging and backend analytics.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt†L41157-L41199】【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt†L43558-L43569】

These additions reflect Quake Live's shift toward persistent profiles and live service tooling, whereas Quake III Arena confines client initialization to whatever logic the dynamically loaded VM provides.

## Using this reference

When porting behaviours from Quake Live to a Quake III-derived environment (or vice versa), treat the items above as checkpoints:

1. Confirm whether a feature was historically engine-driven (Quake III) or moved into the DLL (Quake Live).
2. Map new CVars or configuration keys to the legacy equivalents—or implement shims if they have no counterpart.
3. Account for platform assumptions: Steam-backed identity and messaging code must be replaced or stubbed out if targeting CD-key-based infrastructure.

This comparison should be extended as more HLIL excerpts are annotated, but it captures several high-impact divergences for gameplay and platform integration work.
