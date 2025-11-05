# Documentation Backlog

This backlog tracks upcoming documentation work required to keep contributors aligned as Quake Live parity improves.

## Behavioural Deltas
- **Gameplay Parity Ledger:** A living changelog that records intentional deviations between Quake III baseline behaviour and the Quake Live target (e.g., weapon tuning, spawn logic). Each entry should cross-reference the relevant tests and code paths.
- **Regression Rationale Templates:** Provide a standard template contributors must fill out when documenting a behaviour delta, including reproduction steps, affected assets, and baseline updates.
- **Mapping Table Updates:** Extend `docs/reference-mapping.md` with explicit callouts linking HLIL-derived functions to their reconstructed counterparts when behaviour diverges.

## Outstanding Platform Gaps
- **Toolchain Availability Matrix:** Document host OS requirements for both the legacy QVM toolchain and the native DLL toolset (Visual Studio 2010), including installation guides and known limitations.
- **32-bit Runtime Notes:** Capture the quirks of running 32-bit DLLs on modern Windows (WOW64 considerations, dependency installation) and how to validate runtime environments.
- **Linux/Mac Support Status:** Summarise current efforts (or lack thereof) for non-Windows native builds, highlighting missing syscalls, rendering paths, or platform shims.

## HUD and Menu Follow-Ups
- **UI Asset Audit:** Catalogue outstanding HUD/menu elements that differ from Quake Live (fonts, icons, layout). Include screenshots or HLIL references where available.
- **Menu Scripting Guide:** Expand on how the reconstructed UI scripts map to Quake Live behaviour, noting missing cvars, commands, or localisation entries.
- **Accessibility and Scalability Tasks:** Track plans for resolution scaling, colourblind modes, and other HUD usability improvements flagged during testing.

## Accessibility Backlog
1. **Restore metadata-driven widgets.** Import the missing Quake Live text tables (`country.txt`, `teaminfo.txt`, `hud3.txt`) so spectator overlays and locale pickers regain full context before further accessibility work begins.【F:docs/ui/hud-audit.md†L6-L18】
2. **Package high-contrast HUD art.** Stage and ship the `ui/assets` imagery alongside updated fonts/shaders to preserve dual-encoded color + numeric cues relied on by colorblind players.【F:docs/ui/hud-audit.md†L6-L18】【F:docs/ui/scripting-guide.md†L18-L22】
3. **Plan scalable layout controls.** Extend HUD scripting to keep widescreen groupings intact while preparing for adjustable UI scale sliders and font reflow, ensuring future options improve readability without breaking layout logic.【F:docs/ui/scripting-guide.md†L12-L22】

Maintainers should review and update this backlog as features land, ensuring newcomers can quickly locate the most pressing documentation gaps.
