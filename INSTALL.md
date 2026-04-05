# Installation and Setup

## Requirements

| Requirement | Version | Notes |
|-------------|---------|-------|
| git | any | for cloning |
| bash | 4.0+ | macOS ships bash 3 — see macOS note below |
| Python 3 | 3.8+ | for bootstrap script internals and the GUI |
| tkinter | — | GUI only |
| sed, awk | standard | pre-installed on all platforms |

---

## 1. Clone the repo

```bash
git clone https://github.com/Adamgdwn/ai-project-governance.git
```

You can put it anywhere. A good default:

```bash
git clone https://github.com/Adamgdwn/ai-project-governance.git ~/code/ai-project-governance
cd ~/code/ai-project-governance
```

---

## 2. Make the scripts executable

```bash
chmod +x automation/new_build.sh
chmod +x automation/bootstrap_project.sh
chmod +x automation/governance_check.sh
chmod +x automation/check_required_files.sh
```

---

## 3. Set your project roots

Open `automation/new_build.sh` in any editor and change the two path variables near the top to wherever you want projects created on your machine:

```bash
AGENTS_ROOT="${HOME}/code/agents"       # agent projects go here
APPS_ROOT="${HOME}/code/Applications"   # apps, tools, and automation go here
```

Do the same in `automation/new_build_gui.py` (lines 19–20):

```python
AGENTS_ROOT = Path.home() / "code" / "agents"
APPS_ROOT   = Path.home() / "code" / "Applications"
```

Make the target directories if they don't exist:

```bash
mkdir -p ~/code/agents ~/code/Applications
```

---

## 4. Set your name (optional)

`new_build.sh` fills the `Project Owner` field in `project-control.yaml` with a hardcoded name. Find this line and change it to yours:

```bash
sed -i "s/name: Project Owner/name: Adam Goodwin/" "$PC"
```

---

## 5. Verify

Run the terminal launcher:

```bash
bash automation/new_build.sh
```

You should see the intake prompt. Enter a name, pick `app`, accept the defaults, and confirm. Check that a new directory was created under your `APPS_ROOT`.

---

## GUI setup (Linux)

### Install tkinter

**Debian / Ubuntu / Pop!_OS:**
```bash
sudo apt install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**Arch:**
```bash
sudo pacman -S tk
```

### Run the GUI

```bash
python3 automation/new_build_gui.py
```

### Add a desktop launcher

To launch the GUI from your application menu or desktop, create a `.desktop` file:

```bash
REPO="$HOME/code/ai-project-governance"   # adjust to where you cloned

cat > ~/.local/share/applications/new-build-agent.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=New Build Agent
Comment=Scope and scaffold a new governed project
Icon=${REPO}/automation/new-build-agent.svg
Exec=python3 ${REPO}/automation/new_build_gui.py
Terminal=false
StartupNotify=true
Categories=Development;Utility;
EOF

chmod +x ~/.local/share/applications/new-build-agent.desktop
update-desktop-database ~/.local/share/applications/
```

To also add a shortcut to your Desktop:

```bash
cp ~/.local/share/applications/new-build-agent.desktop ~/Desktop/
chmod +x ~/Desktop/New\ Build\ Agent.desktop
```

---

## macOS

macOS ships with bash 3, which lacks some features used in `new_build.sh` (associative arrays, `mapfile`). Install a current bash first:

```bash
brew install bash
```

Then run scripts explicitly with the Homebrew bash:

```bash
/opt/homebrew/bin/bash automation/new_build.sh
```

tkinter on macOS requires the full Python.org installer or a Homebrew Python built with tk:

```bash
brew install python-tk
python3 automation/new_build_gui.py
```

The `.desktop` launcher is Linux-only. On macOS, create an Automator app or use the terminal command above.

---

## Using with pyenv

If you manage Python with pyenv, point the scripts at your pyenv Python:

```bash
~/.pyenv/versions/3.12.1/bin/python3 automation/new_build_gui.py
```

Or set the version in your project directory:

```bash
cd ~/code/ai-project-governance
pyenv local 3.12.1
```

Then `python3` will resolve correctly.

---

## Optional: add to PATH

To run `new_build.sh` from anywhere without a full path, add the automation directory to your shell profile:

**bash (`~/.bashrc` or `~/.bash_profile`):**
```bash
export PATH="$HOME/code/ai-project-governance/automation:$PATH"
```

**zsh (`~/.zshrc`):**
```zsh
export PATH="$HOME/code/ai-project-governance/automation:$PATH"
```

Then reload your shell and run:
```bash
new_build.sh
```

---

## Updating

```bash
cd ~/code/ai-project-governance
git pull
```

Updates to templates only affect new projects — existing projects are not changed.
