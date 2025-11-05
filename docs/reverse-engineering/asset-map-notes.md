# Asset map gaps

## Missing assets in baseq3 snapshot

- `/description.txt` (referenced 2×)
  - quakelive_steam.exe_hlil_part04.txt :: 0x004d1098 sub_4ecd40 -> "/description.txt"
  - quakelive_steam.exe_hlil_part06.txt :: 0x0052b2e0 sub_52b2e0 -> "/description.txt"
- `access.txt` (referenced 2×)
  - qagamex86.dll.bndb_hlil_part02.txt :: 0x1007b9a5 sub_100793a0 -> "access.txt"
  - qagamex86.dll.bndb_hlil_part03.txt :: global/data -> "access.txt"
- `autoexec.cfg` (referenced 2×)
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cc2a3 sub_4c7cf0 -> "exec autoexec.cfg\n"
  - quakelive_steam.exe_hlil_part06.txt :: 0x0052b2e0 sub_52b2e0 -> "exec autoexec.cfg\n"
- `gameinfo.txt` (referenced 1×)
  - uix86.dll_hlil_part01.txt :: 0x10021270 sub_10021270 -> "gameinfo.txt"
- `mappool.txt` (referenced 2×)
  - quakelive_steam.exe_hlil_part05.txt :: 0x004e3b10 sub_4ce0d0 -> "mappool.txt"
  - quakelive_steam.exe_hlil_part06.txt :: 0x0052b2e0 sub_52b2e0 -> "mappool.txt"
- `qzconfig.cfg` (referenced 6×)
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cb470 sub_4cb370 -> "qzconfig.cfg"
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cc1c5 sub_4cef10 -> "qzconfig.cfg"
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cc282 sub_4c7cf0 -> "exec qzconfig.cfg\n"
  - … 3 more references
- `repconfig.cfg` (referenced 4×)
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cb470 sub_4cb370 -> "repconfig.cfg"
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cc282 sub_4c7cf0 -> "exec repconfig.cfg\n"
  - quakelive_steam.exe_hlil_part06.txt :: 0x0052b2e0 sub_52b2e0 -> "repconfig.cfg"
  - … 1 more references
- `server.cfg` (referenced 2×)
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cc264 sub_4afbf0 -> "exec server.cfg\n"
  - quakelive_steam.exe_hlil_part06.txt :: 0x0052b2e0 sub_52b2e0 -> "exec server.cfg\n"
- `ui/testhud.menu` (referenced 2×)
  - cgamex86.dll_hlil_part01.txt :: 0x10025b54 sub_10025590 -> "ui/testhud.menu"
  - cgamex86.dll_hlil_part02.txt :: 0x10064260 sub_10064260 -> "ui/testhud.menu"
- `zmqpass.txt` (referenced 2×)
  - quakelive_steam.exe_hlil_part06.txt :: 0x0052b2e0 sub_52b2e0 -> "zmqpass.txt"
  - quakelive_steam.exe_hlil_part07.txt :: global/data -> "zmqpass.txt"

## Pattern or format-string references

- `%s.roq` (format string, 6×)
  - uix86.dll_hlil_part01.txt :: 0x10005680 sub_100053c0 -> "%s.roq"
  - uix86.dll_hlil_part01.txt :: 0x1000bb11 sub_10001900 -> "cinematic %s.roq 2\n"
  - uix86.dll_hlil_part01.txt :: 0x1000ef3e sub_10001900 -> "%s.roq"
  - … 3 more references
- `*q3dm*.bsp` (format string, 2×)
  - quakelive_steam.exe_hlil_part04.txt :: 0x004d1538 sub_4c9860 -> "example: fdir *q3dm*.bsp\n"
  - quakelive_steam.exe_hlil_part06.txt :: 0x0052b2e0 sub_52b2e0 -> "example: fdir *q3dm*.bsp\n"
- `maps/%s.bsp` (format string, 11×)
  - cgamex86.dll_hlil_part01.txt :: 0x10048ba9 sub_10057510 -> "maps/%s.bsp"
  - cgamex86.dll_hlil_part02.txt :: 0x10064260 sub_10064260 -> "maps/%s.bsp"
  - qagamex86.dll.bndb_hlil_part01.txt :: 0x10042af3 sub_10070cb0 -> "maps/%s.bsp"
  - … 8 more references
- `models/players/%s/animation.cfg` (format string, 4×)
  - cgamex86.dll_hlil_part01.txt :: 0x1003d500 sub_10057510 -> "models/players/%s/animation.cfg"
  - cgamex86.dll_hlil_part02.txt :: 0x10064260 sub_10064260 -> "models/players/%s/animation.cfg"
  - uix86.dll_hlil_part01.txt :: 0x100141d3 sub_10001830 -> "models/players/%s/animation.cfg"
  - … 1 more references
- `models/players/characters/%s/animation.cfg` (format string, 1×)
  - uix86.dll_hlil_part01.txt :: 0x10021270 sub_10021270 -> "models/players/characters/%s/animation.cfg"

## Strings without explicit asset path

- ".arena" (5 references)
  - quakelive_steam.exe_hlil_part02.txt :: 0x0045ecb4 sub_4d2d80
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cfab2 sub_4d9060
  - quakelive_steam.exe_hlil_part06.txt :: 0x0052b2e0 sub_52b2e0
  - … 2 more references
- ".cfg" (9 references)
  - quakelive_steam.exe_hlil_part04.txt :: 0x004c8720 sub_4d9a60
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cb533 sub_4d9a60
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cb5e5 sub_4d9a60
  - … 6 more references
- ".menu" (4 references)
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cfab2 sub_4d9060
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cf983 sub_4d9060
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cfd09 sub_4d9060
  - … 1 more references
- ".roq" (2 references)
  - uix86.dll_hlil_part01.txt :: 0x1000ac8f sub_100016c0
  - uix86.dll_hlil_part01.txt :: 0x10021270 sub_10021270
- ".txt" (2 references)
  - quakelive_steam.exe_hlil_part04.txt :: 0x004cfab2 sub_4d9060
  - quakelive_steam.exe_hlil_part06.txt :: 0x0052b2e0 sub_52b2e0
