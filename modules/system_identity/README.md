# System Identity 0.0.5

Optional, read-only Dashboard identity card for [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub) (Module API 1).

## Fields

The card preserves LinSpectacles's existing System Identity visual layout while using this order:

- Distribution | System Age | Kernel
- Hostname | Desktop | Session

`System Age` replaces Architecture. It is **Derived** from the birth timestamp reported for the root directory (`stat -c %W /`): current Unix time minus that timestamp, displayed in whole days. This is a filesystem-based age indicator, not an authoritative OS installation date. If the filesystem does not expose a usable birth timestamp, the module reports `Unknown` rather than guessing from another source.

The module is read-only, unprivileged, has no network access, runs no background daemon, and refreshes when the Dashboard becomes active.

## Installation

- **Portable ZIP:** download this module's release ZIP, then in LinSpectacles Hub open **Configuration → Modules → Add Module...**, select the ZIP, and enable the module. The GitHub repository source ZIP is not an individual module release ZIP.
- **Fedora RPM:** install `linspectacles-module-system-identity` from an enabled RPM repository carrying the package. The RPM installs into the Hub's package-managed module directory.

For packaging details, see [`packaging/rpm/README-RPM.md`](packaging/rpm/README-RPM.md). The Hub itself is available at [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub).

## Project and licence

Source: [https://github.com/linspectacles/linspectacles-modules](https://github.com/linspectacles/linspectacles-modules)  
Licence: GPL-3.0-or-later. Copyright © 2026 brunonlinespace.

## Release history

### 0.0.5 — Repository/RPM publication corrective

- Hardens the RPM builder so an existing user-selected build directory is never recursively deleted.
- Retains support for source paths containing spaces; a supplied `RPM_BUILD_ROOT` is now a **parent directory** for a unique temporary work tree.
- Updates repository documentation and provides a portable release ZIP packaging workflow.
- No System Identity collection or Dashboard runtime behaviour or inspection logic changes.

### 0.0.4 — RPM builder corrective

- Corrects the in-tree RPM builder for source paths containing spaces, using a safe `/var/tmp` work tree and quoted buildroot paths.
- No System Identity collection, Dashboard, source or runtime behaviour changes.

### 0.0.3 — In-tree RPM builder

Adds the version-agnostic Fedora RPM builder. Runtime identity collection and Dashboard behaviour are unchanged.

### 0.0.2 — First RPM-ready release

Packaging/distribution metadata only; runtime behaviour unchanged from 0.0.1. An earlier revision updated identity/licensing metadata without functional changes.
