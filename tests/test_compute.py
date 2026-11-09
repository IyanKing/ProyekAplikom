import unittest

from compute import compute_effective_asphalt, compute_marshall


class EffectiveAsphaltTests(unittest.TestCase):
    def test_effective_asphalt_matches_manual_calculation(self):
        result = compute_effective_asphalt(2.65, 2.70, 1.03, 5.5, 6)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["pba"], 0.7197763802)
        self.assertAlmostEqual(result["pbe"], 4.8198113208)
        self.assertAlmostEqual(result["db_ratio"], 6 / 4.8198113208)

    def test_effective_asphalt_without_p200_keeps_binder_values(self):
        result = compute_effective_asphalt(2.65, 2.70, 1.03, 5.5)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["pbe"], 4.8198113208)
        self.assertIsNone(result["db_ratio"])

    def test_invalid_specific_gravity_returns_no_effective_result(self):
        self.assertIsNone(compute_effective_asphalt(2.70, 2.65, 1.03, 5.5, 6))

    def test_marshall_adds_effective_metrics_without_changing_vma(self):
        state = {
            "mz": {
                "g": {"gsb": "2.65", "gse": "2.70", "gb": "1.03", "pg": "1"},
                "rows": [{
                    "ka": "5.5", "a": "1200", "b": "1210", "c": "700",
                    "st": "1000", "fl": "3",
                }],
            },
        }
        gradation = {"rows": [{"d": 0.075, "P": 6}]}

        result = compute_marshall(state, gradation)
        sample = result["samples"][0]

        self.assertAlmostEqual(sample["pba"], 0.7197763802)
        self.assertAlmostEqual(sample["pbe"], 4.8198113208)
        self.assertAlmostEqual(sample["db_ratio"], 6 / 4.8198113208)
        self.assertAlmostEqual(
            sample["vma"],
            100 - sample["gmb"] * (100 - sample["ka"]) / 2.65,
        )


if __name__ == "__main__":
    unittest.main()
