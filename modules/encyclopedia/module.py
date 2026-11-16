#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LinSpectacles Encyclopedia Hub Module
# Copyright (C) 2026 brunonlinespace
# GPL-3.0-or-later

"""Offline Encyclopedia & What's This? module for LinSpectacles Module API v1."""

import html
import json
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSplitter, QTextBrowser, QVBoxLayout, QWidget
)


CONTEXT_TERMS = {
    "boot-inspector": [
        "boot.systemd", "boot.critical-chain", "boot.blame", "boot.initramfs",
        "kernel.command-line", "boot.boot-id", "boot.journal", "systemd.target",
    ],
    "kernel-modules": [
        "kernel.module", "kernel.builtin", "kernel.module-parameter", "kernel.module-alias",
        "kernel.vermagic", "kernel.module-signer", "kernel.module-dependency", "kernel.module-holder",
        "kernel.symbol", "kernel.kallsyms", "kernel.kptr-restrict", "kernel.taint", "kernel.firmware",
    ],
    "systemd-services": [
        "systemd.unit", "systemd.service", "systemd.active-state", "systemd.sub-state",
        "systemd.unit-file-state", "systemd.masked", "systemd.dependency", "systemd.requires",
        "systemd.wants", "systemd.after", "systemd.main-pid", "systemd.cgroup",
        "systemd.restart-policy", "systemd.no-new-privileges", "systemd.private-tmp",
        "systemd.protect-system", "systemd.security-score", "isolation.cgroup",
    ],
    "environment-variables": [
        "linux.environment", "env.path", "env.home", "env.locale", "env.xdg-config-home",
        "env.xdg-session-type", "env.ld-library-path", "linux.session-type",
    ],
    "mounted-filesystems": [
        "storage.mount", "storage.mount-point", "storage.filesystem", "storage.pseudo-filesystem",
        "storage.uuid", "storage.label", "storage.fstab", "storage.mount-options",
        "storage.read-only", "storage.bind-mount", "storage.overlayfs", "storage.tmpfs",
        "storage.inode", "storage.available-space", "storage.overmount",
    ],
    "selinux-inspector": [
        "selinux.selinux", "selinux.enforcing", "selinux.permissive", "selinux.context",
        "selinux.type", "selinux.domain", "selinux.boolean", "selinux.avc",
        "selinux.source-context", "selinux.target-context", "selinux.object-class",
        "selinux.permission", "selinux.policy", "selinux.policy-module", "selinux.permissive-domain",
        "selinux.login-mapping", "selinux.selinux-user", "selinux.port-context",
        "selinux.range", "security.lsm",
    ],
    "installed-software": [
        "packages.package", "packages.version", "packages.architecture", "packages.repository",
        "packages.dependency", "packages.reverse-dependency", "packages.signature", "packages.digest",
        "packages.rpm", "packages.flatpak", "packages.portal", "packages.runtime",
        "packages.appimage", "packages.appdir", "packages.squashfs",
    ],
    "python-packages": [
        "python.distribution", "python.import-package", "python.dist-info", "python.metadata-version",
        "python.requires-python", "python.requires-dist", "python.provides-extra", "python.entry-point",
        "python.console-script", "python.virtualenv", "python.site-packages", "python.editable",
        "python.namespace-package",
    ],
}

