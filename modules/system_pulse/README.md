# System Pulse 0.0.9

Optional live Dashboard summary for [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub) (Module API 1). It never appears in the sidebar or scans another inspector applet.

## What it shows

It reports a compact live summary of:

- System uptime from `/proc/uptime`.
- Memory usage from `/proc/meminfo`, preferring the kernel's `MemAvailable` estimate.
- The hottest exposed thermal sensor from hwmon/sysfs, including hardware-provided max/critical limits when available.
- Linux Pressure Stall Information for I/O from `/proc/pressure/io`.
- Receive/transmit throughput for the default active interface using sysfs counters and a non-blocking delta sampler.
- Battery capacity/status and a time estimate where the kernel exposes compatible power-supply data. The battery row disappears on systems without a battery.

Sampling runs only while the LinSpectacles Dashboard is selected and stops when the user opens an applet.
The module is read-only, requires no privileges, makes no network requests, and launches no subprocesses.

## Installation

- **Portable ZIP:** download this module's release ZIP, then in LinSpectacles Hub open **Configuration → Modules → Add Module...**, select the ZIP, and enable the module. The GitHub repository source ZIP is not an individual module release ZIP.
- **Fedora RPM:** install `linspectacles-module-system-pulse` from an enabled RPM repository carrying the package. The RPM installs into the Hub's package-managed module directory.

For packaging details, see [`packaging/rpm/README-RPM.md`](packaging/rpm/README-RPM.md). The Hub itself is available at [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub).

## Project and licence

Source: [https://github.com/linspectacles/linspectacles-modules](https://github.com/linspectacles/linspectacles-modules)  
Licence: GPL-3.0-or-later. Copyright © 2026 brunonlinespace.

## Release history

### 0.0.9 — Repository/RPM publication corrective

- Hardens the RPM builder so an existing user-selected build directory is never recursively deleted.
- Retains support for source paths containing spaces; a supplied `RPM_BUILD_ROOT` is now a **parent directory** for a unique temporary work tree.
- Updates repository documentation and provides a portable release ZIP packaging workflow.
- No System Pulse sampling, readings, or Dashboard runtime behaviour or inspection logic changes.

### 0.0.8 — RPM builder corrective

Corrects the in-tree RPM builder for source paths containing spaces by using a safe temporary `/var/tmp` work tree and quoting buildroot paths. Runtime behaviour is unchanged from 0.0.7 and the canonical 0.0.3 baseline.

### 0.0.7 — In-tree RPM builder

Adds the version-agnostic Fedora RPM builder; packaging-only update based on the canonical 0.0.3 source.

### 0.0.3 — First RPM-ready release

Packaging/distribution metadata only; functional behaviour unchanged from 0.0.2-r1. An earlier revision corrected identity/licensing metadata without functional changes.
