from __future__ import annotations

from typing import TYPE_CHECKING, Any, BinaryIO

from polars.dependencies import _PYARROW_AVAILABLE
from polars.internals import DataFrame, LazyFrame
from polars.internals.io import _prepare_file_arg
from polars.utils import deprecate_nonkeyword_arguments

if TYPE_CHECKING:
    from io import BytesIO
    from pathlib import Path


@deprecate_nonkeyword_arguments()
def read_ipc(
    file: str | BinaryIO | BytesIO | Path | bytes,
    columns: list[int] | list[str] | None = None,
    n_rows: int | None = None,
    use_pyarrow: bool = False,
    memory_map: bool = True,
    storage_options: dict[str, Any] | None = None,
    row_count_name: str | None = None,
    row_count_offset: int = 0,
    rechunk: bool = True,
) -> DataFrame:
    """
    Read into a DataFrame from Arrow IPC (Feather v2) file.

    Parameters
    ----------
    file
        Path to a file or a file-like object.
        If ``fsspec`` is installed, it will be used to open remote files.
    columns
        Columns to select. Accepts a list of column indices (starting at zero) or a list
        of column names.
    n_rows
        Stop reading from IPC file after reading ``n_rows``.
        Only valid when `use_pyarrow=False`.
    use_pyarrow
        Use pyarrow or the native Rust reader.
    memory_map
        Try to memory map the file. This can greatly improve performance on repeated
        queries as the OS may cache pages.
        Only uncompressed IPC files can be memory mapped.
    storage_options
        Extra options that make sense for ``fsspec.open()`` or a particular storage
        connection, e.g. host, port, username, password, etc.
    row_count_name
        If not None, this will insert a row count column with give name into the
        DataFrame
    row_count_offset
        Offset to start the row_count column (only use if the name is set)
    rechunk
        Make sure that all data is contiguous.

    Returns
    -------
    DataFrame

    Warnings
    --------
    If ``memory_map`` is set, the bytes on disk are mapped 1:1 to memory.
    That means that you cannot write to the same filename.
    E.g. ``pl.read_ipc("my_file.arrow").write_ipc("my_file.arrow")`` will fail.

    """
    if use_pyarrow and n_rows and not memory_map:
        raise ValueError(
            "``n_rows`` cannot be used with ``use_pyarrow=True` "
            "and memory_map=False`."
        )

    storage_options = storage_options or {}
    with _prepare_file_arg(file, use_pyarrow=use_pyarrow, **storage_options) as data:
        if use_pyarrow:
            if not _PYARROW_AVAILABLE:
                raise ImportError(
                    "'pyarrow' is required when using"
                    " 'read_ipc(..., use_pyarrow=True)'."
                )

            import pyarrow as pa
            import pyarrow.feather

            tbl = pa.feather.read_table(data, memory_map=memory_map, columns=columns)
            df = DataFrame._from_arrow(tbl, rechunk=rechunk)
            if row_count_name is not None:
                df = df.with_row_count(row_count_name, row_count_offset)
            if n_rows is not None:
                df = df.slice(0, n_rows)
            return df

        return DataFrame._read_ipc(
            data,
            columns=columns,
            n_rows=n_rows,
            row_count_name=row_count_name,
            row_count_offset=row_count_offset,
            rechunk=rechunk,
            memory_map=memory_map,
        )


@deprecate_nonkeyword_arguments()
def scan_ipc(
    file: str | Path,
    n_rows: int | None = None,
    cache: bool = True,
    rechunk: bool = True,
    row_count_name: str | None = None,
    row_count_offset: int = 0,
    storage_options: dict[str, Any] | None = None,
    memory_map: bool = True,
) -> LazyFrame:
    """
    Lazily read from an Arrow IPC (Feather v2) file or multiple files via glob patterns.

    This allows the query optimizer to push down predicates and projections to the scan
    level, thereby potentially reducing memory overhead.

    Parameters
    ----------
    file
        Path to a IPC file.
    n_rows
        Stop reading from IPC file after reading ``n_rows``.
    cache
        Cache the result after reading.
    rechunk
        Reallocate to contiguous memory when all chunks/ files are parsed.
    row_count_name
        If not None, this will insert a row count column with give name into the
        DataFrame
    row_count_offset
        Offset to start the row_count column (only use if the name is set)
    storage_options
        Extra options that make sense for ``fsspec.open()`` or a
        particular storage connection.
        e.g. host, port, username, password, etc.
    memory_map
        Try to memory map the file. This can greatly improve performance on repeated
        queries as the OS may cache pages.
        Only uncompressed IPC files can be memory mapped.

    """
    return LazyFrame._scan_ipc(
        file=file,
        n_rows=n_rows,
        cache=cache,
        rechunk=rechunk,
        row_count_name=row_count_name,
        row_count_offset=row_count_offset,
        storage_options=storage_options,
        memory_map=memory_map,
    )