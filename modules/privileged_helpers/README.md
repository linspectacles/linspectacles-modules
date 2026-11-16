# Privileged Helpers — LinSpectacles Hub Module

Version **0.0.8** · Module API **v4** · GPLv3-or-later

Privileged Helpers is an optional Hub-level manager for applet-declared **Privileged Helper Contract v1** metadata.

It does not run an applet, start an elevated inspection session, or perform subsystem scans. It integrates into existing Hub surfaces instead of adding its own Dashboard card:

- **Configuration → Helpers** contains the helper inventory and Refresh / Details / Install-Update-Reinstall / Remove actions;
- **Hub State** receives a compact helper count/status line;
- **Inspection Coverage → Helper** reports the exact current helper state for each applicable applet, using the same text as Configuration → Helpers → State;
- direct `/usr/libexec/linspectacles-*` files not declared by any currently discovered applet are surfaced as **Orphaned helper** rows.

The less-frequent provenance and explanatory material is deliberately behind **Details...**: declared publisher, fixed install path, observed ownership/mode, expected and observed SHA-256, and the applet-declared **Standard access vs With helper** capability comparison. A declared helper whose installed SHA-256 no longer matches the currently packaged payload is shown explicitly as **Stale version**. Orphaned helper details show the exact undeclared path, ownership/mode and SHA-256 where readable.

Installing a helper is distinct from using privilege. Privileged sessions remain controlled by each applet and are ephemeral to that applet's declared presentation model; the Hub module never starts an elevated inspection session.

## Safety boundary

Central installation is limited to contracts that declare:

- schema 1;
- `read_only: true`;
- an established ephemeral session model: `window_ephemeral` or `in_place_ephemeral`;
- a regular packaged helper whose SHA-256 matches the applet manifest;
- a direct `/usr/libexec/linspectacles-*` install path.

The module uses fixed `pkexec + install` and `pkexec + rm` operations. It has no arbitrary command runner and does not run the helper itself. Orphan detection is read-only; orphan removal is always an explicit user action against one exact direct `/usr/libexec/linspectacles-*` path, and the module never removes stale or orphaned files automatically.

The SHA-256 check proves package consistency with the applet declaration; it is **not** presented as cryptographic publisher authentication for third-party applets.

## Installation

- **Portable ZIP:** download this module's release ZIP, then in LinSpectacles Hub open **Configuration → Modules → Add Module...**, select the ZIP, and enable the module. The GitHub repository source ZIP is not an individual module release ZIP.
- **Fedora RPM:** install `linspectacles-module-privileged-helpers` from an enabled RPM repository carrying the package. The RPM installs into the Hub's package-managed module directory.

For packaging details, see [`packaging/rpm/README-RPM.md`](packaging/rpm/README-RPM.md). The Hub itself is available at [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub).

## Project and licence

Source: [https://github.com/linspectacles/linspectacles-modules](https://github.com/linspectacles/linspectacles-modules)  
Licence: GPL-3.0-or-later. Copyright © 2026 brunonlinespace.

## Release history

### 0.0.8 — Repository/RPM publication corrective

- Hardens the RPM builder so an existing user-selected build directory is never recursively deleted.
- Retains support for source paths containing spaces; a supplied `RPM_BUILD_ROOT` is now a **parent directory** for a unique temporary work tree.
- Updates repository documentation and provides a portable release ZIP packaging workflow.
- No privileged-helper runtime, discovery, validation or installation changes.


### 0.0.7

- Corrects the in-tree RPM builder so modules can be built from source paths containing spaces.
- RPM's internal `_topdir` now uses a safe temporary `/var/tmp` work tree and generated `%{buildroot}` shell paths are quoted.
- Privileged-helper discovery, stale/orphan detection, installation/removal and runtime behavior are unchanged.

### 0.0.6

- Adds an in-tree, version-agnostic Fedora RPM builder under `packaging/rpm/`.
- Helper discovery, stale/orphan detection, installation/removal safety boundaries and Hub integration are unchanged from 0.0.5.

### 0.0.5

- Adds filesystem scanning for direct `/usr/libexec/linspectacles-*` helper files.
- Declared installed helpers whose SHA-256 no longer matches the currently packaged applet payload are labelled **Stale version**.
- Undeclared direct helper files are listed as **Orphaned helper** and can be inspected or explicitly removed; they are never removed automatically.
- Hub State now reports stale and orphaned counts when present.
- Removes the module's `Tools → Privileged Helpers...` menu contribution; helper management remains in **Configuration → Helpers**.
- Updates documentation to reflect the current LinSpectacles helper namespace and current helper-contract applets.

### 0.0.4

- First RPM-ready Privileged Helpers Hub Module release.
- Packaging/distribution release only; helper-management behaviour is unchanged from 0.0.3-r2.
- System RPM installs the module beneath `/usr/libexec/linspectacles/modules/privileged_helpers/`.
- Current helper-contract applets use the `/usr/libexec/linspectacles-*` helper namespace managed by this module.

### 0.0.3-r2

- LinSpectacles/Hub identity and GPL metadata compliance update.
- Helper install namespace is now `/usr/libexec/linspectacles-*`.
- Functional helper-management model is otherwise unchanged from 0.0.3-r1.

### 0.0.3-r1

- Accepts both established Privileged Helper Contract v1 session models: `window_ephemeral` and `in_place_ephemeral`.
- Resource Monitor helpers using `in_place_ephemeral` are now fully validated and inspected instead of being rejected as a package/contract problem.
- Makes Configuration and Details wording presentation-neutral: the central manager does not require a dedicated Privileged Inspection window.
- Helper Details now reports the applet-declared session model alongside publisher, install path, ownership/mode and SHA-256 facts.
- Helper installation/removal, fixed-path safety restrictions, read-only requirement, SHA-256 verification, Hub State and Inspection Coverage behavior are otherwise unchanged.

### 0.0.3

- Uses Module API v4 to contribute a dedicated **Helper** column to Dashboard → Inspection Coverage.
- Each Helper cell uses the exact same state label as Configuration → Helpers → State (for example **Installed and verified**, **Not installed**, or **Update/repair required**).
- Removes the previous generic Summary annotation.
