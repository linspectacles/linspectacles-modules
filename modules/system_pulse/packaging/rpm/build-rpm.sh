#!/usr/bin/env bash
set -euo pipefail

# Version-agnostic RPM builder for a LinSpectacles Hub Module.
# Module identity and version are read from ../../module.json at build time.
# RPM's internal build tree is deliberately kept out of the source path because
# Fedora BRP helpers do not reliably handle an RPM_BUILD_ROOT containing spaces.

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
MODULE_ROOT="$(cd -- "$HERE/../.." && pwd)"
MANIFEST="$MODULE_ROOT/module.json"
PYTHON="${PYTHON:-python3}"
RPM_RELEASE="${RPM_RELEASE:-1}"
OUT_DIR="${RPM_OUTPUT_DIR:-$MODULE_ROOT/dist/rpm}"
MODE="${1:---all}"
KEEP_BUILD="${KEEP_BUILD:-0}"

usage() {
    cat <<'USAGE'
Usage: build-rpm.sh [--all|--srpm-only|--binary-only|--prepare-only]

The builder reads module identity/version from module.json. No module version is
hard-coded in this script.

Modes:
  --all           Build binary RPM and source RPM (default).
  --srpm-only     Build source RPM only (useful for COPR submission).
  --binary-only   Build binary RPM only.
  --prepare-only  Generate the source tarball and spec without invoking rpmbuild.

Environment overrides:
  PYTHON=/usr/bin/python3
  RPM_RELEASE=1
  RPM_BUILD_ROOT=/space-free/parent/for/work
  RPM_OUTPUT_DIR=/path/to/output
  KEEP_BUILD=1

By default the RPM work tree is created under /var/tmp so source directories
containing spaces are safe. If RPM_BUILD_ROOT is supplied explicitly, it must
not contain whitespace because Fedora RPM post-processing tools do not support
such buildroot paths reliably.
USAGE
}

case "$MODE" in
  --all|--srpm-only|--binary-only|--prepare-only) ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

[[ -f "$MANIFEST" ]] || { echo "ERROR: missing $MANIFEST" >&2; exit 2; }
command -v "$PYTHON" >/dev/null 2>&1 || { echo "ERROR: Python 3 is required." >&2; exit 2; }
if [[ "$MODE" != "--prepare-only" ]]; then
  command -v rpmbuild >/dev/null 2>&1 || {
    echo "ERROR: rpmbuild is required. On Fedora: sudo dnf install rpm-build" >&2
    exit 2
  }
fi

# A caller-supplied RPM_BUILD_ROOT is a PARENT, never a directory to delete.
# The actual working directory is always created uniquely by this invocation.
BUILD_PARENT="${RPM_BUILD_ROOT:-/var/tmp}"
if [[ "$BUILD_PARENT" =~ [[:space:]] ]]; then
  echo "ERROR: RPM_BUILD_ROOT parent must not contain whitespace." >&2
  echo "Leave RPM_BUILD_ROOT unset to use /var/tmp." >&2
  exit 2
fi
if [[ ! -d "$BUILD_PARENT" ]]; then
  echo "ERROR: RPM_BUILD_ROOT parent does not exist: $BUILD_PARENT" >&2
  echo "Create the parent manually, or leave RPM_BUILD_ROOT unset." >&2
  exit 2
fi
BUILD_ROOT="$(mktemp -d -- "$BUILD_PARENT/linspectacles-module-rpm.XXXXXXXX")"

cleanup() {
  if [[ "$KEEP_BUILD" == "1" ]]; then
    echo "RPM work tree kept at: $BUILD_ROOT"
  else
    # Only the uniquely named work tree created above can ever be removed.
    rm -rf -- "$BUILD_ROOT"
  fi
}
trap cleanup EXIT

mkdir -p "$BUILD_ROOT"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS} "$OUT_DIR"

"$PYTHON" - "$MODULE_ROOT" "$BUILD_ROOT" "$OUT_DIR" "$RPM_RELEASE" <<'PYINNER'
from pathlib import Path
import json, re, shutil, sys, tarfile

root = Path(sys.argv[1]).resolve()
top = Path(sys.argv[2]).resolve()
out = Path(sys.argv[3]).resolve()
release = sys.argv[4]
manifest_path = root / "module.json"
data = json.loads(manifest_path.read_text(encoding="utf-8"))

