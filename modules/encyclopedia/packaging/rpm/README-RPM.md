# RPM packaging

This module carries its own **version-agnostic Fedora RPM builder**.

The builder reads the package identity, module version, description, license and repository directly from `../../module.json`. No module version is hard-coded in the script or maintained in a static spec file.

## Build

From the module directory:

```bash
./packaging/rpm/build-rpm.sh
```

The default build creates both the binary RPM and SRPM. For COPR, the source package alone can be produced with:

```bash
./packaging/rpm/build-rpm.sh --srpm-only
```

To inspect the generated spec/source archive without invoking `rpmbuild`:

```bash
./packaging/rpm/build-rpm.sh --prepare-only
```

Outputs are written to `dist/rpm/` by default.

The installed package name is derived as `linspectacles-module-<module-id>`, and the payload is installed beneath `/usr/libexec/linspectacles/modules/<module-directory>/`, which is the Hub's Package-managed module discovery root.

The RPM requires the `linspectacles-hub` package but does **not** pin an exact Hub release. Module/API compatibility remains declared by the module manifest and enforced by the Hub.

### Source paths containing spaces

RPM work files are created under a private `/var/tmp/linspectacles-module-rpm.*` directory by default. This is intentional: Fedora's RPM post-processing helpers do not reliably support an RPM buildroot path containing whitespace, even when the source tree itself is valid and correctly quoted.

Therefore a module may safely live in a path such as `Projects - Software/...`. The finished RPM/SRPM/spec/source files are still copied back to `dist/rpm/` under the module source tree.

If `RPM_BUILD_ROOT` is supplied manually, it names an **existing, whitespace-free parent directory**, not a build tree to be deleted. Each invocation creates a uniquely named subdirectory inside that parent; existing files and directories are never removed. `KEEP_BUILD=1` retains that private work tree for inspection. Without `KEEP_BUILD=1`, only the private directory created for that run is cleaned up.

`RPM_RELEASE` may be overridden when an RPM packaging revision is needed without changing the module source version.
