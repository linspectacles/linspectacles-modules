#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LinSpectacles Privileged Helpers Hub Module
# Copyright (C) 2026 brunonlinespace
# GPL-3.0-or-later

"""Central manager for applet-declared Privileged Helper Contract v1.

This module never starts a privileged inspection session and never imports an
applet. It consumes applet.json metadata through LinSpectacles Module API v4,
checks packaged/installed helper facts, contributes a compact Helpers page to
Configuration, and performs only explicit helper install/update/remove
operations through PolicyKit.
"""

from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

AMBER = "#d7a84b"
MUTED = "#b8b8b8"
ALLOWED_INSTALL_PREFIX = "/usr/libexec/linspectacles-"
ALLOWED_SESSION_MODELS = {"window_ephemeral", "in_place_ephemeral"}
PKEXEC_CANDIDATES = ("/usr/bin/pkexec", "/bin/pkexec")
INSTALL_CANDIDATES = ("/usr/bin/install", "/bin/install")
RM_CANDIDATES = ("/usr/bin/rm", "/bin/rm")
HELPER_DIRECTORY = Path("/usr/libexec")


@dataclass
class HelperDescriptor:
    applet_id: str
    applet_name: str
    applet_version: str
    applet_directory: Path
    contract: dict[str, Any]

    @property
    def helper_id(self) -> str:
        return str(self.contract.get("id") or "")

    @property
    def helper_name(self) -> str:
        return str(self.contract.get("name") or self.helper_id or "Privileged Helper")

    @property
    def required_version(self) -> str:
        return str(self.contract.get("version") or "Unknown")

    @property
    def publisher(self) -> str:
        return str(self.contract.get("publisher") or "Not declared")

    @property
    def install_path(self) -> str:
        return str(self.contract.get("install_path") or "")

    @property
    def expected_sha256(self) -> str:
        return str(self.contract.get("sha256") or "").strip().lower()

    @property
    def payload_path(self) -> Path | None:
        raw = str(self.contract.get("payload") or "")
        if not raw:
            return None
        rel = Path(raw)
        if rel.is_absolute() or ".." in rel.parts:
            return None
        candidate = self.applet_directory / rel
        try:
            candidate.resolve().relative_to(self.applet_directory.resolve())
        except (OSError, ValueError):
            return None
        return candidate

    @property
    def capabilities(self) -> list[dict[str, Any]]:
        raw = self.contract.get("capabilities", [])
        return [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []


@dataclass
class HelperStatus:
    state: str
    label: str
    installed: bool
    ready: bool
    packaged_ok: bool
    expected_sha256: str
    observed_sha256: str = ""
    owner: str = "—"
    mode: str = "—"
    message: str = ""


@dataclass
class OrphanedHelper:
    path: Path
    owner: str = "—"
    mode: str = "—"
    observed_sha256: str = ""
    message: str = "No currently discovered applet declares this helper path."

    @property
    def helper_name(self) -> str:
        return self.path.name


def discover_orphaned_helpers(
    descriptors: list[HelperDescriptor], directory: Path = HELPER_DIRECTORY
) -> list[OrphanedHelper]:
    """Return direct /usr/libexec/linspectacles-* entries not declared by current applets.

    Matching is by direct helper filename so the scanner can be tested against a
    temporary directory without weakening the production install-path contract.
    Nothing is removed automatically.
    """
    declared_names: set[str] = set()
    for desc in descriptors:
        target = Path(desc.install_path)
        if (
            target.parent == HELPER_DIRECTORY
            and target.name.startswith("linspectacles-")
            and target.name not in ("", ".", "..")
        ):
            declared_names.add(target.name)

    try:
        candidates = sorted(
            (path for path in directory.iterdir() if path.name.startswith("linspectacles-")),
            key=lambda path: path.name.casefold(),
        )
    except OSError:
        return []

    orphans: list[OrphanedHelper] = []
    for path in candidates:
        if path.name in declared_names:
            continue
        try:
            st = os.lstat(path)
        except OSError as exc:
            orphans.append(OrphanedHelper(path=path, message=f"Could not inspect orphaned helper candidate: {exc}"))
            continue
        # The namespace is for direct helper files. Ignore directories such as any
        # future linspectacles-* administrative tree; surface files/symlinks only.
        if stat.S_ISDIR(st.st_mode):
            continue
        owner = f"uid {st.st_uid}:gid {st.st_gid}"
        mode = oct(stat.S_IMODE(st.st_mode))
        observed = ""
        if stat.S_ISREG(st.st_mode) and not stat.S_ISLNK(st.st_mode):
            try:
                observed = sha256_file(path)
            except OSError:
                pass
        orphans.append(OrphanedHelper(path=path, owner=owner, mode=mode, observed_sha256=observed))
    return orphans


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def trusted_system_executable(candidates: tuple[str, ...]) -> str | None:
    for text in candidates:
        path = Path(text)
        try:
            st = os.lstat(path)
        except OSError:
            continue
        if (
            stat.S_ISREG(st.st_mode)
            and not stat.S_ISLNK(st.st_mode)
            and st.st_uid == 0
            and not (st.st_mode & 0o022)
            and os.access(path, os.X_OK)
        ):
            return str(path)
    return None


def validate_contract(desc: HelperDescriptor) -> tuple[bool, str]:
    c = desc.contract
    if int(c.get("schema") or 0) != 1:
        return False, "Unsupported privileged-helper contract schema."
    if not desc.helper_id:
        return False, "Helper ID is missing."
    if c.get("read_only") is not True:
        return False, "Central management is limited to helpers explicitly declared read-only."
    session_model = str(c.get("session_model") or "")
    if session_model not in ALLOWED_SESSION_MODELS:
        supported = ", ".join(sorted(ALLOWED_SESSION_MODELS))
        return False, f"Unsupported privileged-helper session model: {session_model or 'missing'}. Supported models: {supported}."
    target = desc.install_path
    if not target.startswith(ALLOWED_INSTALL_PREFIX):
        return False, f"Install path is outside the permitted LinSpectacles helper namespace: {target or 'missing'}"
    target_path = Path(target)
    if target_path.parent != Path("/usr/libexec") or target_path.name in ("", ".", ".."):
        return False, "Helper install path must be a direct /usr/libexec/linspectacles-* file."
    payload = desc.payload_path
    if payload is None:
        return False, "Packaged helper payload path is missing or unsafe."
    try:
        st = os.lstat(payload)
    except OSError as exc:
        return False, f"Packaged helper is unavailable: {exc}"
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
        return False, "Packaged helper must be a regular file and not a symbolic link."
    expected = desc.expected_sha256
    if len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected):
        return False, "Applet manifest does not declare a valid helper SHA-256."
    try:
        actual = sha256_file(payload)
    except OSError as exc:
        return False, f"Could not hash packaged helper: {exc}"
    if actual.lower() != expected:
        return False, "Packaged helper does not match the SHA-256 declared by the applet."
    return True, "Packaged helper matches its applet declaration."


