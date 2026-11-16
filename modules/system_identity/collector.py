#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LinSpectacles System Identity Hub Module
# Copyright (C) 2026 brunonlinespace
# GPL-3.0-or-later

"""Lightweight, read-only collectors for the System Identity Hub Module."""

from __future__ import annotations

import os
import platform
import socket
import subprocess
import time
from pathlib import Path

OS_RELEASE = Path("/etc/os-release")


def _read_os_release() -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        with OS_RELEASE.open("r", encoding="utf-8", errors="replace") as handle:
            for raw in handle:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                values[key] = value.strip().strip('"')
    except OSError:
        pass
    return values


def _system_age_days(timeout: float = 2.0) -> tuple[str, str, str]:
    """Derive age from the birth timestamp reported for `/`.

    This is intentionally presented as a derived filesystem-based age, not as
    an authoritative OS installation date.  A zero/invalid birth timestamp is
    treated as Unknown rather than replaced with a weaker guess.
    """
    try:
        result = subprocess.run(
            ["stat", "-c", "%W", "/"],
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except FileNotFoundError:
        return "Unknown", "stat is not installed", "unknown"
    except subprocess.TimeoutExpired:
        return "Unknown", "stat -c %W / timed out", "unknown"
    except OSError as exc:
        return "Unknown", f"stat -c %W / unavailable ({exc})", "unknown"

    if result.returncode != 0:
        detail = (result.stderr or "").strip()
        source = "stat -c %W /" + (f" · {detail}" if detail else "")
        return "Unknown", source, "unknown"

    raw = (result.stdout or "").strip()
    try:
        birth = int(raw)
    except ValueError:
        return "Unknown", "stat -c %W / returned a non-numeric value", "unknown"

    if birth <= 0:
        return "Unknown", "stat -c %W / did not report a usable birth timestamp", "unknown"

    now = int(time.time())
    if birth > now:
        return "Unknown", "stat -c %W / reported a future birth timestamp", "unknown"

    days = (now - birth) // 86400
    unit = "day" if days == 1 else "days"
    return f"{days} {unit}", "Derived: current Unix time − root directory birth time (stat -c %W /)", "derived"


def collect_system_identity() -> list[dict]:
    release = _read_os_release()
    distro = release.get("PRETTY_NAME") or release.get("NAME") or "Linux"
    desktop = os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION") or "—"
    session = os.environ.get("XDG_SESSION_TYPE") or "—"
    age, age_source, age_state = _system_age_days()

    return [
        {
            "key": "distribution",
            "label": "Distribution",
            "value": distro,
            "source": str(OS_RELEASE),
            "state": "reported",
        },
        {
            "key": "system_age",
            "label": "System Age",
            "value": age,
            "source": age_source,
            "state": age_state,
        },
        {
            "key": "kernel",
            "label": "Kernel",
            "value": platform.release() or "—",
            "source": "platform.release()",
            "state": "reported",
        },
        {
            "key": "hostname",
            "label": "Hostname",
            "value": socket.gethostname() or "—",
            "source": "socket.gethostname()",
            "state": "reported",
        },
        {
            "key": "desktop",
            "label": "Desktop",
            "value": desktop,
            "source": "XDG_CURRENT_DESKTOP or DESKTOP_SESSION",
            "state": "reported",
        },
        {
            "key": "session",
            "label": "Session",
            "value": session,
            "source": "XDG_SESSION_TYPE",
            "state": "reported",
        },
    ]
