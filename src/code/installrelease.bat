cd game
call game_ta
call game
cd ..\cgame
call cgame_ta
call cgame
cd ..\ui
call ui
cd ..
call closefiles
copy release_ta\quake3.exe g:\quake3\quake3.exe
call installvms