def inspect_helper(desc: HelperDescriptor) -> HelperStatus:
    expected = desc.expected_sha256
    packaged_ok, packaged_message = validate_contract(desc)
    if not packaged_ok:
        return HelperStatus(
            state="invalid_contract", label="Package/contract problem", installed=False,
            ready=False, packaged_ok=False, expected_sha256=expected,
            message=packaged_message,
        )

    target = Path(desc.install_path)
    try:
        st = os.lstat(target)
    except FileNotFoundError:
        return HelperStatus(
            state="not_installed", label="Not installed", installed=False,
            ready=False, packaged_ok=True, expected_sha256=expected,
            message="Optional helper is not installed system-wide.",
        )
    except OSError as exc:
        return HelperStatus(
            state="invalid", label="Cannot inspect", installed=True, ready=False,
            packaged_ok=True, expected_sha256=expected,
            message=f"Could not inspect installed helper: {exc}",
        )

    owner = f"uid {st.st_uid}:gid {st.st_gid}"
    mode = oct(stat.S_IMODE(st.st_mode))
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
        return HelperStatus("invalid", "Invalid installed file", True, False, True, expected, owner=owner, mode=mode, message="Installed helper is a symbolic link or is not a regular file.")
    if st.st_uid != 0:
        return HelperStatus("invalid", "Ownership mismatch", True, False, True, expected, owner=owner, mode=mode, message="Installed helper is not owned by root.")
    if st.st_mode & 0o022:
        return HelperStatus("invalid", "Unsafe permissions", True, False, True, expected, owner=owner, mode=mode, message="Installed helper is writable by group or other users.")
    if not os.access(target, os.X_OK):
        return HelperStatus("invalid", "Not executable", True, False, True, expected, owner=owner, mode=mode, message="Installed helper is not executable.")
    try:
        observed = sha256_file(target)
    except OSError as exc:
        return HelperStatus("invalid", "Cannot verify", True, False, True, expected, owner=owner, mode=mode, message=f"Could not hash installed helper: {exc}")
    if observed.lower() != expected:
        return HelperStatus(
            "outdated", "Stale version", True, False, True, expected,
            observed_sha256=observed, owner=owner, mode=mode,
            message="Installed helper does not match the helper packaged with the currently installed applet version.",
        )
    return HelperStatus(
        "ready", "Installed and verified", True, True, True, expected,
        observed_sha256=observed, owner=owner, mode=mode,
        message=f"Installed helper matches the applet-declared payload for required version {desc.required_version}.",
    )