# Additive contextual mappings for newer/renamed LinSpectacles applets.
# Existing mappings above are intentionally retained for compatibility.
CONTEXT_TERMS.update({
    "systemd-inspector": [
        "systemd.unit", "systemd.unit-type", "systemd.load-state", "systemd.active-state",
        "systemd.sub-state", "systemd.unit-file-state", "systemd.fragment-path",
        "systemd.invocation-id", "systemd.failed-unit", "systemd.cgroup",
        "systemd.service", "systemd.mount-unit", "systemd.swap-unit", "systemd.socket-unit",
        "systemd.target", "systemd.device-unit", "systemd.automount-unit",
        "systemd.timer-unit", "systemd.path-unit", "systemd.slice-unit", "systemd.scope-unit",
        "systemd.security-score", "isolation.cgroup",
    ],
    "boot-history": [
        "boot.journal", "boot.boot-id", "journal.boot-index", "journal.record",
        "journal.realtime-timestamp", "journal.monotonic-timestamp", "linux.machine-id",
        "linux.hostname",
    ],
    "boot-timing": [
        "boot.systemd", "boot.critical-chain", "boot.blame", "systemd.activation-time",
        "systemd.unit", "systemd.target", "boot.initramfs",
    ],
    "kernel-messages": [
        "kernel.message", "kernel.ring-buffer", "kernel.dmesg", "journal.priority",
        "journal.transport", "kernel.subsystem", "kernel.device-metadata",
        "journal.boot-index", "boot.boot-id", "kernel.warning", "kernel.oops",
        "kernel.panic", "kernel.watchdog", "kernel.lockup", "kernel.mce", "kernel.pstore",
    ],
    "journal-inspector": [
        "boot.journal", "journal.record", "journal.field", "journal.priority",
        "journal.transport", "journal.identifier", "journal.systemd-unit",
        "journal.cursor", "journal.realtime-timestamp", "journal.monotonic-timestamp",
        "journal.message-id", "journal.json-output", "boot.boot-id", "systemd.invocation-id",
    ],
    "kernel-pressure": [
        "pressure.psi", "pressure.some", "pressure.full", "pressure.cpu", "pressure.memory",
        "pressure.io", "pressure.avg10", "pressure.avg60", "pressure.avg300",
        "pressure.total", "pressure.stall",
    ],
    "file-handles": [
        "process.file-descriptor", "process.open-file", "process.open-file-description",
        "fs.file-nr", "fs.file-max", "fs.inode-nr", "storage.inode",
    ],
    "coredumps-inspector": [
        "process.coredump", "process.signal", "process.signal-number",
        "coredump.storage", "coredump.corefile", "coredump.tool", "process.pid",
    ],
    "problems-inspector": [
        "systemd.failed-unit", "journal.priority", "kernel.warning", "problems.oom",
        "process.coredump", "pressure.psi", "fs.file-nr", "fs.inode-nr",
    ],
})

# Extend long-standing applet contexts without deleting any previous terms.
CONTEXT_TERMS["boot-inspector"] += [
    "boot.uefi", "boot.efi-system-partition", "boot.xbootldr", "boot.efi-variable",
    "boot.uefi-boot-manager", "boot.boot-loader-spec", "boot.loader-entry",
    "boot.systemd-boot", "boot.loader-random-seed", "hardware.secure-boot",
]
CONTEXT_TERMS["kernel-modules"] += ["kernel.modinfo"]

CONTEXT_TERMS["selinux-inspector"] += [
    "selinux.audit-event", "selinux.denied-permission",
]
CONTEXT_TERMS["installed-software"] += [
    "packages.package-manager", "packages.deb", "packages.dpkg",
    "packages.pacman", "packages.snap",
]
CONTEXT_TERMS["python-packages"] += [
    "python.project-metadata", "python.summary", "python.keywords", "python.trove-classifier",
]


# 0.0.3 contextual coverage for newer LinSpectacles applets and deepened inventories.
def _extend_context(applet_id, terms):
    bucket = CONTEXT_TERMS.setdefault(applet_id, [])
    for term in terms:
        if term not in bucket:
            bucket.append(term)

_extend_context("systemd-inspector", [
    "systemd.manager", "systemd.system-manager", "systemd.user-manager",
    "systemd.runtime-unit", "systemd.unit-file", "systemd.reverse-dependency",
    "systemd.before", "systemd.service-result", "systemd.exec-main-status",
    "systemd.timer-next-elapse", "systemd.unit-file-provenance",
])
_extend_context("mounted-filesystems", [
    "mount.mountinfo", "mount.mount-id", "mount.parent-id", "mount.root",
    "mount.major-minor", "mount.propagation", "mount.shared", "mount.master",
    "mount.unbindable", "storage.statvfs", "filesystem.error-forced-read-only",
])

