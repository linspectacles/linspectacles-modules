#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LinSpectacles System Pulse Hub Module
# Copyright (C) 2026 brunonlinespace
# GPL-3.0-or-later

"""Toolkit-neutral collectors for the System Pulse Dashboard module.

All collectors are read-only and intentionally cheap.  They read kernel/sysfs
interfaces directly and do not invoke applets or privileged commands.
"""

from __future__ import annotations

import os
import time
from pathlib import Path


PROC_MEMINFO = Path("/proc/meminfo")
PROC_UPTIME = Path("/proc/uptime")
PROC_PRESSURE_IO = Path("/proc/pressure/io")
PROC_NET_ROUTE = Path("/proc/net/route")
SYS_CLASS_NET = Path("/sys/class/net")
SYS_THERMAL = Path("/sys/class/thermal")
SYS_HWMON = Path("/sys/class/hwmon")
SYS_POWER = Path("/sys/class/power_supply")


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    except (OSError, UnicodeError):
        return None


def _read_int(path: Path) -> int | None:
    value = _read_text(path)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def format_bytes(value: float | int | None, per_second: bool = False) -> str:
    if value is None:
        return "—"
    amount = max(0.0, float(value))
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    unit = units[0]
    for unit in units:
        if amount < 1024.0 or unit == units[-1]:
            break
        amount /= 1024.0
    if unit == "B":
        text = f"{amount:.0f} {unit}"
    elif amount >= 100:
        text = f"{amount:.0f} {unit}"
    elif amount >= 10:
        text = f"{amount:.1f} {unit}"
    else:
        text = f"{amount:.2f} {unit}"
    return text + ("/s" if per_second else "")



def read_uptime() -> dict:
    """Return system uptime in seconds from the kernel's /proc/uptime interface."""
    text = _read_text(PROC_UPTIME)
    if not text:
        return {"available": False}
    fields = text.split()
    if not fields:
        return {"available": False}
    try:
        seconds = max(0.0, float(fields[0]))
    except (TypeError, ValueError):
        return {"available": False}
    return {
        "available": True,
        "seconds": seconds,
        "source": "/proc/uptime",
    }


