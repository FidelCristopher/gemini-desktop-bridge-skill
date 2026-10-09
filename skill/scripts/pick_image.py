#!/usr/bin/env python3
"""
pick_image.py
Image input utility for terminal environments.
Allows terminal agents and users to:
1. Open native Windows / Desktop File Picker GUI dialog to select an image.
2. Grab an image directly from the Windows / system clipboard (e.g., Snipping Tool / Ctrl+C).
3. Select from an image drop-folder.
"""

import sys
import os
import shutil
import subprocess
import argparse
from pathlib import Path

BRIDGE_DIR = Path.home() / ".blender_bridge"
INPUT_DIR = BRIDGE_DIR / "input_images"

def is_wsl():
    return "microsoft" in Path("/proc/version").read_text().lower() if Path("/proc/version").exists() else False

def pick_via_file_dialog():
    """Opens a native graphical file dialog to select an image file."""
    if is_wsl() or sys.platform == "win32":
        # Launch Windows File Picker via PowerShell
        ps_script = """
Add-Type -AssemblyName System.Windows.Forms
$dialog = New-Object System.Windows.Forms.OpenFileDialog
$dialog.Filter = 'Image Files (*.png;*.jpg;*.jpeg;*.webp;*.bmp)|*.png;*.jpg;*.jpeg;*.webp;*.bmp|All Files (*.*)|*.*'
$dialog.Title = 'Select Reference Image for Blender 3D'
$dialog.InitialDirectory = [Environment]::GetFolderPath('MyPictures')
$null = $dialog.ShowDialog()
if ($dialog.FileName) {
    Write-Output $dialog.FileName
}
"""
        cmd = ["powershell.exe", "-Command", ps_script] if is_wsl() else ["powershell", "-Command", ps_script]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            win_path = res.stdout.strip()
            if not win_path:
                return None
            
            # Convert Windows path (e.g. C:\...) to WSL path if inside WSL
            if is_wsl() and ":" in win_path:
                wsl_res = subprocess.run(["wslpath", "-u", win_path], capture_output=True, text=True)
                return wsl_res.stdout.strip() if wsl_res.returncode == 0 else win_path
            return win_path
        except Exception as e:
            print(f"[ERROR] Failed to open Windows file dialog: {e}", file=sys.stderr)
            return None

    # Linux native fallback (zenity or kdialog)
    if shutil.which("zenity"):
        res = subprocess.run(
            ["zenity", "--file-selection", "--title=Select Reference Image", "--file-filter=*.png *.jpg *.jpeg *.webp *.bmp"],
            capture_output=True, text=True
        )
        return res.stdout.strip() if res.returncode == 0 else None
    
    return None

def grab_from_clipboard():
    """Extracts an image from clipboard and saves to a local file."""
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = BRIDGE_DIR / "clipboard_input.png"

    if is_wsl() or sys.platform == "win32":
        # Target path in Windows format for PowerShell
        if is_wsl():
            # Get Windows temp / bridge path
            win_path_res = subprocess.run(["wslpath", "-w", str(out_file)], capture_output=True, text=True)
            win_out = win_path_res.stdout.strip()
        else:
            win_out = str(out_file)

        ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
if ([System.Windows.Forms.Clipboard]::ContainsImage()) {{
    $img = [System.Windows.Forms.Clipboard]::GetImage()
    $img.Save('{win_out}', [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Output 'OK'
}} else {{
    Write-Output 'NO_IMAGE'
}}
"""
        cmd = ["powershell.exe", "-Command", ps_script] if is_wsl() else ["powershell", "-Command", ps_script]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = res.stdout.strip()
            if output == "OK" and out_file.exists():
                return str(out_file)
            else:
                return None
        except Exception as e:
            print(f"[ERROR] Clipboard grab failed: {e}", file=sys.stderr)
            return None

    # Linux native fallback (xclip)
    if shutil.which("xclip"):
        subprocess.run(["xclip", "-selection", "clipboard", "-t", "image/png", "-o"], stdout=open(out_file, "wb"))
        if out_file.exists() and out_file.stat().st_size > 0:
            return str(out_file)

    return None

def list_drop_folder():
    """Lists images placed in the input_images folder."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    images = [p for p in INPUT_DIR.iterdir() if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.bmp')]
    return sorted(images, key=lambda x: x.stat().st_mtime, reverse=True)

def main():
    parser = argparse.ArgumentParser(description="Image input helper for terminal")
    parser.add_argument("--dialog", action="store_true", help="Open native graphical File Explorer to select an image")
    parser.add_argument("--clipboard", action="store_true", help="Grab image from clipboard")
    parser.add_argument("--dropzone", action="store_true", help="Get latest image from drop folder")
    args = parser.parse_args()

    if args.dialog:
        path = pick_via_file_dialog()
        if path:
            print(path)
            sys.exit(0)
        else:
            print("[INFO] No file selected or dialog cancelled", file=sys.stderr)
            sys.exit(1)

    if args.clipboard:
        path = grab_from_clipboard()
        if path:
            print(path)
            sys.exit(0)
        else:
            print("[INFO] No image found in clipboard. Please copy/screenshot an image first.", file=sys.stderr)
            sys.exit(1)

    if args.dropzone:
        imgs = list_drop_folder()
        if imgs:
            print(str(imgs[0]))
            sys.exit(0)
        else:
            print(f"[INFO] No images found in {INPUT_DIR}", file=sys.stderr)
            sys.exit(1)

    # If no flags passed, try clipboard first, then dialog
    path = grab_from_clipboard()
    if path:
        print(path)
        sys.exit(0)
    
    path = pick_via_file_dialog()
    if path:
        print(path)
        sys.exit(0)

    sys.exit(1)

if __name__ == "__main__":
    main()
