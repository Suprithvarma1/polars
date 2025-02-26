from __future__ import annotations

import contextlib
from datetime import time
from typing import TYPE_CHECKING, overload

from polars import functions as F
from polars.functions.range._utils import parse_interval_argument
from polars.utils._parse_expr_input import parse_as_expression
from polars.utils._wrap import wrap_expr
from polars.utils.deprecation import deprecate_saturating

with contextlib.suppress(ImportError):  # Module not available when building docs
    import polars.polars as plr

if TYPE_CHECKING:
    from datetime import timedelta
    from typing import Literal

    from polars import Expr, Series
    from polars.type_aliases import ClosedInterval, IntoExprColumn


@overload
def time_range(
    start: time | IntoExprColumn | None = ...,
    end: time | IntoExprColumn | None = ...,
    interval: str | timedelta = ...,
    *,
    closed: ClosedInterval = ...,
    eager: Literal[False] = ...,
) -> Expr:
    ...


@overload
def time_range(
    start: time | IntoExprColumn | None = ...,
    end: time | IntoExprColumn | None = ...,
    interval: str | timedelta = ...,
    *,
    closed: ClosedInterval = ...,
    eager: Literal[True],
) -> Series:
    ...


@overload
def time_range(
    start: time | IntoExprColumn | None = ...,
    end: time | IntoExprColumn | None = ...,
    interval: str | timedelta = ...,
    *,
    closed: ClosedInterval = ...,
    eager: bool,
) -> Series | Expr:
    ...


def time_range(
    start: time | IntoExprColumn | None = None,
    end: time | IntoExprColumn | None = None,
    interval: str | timedelta = "1h",
    *,
    closed: ClosedInterval = "both",
    eager: bool = False,
) -> Series | Expr:
    """
    Generate a time range.

    Parameters
    ----------
    start
        Lower bound of the time range.
        If omitted, defaults to `time(0,0,0,0)`.
    end
        Upper bound of the time range.
        If omitted, defaults to `time(23,59,59,999999)`.
    interval
        Interval of the range periods, specified as a Python `timedelta` object
        or using the Polars duration string language (see "Notes" section below).
    closed : {'both', 'left', 'right', 'none'}
        Define which sides of the range are closed (inclusive).
    eager
        Evaluate immediately and return a `Series`.
        If set to `False` (default), return an expression instead.

    Returns
    -------
    Expr or Series
        Column of data type `:class:Time`.

    Notes
    -----
    `interval` is created according to the following string language:

    - 1ns   (1 nanosecond)
    - 1us   (1 microsecond)
    - 1ms   (1 millisecond)
    - 1s    (1 second)
    - 1m    (1 minute)
    - 1h    (1 hour)
    - 1d    (1 calendar day)
    - 1w    (1 calendar week)
    - 1mo   (1 calendar month)
    - 1q    (1 calendar quarter)
    - 1y    (1 calendar year)

    Or combine them:
    "3d12h4m25s" # 3 days, 12 hours, 4 minutes, and 25 seconds

    By "calendar day", we mean the corresponding time on the next day (which may
    not be 24 hours, due to daylight savings). Similarly for "calendar week",
    "calendar month", "calendar quarter", and "calendar year".

    See Also
    --------
    time_ranges : Create a column of time ranges.

    Examples
    --------
    >>> from datetime import time, timedelta
    >>> pl.time_range(
    ...     start=time(14, 0),
    ...     interval=timedelta(hours=3, minutes=15),
    ...     eager=True,
    ... ).alias("time")
    shape: (4,)
    Series: 'time' [time]
    [
        14:00:00
        17:15:00
        20:30:00
        23:45:00
    ]
    """
    interval = deprecate_saturating(interval)

    interval = parse_interval_argument(interval)
    for unit in ("y", "mo", "w", "d"):
        if unit in interval:
            raise ValueError(f"invalid interval unit for time_range: found {unit!r}")

    if start is None:
        start = time(0, 0, 0)
    if end is None:
        end = time(23, 59, 59, 999999)

    start_pyexpr = parse_as_expression(start)
    end_pyexpr = parse_as_expression(end)

    result = wrap_expr(plr.time_range(start_pyexpr, end_pyexpr, interval, closed))

    if eager:
        return F.select(result).to_series()

    return result