def format_uptime(seconds: float | int | None) -> str:
    """Format uptime as a compact, factual elapsed duration."""
    if seconds is None:
        return "—"
    total = max(0, int(float(seconds)))
    days, remainder = divmod(total, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _secs = divmod(remainder, 60)
    if days:
        return f"{days}d {hours}h {minutes:02d}m"
    if hours:
        return f"{hours}h {minutes:02d}m"
    return f"{minutes}m"

def read_memory() -> dict:
    """Return Linux memory summary using the kernel's MemAvailable estimate."""
    values: dict[str, int] = {}
    text = _read_text(PROC_MEMINFO)
    if text:
        for line in text.splitlines():
            if ":" not in line:
                continue
            key, remainder = line.split(":", 1)
            fields = remainder.strip().split()
            if not fields:
                continue
            try:
                number = int(fields[0])
            except ValueError:
                continue
            # /proc/meminfo is normally kB for these fields.
            multiplier = 1024 if len(fields) > 1 and fields[1].lower() == "kb" else 1
            values[key] = number * multiplier

    total = values.get("MemTotal")
    available = values.get("MemAvailable")
    if total is None:
        return {"available": False}

    if available is None:
        # Compatibility fallback for unusually old kernels.  Modern kernels
        # provide MemAvailable and that is preferred over hand-made estimates.
        available = sum(
            values.get(name, 0)
            for name in ("MemFree", "Buffers", "Cached", "SReclaimable")
        )
    available = max(0, min(total, available))
    used = max(0, total - available)
    percent = (used / total * 100.0) if total else 0.0
    return {
        "available": True,
        "total": total,
        "used": used,
        "available_bytes": available,
        "percent": percent,
        "source": "/proc/meminfo",
    }


def _millidegrees(value: int | None) -> float | None:
    if value is None:
        return None
    # hwmon and thermal sysfs temperatures are conventionally millidegrees C.
    result = value / 1000.0 if abs(value) > 1000 else float(value)
    if result < -50.0 or result > 200.0:
        return None
    return result


def _hwmon_temperatures() -> list[dict]:
    rows: list[dict] = []
    if not SYS_HWMON.is_dir():
        return rows
    try:
        devices = sorted(SYS_HWMON.glob("hwmon*"))
    except OSError:
        return rows
    for directory in devices:
        chip = _read_text(directory / "name") or directory.name
        try:
            inputs = sorted(directory.glob("temp*_input"))
        except OSError:
            continue
        for input_path in inputs:
            stem = input_path.name[: -len("_input")]
            temp = _millidegrees(_read_int(input_path))
            if temp is None:
                continue
            label = _read_text(directory / f"{stem}_label") or f"{chip} {stem}"
            crit = _millidegrees(_read_int(directory / f"{stem}_crit"))
            maximum = _millidegrees(_read_int(directory / f"{stem}_max"))
            rows.append(
                {
                    "label": label,
                    "chip": chip,
                    "celsius": temp,
                    "critical": crit,
                    "maximum": maximum,
                    "source": str(input_path),
                }
            )
    return rows


def _thermal_zone_temperatures() -> list[dict]:
    rows: list[dict] = []
    if not SYS_THERMAL.is_dir():
        return rows
    try:
        zones = sorted(SYS_THERMAL.glob("thermal_zone*"))
    except OSError:
        return rows
    for zone in zones:
        temp = _millidegrees(_read_int(zone / "temp"))
        if temp is None:
            continue
        label = _read_text(zone / "type") or zone.name
        critical = None
        try:
            trip_types = sorted(zone.glob("trip_point_*_type"))
        except OSError:
            trip_types = []
        for type_path in trip_types:
            kind = (_read_text(type_path) or "").lower()
            if kind not in {"critical", "hot"}:
                continue
            prefix = type_path.name[: -len("_type")]
            candidate = _millidegrees(_read_int(zone / f"{prefix}_temp"))
            if candidate is not None:
                critical = candidate if critical is None else min(critical, candidate)
        rows.append(
            {
                "label": label,
                "chip": "thermal",
                "celsius": temp,
                "critical": critical,
                "maximum": None,
                "source": str(zone / "temp"),
            }
        )
    return rows


def read_thermal() -> dict:
    """Return the hottest exposed sensor, favouring labelled hwmon data."""
    sensors = _hwmon_temperatures()
    if not sensors:
        sensors = _thermal_zone_temperatures()
    if not sensors:
        return {"available": False}
    hottest = max(sensors, key=lambda row: row["celsius"])
    return {
        "available": True,
        "label": hottest["label"],
        "celsius": hottest["celsius"],
        "critical": hottest.get("critical"),
        "maximum": hottest.get("maximum"),
        "sensor_count": len(sensors),
        "source": hottest.get("source"),
    }


def read_io_pressure() -> dict:
    """Return 10-second PSI I/O pressure averages from /proc/pressure/io."""
    text = _read_text(PROC_PRESSURE_IO)
    if not text:
        return {"available": False}
    parsed: dict[str, dict[str, float]] = {}
    for line in text.splitlines():
        fields = line.split()
        if not fields:
            continue
        category = fields[0]
        values: dict[str, float] = {}
        for field in fields[1:]:
            if "=" not in field:
                continue
            key, value = field.split("=", 1)
            try:
                values[key] = float(value)
            except ValueError:
                continue
        parsed[category] = values
    some = parsed.get("some", {}).get("avg10")
    full = parsed.get("full", {}).get("avg10")
    if some is None and full is None:
        return {"available": False}
    return {
        "available": True,
        "some_avg10": some,
        "full_avg10": full,
        "source": "/proc/pressure/io",
    }


def default_interface() -> str | None:
    """Find the kernel default-route interface without spawning `ip`."""
    text = _read_text(PROC_NET_ROUTE)
    candidates: list[tuple[int, str]] = []
    if text:
        for line in text.splitlines()[1:]:
            fields = line.split()
            if len(fields) < 8:
                continue
            iface, destination = fields[0], fields[1]
            if destination != "00000000" or iface == "lo":
                continue
            try:
                flags = int(fields[3], 16)
                metric = int(fields[6])
            except ValueError:
                continue
            if flags & 0x1:  # RTF_UP
                candidates.append((metric, iface))
    if candidates:
        candidates.sort(key=lambda item: (item[0], item[1]))
        return candidates[0][1]

    if SYS_CLASS_NET.is_dir():
        try:
            names = sorted(path.name for path in SYS_CLASS_NET.iterdir() if path.is_dir())
        except OSError:
            names = []
        for name in names:
            if name == "lo":
                continue
            state = _read_text(SYS_CLASS_NET / name / "operstate")
            if state == "up":
                return name
        for name in names:
            if name != "lo":
                return name
    return None


def read_interface_counters(interface: str | None = None) -> dict:
    interface = interface or default_interface()
    if not interface:
        return {"available": False}
    stats = SYS_CLASS_NET / interface / "statistics"
    rx = _read_int(stats / "rx_bytes")
    tx = _read_int(stats / "tx_bytes")
    if rx is None or tx is None:
        return {"available": False, "interface": interface}
    return {
        "available": True,
        "interface": interface,
        "rx_bytes": rx,
        "tx_bytes": tx,
        "source": str(stats),
    }


def _battery_direct_time(directory: Path, status: str) -> float | None:
    """Read kernel-provided time-to-empty/full where the driver exposes it."""
    status_lower = status.lower()
    path = directory / ("time_to_full_now" if status_lower == "charging" else "time_to_empty_now")
    value = _read_int(path)
    if value is None or value <= 0:
        return None
    # power_supply time attributes are seconds where exposed.
    return value / 3600.0


def _battery_estimated_time(directory: Path, status: str) -> float | None:
    status_lower = status.lower()
    charging = status_lower == "charging"
    discharging = status_lower == "discharging"
    if not (charging or discharging):
        return None

    # Keep like units together: energy/power or charge/current.  Ratios of the
    # usual micro-unit sysfs values produce hours directly.
    energy_now = _read_int(directory / "energy_now")
    energy_full = _read_int(directory / "energy_full")
    power_now = _read_int(directory / "power_now")
    if energy_now is not None and power_now and power_now > 0:
        numerator = (
            max(0, (energy_full or energy_now) - energy_now)
            if charging
            else energy_now
        )
        if numerator > 0:
            return numerator / power_now

    charge_now = _read_int(directory / "charge_now")
    charge_full = _read_int(directory / "charge_full")
    current_now = _read_int(directory / "current_now")
    if charge_now is not None and current_now and current_now > 0:
        numerator = (
            max(0, (charge_full or charge_now) - charge_now)
            if charging
            else charge_now
        )
        if numerator > 0:
            return numerator / current_now
    return None


def read_battery() -> dict:
    """Return the first kernel power-supply device explicitly typed Battery."""
    if not SYS_POWER.is_dir():
        return {"available": False}
    try:
        supplies = sorted(path for path in SYS_POWER.iterdir() if path.is_dir())
    except OSError:
        return {"available": False}
    for directory in supplies:
        if (_read_text(directory / "type") or "").lower() != "battery":
            continue
        present = _read_int(directory / "present")
        if present == 0:
            continue
        capacity = _read_int(directory / "capacity")
        status = _read_text(directory / "status") or "Unknown"
        hours = _battery_direct_time(directory, status)
        if hours is None:
            hours = _battery_estimated_time(directory, status)
        return {
            "available": True,
            "name": directory.name,
            "capacity": capacity,
            "status": status,
            "hours": hours,
            "source": str(directory),
        }
    return {"available": False}


class NetworkRateSampler:
    """Non-blocking network rate sampler for Dashboard use."""

    def __init__(self):
        self._previous: dict | None = None
        self._previous_time: float | None = None

    def reset(self):
        self._previous = None
        self._previous_time = None

    def sample(self) -> dict:
        current = read_interface_counters()
        now = time.monotonic()
        if not current.get("available"):
            self.reset()
            return current

        result = dict(current)
        result["primed"] = False
        previous = self._previous
        previous_time = self._previous_time
        self._previous = current
        self._previous_time = now

        if (
            previous is None
            or previous_time is None
            or previous.get("interface") != current.get("interface")
        ):
            result["primed"] = True
            result["rx_rate"] = None
            result["tx_rate"] = None
            return result

        elapsed = now - previous_time
        if elapsed <= 0:
            result["primed"] = True
            result["rx_rate"] = None
            result["tx_rate"] = None
            return result

        result["rx_rate"] = max(0.0, (current["rx_bytes"] - previous["rx_bytes"]) / elapsed)
        result["tx_rate"] = max(0.0, (current["tx_bytes"] - previous["tx_bytes"]) / elapsed)
        return result
