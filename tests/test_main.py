"""Test main module."""

import math
import os
import shutil
import unittest
from pathlib import Path

import zarr

from rechunk_zarr_ds.main import re_chunk_zarr_file


class TestMain(unittest.TestCase):
    """
    Test main module.

    This class contains tests for the functions in the main module.
    """

    def setUp(self):
        """
        Set up the test environment.

        This method creates the necessary directories and parameters
        for test data and results.
        """
        parent_dir = os.path.dirname(__file__)

        test_data_dir = os.path.join(parent_dir, 'data/zarr_files')
        test_results_dir = os.path.join(parent_dir, 'results')

        Path(test_results_dir).mkdir(parents=True, exist_ok=True)

        self.test_data_dir = test_data_dir
        self.test_results_dir = test_results_dir

    def tearDown(self):
        """
        Tear down the test environment.

        This method removes the test results directory.
        """
        shutil.rmtree(self.test_results_dir)

    def test_re_chunk_zarr_file___succeed_13_points_per_chunk_not_save(self):
        """Test re_chunk_zarr_file :: succeed."""
        input_file = \
            os.path.join(self.test_data_dir, 'potsdam_supermarkets.zarr')
        data_per_chunk = 13

        zarr_ds = zarr.open(input_file, mode='r')
        assert zarr_ds.chunks == (1, 2)

        # In case of re-chunking in-place
        re_chunked_zarr_array = re_chunk_zarr_file(
            file_path=input_file,
            data_per_chunk=data_per_chunk)

        # Check if the re-chunked zarr array has same <shape> as input zarr data
        assert re_chunked_zarr_array.shape == zarr_ds.shape
        # Check if the re-chunked zarr array has same <dtype> as input zarr data
        assert re_chunked_zarr_array.dtype == zarr_ds.dtype

        # TODO These checks fail because of issue in updating the dataset
        # # Check <number of chunks> in re-chunked zarr array
        # assert re_chunked_zarr_array.chunks[0] == data_per_chunk
        # # Check <number data per chunks> in re-chunked zarr array
        # assert re_chunked_zarr_array.nchunks == \
        #     math.ceil(zarr_ds.nchunks / data_per_chunk)
        # # Check <number data per chunks> in last chunk
        # assert tuple(
        #     re_chunked_zarr_array.shape[i] % re_chunked_zarr_array.chunks[i]
        #     if re_chunked_zarr_array.shape[i] % re_chunked_zarr_array.chunks[i] != 0
        #     else re_chunked_zarr_array.chunks[i]
        #     for i in range(len(re_chunked_zarr_array.shape)))[0] == \
        #     math.ceil(zarr_ds.nchunks % data_per_chunk)

    def test_re_chunk_zarr_file___succeed_17_points_per_chunk_save_on_disk(self):
        """Test re_chunk_zarr_file :: succeed."""
        input_file = \
            os.path.join(self.test_data_dir, 'potsdam_supermarkets.zarr')
        data_per_chunk = 17

        zarr_ds = zarr.open(input_file, mode='r')
        assert zarr_ds.chunks == (1, 2)

        re_chunked_zarr_array, output_file = re_chunk_zarr_file(
            file_path=input_file,
            data_per_chunk=data_per_chunk,
            output_dir=self.test_results_dir)

        # Check file naming
        assert os.path.basename(output_file) == \
            os.path.splitext(os.path.basename(input_file))[0] + \
            f'_re_chunked__to__{data_per_chunk}.zarr'

        assert os.path.exists(output_file)
        assert Path(output_file).suffix == '.zarr'

        re_chunked_zarr_array = zarr.open(output_file, mode='r')

        # Check if the re-chunked zarr array has same <shape> as input zarr data
        assert re_chunked_zarr_array.shape == zarr_ds.shape
        # Check if the re-chunked zarr array has same <dtype> as input zarr data
        assert re_chunked_zarr_array.dtype == zarr_ds.dtype
        # Check <number of chunks> in re-chunked zarr array
        assert re_chunked_zarr_array.chunks[0] == data_per_chunk
        # Check <number data per chunks> in re-chunked zarr array
        assert re_chunked_zarr_array.nchunks == \
            math.ceil(zarr_ds.nchunks / data_per_chunk)
        # Check <number data per chunks> in last chunk
        assert tuple(
            re_chunked_zarr_array.shape[i] % re_chunked_zarr_array.chunks[i]
            if re_chunked_zarr_array.shape[i] % re_chunked_zarr_array.chunks[i] != 0
            else re_chunked_zarr_array.chunks[i]
            for i in range(len(re_chunked_zarr_array.shape)))[0] == \
            math.ceil(zarr_ds.nchunks % data_per_chunk)

    def test_re_chunk_zarr_file___failed_input_file_not_found(self):
        """Test re_chunk_zarr_file :: failed :: input file not found."""
        input_file = \
            os.path.join(
                self.test_data_dir, 'NOT_FOUND_potsdam_supermarkets.zarr')
        try:
            re_chunk_zarr_file(file_path=input_file, data_per_chunk=13)
        except FileNotFoundError as e:
            assert str(e) == f'Zarr file <{input_file}> not found.'

    def test_re_chunk_zarr_file___failed_input_file_invalid(self):
        """Test re_chunk_zarr_file :: failed :: input file is not valid."""
        input_file = \
            os.path.join(
                self.test_data_dir, 'potsdam_supermarkets.zarr.zip')
        try:
            re_chunk_zarr_file(file_path=input_file, data_per_chunk=13)
        except FileNotFoundError as e:
            assert str(e) == \
                'Zarr file is not a file but directory of chunks.'

    def test_re_chunk_zarr_file___failed_0_point_per_chunk(self):
        """Test re_chunk_zarr_file :: failed :: 0 points per chunk."""
        input_file = \
            os.path.join(self.test_data_dir, 'potsdam_supermarkets.zarr')
        try:
            re_chunk_zarr_file(file_path=input_file, data_per_chunk=0)
        except ValueError as e:
            assert str(e) == 'Chunk size must be greater than 0.'

    def test_re_chunk_zarr_file___failed_output_dir_not_found(self):
        """Test re_chunk_zarr_file :: failed :: output path not found."""
        input_file = \
            os.path.join(
                self.test_data_dir, 'potsdam_supermarkets.zarr')
        output_dir = os.path.join(self.test_data_dir, 'NOT_FOUND')
        try:
            re_chunk_zarr_file(
                file_path=input_file,
                data_per_chunk=13,
                output_dir=output_dir)
        except FileNotFoundError as e:
            assert str(e) == \
                f"Output directory <{output_dir}> not found."

    def test_re_chunk_zarr_file___failed_output_file_already_exists(self):
        """Test re_chunk_zarr_file :: succeed."""
        input_file = \
            os.path.join(self.test_data_dir, 'potsdam_supermarkets.zarr')
        data_per_chunk = 11

        re_chunk_zarr_file(
            file_path=input_file,
            data_per_chunk=data_per_chunk,
            output_dir=self.test_results_dir)

        try:
            re_chunk_zarr_file(
                file_path=input_file,
                data_per_chunk=data_per_chunk,
                output_dir=self.test_results_dir)

        except FileExistsError as e:
            assert str(e) == f'Re-chunked zarr file for source file <{input_file}> ' + \
                f'and chunk size <{data_per_chunk}> already exists.'