required = ("id", "name", "version", "license", "repository", "description")
missing = [key for key in required if not str(data.get(key, "")).strip()]
if missing:
    raise SystemExit("ERROR: module.json is missing required packaging field(s): " + ", ".join(missing))

module_id = str(data["id"]).strip()
name = str(data["name"]).strip()
version = str(data["version"]).strip()
license_id = str(data["license"]).strip()
repository = str(data["repository"]).strip()
description = " ".join(str(data["description"]).split())
module_dir = root.name

if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", module_id):
    raise SystemExit(f"ERROR: unsupported RPM module id: {module_id!r}")
if not re.fullmatch(r"[A-Za-z0-9._+~]+", version):
    raise SystemExit(f"ERROR: unsupported RPM Version value: {version!r}")
if not re.fullmatch(r"[0-9][A-Za-z0-9._+~]*", release):
    raise SystemExit(f"ERROR: unsupported RPM_RELEASE value: {release!r}")
if not re.fullmatch(r"[A-Za-z0-9_]+", module_dir):
    raise SystemExit(f"ERROR: unsupported module directory name: {module_dir!r}")

pkg = f"linspectacles-module-{module_id}"
stem = f"{pkg}-{version}"
source = top / "SOURCES" / f"{stem}.tar.gz"
spec = top / "SPECS" / f"{pkg}.spec"

# Source0 contains only the runtime module payload. Build products and this
# packaging helper are excluded from the installed module.
excluded_roots = {".build", "dist", ".git", "__pycache__"}
with tarfile.open(source, "w:gz", format=tarfile.PAX_FORMAT) as tf:
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if not rel.parts:
            continue
        if rel.parts[0] in excluded_roots:
            continue
        if rel.parts[:2] == ("packaging", "rpm"):
            continue
        if "__pycache__" in rel.parts:
            continue
        arc = Path(stem) / module_dir / rel
        tf.add(path, arcname=str(arc), recursive=False)

summary = f"{name} Hub Module for LinSpectacles"
def rpm_escape(value: str) -> str:
    return value.replace("%", "%%")

spec_text = f'''Name:           {pkg}
Version:        {version}
Release:        {release}%{{?dist}}
Summary:        {rpm_escape(summary)}
License:        {rpm_escape(license_id)}
URL:            {rpm_escape(repository)}
Source0:        %{{name}}-%{{version}}.tar.gz
BuildArch:      noarch
Requires:       linspectacles-hub

%description
{rpm_escape(description)}

%prep
%autosetup -n %{{name}}-%{{version}}

%build
# Pure Python/data Hub Module; nothing to compile.

%install
rm -rf "%{{buildroot}}"
install -d "%{{buildroot}}%{{_libexecdir}}/linspectacles/modules"
cp -a "{module_dir}" "%{{buildroot}}%{{_libexecdir}}/linspectacles/modules/"

%files
%{{_libexecdir}}/linspectacles/modules/{module_dir}
'''
spec.write_text(spec_text, encoding="utf-8")

out.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, out / source.name)
shutil.copy2(spec, out / spec.name)

print(f"PACKAGE={pkg}")
print(f"VERSION={version}")
print(f"MODULE_DIR={module_dir}")
print(f"RPM_TOPDIR={top}")
print(f"SPEC={spec}")
print(f"SOURCE={source}")
PYINNER

SPEC_PATH="$(find "$BUILD_ROOT/SPECS" -maxdepth 1 -type f -name '*.spec' -print -quit)"
[[ -n "$SPEC_PATH" ]] || { echo "ERROR: spec generation failed" >&2; exit 2; }

if [[ "$MODE" == "--prepare-only" ]]; then
  echo "Prepared RPM inputs in: $OUT_DIR"
  exit 0
fi

case "$MODE" in
  --all)         RPMBUILD_MODE=-ba ;;
  --srpm-only)   RPMBUILD_MODE=-bs ;;
  --binary-only) RPMBUILD_MODE=-bb ;;
esac

rpmbuild "$RPMBUILD_MODE" --define "_topdir $BUILD_ROOT" "$SPEC_PATH"

find "$BUILD_ROOT/RPMS" "$BUILD_ROOT/SRPMS" -type f \( -name '*.rpm' -o -name '*.src.rpm' \) -exec cp -f {} "$OUT_DIR/" \; 2>/dev/null || true

echo "RPM output: $OUT_DIR"
