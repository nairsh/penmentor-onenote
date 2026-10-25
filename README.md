<p align="center"><img src="docs/banner.png" alt="penmentor" width="100%"></p>

<p align="center">
A maths mentor at the tip of your pen. Press a key while you work by hand: Claude, Gemini or GPT marks your work on the screen like a teacher with coloured pens, gives you hints instead of answers, and shows the idea as a 3Blue1Brown-style animation.
</p>

<p align="center"><img src="docs/demo.gif" alt="Original demo: writing an integral in xournal++ on Linux, penmentor marking the sign slip, then animating the area" width="860"><br>
<sub>Demo from the Linux/xournal++ original (this fork does the same over OneNote on Windows): handwriting → one key → the slip is marked on the page → box the integral → an interactive manim animation.
(<a href="docs/demo.mp4">video</a>; for a repeatable recording the pen is scripted and the model's answer is a fixed example.)</sub></p>

## About this fork

**penmentor-onenote** is a Windows port of [AbdullahAlhariri/penmentor](https://github.com/AbdullahAlhariri/penmentor) (MIT) for
**OneNote** and a pen. Same idea: hit a key while you write, and the model marks your work on screen with hints, not
answers. What changed: screenshots, windows, hotkeys and menus use Win32 instead of X11/i3/rofi, and the xournal++ plugin is
gone (the model sees the screen). It works with any app on screen, OneNote being the target.

Not GoodNotes: that's iPadOS-only and can't be overlaid. Use OneNote on a Windows laptop, or mirror the laptop to an iPad
with a second-display app and write with the Pencil there ([details](docs/guide.md#install-windows-1011)).

> Status: ported and self-tested on GitHub's Windows runner; not yet used by hand on a pen and OneNote. Issues welcome.

## Works with Claude Code, Codex and Antigravity

| Prefix | Agent | For example |
|---|---|---|
| `claude:` | [Claude Code](https://claude.com/claude-code) | `claude:opus`, `claude:sonnet`, `claude:haiku` |
| `codex:` | [Codex](https://github.com/openai/codex) | `codex:gpt-5.6-terra` |
| `agy:` | Antigravity CLI | `agy:gemini-4-argon-medium` |

## Quick start (PowerShell)

```powershell
git clone https://github.com/nairsh/penmentor-onenote $HOME\penmentor-onenote
cd $HOME\penmentor-onenote
pip install .
penmentor --selftest
```

Then bind a key with [contrib/penmentor.ahk](contrib/penmentor.ahk). Setup, keys and how it works: [the guide](docs/guide.md).

## License

[MIT](LICENSE)
