"""Main module."""

import logging
import os
import pathlib

import geopandas as gp
import numpy as np
import zarr


def create_zarr_file(
        source_path: str,
        output_dir: str = None) -> str:
    """
    Creates a zarr file from a source file.

    Parameters:
    -----------
    source_path: str
        The path to the source file.
    output_dir: Optional[str], None
        The directory to save the zarr file in.

    Returns:
    --------
    str
        The path to the created zarr file.

    Raises:
    -------
    FileNotFoundError
        If the source file is not found.
    ValueError
        If the source file format is not '.json' or if the output directory is not found.
    FileNotFoundError
        If the output file already exists.
    RuntimeError
        If there is no point geometry in the source file or if failed to read the source file.
    RuntimeError
        If failed to generate the zarr file.
    IOError
        If the source file is not a valid JSON file.
    """
    if not os.path.isfile(source_path):
        err_message = f'Source file <{source_path}> not found.'
        logging.error(err_message)
        raise FileNotFoundError(err_message)

    source_format = pathlib.Path(source_path).suffix

    if not source_format:
        err_message = 'Unable to specify the format of the source file. ' + \
            'Please use ".json" format.'
        logging.error(err_message)
        raise ValueError(err_message)

    if source_format != '.json':
        err_message = f'Format <{source_format}> is not supported. ' + \
            'Please use ".json" format.'
        logging.error(err_message)
        raise ValueError(err_message)

    if not output_dir:
        output_dir = os.path.dirname(source_path)

    elif not os.path.isdir(output_dir):
        err_message = f'Output directory <{output_dir}> not found.'
        logging.error(err_message)
        raise FileNotFoundError(err_message)

    output_path = os.path.join(
        output_dir,
        os.path.basename(source_path).replace('.json', '.zarr'))

    if os.path.exists(output_path):
        err_message = f'File <{output_path}> already exists.'
        logging.error(err_message)
        raise FileExistsError(err_message)

    try:
        gdf = gp.read_file(source_path)

    except Exception as e:
        err_message = f'Failed to read source file. {str(e)}'
        logging.error(err_message)
        raise IOError(err_message) from e

    geom_type = gdf.geom_type.unique()

    if len(geom_type) == 0:
        err_message = 'There is no point geometry in the source file.'
        logging.error(err_message)
        raise ValueError(err_message)

    if len(geom_type) > 1:
        err_message = "Multiple geometry types found in file. " + \
            "Pleas use <Point> geometry."
        logging.error(err_message)
        raise ValueError(err_message)

    geom_type = geom_type[0]
    if geom_type != 'Point':
        err_message = "Pleas use <Point> geometry. " + \
            f'Geometry of type <{geom_type}> is not supported.'
        logging.error(err_message)
        raise ValueError(err_message)

    points_np = \
        np.array(
            [[row.geometry.x, row.geometry.y] for id, row in gdf.iterrows()])

    z = zarr.create(
        shape=points_np.shape,
        dtype=points_np.dtype,
        chunks=(1,),
        store=output_path)

    z[:] = points_np

    # print("Zarr Array Info (Saved to File):")
    # print(type(z))
    # print(z.info)
    # print("\nData from Zarr array (Read from File):")
    # for i in range(gdf.geometry.size):
    #     print(f"Chunk {i+1}: {z[i]}")

    return output_path