def discover_descriptors(context) -> list[HelperDescriptor]:
    descriptors: list[HelperDescriptor] = []
    for record in context.get_applet_metadata():
        if not isinstance(record, dict):
            continue
        raw = record.get("manifest")
        if not isinstance(raw, dict):
            continue
        contract = raw.get("privileged_helper")
        if not isinstance(contract, dict):
            continue
        try:
            directory = Path(str(record.get("directory") or "")).resolve()
        except (OSError, ValueError):
            continue
        descriptors.append(
            HelperDescriptor(
                applet_id=str(record.get("id") or raw.get("id") or ""),
                applet_name=str(record.get("name") or raw.get("name") or "Unknown applet"),
                applet_version=str(record.get("version") or raw.get("version") or "0"),
                applet_directory=directory,
                contract=dict(contract),
            )
        )
    return sorted(descriptors, key=lambda d: d.applet_name.casefold())


class HelperDetailsDialog(QDialog):
    """Less-frequent helper provenance and capability comparison details."""

    def __init__(self, desc: HelperDescriptor, status: HelperStatus, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Helper Details — {desc.applet_name}")
        self.resize(1040, 660)
        self.setMinimumSize(760, 500)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        heading = QLabel(desc.helper_name)
        f = heading.font(); f.setBold(True); f.setPointSize(max(f.pointSize(), 11)); heading.setFont(f)
        root.addWidget(heading)

        facts = QFrame()
        facts.setObjectName("helperFacts")
        facts.setStyleSheet("QFrame#helperFacts { background:#252526; border:1px solid #3f3f46; border-radius:6px; }")
        grid = QGridLayout(facts)
        grid.setContentsMargins(12, 10, 12, 10)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(5)
        rows = (
            ("Declared publisher", desc.publisher),
            ("Session model", str(desc.contract.get("session_model") or "Not declared")),
            ("Installed path", desc.install_path or "Not declared"),
            ("Observed ownership", status.owner),
            ("Observed mode", status.mode),
            ("Expected SHA-256", status.expected_sha256 or "Not declared"),
            ("Observed SHA-256", status.observed_sha256 or "—"),
        )
        for row, (title, value) in enumerate(rows):
            left = QLabel(title + ":")
            left.setStyleSheet("color:#9cdcfe; font-weight:600;")
            right = QLabel(str(value))
            right.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            right.setWordWrap(True)
            grid.addWidget(left, row, 0)
            grid.addWidget(right, row, 1)
        grid.setColumnStretch(1, 1)
        root.addWidget(facts)

        compare_heading = QLabel("Standard access vs optional privileged helper")
        cf = compare_heading.font(); cf.setBold(True); compare_heading.setFont(cf)
        root.addWidget(compare_heading)

        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["Information", "Standard access", "With helper", "Relationship"])
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setWordWrap(True)
        table.verticalHeader().setVisible(False)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        caps = desc.capabilities
        table.setRowCount(len(caps))
        for row, cap in enumerate(caps):
            relation = str(cap.get("kind") or "").replace("_", " ").title() or "Declared"
            fields = (
                str(cap.get("label") or cap.get("id") or "Capability"),
                str(cap.get("standard") or "Not described"),
                str(cap.get("elevated") or "Not described"),
                relation,
            )
            for col, value in enumerate(fields):
                item = QTableWidgetItem(value)
                if col == 2:
                    item.setForeground(QColor(AMBER))
                table.setItem(row, col, item)
        table.resizeRowsToContents()
        root.addWidget(table, 1)

        message = QLabel(
            status.message
            + " Privileged inspection sessions themselves remain applet-controlled and are never started from this manager."
        )
        message.setWordWrap(True)
        message.setStyleSheet(f"color:{MUTED};")
        root.addWidget(message)

        security = QLabel(
            "Integrity here means the packaged/installed file matches the SHA-256 declared by the applet. "
            "It does not cryptographically authenticate a third-party publisher. Central installation is restricted to read-only, ephemeral helper contracts "
            "using an established LinSpectacles session model and direct /usr/libexec/linspectacles-* targets."
        )
        security.setWordWrap(True)
        security.setStyleSheet(f"color:{MUTED};")
        root.addWidget(security)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        root.addWidget(buttons)


