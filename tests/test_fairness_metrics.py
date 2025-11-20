import pytest

from module3.fairness_metrics import (
    demographic_parity_difference,
    equal_opportunity_difference,
)


def test_demographic_parity_balanced_rates():
    predictions = [1, 0, 1, 0]
    protected = [1, 1, 0, 0]

    assert demographic_parity_difference(predictions, protected) == pytest.approx(0)


def test_demographic_parity_detects_gap():
    predictions = [1, 1, 0, 0, 1, 0]
    protected = [1, 1, 1, 0, 0, 0]

    # Protected group has 2/3 positive vs 1/3 for unprotected.
    assert demographic_parity_difference(predictions, protected) == pytest.approx(1 / 3)


def test_demographic_parity_requires_groups():
    with pytest.raises(ValueError):
        demographic_parity_difference([1, 0, 1], [1, 1, 1])


def test_equal_opportunity_difference_balanced_tpr():
    labels = [1, 1, 0, 0]
    predictions = [1, 1, 0, 0]
    protected = [1, 0, 1, 0]

    assert equal_opportunity_difference(labels, predictions, protected) == pytest.approx(0)


def test_equal_opportunity_difference_detects_gap():
    labels = [1, 1, 1, 0, 0, 0]
    predictions = [1, 0, 1, 0, 0, 0]
    protected = [1, 1, 0, 0, 1, 0]

    # Protected group true positives: 1/2, unprotected true positives: 1/1
    assert equal_opportunity_difference(labels, predictions, protected) == pytest.approx(-0.5)


def test_equal_opportunity_difference_requires_positive_labels():
    labels = [0, 0, 0]
    predictions = [0, 0, 0]
    protected = [1, 0, 1]

    with pytest.raises(ValueError):
        equal_opportunity_difference(labels, predictions, protected)


def test_length_mismatch_raises():
    with pytest.raises(ValueError):
        equal_opportunity_difference([1, 0], [1], [1, 0])
