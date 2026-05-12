from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "CombinedProbability",
    "linear_pool",
    "logarithmic_pool",
]


@dataclass(frozen=True)
class CombinedProbability:
    value: float
    confidence: float
    method: str
    source_count: int


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def linear_pool(
    estimates: list[tuple[float, float]],
) -> CombinedProbability:
    """Linear opinion pool: weighted average of probabilities.

    Parameters
    ----------
    estimates:
        List of (probability, weight) pairs.  Probabilities must be in
        [0, 1]; weights must be non-negative.

    Returns
    -------
    CombinedProbability
        Combined value, confidence score, method name, and source count.
    """
    if not estimates:
        return CombinedProbability(
            value=0.5, confidence=0.0, method="linear_pool", source_count=0
        )

    total_weight = sum(w for _, w in estimates)
    if total_weight <= 0:
        return CombinedProbability(
            value=0.5, confidence=0.0, method="linear_pool", source_count=len(estimates)
        )

    combined = sum(p * w for p, w in estimates) / total_weight
    combined = _clamp(combined)

    probs = [p for p, _ in estimates]
    variance = sum((p - combined) ** 2 for p in probs) / len(probs)
    confidence = 1.0 / (1.0 + variance * 10.0)

    return CombinedProbability(
        value=combined,
        confidence=_clamp(confidence),
        method="linear_pool",
        source_count=len(estimates),
    )


def logarithmic_pool(
    estimates: list[tuple[float, float]],
) -> CombinedProbability:
    """Logarithmic opinion pool: geometric mean of odds ratios.

    Satisfies the externality property: adding a new source does not
    change the relative weights of existing sources.  Naturally
    down-weights divergent signals.

    Parameters
    ----------
    estimates:
        List of (probability, weight) pairs.  Probabilities must be in
        (0, 1) — extreme 0 or 1 values are clamped to [epsilon, 1-epsilon].
        Weights must be non-negative.

    Returns
    -------
    CombinedProbability
        Combined value, confidence score, method name, and source count.
    """
    if not estimates:
        return CombinedProbability(
            value=0.5, confidence=0.0, method="logarithmic_pool", source_count=0
        )

    eps = 1e-10
    clamped = [(_clamp(p, eps, 1.0 - eps), w) for p, w in estimates]

    log_yes = sum(w * math.log(p) for p, w in clamped)
    log_no = sum(w * math.log(1.0 - p) for p, w in clamped)

    log_odds = log_yes - log_no
    if log_odds > 500:
        combined = 1.0 - eps
    elif log_odds < -500:
        combined = eps
    else:
        combined = 1.0 / (1.0 + math.exp(-log_odds))

    combined = _clamp(combined)

    probs = [p for p, _ in clamped]
    variance = sum((p - combined) ** 2 for p in probs) / len(probs)
    confidence = 1.0 / (1.0 + variance * 10.0)

    return CombinedProbability(
        value=combined,
        confidence=_clamp(confidence),
        method="logarithmic_pool",
        source_count=len(estimates),
    )
