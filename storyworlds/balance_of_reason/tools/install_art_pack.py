#!/usr/bin/env python3
"""Safely install the seven generated WebP scenes into the static Storyworld player.

Examples:
    python storyworlds/balance_of_reason/tools/install_art_pack.py /path/to/balance-of-reason-production-art-pack.zip
    python storyworlds/balance_of_reason/tools/install_art_pack.py art.zip --target /tmp/pages-worktree/assets --check
    python storyworlds/balance_of_reason/tools/install_art_pack.py art.zip --target /tmp/pages-worktree/assets --replace

This changes image assets only. Commit/push actions stay with the repo owner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import tempfile
import zipfile
from pathlib import Path

IMAGES = (
    "hero.webp", "warroom.webp", "summit.webp", "world.webp",
    "dialogue.webp", "ceasefire.webp", "characters.webp",
)
MAX_BYTES_PER_IMAGE = 5 * 1024 * 1024
MAX_TOTAL_BYTES = 24 * 1024 * 1024
DEFAULT_TARGET = Path(__file__).resolve().parents[1] / "assets"


def check_webp(data: bytes, name: str) -> None:
    if not (16 <= len(data) <= MAX_BYTES_PER_IMAGE):
        raise ValueError(f"{name}: invalid image size {len(data)}")
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError(f"{name}: expected RIFF/WebP image data")
    if int.from_bytes(data[4:8], "little") + 8 != len(data):
        raise ValueError(f"{name}: WebP RIFF size does not match file size")
    if data[12:16] not in (b"VP8 ", b"VP8L", b"VP8X"):
        raise ValueError(f"{name}: unrecognized WebP image encoding")


def read_pack(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        allowed = {f"assets/{n}" for n in IMAGES} | {"INSTALL.txt"}
        present = {m.filename for m in members}
        expected = {f"assets/{n}" for n in IMAGES}
        if not expected.issubset(present):
            raise ValueError("Missing images: " + ", ".join(sorted(expected - present)))
        if present - allowed:
            raise ValueError("Unexpected archive paths: " + ", ".join(sorted(present - allowed)))
        if len(present) != len(members):
            raise ValueError("Archive has duplicate entries")
        if sum(m.file_size for m in members) > MAX_TOTAL_BYTES:
            raise ValueError("Archive exceeds decompressed size limit")
        for member in members:
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode) or stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                raise ValueError("Archive may only contain regular files")
            if member.file_size > MAX_BYTES_PER_IMAGE and member.filename != "INSTALL.txt":
                raise ValueError(f"{member.filename}: image exceeds size limit")
        contents = {name: archive.read(f"assets/{name}") for name in IMAGES}
    for name, data in contents.items():
        check_webp(data, name)
    return contents


def manifest_for(images: dict[str, bytes]) -> dict:
    return {
        "pack": "balance-of-reason-production-art",
        "format": "webp",
        "purpose": "fictional strategy-game concept art",
        "assets": {
            n: {"bytes": len(images[n]), "sha256": hashlib.sha256(images[n]).hexdigest()}
            for n in IMAGES
        },
    }


def install(path: Path, target: Path, *, dry_run=False, replace=False, check=False) -> dict:
    images = read_pack(path)
    summary = manifest_for(images)
    if check:
        for name, source in images.items():
            installed = target / name
            if not installed.is_file() or installed.read_bytes() != source:
                raise ValueError(f"Different or missing installed artwork: {installed}")
        return summary
    if dry_run:
        return summary
    target.mkdir(parents=True, exist_ok=True)
    for name, data in images.items():
        output = target / name
        if output.exists() and not replace:
            if output.read_bytes() == data:
                continue
            raise FileExistsError(f"{output} exists. Use --replace to replace it.")
        with tempfile.NamedTemporaryFile(dir=target, prefix=f".{name}.", delete=False) as f:
            temporary = Path(f.name)
            try:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            except BaseException:
                temporary.unlink(missing_ok=True)
                raise
        try:
            os.replace(temporary, output)
        finally:
            temporary.unlink(missing_ok=True)
    (target / "art_pack_manifest.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path, help="Downloaded production-art-pack.zip")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET, help="Destination assets/ directory")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing")
    parser.add_argument("--check", action="store_true", help="Verify installed artwork against the ZIP")
    parser.add_argument("--replace", action="store_true", help="Permit replacement of changed installed WebPs")
    args = parser.parse_args()
    if args.check and args.dry_run:
        parser.error("Use either --dry-run or --check")
    result = install(args.zip_path, args.target, dry_run=args.dry_run, check=args.check, replace=args.replace)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