CONTEXT_TERMS["filesystem-details"] = [
    "storage.filesystem", "storage.uuid", "mount.mountinfo",
    "filesystem.ext4-block-group", "filesystem.ext4-mb-groups",
    "filesystem.xfs-allocation-group", "filesystem.xfs-checked", "filesystem.xfs-sick",
    "filesystem.btrfs-space-class", "filesystem.btrfs-profile",
    "filesystem.btrfs-member-device", "filesystem.getfsmap", "filesystem.physical-map",
]
CONTEXT_TERMS["block-devices"] = [
    "storage.block-device", "storage.partition", "block.major-minor", "block.device-mapper",
    "block.md-raid", "block.holder", "block.slave", "block.loop", "block.zram",
    "block.partition-start", "block.partition-sectors", "block.mapping",
    "block.signature", "block.libblkid", "block.partuuid", "block.partlabel",
    "storage.logical-block-size", "storage.physical-block-size", "storage.rotational",
    "storage.scheduler", "storage.queue-depth",
]
CONTEXT_TERMS["path-inspector"] = [
    "security.dac", "security.posix-mode", "security.acl", "security.acl-mask",
    "security.effective-access", "security.file-capability", "security.sha256",
    "selinux.file-label", "selinux.file-context-rule", "selinux.file-context-check",
    "selinux.expected-file-context", "selinux.actual-file-context", "file.hard-link",
    "file.symlink", "file.link-count", "file.extended-attribute", "file.sparse",
    "file.apparent-size", "file.allocated-size", "file.device-id", "binary.elf",
    "binary.build-id", "file.printable-strings", "packages.package-ownership", "storage.inode",
]
CONTEXT_TERMS["namespace-inspector"] = [
    "isolation.namespace", "isolation.mount-namespace", "isolation.pid-namespace",
    "isolation.network-namespace", "isolation.ipc-namespace", "isolation.uts-namespace",
    "isolation.user-namespace", "isolation.cgroup-namespace", "isolation.time-namespace",
    "isolation.namespace-handle", "isolation.namespace-id", "isolation.nsfs",
    "isolation.parent-namespace", "isolation.owning-user-namespace",
    "isolation.pid-for-children", "isolation.time-for-children",
    "isolation.namespace-representative",
]
CONTEXT_TERMS["ipc-inspector"] = [
    "ipc.pipe", "ipc.pipe-end", "ipc.fifo", "ipc.dormant-fifo", "ipc.unix-socket",
    "ipc.abstract-unix-socket", "ipc.unnamed-unix-socket", "ipc.posix-message-queue",
    "ipc.mqueue-filesystem", "ipc.sysv", "ipc.sysv-shared-memory",
    "ipc.sysv-semaphore-set", "ipc.sysv-message-queue", "ipc.sysv-key", "ipc.sysv-id",
    "isolation.ipc-namespace", "isolation.network-namespace",
]
CONTEXT_TERMS["login-inspector"] = [
    "logind.systemd-logind", "logind.session", "logind.user", "logind.seat",
    "logind.manager", "linux.session-type", "process.pid",
]
CONTEXT_TERMS["timekeeping-inspector"] = [
    "time.posix-clock", "time.clock-resolution", "time.clock-realtime",
    "time.clock-monotonic", "time.clock-monotonic-raw", "time.clock-boottime",
    "time.clock-tai", "time.clock-process-cpu", "time.clock-thread-cpu", "time.clocksource",
    "time.current-clocksource", "time.available-clocksources", "time.adjtimex",
    "time.ntp-synchronized", "time.rtc", "time.hardware-clock",
    "time.systemd-timedated", "time.systemd-timesyncd", "time.timesync1",
]
CONTEXT_TERMS["autostart-inspector"] = [
    "autostart.desktop-entry", "autostart.xdg", "autostart.cron",
    "autostart.crontab", "autostart.cron-d", "autostart.anacron",
    "autostart.rc-local", "autostart.sysv-runlevel-link", "systemd.service",
    "systemd.timer-unit", "systemd.system-manager", "systemd.user-manager",
]
CONTEXT_TERMS["initramfs-inspector"] = [
    "boot.initramfs", "boot.initramfs-image", "boot.cpio-archive",
    "boot.initramfs-compression", "kernel.command-line",
]
CONTEXT_TERMS["boot-loaders"] = [
    "boot.bootctl", "boot.uefi", "boot.efi-system-partition", "boot.xbootldr",
    "boot.efi-variable", "boot.uefi-boot-manager", "boot.boot-loader-spec",
    "boot.loader-entry", "boot.systemd-boot", "boot.loader-random-seed",
    "hardware.secure-boot", "kernel.command-line",
]
CONTEXT_TERMS["hardware-topology"] = [
    "hardware.cpu-topology", "hardware.pci-address", "hardware.pci-id", "hardware.driver",
    "hardware.iommu-group", "hardware.numa", "hardware.numa-node",
    "hardware.numa-cpulist", "hardware.numa-cpumap", "hardware.numa-distance",
    "hardware.numastat", "hardware.numa-hit", "hardware.numa-miss",
    "hardware.numa-foreign", "hardware.numa-local-node", "hardware.numa-other-node",
    "hardware.numa-vmstat", "hardware.numa-meminfo", "hardware.numa-interleave-hit",
    "memory.huge-page", "memory.huge-page-pool",
    "hardware.cpu-vulnerability", "hardware.cpu-mitigation",
    "hardware.vulnerability-not-affected", "hardware.vulnerability-vulnerable",
    "hardware.vulnerability-unknown",
]
CONTEXT_TERMS["kernel-ring-buffer"] = [
    "kernel.ring-buffer", "kernel.kmsg-device", "kernel.printk", "kernel.message",
    "journal.priority",
]
CONTEXT_TERMS["linux-resmon"] = [
    "process.pid", "process.thread", "process.cpu-time", "process.file-descriptor",
    "process.open-file", "process.io-counters", "memory.rss", "memory.pss",
    "memory.uss", "memory.swap", "memory.memavailable", "memory.page-cache",
    "network.interface", "network.socket", "network.tcp", "network.udp",
    "network.listening-port", "systemd.cgroup", "isolation.cgroup",
]

