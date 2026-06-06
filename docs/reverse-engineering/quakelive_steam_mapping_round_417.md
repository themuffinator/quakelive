# Quake Live ZMQ/CZMQ Mapping Round 417

Date: 2026-06-06

## Scope

This pass closes the `own_t` owned-child pointer-set support slab left around
the already named ZMQ lifecycle methods.  Round 148 identified the shared
pointer-keyed red-black-tree insert, erase, and rebalance helpers used by
`own.cpp`, `router.cpp`, `session_base.cpp`, and `mtrie.cpp`; Round 417 fills
the local create/find/iterator/clear helpers that make `own_t::process_own`,
`own_t::process_term_req`, the destructor, and `own_t::process_term` read as a
single owned pointer set instead of a collection of anonymous STL fragments.

Canonical evidence:

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- Ghidra function inventory:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Companion pass:
  `docs/reverse-engineering/quakelive_steam_mapping_round_148.md`

## Alias Reconstruction

This pass added 8 aliases:

| symbol | alias | confidence | evidence |
|---|---|---|---|
| `sub_40F720` | `std_tree_free_zmq_ptr_node_subtree` | High | Recursive delete helper for the `0x14` pointer-node tree layout; used by `own_t::process_term` and the shared full-tree clear helper. |
| `sub_40F760` | `std_tree_rotate_right_zmq_ptr_node` | High | Red-black-tree right rotation over the pointer-node layout with parent/child repair and `0x11` sentinel checks. |
| `sub_40F7C0` | `std_tree_rightmost_zmq_ptr_node` | High | Walks right children until the `0x11` sentinel; used by the shared pointer-node erase helper. |
| `sub_40FA10` | `std_tree_prev_zmq_ptr_node` | High | Iterator predecessor over the same `0x10/0x11` color/sentinel pointer-node layout; used by duplicate-aware insert. |
| `sub_40FA70` | `std_tree_find_zmq_ptr_node_iter` | High | Linear iterator find over pointer-key payload `node[3]`; called by `own_t::process_term_req` before erasing an owned child. |
| `sub_40FAE0` | `std_tree_create_zmq_ptr_node` | High | Allocates a `0x14` node, initializes header links from the tree head, and stores the pointer key at `+0x0C`; called by `own_t::process_own` and other pointer-set owners. |
| `sub_416510` | `std_tree_erase_zmq_ptr_node_range` | High | Range erase wrapper that fast-clears whole pointer-node trees or erases each iterator through `std_tree_erase_zmq_ptr_node_iter`. |
| `sub_4166B0` | `std_tree_clear_zmq_ptr_node_tree` | High | Full tree clear/reset helper for the pointer-node family; frees subtrees, restores header self-links, and resets size to zero. |

## Observed Facts

- `own_t` construction allocates a `0x14` tree header, points its left, parent,
  and right links back at itself, sets both the color and sentinel bytes, and
  initializes the owned-set count to zero.
- `own_t::~own_t` erases the full `arg1[0x99]` tree range through
  `sub_416510`, then deletes the tree header.
- `own_t::process_own` inserts the child pointer through
  `sub_416700(&var_c, arg1 + 0x264, sub_40fae0(arg1 + 0x264))` while not
  terminating.
- `own_t::process_term_req` finds the child pointer through `sub_40fa70`,
  erases it through `sub_416020`, increments the pending termination-ack count,
  and sends command opcode `0xB` to the child object.
- `own_t::process_term` iterates the owned set, sends command opcode `0xB` to
  each child, folds the outstanding child count into `term_acks`, clears the
  tree through `sub_40f720`, resets the header links and count, marks
  `terminating`, and then calls `check_term_acks`.
- The node layout matches the Round 148 pointer family: left/parent/right at
  `0x00/0x04/0x08`, pointer key at `0x0C`, color at `0x10`, and sentinel at
  `0x11`.

## Source Reconstruction Shape

The retail behavior now supports this reconstructed container-level shape:

```cpp
class own_t : public object_t {
	std::set<own_t *> owned;
	bool terminating;
	int sent_seqnum;
	int processed_seqnum;
	int owner;
	int term_acks;

	void process_own(own_t *object)
	{
		if (!terminating) {
			owned.insert(object);
			return;
		}

		++term_acks;
		send_term(object, 0);
	}

	void process_term_req(own_t *object)
	{
		if (!terminating) {
			auto it = owned.find(object);
			if (it != owned.end()) {
				owned.erase(it);
				++term_acks;
				send_term(object, linger);
			}
		}
	}

	void process_term(int linger)
	{
		for (own_t *child : owned)
			send_term(child, linger);
		term_acks += owned.size();
		owned.clear();
		terminating = true;
		check_term_acks();
	}
};
```

The source sketch is intentionally container-level.  It identifies the STL
shape and lifecycle flow, while the exact field names and command-send helper
wrappers remain governed by the surrounding `object_t`/`own_t` aliases.

## Inference Boundary

- The helper aliases are STL/support-library names, not claims that these
  functions are source-authored ZMQ methods.
- `std_tree_create_zmq_ptr_node` is shared by several pointer-set owners.  The
  alias stays generic even though this pass used `own.cpp` as the strongest
  lifecycle witness.
- The reconstructed `send_term` name in the sketch is a semantic shorthand for
  the observed command opcode `0xB` send path; this pass does not promote a new
  dedicated send-helper alias for that inline sequence.

## Verification

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_own_ptr_tree_round_417_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

No runtime launch was needed; this was a static mapping pass over committed
HLIL/Ghidra evidence.

## Parity Estimate

- Focused ZMQ `own_t` owned pointer-set lifecycle confidence:
  **before 42% -> after 94%**.
- ZMQ-related source reconstruction confidence:
  **before 93.6% -> after 93.8%**.
- Overall Quake Live source parity:
  **before 55.80% -> after 55.81%**.
