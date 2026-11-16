# Applet Organizer 0.0.16

Applet Organizer is an optional, offline **Module API v7** extension for [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub). It organizes discovered applets without managing installations or scanning Linux itself.

## Features

- Mark applets as **Favourites** and assign them to system-stack **Layers**, such as Hardware, Kernel, Filesystem, Userland and Multi-Layer.
- Organize navigation in **Configuration → Applets**, including Manage Layers, layer order, and Reset Layers.
- Keep user-defined Layer overrides and Favourites across sessions; unknown applets remain under **Unsorted**.
- Treat User and Package-managed copies of the same logical applet as one organizational entry, while the Hub continues to display and manage each discovered copy separately.
- Put **Problem Finder** in the final built-in **Multi-Layer** category by default, without changing its Favourite status or overriding an existing user-assigned layer.
- Display **Display Server** by the name used in the organisation applet index; its technical ID stays `display-server`.
- Recognize **Virtualisation Inspector** under **Userland**, including libvirt/QEMU virtual machines, KVM host capabilities and current guest-environment inspection.
- Work offline, without automatically installing, updating or downloading applets.

**Compatibility:** Module API 7. Hub **0.2.2** provides Module API 8 with compatibility for earlier APIs; this does not require changing Organizer's declared API. The existing release history records Hub 0.0.9 as the minimum when API 7 was introduced.

## Installation

- **Portable ZIP:** download this module's release ZIP, then in LinSpectacles Hub open **Configuration → Modules → Add Module...**, select the ZIP, and enable the module. The GitHub repository source ZIP is not an individual module release ZIP.
- **Fedora RPM:** install `linspectacles-module-applet-organizer` from an enabled RPM repository carrying the package. The RPM installs into the Hub's package-managed module directory.

For packaging details, see [`packaging/rpm/README-RPM.md`](packaging/rpm/README-RPM.md). The Hub itself is available at [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub).

## Project and licence

