# Boot Environment 0.0.5

Optional, read-only Dashboard context for the **currently running boot** in [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub).

## What it shows

It reports, read-only and without privilege:

- current boot ID;
- running kernel release;
- architecture;
- current kernel command line;
- UEFI vs legacy/non-EFI interface and EFI platform width when exposed;
- Secure Boot state when the EFI variable is readable;
- the current boot loader Product reported by `bootctl status`, when available.

The module deliberately does **not** inspect boot timing, boot history, kernel messages, failed units, or detailed boot-loader entries/configuration. Those belong to dedicated inspectors.

Collection is intentionally lightweight and refreshes when the LinSpectacles Dashboard becomes active. No background daemon, privileged helper, network access, or state-changing operation is used.

## Data sources

- `/proc/sys/kernel/random/boot_id`
- `/proc/cmdline`
- Python platform/kernel interfaces
- `/sys/firmware/efi`
- `/sys/firmware/efi/fw_platform_size`
- `/sys/firmware/efi/efivars/SecureBoot-*`
- `bootctl status --no-pager` (Current Boot Loader → Product only)

## Installation

- **Portable ZIP:** download this module's release ZIP, then in LinSpectacles Hub open **Configuration → Modules → Add Module...**, select the ZIP, and enable the module. The GitHub repository source ZIP is not an individual module release ZIP.
- **Fedora RPM:** install `linspectacles-module-boot-environment` from an enabled RPM repository carrying the package. The RPM installs into the Hub's package-managed module directory.

For packaging details, see [`packaging/rpm/README-RPM.md`](packaging/rpm/README-RPM.md). The Hub itself is available at [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub).

## Project and licence

Source: [https://github.com/linspectacles/linspectacles-modules](https://github.com/linspectacles/linspectacles-modules)  
Licence: GPL-3.0-or-later. Copyright © 2026 brunonlinespace.

## Release history

### 0.0.5 — Repository/RPM publication corrective

- Hardens the RPM builder so an existing user-selected build directory is never recursively deleted.
- Retains support for source paths containing spaces; a supplied `RPM_BUILD_ROOT` is now a **parent directory** for a unique temporary work tree.
- Updates repository documentation and provides a portable release ZIP packaging workflow.
- No Boot Environment runtime behaviour or inspection logic changes.

### 0.0.4 — RPM builder corrective

- Corrects the in-tree RPM builder for source paths containing spaces using a safe `/var/tmp` work tree and quoted generated buildroot paths.
- No collection, Dashboard, source, or runtime behaviour changes.

### 0.0.3 — In-tree RPM builder

Adds the version-agnostic Fedora RPM builder in `packaging/rpm/`. Runtime identity collection and Dashboard behaviour are unchanged.

### 0.0.2 — First RPM-ready release

Packaging/distribution metadata only; runtime behaviour remains unchanged from 0.0.1-r1. An earlier revision also corrected identity/licensing metadata without functional changes.
