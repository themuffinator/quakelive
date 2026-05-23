# Quake Live Steam Host Mapping Round 44

## Scope

This round closes the renderer skin-parser, video-mode, screenshot, and renderer-bootstrap helper band inside `quakelive_steam.exe`.

The newly promoted tranche is tightly grouped and source-shaped:

- the skin-only comma parser used by `RE_RegisterSkin`
- the renderer CVar range/assert helper and the video-mode query helpers
- the full screenshot and levelshot path, from command handlers down to the render-command payload writers
- the GL default-state, renderer-info, renderer registration, and OpenGL bootstrap helpers

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/renderer/tr_image.c`
- `src/code/renderer/tr_init.c`

## Exact Skin Parser Helper

### `sub_4478B0`: `CommaParse`

Observed local facts:

1. The helper skips leading whitespace, `//` comments, and `/* ... */` comments before emitting any token.
2. It treats `,` as a delimiter for unquoted tokens instead of using the regular Quake parser rules.
3. It preserves quoted-string parsing and returns an empty string on end-of-buffer.
4. `RE_RegisterSkin` at `0x004479C0` calls it twice per surface record in the exact `surface,shader` loop shape used by `tr_image.c`.

That is the exact skin parser helper `CommaParse`.

## Renderer CVar And Video-Mode Helpers

### `sub_447D50`: `AssertCvarRange`

Observed local facts:

1. The helper optionally checks `cv->integer` against `cv->value` and emits:
   - `WARNING: cvar '%s' must be integral (%f)\n`
2. It clamps below-minimum and above-maximum values with:
   - `WARNING: cvar '%s' out of range (%f < %f)\n`
   - `WARNING: cvar '%s' out of range (%f > %f)\n`
3. It rewrites the offending CVar via the same `Cvar_Set` pattern used by the local reconstructed clamp helper.
4. `R_Register` uses it immediately after registering `r_displayRefresh` and `r_picmip`, matching the reconstructed renderer clamp pass in `tr_init.c`.

The exact retail symbol name is still inferred, but the bounded role matches the local helper cleanly enough to promote `sub_447D50` as `AssertCvarRange`.

### `sub_447E40`: `GL_CheckErrors`

Observed local facts:

1. The helper calls `qglGetError()` and returns immediately on `GL_NO_ERROR`.
2. It honors the `r_ignoreGLErrors` CVar before doing any reporting.
3. It maps the exact OpenGL error constants to the same string set used by `tr_init.c`:
   - `GL_INVALID_ENUM`
   - `GL_INVALID_VALUE`
   - `GL_INVALID_OPERATION`
   - `GL_STACK_OVERFLOW`
   - `GL_STACK_UNDERFLOW`
   - `GL_OUT_OF_MEMORY`
4. It ends by raising the fatal error:
   - `GL_CheckErrors: %s`

That is the exact OpenGL error-check helper `GL_CheckErrors`.

### `sub_448010`: `R_GetModeInfo`

Observed local facts:

1. The helper rejects out-of-range mode indices below `-1` or past the mode table length.
2. For `mode == -1` it selects either the custom fullscreen pair or the windowed pair based on the final boolean argument.
3. It classifies custom dimensions into the same `r_aspectRatio` preset buckets used by the Win32 host (`16:9`, `16:10`, `4:3`, or `5:4`).
4. For table-backed modes it indexes the packed mode records and returns width, height, and the stored aspect preset from the retail table.

That is the exact video-mode query helper `R_GetModeInfo`.

### `sub_448110`: `R_GetMode`

Observed local facts:

1. When `r_fullscreen` is false and the windowed-mode CVar exists, the helper returns `r_windowedMode->integer`.
2. Otherwise it returns `r_mode->integer` when present.
3. When neither branch is usable it falls back to mode `3`.

That is the exact mode-selection helper `R_GetMode`.

### `sub_448160`: `R_ModeList_f`

Observed local facts:

1. `R_Register` wires the `"modelist"` command to `sub_448160`.
2. The helper prints a leading blank line, iterates the video-mode description table, prints each description with `%s\n`, then prints the trailing blank line.
3. That is the exact behavior of `tr_init.c::R_ModeList_f`.

`functions.csv` does not currently emit `0x00448160` as a function start, but the HLIL body and the registered command target make the helper stable enough to promote as `R_ModeList_f`.

## Exact Screenshot And Levelshot Helpers

### `sub_4481C0`: `RB_TakeScreenshot`

Observed local facts:

1. The helper allocates `vidWidth * vidHeight * 3 + 18` bytes and writes the same 24-bit TGA header fields used by `tr_init.c`.
2. It releases the post-process scene render target when active, reads back `GL_RGB` pixels, then rebinds the scene target.
3. It swaps RGB to BGR in-place across the captured payload.
4. It gamma-corrects the payload when overbright and hardware gamma are both active.
5. It writes the final file and frees the temp buffer.

