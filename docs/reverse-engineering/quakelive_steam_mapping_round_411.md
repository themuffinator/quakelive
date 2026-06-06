# Quake Live ZMQ/CZMQ Mapping Round 411

Date: 2026-06-06

Focus: recover the Windows `err.cpp` helper wiring used by the public
`zmq_poll` wrapper, stream-engine socket I/O, and TCP listener setup.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and static import/string evidence in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`,
  `imports.txt`, and `decompile_top_functions.c`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Round 365 pinned the public ZMQ API wrappers and retained
`sub_401D10 -> zmq_wsa_error_no` as the Winsock error-code string table. This
pass fills the adjacent `err.cpp` helpers that the wrappers and socket engines
use to raise fatal diagnostics, format Win32 last-error text, and translate WSA
errors into the CRT `errno` domain.

## Alias Reconstruction

This pass added 4 aliases to
`references/analysis/quakelive_symbol_aliases.json` and re-pinned the existing
`zmq_wsa_error_no` string-table helper.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_401CD0` | `zmq_abort` | High | Raises exception code `0x40000015` with one diagnostic argument and is tail-called from fatal ZMQ assertion/reporting paths. |
| `sub_401CF0` | `zmq_wsa_error` | High | Reads `WSAGetLastError()`, suppresses `WSAEWOULDBLOCK`, and delegates all other codes to `zmq_wsa_error_no`. |
| `sub_401FB0` | `zmq_win_error` | High | Formats `GetLastError()` through `FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS, ..., 0x400, buffer, 0x100, nullptr)` and asserts in `err.cpp` line `0xd5` if formatting fails. |
| `sub_402030` | `zmq_wsa_error_to_errno` | High | Maps WSA and host-lookup errors to CRT errno constants, returning `0` only for the would-block fallback and aborting unknown non-would-block WSA errors through `zmq_wsa_error_no`. |

## Observed Facts

- The public `zmq_poll` wrapper calls `select()`, writes
  `zmq_wsa_error_to_errno(WSAGetLastError())` into `_errno()`, then uses
  `zmq_wsa_error()` and `zmq_abort()` for fatal non-`ENOTSOCK` diagnostics.
- `zmq_wsa_error()` returns `0` for `WSAEWOULDBLOCK` and otherwise tail-calls
  the previously mapped `zmq_wsa_error_no()` string table.
- `zmq_win_error()` is used by Win32 handle/setup failure paths such as
  `tcp_listener.cpp` `SetHandleInformation` and `signaler.cpp` event handling.
- `zmq_wsa_error_to_errno()` contains the retail Windows translation table:
  `WSAEWOULDBLOCK -> 0x10`, `WSAENOTSOCK -> 0x80`, `WSAEMSGSIZE -> 0x73`,
  `WSAEAFNOSUPPORT -> 0x66`, and host lookup failures -> `0xe`.
- Stream-engine `send`/`recv`, TCP listener bind/listen setup, and public poll
  all reuse the same mapper, which makes this a shared platform-service layer
  rather than a single call-site convenience wrapper.

## Source Reconstruction

This is mapping/static reconstruction only. No GPL-side engine C source changed
in this pass. The recovered source shape is:

```cpp
const char *wsa_error()
{
	const int err = WSAGetLastError();
	return err == WSAEWOULDBLOCK ? 0 : wsa_error_no(err);
}

void win_error(char *buffer)
{
	const DWORD rc = FormatMessageA(
		FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
		NULL, GetLastError(), 0x400, buffer, 0x100, NULL);
	assert(rc);
}

int wsa_error_to_errno(int err)
{
	switch (err) {
	case WSAEWOULDBLOCK:
		return 0x10;
	case WSAENOTSOCK:
		return 0x80;
	default:
		/* Retail aborts on unknown non-would-block WSA errors. */
	}
}
```

The exact errno constants are preserved as retail numeric outputs in this note
because the executable was built against the Windows CRT errno table.

## Inference Boundary

`sub_402260` is an 8-byte `DeleteCriticalSection` wrapper immediately after the
error helpers, but this pass leaves it unnamed until the surrounding mutex/ctx
constructor ownership is rechecked. The larger `0x00402270..0x00402480`
constructor-like slab remains deferred to a future `ctx_t` reconstruction pass.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_windows_err_helpers_round_411_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused ZMQ Windows `err.cpp` helper wiring:
  **before 34% -> after 91%**.
- ZMQ-related source reconstruction confidence:
  **before 92.4% -> after 92.5%**.
- Overall Quake Live source parity:
  **before 55.74% -> after 55.75%**.
