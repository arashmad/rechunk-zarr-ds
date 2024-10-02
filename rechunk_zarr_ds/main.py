"""The main module."""

import logging
import os
from typing import Optional

import numpy as np
import zarr


def re_chunk_zarr_file(
    file_path: str,
    data_per_chunk: int,
    output_dir: Optional[str] = None) -> \
        zarr.Array | tuple[zarr.Array, str]:
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
    if output_dir:
        if not os.path.isdir(output_dir):
            err_message = f'Output directory <{output_dir}> not found.'
            logging.error(err_message)
            raise FileNotFoundError(err_message)

        re_chunked_file_path = os.path.join(
            output_dir,
            os.path.splitext(os.path.basename(file_path))[0] +
            f'_re_chunked__to__{data_per_chunk}.zarr')

        if os.path.exists(re_chunked_file_path):
            err_message = f'Re-chunked zarr file for source file <{file_path}> ' + \
                f'and chunk size <{data_per_chunk}> already exists.'
            logging.error(err_message)
            raise FileExistsError(err_message)

    zarr_ds = zarr.open_array(file_path, mode='r+')

    if output_dir:
        zarr_rechunked = zarr.create(
            shape=zarr_ds.shape,
            dtype=zarr_ds.dtype,
            chunks=(data_per_chunk,),
            store=re_chunked_file_path)

    total_size = zarr_ds.shape[0]  # Total number of elements
    current_chunk_size = zarr_ds.chunks[0]  # Get the current chunk size

    new_chunk_data = []  # Buffer to store the new chunks
    write_index = 0  # Track the correct write index

    for i in range(0, total_size, current_chunk_size):
        # Read the current chunk
        current_chunk = zarr_ds[i:i + current_chunk_size]
        new_chunk_data.extend(current_chunk)  # Append to the buffer

        # If the buffer size reaches or exceeds the new chunk size, write it back
        while len(new_chunk_data) >= data_per_chunk:
            # Extract the chunk to write
            chunk_to_write = np.array(new_chunk_data[:data_per_chunk])

            if output_dir:
                zarr_rechunked[write_index:write_index + data_per_chunk] = \
                    chunk_to_write
            else:
                zarr_ds[write_index:write_index + data_per_chunk] = \
                    chunk_to_write

            # Remove the written chunk from the buffer and update the write index
            new_chunk_data = new_chunk_data[data_per_chunk:]
            write_index += data_per_chunk

    # Managing last chunk for remaining data points
    if new_chunk_data:
        final_chunk_size = len(new_chunk_data)
        remained_chunk = np.array(new_chunk_data[:final_chunk_size])

        if output_dir:
            zarr_rechunked[-final_chunk_size:] = remained_chunk
            return zarr_rechunked, re_chunked_file_path

        zarr_ds[-final_chunk_size:] = remained_chunk
        return zarr_ds
