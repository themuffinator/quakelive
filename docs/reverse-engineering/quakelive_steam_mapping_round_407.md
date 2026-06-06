# Quake Live ZMQ/CZMQ Mapping Round 407

Date: 2026-06-06

Focus: close the deferred retained libzmq endpoint container lifecycle helpers
that connect `socket_base_t` endpoint parsing, TCP address ownership, endpoint
URI rendering, and `session_base_t` cleanup.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and the retained `tcp` literal in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Rounds 390 and 391 deliberately left `sub_41AAE0`/`sub_41AB60` unnamed while
the listener, connecter, and shared endpoint renderer were being pinned. With
the TCP address parser now closed in round 406, these two helpers have enough
cross-cutting evidence to promote.

## Alias Reconstruction

This pass added 2 aliases to
`references/analysis/quakelive_symbol_aliases.json` and re-pinned the existing
endpoint renderer as the downstream consumer.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_41AAE0` | `zmq_endpoint_t_ctor` | High | Constructor initializes two MSVC string fields from the parsed protocol/address strings and clears the optional concrete address pointer at offset `0x38`. `socket_base_t` allocates this `0x3c`-byte object after endpoint parsing. |
| `sub_41AB60` | `zmq_endpoint_t_dtor` | High | Destructor conditionally deletes the concrete TCP address object when the protocol string equals the retained `tcp` literal, then releases both endpoint strings. `socket_base_t` failure cleanup and `session_base_t` destruction both call it before freeing the object. |
| `sub_41AC10` | `zmq_endpoint_t_to_string` | Existing | Re-pinned as the renderer that either delegates to the concrete TCP address object's virtual formatter or falls back to `protocol://address` from the two stored strings. |

## Observed Facts

- `socket_base_t` allocates a `0x3c`-byte endpoint object and calls
  `sub_41AAE0(arguments_2, &var_54, &var_70)` after parsing an endpoint into
  protocol and address string fields.
- When the protocol equals the retained literal `tcp` at `data_54f8c0`,
  `socket_base_t` allocates a concrete `tcp_address_t`, stores it in endpoint
  field `0x38`, and resolves the textual address through the already named TCP
  address constructor/parser path.
- On TCP address resolution failure, `socket_base_t` calls `sub_41AB60` and
  then deletes the endpoint allocation, proving the destructor/free split.
- `session_base_t` stores the endpoint pointer in field `0xad`; its destructor
  calls `sub_41AB60(esi)` and then frees the endpoint object.
- `zmq_endpoint_t_to_string` consumes the same object. TCP endpoints with a
  concrete address object dispatch through that object's virtual `to_string`;
  non-concrete endpoints render the stored protocol and address strings as a
  URI.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered lifecycle is:

```c
// conceptual reconstruction, not checked-in engine C source
endpoint_t::endpoint_t(const string &protocol, const string &address)
{
	this->protocol = protocol;
	this->address = address;
	this->tcp_address = NULL;
}

endpoint_t::~endpoint_t()
{
	if (protocol == "tcp" && tcp_address != NULL) {
		delete tcp_address;
		tcp_address = NULL;
	}
	address.clear();
	protocol.clear();
}
```

The GPL-side server ZMQ reconstruction remains in `src/code/server/sv_zmq.c`
and still uses the public dynamically loaded ZMQ API. These aliases document
the retained libzmq object lifetime underneath that API rather than adding a
private C++ libzmq clone to the source tree.

## Inference Boundary

The names are promoted only for the endpoint container lifecycle. The nearby
`sub_41AF75` exception-state helper is intentionally left anonymous because it
is MSVC stringstream failure handling, not a stable ZMQ source function.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_endpoint_lifecycle_round_407_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused ZMQ endpoint container lifecycle wiring:
  **before 48% -> after 93%**.
- ZMQ-related source reconstruction confidence, including retained socket
  families, session/engine wiring, pipe lifecycle, routing, subscription
  prefixes, TCP transport, TCP endpoint parsing, and endpoint object lifetime:
  **before 91.9% -> after 92.1%**.
- Overall Quake Live source parity:
  **before 55.70% -> after 55.71%**.
