# linspectacles-modules RPM metapackage

This kit builds the dependency-only RPM package:

`linspectacles-modules`

It contains **no Hub Module implementation source**. Its purpose is to install all six official Hub Module RPMs together while retaining independent module RPM versions and upgrades. The six module RPMs are **Recommends** (weak dependencies): normally installed together by DNF, but no longer required to keep the metapackage installed. Systems configured to skip weak dependencies may not install them automatically.

## Recommended Module packages

- `linspectacles-module-applet-organizer`
- `linspectacles-module-boot-environment`
- `linspectacles-module-encyclopedia`
- `linspectacles-module-privileged-helpers`
- `linspectacles-module-system-identity`
- `linspectacles-module-system-pulse`

There are deliberately no exact version pins. Normal DNF upgrades of an individual Module do not require a new metapackage release unless the composition itself changes.

## What it does not contain

- no Hub application
- no Module Python implementation
- no applets
- no helper binaries
- no desktop entry
- no AppStream application entry

The individual Module RPMs own their payloads and each declares its own Hub compatibility dependency.

## Fedora build

Install the RPM build tool if necessary:

```bash
sudo dnf install rpm-build
```

From `metapackage/` in the [official source repository](https://github.com/linspectacles/linspectacles-modules), run:

```bash
./build-rpm-fedora.sh
```

The build script recreates its source tarball from `README.md` and `LICENSE` at build time. It uses a private temporary RPM work tree and never deletes an existing output directory.

The generated binary RPM and source RPM are written to:

`dist-rpm/`

Upload the generated `.src.rpm` to your chosen RPM build service when configured; this source repository does not itself configure COPR.

To prepare the spec and source tarball without `rpmbuild`:

```bash
./build-rpm-fedora.sh --prepare-only
```

If `RPM_TOPDIR` is set, it must name an existing, whitespace-free **parent** directory for a temporary work tree (not a path to delete). Set `KEEP_BUILD=1` to retain the build tree.

## Install test

After COPR publishes it:

```bash
sudo dnf install linspectacles-modules
```

With Fedora's normal weak-dependency installation setting, DNF should offer the six individual `linspectacles-module-*` RPMs. Existing installed modules are retained. To verify independent removal, inspect the transaction from `sudo dnf remove linspectacles-module-system-pulse` and confirm that the `linspectacles-modules` metapackage is not a dependent removal; cancel before applying if other unexpected packages are listed.
