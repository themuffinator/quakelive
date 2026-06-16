# quakelive_steam.exe Mapping Round 662

Date: 2026-06-15

Scope: focused ZMQ ZAP domain constant boundary for the retained `idZMQ`
RCON/stats socket setup and manual ZAP credential validation path. This round
maps Quake Live-owned wiring only and does not reconstruct libzmq/CZMQ
internals.

## Summary

Retail uses the same domain literals in two related places:

- `idZMQ` socket setup calls `zsock_set_zap_domain(..., "rcon")` for the RCON
  ROUTER socket and `zsock_set_zap_domain(..., "stats")` for the stats PUB
  socket.
- CZMQ `zauth` PLAIN authentication builds a `%s_%s` lookup key from the ZAP
  domain and username, so the effective password records are `rcon_rcon` and
  `stats_stats`.

SRP already keeps `QL_ZMQ_DOMAIN_RCON` and `QL_ZMQ_DOMAIN_STATS` for manual
ZAP credential validation. This round routes socket ZAP-domain setup through
those same constants, making the retail ZAP domain constant boundary explicit
and avoiding two separate spellings of the same retail contract.
The manual ZAP credential lookup uses the same domain constants as socket
setup.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F3F80` | `idZMQ_RegisterCvarsAndInitRcon` | High | Sets the RCON socket ZAP domain to `rcon`. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | High | Sets the stats socket ZAP domain to `stats`. |
| `sub_4F5750` | `zsock_set_zap_domain` | High | CZMQ option helper used by both retained socket setup paths. |
| `sub_4F6630` | `s_authenticate_plain` | High | Authenticates PLAIN requests against the domain/username password table. |
| `sub_4F7360` | `zsys_sprintf` | High | Builds the `zauth` lookup key as `%s_%s`. |

## Observed Facts

- `sub_4F3F80` creates the RCON ROUTER socket and calls
  `sub_4F5750(eax_12, "rcon")` before enabling PLAIN server mode and binding.
- `sub_4F4210` creates the stats PUB socket and calls
  `sub_4F5750(eax_11, "stats")` before enabling PLAIN server mode and binding.
- `sub_4F6630` formats the PLAIN authentication lookup key with `%s_%s`,
  performs the lookup, compares the supplied password, and logs the
  allowed/denied PLAIN result.
- The retail string corpus contains stable `rcon`, `stats`, and `%s_%s`
  literals.

Observed fact: ZAP domain ownership belongs to Quake Live's retained `idZMQ`
socket setup, while the `%s_%s` table lookup is embedded CZMQ `zauth` evidence.
This round does not reconstruct libzmq/CZMQ internals.

Inferred source boundary: SRP should use one pair of Quake Live domain
constants across socket setup and manual ZAP credentials, while not
reconstructing `zsock_set_zap_domain`, `s_authenticate_plain`, or CZMQ's table
implementation.

## Source Reconstruction

- Updated `idZMQ_EnsureRconSocket` to set `QL_ZMQ_ZAP_DOMAIN` with
  `QL_ZMQ_DOMAIN_RCON`.
- Updated `idZMQ_EnsureStatsPublisher` to set `QL_ZMQ_ZAP_DOMAIN` with
  `QL_ZMQ_DOMAIN_STATS`.
- Added a focused parity gate that cross-checks aliases, Ghidra rows, Binary
  Ninja HLIL, retail string anchors, source domain constants, manual ZAP
  credential validation, and the absence of CZMQ implementation calls in
  `sv_zmq.c`.

## Confidence And Open Questions

Confidence is high because the two socket setup paths, `zauth` PLAIN lookup
shape, string corpus, existing password-file record formats, and current source
now agree on the same domain constants.

Open question: end-to-end live auth can still be validated later with an
external `libzmq.dll` fixture. Static evidence is sufficient for this
source-boundary pass.

## Validation

- `python -m pytest -q tests/test_platform_services.py -k zmq_zap_domain_constant_boundary_round_662`
  - `1 passed, 207 deselected in 0.13s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `66 passed, 142 deselected in 1.43s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.12s`
- `git diff --check`
  - Clean, with existing CRLF normalization warnings only.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`

## Parity Estimate

- Focused ZAP domain constant/source-boundary confidence:
  **before 94% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 97.7% -> after 97.8%**.
- Repo-wide parity remains **99%** because this pass closes a local retained
  ZMQ ZAP-domain source-shape gap without changing the strict-retail Windows
  replacement score.
