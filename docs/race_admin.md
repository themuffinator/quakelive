# Race Admin Workflow

This document summarizes how to manage the Race gametype checkpoints and how to
verify the new flow works end-to-end.

## Managing checkpoints

1. **Clear existing checkpoints** – use `racepoint clear` after enabling cheats
   (for example `/devmap` or `\nocheat`). This removes every `race_point` entity in the map and resets the
   `race_init` broadcast. Every client receives `clearing race points` when
   the wipe succeeds.
2. **Dump checkpoints** – run `racepoint dump` to emit each checkpoint origin as
   a plain `x y z` print. This mirrors the retail admin dump flow and
   is useful when copying positions into a map script.
3. **Spawn checkpoints** – issue `racepoint` with no arguments while standing at
   the desired location. Each spawn:
   - Creates a `race_point` trigger just below the admin's feet, matching the
     retail `z - 8` placement path.
   - Assigns it an `arpN` targetname and links the previously spawned admin
     checkpoint to that target so the chain stays deterministic.
   - Broadcasts bare `race_init` so connected clients rebuild their race HUD
     state.
   - Rebroadcasts the current checkpoint metadata with the retail `arpN`
     target/targetname chain.
4. **Map support** – checkpoints can also be authored directly in `.map` files
   via the `race_point` classname once `g_spawn.c` registers the entity. Mixing
   map-placed points and admin-spawned points is supported, though `racepoint
   clear` wipes both to keep the list deterministic.

## Testing checklist

Follow these manual steps after touching any race-related code:

1. Launch a local Race server (e.g., `/map <levelname>; set g_gametype 10;
   map_restart`).
2. Clear checkpoints (`racepoint clear`), spawn at least three points (start,
   mid, finish), and confirm that each spawn prints the `admin_race_point_%i`
   line with the expected `arpN` target chain.
3. Run through the checkpoints. Watch for the console message
   `"<name> finished the race in <mm:ss.mmm>"` and ensure a second finish with a
   slower time does **not** print `^1Personal best!`.
4. Query the scoreboard with the `score` command and confirm the server replies
   with the `scores_race` payload instead of the legacy `scores` string.
5. Connect a second client (or use `/clientkick` to force a reconnect) and
   verify that joining players receive the latest `race_init` + `race_info`
   configstrings immediately.

Documenting the workflow ensures future changes keep the admin UX intact without
requiring a dedicated QA pass every time the race controller is touched.
