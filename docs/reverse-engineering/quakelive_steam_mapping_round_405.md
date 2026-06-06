# Quake Live ZMQ/CZMQ Mapping Round 405

Date: 2026-06-06

Focus: recover the subscription-prefix trie wiring adjacent to the FQ/LB/DIST
pipe routing layer: XPUB's multi-pipe subscription trie, XSUB's local
subscription trie, and the bridge that marks matching DIST pipes.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Round 404 pinned the immediate pipe-routing helpers. This pass follows the
publication socket wiring into prefix storage: `mtrie_t` for XPUB subscriptions
keyed by `pipe_t`, `trie_t` for XSUB local subscriptions, and the compiled
matcher that turns subscription hits into DIST matching-window entries. Short
label: ZMQ subscription trie/mtrie wiring.

## Alias Reconstruction

This pass added 8 aliases and re-pinned 5 existing aliases in
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_41ED40` | `zmq_mtrie_t_dtor` | High | XPUB destructor calls this helper on the `mtrie_t` member; the body destroys the pipe set, recursively destroys child nodes, frees child tables, and asserts `next.node` when a single-child node is malformed. |
| `sub_41EE80` | `zmq_mtrie_t_destroy_pipe_set` | High | Shared mtrie pipe-set teardown path destroys the red-black tree storage and deletes the set object. |
| `sub_41EEF0` | `zmq_mtrie_t_destroy_node` | High | Delete wrapper calls the mtrie destructor body and then releases the node allocation. |
| `sub_41EF10` | `zmq_mtrie_t_add` | Existing | Re-pinned as the XPUB multi-pipe prefix insert path, including first-pipe set allocation, child-table expansion, and `live_nodes` maintenance. |
| `sub_41F3C0` | `zmq_mtrie_t_rm_helper` | Existing | Re-pinned as the recursive remove/enumeration helper that calls the supplied erased-pipe callback, rewrites compressed child ranges, and prunes empty child nodes. |
| `sub_41FA70` | `zmq_mtrie_t_rm` | Existing | Re-pinned as the public remove path that delegates to the recursive helper, verifies `erased == 1`, destroys empty children, and reports whether the node became redundant. |
| `sub_41FF60` | `zmq_mtrie_t_match_to_dist` | High | XPUB send path calls this matcher before `dist_t::send_to_matching`; the body walks matching subscription prefixes and swaps hit pipes into the DIST matching range. |
| `sub_420100` | `zmq_mtrie_t_is_redundant` | High | Small mtrie predicate returns true only when no pipe set and no live child nodes remain. |
| `sub_420840` | `zmq_trie_t_dtor` | High | XSUB destructor calls this helper on the local `trie_t`; the body recursively destroys child nodes, frees child tables, and asserts `next.node` for malformed single-child nodes. |
| `sub_420900` | `zmq_trie_t_destroy_node` | High | Delete wrapper calls the trie destructor body and then releases the node allocation. |
| `sub_420920` | `zmq_trie_t_add` | Existing | Re-pinned as the local subscription-prefix insert path, including child-table expansion and `live_nodes` updates. |
| `sub_420D90` | `zmq_trie_t_rm` | Existing | Re-pinned as the local subscription-prefix removal path, including node pruning and compressed-range shrinkage. |
| `sub_421320` | `zmq_trie_t_apply` | High | XSUB pipe attach/activation calls this walker with `sub_418A80`; the body grows the prefix buffer, calls the callback for subscribed nodes, and recursively emits child prefixes. |

## Observed Facts

- XPUB owns an `mtrie_t` at the same object region that destruction passes to
  `sub_41ED40`. It also owns the `dist_t` region used by round 404.
- XPUB send first calls `sub_41FF60(arg1 + 0x380, sub_40B660(...), size,
  arg1)`, then calls `sub_420500(..., arg1 + 0x390)`. The matcher therefore
  marks `dist_t` matching entries before `dist_t::send_to_matching` fans the
  message out.
- The mtrie destructor and remove paths use the same child encoding pattern:
  `count == 0` for no child, `count == 1` for a direct `next.node`, and
  `count > 1` for a table indexed from `min` through `min + count - 1`.
- The mtrie remove helper preserves a per-node pipe set, destroys it when empty,
  and prunes child nodes when `mtrie_t_is_redundant` reports no pipes and no
  live children.
- XSUB owns a local `trie_t` and calls `sub_421320` on pipe attach and
  activation, with `sub_418A80` as the callback that forwards stored
  subscriptions to the pipe.
- The trie apply walker maintains a growable byte buffer, writes each child byte
  into the buffer, calls the supplied callback when a subscribed node is reached,
  and recurses through the compressed child layout.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered subscription
layer gives the following model:

```c
// conceptual reconstruction, not checked-in engine C source
void xpub_t::xsend(msg_t *msg)
{
	if (!manual_matching)
		subscriptions.match_to_dist(msg->data(), msg->size(), this);

	dist.send_to_matching(msg);
	more_out = msg->flags() & msg_t::more;
	if (!more_out)
		dist.unmatch_all();
}

bool mtrie_t::rm(pipe_t *pipe, unsigned char *prefix, size_t size)
{
	bool erased = rm_helper(pipe, prefix, size, on_pipe_removed, NULL);
	assert(erased == 1);
	return pipes.empty() && live_nodes == 0;
}

void trie_t::apply(unsigned char **buffer, size_t size, size_t max,
	void (*fn)(unsigned char *data, size_t size, void *arg), void *arg)
{
	if (refcnt)
		fn(*buffer, size, arg);

	ensure_capacity(buffer, size + 1, &max);
	for (each child) {
		(*buffer)[size] = child_byte;
		child->apply(buffer, size + 1, max, fn, arg);
	}
}
```

## Inference Boundary

`sub_41FF60` is named `match_to_dist` instead of plain `match` because the HLIL
body does not expose a generic callback parameter. It is called from XPUB with
the XPUB object as context and directly swaps hit pipes into the DIST matching
window. The name keeps the observed specialization visible while preserving the
underlying mtrie ownership. This pass does not rename the nearby xpub/xsub
socket member functions themselves.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_subscription_trie_round_405_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused ZMQ subscription trie/mtrie wiring:
  **before 40% -> after 88%**.
- ZMQ-related source reconstruction confidence, including retained socket
  families, session/engine wiring, pipe lifecycle, message queues, immediate
  pipe routing, and subscription-prefix ownership:
  **before 91.5% -> after 91.7%**.
- Overall Quake Live source parity:
  **before 55.68% -> after 55.69%**.
