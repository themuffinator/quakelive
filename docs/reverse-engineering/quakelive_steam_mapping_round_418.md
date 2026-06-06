# Quake Live ZMQ/CZMQ Mapping Round 418

Date: 2026-06-06

## Scope

This pass closes the ZMQ clock/thread support slab that connects the
already-mapped socket command paths, select poller, io-thread, and reaper
objects to their retail runtime scaffolding.  Earlier ZMQ passes named the
select/mailbox/signaler surface and the io-thread/reaper command handlers; this
round names the cached millisecond clock helper and the thread start/stop wrappers
those paths rely on.

Canonical evidence:

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- Static initializer/vtable evidence:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- Ghidra function inventory:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Companion passes:
  `docs/reverse-engineering/quakelive_steam_mapping_round_370.md`,
  `docs/reverse-engineering/quakelive_steam_mapping_round_376.md`

## Alias Reconstruction

This pass added 5 aliases:

| symbol | alias | confidence | evidence |
|---|---|---|---|
| `sub_40B9A0` | `zmq_clock_t_now_ms_cached` | High | Uses `_rdtsc` as a short-window cache guard and refreshes through the `data_12d3478` `GetTickCount64`/fallback function pointer; called by socket send/recv timeout loops and poller timing. |
| `sub_40BA00` | `zmq_thread_t_thread_routine` | High | `_beginthreadex` trampoline that calls the stored function pointer with the stored argument and returns `0`. |
| `sub_40BA20` | `zmq_thread_t_start` | High | Stores the poller loop function/argument pair, starts `_beginthreadex`, and asserts with `thread.cpp:0x33` on failure. |
| `sub_40BB30` | `zmq_thread_t_stop` | High | Joins the stored thread handle with `WaitForSingleObject`, closes it with `CloseHandle`, and asserts at `thread.cpp:0x39/0x3B` on failures. |
| `sub_52B070` | `zmq_clock_t_tickcount_lock_atexit` | High | Atexit cleanup for the critical section used by the `GetTickCount` fallback that backs `data_12d3478` when `GetTickCount64` is unavailable. |

## Observed Facts

- `sub_52aa00` loads `Kernel32.dll`, resolves `GetTickCount64`, and stores the
  result in `data_12d3478`.  If the function is unavailable, the initializer
  stores `sub_40b950` instead.
- `sub_40b950` is the fallback body: it enters `data_12d3460`, calls
  `GetTickCount`, increments a high-word wrap counter when the 32-bit tick value
  wraps, updates the last low tick value, and leaves the critical section.
- `sub_52a9e0` initializes the fallback lock and registers `sub_52b070` with
  `_atexit`; `sub_52b070` deletes that lock.
- `sub_40b9a0` caches the last TSC and last millisecond value in the caller's
  clock object.  If the TSC is zero it jumps directly to `data_12d3478`; if the
  cached TSC delta is within the small refresh window it returns the cached
  millisecond value; otherwise it refreshes from `data_12d3478`.
- `socket_base_t::send` and `socket_base_t::recv` use `sub_40b9a0` to compute
  absolute timeout deadlines and remaining wait intervals while processing
  commands.
- `ctx_t::create_socket` starts both the reaper select loop and each io-thread
  select loop through `sub_40ba20`.  `select_t::~select_t` joins the same
  thread wrapper through `sub_40bb30`.

## Source Reconstruction Shape

The retail runtime support now supports this reconstructed shape:

```cpp
class clock_t {
	uint64_t last_tsc;
	uint64_t last_time;

	uint64_t now_ms()
	{
		const uint64_t current_tsc = rdtsc();
		if (!current_tsc)
			return now_ms_unlocked();

		if (current_tsc >= last_tsc && current_tsc - last_tsc <= cache_window)
			return last_time;

		last_tsc = current_tsc;
		last_time = now_ms_unlocked();
		return last_time;
	}
};

class thread_t {
	void (*tfn)(void *);
	void *arg;
	HANDLE descriptor;

	static unsigned __stdcall thread_routine(void *arg)
	{
		thread_t *self = static_cast<thread_t *>(arg);
		self->tfn(self->arg);
		return 0;
	}

	void start(void (*tfn_)(void *), void *arg_)
	{
		tfn = tfn_;
		arg = arg_;
		descriptor = reinterpret_cast<HANDLE>(
			_beginthreadex(nullptr, 0, thread_routine, this, 0, nullptr));
		assert(descriptor);
	}

	void stop()
	{
		assert(WaitForSingleObject(descriptor, INFINITE) != WAIT_FAILED);
		assert(CloseHandle(descriptor));
	}
};
```

The thread entry function observed in this binary is the already-mapped
`zmq_select_t_loop_entry`, and the higher-level owners remain
`ctx_t`/`select_t` rather than the helpers themselves.

## Inference Boundary

- `sub_40b950` is not promoted as an alias in this round because the committed
  Ghidra function inventory does not expose it as a normal address-backed row.
  It is still used as direct HLIL evidence for the fallback path.
- The `_rdtsc` cache window is retained as an observed constant behavior rather
  than converted into a named timing policy; exact source spelling may differ.
- The thread wrappers are source-level ZMQ support helpers, but their failure
  text is produced through the already-mapped `err.cpp` Windows error helpers.

## Verification

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_clock_thread_round_418_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

No runtime launch was needed; this was a static mapping pass over committed
HLIL/Ghidra evidence.

## Parity Estimate

- Focused ZMQ clock/thread runtime wiring confidence:
  **before 48% -> after 93%**.
- ZMQ-related source reconstruction confidence:
  **before 93.8% -> after 94.0%**.
- Overall Quake Live source parity:
  **before 55.81% -> after 55.82%**.
