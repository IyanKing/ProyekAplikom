import json
import tempfile
import unittest
from pathlib import Path

from specs import load_specifications, specification_version_name


class SpecificationTests(unittest.TestCase):
    def test_default_presets_include_gradation_and_marshall_limits(self):
        data = load_specifications()
        version_id = data["default_version"]
        version = data["versions"][version_id]

        self.assertEqual(version_id, "bina-marga-2018")
        self.assertEqual(version["gradation"]["AC-WC"][0], [25, 100, 100])
        self.assertEqual(version["gradation"]["AC-WC"][-1], [0.075, 4, 9])
        self.assertEqual(version["marshall"]["AC-WC"]["vma"], 15)
        self.assertIsNone(version["marshall"]["AC-Base"]["mq"])

    def test_version_name_keeps_unavailable_historical_id(self):
        data = load_specifications()

        self.assertEqual(
            specification_version_name(data, data["default_version"]),
            "Bina Marga 2018",
        )
        self.assertEqual(
            specification_version_name(data, "future-version"),
            "future-version",
        )

    def test_supports_appending_another_version_entry(self):
        data = load_specifications()
        data["versions"]["bina-marga-test"] = data["versions"]["bina-marga-2018"]

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "specs.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            loaded = load_specifications(path)

        self.assertIn("bina-marga-test", loaded["versions"])

    def test_rejects_unsorted_or_invalid_gradation_rows(self):
        data = load_specifications()
        data["versions"][data["default_version"]]["gradation"]["AC-WC"][1][0] = 26
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "specs.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "urutan batas gradasi"):
                load_specifications(path)


if __name__ == "__main__":
    unittest.main()
