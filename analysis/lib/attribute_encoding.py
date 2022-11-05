def encode_values(df, total, scale=100):
    """Convert a dataframe from acres to integer scalar values:
    scale * value / total

    This can be used to express percent where scale = 100

    Values are packed into a pipe-delimited string with 0 values omitted, e.g.,
    '10|20|70||'

    Parameters
    ----------
    df : DataFrame
        Note: only includes columns to be divided by total.
    total : ndarray
        Must be in same order as df and be greater than 0.

    Returns
    -------
    Series
        Contains string for each record with pipe-delimited values.  If
        max encoded value across all bins is 0, an empty string is returned instead.
    """
    return (
        (scale * df.divide(total, axis=0))
        .round()
        .astype("uint")
        .apply(lambda r: "|".join(str(v or "") for v in r) if r.max() else "", axis=1)
    )


def delta_encode_values(df, total, scale=100):
    """Convert a dataframe from acres to delta-encoded integer scalar values,
    where original values are first scaled.

    This can be used to express percent where scale = 100.

    Values are packed into a caret-delimited string with 0 values omitted, e.g.,
    '<baseline_value>^<delta_value1>^<delta_value2>...'

    If there is no change from the baseline value, that value plus an indication
    of number of values is returned instead:
    '<baseline_value>x<num_values>'


    Parameters
    ----------
    df : DataFrame
        Note: only includes columns to be divided by total.
    total : ndarray
        Representative acres of record in df; must be in same order as df and
        be greater than 0.

    Returns
    -------
    Series
        Contains string for each record with caret-delimited values.  If
        max encoded value across all bins is 0, an empty string is returned instead.
    """
    scaled = (scale * df.divide(total, axis=0)).round().astype("uint")

    # calculate delta values
    delta = scaled[scaled.columns[1:]].subtract(
        scaled[scaled.columns[:-1]].values, axis=0
    )

    # caret must be escaped
    # nochange = "\^" * len(delta.columns)

    return (
        scaled[[scaled.columns[0]]]
        .join(delta)
        .apply(lambda r: "^".join(str(v or "") for v in r) if r.max() else "", axis=1)
    )
