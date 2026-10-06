"""Installer regression checks; all writes stay inside temporary directories."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import install_release as installer


class ReleaseInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='esign-release-test-')
        self.addCleanup(self.temp.cleanup)
        self.pets = Path(self.temp.name) / 'pets'
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            pet = {'id': installer.PET_ID, 'displayName': 'eSign AI 小象',
                   'description': 'Test manifest', 'spriteVersionNumber': 2,
                   'spritesheetPath': 'spritesheet.webp'}
            archive.writestr(installer.PET_ID + '/pet.json', json.dumps(pet))
            archive.writestr(installer.PET_ID + '/spritesheet.webp', b'test-sprite')
        self.data = buffer.getvalue()
        self.addCleanup(patch.stopall)
        patch.object(installer, 'EXPECTED_SHA256', hashlib.sha256(self.data).hexdigest()).start()

    def test_install_and_repeat_without_rewriting(self):
        target, created = installer.install(self.data, self.pets)
        self.assertTrue(created)
        before = (target / 'pet.json').stat().st_mtime_ns
        self.assertEqual(installer.install(self.data, self.pets), (target, False))
        self.assertEqual((target / 'pet.json').stat().st_mtime_ns, before)

    def test_changed_existing_pet_is_preserved(self):
        target, _ = installer.install(self.data, self.pets)
        (target / 'spritesheet.webp').write_bytes(b'personal-pet')
        with self.assertRaises(ValueError):
            installer.install(self.data, self.pets)
        self.assertEqual((target / 'spritesheet.webp').read_bytes(), b'personal-pet')

    def test_tampered_archive_writes_nothing(self):
        with self.assertRaises(ValueError):
            installer.install(self.data + b'tampered', self.pets)
        self.assertFalse(self.pets.exists())

    def test_broken_symlink_is_preserved(self):
        self.pets.mkdir()
        target = self.pets / installer.PET_ID
        target.symlink_to(self.pets / 'missing')
        with self.assertRaises(ValueError):
            installer.install(self.data, self.pets)
        self.assertTrue(target.is_symlink())

    def test_unexpected_archive_paths_are_rejected(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('../outside', b'unexpected')
        data = buffer.getvalue()
        with patch.object(installer, 'EXPECTED_SHA256', hashlib.sha256(data).hexdigest()):
            with self.assertRaises(ValueError):
                installer.install(data, self.pets)
        self.assertFalse(self.pets.exists())


if __name__ == '__main__':
    unittest.main()
