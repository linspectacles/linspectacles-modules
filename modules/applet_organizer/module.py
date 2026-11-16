#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2026 brunonlinespace
# GPL-3.0-or-later

import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)

# Permissive development catalogue. This enriches known applets only; it is
# never a whitelist. Any installed applet whose ID is absent here is retained
# under Unsorted and remains fully usable.
APPLET_CATALOG = {
    # Hardware and device-facing inspection.
    "block-devices": ("Block Devices", "Hardware", ["block", "devices", "partitions", "storage"]),
    "hardware-topology": ("Hardware Topology", "Hardware", ["cpu", "pci", "numa", "iommu"]),
    "gpu-inspector": ("GPU Inspector", "Hardware", ["gpu", "drm", "render nodes", "clients", "memory", "engines"]),
    "input-devices": ("Input Devices", "Hardware", ["input", "devices", "evdev", "capabilities", "hardware"]),
    "power-thermal-inspector": ("Power and Thermal Inspector", "Hardware", ["power", "thermal", "cooling", "cpufreq", "power supply"]),

    # Platform firmware inspection.
    "firmware-inspector": ("Firmware Inspector", "Firmware", ["firmware", "uefi", "dmi", "smbios", "acpi", "efi", "fwupd"]),
    "tpm-inspector": ("TPM Inspector", "Firmware", ["tpm", "pcr", "measured boot", "firmware"]),

    # Bootloader and early userspace.
    "boot-loaders": ("Boot Loaders", "Bootloader", ["boot", "efi", "esp", "loader"]),
    "boot-timing": ("Boot Timing", "Init", ["boot", "timing", "critical chain", "systemd"]),
    "initramfs-inspector": ("Initramfs Inspector", "Init", ["initramfs", "early userspace", "boot", "image"]),

    # Kernel-facing inspection.
    "cgroups-inspector": ("Cgroups Inspector", "Kernel", ["cgroups", "controllers", "limits", "pressure", "membership"]),
    "crypto-registry": ("Crypto Registry", "Kernel", ["crypto", "algorithms", "kernel"]),
    "cpu-vulnerabilities": ("CPU Vulnerabilities", "Kernel", ["cpu", "vulnerabilities", "mitigations", "security"]),
    "interrupts-inspector": ("Interrupts Inspector", "Kernel", ["interrupts", "irq", "softirq", "affinity", "cpu"]),
    "ipc-inspector": ("IPC Inspector", "Kernel", ["ipc", "pipes", "fifo", "sockets", "sysv", "mqueue"]),
    "kernel-modules": ("Kernel Modules", "Kernel", ["kernel", "modules", "drivers"]),
    "kernel-pressure": ("Kernel Pressure", "Kernel", ["psi", "pressure", "cpu", "memory", "io"]),
    "kernel-ring-buffer": ("Kernel Ring Buffer", "Kernel", ["kernel", "ring", "buffer", "kmsg"]),
    "kernel-tunables": ("Kernel Tunables", "Kernel", ["kernel", "sysctl", "proc sys", "runtime parameters"]),
    "namespace-inspector": ("Namespace Inspector", "Kernel", ["namespaces", "processes", "isolation", "proc"]),
    "scheduler-inspector": ("Scheduler Inspector", "Kernel", ["scheduler", "policy", "affinity", "schedstat", "sched_ext"]),
    "selinux-inspector": ("SELinux Inspector", "Kernel", ["selinux", "lsm", "security", "contexts", "policy"]),
    "timekeeping-inspector": ("Timekeeping Inspector", "Kernel", ["time", "clocks", "clocksource", "rtc", "synchronization"]),

    # Init/service-manager layer.
    "journal-inspector": ("Journal Inspector", "Init", ["journal", "journald", "logs", "systemd"]),
    "systemd-inspector": ("Systemd Inspector", "Init", ["systemd", "services", "units", "init"]),

    # General userland services and runtime state.
    "autostart-inspector": ("Autostart Inspector", "Userland", ["autostart", "startup", "systemd user", "xdg", "cron"]),
    "coredumps-inspector": ("Coredumps Inspector", "Userland", ["crash", "core", "signal", "coredumpctl"]),
    "dbus-inspector": ("D-Bus Inspector", "Userland", ["dbus", "bus", "services", "objects", "interfaces"]),
    "linux-resmon": ("Resource Monitor", "Userland", ["resource", "processes", "cpu", "memory", "disk", "network"]),
    "login-inspector": ("Login Inspector", "Userland", ["login", "sessions", "users", "seats", "logind"]),
    "resolver-inspector": ("Resolver Inspector", "Userland", ["dns", "resolver", "resolved", "nss", "name resolution"]),
    "virtualisation-inspector": ("Virtualisation Inspector", "Userland", ["virtualisation", "virtualization", "kvm", "libvirt", "qemu", "virtual machines", "vm", "guest", "hypervisor"]),
    "problem-finder": ("Problem Finder", "Multi-Layer", ["problems", "diagnostics", "health", "checks"]),

    # Display server/session stack.
    "display-server": ("Display Server", "Display Server", ["display", "wayland", "x11", "xwayland", "outputs", "modes", "protocols"]),

    # Desktop environment integration.
    "desktop-integration": ("Desktop Integration", "Desktop Environment", ["desktop entries", "mime", "associations", "xdg", "applications"]),
    "xdg-portals": ("XDG Portals", "Desktop Environment", ["xdg", "portals", "desktop", "backends", "configuration"]),

    # Shell and terminal environment.
    "environment-variables": ("Environment Variables", "Shell & Terminal", ["environment", "variables", "shell"]),
    "tty-inspector": ("TTY Inspector", "Shell & Terminal", ["tty", "pty", "terminal", "drivers", "line disciplines"]),

    # Filesystem and path-facing inspection.
    "file-handles": ("File Handles", "Filesystem", ["files", "handles", "inode", "filesystem"]),
    "filesystem-details": ("Filesystem Details", "Filesystem", ["filesystem", "ext4", "xfs", "btrfs", "allocation", "physical map"]),
    "mounted-filesystems": ("Mounted Filesystems", "Filesystem", ["mounts", "filesystem", "storage"]),
    "path-inspector": ("Path Inspector", "Filesystem", ["path", "access", "integrity", "usage", "filesystem"]),

    # Installed applications and language packages.
    "installed-software": ("Installed Software", "Applications", ["packages", "appimage", "flatpak", "software"]),
    "python-packages": ("Python Packages", "Applications", ["python", "pip", "packages"]),
}

