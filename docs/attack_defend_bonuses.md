# Attack & Defend scoring bonuses

Quake Live's Attack & Defend rules award round score for three distinct actions:

* **Touches** – attackers earn a bonus as soon as they secure the defender's flag.
* **Eliminations** – every frag against the opposing team increments the round score.
* **Captures** – sealing the objective after a touch yields the largest bump.

This repository now exposes three server cvars so admins can tune those values to match the reference DLL defaults that were recovered from the HLIL dumps:

| Cvar | Default | Description |
| ---- | ------- | ----------- |
| `g_adTouchScoreBonus` | `1` | Additional team + personal score applied when an attacker first touches the enemy flag. |
| `g_adElimScoreBonus` | `2` | Extra points granted to both the attacker and their team for each enemy frag while playing Attack & Defend. |
| `g_adCaptureScoreBonus` | `3` | Bonus stacked on top of the normal capture point that is issued when the flag is secured. |

The defaults above mirror the strings captured inside the Quake Live HLIL output (`data_1007d1d8` = `"1"`, `data_1007d53c` = `"2"`, `data_100874e0` = `"3"`), so changing them is only required if you want to experiment with alternative scoring curves.

Each bonus updates both the individual scoreboard entry and the Attack & Defend team totals via `AddScore`/`AddTeamScore`. The helpers also centerprint the team-specific announcements ("Touch bonus", "Elimination bonus", "Capture bonus") so players get instant feedback whenever a configured bonus fires.

## Tuning workflow

1. Set the three cvars in your server config (or via `seta` at runtime) before the match loads. All of them are archived and published through serverinfo.
2. Verify the new values with `\cvarlist adScore` or `\cg_scoreboard 1` while the game is running; the centerprint confirms the bonus amount applied.
3. Restart the map if you change the multipliers mid-match so both the server and connected clients stay in sync with the scoreboard math.

Because the scoring helper short-circuits outside of `GT_ATTACK_DEFEND`, the cvars are harmless to adjust in other modes and make it easy to reproduce the HLIL defaults should they ever be modified.
