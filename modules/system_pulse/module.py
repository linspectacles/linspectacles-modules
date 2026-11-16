#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LinSpectacles System Pulse Hub Module
# Copyright (C) 2026 brunonlinespace
# GPL-3.0-or-later

"""Dashboard-only System Pulse module for LinSpectacles Module API v1."""

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from .collector import (
    NetworkRateSampler,
    format_bytes,
    format_uptime,
    read_battery,
    read_io_pressure,
    read_memory,
    read_uptime,
    read_thermal,
)


class SystemPulseModule:
    REFRESH_MS = 2000

    def __init__(self, context):
        self.context = context
        self.card = None
        self.timer = None
        self.network = NetworkRateSampler()
        self.labels = {}
        self._dashboard_active = False

    def activate(self):
        self.card = self._build_card()
        self.context.add_dashboard_widget(self.card)
        self.context.subscribe("selection.changed", self._selection_changed)

        self.timer = QTimer(self.card)
        self.timer.setInterval(self.REFRESH_MS)
        self.timer.timeout.connect(self.refresh)

        # Dashboard is represented by no current applet ID in Module API v1.
        self._set_dashboard_active(self.context.current_applet_id() is None)

    def deactivate(self):
        if self.timer is not None:
            self.timer.stop()
        self.network.reset()

    def _build_card(self):
        card = QFrame()
        card.setObjectName("systemPulseCard")
        card.setStyleSheet(
            "QFrame#systemPulseCard { background:#252526; border:1px solid #3f3f46; "
            "border-radius:8px; }"
        )

        root = QVBoxLayout(card)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        heading = QLabel("System Pulse")
        heading_font = heading.font()
        heading_font.setBold(True)
        heading.setFont(heading_font)
        root.addWidget(heading)

        note = QLabel(
            "Live kernel-native summary. Sampling runs only while Dashboard is visible."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color:#b8b8b8;")
        root.addWidget(note)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(7)
        rows = (
            ("uptime", "Uptime"),
            ("memory", "Memory"),
            ("thermal", "Thermal"),
            ("io", "I/O Pressure"),
            ("network", "Network"),
            ("battery", "Battery"),
        )
        for row, (key, title) in enumerate(rows):
            title_label = QLabel(title + ":")
            title_label.setStyleSheet("color:#9cdcfe; font-weight:600;")
            value_label = QLabel("—")
            value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            value_label.setWordWrap(True)
            grid.addWidget(title_label, row, 0)
            grid.addWidget(value_label, row, 1)
            self.labels[key] = (title_label, value_label)
        grid.setColumnStretch(1, 1)
        root.addLayout(grid)
        return card

    def _selection_changed(self, applet_id=None, label=None, **_payload):
        self._set_dashboard_active(applet_id is None)

    def _set_dashboard_active(self, active):
        active = bool(active)
        if active == self._dashboard_active and self.timer is not None:
            return
        self._dashboard_active = active
        if not active:
            if self.timer is not None:
                self.timer.stop()
            self.network.reset()
            return

        self.network.reset()
        self.refresh()
        if self.timer is not None:
            self.timer.start()

    @staticmethod
    def _hours_text(hours, status):
        if hours is None or hours <= 0 or hours > 240:
            return ""
        total_minutes = max(1, int(round(hours * 60)))
        whole_hours, minutes = divmod(total_minutes, 60)
        if whole_hours:
            duration = f"~{whole_hours}h {minutes:02d}m"
        else:
            duration = f"~{minutes}m"
        if str(status).lower() == "charging":
            return duration + " to full"
        if str(status).lower() == "discharging":
            return duration + " left"
        return duration

    def refresh(self):
        if not self._dashboard_active or not self.labels:
            return

        uptime = read_uptime()
        if uptime.get("available"):
            self.labels["uptime"][1].setText(format_uptime(uptime.get("seconds")))
            self.labels["uptime"][1].setToolTip(str(uptime.get("source", "")))
        else:
            self.labels["uptime"][1].setText("Unavailable")
            self.labels["uptime"][1].setToolTip("")

        memory = read_memory()
        if memory.get("available"):
            self.labels["memory"][1].setText(
                f"{format_bytes(memory['used'])} / {format_bytes(memory['total'])} used "
                f"· {format_bytes(memory['available_bytes'])} available "
                f"· {memory['percent']:.1f}%"
            )
            self.labels["memory"][1].setToolTip(str(memory.get("source", "")))
        else:
            self.labels["memory"][1].setText("Unavailable")
            self.labels["memory"][1].setToolTip("")

        thermal = read_thermal()
        if thermal.get("available"):
            detail = f"{thermal['label']} · {thermal['celsius']:.1f} °C"
            critical = thermal.get("critical")
            maximum = thermal.get("maximum")
            if critical is not None:
                detail += f" · critical {critical:.1f} °C"
            elif maximum is not None:
                detail += f" · max {maximum:.1f} °C"
            self.labels["thermal"][1].setText(detail)
            self.labels["thermal"][1].setToolTip(str(thermal.get("source", "")))
        else:
            self.labels["thermal"][1].setText("Not exposed by this system")
            self.labels["thermal"][1].setToolTip("")

        pressure = read_io_pressure()
        if pressure.get("available"):
            some = pressure.get("some_avg10")
            full = pressure.get("full_avg10")
            pieces = []
            if some is not None:
                pieces.append(f"some {some:.2f}%")
            if full is not None:
                pieces.append(f"full {full:.2f}%")
            self.labels["io"][1].setText(" · ".join(pieces) + " · 10 s PSI")
            self.labels["io"][1].setToolTip(str(pressure.get("source", "")))
        else:
            self.labels["io"][1].setText("PSI unavailable")
            self.labels["io"][1].setToolTip("")

        network = self.network.sample()
        if network.get("available"):
            iface = network.get("interface", "—")
            if network.get("primed"):
                detail = f"{iface} · measuring throughput…"
            else:
                detail = (
                    f"{iface} · ↓ {format_bytes(network.get('rx_rate'), per_second=True)} "
                    f"· ↑ {format_bytes(network.get('tx_rate'), per_second=True)}"
                )
            self.labels["network"][1].setText(detail)
            self.labels["network"][1].setToolTip(str(network.get("source", "")))
        else:
            self.labels["network"][1].setText("No active interface detected")
            self.labels["network"][1].setToolTip("")

        battery = read_battery()
        battery_title, battery_value = self.labels["battery"]
        if battery.get("available"):
            battery_title.setVisible(True)
            battery_value.setVisible(True)
            pieces = []
            if battery.get("capacity") is not None:
                pieces.append(f"{battery['capacity']}%")
            pieces.append(str(battery.get("status") or "Unknown"))
            time_text = self._hours_text(battery.get("hours"), battery.get("status"))
            if time_text:
                pieces.append(time_text)
            battery_value.setText(" · ".join(pieces))
            battery_value.setToolTip(str(battery.get("source", "")))
        else:
            # Desktop systems should not carry a permanent "No battery" row.
            battery_title.setVisible(False)
            battery_value.setVisible(False)
            battery_value.setToolTip("")


def create_module(context):
    return SystemPulseModule(context)
