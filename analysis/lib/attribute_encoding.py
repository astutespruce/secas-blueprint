import pandas as pd


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
    total : number
        Must be greater than 0.

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
    total : number
        Must be greater than 0.

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
        # .str.replace(nochange, f"x{len(delta.columns)}")
    )


def encode_indicators(df, shape_mask, prefix, indicators):
    """Encode indicators into a dict-encoded structure with counts
    encoded according to encode_values above, and with additional columns for
    average values ('*_avg') for average values of continous indicators, if any
    are present.


    Parameters
    ----------
    df : DataFrame
    shape_mask : Series
        contains counts present in shape
    prefix : str
        prefix of input group, e.g., 'sa'.  Used as prefex for outputs: <prefix>_indicators
    indicators : dict
        data structure with indicator info, such as id

    Returns
    -------
    DataFrame
        will always include <prefix>_indicators, and may optionally include
        <prefix>_indicator_avg if any average values are present in df
    """

    indicator_cols = [c for c in df.columns if c.startswith(f"{prefix}:")]
    avg_cols = [c for c in indicator_cols if c.endswith("_avg")]
    ids = [f"{prefix}:{i['id']}" for i in indicators]

    counts = dict()
    # serialized id is based on position
    for i, id in enumerate(ids):
        value_cols = [
            c for c in indicator_cols if c.startswith(id) and not c.endswith("_avg")
        ]
        values = df[value_cols]

        # drop indicators that are not present in this area
        # if only 0 values are present, ignore this indicator
        ix = values[value_cols[1:]].sum(axis=1) > 0
        counts[i] = encode_values(values.loc[ix], shape_mask.loc[ix], 1000).rename(i)

    # encode to dict-encoded value <i>:<percents>,...
    # dropping any that are not present in a given record
    out = pd.DataFrame(
        pd.DataFrame(counts)
        .fillna("")
        .apply(lambda g: ",".join((f"{k}:{v}" for k, v in g.items() if v)), axis=1)
        .rename(f"{prefix}_indicators")
    )

    if len(avg_cols) > 0:
        means = dict()
        for col in avg_cols:
            i = ids.index(col.replace("_avg", ""))

            # all averages should be unsigned integer where present
            means[i] = df[col].apply(
                lambda v: str(round(v)) if not pd.isnull(v) else ""
            )

        means = (
            pd.DataFrame(means)
            .apply(lambda g: ",".join((f"{k}:{v}" for k, v in g.items() if v)), axis=1)
            .rename(f"{prefix}_indicator_avg")
        )

        out = out.join(means)

    return out