That is the exact render-backend screenshot writer `RB_TakeScreenshot`.

### `sub_4482E0`: `RB_TakeScreenshotJPEG`

Observed local facts:

1. The helper allocates `vidWidth * vidHeight * 4` bytes.
2. It releases the post-process scene render target when active, reads `GL_RGBA` pixels, rebinds the scene target, and optionally gamma-corrects the buffer.
3. It writes a one-byte placeholder file to create the target path.
4. It calls the already-mapped `SaveJPG` helper at `0x00446880`.

That is the exact JPEG screenshot backend helper `RB_TakeScreenshotJPEG`.

### `sub_4483B0`: `RB_TakeScreenshotCmd`

Observed local facts:

1. The helper inspects the command payload flag at offset `0x18`.
2. It dispatches to the JPEG or TGA backend helper accordingly.
3. It returns `cmd + 1`, matching the render-command queue iterator convention.

That is the exact render-command wrapper `RB_TakeScreenshotCmd`.

### `sub_448410`: `R_ScreenshotFilename`

Observed local facts:

1. The helper clamps out-of-range screenshot numbers to `screenshots/shot9999.tga`.
2. Otherwise it decomposes the number into four decimal digits and formats:
   - `screenshots/shot%i%i%i%i.tga`

That is the exact TGA screenshot filename helper `R_ScreenshotFilename`.

### `sub_4484B0`: `R_ScreenshotFilenameJPEG`

Observed local facts:

1. The helper mirrors the TGA helper logic but formats the `.jpg` variant.
2. Its overflow path is:
   - `screenshots/shot9999.jpg`
3. Its regular path is:
   - `screenshots/shot%i%i%i%i.jpg`

That is the exact JPEG screenshot filename helper `R_ScreenshotFilenameJPEG`.

### `sub_448550`: `R_LevelShot`

Observed local facts:

1. The helper formats:
   - `levelshots/%s.tga`
   using `tr.world->baseName`.
2. It captures the full front buffer as RGB.
3. It downscales into a `128 x 128` TGA by averaging the same `4 x 3` source sample lattice used in `tr_init.c`.
4. It applies the same optional gamma correction, writes the TGA, frees both temp buffers, and prints:
   - `Wrote %s\n`

That is the exact levelshot generator `R_LevelShot`.

### `sub_4487F0`: `R_ScreenShot_f`

Observed local facts:

1. The helper special-cases the literal command arguments `levelshot` and `silent`.
2. In the `levelshot` case it dispatches to the now-closed `R_LevelShot`.
3. For explicit filenames it formats:
   - `screenshots/%s.tga`
4. For auto-numbered captures it walks the `R_ScreenshotFilename` sequence until `FS_FileExists` reports a free slot, preserving the same static `lastNumber` behavior.
5. It queues the screenshot command with the JPEG flag cleared and prints `Wrote %s\n` unless the `silent` path is active.

That is the exact screenshot console command `R_ScreenShot_f`.

### `sub_4489D0`: `R_ScreenShotJPEG_f`

Observed local facts:

1. The helper mirrors the TGA command path but formats:
   - `screenshots/%s.jpg`
2. It scans numbered filenames through `R_ScreenshotFilenameJPEG`.
3. It queues the screenshot command with the JPEG flag set.
4. It reuses the same `levelshot` and `silent` behavior as the TGA command.

That is the exact JPEG screenshot console command `R_ScreenShotJPEG_f`.

## Exact Renderer Bootstrap Helpers

### `sub_448BC0`: `GL_SetDefaultState`

Observed local facts:

1. The helper clears depth to `1.0f`, sets `GL_FRONT` culling, and sets the current color to white.
2. When multitexture is available it initializes texture unit `1`, applies `GL_TextureMode`, sets `GL_MODULATE`, disables `GL_TEXTURE_2D`, and returns to texture unit `0`.
3. It enables `GL_TEXTURE_2D`, reapplies the texture mode, sets `GL_MODULATE`, `GL_SMOOTH`, and `GL_LEQUAL`.
4. It enables the vertex array client state and seeds the same initial GL state bits as `tr_init.c`.
5. It finishes with the same polygon/depth/scissor/cull/blend state sequence used by the source.

That is the exact renderer default-state initializer `GL_SetDefaultState`.

### `sub_448CE0`: `GfxInfo_f`

Observed local facts:

1. The helper queries `sys_cpustring` and prints the exact graphics-information banner family:
   - `GL_VENDOR`
   - `GL_RENDERER`
   - `GL_VERSION`
   - `GL_EXTENSIONS`
   - `GL_MAX_TEXTURE_SIZE`
   - `GL_MAX_ACTIVE_TEXTURES_ARB`
