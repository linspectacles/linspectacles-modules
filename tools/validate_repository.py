#!/usr/bin/env python3
"""Small dependency-free publication checks for the LinSpectacles Modules repository."""

import ast
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "modules"
EXPECTED = {
    "applet_organizer": "applet-organizer",
    "boot_environment": "boot-environment",
    "encyclopedia": "encyclopedia",
    "privileged_helpers": "privileged-helpers",
    "system_identity": "system-identity",
    "system_pulse": "system-pulse",
}
REPO = "https://github.com/linspectacles/linspectacles-modules"
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def parse_python(path):
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeError) as exc:
        errors.append(f"Python syntax: {path.relative_to(ROOT)}: {exc}")
        return None


def validate():
    for required in ("README.md", "LICENSE", ".gitignore", "metapackage/linspectacles-modules.spec", "metapackage/README.md", ".github/workflows/validate.yml"):
        check((ROOT / required).is_file(), f"missing repository file: {required}")
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check(REPO in root_readme, "root README does not link to the canonical repository")
    check("https://github.com/linspectacles/linspectacles-hub" in root_readme, "root README must link to Hub")
    check(not (ROOT / "metapackage/linspectacles-modules-0.0.1.tar.gz").exists(), "stale generated tarball remains checked in")
    got = {d.name for d in MODULES.iterdir() if d.is_dir()}
    check(got == set(EXPECTED), f"module directory inventory mismatch: {sorted(got)}")
    scripts = []
    for folder, module_id in EXPECTED.items():
        p = MODULES / folder
        manifest = p / "module.json"
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            errors.append(f"manifest parse failed for {folder}: {exc}")
            continue
        for key in ("name", "version", "description", "license", "repository", "entrypoint", "factory", "module_api"):
            check(bool(data.get(key)), f"{folder}: missing manifest field {key}")
        check(data.get("id") == module_id, f"{folder}: wrong module ID")
        check(data.get("repository") == REPO, f"{folder}: incorrect repository URL")
        check(data.get("license") == "GPL-3.0-or-later", f"{folder}: incorrect licence")
        check(data.get("enabled_by_default") is False, f"{folder}: default activation was changed prematurely")
        readme_text = (p / "README.md").read_text(encoding="utf-8")
        check(str(data.get("version")) in " ".join(readme_text.splitlines()[:5]), f"{folder}: README version does not match manifest")
        for req in ("README.md", "LICENSE", "module.json", str(data.get("entrypoint")), "packaging/rpm/README-RPM.md"):
            check((p / req).is_file(), f"{folder}: missing {req}")
        entry = p / str(data.get("entrypoint"))
        tree = parse_python(entry) if entry.is_file() else None
        if tree is not None:
            functions = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            check(data.get("factory") in functions, f"{folder}: factory {data.get('factory')} not found")
        for py in p.rglob("*.py"):
            parse_python(py)
        s = p / "packaging/rpm/build-rpm.sh"
        scripts.append(s)
        check(s.is_file(), f"{folder}: missing RPM builder")
        check(s.stat().st_mode & 0o111 != 0, f"{folder}: RPM builder is not executable")
        check(REPO in readme_text, f"{folder}: README does not cite canonical repository")
    organizer_tree = parse_python(MODULES / "applet_organizer/module.py")
    if organizer_tree is not None:
        assignments = {
            node.targets[0].id: node.value
            for node in organizer_tree.body
            if isinstance(node, ast.Assign) and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        }
        try:
            catalog = ast.literal_eval(assignments["APPLET_CATALOG"])
            order = ast.literal_eval(assignments["DEFAULT_GROUP_ORDER"])
            favorites = ast.literal_eval(assignments["DEFAULT_FAVORITES"])
            check(catalog["problem-finder"][1] == "Multi-Layer", "Problem Finder is not in Multi-Layer")
            check(catalog["display-server"][0] == "Display Server", "Display Server display name mismatch")
            check(catalog["virtualisation-inspector"][0] == "Virtualisation Inspector", "Virtualisation Inspector display name mismatch")
            check(catalog["virtualisation-inspector"][1] == "Userland", "Virtualisation Inspector must default to Userland")
            check("libvirt" in catalog["virtualisation-inspector"][2] and "kvm" in catalog["virtualisation-inspector"][2], "Virtualisation Inspector search tags missing")
            check(order[-2:] == ["Multi-Layer", "Unsorted"], "Multi-Layer must be the last built-in layer")
            check("problem-finder" in favorites, "Problem Finder default Favourite was lost")
        except (KeyError, ValueError, TypeError, IndexError) as exc:
            errors.append(f"Organizer layer defaults could not be checked: {exc}")
    if scripts and all(p.exists() for p in scripts):
        baseline = scripts[0].read_bytes()
        for other in scripts[1:]:
            check(other.read_bytes() == baseline, f"RPM builders differ: {other.relative_to(ROOT)}")
    spec = (ROOT / "metapackage/linspectacles-modules.spec").read_text(encoding="utf-8")
    check(REPO in spec, "metapackage spec has wrong repository URL")
    for module_id in EXPECTED.values():
        check(f"Requires:       linspectacles-module-{module_id}" in spec, f"metapackage missing dependency: {module_id}")
    check(len(re.findall(r"^Requires:\s+linspectacles-module-", spec, flags=re.M)) == len(EXPECTED), "metapackage has unexpected module dependencies")
    for script in [*scripts, ROOT / "metapackage/build-rpm-fedora.sh"]:
        result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
        check(result.returncode == 0, f"Bash syntax: {script}: {result.stderr.strip()}")
    parse_python(ROOT / "tools/build_module_zips.py")
    with tempfile.TemporaryDirectory(prefix="linspectacles-repository-qa-") as tmp:
        tmp_path = Path(tmp)
        output = tmp_path / "portable"
        cmd = [sys.executable, str(ROOT / "tools/build_module_zips.py"), "--all", "--output", str(output)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        check(result.returncode == 0, f"portable ZIP generator failed: {result.stderr.strip()}")
        for folder, module_id in EXPECTED.items():
            data = json.loads((MODULES / folder / "module.json").read_text(encoding="utf-8"))
            release = output / f"linspectacles-module-{module_id}-{data['version']}.zip"
            check(release.is_file(), f"missing generated portable ZIP: {release.name}")
            if release.exists():
                with ZipFile(release) as z:
                    names = z.namelist()
                    check(z.testzip() is None, f"corrupt release ZIP: {release.name}")
                    check(f"{folder}/module.json" in names, f"release ZIP missing module manifest: {release.name}")
                    check(f"{folder}/module.py" in names, f"release ZIP missing implementation: {release.name}")
                    check(not any("packaging/" in n for n in names), f"release ZIP incorrectly embeds builder: {release.name}")

    if errors:
        for item in errors:
            print(f"FAIL: {item}", file=sys.stderr)
        return 1
    print(f"PASS: {len(EXPECTED)} manifests, Python AST, shell syntax, RPM builder parity, metapackage dependencies, portable ZIPs")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