CONTEXT_TERMS["crypto-registry"] = [
    "crypto.kernel-api", "crypto.proc-registry", "crypto.registration",
    "crypto.transformation", "crypto.algorithm-name", "crypto.driver-name",
    "crypto.algorithm-type", "crypto.priority", "kernel.module",
]

CONTEXT_TERMS["problem-finder"] = [
    "systemd.failed-unit", "journal.priority", "problems.oom", "fs.file-handle-exhaustion",
    "process.thread-capacity", "fs.space-exhaustion", "fs.inode-exhaustion",
    "network.rx-errors", "network.tx-errors", "network.rx-drops", "network.tx-drops",
    "network.carrier-errors", "network.fifo-errors", "network.frame-errors",
    "network.collisions", "network.conntrack-count", "network.conntrack-max",
    "block.md-degraded", "block.md-faulty-member", "block.md-sync-action",
    "filesystem.error-forced-read-only", "filesystem.xfs-sick",
    "hardware.edac", "hardware.corrected-ecc", "hardware.uncorrectable-ecc",
    "hardware.pcie-aer", "hardware.thermal-critical", "hardware.power-supply-health",
    "process.zombie", "process.uninterruptible-sleep", "process.rlimit-nofile",
    "isolation.memory-events", "isolation.pids-events", "isolation.cpu-stat",
    "kernel.threads-max", "kernel.pid-max", "kernel.aio-nr", "kernel.aio-max-nr",
    "kernel.inotify-max-watches", "kernel.inotify-max-instances", "memory.commit-limit",
    "memory.committed-as", "memory.swap-exhaustion", "memory.huge-page-pool",
    "filesystem.btrfs-error-counters", "packages.package-database",
    "packages.broken-dependency", "packages.interrupted-configuration",
]
_extend_context("problems-inspector", CONTEXT_TERMS["problem-finder"])


