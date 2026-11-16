Name:           linspectacles-modules
Version:        0.0.2
Release:        1%{?dist}
Summary:        Official LinSpectacles Hub Modules metapackage
License:        GPL-3.0-or-later
URL:            https://github.com/linspectacles/linspectacles-modules
Vendor:         LinSpectacles
Packager:       brunonlinespace
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       linspectacles-module-applet-organizer
Requires:       linspectacles-module-boot-environment
Requires:       linspectacles-module-encyclopedia
Requires:       linspectacles-module-privileged-helpers
Requires:       linspectacles-module-system-identity
Requires:       linspectacles-module-system-pulse

%description
linspectacles-modules is the convenience metapackage for installing all
official LinSpectacles Hub Modules. The Modules remain separate RPM packages
so each can be installed and upgraded independently. Removing one of the
required modules may also require removing this metapackage.

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
* Sun Nov 15 2026 brunonlinespace - 0.0.2-1
- Correct the authoritative source repository URL.
- Generate source archive from maintained documentation during RPM builds.
- Clarify required-dependency removal semantics; no runtime payload changes.
* Thu Sep 24 2026 brunonlinespace - 0.0.1-1
- Initial LinSpectacles Hub Modules metapackage.
- Require all six official individual linspectacles-module-* RPM packages.
- Include no Hub Module implementation source or runtime payload.
