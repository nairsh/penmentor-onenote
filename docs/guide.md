# penmentor: the full guide

Press a key while you work through maths by hand, and an AI model (Claude, Gemini or GPT) answers by drawing on your screen, the way a teacher
marks work with coloured pens: rings round the mistake, ticks on the right lines, a faint ghost of the next step,
arrows from cause to effect. Words are a last resort.

This fork runs on Windows and is made for OneNote (desktop app) with a pen: a touchscreen laptop, a pen tablet, or an iPad
used as a second screen. It reads whatever maths is on screen. Forked from [AbdullahAlhariri/penmentor](https://github.com/AbdullahAlhariri/penmentor), the xournal++/Linux original.

## What it can do

| Menu entry | What you get |
|---|---|
| Did I make any mistakes? | the first real error circled with its fix, later lines that inherit it underlined, correct lines ticked |
| Solution check | is the final answer right, and is anything missing (+C, bounds, absolute values…)? |
| Give me a hint | the smallest nudge: one thing highlighted, the next step not given away |
| Which technique? | the features that point to a method are coloured, no method named; you pick one (`p`) and it says whether it fits |
| Quiz me on my steps | a question at the 1 or 2 steps that matter most; answer by typing (`a`) or by writing on the page (`w`) |
| Find-the-error drill | a new worked problem like yours with one planted mistake; tap the wrong line |
| Show me (animation) | box what you want to see (one box or several), then get an animation of it made with 3Blue1Brown's own [manim](https://github.com/3b1b/manim), on the other monitor, that you can play with: Riemann sums, areas, improper integrals, substitution as a stretch of the axis, solids of revolution, series, Taylor polynomials, polar and parametric curves |
| Ask about a box | drag a box round something and ask about just that |

The marks stay on your live screen: keep writing, scroll, move windows, they stay until you press **Esc**. Only
the marks themselves catch the pen (tap one to pin its "why"); everywhere else it goes to your app. Their bar of
buttons, bottom right (tap with the pen; pressing the penmentor key again opens the same as a menu):

| Button | |
|---|---|
| check new work | write more, then tap it: the model checks what you added |
| more help | one rung up the ladder: nudge → name the technique → ghost the next line → full fix |
| ask… | a follow-up question |
| show me | box what to animate, then watch it |
| what I read / stats | what the model read / harness and model, tokens, plan usage (Claude Code) |
| replay | the marks again |
| close · esc | **Esc** stops penmentor wherever you are: in a menu, while the model thinks (it stops too), or with the marks up |

A pen button or hotkey (`penmentor --ask check`) while the marks are up checks the work as it is now.

Show me starts on the frozen screen: drag boxes round what to animate (right-click takes one back), then tap the badge
or press Enter. The window opens straight away (a loading animation runs while the model thinks) and stays until you
press `q` in it (Esc leaves it open). Drag in it to move the bound, the number of rectangles, the degree, the point on the
curve (or turn a 3D solid); where curves cross, and where the bounds x = a and x = b meet them, is marked with
its coordinates. Change the maths in place: click a value in the row at the bottom (the function, a, b, n) and type a
new one, or drag a bound line; it redraws at once (and goes in the history). Scroll to zoom, arrows to step, space to replay. Every animation is kept: *Settings →
history* plays an old one again, without asking the model.

Hover or tap a mark for its one-line "why". Questions build on each other (one conversation) until you pick
*Clear context*; turn that off in *Settings*, where you also choose the model (see below) and effort.

## How it works, and what leaves your computer

A screenshot of every monitor goes to the
model you picked in *Settings*, through its company's command-line agent, so it runs on a subscription you already
have. Models are written `harness:model`; the prefix says which agent runs it:

| Prefix | Agent | How it runs |
|---|---|---|
| `claude:` | [Claude Code](https://claude.com/claude-code) (`claude -p`) | images inline; no tools, no MCP servers |
| `agy:` | Antigravity (`agy --print`) | it reads the images as files, in its sandbox, told to use only its file viewer |
| `codex:` | [Codex](https://github.com/openai/codex) (`codex exec`) | images attached; read-only sandbox, your Codex config and rules ignored |

*Settings* lists the models of the agents you have installed. Any other name the agent accepts works too: put
`"model": "codex:gpt-5.6-terra"` in `~/.config/penmentor/settings.json`. Switching agent starts a new conversation.

The model answers in JSON (what it read, a verdict, marks with boxes); penmentor snaps the boxes onto your ink and draws them
on top of your live screen. Nothing else is sent and nothing runs in the background between questions.

## Install (Windows 10/11)

1. Install [Python 3.10+](https://www.python.org/downloads/windows/) (tick "Add to PATH").
2. Install one agent and log in once by running it: [Claude Code](https://claude.com/claude-code) (use its native
   Windows install, not an npm `.cmd` shim: the system prompt is passed as an argument), `agy`, or [Codex](https://github.com/openai/codex).
3. In PowerShell:

```powershell
git clone https://github.com/nairsh/penmentor-onenote $HOME\penmentor-onenote
cd $HOME\penmentor-onenote
pip install .
penmentor --selftest
```

4. Optional, for real LaTeX instead of matplotlib's imitation: [MiKTeX](https://miktex.org/) (needs `latex` and `dvipng` on PATH).
5. **A key:** install [AutoHotkey v2](https://www.autohotkey.com/) and double-click [contrib/penmentor.ahk](../contrib/penmentor.ahk)
   (F9 asks, F10 checks new work; edit the paths and keys inside). `pythonw` avoids a console window. If your pen has a
   button, Windows *Settings → Bluetooth & devices → Pen & Windows Ink → Pen shortcuts* can open the script's shortcut or
   an app instead.

Use OneNote's desktop app (not the web) with its page open on a monitor. Start `penmentor`, pick a question; the marks
stay over OneNote until Esc.

**iPad:** penmentor cannot run on iPadOS. Mirror the laptop to the iPad with a second-display app (Duet Display, Spacedesk,
Luna Display…) and write with the Pencil on the mirrored OneNote: the marks show there too. Whether Pencil pressure
and taps pass through depends on that app.

**Show me** needs manimgl (3Blue1Brown's manim) and its OpenGL window, untested on Windows in this fork. Put it in its own environment, where penmentor looks for it:

```powershell
python -m venv --system-site-packages $env:LOCALAPPDATA\penmentor\data\manim
& $env:LOCALAPPDATA\penmentor\data\manim\Scripts\pip install manimgl audioop-lts
```

(or `pip install ".[show]"` into the Python that runs penmentor).

**Known limits:** one display scale for all monitors works best (mixed-DPI setups can shift marks); the model sees
the screen, not the whole OneNote page, so keep the problem visible; menus are small tkinter windows, not rofi.

## Development

```sh
python bin/penmentor --selftest                       # page analysis, text, formulas, plots, drill logic; no model, no screen
python bin/penmentor --test shot.png check            # ask your model about a saved screenshot: shot.penmentor.json and shot.penmentor.png
python bin/penmentor --render shot.png shot.penmentor.json  # redraw a saved answer without the model (tune the visuals)
$env:PYTHONPATH='src'; & $env:LOCALAPPDATA\penmentor\data\manim\Scripts\python -m penmentor.plot --png spec.json out.png   # one animation's last frame
& $env:LOCALAPPDATA\\penmentor\\data\\manim\\Scripts\\python docs/assets.py   # the README's banner
```

| Module | |
|---|---|
| `cli.py` | entry point: capture, menu, settings |
| `prompts.py` | everything the model is told, and the JSON schema it answers in |
| `harness.py` | the `claude`, `agy` and `codex` calls, sessions, token and usage stats |
| `desktop.py`, `picker.py`, `xournal.py` | screenshots, monitors, windows, the pointer (Win32 through ctypes); the tkinter menu and box selector; a stub where xournal++'s page export was |
| `page.py` | where the ink is: snapping boxes onto strokes, finding empty space |
| `overlay.py`, `draw.py`, `style.py` | the marks over your live screen (a shaped window), the modes |
| `typeset.py` | LaTeX (or mathtext) into images |
| `plot.py`, `show.py`, `expr.py` | Show me: the manim scenes (run by manim's Python), opening their window and its history, and a safe evaluator for the model's formulas |