# 0.0.5 contextual coverage for the current LinSpectacles applet roster.
CONTEXT_TERMS["cgroups-inspector"] = [
    "isolation.cgroup", "isolation.controller", "isolation.subtree-control", "isolation.cgroup-procs",
    "isolation.cgroup-type", "isolation.cgroup-events", "isolation.cgroup-freeze",
    "isolation.cpu-max", "isolation.cpu-stat", "isolation.memory-current", "isolation.memory-high",
    "isolation.memory-max", "isolation.memory-events", "isolation.pids-current", "isolation.pids-max",
    "isolation.pids-events", "isolation.io-max", "isolation.cgroup-pressure",
    "pressure.cpu", "pressure.memory", "pressure.io",
]
CONTEXT_TERMS["dbus-inspector"] = [
    "dbus.message-bus", "dbus.bus-name", "dbus.well-known-name", "dbus.unique-name",
    "dbus.activatable-name", "dbus.object-path", "dbus.interface", "dbus.method",
    "dbus.property", "dbus.signal", "dbus.introspection",
]
CONTEXT_TERMS["interrupts-inspector"] = [
    "kernel.irq", "kernel.proc-interrupts", "kernel.softirq", "kernel.proc-softirqs",
    "kernel.irq-affinity", "kernel.irq-effective-affinity", "process.affinity",
]
CONTEXT_TERMS["kernel-tunables"] = [
    "kernel.sysctl", "kernel.proc-sys", "kernel.runtime-tunable", "kernel.persistent-sysctl",
    "kernel.threads-max", "kernel.pid-max", "kernel.aio-nr", "kernel.aio-max-nr",
    "kernel.inotify-max-watches", "kernel.inotify-max-instances",
]
CONTEXT_TERMS["power-thermal-inspector"] = [
    "hardware.thermal-zone", "hardware.trip-point", "hardware.thermal-critical",
    "hardware.cooling-device", "hardware.cpufreq-policy", "hardware.cpufreq-driver",
    "hardware.cpufreq-governor", "hardware.power-supply", "hardware.power-supply-health",
    "hardware.battery-capacity", "hardware.battery-status", "hardware.powercap-domain",
    "hardware.powercap-constraint", "hardware.energy-counter",
]
CONTEXT_TERMS["resolver-inspector"] = [
    "network.dns", "network.nameserver", "network.default-route", "network.systemd-resolved",
    "network.resolve1", "network.dnssec", "network.search-domain", "network.routing-domain",
    "network.per-link-dns", "network.resolver-cache", "network.nss",
]
CONTEXT_TERMS["scheduler-inspector"] = [
    "process.scheduling-policy", "process.sched-other", "process.sched-fifo", "process.sched-rr",
    "process.sched-deadline", "process.sched-ext", "process.affinity", "process.nice",
    "process.schedstat", "process.scheduler-domain", "process.runqueue-wait", "process.wakeup",
]


# 0.0.6 contextual coverage for CPU Vulnerabilities and the new firmware/display/GPU applets.
CONTEXT_TERMS["cpu-vulnerabilities"] = [
    "hardware.cpu-vulnerability", "hardware.cpu-mitigation",
    "hardware.vulnerability-not-affected", "hardware.vulnerability-vulnerable",
    "hardware.vulnerability-unknown",
]
CONTEXT_TERMS["display-server"] = [
    "linux.session-type", "env.xdg-session-type", "logind.session",
    "display.wayland", "display.x11", "display.xwayland", "display.compositor",
    "display.output", "display.mode", "display.refresh-rate", "display.scale",
    "display.wayland-protocol",
]
CONTEXT_TERMS["firmware-inspector"] = [
    "firmware.platform", "firmware.dmi-smbios", "firmware.acpi-table",
    "boot.uefi", "firmware.efivarfs", "boot.efi-variable", "hardware.secure-boot",
    "firmware.esrt", "firmware.fwupd-device", "firmware.update-history", "kernel.firmware",
]
CONTEXT_TERMS["gpu-inspector"] = [
    "gpu.drm", "gpu.drm-node", "gpu.primary-node", "gpu.render-node",
    "gpu.drm-client", "gpu.drm-fdinfo", "gpu.memory-region", "gpu.engine",
    "gpu.engine-busy-time", "gpu.device-memory", "hardware.pci-address",
    "hardware.driver", "hardware.iommu-group", "hardware.numa-node",
    "process.file-descriptor",
]


