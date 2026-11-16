#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LinSpectacles System Identity Hub Module
# Copyright (C) 2026 brunonlinespace
# GPL-3.0-or-later

"""Dashboard-only System Identity module for LinSpectacles Module API v1."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from .collector import collect_system_identity


class SystemIdentityModule:
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
        # Deliberately mirrors the existing built-in System Identity dashboard
        # card so the later Hub extraction does not introduce a new UI dialect.
        card = QFrame()
        card.setObjectName("systemIdentityCard")
        card.setStyleSheet(
            "QFrame#systemIdentityCard { background:#252526; border:1px solid #3f3f46; "
            "border-radius:8px; }"
        )

        root = QVBoxLayout(card)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        heading = QLabel("System Identity")
        heading_font = heading.font()
        heading_font.setBold(True)
        heading.setFont(heading_font)
        root.addWidget(heading)

        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(7)

        # Two rows of three, preserving the existing card's visual grammar.
        # Requested first-row order: Distribution | System Age | Kernel.
        fields = (
            ("distribution", "Distribution"),
            ("system_age", "System Age"),
            ("kernel", "Kernel"),
            ("hostname", "Hostname"),
            ("desktop", "Desktop"),
            ("session", "Session"),
        )
        for index, (key, name) in enumerate(fields):
            row = index // 3
            col = (index % 3) * 2
            title = QLabel(name + ":")
            title.setStyleSheet("color:#9cdcfe; font-weight:600;")
            value = QLabel("—")
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            value.setWordWrap(True)
            grid.addWidget(title, row, col)
            grid.addWidget(value, row, col + 1)
            self.labels[key] = value

        for column in (1, 3, 5):
            grid.setColumnStretch(column, 1)
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
        for record in collect_system_identity():
            label = self.labels.get(record.get("key"))
            if label is None:
                continue
            label.setText(str(record.get("value") or "—"))
            label.setToolTip(str(record.get("source") or ""))


def create_module(context):
    return SystemIdentityModule(context)
