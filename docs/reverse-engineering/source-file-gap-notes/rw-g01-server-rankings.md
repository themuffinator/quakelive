# `src/code/server/sv_rankings.c` Divergence Note

Last updated: 2026-04-22

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Documented repo-wide divergence; default builds intentionally expose a retained rankings compatibility surface instead of a live service integration.

## Why this file remains a documented divergence

The default `!QL_ENABLE_RANKINGS` branch is explicit and useful, but it keeps the checked-in default build honest about not implementing retail-equivalent rankings behavior.

## Observed facts

- The disabled branch logs `Rankings disabled by build policy (QL_ENABLE_RANKINGS=0)` and forces `sv_enableRankings` back to `0` when requested.
- Most disabled-branch functions publish compatibility-safe return values or no-ops rather than a live rankings path.
- The live rankings implementation remains present under the enabled branch, but the repo-wide default policy keeps that surface outside closure.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `SV_GetRankingsProviderLabel` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_GetRankingsPolicyLabel` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RefreshRankingsPolicyCvars` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankPublishDisabledState` | `divergence owner` | Publishes the disabled compatibility state to cvars. |
| `SV_RankLogDisabledState` | `divergence owner` | Makes the build-disabled rankings policy explicit at runtime. |
| `SV_RankBegin` | `divergence owner` | Disabled-branch entry point forces the rankings surface back to compatibility-only behavior. |
| `SV_RankCheckInit` | `bounded compatibility` | Only reports the stub server-id state in disabled builds. |
| `SV_RankActive` | `bounded compatibility` | Hard-wired false in the disabled branch. |
| `SV_RankPoll` | `bounded compatibility` | No-op in the disabled branch. |
| `SV_RankUserStatus` | `bounded compatibility` | Returns compatibility-safe defaults in the disabled branch. |
| `SV_RankUserReset` | `bounded compatibility` | No-op compatibility branch. |
| `SV_RankReportInt` | `bounded compatibility` | No-op compatibility branch. |
| `SV_RankReportStr` | `bounded compatibility` | No-op compatibility branch. |
| `SV_RankBegin` | `divergence owner` | Disabled-branch entry point forces the rankings surface back to compatibility-only behavior. |
| `SV_RankEnd` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankPoll` | `bounded compatibility` | No-op in the disabled branch. |
| `SV_RankCheckInit` | `bounded compatibility` | Only reports the stub server-id state in disabled builds. |
| `SV_RankActive` | `bounded compatibility` | Hard-wired false in the disabled branch. |
| `SV_RankUserStatus` | `bounded compatibility` | Returns compatibility-safe defaults in the disabled branch. |
| `SV_RankUserGrank` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankUserReset` | `bounded compatibility` | No-op compatibility branch. |
| `SV_RankUserSpectate` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankUserCreate` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankUserLogin` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankUserValidate` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankUserLogout` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankReportInt` | `bounded compatibility` | No-op compatibility branch. |
| `SV_RankReportStr` | `bounded compatibility` | No-op compatibility branch. |
| `SV_RankQuit` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankNewGameCBF` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankUserCBF` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankJoinGameCBF` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankSendReportsCBF` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankCleanupCBF` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankCloseContext` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `least` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `least` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankEncodeGameID` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankDecodePlayerID` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankDecodePlayerKey` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankStatusString` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |
| `SV_RankError` | `bounded compatibility` | File member inside the retained rankings compatibility branch. |

## Maintenance expectations

- Keep rankings permanently documented as a bounded compatibility lane unless a real open replacement path is adopted.
- If the checked-in default branch changes, refresh the rankings note and repo-wide audit together.
