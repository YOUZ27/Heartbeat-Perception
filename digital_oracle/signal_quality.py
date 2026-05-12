from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "ProbabilityMeasure",
    "SignalQuality",
]

ProbabilityMeasure = str
PROBABILITY_PHYSICAL = "physical"
PROBABILITY_RISK_NEUTRAL = "risk_neutral"
PROBABILITY_NAIVE_MIDPOINT = "naive_midpoint"


@dataclass(frozen=True)
class SignalQuality:
    liquidity_tier: str
    staleness_hours: float
    update_frequency: str
    probability_measure: ProbabilityMeasure | None = None

    @property
    def is_fresh(self) -> bool:
        thresholds = {
            "realtime": 1.0,
            "daily": 48.0,
            "weekly": 192.0,
            "monthly": 768.0,
            "quarterly": 2304.0,
            "annual": 9000.0,
        }
        limit = thresholds.get(self.update_frequency, 48.0)
        return self.staleness_hours <= limit

    @property
    def is_reliable(self) -> bool:
        return self.liquidity_tier in ("high", "medium") and self.is_fresh
