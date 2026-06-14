# Install

## Windows

Download `tawreed-windows.zip` from the [Releases page](https://github.com/sfkareem/tawreed/releases),
unzip, and double-click `Tawreed.exe`.

### SmartScreen

The EXE is **not code-signed** (signing certificates are expensive
and the project is solo-maintained). On first launch, Windows
SmartScreen will show a blue dialog:

> Windows protected your PC.
> Microsoft Defender SmartScreen prevented an unrecognised app
> from starting. Running this app might put your PC at risk.

To run Tawreed anyway:

1. Click **More info**.
2. Click **Run anyway**.

You only need to do this once — SmartScreen remembers the decision
per-user, per-file-hash. If you upgrade Tawreed, the hash changes
and you'll see the dialog again.

### Antivirus false positives

Some antivirus products flag PyInstaller binaries as "Suspicious"
or "Trojan.Generic" because of how the bootloader unpacks itself.
This is a known false-positive pattern across all PyInstaller apps.
If your AV deletes the EXE, add an exception for the `Tawreed\`
folder.

## macOS

Download `tawreed-macos.zip`, unzip, and drag `Tawreed.app` to
`/Applications/`.

### Gatekeeper

On first launch, macOS will show:

> "Tawreed" cannot be opened because the developer cannot be verified.

To open anyway:

1. Open **System Settings** → **Privacy & Security**.
2. Scroll to the bottom — you'll see a message about Tawreed
   being blocked.
3. Click **Open Anyway**.

Or, in a terminal:

```bash
xattr -dr com.apple.quarantine /Applications/Tawreed.app
```

## Linux

Download `tawreed-linux.tar.gz`, extract, and run `./Tawreed` from
the extracted folder.

### Dependencies

Some distros require explicit Qt dependencies:

```bash
# Debian / Ubuntu
sudo apt install python3-pyqt6 libxcb-cursor0

# Fedora
sudo dnf install python3-pyqt6 libxcb

# Arch
sudo pacman -S python-pyqt6 libxcb
```

### Wayland

Tawreed uses Qt's XCB platform plugin by default. On Wayland-only
sessions, set `QT_QPA_PLATFORM=wayland` before launching:

```bash
QT_QPA_PLATFORM=wayland ./Tawreed
```
