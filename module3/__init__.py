"""Fairness auditing utilities for ProductionEquityAI."""

from .fairness_metrics import demographic_parity_difference, equal_opportunity_difference

__all__ = [
    "demographic_parity_difference",
    "equal_opportunity_difference",
]
