; AutoHotkey v2. Double-click to run; keep it running (or put a shortcut in shell:startup).
; Adjust the path if penmentor is not pip-installed: use  pythonw "C:\path\to\penmentor-onenote\bin\penmentor"
F9::Run 'pythonw -m penmentor', , 'Hide'                  ; the menu; with marks up, opens their menu
F10::Run 'pythonw -m penmentor --ask check', , 'Hide'     ; straight to "check new work"
