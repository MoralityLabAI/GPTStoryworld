"""Safe art pack installer tests. Run: python -m unittest discover -s tools -p 'test_*.py'"""
import importlib.util
import json
import stat
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("install_art_pack.py")
spec = importlib.util.spec_from_file_location("bor_art_installer", SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def webp(seed=0):
    payload = b"VP8 " + bytes([seed]) * 16
    return b"RIFF" + (len(payload) + 4).to_bytes(4, "little") + b"WEBP" + payload


def make_zip(path, *, omit=None, extra=None, bad=None, symlink=False, install_note=True):
    with zipfile.ZipFile(path, "w") as z:
        for name in installer.IMAGES:
            if name == omit:
                continue
            info = zipfile.ZipInfo("assets/" + name)
            info.external_attr = (0o100644 if not symlink or name != "hero.webp" else 0o120777) << 16
            z.writestr(info, b"NOT WEBP" if name == bad else webp(len(name)))
        if extra:
            z.writestr(extra, b"forbidden")
        if install_note:
            info = zipfile.ZipInfo("INSTALL.txt")
            info.external_attr = 0o600 << 16
            z.writestr(info, b"Documentation")


class ArtInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.pack = self.root / "pack.zip"
        self.target = self.root / "assets"

    def test_install_is_reproducible_and_checksum_verified(self):
        make_zip(self.pack)
        first = installer.install(self.pack, self.target)
        self.assertEqual(len(first["assets"]), 7)
        self.assertEqual(first, installer.install(self.pack, self.target, check=True))
        self.assertEqual(first, json.loads((self.target / "art_pack_manifest.json").read_text()))
        self.assertEqual(first, installer.install(self.pack, self.target))
        self.assertEqual(
            {p.name for p in self.target.iterdir()}, set(installer.IMAGES) | {"art_pack_manifest.json"}
        )

    def test_dry_run_does_not_write(self):
        make_zip(self.pack)
        self.assertEqual(len(installer.install(self.pack, self.target, dry_run=True)["assets"]), 7)
        self.assertFalse(self.target.exists())

    def test_changed_existing_file_requires_explicit_replace(self):
        make_zip(self.pack)
        installer.install(self.pack, self.target)
        (self.target / "hero.webp").write_bytes(webp(99))
        with self.assertRaises(FileExistsError):
            installer.install(self.pack, self.target)
        installer.install(self.pack, self.target, replace=True)
        installer.install(self.pack, self.target, check=True)

    def test_malicious_and_corrupt_archives_are_rejected(self):
        for options in (
            {"omit": "summit.webp"},
            {"extra": "../escape.txt"},
            {"bad": "hero.webp"},
            {"symlink": True},
        ):
            with self.subTest(options=options):
                make_zip(self.pack, **options)
                with self.assertRaises(ValueError):
                    installer.install(self.pack, self.target, dry_run=True)
                self.assertFalse(self.target.exists())

    def test_verify_detects_missing_art(self):
        make_zip(self.pack)
        installer.install(self.pack, self.target)
        (self.target / "world.webp").unlink()
        with self.assertRaisesRegex(ValueError, "Different or missing installed artwork"):
            installer.install(self.pack, self.target, check=True)


if __name__ == "__main__":
    unittest.main()
