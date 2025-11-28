# `g_items` Unlock and Spawn Gating (qagamex86.dll HLIL)

This snapshot pulls the Binary Ninja HLIL emitted for the Quake Live `qagamex86.dll`
item helpers that gate pickups behind unlock tiers and server-level spawn toggles.

## Weapon Unlock Tier Lookup

`sub_10001840` dispatches on an item index (the `IT_WEAPON` slot number) and
indexes `lookup_table_10001900` to turn that index into a weapon class tier.
That tier then chooses the weapon name string returned to the caller. The table
encodes the unlock tier used by later gating code (values from `0x0` to `0x10`,
where `0x10` marks "no unlock tier").

| Item Index | Unlock Tier | Weapon Class |
| ---: | ---: | --- |
| 0 | 0 | Shotgun |
| 1 | 1 | Gauntlet |
| 2 | 2 | Machine Gun |
| 3–4 | 3 | Grenade Launcher |
| 5–6 | 4 | Rocket Launcher |
| 7–8 | 5 | Plasmagun |
| 9, 0x20 | 6 | Railgun |
| 0x0A, 0x1E | 7 | Lightning Gun |
| 0x0B–0x0C | 8 | BFG10K |
| 0x16 | 9 | Nailgun |
| 0x17 | 0x0A | Chaingun |
| 0x18 | 0x0B | Proximity Launcher |
| 0x19 | 0x0C | Kamikaze |
| 0x1A | 0x0D | Prox mine |
| 0x1B | 0x0E | Grapple |
| 0x1F | 0x0F | Heavy Machine Gun |
| others | 0x10 | [unknown weapon] |

## Server-Side Pickup Gating

`sub_10053400` consumes `g_spawnItemWeapon`, `g_spawnItemPowerup`, and
`g_spawnItemHoldable` server cvars and turns them into bitflags that control
whether the corresponding item classes can spawn (and thus be picked up). The
function probes each cvar name via `sub_10070a40` and, if the cvar is absent or
returns a non-zero match against the override list passed in `arg1 + 8`, sets a
bitmask on `ebp_1` to disable spawning for that class:

- Weapons: missing/blocked `g_spawnItemWeapon` sets `ebp_1 |= 0x400000`.
- Powerups: missing/blocked `g_spawnItemPowerup` follows the same path via the
  shared fall-through to `label_100545f8`.
- Holdables: similarly share the `label_100545f8` path when
  `g_spawnItemHoldable` is unavailable.

These masks are fed into the larger ruleset that prevents item pickups when the
corresponding spawn toggle is deactivated.