# 0.0.7 contextual coverage for the newest applets and Firmware Inspector deepenings.
CONTEXT_TERMS["tty-inspector"] = [
    "tty.tty", "tty.pty", "tty.controlling-terminal", "tty.driver", "tty.line-discipline",
    "tty.devpts", "tty.ptmx", "process.session-id", "process.process-group",
]
CONTEXT_TERMS["xdg-portals"] = [
    "packages.portal", "portal.frontend", "portal.backend", "portal.descriptor",
    "portal.impl-interface", "portal.config", "portal.default-backend",
    "portal.interface-override", "portal.usein", "portal.desktop-service", "portal.impl-namespace",
]
CONTEXT_TERMS["tpm-inspector"] = [
    "security.tpm", "security.tpm-resource-manager", "security.pcr", "security.pcr-bank",
    "security.measured-boot", "security.tpm-event-log", "security.tpm-securityfs-log",
]
CONTEXT_TERMS["input-devices"] = [
    "hardware.input-subsystem", "hardware.input-device", "hardware.evdev",
    "hardware.input-capability", "hardware.input-event-type", "hardware.input-key-capability",
    "hardware.input-relative-axis", "hardware.input-absolute-axis", "hardware.input-properties",
    "hardware.input-uniq",
]
CONTEXT_TERMS["desktop-integration"] = [
    "autostart.desktop-entry", "desktop.desktop-file-id", "desktop.exec", "desktop.tryexec",
    "desktop.hidden", "desktop.nodisplay", "desktop.onlyshowin", "desktop.notshowin",
    "desktop.action", "desktop.mime-type", "desktop.mime-association", "desktop.mime-applications",
    "desktop.mimeapps-list", "desktop.default-applications", "desktop.added-associations",
    "desktop.removed-associations", "desktop.mime-alias", "desktop.mime-subclass",
]
CONTEXT_TERMS["firmware-inspector"] += [
    "hardware.microcode", "firmware.microcode-revision", "firmware.microcode-loader",
    "firmware.intel-ucode", "firmware.amd-ucode", "firmware.device-tree", "firmware.dt-node",
    "firmware.dt-compatible", "firmware.dt-device-type", "firmware.dt-phandle",
    "firmware.dt-chosen", "firmware.dt-reserved-memory",
]


# 0.0.14: Virtualisation Inspector 0.0.3 context, using its Hub-normalized ID.
CONTEXT_TERMS["virtualisation-inspector"] = [
    "virt.virtual-machine", "virt.hypervisor", "virt.qemu", "virt.kvm",
    "virt.cpu-virtualisation-flags", "virt.kvm-device", "virt.kvm-modules",
    "virt.nested-virtualisation", "virt.libvirt", "virt.virsh-readonly",
    "virt.session-connection", "virt.system-connection", "virt.connection-access",
    "virt.libvirt-domain", "virt.domain-uuid", "virt.domain-state",
    "virt.domain-persistence", "virt.domain-autostart", "virt.virtual-cpu",
    "virt.configured-memory", "virt.domain-xml", "virt.domain-cpu-settings",
    "virt.domain-devices", "virt.domain-disk", "virt.domain-network",
    "virt.domain-snapshot", "virt.guest-vm-detection", "virt.guest-dmi-evidence",
    "virt.cpu-hypervisor-flag",
    "kernel.module", "firmware.dmi-smbios",
]


class KnowledgeBase:
    def __init__(self, root):
        self.root = Path(root)
        entries_doc = json.loads((self.root / "knowledge" / "entries.json").read_text(encoding="utf-8"))
        source_doc = json.loads((self.root / "knowledge" / "sources.json").read_text(encoding="utf-8"))
        self.title = entries_doc.get("title", "LinSpectacles Encyclopedia")
        self.version = entries_doc.get("version", "0")
        self.reviewed = entries_doc.get("reviewed", "")
        self.scope_note = entries_doc.get("scope_note", "")
        self.categories = list(entries_doc.get("categories", []))
        self.entries = list(entries_doc.get("entries", []))
        self.sources = dict(source_doc.get("sources", {}))
        self.by_id = {e["id"]: e for e in self.entries}

    def search(self, query="", category="All Categories", restrict_ids=None):
        q = str(query or "").strip().casefold()
        allowed = set(restrict_ids or ()) if restrict_ids is not None else None
        results = []
        for entry in self.entries:
            if allowed is not None and entry["id"] not in allowed:
                continue
            if category != "All Categories" and entry.get("category") != category:
                continue
            if q:
                hay = " ".join([
                    entry.get("term", ""), entry.get("category", ""), entry.get("summary", ""),
                    entry.get("details", ""), entry.get("why_it_matters", ""),
                    " ".join(entry.get("aliases", [])),
                ]).casefold()
                if q not in hay:
                    continue
            results.append(entry)
        return sorted(results, key=lambda e: e.get("term", "").casefold())


