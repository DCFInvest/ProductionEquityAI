# ProductionEquityAI

ProductionEquityAI is a lightweight toolkit for exploring model fairness
concepts. Each module focuses on a specific fairness audit technique or
metric so they can be combined into a classroom or workshop setting.

## Module 3: Fairness metrics

Module 3 introduces two common fairness measurements for binary
classification: demographic parity difference and equal opportunity
difference. The module relies solely on the Python standard library so
it can be run in constrained environments.

### Usage

```python
from module3 import demographic_parity_difference, equal_opportunity_difference

predictions = [1, 1, 0, 0, 1, 0]
protected_group = [1, 1, 1, 0, 0, 0]
labels = [1, 0, 1, 0, 1, 0]

parity_gap = demographic_parity_difference(predictions, protected_group)
equal_opp_gap = equal_opportunity_difference(labels, predictions, protected_group)
```

- **`parity_gap`** expresses the difference in positive prediction rates
  between protected and unprotected groups.
- **`equal_opp_gap`** compares true positive rates to highlight potential
  disparities in correct positive predictions across groups.

### Development

1. Install test dependencies: `python -m pip install -r requirements-dev.txt`
   (or `python -m pip install pytest` if you only need the test runner).
2. Run the test suite: `python -m pytest`.
