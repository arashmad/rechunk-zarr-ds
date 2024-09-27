# My Project

This is an example Python package using Poetry.

## Installation

You can install the package using Poetry:

```bash
poetry install
poetry shell
```


## Test

To run test, do

```bash
poetry run pytest
poetry run pytest -v -s
poetry run pytest --cov=market_share_score --cov-report=html
```

## Example

```python
from market_share_score.main import add_numbers
print(add_numbers(2, 3))

```