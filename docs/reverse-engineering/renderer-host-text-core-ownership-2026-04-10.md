# Renderer Host Text Core Ownership Note

Last updated: 2026-04-10

This note records the renderer-owned host text-engine core now present in
writable source after `RG-P8`.

## Retail-Backed Host Text Core Behaviors

Observed facts now mirrored in source:

- `src/code/renderer/tr_font.c` owns a retained atlas named `*fontstash`
  through the normal renderer image or shader path.
- The retained atlas starts at `512 x 512`, uses the retail
  `R_fonsErrorCallback: error %d val %d\n` callback string, expands toward the
  retail `2048 x 1024` ceiling, and flushes once that ceiling is reached.
- The renderer now retains the five recovered host-text faces in one table:
  - `normal`
  - `sans`
  - `mono`
  - `sans-fallback`
  - `sans-windows-fallback`
- The dedicated Windows fallback face mirrors the retail host search order:
  `ARIALUNI.TTF`, `segoeui.ttf`, then `l_10646.ttf`.
- The retained core also tracks the recovered preferred face slots for the
  primary sans lane, the packaged fallback lane, and the Windows fallback lane.

Inference:

- The repo now has a direct renderer-owned lifetime for the retail host text
  core instead of only compatibility wrappers built on baked `fontInfo_t`.

## Downstream Closure

The `RG-P8` closure only covered the retained host-text core itself. The
downstream native-import switchover plus debug-atlas draw path were closed
separately in `RG-P9`; see
`docs/reverse-engineering/renderer-host-text-import-switchover-and-debug-atlas-2026-04-10.md`.

RG-P8 is now considered complete.