# The Organizer's default model follows the Linux system stack. Empty layers
# are retained in the manager so future applets can land in the right place
# without redefining the model.
DEFAULT_GROUP_ORDER = [
    "Hardware",
    "Firmware",
    "Bootloader",
    "Kernel",
    "Init",
    "Userland",
    "Shell & Terminal",
    "Filesystem",
    "Display Server",
    "Desktop Environment",
    "Applications",
    "Multi-Layer",
    "Unsorted",
]

OLD_BUILTIN_GROUPS = {
    "Boot", "Monitoring", "Security", "Software", "Storage", "System"
}
ORGANIZATION_MODEL = "layers-v1"
CATALOG_DEFAULTS_VERSION = 1
DEFAULT_FAVORITES = {"problem-finder"}


class CategoryManagerDialog(QDialog):
    """Small organizer-only dialog for layer order and layout locking."""

    def __init__(self, order, locked, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Applet Layers — LinSpectacles")
        self.resize(420, 430)
        self.reset_requested = False

        root = QVBoxLayout(self)
        note = QLabel(
            "Reorder Linux system layers used by Applet Organizer. Layer assignment itself is edited "
            "directly in the Layer column on Configuration → Applets."
        )
        note.setWordWrap(True)
        root.addWidget(note)

        self.list = QListWidget()
        for name in order:
            self.list.addItem(str(name))
        if self.list.count():
            self.list.setCurrentRow(0)
        root.addWidget(self.list, 1)

        controls = QHBoxLayout()
        up = QPushButton("Up")
        down = QPushButton("Down")
        up.clicked.connect(lambda: self._move(-1))
        down.clicked.connect(lambda: self._move(1))
        controls.addWidget(up)
        controls.addWidget(down)
        reset = QPushButton("Reset Layers")
        reset.setToolTip("Restore canonical layer assignments and the default layer order. Favourites are unchanged.")
        reset.clicked.connect(self._reset_layers)
        controls.addStretch(1)
        controls.addWidget(reset)
        root.addLayout(controls)

        self.lock_box = QCheckBox("Lock layer layout")
        self.lock_box.setChecked(bool(locked))
        self.lock_box.setToolTip(
            "When locked, the Layer column remains visible but cannot be edited. Favourites remain available."
        )
        root.addWidget(self.lock_box)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _move(self, direction):
        row = self.list.currentRow()
        new_row = row + int(direction)
        if row < 0 or not 0 <= new_row < self.list.count():
            return
        item = self.list.takeItem(row)
        self.list.insertItem(new_row, item)
        self.list.setCurrentRow(new_row)

    def _reset_layers(self):
        self.reset_requested = True
        self.list.clear()
        for name in DEFAULT_GROUP_ORDER:
            self.list.addItem(name)
        if self.list.count():
            self.list.setCurrentRow(0)

    def values(self):
        return [self.list.item(i).text() for i in range(self.list.count())]


class OrganizerModule:
    def __init__(self, context):
        self.context = context
        self.data_path = context.storage_dir / "organizer.json"
        self.data = {
            "favorites": [],
            "category_overrides": {},
            "group_order": list(DEFAULT_GROUP_ORDER),
            "lock_layout": False,
            "organization_model": ORGANIZATION_MODEL,
            "catalog_defaults_version": 0,
        }
        self._records = []
        self._needs_model_migration = False
        self._needs_catalog_defaults = False
        self._load()

    def _load(self):
        try:
            raw = json.loads(self.data_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                self._needs_catalog_defaults = True
                return
            favorites = raw.get("favorites", [])
            if isinstance(favorites, list):
                self.data["favorites"] = [str(value) for value in favorites]
            overrides = raw.get("category_overrides", {})
            if isinstance(overrides, dict):
                self.data["category_overrides"] = {
                    str(key): str(value).strip()
                    for key, value in overrides.items()
                    if str(value).strip()
                }
            group_order = raw.get("group_order", [])
            if isinstance(group_order, list):
                cleaned = []
                for value in group_order:
                    text = str(value).strip()
                    if text and text not in cleaned:
                        cleaned.append(text)
                if cleaned:
                    self.data["group_order"] = cleaned
            self.data["lock_layout"] = bool(raw.get("lock_layout", False))
            try:
                defaults_version = int(raw.get("catalog_defaults_version", 0))
            except (TypeError, ValueError):
                defaults_version = 0
            self.data["catalog_defaults_version"] = max(0, defaults_version)
            if self.data["catalog_defaults_version"] < CATALOG_DEFAULTS_VERSION:
                self._needs_catalog_defaults = True
            if str(raw.get("organization_model", "")).strip() != ORGANIZATION_MODEL:
                self._needs_model_migration = True
            else:
                self.data["organization_model"] = ORGANIZATION_MODEL
        except (OSError, ValueError, TypeError):
            self._needs_catalog_defaults = True

    def _apply_catalog_defaults(self):
        favorites = set(self.data.get("favorites", []))
        favorites.update(DEFAULT_FAVORITES)
        self.data["favorites"] = sorted(favorites)
        self.data["catalog_defaults_version"] = CATALOG_DEFAULTS_VERSION

    def _migrate_to_layer_model(self):
        """Migrate the former mixed-purpose category model to system layers.

        Built-in legacy category assignments are replaced by each applet's new
        canonical layer. Truly custom user labels are retained and placed before
        Unsorted so explicit user organisation is not discarded.
        """
        overrides = dict(self.data.get("category_overrides", {}))
        migrated = {}
        custom_layers = []
        for applet_id, value in overrides.items():
            value = str(value or "").strip()
            if not value:
                continue
            if value in OLD_BUILTIN_GROUPS:
                canonical = APPLET_CATALOG.get(applet_id, (applet_id, "Unsorted", []))[1]
                if canonical != "Unsorted":
                    # No override is needed when adopting the canonical layer.
                    continue
                value = "Unsorted"
            migrated[applet_id] = value
            if value not in DEFAULT_GROUP_ORDER and value not in custom_layers:
                custom_layers.append(value)

        order = [value for value in DEFAULT_GROUP_ORDER if value != "Unsorted"]
        order.extend(custom_layers)
        order.append("Unsorted")
        self.data["category_overrides"] = migrated
        self.data["group_order"] = order
        self.data["organization_model"] = ORGANIZATION_MODEL

    def _derived_group_order(self):
        custom_layers = []
        for value in self.data.get("category_overrides", {}).values():
            text = str(value or "").strip()
            if text and text not in DEFAULT_GROUP_ORDER and text not in custom_layers:
                custom_layers.append(text)
        order = [value for value in DEFAULT_GROUP_ORDER if value != "Unsorted"]
        order.extend(custom_layers)
        order.append("Unsorted")
        return order

    def _save(self):
        self.data["organization_model"] = ORGANIZATION_MODEL
        self.data["catalog_defaults_version"] = CATALOG_DEFAULTS_VERSION
        payload = {
            "favorites": list(self.data.get("favorites", [])),
            "category_overrides": dict(self.data.get("category_overrides", {})),
            "lock_layout": bool(self.data.get("lock_layout", False)),
            "organization_model": ORGANIZATION_MODEL,
            "catalog_defaults_version": CATALOG_DEFAULTS_VERSION,
        }
        # Built-in layers and custom layers implied by assignments are derived.
        # Persist an explicit order only when the user has actually reordered it.
        current_order = list(self.data.get("group_order", []))
        if current_order != self._derived_group_order():
            payload["group_order"] = current_order
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            self.data_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        except OSError:
            pass

    def activate(self):
        # API 7 integrates Organizer into the Hub's one canonical Applets table.
        self._refresh_cache()
        changed = False
        if self._needs_model_migration:
            self._migrate_to_layer_model()
            self._refresh_cache()
            self._needs_model_migration = False
            changed = True
        if self._needs_catalog_defaults:
            self._apply_catalog_defaults()
            self._needs_catalog_defaults = False
            changed = True
        if changed:
            self._save()
        self.context.set_navigation_provider(self.navigation_model)
        self.context.add_applets_column(
            "favourite", "Favourite", self._favorite_value,
            self._favorite_changed, kind="check", editable=True,
        )
        self.context.add_applets_column(
            "category", "Layer", self._category_value,
            self._category_changed, kind="text", editable=self._category_editable,
        )
        self.context.add_applets_action(
            "manage-categories", "Manage Layers…", self._manage_categories
        )
        self.context.add_suite_state_item("Applet organization", self._suite_state_text)
        self.context.subscribe("configuration.changed", self._host_changed)

    def deactivate(self):
        pass

    def _catalog_definition(self, applet_id):
        known = APPLET_CATALOG.get(applet_id)
        if known is None:
            return applet_id, "Unsorted", []
        return known

    def _refresh_cache(self):
        # Keep every discovered physical applet instance. Organisation itself
        # remains keyed by the logical applet ID so Manual/Managed copies share
        # Favourite, Layer and tags without one installation overwriting another.
        installed = [dict(record) for record in self.context.get_applet_states()]
        overrides = self.data.get("category_overrides", {})
        records = []
        for state in installed:
            applet_id = str(state.get("id", "")).strip()
            if not applet_id:
                continue
            canonical_name, canonical_category, tags = self._catalog_definition(applet_id)
            category = str(overrides.get(applet_id, canonical_category) or "Unsorted").strip() or "Unsorted"
            records.append(
                {
                    "id": applet_id,
                    "instance_id": str(state.get("instance_id", applet_id)),
                    "name": state.get("name", canonical_name),
                    "canonical_category": canonical_category,
                    "category": category,
                    "tags": list(tags),
                    "enabled": bool(state.get("enabled")),
                    "version": state.get("version", "—"),
                    "source": state.get("source", ""),
                }
            )
        self._records = records
        self._normalize_group_order()

    def _normalize_group_order(self):
        order = []
        for value in self.data.get("group_order", []):
            text = str(value).strip()
            if text and text not in order:
                order.append(text)
        for value in DEFAULT_GROUP_ORDER:
            if value not in order:
                if value == "Multi-Layer" and "Unsorted" in order:
                    # Add the new built-in layer without reordering a saved layout.
                    order.insert(order.index("Unsorted"), value)
                else:
                    order.append(value)
        for record in self._records:
            category = record["category"]
            if category not in order:
                insert_at = order.index("Unsorted") if "Unsorted" in order else len(order)
                order.insert(insert_at, category)
        self.data["group_order"] = order

    def _host_changed(self, **_payload):
        self._refresh_cache()
        self.context.refresh_navigation()

    def _record_for_id(self, applet_id):
        return next((record for record in self._records if record["id"] == applet_id), None)

    def _favorite_value(self, applet_id):
        return applet_id in set(self.data.get("favorites", []))

    def _favorite_changed(self, applet_id, checked):
        favorites = set(self.data.get("favorites", []))
        if bool(checked):
            favorites.add(applet_id)
        else:
            favorites.discard(applet_id)
        self.data["favorites"] = sorted(favorites)
        self._save()
        self.context.refresh_navigation()

    def _category_value(self, applet_id):
        record = self._record_for_id(applet_id)
        return record["category"] if record is not None else "Unsorted"

    def _category_editable(self, _applet_id):
        return not bool(self.data.get("lock_layout", False))

    def _category_changed(self, applet_id, value):
        if bool(self.data.get("lock_layout", False)):
            return self._category_value(applet_id)
        record = self._record_for_id(applet_id)
        if record is None:
            return "Unsorted"
        value = str(value or "").strip()
        overrides = dict(self.data.get("category_overrides", {}))
        if not value:
            value = record["canonical_category"] or "Unsorted"
            overrides.pop(applet_id, None)
        elif value == record["canonical_category"]:
            overrides.pop(applet_id, None)
        else:
            overrides[applet_id] = value
        record["category"] = value
        self.data["category_overrides"] = overrides
        self._normalize_group_order()
        self._save()
        self.context.refresh_navigation()
        return value

    def _manage_categories(self, parent=None):
        self._refresh_cache()
        dialog = CategoryManagerDialog(
            self.data.get("group_order", DEFAULT_GROUP_ORDER),
            self.data.get("lock_layout", False),
            parent,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        if dialog.reset_requested:
            self.data["category_overrides"] = {}
            self.data["group_order"] = list(DEFAULT_GROUP_ORDER)
            self._refresh_cache()
        else:
            self.data["group_order"] = dialog.values()
        self.data["lock_layout"] = bool(dialog.lock_box.isChecked())
        self._normalize_group_order()
        self._save()
        self.context.refresh_navigation()

    def navigation_model(self):
        favorites = set(self.data.get("favorites", []))
        items = {}
        # Navigation metadata is logical-app-level.  Multiple physical copies
        # therefore contribute one organisation entry, while the Hub chooses
        # the presented Manual/Managed instance according to its own policy.
        for record in self._records:
            applet_id = record["id"]
            if applet_id in items or not record["enabled"]:
                continue
            items[applet_id] = {
                "group": record["category"] or "Unsorted",
                "tags": list(record["tags"]),
                "favorite": applet_id in favorites,
            }
        return {"items": items, "group_order": list(self.data.get("group_order", DEFAULT_GROUP_ORDER))}

    def _suite_state_text(self):
        favorites = set(self.data.get("favorites", []))
        logical = {}
        for record in self._records:
            logical.setdefault(record["id"], record)
        favourite_count = sum(1 for applet_id in logical if applet_id in favorites)
        unsorted = sum(1 for record in logical.values() if record["category"] == "Unsorted")
        return f"{favourite_count} favourites · {unsorted} unsorted"


def create_module(context):
    return OrganizerModule(context)
