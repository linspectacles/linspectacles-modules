#!/usr/bin/env python3
"""Create distributable single-module ZIPs from the authoritative module manifests."""

import argparse
import json
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent
MODULES = ROOT / "modules"
EXCLUDED_DIRS = {"packaging", "dist", ".git", ".build", "__pycache__"}


def module_dirs():
    return sorted(p for p in MODULES.iterdir() if p.is_dir() and (p / "module.json").exists())


def module_info(directory):
    data = json.loads((directory / "module.json").read_text(encoding="utf-8"))
    if not all(data.get(k) for k in ("id", "name", "version", "entrypoint")):
        raise ValueError(f"incomplete module.json in {directory}")
    return data


def release_archive(directory, output):
    data = module_info(directory)
    destination = output / f"linspectacles-module-{data['id']}-{data['version']}.zip"
    if not (directory / str(data['entrypoint'])).is_file():
        raise ValueError(f"missing entrypoint for {directory.name}")
    output.mkdir(parents=True, exist_ok=True)
    included = []
    with ZipFile(destination, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"symlinks are unsupported in portable module ZIPs: {path}")
            if not path.is_file():
                continue
            rel = path.relative_to(directory)
            if any(part in EXCLUDED_DIRS for part in rel.parts):
                continue
            if path.name in {".DS_Store"} or path.suffix in {".pyc", ".pyo"}:
                continue
            arcname = (Path(directory.name) / rel).as_posix()
            archive.write(path, arcname=arcname)
            included.append(arcname)
    if len(included) < 3:
        destination.unlink(missing_ok=True)
        raise ValueError(f"module archive unexpectedly small: {directory}")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--all", action="store_true", help="package all six modules")
    choice.add_argument("--module", help="module folder (e.g. encyclopedia) or ID (e.g. boot-environment)")
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "portable", help="ZIP output directory")
    args = parser.parse_args()
    available = module_dirs()
    selected = available if args.all else [d for d in available if args.module in (d.name, module_info(d)["id"])]
    if not selected:
        parser.error(f"unknown module: {args.module}")
    try:
        for directory in selected:
            print(release_archive(directory, args.output.resolve()))
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
