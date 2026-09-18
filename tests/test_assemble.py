"""Exercise publication isolation with real temporary site directories."""

import tempfile
import unittest
from pathlib import Path

from scripts.assemble import assemble


class AssemblyTests(unittest.TestCase):
    def test_branch_updates_and_deleted_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prod, stage, output = (root / name for name in ("prod", "stage", "output"))
            for source, text in ((prod, "production v1"), (stage, "staging v1")):
                source.mkdir()
                (source / "index.html").write_text(text)
            (stage / "old.html").write_text("removed next build")
            assemble(prod, stage, output)
            (stage / "old.html").unlink()
            (stage / "index.html").write_text("staging v2")
            assemble(prod, stage, output)
            self.assertEqual((output / "index.html").read_text(), "production v1")
            self.assertEqual((output / "staging/index.html").read_text(), "staging v2")
            self.assertFalse((output / "staging/old.html").exists())
            (prod / "index.html").write_text("production v2")
            assemble(prod, stage, output)
            self.assertEqual((output / "index.html").read_text(), "production v2")
            self.assertEqual((output / "staging/index.html").read_text(), "staging v2")

    def test_missing_branch_and_overlapping_output_preserve_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prod, stage, output = (root / name for name in ("prod", "stage", "output"))
            prod.mkdir()
            output.mkdir()
            (prod / "index.html").write_text("source")
            (output / "index.html").write_text("previous deployment")
            with self.assertRaises(ValueError):
                assemble(prod, stage, output)
            self.assertEqual((output / "index.html").read_text(), "previous deployment")
            with self.assertRaises(ValueError):
                assemble(prod, prod, prod)
            self.assertEqual((prod / "index.html").read_text(), "source")
