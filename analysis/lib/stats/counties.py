import geopandas as gp

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
    df = gp.sjoin(units_df, counties)[["FIPS", "state", "county"]].reset_index().round()
    df.to_feather(results_filename)
