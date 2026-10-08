#!/usr/bin/env python3
"""
send_to_blender.py
CLI tool to dispatch Python bpy scripts to an active Blender desktop session.
Supports dual-transport: Fast HTTP REST with automatic Windows/WSL Host resolution,
and zero-network Shared File Watcher fallback.
"""

import sys
import os
import json
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path

DEFAULT_PORT = 9876
TIMEOUT = 45

def get_wsl_host_ips():
    """Detects Windows host IPs from WSL environment."""
    ips = ["localhost", "127.0.0.1"]
    
    # Check default route
    try:
        with open("/proc/net/route", "r") as f:
            for line in f.readlines()[1:]:
                fields = line.strip().split()
                if fields[1] == "00000000": # default gateway
                    gw_hex = fields[2]
                    # Convert hex to IP
                    gw_ip = ".".join(str(int(gw_hex[i:i+2], 16)) for i in (6, 4, 2, 0))
                    if gw_ip not in ips:
                        ips.append(gw_ip)
    except Exception:
        pass

    # Check /etc/resolv.conf
    try:
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                if line.startswith("nameserver"):
                    ns = line.split()[1].strip()
                    if ns not in ips:
                        ips.append(ns)
    except Exception:
        pass

    return ips

def find_bridge_dirs():
    """Finds possible bridge directories across Linux, WSL, and native environments."""
    dirs = []
    
    # 1. Standard home
    dirs.append(Path.home() / ".blender_bridge")

    # 2. If in WSL, scan /mnt/c/Users/*
    c_users = Path("/mnt/c/Users")
    if c_users.exists():
        for p in c_users.iterdir():
            if p.is_dir() and p.name not in ("All Users", "Default", "Default User", "Public"):
                dirs.append(p / ".blender_bridge")

    return dirs

def try_http_send(code, port=DEFAULT_PORT):
    """Attempts to send code to Blender via HTTP POST."""
    hosts = get_wsl_host_ips()
    payload = json.dumps({"code": code}).encode("utf-8")

    for host in hosts:
        url = f"http://{host}:{port}/execute"
        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return True, data
        except (urllib.error.URLError, TimeoutError, ConnectionRefusedError, OSError):
            continue

    return False, None

def try_file_send(code):
    """Fallback: writes code to bridge directory and polls for result.json."""
    bridge_dirs = find_bridge_dirs()
    target_dir = None

    for d in bridge_dirs:
        try:
            d.mkdir(parents=True, exist_ok=True)
            target_dir = d
            break
        except Exception:
            continue

    if not target_dir:
        return False, {"error": "Could not locate or create .blender_bridge directory"}

    task_file = target_dir / "task.py"
    result_file = target_dir / "result.json"

    # Remove any stale result file
    if result_file.exists():
        try:
            result_file.unlink()
        except Exception:
            pass

    # Write task
    try:
        task_file.write_text(code, encoding="utf-8")
    except Exception as e:
        return False, {"error": f"Failed to write task file: {e}"}

    # Wait for result
    start_time = time.time()
    while time.time() - start_time < TIMEOUT:
        if result_file.exists():
            time.sleep(0.05)
            try:
                content = result_file.read_text(encoding="utf-8")
                result_file.unlink()
                data = json.loads(content)
                return True, data
            except Exception:
                pass
        time.sleep(0.2)

    return False, {"error": f"Timeout waiting for Blender to process task via {target_dir}"}

def main():
    parser = argparse.ArgumentParser(description="Send Python script to Blender desktop")
    parser.add_argument("--code", "-c", type=str, help="Python code to execute")
    parser.add_argument("--file", "-f", type=str, help="Path to Python script file")
    parser.add_argument("--status", action="store_true", help="Check Blender connection status")
    parser.add_argument("--port", "-p", type=int, default=DEFAULT_PORT, help="Bridge HTTP port")
    args = parser.parse_args()

    if args.status:
        hosts = get_wsl_host_ips()
        for host in hosts:
            try:
                req = urllib.request.Request(f"http://{host}:{args.port}/status")
                with urllib.request.urlopen(req, timeout=2) as resp:
                    print(f"🟢 Connected to Blender on {host}:{args.port} -> {resp.read().decode('utf-8')}")
                    return 0
            except Exception:
                pass
        print("🔴 Blender HTTP bridge is not responding. Checking shared directories...")
        for d in find_bridge_dirs():
            if d.exists():
                print(f"📁 Shared directory found: {d}")
        return 1

    code = ""
    if args.code:
        code = args.code
    elif args.file:
        code = Path(args.file).read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        code = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    if not code.strip():
        print("Error: No code provided", file=sys.stderr)
        sys.exit(1)

    # 1. Try HTTP transport
    success, result = try_http_send(code, args.port)
    if not success:
        # 2. Fallback to File Watcher transport
        success, result = try_file_send(code)

    if not success:
        print("❌ Error: Failed to communicate with Blender.", file=sys.stderr)
        if result and "error" in result:
            print(f"Detail: {result['error']}", file=sys.stderr)
        print("\nPastikan script 'blender_bridge.py' sudah di-run di Blender Desktop!", file=sys.stderr)
        sys.exit(1)

    # Print output
    if result.get("output"):
        print(result["output"].strip())
    
    if result.get("status") == "error":
        print("❌ Blender Execution Error:\n" + result.get("error", ""), file=sys.stderr)
        sys.exit(2)
    else:
        print("✅ Successfully executed in Blender!")
        sys.exit(0)

if __name__ == "__main__":
    main()
