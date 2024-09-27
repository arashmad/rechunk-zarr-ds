"""The main module."""

import logging
import os
from typing import Optional

import zarr


def re_chunk_zarr_file(
        file_path: str,
        data_per_chunk: int,
        output_dir: Optional[str] = None) -> zarr.Array | tuple[zarr.Array, str]:
    """
    Re-chunks a zarr file for a given chunk size.

    Parameters
    ----------
    file_path: str
        The path to the zarr file.
    data_per_chunk: int
        The data points per chunk in new zarr data.
    output_dir: Optional[str], None
        The directory to save the re-chunked zarr file on disk. If specified,
        it returns the re-chunked `zarr.Array` and the path to the file generated
        for it.

    Returns
    -------
    Union[zarr.Array, tuple[zarr.Array, str]]
        The re-chunked zarr array or a tuple with the re-chunked zarr array
        and the path to the re-chunked zarr file.

    Raises
    ------
    FileNotFoundError
        If the zarr file does not exist.
    ValueError
        If the zarr file name or extension is incorrect or the chunk size is
        less than 1.
    RuntimeError
        If an error occurs during the re-chunking process.
    """
    if not os.path.exists(file_path):
        err_message = f'Zarr file <{file_path}> not found.'
        logging.error(err_message)
        raise FileNotFoundError(err_message)

    if os.path.isfile(file_path):
        err_message = 'Zarr file is not a file but directory of chunks.'
        logging.error(err_message)
        raise FileNotFoundError(err_message)

    # Check if the chunk size is valid
    if data_per_chunk < 1:
        err_message = 'Chunk size must be greater than 0.'
        logging.error(err_message)
        raise ValueError(err_message)

    # Check if the output directory exists
    if output_dir and not os.path.isdir(output_dir):
        err_message = f'Output directory <{output_dir}> not found.'
        logging.error(err_message)
        raise FileNotFoundError(err_message)

    # Open the zarr file
    read_mode = 'r+' if output_dir else 'r'
    zarr_ds = zarr.open_array(file_path, mode=read_mode)
    zarr_ds_array = zarr_ds[:]

    # If the output directory is specified, save the re-chunked zarr as a file on disk
    if output_dir:
        re_chunked_file_path = os.path.join(
            output_dir,
            os.path.splitext(os.path.basename(file_path))[0] +
            f'_re_chunked__to__{data_per_chunk}.zarr')

        if os.path.exists(re_chunked_file_path):
            err_message = f'Re-chunked zarr file for source file <{file_path}> ' + \
                f'and chunk size <{data_per_chunk}> already exists.'
            logging.error(err_message)
            raise FileExistsError(err_message)

        shape = zarr_ds_array.shape

        zarr_ds.resize(shape)  # Make sure that it hase the same shape.
        zarr_ds = zarr.create(
            shape=shape,
            dtype=zarr_ds_array.dtype,
            chunks=(data_per_chunk,),
            store=re_chunked_file_path)

        zarr_ds[:] = zarr_ds_array
        return zarr_ds, re_chunked_file_path

    zarr_re_chunked = zarr.array(zarr_ds_array, chunks=(data_per_chunk,))
    return zarr_re_chunked