class PrivilegedHelpersPage(QWidget):
    """Compact Configuration page; detailed provenance lives behind Details."""

    def __init__(self, context, on_changed=None, parent=None):
        super().__init__(parent)
        self.context = context
        self.on_changed = on_changed
        self.descriptors: list[HelperDescriptor] = []
        self.statuses: list[HelperStatus] = []
        self.orphans: list[OrphanedHelper] = []
        self.process: QProcess | None = None
        self.pending_action: str | None = None
        self.pending_desc: HelperDescriptor | None = None
        self.pending_orphan: OrphanedHelper | None = None
        self._details_dialogs = []

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        heading = QLabel("Privileged Helpers")
        f = heading.font(); f.setBold(True); heading.setFont(f)
        root.addWidget(heading)

        note = QLabel(
            "Optional root-owned helpers extend read-only inspection for specific applets. This page also detects stale declared helpers and orphaned /usr/libexec/linspectacles-* helper files. Nothing is removed automatically."
        )
        note.setWordWrap(True)
        note.setStyleSheet(f"color:{MUTED};")
        root.addWidget(note)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Applet", "Helper", "Required", "Installed", "State"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.itemSelectionChanged.connect(self._selection_changed)
        self.table.itemDoubleClicked.connect(lambda *_: self._show_details())
        root.addWidget(self.table, 1)

        controls = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        controls.addWidget(self.refresh_btn)
        controls.addStretch(1)
        self.details_btn = QPushButton("Details...")
        self.details_btn.clicked.connect(self._show_details)
        controls.addWidget(self.details_btn)
        self.install_btn = QPushButton("Install Helper...")
        self.install_btn.clicked.connect(self._install_or_update)
        controls.addWidget(self.install_btn)
        self.remove_btn = QPushButton("Remove Helper...")
        self.remove_btn.clicked.connect(self._remove)
        controls.addWidget(self.remove_btn)
        root.addLayout(controls)

        self.refresh()

    def can_close_configuration(self):
        if self.process is not None and self.process.state() != QProcess.ProcessState.NotRunning:
            return False, "Wait for the current PolicyKit helper operation to finish before closing Configuration."
        return True, ""

    def current_index(self) -> int:
        rows = self.table.selectionModel().selectedRows() if self.table.selectionModel() else []
        return rows[0].row() if rows else -1

    def current(self) -> tuple[HelperDescriptor | None, HelperStatus | None]:
        row = self.current_index()
        if row < 0 or row >= len(self.descriptors):
            return None, None
        return self.descriptors[row], self.statuses[row]

    def current_orphan(self) -> OrphanedHelper | None:
        row = self.current_index() - len(self.descriptors)
        if row < 0 or row >= len(self.orphans):
            return None
        return self.orphans[row]

    def refresh(self):
        selected_key: tuple[str, str] | None = None
        desc, _status = self.current()
        orphan = self.current_orphan()
        if desc:
            selected_key = ("declared", desc.applet_id)
        elif orphan:
            selected_key = ("orphan", str(orphan.path))

        self.descriptors = discover_descriptors(self.context)
        self.statuses = [inspect_helper(desc) for desc in self.descriptors]
        self.orphans = discover_orphaned_helpers(self.descriptors)
        total_rows = len(self.descriptors) + len(self.orphans)
        self.table.blockSignals(True)
        self.table.setRowCount(total_rows)
        select_row = 0
        for row, (desc, status) in enumerate(zip(self.descriptors, self.statuses)):
            installed = desc.required_version if status.ready else ("Present" if status.installed else "—")
            values = [desc.applet_name, desc.helper_name, desc.required_version, installed, status.label]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setData(Qt.ItemDataRole.UserRole, desc.applet_id)
                self.table.setItem(row, col, item)
            if selected_key == ("declared", desc.applet_id):
                select_row = row

        offset = len(self.descriptors)
        for index, orphan in enumerate(self.orphans):
            row = offset + index
            values = ["—", orphan.helper_name, "—", "Present", "Orphaned helper"]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setData(Qt.ItemDataRole.UserRole, str(orphan.path))
                self.table.setItem(row, col, item)
            if selected_key == ("orphan", str(orphan.path)):
                select_row = row

        self.table.blockSignals(False)
        if total_rows:
            self.table.selectRow(min(select_row, total_rows - 1))
        self._selection_changed()
        if callable(self.on_changed):
            self.on_changed()

    def _selection_changed(self):
        desc, status = self.current()
        orphan = self.current_orphan()
        available = (desc is not None and status is not None) or orphan is not None
        self.details_btn.setEnabled(available)
        if orphan is not None:
            self.install_btn.setEnabled(False)
            self.install_btn.setText("Install Helper...")
            self.remove_btn.setEnabled(self.process is None)
            self.remove_btn.setText("Remove Orphan...")
            return
        self.remove_btn.setText("Remove Helper...")
        if desc is None or status is None:
            self.install_btn.setEnabled(False)
            self.remove_btn.setEnabled(False)
            return
        self.install_btn.setEnabled(status.packaged_ok and self.process is None)
        if not status.installed:
            self.install_btn.setText("Install Helper...")
        elif status.ready:
            self.install_btn.setText("Reinstall Helper...")
        else:
            self.install_btn.setText("Update / Repair Helper...")
        self.remove_btn.setEnabled(status.installed and self.process is None)

    def _show_details(self):
        orphan = self.current_orphan()
        if orphan is not None:
            digest = orphan.observed_sha256 or "Unavailable"
            QMessageBox.information(
                self,
                "Orphaned Privileged Helper",
                "No currently discovered applet declares this helper path.\n\n"
                f"Path: {orphan.path}\n"
                f"Owner: {orphan.owner}\n"
                f"Mode: {orphan.mode}\n"
                f"SHA-256: {digest}\n\n"
                "The module will never remove an orphan automatically. Use Remove Orphan... only if you intentionally want to delete this exact file.",
            )
            return
        desc, status = self.current()
        if not desc or not status:
            return
        dialog = HelperDetailsDialog(desc, status, self)
        self._details_dialogs.append(dialog)
        dialog.finished.connect(lambda _result, d=dialog: self._details_finished(d))
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def _details_finished(self, dialog):
        try:
            self._details_dialogs.remove(dialog)
        except ValueError:
            pass
        dialog.deleteLater()

    def _confirm(self, title: str, text: str) -> bool:
        return QMessageBox.question(
            self, title, text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes

    def _install_or_update(self):
        desc, status = self.current()
        if not desc or not status:
            return
        ok, reason = validate_contract(desc)
        if not ok:
            QMessageBox.warning(self, "Privileged Helpers", reason)
            return
        verb = "Reinstall" if status.ready else ("Update/repair" if status.installed else "Install")
        text = (
            f"{verb} {desc.helper_name}?\n\n"
            f"Applet: {desc.applet_name} {desc.applet_version}\n"
            f"Target: {desc.install_path}\n"
            f"Required helper version: {desc.required_version}\n\n"
            "PolicyKit will request administrator authorization. The GUI itself is not elevated. "
            "This operation copies only the applet-declared, SHA-256-verified helper to its fixed /usr/libexec/linspectacles-* path as root:root mode 0755.\n\n"
            "Installing the helper does not start privileged inspection."
        )
        if not self._confirm(f"{verb} Privileged Helper", text):
            return
        pkexec = trusted_system_executable(PKEXEC_CANDIDATES)
        install_bin = trusted_system_executable(INSTALL_CANDIDATES)
        if not pkexec or not install_bin:
            QMessageBox.warning(self, "Privileged Helpers", "Trusted pkexec/install executables were not found.")
            return
        payload = desc.payload_path
        if payload is None:
            QMessageBox.warning(self, "Privileged Helpers", "Packaged helper payload is unavailable.")
            return
        self._start_process(
            "install", desc, pkexec,
            [install_bin, "-o", "root", "-g", "root", "-m", "0755", "--", str(payload), desc.install_path],
        )

    def _remove(self):
        orphan = self.current_orphan()
        if orphan is not None:
            path = orphan.path
            if path.parent != HELPER_DIRECTORY or not path.name.startswith("linspectacles-"):
                QMessageBox.warning(self, "Privileged Helpers", "The orphan path is outside the permitted LinSpectacles helper namespace.")
                return
            text = (
                f"Remove orphaned helper?\n\nTarget: {path}\n\n"
                "No currently discovered applet declares this file. PolicyKit will request administrator authorization. "
                "Only this exact file will be removed; nothing is removed automatically."
            )
            if not self._confirm("Remove Orphaned Privileged Helper", text):
                return
            pkexec = trusted_system_executable(PKEXEC_CANDIDATES)
            rm_bin = trusted_system_executable(RM_CANDIDATES)
            if not pkexec or not rm_bin:
                QMessageBox.warning(self, "Privileged Helpers", "Trusted pkexec/rm executables were not found.")
                return
            self._start_process("remove_orphan", None, pkexec, [rm_bin, "-f", "--", str(path)], orphan=orphan)
            return

        desc, status = self.current()
        if not desc or not status or not status.installed:
            return
        ok, reason = validate_contract(desc)
        if not ok:
            if not desc.install_path.startswith(ALLOWED_INSTALL_PREFIX) or Path(desc.install_path).parent != HELPER_DIRECTORY:
                QMessageBox.warning(self, "Privileged Helpers", reason)
                return
        text = (
            f"Remove {desc.helper_name}?\n\n"
            f"Target: {desc.install_path}\n\n"
            "PolicyKit will request administrator authorization. Only this exact helper file will be removed. "
            "The applet will continue to work with ordinary-user inspection."
        )
        if not self._confirm("Remove Privileged Helper", text):
            return
        pkexec = trusted_system_executable(PKEXEC_CANDIDATES)
        rm_bin = trusted_system_executable(RM_CANDIDATES)
        if not pkexec or not rm_bin:
            QMessageBox.warning(self, "Privileged Helpers", "Trusted pkexec/rm executables were not found.")
            return
        self._start_process("remove", desc, pkexec, [rm_bin, "-f", "--", desc.install_path])

    def _start_process(self, action: str, desc: HelperDescriptor | None, program: str, args: list[str], orphan: OrphanedHelper | None = None):
        if self.process is not None:
            return
        proc = QProcess(self)
        self.process = proc
        self.pending_action = action
        self.pending_desc = desc
        self.pending_orphan = orphan
        proc.finished.connect(self._process_finished)
        proc.errorOccurred.connect(self._process_error)
        self.refresh_btn.setEnabled(False)
        self.details_btn.setEnabled(False)
        self.install_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        self.context.set_status("Waiting for PolicyKit authorization and privileged-helper file operation…")
        proc.start(program, args)

    def _finish_process_ui(self):
        if self.process is not None:
            self.process.deleteLater()
        self.process = None
        self.pending_action = None
        self.pending_desc = None
        self.pending_orphan = None
        self.refresh_btn.setEnabled(True)
        self.context.set_status("Privileged helper inventory refreshed.")
        self.refresh()

    def _process_finished(self, exit_code: int, _exit_status):
        proc = self.process
        action = self.pending_action or "operation"
        desc = self.pending_desc
        orphan = self.pending_orphan
        stderr = bytes(proc.readAllStandardError()).decode(errors="replace").strip() if proc else ""
        stdout = bytes(proc.readAllStandardOutput()).decode(errors="replace").strip() if proc else ""
        if exit_code != 0:
            QMessageBox.warning(
                self, "Privileged Helpers",
                stderr or stdout or "Authorization was cancelled or the helper operation failed.",
            )
        elif action == "remove_orphan" and orphan is not None:
            if orphan.path.exists() or orphan.path.is_symlink():
                QMessageBox.warning(self, "Privileged Helpers", "The orphaned helper still exists after the removal command completed.")
            else:
                QMessageBox.information(self, "Privileged Helpers", f"{orphan.helper_name} was removed.")
        elif desc:
            if action == "install":
                refreshed = inspect_helper(desc)
                if refreshed.ready:
                    QMessageBox.information(self, "Privileged Helpers", f"{desc.helper_name} is installed and matches the applet-declared helper payload.")
                else:
                    QMessageBox.warning(self, "Privileged Helpers", refreshed.message)
            elif Path(desc.install_path).exists():
                QMessageBox.warning(self, "Privileged Helpers", "The helper still exists after the removal command completed.")
            else:
                QMessageBox.information(self, "Privileged Helpers", f"{desc.helper_name} was removed.")
        self._finish_process_ui()

    def _process_error(self, _error):
        if self.process is None:
            return
        if self.process.state() == QProcess.ProcessState.NotRunning:
            QMessageBox.warning(self, "Privileged Helpers", self.process.errorString() or "Could not start the privileged helper operation.")
            self._finish_process_ui()


class PrivilegedHelpersModule:
    def __init__(self, context):
        self.context = context
        self.pages: list[PrivilegedHelpersPage] = []

    def activate(self):
        if int(getattr(self.context, "api_version", 0)) < 4 or not hasattr(self.context, "add_coverage_column"):
            raise RuntimeError("Privileged Helpers requires LinSpectacles Module API v4.")
        self.context.add_configuration_page("helpers", "Helpers", self._create_page)
        self.context.add_suite_state_item("Privileged helpers", self.suite_state_text)
        self.context.add_coverage_column("Helper", self.coverage_helper_state)
        self.context.subscribe("applets.changed", self._applets_changed)

    def deactivate(self):
        self.pages.clear()

    def _create_page(self, parent=None):
        page = PrivilegedHelpersPage(self.context, on_changed=self._page_changed, parent=parent)
        self.pages.append(page)
        page.destroyed.connect(lambda *_args, p=page: self._page_destroyed(p))
        return page

    def _page_destroyed(self, page):
        try:
            self.pages.remove(page)
        except ValueError:
            pass

    def _page_changed(self):
        # Dashboard providers are evaluated the next time the Dashboard updates.
        pass

    def _applets_changed(self, **_payload):
        for page in list(self.pages):
            try:
                page.refresh()
            except RuntimeError:
                self._page_destroyed(page)

    def _inventory(self):
        descriptors = discover_descriptors(self.context)
        statuses = [inspect_helper(d) for d in descriptors]
        return descriptors, statuses

    def suite_state_text(self):
        descriptors, statuses = self._inventory()
        total = len(descriptors)
        installed = sum(1 for status in statuses if status.installed)
        stale = sum(1 for status in statuses if status.state == "outdated")
        repair = sum(1 for status in statuses if status.installed and not status.ready and status.state != "outdated")
        orphaned = len(discover_orphaned_helpers(descriptors))
        if not total and not orphaned:
            return "0 available"
        text = f"{total} available · {installed} installed"
        if stale:
            text += f" · {stale} stale"
        if repair:
            text += f" · {repair} need repair"
        if orphaned:
            text += f" · {orphaned} orphaned"
        return text

    def coverage_helper_state(self, record):
        """Return the same State text used by the Helpers inventory table."""
        applet_id = str(record.get("id") or "") if isinstance(record, dict) else ""
        if not applet_id:
            return ""
        for descriptor in discover_descriptors(self.context):
            if descriptor.applet_id == applet_id:
                return inspect_helper(descriptor).label
        return ""


def create_module(context):
    return PrivilegedHelpersModule(context)
