#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LinSpectacles Boot Environment Hub Module
# Copyright (C) 2026 brunonlinespace
# GPL-3.0-or-later

"""Read-only collectors for the Boot Environment Hub Module."""

from __future__ import annotations

import glob
import os
import platform
import re
import subprocess
from pathlib import Path

BOOT_ID = Path("/proc/sys/kernel/random/boot_id")
CMDLINE = Path("/proc/cmdline")
EFI_ROOT = Path("/sys/firmware/efi")
EFI_PLATFORM_SIZE = EFI_ROOT / "fw_platform_size"
ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def _read_text(path: Path) -> tuple[str, str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip(), "available"
    except PermissionError:
        return "Restricted", "restricted"
    except FileNotFoundError:
        return "Unavailable", "unavailable"
    except OSError as exc:
        return f"Unavailable ({exc})", "unavailable"


def _secure_boot_state() -> tuple[str, str]:
    matches = sorted(glob.glob(str(EFI_ROOT / "efivars" / "SecureBoot-*")))
    if not matches:
        return "Not reported", "SecureBoot EFI variable not exposed"
    path = Path(matches[0])
    try:
        data = path.read_bytes()
        if len(data) < 5:
            return "Unavailable", f"{path}: unexpected EFI variable format"
        value = data[4]
        if value == 1:
            return "Enabled", str(path)
        if value == 0:
            return "Disabled", str(path)
        return f"Reported value {value}", str(path)
    except PermissionError:
        return "Restricted", str(path)
    except OSError as exc:
        return f"Unavailable ({exc})", str(path)


def _command_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["SYSTEMD_COLORS"] = "0"
    env["SYSTEMD_PAGER"] = "cat"
    env["LC_ALL"] = "C"
    env["LANG"] = "C"
    return env


def parse_current_boot_loader_product(text: str) -> str | None:
    """Return Product from bootctl's Current Boot Loader section only."""
    in_current = False
    for raw in ANSI_ESCAPE_RE.sub("", text or "").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if not line.startswith((" ", "\t")) and stripped.endswith(":"):
            in_current = stripped == "Current Boot Loader:"
            continue
        if in_current and stripped.startswith("Product:"):
            value = stripped.partition(":")[2].strip()
            return value or None
    return None


def read_boot_loader_identity(timeout: float = 5.0) -> dict:
    try:
        result = subprocess.run(
            ["bootctl", "status", "--no-pager"],
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            env=_command_environment(),
        )
    except FileNotFoundError:
        return {"value": "Unavailable", "source": "bootctl is not installed"}
    except subprocess.TimeoutExpired:
        return {"value": "Unavailable", "source": "bootctl status timed out"}
    except OSError as exc:
        return {"value": f"Unavailable ({exc})", "source": "bootctl status --no-pager"}

    output = (result.stdout or result.stderr or "").strip()
    product = parse_current_boot_loader_product(output)
    if product:
        return {"value": product, "source": "bootctl status --no-pager · Current Boot Loader → Product"}
    if result.returncode == 0:
        return {"value": "Not reported", "source": "bootctl status --no-pager"}
    return {"value": "Unavailable", "source": "bootctl status --no-pager"}


def collect_boot_environment() -> list[dict]:
    boot_id, boot_id_state = _read_text(BOOT_ID)
    cmdline, cmdline_state = _read_text(CMDLINE)
    efi = EFI_ROOT.is_dir()

    if efi:
        fw_size, fw_state = _read_text(EFI_PLATFORM_SIZE)
        firmware = "UEFI"
        if fw_state == "available" and fw_size:
            firmware += f" · {fw_size}-bit"
        secure_boot, secure_source = _secure_boot_state()
    else:
        firmware = "Legacy / non-EFI interface"
        secure_boot = "Not applicable"
        secure_source = str(EFI_ROOT)

    loader = read_boot_loader_identity()

    return [
        {
            "key": "boot_id",
            "label": "Boot ID",
            "value": boot_id,
            "source": str(BOOT_ID),
            "state": boot_id_state,
        },
        {
            "key": "kernel",
            "label": "Kernel",
            "value": platform.uname().release or "Not reported",
            "source": "platform.uname().release",
            "state": "available",
        },
        {
            "key": "architecture",
            "label": "Architecture",
            "value": platform.machine() or "Not reported",
            "source": "platform.machine()",
            "state": "available",
        },
        {
            "key": "cmdline",
            "label": "Command line",
            "value": cmdline,
            "source": str(CMDLINE),
            "state": cmdline_state,
        },
        {
            "key": "firmware",
            "label": "Firmware",
            "value": firmware,
            "source": str(EFI_ROOT) + (f"; {EFI_PLATFORM_SIZE}" if efi else ""),
            "state": "available",
        },
        {
            "key": "secure_boot",
            "label": "Secure Boot",
            "value": secure_boot,
            "source": secure_source,
            "state": "available" if secure_boot not in {"Restricted", "Not reported"} and not secure_boot.startswith("Unavailable") else "reported",
        },
        {
            "key": "boot_loader",
            "label": "Boot loader",
            "value": loader["value"],
            "source": loader["source"],
            "state": "reported",
        },
    ]