class EncyclopediaDialog(QDialog):
    def __init__(self, kb, parent=None, title="Encyclopedia", restrict_ids=None, initial_query=""):
        super().__init__(parent)
        self.kb = kb
        self.restrict_ids = list(restrict_ids) if restrict_ids is not None else None
        self.setWindowTitle(title)
        self.resize(980, 680)
        self.setMinimumSize(760, 500)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        self.heading = QLabel(title)
        font = self.heading.font(); font.setBold(True); font.setPointSize(max(font.pointSize(), 11)); self.heading.setFont(font)
        root.addWidget(self.heading)

        scope = QLabel(f"{len(kb.entries)} source-linked Linux terms · reviewed {kb.reviewed}. " + kb.scope_note)
        scope.setWordWrap(True)
        scope.setStyleSheet("color:#b8b8b8;")
        root.addWidget(scope)

        controls = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search term, alias or explanation...")
        self.search.setClearButtonEnabled(True)
        self.search.setText(initial_query)
        controls.addWidget(self.search, 1)
        self.category = QComboBox()
        self.category.addItem("All Categories")
        self.category.addItems(kb.categories)
        self.category.setMinimumWidth(210)
        controls.addWidget(self.category)
        root.addLayout(controls)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.list = QListWidget()
        self.list.setMinimumWidth(250)
        self.list.currentItemChanged.connect(self._selection_changed)
        splitter.addWidget(self.list)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        splitter.addWidget(self.browser)
        splitter.setSizes([300, 650])
        root.addWidget(splitter, 1)

        footer = QHBoxLayout()
        self.count = QLabel("")
        self.count.setStyleSheet("color:#b8b8b8;")
        footer.addWidget(self.count)
        footer.addStretch(1)
        self.encyclopedia_btn = None
        if self.restrict_ids is not None:
            self.encyclopedia_btn = QPushButton("← Encyclopedia")
            self.encyclopedia_btn.clicked.connect(self._open_full_encyclopedia)
            footer.addWidget(self.encyclopedia_btn)
        close = QPushButton("Close")
        close.clicked.connect(self.close)
        footer.addWidget(close)
        root.addLayout(footer)

        self.search.textChanged.connect(self.refresh_list)
        self.category.currentTextChanged.connect(self.refresh_list)
        self.refresh_list()

    def _open_full_encyclopedia(self):
        self.restrict_ids = None
        self.setWindowTitle("Encyclopedia")
        self.heading.setText("Encyclopedia")

        self.search.blockSignals(True)
        self.search.clear()
        self.search.blockSignals(False)
        self.category.blockSignals(True)
        self.category.setCurrentIndex(0)
        self.category.blockSignals(False)

        # Match a fresh Dashboard "Open Encyclopedia" view rather than merely
        # broadening the current contextual list.
        self.list.clear()
        self.refresh_list()
        if self.encyclopedia_btn is not None:
            self.encyclopedia_btn.hide()

    def refresh_list(self):
        current_id = None
        item = self.list.currentItem()
        if item is not None:
            current_id = item.data(Qt.ItemDataRole.UserRole)
        rows = self.kb.search(self.search.text(), self.category.currentText(), self.restrict_ids)
        self.list.blockSignals(True)
        self.list.clear()
        select_row = 0
        for i, entry in enumerate(rows):
            item = QListWidgetItem(entry["term"])
            item.setToolTip(entry.get("summary", ""))
            item.setData(Qt.ItemDataRole.UserRole, entry["id"])
            self.list.addItem(item)
            if entry["id"] == current_id:
                select_row = i
        self.list.blockSignals(False)
        self.count.setText(f"{len(rows)} of {len(self.kb.entries)} terms")
        if rows:
            self.list.setCurrentRow(min(select_row, len(rows)-1))
        else:
            self.browser.setHtml("<p>No matching encyclopedia entries.</p>")

    def _selection_changed(self, current, previous=None):
        if current is None:
            return
        entry = self.kb.by_id.get(current.data(Qt.ItemDataRole.UserRole))
        if entry:
            self.browser.setHtml(self._entry_html(entry))

    def _entry_html(self, entry):
        esc = html.escape
        aliases = entry.get("aliases", [])
        related = [self.kb.by_id[r]["term"] for r in entry.get("related", []) if r in self.kb.by_id]
        source_items = []
        for key in entry.get("sources", []):
            src = self.kb.sources.get(key)
            if not src:
                continue
            source_items.append(
                f'<li><a href="{esc(src["url"], quote=True)}">{esc(src["title"])}</a>'
                f' — {esc(src.get("publisher", ""))}</li>'
            )
        chunks = [
            f"<h2>{esc(entry['term'])}</h2>",
            f"<p><b>Category:</b> {esc(entry.get('category',''))}</p>",
            f"<p><b>Definition</b><br>{esc(entry.get('summary',''))}</p>",
            f"<p><b>In context</b><br>{esc(entry.get('details',''))}</p>",
        ]
        if entry.get("why_it_matters"):
            chunks.append(f"<p><b>Why it matters</b><br>{esc(entry['why_it_matters'])}</p>")
        if entry.get("caution"):
            chunks.append(f"<p><b>Be careful not to assume</b><br>{esc(entry['caution'])}</p>")
        if aliases:
            chunks.append(f"<p><b>Also known as</b><br>{esc(', '.join(aliases))}</p>")
        if related:
            chunks.append(f"<p><b>Related terms</b><br>{esc(' · '.join(related))}</p>")
        chunks.append("<h3>Sources</h3><ul>" + "".join(source_items) + "</ul>")
        chunks.append(f"<p style='color:#888'><small>Knowledge entry: {esc(entry['id'])} · library reviewed {esc(self.kb.reviewed)}</small></p>")
        return "".join(chunks)


