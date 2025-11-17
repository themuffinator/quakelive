# Race Admin Workflow

This document summarizes how to manage the Race gametype checkpoints and how to
verify the new flow works end-to-end.

## Managing checkpoints

1. **Clear existing checkpoints** – use `racepoint clear` after enabling cheats
   (for example `/devmap` or `\nocheat`). This removes every `race_point` entity in the map and resets the
   `race_init` broadcast. The server console prints `clearing race points` when
   the wipe succeeds.
2. **Dump checkpoints** – run `racepoint dump` to emit each checkpoint index and
   origin. This mirrors the `admin_race_point_%i` output sent to clients and is
   useful when copying positions into a map script.
3. **Spawn checkpoints** – issue `racepoint` with no arguments while standing at
   the desired location. Each spawn:
   - Creates a `race_point` trigger.
   - Assigns it an incrementing index (0 = start, last index = finish).
   - Broadcasts `race_init <count>` so connected clients can rebuild their HUD
     widgets.
   - Sends `admin_race_point_%i <x> <y> <z>` to all clients so admins can copy
     the latest origin.
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
   line in the server console.
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