2. It prints mode, refresh, gamma mode, CPU string, primitive mode, texture mode, picmip, texture bits, and the extension enable lines in the same order as `tr_init.c`.
3. It retains the same hardware-specific hack notices for vertex light, Rage Pro, and Riva 128.
4. It prints the dual-processor acceleration and forced-`glFinish` lines under the same conditions as the source.

That is the exact renderer info command `GfxInfo_f`.

### `sub_449000`: `R_Register`

Observed local facts:

1. The helper registers the full renderer CVar block, including the Quake Live post-process and bloom additions.
2. It immediately applies the same range assertion helper to `r_displayRefresh` and `r_picmip`.
3. It adds the exact command set later mirrored by the source:
   - `imagelist`
   - `shaderlist`
   - `skinlist`
   - `modellist`
   - `modelist`
   - `screenshot`
   - `screenshotJPEG`
   - `gfxinfo`
4. The command targets line up with the newly promoted screenshot, mode-list, and gfx-info helpers.

That is the exact renderer CVar-and-command registration entry point `R_Register`.

### `sub_44A150`: `InitOpenGL`

Observed local facts:

1. The helper only calls the platform GL init path when `glConfig.vidWidth == 0`.
2. In that bootstrap path it calls the platform GL init helper, lowercases the renderer string copy, queries `GL_MAX_TEXTURE_SIZE`, and clamps broken `<= 0` reports back to zero.
3. It initializes the command buffers after the platform setup.
4. It then calls the newly closed `GfxInfo_f` and `GL_SetDefaultState`.

That is the exact OpenGL bootstrap helper `InitOpenGL`.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4478B0` (`0x004478B0`) | `CommaParse` | Observed | Exact skin-only comma parser used by `RE_RegisterSkin`. |
| `sub_447D50` (`0x00447D50`) | `AssertCvarRange` | Observed plus bounded inference | Renderer CVar clamp/assert helper used by the Quake Live registration path. |
| `sub_447E40` (`0x00447E40`) | `GL_CheckErrors` | Observed | Exact OpenGL error-check helper. |
| `sub_448010` (`0x00448010`) | `R_GetModeInfo` | Observed | Exact video-mode dimension/aspect query helper. |
| `sub_448110` (`0x00448110`) | `R_GetMode` | Observed | Exact current-mode selector. |
| `sub_448160` (`0x00448160`) | `R_ModeList_f` | Observed | HLIL-only mode-list console command helper registered by `R_Register`. |
| `sub_4481C0` (`0x004481C0`) | `RB_TakeScreenshot` | Observed | Exact TGA screenshot backend helper. |
| `sub_4482E0` (`0x004482E0`) | `RB_TakeScreenshotJPEG` | Observed | Exact JPEG screenshot backend helper. |
| `sub_4483B0` (`0x004483B0`) | `RB_TakeScreenshotCmd` | Observed | Exact render-command screenshot dispatcher. |
| `sub_448410` (`0x00448410`) | `R_ScreenshotFilename` | Observed | Exact numbered TGA screenshot filename formatter. |
| `sub_4484B0` (`0x004484B0`) | `R_ScreenshotFilenameJPEG` | Observed | Exact numbered JPEG screenshot filename formatter. |
| `sub_448550` (`0x00448550`) | `R_LevelShot` | Observed | Exact levelshot generator. |
| `sub_4487F0` (`0x004487F0`) | `R_ScreenShot_f` | Observed | Exact TGA screenshot console command. |
| `sub_4489D0` (`0x004489D0`) | `R_ScreenShotJPEG_f` | Observed | Exact JPEG screenshot console command. |
| `sub_448BC0` (`0x00448BC0`) | `GL_SetDefaultState` | Observed | Exact renderer default-state initializer. |
| `sub_448CE0` (`0x00448CE0`) | `GfxInfo_f` | Observed | Exact renderer info console command. |
| `sub_449000` (`0x00449000`) | `R_Register` | Observed | Exact renderer CVar and command registration entry point. |
| `sub_44A150` (`0x0044A150`) | `InitOpenGL` | Observed | Exact OpenGL bootstrap helper. |

## Coverage Impact

On the committed `quakelive_steam.exe` Ghidra baseline of `5473` functions, this pass moves the explicit address-backed `quakelive_steam` alias set from `424` to `442` functions, which is approximately `7.7%` to `8.1%` host-symbol coverage.

The raw alias table also moves from `425` to `443` entries. The one-entry difference between those totals and the address-backed counts is the existing non-address export alias `__initp_misc_invarg -> RE_SetWorldVisData`.

## Open Questions

1. `R_ModeList_f` is stable from HLIL and command registration, but the committed `functions.csv` still omits `0x00448160` as a function start.
2. `AssertCvarRange` is the only name in this round that remains slightly synthetic. The behavior and call pattern are solid; the exact original retail spelling is still inferred from the local reconstruction.
3. The next clean continuation after this pass is the remaining renderer bootstrap and post-process helper band immediately above `InitOpenGL`, especially the Quake Live-specific post-process state/update path.
