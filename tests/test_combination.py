from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_oracle.combination import (
    CombinedProbability,
    linear_pool,
    logarithmic_pool,
)


class TestLinearPool(unittest.TestCase):
    def test_single_estimate_returns_same_value(self):
        result = linear_pool([(0.7, 1.0)])
        self.assertAlmostEqual(result.value, 0.7)
        self.assertAlmostEqual(result.confidence, 1.0)
        self.assertEqual(result.source_count, 1)
        self.assertEqual(result.method, "linear_pool")

    def test_equal_weights_averages(self):
        result = linear_pool([(0.6, 1.0), (0.8, 1.0)])
        self.assertAlmostEqual(result.value, 0.7)

    def test_unequal_weights(self):
        result = linear_pool([(0.4, 1.0), (0.8, 3.0)])
        expected = (0.4 * 1.0 + 0.8 * 3.0) / 4.0
        self.assertAlmostEqual(result.value, expected)

    def test_agreement_yields_high_confidence(self):
        result = linear_pool([(0.60, 1.0), (0.62, 1.0), (0.61, 1.0)])
        self.assertGreater(result.confidence, 0.9)

    def test_disagreement_yields_low_confidence(self):
        result = linear_pool([(0.1, 1.0), (0.9, 1.0)])
        self.assertLess(result.confidence, 0.5)

    def test_empty_returns_half(self):
        result = linear_pool([])
        self.assertAlmostEqual(result.value, 0.5)
        self.assertAlmostEqual(result.confidence, 0.0)
        self.assertEqual(result.source_count, 0)

    def test_zero_weights_returns_half(self):
        result = linear_pool([(0.8, 0.0), (0.2, 0.0)])
        self.assertAlmostEqual(result.value, 0.5)

    def test_value_clamped_to_unit_interval(self):
        result = linear_pool([(0.5, 1.0)])
        self.assertGreaterEqual(result.value, 0.0)
        self.assertLessEqual(result.value, 1.0)


class TestLogarithmicPool(unittest.TestCase):
    def test_single_estimate_returns_same_value(self):
        result = logarithmic_pool([(0.7, 1.0)])
        self.assertAlmostEqual(result.value, 0.7, places=5)
        self.assertEqual(result.source_count, 1)
        self.assertEqual(result.method, "logarithmic_pool")

    def test_equal_probabilities_amplified(self):
        result = logarithmic_pool([(0.6, 1.0), (0.6, 1.0)])
        self.assertGreater(result.value, 0.6)
        self.assertLess(result.value, 1.0)

    def test_divergent_signals_pull_toward_50(self):
        result = logarithmic_pool([(0.1, 1.0), (0.9, 1.0)])
        self.assertAlmostEqual(result.value, 0.5, places=2)

    def test_higher_weight_dominates(self):
        result = logarithmic_pool([(0.2, 1.0), (0.8, 5.0)])
        self.assertGreater(result.value, 0.5)

    def test_agreement_yields_high_confidence(self):
        result = logarithmic_pool([(0.60, 1.0), (0.62, 1.0), (0.61, 1.0)])
        self.assertGreater(result.confidence, 0.5)

    def test_disagreement_yields_low_confidence(self):
        result = logarithmic_pool([(0.1, 1.0), (0.9, 1.0)])
        self.assertLess(result.confidence, 0.5)

    def test_empty_returns_half(self):
        result = logarithmic_pool([])
        self.assertAlmostEqual(result.value, 0.5)
        self.assertAlmostEqual(result.confidence, 0.0)

    def test_extreme_values_clamped(self):
        result = logarithmic_pool([(0.0, 1.0), (1.0, 1.0)])
        self.assertGreater(result.value, 0.0)
        self.assertLess(result.value, 1.0)

    def test_externality_property(self):
        r1 = logarithmic_pool([(0.6, 1.0), (0.8, 2.0)])
        r2 = logarithmic_pool([(0.6, 1.0), (0.8, 2.0), (0.5, 0.0)])
        self.assertAlmostEqual(r1.value, r2.value, places=5)


class TestCombinedProbabilityFrozen(unittest.TestCase):
    def test_frozen_dataclass(self):
        cp = CombinedProbability(value=0.5, confidence=0.8, method="test", source_count=2)
        with self.assertRaises(AttributeError):
            cp.value = 0.6  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