Source: [https://github.com/linspectacles/linspectacles-modules](https://github.com/linspectacles/linspectacles-modules)  
Licence: GPL-3.0-or-later. Copyright © 2026 brunonlinespace.

## Release history

### 0.0.16 — Virtualisation Inspector catalogue addition

- Adds **Virtualisation Inspector 0.0.3** to the permissive catalogue using the Hub-normalized logical ID `virtualisation-inspector`.
- Its default layer is **Userland**. Search tags cover KVM, libvirt, QEMU, virtual machines, guests and hypervisors.
- Existing custom Layer assignments, Favourites, layer ordering and the Module API remain unchanged. Unknown applets continue under **Unsorted**.
- Retains `enabled_by_default: false`; no Hub, other-module, metapackage or inspector runtime changes.

### 0.0.15 — Catalogue and layer alignment

- Adds **Multi-Layer** as the final built-in layer (before **Unsorted**) and assigns **Problem Finder** to it by default, matching the LinSpectacles organisation applet index.
- Changes the catalogue display name **Display Server Inspector → Display Server** without changing its applet ID.
- Preserves existing user layer overrides and Favourites; a saved layer order gains the new layer before Unsorted without reordering existing entries. **Reset Layers** includes Multi-Layer.
- Retains `enabled_by_default: false`; default module activation is reserved for a later release.
- No module API, Hub integration, privilege behaviour, network behaviour, or inspection logic changes.

### 0.0.14 — Repository/RPM publication corrective

- Hardens the RPM builder so an existing user-selected build directory is never recursively deleted.
- Retains support for source paths containing spaces; a supplied `RPM_BUILD_ROOT` is now a **parent directory** for a unique temporary work tree.
- Updates repository documentation and provides a portable release ZIP packaging workflow.
- No Organizer runtime behaviour or inspection logic changes.

## 0.0.13

- Corrects the in-tree RPM builder so modules can be built from source paths containing spaces.
- RPM's internal `_topdir` now uses a safe temporary `/var/tmp` work tree and generated `%{buildroot}` shell paths are quoted.
- No Organizer catalogue, Favourite, Layer, persistence, navigation, or runtime behavior changes.

## 0.0.12

- Adds an in-tree, version-agnostic Fedora RPM builder under `packaging/rpm/`.
- The builder derives module identity/version from `module.json`, emits binary RPM + SRPM, and installs to the Hub Package-managed module store.
- No Organizer catalogue, Favourite, Layer, persistence, navigation, or runtime behavior changes.

## 0.0.11

- Adds **Filesystem Details → Filesystem** to the permissive applet catalogue using the Hub-normalized logical ID `filesystem-details`.
- Preserves all 0.0.10 catalogue additions, including Input Devices, TPM Inspector, TTY Inspector, Desktop Integration and XDG Portals.
- Existing user Layer overrides remain authoritative.
- No Favourite, Reset Layers, persistence, navigation, Module API, instance handling, layer-order, Hub integration, or other Organizer behavior changes.


## 0.0.10

- Adds **Input Devices → Hardware**, **TPM Inspector → Firmware**, **TTY Inspector → Shell & Terminal**, and **Desktop Integration / XDG Portals → Desktop Environment** to the permissive applet catalogue using Hub-normalized logical IDs.
- Firmware Inspector remains a single **Firmware** applet; its Microcode and Device Tree deepenings do not create new Organizer destinations.
- Existing user Layer overrides remain authoritative.
- No Favourite, Reset Layers, persistence, navigation, Module API, instance handling, layer-order, Hub integration, or other Organizer behavior changes.


## 0.0.9

- Corrects the Hub-normalized Coredumps applet catalogue ID from `coredumps` to `coredumps-inspector`, restoring **Coredumps Inspector → Userland**.
- No other catalogue assignment, Favourite, layer-reset, persistence, navigation, or Hub integration behavior changes.

## 0.0.8

- Adds **GPU Inspector → Hardware**, **Firmware Inspector → Firmware**, and **Display Server Inspector → Display Server** to the permissive applet catalogue using the Hub-normalized logical IDs.
- Retains the 0.0.7 CPU Vulnerabilities, Resource Monitor, Problem Finder Favourite, Reset Layers, and lean persistence behavior unchanged.
- Existing user Layer overrides remain authoritative; the new defaults apply when no user override exists.
- No Hub navigation API, applet discovery, installation, package-management, Favourite, persistence-model, or network behavior changes.


## 0.0.7

- Adds **Problem Finder** to the catalogue and makes it a **Favourite by default** through a one-time defaults migration; users can still unfavourite it normally afterwards.
- Adds **CPU Vulnerabilities → Kernel** and corrects the Resource Monitor catalogue ID to `linux-resmon`, restoring its **Userland** assignment.
- Adds **Reset Layers** to Manage Layers. Reset restores canonical applet layer assignments and the default layer order while leaving Favourites unchanged.
- Simplifies Organizer persistence: untouched built-in layer order and custom layers already implied by applet assignments are derived at runtime instead of being redundantly written to `organizer.json`; an explicit `group_order` is stored only after an actual user reorder.
- No Hub navigation API, applet discovery, installation, package-management or network behavior changes.

## 0.0.6

- Makes the Organizer instance-aware for Hub runtimes where Manual and Managed copies of the same logical applet can coexist.
- Retains every physical applet state record instead of collapsing duplicate logical IDs in the Organizer cache.
- Keeps **Favourite**, **Layer**, tags and grouped navigation intentionally keyed by logical applet identity, so duplicate installations share one organization model.
- Hub State counts logical applets rather than double-counting duplicate Manual/Managed installations.
- Does not alter catalogue assignments, layer ordering, favourites, navigation appearance or installation behavior.

## 0.0.5

- Requires LinSpectacles Hub 0.0.9 / Module API 7.
- Replaces the former mixed-purpose category defaults with a Linux system-stack **Layer** model:
  **Hardware → Firmware → Bootloader → Kernel → Init → Userland → Shell & Terminal → Filesystem → Display Server → Desktop Environment → Applications**.
- Keeps **Favourite** and organization directly in the Hub's single **Configuration → Applets** table; the visible organization column is now **Layer**.
- Renames **Manage Categories…** to **Manage Layers…** and retains layer ordering plus layout locking in the compact dialog.
- Adds current catalogue coverage for Cgroups Inspector, D-Bus Inspector, Interrupts Inspector, Kernel Tunables, Power and Thermal Inspector, Resolver Inspector, and Scheduler Inspector.
- Existing catalogue entries are reassigned to their primary inspected system layer rather than broad functional buckets such as System, Security, Storage, Monitoring, or Software.
- On first load from an older Organizer configuration, former built-in category ordering is migrated to the layered model. Favourites are preserved; genuinely custom user labels are retained as custom layers.
- No separate Organizer Configuration tab, duplicate applet grid, or separate Dashboard card is introduced.
- The catalogue remains offline and permissive; unknown installed applets remain under **Unsorted**.
- No download, install, package-manager, or automatic network behavior is added.
