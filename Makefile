# Run test for code style.
lint:
	poetry run pylint rechunk_zarr_ds/ tests/

# Run test and and generate coverage report in xml format.
test:
	poetry run pytest --cov --cov-report=xml -v
# poetry run coverage run --source=rechunk_zarr_ds/ -m pytest -v
# poetry run coverage report --show-missing
# poetry run coverage html
# poetry run coverage json -o coverage.json

# Build docs.
docs:
	poetry run mkdocs build

# Build and run it locally over http://127.0.0.1:8000/.
docs-online:
	poetry run mkdocs serve