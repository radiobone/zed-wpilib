#!/usr/bin/env python3
"""Install zed-wpilib on macOS, Windows or Linux: the `wpilib` command, the Zed tasks,
a Shift-F5 Deploy key, and Zed's Java extension.

    python3 install.py              install / update
    python3 install.py --uninstall  remove (leaves projects alone)

Only WPILib entries in Zed's files are touched, and each changed file is backed up as *.bak first.
"""
import importlib.util
import json
import os
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

if sys.version_info < (3, 9):
    sys.exit("zed-wpilib needs Python 3.9 or newer.")

REPO = Path(__file__).resolve().parent
CLI = REPO / "bin" / "wpilib"
HOME = Path.home()
IS_WIN = os.name == "nt"
IS_MAC = sys.platform == "darwin"
DEPLOY_KEY = "shift-f5"  # same key as the VS Code WPILib extension
MARK = "zed-wpilib"


def _load_cli():
    loader = SourceFileLoader("wpilib_cli", str(CLI))
    spec = importlib.util.spec_from_loader("wpilib_cli", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


wp = _load_cli()
ZED_CFG = wp.zed_config_dir()
BIN_DIR = (Path(os.environ.get("LOCALAPPDATA", HOME / "AppData" / "Local")) / "zed-wpilib" / "bin") if IS_WIN else HOME / ".local" / "bin"
COMMAND = BIN_DIR / ("wpilib.cmd" if IS_WIN else "wpilib")


def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def save(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if read(path) == text:
            return False
        (path.with_name(path.name + ".bak")).write_text(read(path), encoding="utf-8")
    path.write_text(text, encoding="utf-8")
    return True


def read_list(path):
    if not path.exists():
        return []
    data = wp.load_jsonc(path)
    return data if isinstance(data, list) else []


def is_ours_key(entry):
    v = entry.get("bindings", {}).get(DEPLOY_KEY) if isinstance(entry, dict) else None
    return isinstance(v, list) and len(v) == 2 and isinstance(v[1], dict) and str(v[1].get("task_name", "")).startswith("WPILib:")


def install_command():
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    if IS_WIN:
        # -X utf8: WPILib templates and our output use UTF-8; Windows' default code page doesn't.
        COMMAND.write_text(f'@"{sys.executable}" -X utf8 "{CLI}" %*\r\n', encoding="utf-8")
        add_to_windows_path(BIN_DIR)
    else:
        CLI.chmod(0o755)
        if COMMAND.is_symlink() or COMMAND.exists():
            COMMAND.unlink()
        COMMAND.symlink_to(CLI)
        add_to_unix_path(BIN_DIR)
    print(f"installed the wpilib command: {COMMAND}")


def add_to_windows_path(d):
    import ctypes
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE) as k:
        try:
            cur, kind = winreg.QueryValueEx(k, "Path")
        except FileNotFoundError:
            cur, kind = "", winreg.REG_EXPAND_SZ
        parts = [p for p in cur.split(";") if p]
        if str(d).lower() in (p.lower() for p in parts):
            return
        winreg.SetValueEx(k, "Path", 0, kind, ";".join(parts + [str(d)]))
    # Tell running programs (Explorer, new terminals) that PATH changed.
    ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x1A, 0, "Environment", 0x2, 5000, None)
    print(f"added {d} to your PATH (restart Zed and terminals to pick it up)")


def add_to_unix_path(d):
    if str(d) in os.environ.get("PATH", "").split(os.pathsep):
        return
    shell = Path(os.environ.get("SHELL", "")).name
    line = f'export PATH="$HOME/.local/bin:$PATH"  # added by {MARK}\n'
    if shell == "zsh":
        rc = HOME / ".zprofile"
    elif shell == "bash":
        rc = HOME / (".bash_profile" if IS_MAC else ".profile")
    else:
        print(f"  note: add {d} to your PATH to use `wpilib` in a terminal (fish: fish_add_path {d})")
        return
    if MARK not in read(rc):
        with rc.open("a", encoding="utf-8") as f:
            f.write("\n" + line)
        print(f"added {d} to your PATH in {rc} (open a new terminal to use it)")


def install_tasks():
    path = ZED_CFG / "tasks.json"
    ours = wp.load_jsonc(REPO / "zed" / "tasks.json")
    for t in ours:
        t["command"] = str(COMMAND)
    keep = [t for t in read_list(path) if not str(t.get("label", "")).startswith("WPILib:")]
    text = f"// Zed tasks. The WPILib entries are managed by {MARK}; re-running its installer replaces them.\n"
    if save(path, text + json.dumps(keep + ours, indent=2) + "\n"):
        print(f"installed {len(ours)} WPILib tasks in {path}")


def install_keymap():
    path = ZED_CFG / "keymap.json"
    cur = read_list(path)
    if any(is_ours_key(k) for k in cur):
        return
    cur.append({"context": "Workspace", "bindings": {DEPLOY_KEY: ["task::Spawn", {"task_name": "WPILib: Deploy Robot Code"}]}})
    save(path, f"// Zed keymap. The {DEPLOY_KEY} WPILib Deploy binding is managed by {MARK}.\n" + json.dumps(cur, indent=2) + "\n")
    print(f"bound {DEPLOY_KEY} to Deploy in {path}")


def install_settings():
    """Turn on auto-install of Zed's Java extension. A text insert keeps the user's comments."""
    path = ZED_CFG / "settings.json"
    txt = read(path) or "{\n}\n"
    if '"auto_install_extensions"' not in txt:
        i = txt.index("{")
        save(path, txt[:i + 1] + '\n  "auto_install_extensions": { "java": true },' + txt[i + 1:])
        print(f"turned on Zed's Java extension in {path}")
    elif '"java"' not in txt.split('"auto_install_extensions"', 1)[1][:300]:
        print(f'  note: add "java": true to "auto_install_extensions" in {path}')


def install():
    install_command()
    install_tasks()
    install_keymap()
    install_settings()
    if wp.installed_years():
        wp.resources(wp.wpilib_home())  # unpack templates now so the first `wpilib new` is instant
    else:
        print("\n  WPILib isn't installed yet. zed-wpilib is ready, but it needs WPILib to build robot code.")
        print("  Install it: https://docs.wpilib.org/en/stable/docs/zero-to-robot/step-2/wpilib-setup.html")
        print("  You don't need to run this installer again afterwards.")
    picker = "Cmd-Shift-R" if IS_MAC else "Alt-Shift-T"
    print(f"\nDone. Restart Zed, then press {picker} and type WPILib.")


def uninstall():
    if COMMAND.exists() or COMMAND.is_symlink():
        COMMAND.unlink()
        print(f"removed {COMMAND}")
    tp = ZED_CFG / "tasks.json"
    if tp.exists():
        save(tp, json.dumps([t for t in read_list(tp) if not str(t.get("label", "")).startswith("WPILib:")], indent=2) + "\n")
        print(f"removed WPILib tasks from {tp}")
    kp = ZED_CFG / "keymap.json"
    if kp.exists():
        save(kp, json.dumps([k for k in read_list(kp) if not is_ours_key(k)], indent=2) + "\n")
        print(f"removed the WPILib key from {kp}")
    print("Left Zed's settings.json, your PATH and your projects' .zed folders alone.")


if __name__ == "__main__":
    uninstall() if "--uninstall" in sys.argv else install()
