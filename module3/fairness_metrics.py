"""Utility functions for auditing binary classification fairness metrics.

The functions in this module provide transparent calculations for
commonly referenced fairness gaps. They operate on plain Python
iterables so they can be used with data loaded from CSVs, SQL queries,
or in-memory lists without additional dependencies.
"""
from __future__ import annotations

from typing import Iterable, Sequence


def _validate_lengths(*sequences: Sequence[object]) -> int:
    """Validate that all sequences share the same length.

    Returns the common length when validation succeeds.
    Raises:
        ValueError: if the provided sequences do not all share the same length.
    """

    lengths = {len(seq) for seq in sequences}
    if len(lengths) != 1:
        raise ValueError("All inputs must be the same length")
    return lengths.pop()


def _positive_rate(values: Sequence[int], positive_label: int) -> float:
    """Calculate the share of positive labels in a sequence."""

    if not values:
        return 0.0
    positives = sum(1 for value in values if value == positive_label)
    return positives / len(values)


def demographic_parity_difference(
    predictions: Sequence[int],
    protected_attributes: Sequence[int],
    *,
    positive_label: int = 1,
    protected_value: int = 1,
) -> float:
    """Measure the demographic parity difference between groups.

    Args:
        predictions: Model predictions encoded as binary values.
        protected_attributes: Binary indicators denoting protected group membership
            for each prediction.
        positive_label: The label in ``predictions`` considered a positive outcome.
        protected_value: The value in ``protected_attributes`` that marks protected
            membership.

    Returns:
        The difference in positive prediction rates between the protected and
        unprotected groups. A positive value indicates the protected group
        receives positive outcomes more often.

    Raises:
        ValueError: if ``predictions`` and ``protected_attributes`` have different
            lengths or if either group is empty.
    """

    _validate_lengths(predictions, protected_attributes)

    protected_predictions = [
        pred for pred, group in zip(predictions, protected_attributes) if group == protected_value
    ]
    unprotected_predictions = [
        pred for pred, group in zip(predictions, protected_attributes) if group != protected_value
    ]

    if not protected_predictions or not unprotected_predictions:
        raise ValueError("Both protected and unprotected groups must contain observations")

    protected_rate = _positive_rate(protected_predictions, positive_label)
    unprotected_rate = _positive_rate(unprotected_predictions, positive_label)
    return protected_rate - unprotected_rate


def equal_opportunity_difference(
    labels: Sequence[int],
    predictions: Sequence[int],
    protected_attributes: Sequence[int],
    *,
    positive_label: int = 1,
    protected_value: int = 1,
) -> float:
    """Measure the equal opportunity difference between groups.

    Args:
        labels: Ground-truth labels encoded as binary values.
        predictions: Model predictions encoded as binary values.
        protected_attributes: Binary indicators denoting protected group membership
            for each observation.
        positive_label: The label considered a positive outcome in both ``labels``
            and ``predictions``.
        protected_value: The value in ``protected_attributes`` that marks protected
            membership.

    Returns:
        The difference in true positive rates between the protected and
        unprotected groups. A positive value indicates the protected group
        has a higher true positive rate.

    Raises:
        ValueError: if the provided sequences differ in length or if either group
            does not have any positive ground-truth labels.
    """

    _validate_lengths(labels, predictions, protected_attributes)

    protected_pairs = [
        (label, pred)
        for label, pred, group in zip(labels, predictions, protected_attributes)
        if group == protected_value
    ]
    unprotected_pairs = [
        (label, pred)
        for label, pred, group in zip(labels, predictions, protected_attributes)
        if group != protected_value
    ]

    def true_positive_rate(pairs: Iterable[tuple[int, int]]) -> float:
        positives = [(label, pred) for label, pred in pairs if label == positive_label]
        if not positives:
            raise ValueError(
                "Both protected and unprotected groups must contain positive ground-truth labels"
            )
        true_positives = sum(1 for label, pred in positives if pred == positive_label)
        return true_positives / len(positives)

    protected_tpr = true_positive_rate(protected_pairs)
    unprotected_tpr = true_positive_rate(unprotected_pairs)
    return protected_tpr - unprotected_tpr
