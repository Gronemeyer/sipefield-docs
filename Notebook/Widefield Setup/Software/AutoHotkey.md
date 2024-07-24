Bash scripting for launching custom hotkeys and operating system commands

```AutoHotkey
; AutoHotkey script to run on startup
; Save this script as `startup_script.ahk` and place it in the startup folder
; You can find the startup folder by typing `shell:startup` in the Run dialog (Win+R)

; F3 hotkey action 
dir := "C:\dev\PyLab\pylab"
script  = %dir%\napari_acquisition_gui.py
F3::Run, %ComSpec% /k C:\Users\SIPE_LAB\anaconda3\envs\sipefield\python "%script%"
```
