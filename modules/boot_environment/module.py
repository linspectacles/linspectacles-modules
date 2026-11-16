#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LinSpectacles Boot Environment Hub Module
# Copyright (C) 2026 brunonlinespace
# GPL-3.0-or-later

"""Dashboard-only Boot Environment module for LinSpectacles Module API v1."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from .collector import collect_boot_environment


class BootEnvironmentModule:
    def __init__(self, context):
        self.context = context
        self.card = None
        self.labels = {}
        self._dashboard_active = False

    def activate(self):
        self.card = self._build_card()
        self.context.add_dashboard_widget(self.card)
        self.context.subscribe("selection.changed", self._selection_changed)
        self._set_dashboard_active(self.context.current_applet_id() is None)

    def deactivate(self):
        self.labels.clear()

    def _build_card(self):
        card = QFrame()
        card.setObjectName("bootEnvironmentCard")
        card.setStyleSheet(
            "QFrame#bootEnvironmentCard { background:#252526; border:1px solid #3f3f46; "
            "border-radius:8px; }"
        )

        root = QVBoxLayout(card)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        heading = QLabel("Boot Environment")
        font = heading.font()
        font.setBold(True)
        heading.setFont(font)
        root.addWidget(heading)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(7)

        rows = (
            ("boot_id", "Boot ID"),
            ("kernel", "Kernel"),
            ("architecture", "Architecture"),
            ("cmdline", "Command line"),
            ("firmware", "Firmware"),
            ("secure_boot", "Secure Boot"),
            ("boot_loader", "Boot loader"),
        )
        for row, (key, title) in enumerate(rows):
            title_label = QLabel(title + ":")
            title_label.setStyleSheet("color:#9cdcfe; font-weight:600;")
            value_label = QLabel("—")
            value_label.setWordWrap(True)
            value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            grid.addWidget(title_label, row, 0, Qt.AlignmentFlag.AlignTop)
            grid.addWidget(value_label, row, 1)
            self.labels[key] = value_label
        grid.setColumnStretch(1, 1)
        root.addLayout(grid)
        return card

    def _selection_changed(self, applet_id=None, label=None, **_payload):
        self._set_dashboard_active(applet_id is None)

    def _set_dashboard_active(self, active):
        active = bool(active)
        if active == self._dashboard_active:
            return
        self._dashboard_active = active
        if active:
            self.refresh()

    def refresh(self):
        if not self.labels:
            return
        for record in collect_boot_environment():
            label = self.labels.get(record.get("key"))
            if label is None:
                continue
            label.setText(str(record.get("value") or "—"))
            label.setToolTip(str(record.get("source") or ""))


def create_module(context):
    return BootEnvironmentModule(context)
