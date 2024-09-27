# Run test for code style.
lint:
	poetry run pylint rechunk_zarr_ds/ tests/

# Run test and display/create coverage report.
test:
	poetry run coverage run --source=rechunk_zarr_ds/ -m pytest -v
	poetry run coverage report --show-missing
	poetry run coverage html

# Build docs.
docs:
	poetry run mkdocs build

# Build and run it locally over http://127.0.0.1:8000/.
docs-online:
	poetry run mkdocs serve