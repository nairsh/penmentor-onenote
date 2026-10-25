"""The menu and the region selector for penmentor on Windows (what rofi and slop were on Linux). Run as a script, standard
library only, so it starts fast:

  picker.py menu PROMPT    rows on stdin; prints the picked row, or the typed text; exit 1 on Esc
  picker.py region         drag a box on the desktop; prints "x y w h" in desktop pixels; exit 1 on Esc or a tap
"""
import ctypes
import sys
import tkinter as tk

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except (AttributeError, OSError):
    pass
user32 = ctypes.windll.user32
BG, FG = '#16161a', '#e6e6e6'


def front(root):
    user32.keybd_event(0x12, 0, 0, 0)  # an Alt tap lets a window take the foreground from the app that started it
    user32.keybd_event(0x12, 0, 2, 0)
    root.attributes('-topmost', True)
    root.focus_force()


def menu(prompt, rows):
    root = tk.Tk()
    root.title(f'penmentor · {prompt}')
    root.configure(bg=BG)
    var, shown, out = tk.StringVar(), [], []
    entry = tk.Entry(root, textvariable=var, font=('Segoe UI', 14), bg='#222228', fg=FG, insertbackground=FG, relief='flat')
    entry.pack(fill='x', padx=10, pady=(10, 6), ipady=6)
    box = tk.Listbox(root, font=('Segoe UI', 13), bg=BG, fg=FG, selectbackground='#2f6fde', activestyle='none', relief='flat',
                     highlightthickness=0, width=48, height=min(max(len(rows), 1), 14))
    if rows:
        box.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def refill(*_):
        q = var.get().lower()
        shown[:] = [r for r in rows if q in r.lower()]
        box.delete(0, 'end')
        box.insert('end', *shown)
        if shown:
            box.selection_set(0)

    def pick(typed=False):
        sel = box.curselection()
        out.append(var.get().strip() if typed or not shown or not sel else shown[sel[0]])
        root.destroy()

    def move(d):
        sel = box.curselection()
        if shown:
            i = max(0, min((sel[0] if sel else -1) + d, len(shown) - 1))
            box.selection_clear(0, 'end')
            box.selection_set(i)
            box.see(i)
        return 'break'

    var.trace_add('write', refill)
    refill()
    root.bind('<Return>', lambda e: pick())
    root.bind('<Shift-Return>', lambda e: pick(True))  # your own words, even when a row matches them
    root.bind('<Escape>', lambda e: root.destroy())
    root.bind('<Down>', lambda e: move(1))
    root.bind('<Up>', lambda e: move(-1))
    box.bind('<Double-Button-1>', lambda e: pick())
    root.update_idletasks()
    w, h = root.winfo_reqwidth(), root.winfo_reqheight()
    root.geometry(f'+{(root.winfo_screenwidth() - w) // 2}+{root.winfo_screenheight() // 4}')
    front(root)
    entry.focus_set()
    root.mainloop()
    if not out:
        sys.exit(1)
    sys.stdout.write(out[0])


def region():
    g = user32.GetSystemMetrics
    x, y, w, h = g(76), g(77), g(78), g(79)
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry(f'{w}x{h}+{x}+{y}')
    root.attributes('-alpha', .3)
    canvas = tk.Canvas(root, bg='black', highlightthickness=0, cursor='crosshair')
    canvas.pack(fill='both', expand=True)
    s, out = {}, []

    def press(e):
        s.update(x0=e.x, y0=e.y, id=canvas.create_rectangle(e.x, e.y, e.x, e.y, outline='#00dcff', width=4))

    def release(e):
        if 'id' in s:
            x0, x1 = sorted((s['x0'], e.x))
            y0, y1 = sorted((s['y0'], e.y))
            if x1 - x0 > 12 and y1 - y0 > 12:  # a tap is not a box
                out.append(f'{x + x0} {y + y0} {x1 - x0} {y1 - y0}')
        root.destroy()

    canvas.bind('<ButtonPress-1>', press)
    canvas.bind('<B1-Motion>', lambda e: 'id' in s and canvas.coords(s['id'], s['x0'], s['y0'], e.x, e.y))
    canvas.bind('<ButtonRelease-1>', release)
    root.bind('<Escape>', lambda e: root.destroy())
    front(root)
    root.mainloop()
    if not out:
        sys.exit(1)
    sys.stdout.write(out[0])


if __name__ == '__main__':
    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1] == 'menu':
        menu(sys.argv[2], [r for r in sys.stdin.read().split('\n') if r])
    else:
        region()
