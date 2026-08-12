# Pomodoro Timer

Cross-platform Pomodoro timer (PySide6). Works on Windows and macOS.

## Run from source (any OS)

```bash
python3 -m pip install -r requirements.txt
python3 pomodoro_pyside6.py
```

## Build a standalone app

- **Windows:** run `build.bat`
- **macOS:** run `chmod +x build.sh && ./build.sh`
  - Produces `PomodoroTimer_Mac/PomodoroTimer.app`
  - First launch: right-click the app → "Open" (it isn't signed/notarized
    with an Apple Developer ID, so Gatekeeper will otherwise block it)

Both scripts now install `requirements.txt` first, verify `PySide6`
actually imports, clean any stale `build/`/`dist/` folders, and pass
`--collect-all PySide6` to PyInstaller. This avoids a build that
reports success but then fails at runtime with something like:

```
Failed to execute script pomodoro_pyside6 due to unhandled exception:
No module named 'PySide6'
```

That error means PyInstaller's build machine either didn't have
PySide6 installed in the same Python it ran under, or a leftover
`build/`/`dist/` folder from an earlier broken attempt got reused.
If you still hit it after the updated `build.bat`/`build.sh`:
- Make sure only one Python is on PATH (`where python` on Windows /
  `which python3` on macOS should point to the one you expect)
- Delete the `build/`, `dist/`, and `*.spec` files and re-run the
  build script from a clean checkout

## Notes on macOS support

- Menu bar (system tray) icon, the always-on-top floating widget, and
  notifications all use standard Qt APIs and work the same as on
  Windows.
- Settings/config live at `~/.pomodoro/config.json`, session data at
  `~/PomodoroData` — both OS-independent via `pathlib`.

### Floating widget: always-on-top without stealing focus (macOS)

On macOS, `pip install -r requirements.txt` also installs
`pyobjc-framework-Cocoa`. This lets the floating widget set its native
window level directly, so it stays visible above other windows without
ever calling `raise_()`/activating the app — which is what caused it to
steal keyboard focus from whatever app you clicked into.

**Running a packaged `.app`?** PyInstaller doesn't always detect PyObjC's
`objc`/`AppKit`/`Foundation` modules automatically, so `build.sh` now
passes `--collect-all` for each of them. If you built with an older
version of this script, rebuild with the updated `build.sh` — a build
missing those modules "succeeds" but the native always-on-top code
silently fails at runtime (no console output, since it's a windowed
app), so the widget falls back to a much less reliable behavior.

To check what's actually happening (from source or from a built app),
look at the log file:

```bash
tail -f ~/Library/Logs/PomodoroTimer.log
```

You want to see `Native macOS always-on-top applied.` shortly after
switching to widget mode. If instead you see something like
`pyobjc-framework-Cocoa not importable`, PyObjC isn't available in
whichever Python actually ran the app — reinstall it (from source) or
rebuild with the updated `build.sh` (packaged app).

