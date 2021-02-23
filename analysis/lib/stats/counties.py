import geopandas as gp


from analysis.lib.pygeos_util import sjoin

county_filename = "data/inputs/boundaries/counties.feather"
results_filename = "data/results/huc12/counties.feather"


def summarize_by_huc12(units_df):
    """Calculate spatial join with counties

    Parameters
    ----------
    df : GeoDataFrame
        summary units
    """

    print("Calculating spatial join with counties")
    counties = gp.read_feather(county_filename)
    df = (
        sjoin(units_df, counties, how="inner")[["FIPS", "state", "county"]]
        .reset_index()
        .round()
    )
    df.to_feather(results_filename)
