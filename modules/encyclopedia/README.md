# Encyclopedia & What's This? 0.0.14

An optional, offline reference and contextual-help module for [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub) (Module API 1).

## What it does

- Adds a discreet Dashboard search card for opening the full **Encyclopedia**.
- Provides contextual **What's This?** help (`Shift+F1`; surfaced by the Hub contextual action on Hub 0.2.0).
- Ships **665 offline, source-linked Linux definitions** across **10 categories**.
- Preserves all **628 definitions** and **152 source records** from 0.0.8, then adds **8 Crypto Registry definitions** and **2 Linux kernel Crypto API source records**.
- Adds **29 Virtualisation Inspector definitions** and contextual What's This? coverage for the four applet views, including KVM host signals, local libvirt/QEMU connections, VM configuration/devices/snapshots and current guest detection.
- Adds contextual What's This? coverage for **Filesystem Details** by reusing existing deep-filesystem terms rather than duplicating them.
- Reassigns only the file/folder SELinux context chooser terminology from **SELinux Inspector** to **Path Inspector**; broader SELinux coverage remains unchanged.

## Trust and privacy

The knowledge library is local JSON. Searching it makes no network request, performs no system probe and loads no applet. Clicking a source link intentionally opens that documentation in the user's browser.

The wording is deliberately conservative: availability varies by kernel configuration, distribution, permissions, namespace, filesystem, userspace version and hardware. The library describes evidence and interfaces without turning their mere presence into health or safety claims.

## Sources

See `knowledge/sources.json` and `SOURCES.md`. Entries carry source IDs that resolve to those records.

## Installation

- **Portable ZIP:** download this module's release ZIP, then in LinSpectacles Hub open **Configuration → Modules → Add Module...**, select the ZIP, and enable the module. The GitHub repository source ZIP is not an individual module release ZIP.
- **Fedora RPM:** install `linspectacles-module-encyclopedia` from an enabled RPM repository carrying the package. The RPM installs into the Hub's package-managed module directory.

For packaging details, see [`packaging/rpm/README-RPM.md`](packaging/rpm/README-RPM.md). The Hub itself is available at [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub).

## Project and licence

