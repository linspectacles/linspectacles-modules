Name:           linspectacles-modules
Version:        0.0.3
Release:        1%{?dist}
Summary:        Official LinSpectacles Hub Modules metapackage
License:        GPL-3.0-or-later
URL:            https://github.com/linspectacles/linspectacles-modules
Vendor:         LinSpectacles
Packager:       brunonlinespace
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

Recommends:      linspectacles-module-applet-organizer
Recommends:      linspectacles-module-boot-environment
Recommends:      linspectacles-module-encyclopedia
Recommends:      linspectacles-module-privileged-helpers
Recommends:      linspectacles-module-system-identity
Recommends:      linspectacles-module-system-pulse

%description
linspectacles-modules is the convenience metapackage for installing all
official LinSpectacles Hub Modules. The Modules remain separate RPM packages
so each can be installed, upgraded and removed independently. The modules
are recommended by default, not mandatory dependencies of this metapackage.

This package contains no Hub Module implementation source or runtime payload.
It provides only dependency composition plus its own documentation and license.

%prep
%autosetup

%build
# Dependency-only metapackage; no build step is required.

%install
# No module payload is installed by this metapackage.

%files
%license LICENSE
%doc README.md

%changelog
* Mon Nov 16 2026 brunonlinespace - 0.0.3-1
- Recommend all six official Hub Modules instead of requiring them.
- Allow removing an individual Module without requiring metapackage removal.
- No Hub Module payload or individual module version changes.
* Sun Nov 15 2026 brunonlinespace - 0.0.2-1
- Correct the authoritative source repository URL.
- Generate source archive from maintained documentation during RPM builds.
- Clarify required-dependency removal semantics; no runtime payload changes.
* Thu Sep 24 2026 brunonlinespace - 0.0.1-1
- Initial LinSpectacles Hub Modules metapackage.
- Require all six official individual linspectacles-module-* RPM packages.
- Include no Hub Module implementation source or runtime payload.
