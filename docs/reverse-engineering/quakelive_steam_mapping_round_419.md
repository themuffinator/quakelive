# Quake Live ZMQ/CZMQ Mapping Round 419

Date: 2026-06-06

## Scope

This pass pins the `options_t::setsockopt` / `options_t::getsockopt` switch
tables that feed the retained server-owned `idZMQ` integration in
`src/code/server/sv_zmq.c`.  Round 378 mapped the `options_t` default layout
and address-mask helper layer; this round ties the retail switch-table entries
for ROUTER mandatory delivery, PLAIN server mode, and ZAP domain strings to the
source constants used by the RCON and stats endpoints.

Canonical evidence:

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- Ghidra function inventory:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/server/sv_zmq.c`
- Companion pass:
  `docs/reverse-engineering/quakelive_steam_mapping_round_378.md`

## Alias Reconstruction

This pass re-pinned 2 existing aliases:

| symbol | alias | confidence | evidence |
|---|---|---|---|
| `sub_40E0E0` | `zmq_options_t_setsockopt` | High | Validates option ids `4..0x37`, dispatches through `jump_table_40e5e4` / `lookup_table_40e65c`, rejects invalid size/value pairs with `EINVAL`, and stores the option payloads into the `options_t` layout named in Round 378. |
| `sub_40E690` | `zmq_options_t_getsockopt` | High | Mirrors the same option id range through `jump_table_40ea44` / `lookup_table_40eac0`, copies integer/string fields back to caller buffers, and reports `EINVAL` for unsupported options or undersized output buffers. |

No new aliases were needed: the switch owners were already named, but this
round adds the missing constant-level linkage between the retail dependency
surface and the reconstructed Quake Live server integration.

## Observed Facts

- Both option switch functions accept option numbers from `4` through `0x37`
  and reject out-of-range values by writing errno `0x16` (`EINVAL`).
- `setsockopt` option `0x21` stores an integer at `options + 0x168`
  (`arg2[0x5a]` in HLIL).  `sv_zmq.c` uses the same number as
  `QL_ZMQ_ROUTER_MANDATORY` when creating the RCON ROUTER socket.
- `setsockopt` option `0x2c` updates the PLAIN-server state pair at
  `options + 0x17c/0x180` (`arg2[0x5f]` / `arg2[0x60]`).  `sv_zmq.c` uses the
  same number as `QL_ZMQ_PLAIN_SERVER` for both RCON and stats sockets.
- `setsockopt` option `0x37` copies a string into the short-string storage at
  `options + 0x184` (`arg2[0x61]`).  `sv_zmq.c` uses the same number as
  `QL_ZMQ_ZAP_DOMAIN` with the retail domains `rcon` and `stats`.
- The matching `getsockopt` switch returns those same fields from
  `arg2[0x5a]`, the PLAIN-server state pair, and the ZAP-domain short-string
  storage, confirming that the set/get tables agree on the option layout.
- The retained server source does not need to reconstruct these C++ switch
  bodies: it dynamically resolves external libzmq for opted-in online-service
  builds and uses the pinned option constants at the integration boundary.

## Source Reconstruction Shape

The current source-facing contract is now pinned as:

```c
#define QL_ZMQ_ROUTER_MANDATORY 33
#define QL_ZMQ_PLAIN_SERVER 44
#define QL_ZMQ_ZAP_DOMAIN 55
```

and the retained server integration applies it as:

```c
idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, "rcon" );
idZMQ_TrySetSocketInt( socket, QL_ZMQ_ROUTER_MANDATORY, 1 );
idZMQ_TrySetSocketInt( socket, QL_ZMQ_PLAIN_SERVER, s_zmq.rconPassword[0] ? 1 : 0 );

idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, "stats" );
idZMQ_TrySetSocketInt( socket, QL_ZMQ_PLAIN_SERVER, s_zmq.statsPassword[0] ? 1 : 0 );
```

That is the correct reconstruction boundary for this repository: the numbers
are retail libzmq option ids, while the source-owned behavior is the Quake Live
server's RCON/stats application of those ids.

## Inference Boundary

- The option names are public libzmq semantic names; the evidence here is not a
  claim that the repository should vendor or reimplement the embedded retail
  libzmq switch bodies.
- The precise C++ field names inside `options_t` remain inferred from option
  semantics plus offset reuse.  The observed facts are the option numbers,
  switch table entries, field offsets, and source call sites.
- This round does not change live-service policy: all live ZMQ transport remains
  behind `QL_BUILD_ONLINE_SERVICES`, with default builds retaining fallback
  behavior.

## Verification

- `python -m pytest -q tests/test_platform_services.py::test_zmq_option_switch_tables_round_419_pin_source_constants`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

No runtime launch was needed; this was a static mapping pass over committed
HLIL/Ghidra evidence and reconstructed source constants.

## Parity Estimate

- Focused ZMQ option-switch/source-constant linkage confidence:
  **before 68% -> after 93%**.
- ZMQ-related source reconstruction confidence:
  **before 94.0% -> after 94.1%**.
- Overall Quake Live source parity:
  **before 55.82% -> after 55.83%**.
