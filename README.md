# LinSpectacles Modules

**Linux Inspection Suite** — *Expose. Explore. Explain.*

**Official optional Hub Modules for [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub).** These modules extend the Hub's Dashboard, help, configuration and navigation. They are **not standalone inspector applets** and require LinSpectacles Hub.

## Included modules

| Module | What it adds | Where to find it |
| --- | --- | --- |
| [Applet Organizer](modules/applet_organizer/) | Favourites and Linux system-stack Layers for applet navigation | Configuration → Applets |
| [Boot Environment](modules/boot_environment/) | Current boot ID, kernel, command line, firmware and boot-loader context | Dashboard |
| [Encyclopedia & What's This?](modules/encyclopedia/) | 665 offline Linux definitions, 162 source records, contextual help | Dashboard / contextual action (`Shift+F1`) |
| [Privileged Helpers](modules/privileged_helpers/) | Management and provenance of optional applet-declared helpers | Configuration → Helpers; Inspection Coverage |
| [System Identity](modules/system_identity/) | Distribution, derived system age, kernel, hostname, desktop and session | Dashboard |
| [System Pulse](modules/system_pulse/) | Live uptime, memory, thermals, I/O pressure, network throughput and battery summary | Dashboard |

All six modules are versioned separately. See each module's `module.json` for the authoritative version, API requirements and description, and its README for features and release history.

## How modules work in the Hub

**Inspectors inspect Linux. Hub Modules enhance the workbench.** Modules add optional navigation, context, explanations and other Hub functionality; they are not required for applets to run standalone. Installing a module makes it available, but **all six currently ship disabled by default**. After installing a portable module ZIP or an RPM, open **Configuration → Modules** and enable the modules you want.

A module's **Enabled** state is separate from its **Dashboard** visibility. You can hide its Dashboard contribution without disabling its other capabilities. **Privileged Helpers** being enabled does not grant privileged access automatically; privileged inspection remains explicit and helper-scoped.

LinSpectacles Hub **0.2.2** implements **Module API 8** and remains compatible with earlier Module APIs. These modules declare API versions **1, 4 or 7** in their manifests; there is no reason to rewrite them to API 8 solely to use them with Hub 0.2.2. The Hub remains responsible for checking compatibility.

### Installation ownership

The Hub distinguishes **User** modules from **Package-managed** modules:

| Hub runtime | User module location |
| --- | --- |
| Source — Portable | `<Hub>/modules/` |
| Source — Integrated | `${XDG_DATA_HOME:-~/.local/share}/linspectacles/modules/` |
| Packaged | `${XDG_DATA_HOME:-~/.local/share}/linspectacles/modules/` |

Fedora RPMs install **Package-managed** modules under `/usr/libexec/linspectacles/modules/` (or the package's configured system root). The Hub can discover User and Package-managed copies separately; RPM-installed copies are updated or removed with **DNF/RPM**, not the Hub's User-module removal action. Configuration shows discovered copies and the Hub applies its component-source preference where applicable.

## Installation

### Portable module ZIPs

1. Get the **individual module release ZIP** (`linspectacles-module-<name>-<version>.zip`) from the [GitHub Releases](https://github.com/linspectacles/linspectacles-modules/releases) page.
2. In Hub, open **Configuration → Modules → Add Module...** and select the module ZIP.
3. In **Configuration → Modules**, enable the module (it is not enabled automatically).

Each portable ZIP contains a single module directory (for example, `applet_organizer/`), including `module.json`. **GitHub's generic “Download ZIP” for this repository is source code, not a portable module release ZIP.**

### Fedora RPMs

When a package repository containing the RPMs has been enabled, install one module:

```bash
sudo dnf install linspectacles-module-encyclopedia
```

Or install the complete six-module set through the optional metapackage:

```bash
sudo dnf install linspectacles-modules
```

See [metapackage/README-RPM.md](metapackage/README-RPM.md) for the package list. The metapackage **recommends all six packages** (weak RPM dependencies). DNF normally installs the complete set, but an individual module can be removed without forcing removal of the metapackage. Installations configured with `install_weak_deps=False` may omit the recommended modules. Each module RPM can also be installed independently.

These commands require an RPM repository already providing the named packages; this source tree does not itself configure a COPR repository. After RPM installation, enable the installed modules in **Configuration → Modules**.

## Source builds and packaging

The six module sources are in [`modules/`](modules/), with one version-agnostic Fedora RPM builder per module at `modules/<module>/packaging/rpm/build-rpm.sh`.

From the repository root:

```bash
# Build portable module release ZIPs in dist/portable/
python3 build_module_zips.py --all

# Prepare RPM inputs (source tarball + spec) without needing rpmbuild
bash modules/encyclopedia/packaging/rpm/build-rpm.sh --prepare-only

# On Fedora with rpm-build installed, build an individual module RPM + SRPM
bash modules/encyclopedia/packaging/rpm/build-rpm.sh --all

# Build the optional metapackage RPM + SRPM
bash metapackage/build-rpm-fedora.sh
```

See the individual packaging READMEs and [metapackage/README-RPM.md](metapackage/README-RPM.md).

## Project

Repository: https://github.com/linspectacles/linspectacles-modules  
Hub: https://github.com/linspectacles/linspectacles-hub

**License:** GPL-3.0-or-later. Copyright © 2026 brunonlinespace. See [`LICENSE`](LICENSE) and each module's own `LICENSE` file.
