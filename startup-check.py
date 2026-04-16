#!/usr/bin/env python3
"""
Startup Check - Solomon Empire
Pre-flight verification before launching all systems
"""

import os
import sys
import socket
from pathlib import Path


def check_python_version():
    if sys.version_info < (3, 8):
        print("  FAIL  Python 3.8+ required (you have {}.{})".format(*sys.version_info[:2]))
        return False
    print(f"  PASS  Python {sys.version.split()[0]}")
    return True


def check_directories():
    dirs = [
        "data", "data/generated_content", "data/email_marketing",
        "data/market_intelligence", "data/shopify", "data/reports",
        "logs", "logs/empire", "memory",
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print(f"  PASS  Directories ready ({len(dirs)} created/verified)")
    return True


def check_dependencies():
    pkgs = {
        "flask": "Flask",
        "flask_cors": "Flask-CORS",
        "requests": "requests",
        "dotenv": "python-dotenv",
        "psutil": "psutil",
    }
    missing = []
    for import_name, pkg_name in pkgs.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg_name)

    if missing:
        print(f"  FAIL  Missing packages: {', '.join(missing)}")
        print(f"        Fix: pip install -r requirements.txt")
        return False

    print(f"  PASS  All {len(pkgs)} packages installed")
    return True


def check_core_files():
    files = [
        "business_memory.py", "revenue_tracker.py", "content_generator.py",
        "email_marketing.py", "market_intelligence.py", "shopify_integration.py",
        "mission_control_hub.py", "master-control.py", "mission_control_dashboard.py",
        "api-server.py", "empire-auto.py", "empire-status.py",
    ]
    missing = [f for f in files if not Path(f).exists()]

    if missing:
        print(f"  WARN  Missing files: {', '.join(missing)}")
        return True  # Warn but don't fail

    print(f"  PASS  All {len(files)} core files present")
    return True


def check_ports():
    ports = {8080: "Mission Control Hub", 5001: "API Server",
             5002: "Master Control", 5003: "Agent Dashboard"}
    in_use = []

    for port, name in ports.items():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex(("127.0.0.1", port))
                if result == 0:
                    in_use.append(f"{port} ({name})")
        except Exception:
            pass

    if in_use:
        print(f"  WARN  Ports already in use: {', '.join(in_use)}")
        print(f"        Close other apps using those ports, or they may conflict")
    else:
        print(f"  PASS  All {len(ports)} ports available")
    return True


def check_env():
    env_file = Path(".env")
    if env_file.exists():
        print("  PASS  .env file found")
    else:
        print("  INFO  No .env file (running with defaults - OK)")
    return True


def main():
    print("\n" + "=" * 55)
    print("  SOLOMON EMPIRE - PRE-FLIGHT CHECK".center(55))
    print("=" * 55 + "\n")

    checks = [
        ("Python Version",  check_python_version),
        ("Directories",     check_directories),
        ("Dependencies",    check_dependencies),
        ("Core Files",      check_core_files),
        ("Ports",           check_ports),
        ("Environment",     check_env),
    ]

    results = []
    for name, fn in checks:
        print(f"  Checking {name}...")
        try:
            ok = fn()
        except Exception as e:
            print(f"  ERROR  {name}: {e}")
            ok = False
        results.append(ok)
        print()

    all_pass = all(results)
    print("=" * 55)
    if all_pass:
        print("  ALL CHECKS PASSED - Ready to launch!".center(55))
        print("=" * 55)
        print("\n  Run: run.bat (Windows)  or  bash run.sh (Linux/Mac)\n")
    else:
        print("  FIX THE ISSUES ABOVE THEN TRY AGAIN".center(55))
        print("=" * 55)
        print()

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
