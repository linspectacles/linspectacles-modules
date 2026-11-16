# LinSpectacles Hub Modules — RPM metapackage

`linspectacles-modules` is the optional RPM metapackage for installing all six official [LinSpectacles Hub](https://github.com/linspectacles/linspectacles-hub) Modules together.

The metapackage contains no module implementation or runtime executable. It depends on the following individually versioned packages:

- `linspectacles-module-applet-organizer`
- `linspectacles-module-boot-environment`
- `linspectacles-module-encyclopedia`
- `linspectacles-module-privileged-helpers`
- `linspectacles-module-system-identity`
- `linspectacles-module-system-pulse`

The individual packages can be installed and upgraded separately. **While the metapackage is installed, all six are required dependencies**; removing any one module may also remove the metapackage.

After enabling a package repository that supplies these RPMs, install the set with:

```bash
sudo dnf install linspectacles-modules
```

For the build process, see [README-RPM.md](README-RPM.md) in the source repository.

Repository: https://github.com/linspectacles/linspectacles-modules  
Licence: GPL-3.0-or-later. Copyright © 2026 brunonlinespace.