class EncyclopediaModule:
    def __init__(self, context):
        self.context = context
        self.root = Path(__file__).resolve().parent
        self.kb = KnowledgeBase(self.root)
        self.dialogs = []
        self.card = None

    def activate(self):
        self.context.add_menu_action("help", "Encyclopedia", self.open_encyclopedia)
        self.context.add_menu_action("help", "What's This?", self.open_whats_this, "Shift+F1")
        self.card = self._build_dashboard_card()
        self.context.add_dashboard_widget(self.card)

    def deactivate(self):
        for dialog in list(self.dialogs):
            try: dialog.close()
            except Exception: pass
        self.dialogs.clear()

    def _build_dashboard_card(self):
        card = QFrame()
        card.setObjectName("encyclopediaCard")
        card.setStyleSheet("QFrame#encyclopediaCard { background:#252526; border:1px solid #3f3f46; border-radius:8px; }")
        root = QVBoxLayout(card)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(8)
        heading = QLabel("Encyclopedia")
        f = heading.font(); f.setBold(True); heading.setFont(f)
        root.addWidget(heading)
        note = QLabel(f"{len(self.kb.entries)} source-linked Linux terms available offline. Search without scanning any applet.")
        note.setWordWrap(True); note.setStyleSheet("color:#b8b8b8;")
        root.addWidget(note)
        row = QHBoxLayout()
        search = QLineEdit(); search.setPlaceholderText("Search Linux terminology..."); search.setClearButtonEnabled(True)
        button = QPushButton("Open Encyclopedia...")
        row.addWidget(search, 1); row.addWidget(button)
        root.addLayout(row)
        search.returnPressed.connect(lambda: self.open_encyclopedia(search.text()))
        button.clicked.connect(lambda: self.open_encyclopedia(search.text()))
        return card

    def _track(self, dialog):
        self.dialogs.append(dialog)
        dialog.finished.connect(lambda _result, d=dialog: self._forget(d))
        dialog.show(); dialog.raise_(); dialog.activateWindow()
        return dialog

    def _forget(self, dialog):
        try: self.dialogs.remove(dialog)
        except ValueError: pass
        dialog.deleteLater()

    def open_encyclopedia(self, query=""):
        # QAction passes a checked bool; ignore it.
        if isinstance(query, bool): query = ""
        dlg = EncyclopediaDialog(self.kb, title="Encyclopedia", initial_query=str(query or ""))
        self.context.set_status(f"Encyclopedia opened — {len(self.kb.entries)} terms available.")
        return self._track(dlg)

    def open_whats_this(self, checked=False):
        applet_id = self.context.current_applet_id()
        ids = CONTEXT_TERMS.get(applet_id)
        if ids:
            states = {s.get("id"): s for s in self.context.get_applet_states()}
            label = states.get(applet_id, {}).get("name", applet_id)
            title = f"What's This? — {label}"
            dlg = EncyclopediaDialog(self.kb, title=title, restrict_ids=ids)
            self.context.set_status(f"Context help opened for {label}.")
        else:
            dlg = EncyclopediaDialog(self.kb, title="What's This? — LinSpectacles")
            self.context.set_status("General LinSpectacles context help opened.")
        return self._track(dlg)


def create_module(context):
    return EncyclopediaModule(context)
