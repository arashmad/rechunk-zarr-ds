"""Test utils.main module."""

import os
import shutil
import unittest
from pathlib import Path

import zarr

from rechunk_zarr_ds.utils.main import create_zarr_file


class TestUtilsMain(unittest.TestCase):
    """
    Test utils.main module.

    This class contains tests for the functions in the utils.main module.
    """

    def setUp(self):
        """
        Set up the test environment.

        This method creates the necessary directories and parameters
        for test data and results.
        """
        parent_dir = os.path.dirname(__file__)

        test_data_dir = os.path.join(parent_dir, 'data/json_files')
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

    def test_generate_zarr_file___succeed(self):
        """Test generating zarr file :: succeed."""
        input_file = \
            os.path.join(self.test_data_dir, 'potsdam_supermarkets.json')

        output = create_zarr_file(
            source_path=input_file,
            output_dir=self.test_results_dir)

        assert os.path.exists(output)
        assert Path(output).suffix == '.zarr'

        zarr_ds = zarr.open(output, mode='r')
        assert zarr_ds.shape == (63, 2)
        assert zarr_ds.chunks == (1, 2)
        assert zarr_ds.dtype == 'float64'

        temp_dir = os.path.join(self.test_results_dir, 'temp')
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        shutil.copy(input_file, temp_dir)

        input_file = os.path.join(temp_dir, 'potsdam_supermarkets.json')

        output = create_zarr_file(source_path=input_file)

        assert os.path.exists(output)
        assert Path(output).suffix == '.zarr'

        zarr_ds = zarr.open(output, mode='r')
        assert zarr_ds.shape == (63, 2)
        assert zarr_ds.chunks == (1, 2)
        assert zarr_ds.dtype == 'float64'

    def test_generate_zarr_file___failed_input_file_not_found(self):
        """Test generating zarr file :: input file not found."""
        input_file = \
            os.path.join(
                self.test_data_dir, 'NOT_FOUND_potsdam_supermarkets.json')
        try:
            create_zarr_file(input_file, self.test_results_dir)
        except FileNotFoundError as e:
            assert str(e) == f'Source file <{input_file}> not found.'

    def test_generate_zarr_file___failed_input_file_without_format(self):
        """Test generating zarr file :: input file without format."""
        input_file = \
            os.path.join(self.test_data_dir, 'potsdam_supermarkets')
        try:
            create_zarr_file(input_file, self.test_results_dir)
        except ValueError as e:
            assert str(e) == \
                'Unable to specify the format of the source file. ' + \
                'Please use ".json" format.'

    def test_generate_zarr_file___failed_input_file_with_wrong_format(self):
        """Test generating zarr file :: input file with wrong format."""
        input_file = \
            os.path.join(self.test_data_dir, 'potsdam_supermarkets.txt')
        try:
            create_zarr_file(input_file, self.test_results_dir)
        except ValueError as e:
            assert str(e) == \
                'Format <.txt> is not supported. Please use ".json" format.'

    def test_generate_zarr_file___failed_output_dir_not_found(self):
        """Test generating zarr file :: output dir not found."""
        input_file = \
            os.path.join(self.test_data_dir, 'potsdam_supermarkets.json')
        try:
            ouput_dir_not_exists = \
                os.path.join(self.test_results_dir, 'NOT_FOUND')
            create_zarr_file(input_file, ouput_dir_not_exists)
        except FileNotFoundError as e:
            assert str(e) == \
                f"Output directory <{ouput_dir_not_exists}> not found."

    def test_generate_zarr_file___failed_output_file_already_generated(self):
        """Test generating zarr file :: output file already generated."""
        input_file = \
            os.path.join(self.test_data_dir, 'potsdam_supermarkets.json')
        output_path = \
            os.path.join(self.test_results_dir, 'potsdam_supermarkets.zarr')

        try:
            create_zarr_file(
                source_path=input_file,
                output_dir=self.test_results_dir)
            create_zarr_file(
                source_path=input_file,
                output_dir=self.test_results_dir)
        except FileExistsError as e:
            assert str(e) == \
                f'File <{output_path}> already exists.'

    def test_generate_zarr_file___failed_input_file_with_empty_geometry(self):
        """Test generating zarr file :: input file has no features."""
        input_file = os.path.join(self.test_data_dir,
                                  'potsdam_supermarkets_no_geom.json')
        try:
            create_zarr_file(
                source_path=input_file,
                output_dir=self.test_results_dir)
        except ValueError as e:
            assert str(e) == \
                'There is no point geometry in the source file.'

    def test_generate_zarr_file___failed_input_file_invalid_file(self):
        """Test generating zarr file :: input file is not valid."""

        input_file = os.path.join(self.test_data_dir,
                                  'potsdam_supermarkets_invalid.json')
        try:
            create_zarr_file(
                source_path=input_file,
                output_dir=self.test_results_dir)
        except IOError as e:
            assert 'Failed to read source file.' in str(e)

    def test_generate_zarr_file___failed_input_file_with_multiple_geometry_types(self):
        """Test generating zarr file :: input file has more than one geometry types."""

        input_file = os.path.join(self.test_data_dir,
                                  'potsdam_supermarkets_point_line.json')
        try:
            create_zarr_file(
                source_path=input_file,
                output_dir=self.test_results_dir)
        except ValueError as e:
            assert 'Multiple geometry types found in file.' in str(e)

    def test_generate_zarr_file___failed_input_file_with_polygon_geometry(self):
        """Test generating zarr file :: input file geometry is of type polygon."""

        input_file = os.path.join(self.test_data_dir,
                                  'potsdam_supermarkets_polygon.json')
        try:
            create_zarr_file(
                source_path=input_file,
                output_dir=self.test_results_dir)
        except ValueError as e:
            assert 'Geometry of type <Polygon> is not supported.' in str(e)
