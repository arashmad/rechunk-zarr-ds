# ReChunk-Zarr-DS

A small python module that provides functionalities to generate and re-chunk input zarr files.

## Resources

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![coverage](https://img.shields.io/badge/Coverage-unknown-red)]()

Poetry helps you declare, manage and install dependencies of Python projects,
ensuring you have the right stack everywhere.

## Installation

```bash
# Install Poetry
pipx install poetry
# Download the source code
git clone https://github.com/arashmad/rechunk-zarr-ds.git
# Install dependencies
cd rechunk-zarr-ds
poetry install
# Activate virtual environment
poetry shell
# Test the code and installation
make lint && make test
```

## Example

#### 1. Create zarr file

```python
import zarr
from rechunk_zarr_ds.utils.main import create_zarr_file

input_file = 'rechunk_zarr_ds/tests/data/json_files/potsdam_supermarkets.json'
output_dir = '/path/to/output/dir'

output = create_zarr_file(
    source_path=input_file,
    output_dir=output_dir)

print(output) # '/path/to/output/dir/potsdam_supermarkets.zarr'

zarr_ds = zarr.open(output, mode='r')
print(zarr_ds.shape) # (63, 2) for test data "potsdam_supermarkets.json"
print(zarr_ds.chunks) # (1, 2) for test data "potsdam_supermarkets.json"
print(zarr_ds.nchunks) # 63 for test data "potsdam_supermarkets.json"
```

#### 2. Re-chunk zarr file

```python
from rechunk_zarr_ds.main import re_chunk_zarr_file

input_file = '/path/to/output/dir/potsdam_supermarkets.zarr'

re_chunked_zarr_ds = re_chunk_zarr_file(
    file_path=input_file,
    data_per_chunk=13)

print(re_chunked_zarr_ds.shape) # (63, 2) for test data "potsdam_supermarkets.zarr"
print(re_chunked_zarr_ds.chunks) # (13, 2) for test data "potsdam_supermarkets.zarr"
print(re_chunked_zarr_ds.nchunks) # 5 for test data "potsdam_supermarkets.zarr"
```