Source: [https://github.com/linspectacles/linspectacles-modules](https://github.com/linspectacles/linspectacles-modules)  
Licence: GPL-3.0-or-later. Copyright © 2026 brunonlinespace.

## Release history

### 0.0.14 — Virtualisation Inspector knowledge and contextual help

- Adds **29 source-linked definitions** covering Virtualisation Inspector 0.0.3: KVM and host capability signals; local `qemu:///session` and `qemu:///system` libvirt connections; domains, runtime state and configured resources; VM devices and snapshots; and current-guest detection.
- Adds **8 authoritative source records** from Linux kernel, libvirt and systemd documentation, bringing the library to **665 definitions / 162 sources / 10 categories**.
- Adds the Hub-normalized `virtualisation-inspector` What's This? context, reusing existing kernel-module and DMI concepts where appropriate.
- Preserves all previous **636 definitions, 154 sources, contexts and UI behaviour**. No scanning, network requests or privilege are added to Encyclopedia.


### 0.0.13 — Repository/RPM publication corrective

- Hardens the RPM builder so an existing user-selected build directory is never recursively deleted.
- Retains support for source paths containing spaces; a supplied `RPM_BUILD_ROOT` is now a **parent directory** for a unique temporary work tree.
- Updates repository documentation and provides a portable release ZIP packaging workflow.
- No changes to the knowledge library, contextual mappings, UI or runtime behaviour.

### 0.0.12 RPM builder corrective

This release corrects the in-tree RPM builder for source paths containing spaces. RPM's internal `_topdir` now uses a safe temporary `/var/tmp` work tree and generated `%{buildroot}` shell paths are quoted. The knowledge library, contextual mappings and Encyclopedia UI remain unchanged at **636 definitions / 154 source records**.

### 0.0.11 RPM builder update

This release adds an in-tree, version-agnostic Fedora RPM builder under `packaging/rpm/`. The knowledge library, contextual mappings and Encyclopedia UI remain unchanged at **636 definitions / 154 source records**.

### 0.0.10 contextual navigation update

This release changes only the contextual What's This? navigation:

- Removes the top-row **Show All Terms → Showing All Terms** control.
- Adds **← Encyclopedia** in the bottom-right footer immediately before **Close** when the dialog is opened in applet-specific What's This? mode.
- **← Encyclopedia** restores the same full Encyclopedia state as a fresh Dashboard **Open Encyclopedia** action: unrestricted catalogue, empty search, **All Categories**, and the normal **Encyclopedia** title.
- The back button disappears after returning to the full Encyclopedia view.
- The knowledge library is unchanged at **636 definitions / 154 source records**.

### 0.0.9 context-link and Crypto Registry update

This release repairs three contextual What's This? links and adds focused Crypto Registry terminology sourced from the Linux kernel Crypto API documentation:

- **Resource Monitor** — context key corrected to the Hub-normalized `linux-resmon` ID.
- **Coredumps Inspector** — context key corrected to the Hub-normalized `coredumps-inspector` ID.
- **Crypto Registry** — adds contextual coverage for the Kernel Crypto API, `/proc/crypto` registry/registration, transformation, algorithm name, implementation driver name, type and priority, while reusing the existing Kernel module term for the reported module field.
- Adds **8 definitions** and **2 source records**; all 0.0.8 definitions and source records remain preserved.

No applet probing, UI behavior or existing knowledge wording is changed.

### 0.0.8 contextual ownership update

This release preserves the complete 0.0.7 knowledge library — **628 definitions** and **152 source records** — and changes only contextual ownership for the newest filesystem work:

- **Filesystem Details** — receives the existing deep filesystem structural terminology previously attached to Mounted Filesystems: ext4 block groups / `mb_groups`, XFS allocation-group health, Btrfs space/profile/member-device concepts, `FS_IOC_GETFSMAP`, and physical filesystem maps.
- **Mounted Filesystems** — keeps mount inventory, topology, propagation, capacity/statvfs and mount-state terminology; it no longer claims the deep filesystem-structure terms spun out into Filesystem Details.
- **Path Inspector** — now owns the file/folder SELinux context chooser terminology: file label, file-context rule, expected context, actual context and file-context check.
- **SELinux Inspector** — retains all broader SELinux terminology; only the file/folder context chooser context moved.

No definitions or source records were added, removed or rewritten. The Encyclopedia UI and offline/no-probing behavior are unchanged.

### 0.0.7 knowledge expansion

This release preserves the complete 0.0.6 library and adds **64 definitions** plus contextual mappings for the newest inspectors and Firmware Inspector deepenings:

- **TTY Inspector** — TTY/PTY endpoints, controlling terminals, TTY drivers, line disciplines, devpts/ptmx, process sessions and process groups.
- **XDG Portals** — reuses the existing Desktop portal term and adds frontend/backend, `.portal` descriptors, implementation interfaces, `portals.conf`, selection overrides and runtime service namespaces.
- **TPM Inspector** — TPM/resource-manager devices, PCRs/banks, measured boot and firmware event-log evidence.
- **Input Devices** — Linux input subsystem, evdev nodes, capability bitmaps, event/code families, properties and the potentially identifying `uniq` field.
- **Desktop Integration** — reuses the existing Desktop entry term and adds desktop-file IDs/keys/actions plus MIME application/default/association resolution.
- **Firmware Inspector 0.0.4** — reuses the existing CPU microcode term and adds loaded revision/loader/local firmware evidence plus Device Tree nodes/properties and special nodes.

Existing entries, source records and contextual mappings are preserved. The evidence boundaries remain explicit: registry/capability/configuration presence is not promoted into activity, success, trust, driver-binding, mitigation or application verdicts. The Encyclopedia UI and offline/no-probing behavior are unchanged.

### 0.0.6 knowledge expansion

This release preserves the complete 0.0.5 library and adds **26 definitions** plus contextual mappings for the newest inspectors:

- **CPU Vulnerabilities** — wires the existing kernel-reported vulnerability/mitigation definitions into contextual What's This? help.
- **Display Server Inspector** — Wayland, X11, XWayland, compositor, outputs, modes, refresh rate, scale and protocol advertisements.
- **Firmware Inspector** — platform firmware, DMI/SMBIOS, ACPI tables, efivarfs, ESRT, fwupd devices and update history, alongside existing UEFI/EFI/Secure Boot terms.
- **GPU Inspector** — DRM, primary/render nodes, DRM clients/fdinfo, memory regions, engines, busy-time counters and device-level GPU memory.

Existing entries, source records and contextual mappings are preserved. This remains additive knowledge coverage; the Encyclopedia UI and offline/no-probing behavior are unchanged.

### 0.0.5 knowledge expansion

This release adds terminology actually exposed by the current applets:

- **Cgroups Inspector** — cgroup type/events/freezer state, `cpu.max`, `memory.high`, `io.max`, and per-cgroup PSI.
- **D-Bus Inspector** — message buses, well-known/unique/activatable names, object paths, interfaces, methods, properties, signals and introspection.
- **Interrupts Inspector** — IRQs, `/proc/interrupts`, SoftIRQs, `/proc/softirqs`, configured IRQ affinity and effective affinity.
- **Kernel Tunables** — sysctl, `/proc/sys`, live runtime tunables and persistent sysctl assignment evidence.
- **Power and Thermal Inspector** — cooling devices, CPUFreq policies/drivers/governors, power supplies and power-cap domains/constraints/energy counters.
- **Resolver Inspector** — systemd-resolved, `org.freedesktop.resolve1`, DNSSEC, search/routing domains, per-link DNS, resolver cache and NSS.
- **Scheduler Inspector** — scheduling policies, SCHED_OTHER/FIFO/RR/DEADLINE/EXT, schedstat, scheduler domains, runqueue wait and wakeups.

Existing entries, source records and contextual mappings are preserved. This is additive knowledge coverage; the Encyclopedia UI and offline/no-probing behavior are unchanged.

### Earlier versions

- **0.0.4** — First RPM-ready release; packaging/distribution metadata only.
- **0.0.3-r1** — LinSpectacles identity/licensing compliance correction.
- **0.0.3** — Major knowledge expansion for the preceding specialist applet wave.
