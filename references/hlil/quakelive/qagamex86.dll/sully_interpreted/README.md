# Sully-Interpreted HLIL Snapshots for `qagamex86.dll`

The files under this directory reinterpret the raw Binary Ninja HLIL export for
Quake Live's dedicated gameplay DLL through the lens of the original Quake III
Arena `game` module.  Each write-up focuses on surfacing:

* The canonical Quake III symbol or subsystem that the stripped Quake Live
  function maps back to.
* Key structural offsets that appear in the HLIL and how they line up with the
  public GPL sources (`g_local.h`, `g_client.c`, `g_main.c`, etc.).
* Behavioural deltas that Quake Live introduced (for example, Steam auth
  plumbing, persistent stat resets, and expanded client state).

The goal is to provide a quick "Sully pass"—a terminology the team uses for a
first-principles translation pass that blends HLIL control flow with domain
knowledge—so future reconstruction work can trace the intent of each routine
without wading through raw auto-generated text dumps.

## Layout

```
functions/
  g_main/      # Frame loop and level lifecycle helpers
  g_client/    # Client handshake, persistence, and spawn helpers
structs/        # Structures inferred from HLIL array math
```

All addresses reference the Quake Live retail `qagamex86.dll` (PE base
`0x10000000`).
