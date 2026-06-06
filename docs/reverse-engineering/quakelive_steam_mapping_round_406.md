# Quake Live ZMQ/CZMQ Mapping Round 406

Date: 2026-06-06

Focus: complete the TCP endpoint address parser and address-mask wiring that
feeds the already mapped TCP listener/connecter/socket transport stack.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json` and promoted
  `tcp_address_t`/`tcp_address_mask_t` RTTI/vtable symbols in
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`.

Round 390 pinned listener transport ownership and explicitly left endpoint
formatting for a future pass. This pass closes that gap around
`tcp_address.cpp`: interface resolution, host/port parsing, sockaddr-backed
construction, endpoint string formatting, CIDR-like mask parsing, and accept
filter matching. Short label: ZMQ TCP address endpoint parser wiring.

## Alias Reconstruction

This pass added 5 aliases and re-pinned 5 existing aliases in
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_411A10` | `zmq_tcp_address_t_resolve_interface` | Existing | Re-pinned as the interface wildcard or named-interface resolver that seeds IPv4/IPv6 sockaddr storage before `tcp_address_t::resolve` sets the port. |
| `sub_411D20` | `zmq_tcp_address_t_resolve_nic_name` | High | Helper calls `getaddrinfo` on a NIC/host name with address-family selection and copies the resulting sockaddr into the address object. |
| `sub_411E20` | `zmq_tcp_address_t_ctor` | High | Default constructor installs the `tcp_address_t` vtable and zeros the sockaddr storage. |
| `sub_411E50` | `zmq_tcp_address_t_ctor_from_sockaddr` | High | Sockaddr constructor asserts `sa && sa_len > 0`, installs the vtable, zeros storage, and copies IPv4/IPv6 sockaddr fields according to family and length. |
| `sub_411F20` | `zmq_tcp_address_t_dtor` | High | Tiny complete destructor restores the `tcp_address_t` vtable; vtable evidence shares the scalar-delete thunk through the common address base. |
| `sub_411F30` | `zmq_tcp_address_t_resolve` | Existing | Re-pinned as the host/port parser that handles bracketed IPv6 literals, wildcard ports, numeric ports, and interface-vs-host resolution modes. |
| `sub_412180` | `zmq_tcp_address_t_to_string` | Existing | Re-pinned as the `tcp://host:port` formatter, using `getnameinfo`, bracketed IPv6 output, and stringstream cleanup. |
| `sub_4124E0` | `zmq_tcp_address_mask_t_resolve` | Existing | Re-pinned as the address-mask parser that splits `address/mask`, resolves the address, validates IPv4/IPv6 prefix bounds, and stores the effective mask width. |
| `sub_412720` | `zmq_tcp_address_mask_t_to_string` | Existing | Re-pinned as the `address/mask` formatter, with bracketed IPv6 mask output and empty-string fallback for invalid masks. |
| `sub_412970` | `zmq_tcp_address_mask_t_match_address` | High | Listener accept filtering calls this helper; it validates sockaddr family/length, compares full bytes, applies the residual-bit mask, and returns match/no-match. |

## Observed Facts

- The `tcp_address_t` vtable has only a scalar-delete slot and a `to_string`
  slot. `tcp_address_mask_t` reuses that shape but points the formatter slot at
  the mask-specific output body.
- `tcp_address_t::resolve` splits on the last colon, strips IPv6 brackets, and
  accepts wildcard-style service strings through the two literal comparisons
  visible in HLIL. It calls either `resolve_interface` or `resolve_nic_name`
  depending on the caller's resolution mode.
- `resolve_interface` handles wildcard addresses directly: IPv4 stores
  `AF_INET` plus `htonl(0)`, while IPv6 stores `AF_INET6` and zeroed IPv6
  storage. Non-wildcard names are routed through `getaddrinfo`.
- `tcp_listener_t::get_address` constructs a `tcp_address_t` from `getsockname`
  output and immediately calls `tcp_address_t::to_string`.
- `tcp_listener_t::accept` calls `tcp_address_mask_t::match_address` for each
  configured mask before accepting a peer socket.
- `tcp_address_mask_t::match_address` compares whole bytes first and then masks
  the remaining high bits, using a 32-bit maximum for IPv4 and a 128-bit maximum
  for IPv6.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered address layer
gives the following model:

```c
// conceptual reconstruction, not checked-in engine C source
int tcp_address_t::resolve(const char *name, bool local, bool ipv6)
{
	const char *colon = strrchr(name, ':');
	if (!colon) {
		errno = EINVAL;
		return -1;
	}

	string host(name, colon - name);
	string service(colon + 1);
	if (host_is_bracketed_ipv6(host))
		host = host.substr(1, host.size() - 2);

	uint16_t port = service_is_wildcard(service) ? 0 : atoi(service.c_str());
	if (!port && !service_is_wildcard(service)) {
		errno = EINVAL;
		return -1;
	}

	int rc = local
		? resolve_interface(host.c_str(), ipv6)
		: resolve_nic_name(host.c_str(), ipv6);
	if (rc == 0)
		address.port = htons(port);
	return rc;
}

bool tcp_address_mask_t::match_address(const sockaddr *addr, size_t addrlen)
{
	assert(address_mask != -1 && addr != NULL);
	if (addr->sa_family != address.ss_family)
		return false;

	int max_bits = (addr->sa_family == AF_INET6) ? 128 : 32;
	int bits = min(address_mask, max_bits);
	int whole_bytes = bits / 8;
	int residual = bits % 8;
	if (memcmp(address_bytes, addr_bytes, whole_bytes) != 0)
		return false;
	if (!residual)
		return true;
	return (address_bytes[whole_bytes] & (0xff << (8 - residual)))
		== (addr_bytes[whole_bytes] & (0xff << (8 - residual)));
}
```

## Inference Boundary

The MSVC stringstream/stringbuf helpers around `0x00412B50..0x00413280` remain
unnamed in this pass. They are local formatting scaffolding for the recovered
`to_string` bodies, while the stable ZeroMQ ownership is already expressed by
the address object functions and vtable slots.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_tcp_address_round_406_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused ZMQ TCP address endpoint parser wiring:
  **before 57% -> after 91%**.
- ZMQ-related source reconstruction confidence, including retained socket
  families, session/engine wiring, pipe lifecycle, routing, subscription
  prefixes, TCP transport, and TCP endpoint parsing:
  **before 91.7% -> after 91.9%**.
- Overall Quake Live source parity:
  **before 55.69% -> after 55.70%**.
