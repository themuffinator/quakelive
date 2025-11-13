# Auto-hop regression check

These steps verify that holding the jump control with `pmove_AutoHop` enabled
produces consecutive takeoffs at the cadence enforced by the movement tuning
cvars.

## Setup

1. Launch a local server or start an offline practice match.
2. Open the server console and run the following commands to ensure auto-hop is
enabled and the jump window is easy to observe:

   ```text
   pmove_AutoHop 1
   pmove_BunnyHop 0
   pmove_JumpTimeDeltaMin 250
   pmove_JumpVelocity 275
   g_debugMove 2
   ```

   The `g_debugMove` toggle causes the server to print a `pmove_cfg` line once
   per frame. Confirm that the line includes `autoHop=1` and `bunnyHop=0` so the
   session is using the expected settings.

3. Bind a convenient key for jump if one is not already configured:

   ```text
   bind space +moveup
   ```

## Repro

1. Stand on level ground, press and hold `+moveup`, and add `+forward` to keep
momentum.
2. Watch the console output or enable `cg_drawSpeed 1` on the client to observe
that each landing immediately triggers another jump without releasing the key.
3. Adjust `pmove_JumpTimeDeltaMin` (for example, set it to `400`) and repeat.
   The gap between takeoffs should expand or shrink to match the configured
   window while continuous jumping remains possible.

When the fix regresses, the avatar will fail to take off on some landings while
`PMF_JUMP_HELD` remains set, or the console debug line will report `autoHop=1`
with no observable chained jumps.
