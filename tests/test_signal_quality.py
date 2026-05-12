from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_oracle.signal_quality import (
    PROBABILITY_NAIVE_MIDPOINT,
    PROBABILITY_PHYSICAL,
    PROBABILITY_RISK_NEUTRAL,
    SignalQuality,
)


class TestSignalQualityFreshness(unittest.TestCase):
    def test_realtime_is_fresh_within_1_hour(self):
        sq = SignalQuality(
            liquidity_tier="high",
            staleness_hours=0.5,
            update_frequency="realtime",
        )
        self.assertTrue(sq.is_fresh)

    def test_realtime_is_stale_after_1_hour(self):
        sq = SignalQuality(
            liquidity_tier="high",
            staleness_hours=2.0,
            update_frequency="realtime",
        )
        self.assertFalse(sq.is_fresh)

    def test_weekly_is_fresh_within_8_days(self):
        sq = SignalQuality(
            liquidity_tier="high",
            staleness_hours=168.0,
            update_frequency="weekly",
        )
        self.assertTrue(sq.is_fresh)

    def test_weekly_is_stale_after_8_days(self):
        sq = SignalQuality(
            liquidity_tier="high",
            staleness_hours=200.0,
            update_frequency="weekly",
        )
        self.assertFalse(sq.is_fresh)

    def test_annual_is_fresh_within_a_year(self):
        sq = SignalQuality(
            liquidity_tier="medium",
            staleness_hours=8000.0,
            update_frequency="annual",
        )
        self.assertTrue(sq.is_fresh)


class TestSignalQualityReliability(unittest.TestCase):
    def test_high_liquidity_fresh_is_reliable(self):
        sq = SignalQuality(
            liquidity_tier="high",
            staleness_hours=0.5,
            update_frequency="realtime",
        )
        self.assertTrue(sq.is_reliable)

    def test_low_liquidity_is_not_reliable(self):
        sq = SignalQuality(
            liquidity_tier="low",
            staleness_hours=0.5,
            update_frequency="realtime",
        )
        self.assertFalse(sq.is_reliable)

    def test_stale_high_liquidity_is_not_reliable(self):
        sq = SignalQuality(
            liquidity_tier="high",
            staleness_hours=100.0,
            update_frequency="daily",
        )
        self.assertFalse(sq.is_reliable)

    def test_medium_liquidity_fresh_is_reliable(self):
        sq = SignalQuality(
            liquidity_tier="medium",
            staleness_hours=12.0,
            update_frequency="daily",
        )
        self.assertTrue(sq.is_reliable)


class TestProbabilityMeasureConstants(unittest.TestCase):
    def test_constants_are_strings(self):
        self.assertIsInstance(PROBABILITY_PHYSICAL, str)
        self.assertIsInstance(PROBABILITY_RISK_NEUTRAL, str)
        self.assertIsInstance(PROBABILITY_NAIVE_MIDPOINT, str)

    def test_probability_measure_optional(self):
        sq = SignalQuality(
            liquidity_tier="high",
            staleness_hours=0.0,
            update_frequency="realtime",
        )
        self.assertIsNone(sq.probability_measure)

    def test_probability_measure_set(self):
        sq = SignalQuality(
            liquidity_tier="high",
            staleness_hours=0.0,
            update_frequency="realtime",
            probability_measure=PROBABILITY_PHYSICAL,
        )
        self.assertEqual(sq.probability_measure, "physical")


class TestSignalQualityFrozen(unittest.TestCase):
    def test_frozen_dataclass(self):
        sq = SignalQuality(
            liquidity_tier="high",
            staleness_hours=0.0,
            update_frequency="realtime",
        )
        with self.assertRaises(AttributeError):
            sq.liquidity_tier = "low"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
