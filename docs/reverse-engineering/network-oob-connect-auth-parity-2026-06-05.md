# Network OOB Connect/Auth Parity - 2026-06-05

## Scope

This note is the human-readable companion for
`docs/reverse-engineering/network-oob-connect-auth-parity-2026-06-05.json`.
It closes the Medium implementation-plan entry in
`docs/plans/2026-06-05-networking-2.md`: audit OOB/connect/auth behavior and
confirm whether any retail path applies compression beyond raw OOB primitives.

No runtime launch was required. This pass used static source inspection plus
the committed retail HLIL and symbol-alias corpus.

## Evidence Used

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed reference corpus:

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`

Writable source inspected:

- `src/code/qcommon/msg.c`
- `src/code/qcommon/huffman.c`
- `src/code/qcommon/common.c`
- `src/code/qcommon/net_chan.c`
- `src/code/client/cl_main.c`
- `src/code/server/sv_main.c`

## Result

The OOB rule is now explicit: ordinary OOB traffic stays raw. The only
profile-91 Huffman exception found in the source and committed retail HLIL is
the client `connect` request body after the clear `connect ` prefix.

| Lane | Sender | Encoding | Retail/source conclusion |
| --- | --- | --- | --- |
| Text OOB commands such as `getinfo`, `getstatus`, `disconnect`, `rcon`, `heartbeat`, responses | `NET_OutOfBandPrint` | Raw bytes after `0xffffffff` | No Huffman step. |
| Steam auth `getchallenge` payload | `CL_BuildSteamChallengeRequest` -> `NET_OutOfBandRaw` | Raw binary bytes after `0xffffffff` | No Huffman step; live platform auth remains build/policy gated. |
| Fallback `getchallenge` | `NET_OutOfBandPrint` | Raw text | No Huffman step. |
| `connect "%s"` userinfo | `CL_CheckForResend` -> `NET_OutOfBandData` | Clear `connect ` through offset `11`, Huffman from offset `12` | The narrow compressed-connect exception. |
| Legacy Q3 authorize commands | `NET_OutOfBandPrint` | Raw text | Disabled for `NETPROFILE_QL_RETAIL`; raw if another profile enables it. |

## Retail Anchors

| Retail symbol | Address | Observation |
| --- | --- | --- |
| `MSG_WriteBits` | `0x004D4AF0` | OOB branch writes direct 8/16/32-bit values; Huffman helpers are in the non-OOB branch. |
| `MSG_ReadBits` | `0x004D4C70` | OOB branch reads direct 8/16/32-bit values; Huffman helpers are in the non-OOB branch. |
| `MSG_BeginReadingOOB` | `0x004D4A80` | Resets read counters and sets the OOB flag. |
| `MSG_InitOOB` | `0x004D6C50` | Initializes `msg_t` storage and sets the OOB flag. |
| `Huff_Decompress` | `0x004D3E60` | Retail server path calls this with offset `0x0c` only after identifying a clear `connect` token. |
| `Huff_Compress` | `0x004D40F0` | Retail `NET_OutOfBandData` calls this with offset `0x0c`. |
| `CL_CheckForResend` | `0x004B9150` | Uses `NET_OutOfBandData` for `connect`; sends Steam `getchallenge` as a raw OOB buffer. |
| `NET_OutOfBandPrint` | `0x004D7080` | Writes four `0xff` bytes and sends raw formatted bytes. |
| `NET_OutOfBandData` | `0x004D7120` | Writes four `0xff` bytes, copies payload, compresses from offset `0x0c`, then sends. |
| `SV_ConnectionlessPacket` | `0x004E4340` | Checks clear `connect` bytes at offset `4` and decompresses from offset `0x0c` before tokenizing. |

## Assertions Added

The parity manifest test now verifies:

- `MSG_InitOOB` and `MSG_BeginReadingOOB` set `msg->oob`.
- OOB scalar read/write branches use raw byte/word/dword operations and keep
  Huffman helpers in the non-OOB branch.
- `NET_OutOfBandPrint` and `NET_OutOfBandRaw` never call `Huff_Compress`.
- Steam auth `getchallenge` uses `NET_OutOfBandRaw`; fallback challenge uses
  `NET_OutOfBandPrint`.
- `NET_OutOfBandData` remains the compressed connect helper and compresses at
  offset `12`.
- Server decompression remains guarded by
  `NET_ProtocolUsesCompressedConnect() && NET_IsConnectRequestPacket(msg)`.
- Retail HLIL contains the same offset-`0x0c` compression/decompression and
  raw challenge split.

## Residual Risks

No source patch was required. Remaining risk is limited to evidence that is not
committed in this repository:

- There is still no retail packet capture for byte-for-byte compressed connect
  comparison.
- Live Steam platform auth remains a documented online-service divergence
  unless `QL_BUILD_ONLINE_SERVICES` is enabled.

Estimated parity movement for this task:

- Focused OOB/connect/auth slice: `62%` before, `90%` after.
- Overall network-protocol parity: `84%` before, `85%` after.