@overload
def time_ranges(
    start: time | IntoExprColumn | None = ...,
    end: time | IntoExprColumn | None = ...,
    interval: str | timedelta = ...,
    *,
    closed: ClosedInterval = ...,
    eager: Literal[False] = ...,
) -> Expr:
    ...


@overload
def time_ranges(
    start: time | IntoExprColumn | None = ...,
    end: time | IntoExprColumn | None = ...,
    interval: str | timedelta = ...,
    *,
    closed: ClosedInterval = ...,
    eager: Literal[True],
) -> Series:
    ...


@overload
def time_ranges(
    start: time | IntoExprColumn | None = ...,
    end: time | IntoExprColumn | None = ...,
    interval: str | timedelta = ...,
    *,
    closed: ClosedInterval = ...,
    eager: bool,
) -> Series | Expr:
    ...


def time_ranges(
    start: time | IntoExprColumn | None = None,
    end: time | IntoExprColumn | None = None,
    interval: str | timedelta = "1h",
    *,
    closed: ClosedInterval = "both",
    eager: bool = False,
) -> Series | Expr:
    """
    Create a column of time ranges.

    Parameters
    ----------
    start
        Lower bound of the time range.
        If omitted, defaults to `time(0, 0, 0, 0)`.
    end
        Upper bound of the time range.
        If omitted, defaults to `time(23, 59, 59, 999999)`.
    interval
        Interval of the range periods, specified as a Python `timedelta` object
        or using the Polars duration string language (see "Notes" section below).
    closed : {'both', 'left', 'right', 'none'}
        Define which sides of the range are closed (inclusive).
    eager
        Evaluate immediately and return a `Series`.
        If set to `False` (default), return an expression instead.

    Returns
    -------
    Expr or Series
        Column of data type `List(Time)`.

    Notes
    -----
    `interval` is created according to the following string language:

    - 1ns   (1 nanosecond)
    - 1us   (1 microsecond)
    - 1ms   (1 millisecond)
    - 1s    (1 second)
    - 1m    (1 minute)
    - 1h    (1 hour)
    - 1d    (1 calendar day)
    - 1w    (1 calendar week)
    - 1mo   (1 calendar month)
    - 1q    (1 calendar quarter)
    - 1y    (1 calendar year)

    Or combine them:
    "3d12h4m25s" # 3 days, 12 hours, 4 minutes, and 25 seconds

    By "calendar day", we mean the corresponding time on the next day (which may
    not be 24 hours, due to daylight savings). Similarly for "calendar week",
    "calendar month", "calendar quarter", and "calendar year".

    See Also
    --------
    time_range : Generate a single time range.

    Examples
    --------
    >>> from datetime import time
    >>> df = pl.DataFrame(
    ...     {
    ...         "start": [time(9, 0), time(10, 0)],
    ...         "end": time(11, 0),
    ...     }
    ... )
    >>> df.with_columns(time_range=pl.time_ranges("start", "end"))
    shape: (2, 3)
    ┌──────────┬──────────┬────────────────────────────────┐
    │ start    ┆ end      ┆ time_range                     │
    │ ---      ┆ ---      ┆ ---                            │
    │ time     ┆ time     ┆ list[time]                     │
    ╞══════════╪══════════╪════════════════════════════════╡
    │ 09:00:00 ┆ 11:00:00 ┆ [09:00:00, 10:00:00, 11:00:00] │
    │ 10:00:00 ┆ 11:00:00 ┆ [10:00:00, 11:00:00]           │
    └──────────┴──────────┴────────────────────────────────┘
    """
    interval = deprecate_saturating(interval)
    interval = parse_interval_argument(interval)
    for unit in ("y", "mo", "w", "d"):
        if unit in interval:
            raise ValueError(f"invalid interval unit for time_range: found {unit!r}")

    if start is None:
        start = time(0, 0, 0)
    if end is None:
        end = time(23, 59, 59, 999999)

    start_pyexpr = parse_as_expression(start)
    end_pyexpr = parse_as_expression(end)

    result = wrap_expr(plr.time_ranges(start_pyexpr, end_pyexpr, interval, closed))

    if eager:
        return F.select(result).to_series()

    return result
