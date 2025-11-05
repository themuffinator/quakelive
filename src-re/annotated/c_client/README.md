# Annotated Client Frame Loop

This directory mirrors the pieces of the Quake Live client that govern
`CL_Frame`, snapshot interpolation, and HUD drawing.  Each translation unit
introduces lightweight shadow structs that capture only the fields touched by
the original routines so the control flow can be studied or replayed without the
full engine dependencies.

* `cl_frame.c` – frame pump skeleton with menu activation, time-step handling,
  and hooks for console/snapshot/service routines.  The trailing comment blocks
  list the renderer, sound, and UI DLL entry points that need stubbing when
  hosted outside the original engine.
* `cl_snapshot.c` – annotated versions of `CL_AdjustTimeDelta`,
  `CL_FirstSnapshot`, and `CL_SetCGameTime` written against the shared shadow
  types.  Hook tables document the error/print/demo services that still need to
  be provided by a harness.
* `cl_hud.c` – resolution-independent HUD helpers (`SCR_AdjustFrom640` and
  friends) with a flattened renderer interface; comments capture the OpenGL
  calls the real renderer issues.
* `client_math.h`, `client_offsets.h`, and `client_types.h` – supporting headers
  that document structure sizes/offsets and small math helpers that the annotated
  code relies on.

The goal is to make the high-level client control flow available for
experimentation (e.g. tooling or prototype front-ends) while clearly documenting
where real Quake Live DLL interactions must be emulated.
