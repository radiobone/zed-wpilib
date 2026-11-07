# zed-wpilib

Write FRC robot code in [Zed](https://zed.dev) instead of VS Code. You get everything the WPILib VS Code extension does: create projects, build, deploy, simulate, debug, RioLog, vendor libraries, WPILib tools, and Java/C++ code completion.

Works on **Windows, macOS and Linux**. It uses your normal WPILib install (JDK, GradleRIO, roboRIO toolchain, tools and project templates), so it always matches the WPILib version you have installed.

## Install

You need:
- **WPILib** for this season, installed as usual (it's fine to keep VS Code too): https://docs.wpilib.org/en/stable/docs/zero-to-robot/step-2/wpilib-setup.html
- **Zed**: https://zed.dev/download
- **Python 3.9+**. The Windows installer offers to install it for you. On a Mac, run `xcode-select --install` if you don't have it.

Then run one command.

**Windows** (in PowerShell):
```powershell
irm https://raw.githubusercontent.com/OWNER/zed-wpilib/main/install.ps1 | iex
```

**macOS / Linux** (in Terminal):
```bash
curl -fsSL https://raw.githubusercontent.com/OWNER/zed-wpilib/main/install.sh | sh
```

**Restart Zed** afterwards; it installs its Java extension on startup.

To update later, run **WPILib: Update zed-wpilib** in Zed, or run the install command again.

## Using it

| | macOS | Windows / Linux |
|---|---|---|
| Open the WPILib command list (task picker) | **Cmd-Shift-R** | **Alt-Shift-T** |
| Deploy robot code | **Shift-F5** | **Shift-F5** |
| Run the last command again | **Cmd-Option-R** | **Alt-T** |

Open the task picker and type `WPILib` to see every command. You can also reach it from the command palette: `task: spawn`.

**Open your robot project as a folder** (File → Open, choose the folder with `build.gradle`). The first time, Zed shows a **"!"** in the title bar: click it and choose **Trust**. Until you do, Zed won't start code completion for that project.

**Existing projects:** run **WPILib: Set Up Zed for This Project** once per computer. It writes a `.zed/` folder with this computer's JDK paths and adds `.zed/` to `.gitignore`, so teammates on VS Code aren't affected.

### VS Code command → Zed

| VS Code WPILib command | In Zed |
|---|---|
| Create a new project | `WPILib: Create a New Project` |
| Build Robot Code | `WPILib: Build Robot Code` |
| Deploy Robot Code | **Shift-F5** or `WPILib: Deploy Robot Code` |
| Simulate Robot Code | `WPILib: Simulate Robot Code` (asks which sim extensions to load) |
| Hardware Sim Robot Code | `WPILib: Simulate Robot Code (Hardware Sim)` |
| Test Robot Code | `WPILib: Test Robot Code` |
| Debug Robot Code | Debug panel → **WPILib: Debug Robot Code (roboRIO)**. It deploys in debug mode, then attaches |
| Debug in simulation | Debug panel → **WPILib: Simulate Robot Code (with debugger)** |
| Start RioLog | `WPILib: Start RioLog` |
| Set Team Number | `WPILib: Set Team Number` |
| Manage Vendor Libraries | `WPILib: Manage Vendor Libraries` / `Install` / `Check for Updates` / `Uninstall` |
| Start Tool | `WPILib: Start Tool`, or `WPILib: Start AdvantageScope`, `Elastic`, `Glass`, `SysId`, … |
| Create a new class/command | `WPILib: Create a New Class/Command` (creates it next to the file you have open) |
| Import a 2020-2025 Gradle project | `WPILib: Import a 2020-2025 Project` |
| Open API Documentation / Help | `WPILib: Open API Documentation`, `WPILib: Open FRC Docs` |
| Refresh C++ IntelliSense / Select toolchain | `WPILib: Refresh C++ IntelliSense`, `WPILib: Select C++ IntelliSense Toolchain` |
| Run a command in Gradle / Clean | `WPILib: Run a Gradle Command`, `WPILib: Clean` |
| Change Language / Desktop Support settings | `WPILib: Change Language Setting`, `WPILib: Change Desktop Support Setting` |
| Offline, Skip Tests, Auto RioLog, … settings | `WPILib: Change Settings` (saved per project in `.wpilib/zed_settings.json`) |
| Open Project Information | `WPILib: Open Project Information` |
| Check for WPILib Updates | `WPILib: Check for WPILib Updates` |

Commands that need a choice (template, team number, vendor library) ask in Zed's terminal panel: type a number, or type text to filter the list.

Everything also works from a terminal: `wpilib --help`, e.g. `wpilib deploy --team 1234`, `wpilib vendordep add <url>`, `wpilib tool glass`.

## Good to know

- **The first build of a project needs internet.** It downloads build tools that the offline WPILib copy doesn't include. After that, builds can run offline (`WPILib: Toggle Offline Mode`). Deploys run offline by default, like VS Code, so deploying over the robot's Wi-Fi works.
- **Deploying:** plug into the robot with USB or Ethernet, or join its Wi-Fi, then press Shift-F5. The first deploy asks for your team number if it isn't set.
- **Code completion:** Java uses Zed's Java extension. Its language server runs on JDK 25+: it uses one you have installed, or Zed downloads one. Your code still compiles with WPILib's JDK 17. C++ uses clangd with the roboRIO toolchain's headers, refreshed on every build.
- **C++ debugging on the roboRIO** is experimental. WPILib's ARM `gdb` is too old for Zed's GDB support, so it uses LLDB instead. C++ simulation debugging works normally.
- **Vendor libraries** install from WPILib's online list, from your WPILib install's `vendordeps` folder, or from any vendor JSON URL.
- Run **WPILib: Check Setup (Doctor)** if something isn't working.

## Uninstall

```bash
python3 ~/.local/share/zed-wpilib/install.py --uninstall
```
On Windows: `py "$env:LOCALAPPDATA\zed-wpilib\app\install.py" --uninstall`

## What's in here

```
bin/wpilib        the `wpilib` command (Python, standard library only)
zed/tasks.json    the WPILib tasks added to Zed
install.py        installer / uninstaller (all platforms)
install.sh        one-line installer for macOS / Linux
install.ps1       one-line installer for Windows
```
