"""The Windows desktop: screenshots, monitors, windows, menus, notifications.

Everything is in physical pixels (the process is made DPI-aware first). The screenshot is the whole virtual desktop,
so ORIGIN is where its top-left corner sits on the desktop (negative when a monitor lies left of or above the main one);
monitors and windows are returned in screenshot pixels, the pointer in desktop pixels.
"""
import ctypes
import subprocess
import sys
import threading
import time
from ctypes import wintypes
from pathlib import Path

from PIL import ImageGrab

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # per-monitor: screenshots, windows and the pointer all in real pixels
except (AttributeError, OSError):
    pass

user32, dwm = ctypes.windll.user32, ctypes.windll.dwmapi
NO_WINDOW = 0x08000000  # CREATE_NO_WINDOW: no console flashing up when started from pythonw
PICKER = Path(__file__).with_name('picker.py')
ORIGIN = (0, 0)
SKIP = {'Progman', 'WorkerW', 'Shell_TrayWnd', 'Shell_SecondaryTrayWnd', 'Windows.UI.Core.CoreWindow'}


class Oops(Exception):
    """A problem you can fix: shown as a plain notification, no traceback."""


class MONITORINFO(ctypes.Structure):
    _fields_ = [('cbSize', wintypes.DWORD), ('rcMonitor', wintypes.RECT), ('rcWork', wintypes.RECT), ('dwFlags', wintypes.DWORD)]


ENUM_MONITORS = ctypes.WINFUNCTYPE(wintypes.BOOL, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
ENUM_WINDOWS = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.GetForegroundWindow.restype = wintypes.HWND
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.IsWindowVisible.argtypes = user32.IsIconic.argtypes = user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.EnumDisplayMonitors.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ENUM_MONITORS, wintypes.LPARAM]
user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MONITORINFO)]
user32.EnumWindows.argtypes = [ENUM_WINDOWS, wintypes.LPARAM]
dwm.DwmGetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]


def notify(msg, ms=None, critical=False, title='penmentor'):
    """A message box (always on top). With ms it waits on a thread, so the caller carries on."""
    box = lambda: user32.MessageBoxW(None, msg, title, (0x10 if critical else 0x40) | 0x40000 | 0x10000)  # icon, topmost, foreground
    threading.Thread(target=box).start() if ms else box()


def virtual():
    """The whole desktop (x, y, w, h)."""
    return tuple(user32.GetSystemMetrics(i) for i in (76, 77, 78, 79))  # SM_[XY]VIRTUALSCREEN, SM_CX/CYVIRTUALSCREEN


def monitors():
    """Work areas (x, y, w, h) in desktop pixels, left to right: the taskbar is not part of them."""
    out = []

    @ENUM_MONITORS
    def each(hmon, dc, rect, data):
        info = MONITORINFO(cbSize=ctypes.sizeof(MONITORINFO))
        if user32.GetMonitorInfoW(hmon, ctypes.byref(info)):
            r = info.rcWork
            out.append((r.left, r.top, r.right - r.left, r.bottom - r.top))
        return True
    user32.EnumDisplayMonitors(None, None, each, 0)
    return sorted(out)


def windows():
    """Visible, titled top-level windows (x, y, w, h) in desktop pixels, front first, and the focused one's rect (or None)."""
    wins, focus, fg = [], None, user32.GetForegroundWindow()

    @ENUM_WINDOWS
    def each(hwnd, data):
        nonlocal focus
        if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd) or not user32.GetWindowTextLengthW(hwnd):
            return True
        cloaked = wintypes.DWORD()  # a UWP app's ghost, or a window on another virtual desktop
        dwm.DwmGetWindowAttribute(hwnd, 14, ctypes.byref(cloaked), 4)
        cls = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls, 256)
        if cloaked.value or cls.value in SKIP or user32.GetWindowLongW(hwnd, -20) & 0x80:  # GWL_EXSTYLE & WS_EX_TOOLWINDOW
            return True
        r = wintypes.RECT()  # the visible frame, without the invisible resize border Windows adds
        if dwm.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(r), ctypes.sizeof(r)):
            user32.GetWindowRect(hwnd, ctypes.byref(r))
        rect = (r.left, r.top, r.right - r.left, r.bottom - r.top)
        if rect[2] >= 100 and rect[3] >= 100 and rect not in wins:
            wins.append(rect)
            if hwnd == fg:
                focus = rect
        return True
    user32.EnumWindows(each, 0)
    return wins, focus


def capture():
    """Everything on screen: (desktop image, monitors left to right, index of the focused one, visible windows),
    the last two lists in image pixels. Sets ORIGIN."""
    global ORIGIN
    try:
        shot = ImageGrab.grab(all_screens=True).convert('RGB')
    except OSError:
        raise Oops('Could not take a screenshot.')
    vx, vy, _, _ = virtual()
    ORIGIN = (vx, vy)
    wins, focus = windows()
    if not wins:
        raise Oops('Nothing on screen to look at. Open OneNote, then press the key again.')
    shift = lambda r: (r[0] - vx, r[1] - vy, r[2], r[3])
    screens = [shift(m) for m in monitors()] or [(0, 0, *shot.size)]
    if focus is None:
        p = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(p))
        focus = (p.x, p.y, 1, 1)
    cx, cy = focus[0] - vx + focus[2] / 2, focus[1] - vy + focus[3] / 2
    main = next((i for i, (x, y, w, h) in enumerate(screens) if x <= cx < x + w and y <= cy < y + h), 0)
    return shot, screens, main, [shift(w) for w in wins]


def active_window():
    """The focused window, to hand the focus back later, or None."""
    return user32.GetForegroundWindow() or None


def activate(window):
    """Give the focus back to the app after a picker had the keyboard."""
    if window:
        user32.keybd_event(0x12, 0, 0, 0)  # an Alt tap: Windows refuses SetForegroundWindow without a recent key press
        user32.keybd_event(0x12, 0, 2, 0)
        user32.SetForegroundWindow(window)


def pointer():
    """(x, y, held) of the mouse or pen anywhere on the desktop (held: the button or the pen tip is down), or None.
    The marks' window is only their own pixels, so the pointer is mostly over OneNote: this asks Windows directly."""
    p = wintypes.POINT()
    if not user32.GetCursorPos(ctypes.byref(p)):
        return None
    return p.x, p.y, bool(user32.GetAsyncKeyState(0x01) & 0x8000)  # VK_LBUTTON: Windows Ink pen taps count


def on_escape(callback):
    """callback() on a thread whenever Escape is pressed, wherever the focus is (the key still reaches your apps),
    so Esc stops penmentor while the model thinks."""
    def watch():
        was = False
        while True:
            down = bool(user32.GetAsyncKeyState(0x1B) & 0x8000)
            if down and not was:
                callback()
            was = down
            time.sleep(.03)
    threading.Thread(target=watch, daemon=True).start()


def picker(*args, input=''):
    p = subprocess.run([sys.executable, '-I', str(PICKER), *args], input=input, capture_output=True, text=True,
                       encoding='utf-8', creationflags=NO_WINDOW)
    return p.stdout.strip() if p.returncode == 0 else None


def rofi(options, prompt):
    """The picked (or typed) row, None on Esc. No options: a plain text box. (Named for the Linux original's menu.)"""
    return picker('menu', prompt, input='\n'.join(options))


def select_region(geom):
    """Drag a box on the desktop: (x0, y0, x1, y1) in screenshot pixels, None on Esc."""
    out = picker('region')
    if not out:
        return None
    x, y, w, h = map(int, out.split())
    return (x - geom[0], y - geom[1], x - geom[0] + w, y - geom[1] + h)
