from pathlib import Path

import geopandas as gp
import pandas as pd
from pyogrio.geopandas import read_dataframe, write_dataframe
import rasterio
from rasterio.features import rasterize, dataset_features
from rasterio import windows
import shapely

from analysis.constants import DATA_CRS, SECAS_STATES
from analysis.lib.geometry import make_valid, to_dict_all
from analysis.lib.raster import write_raster, add_overviews


src_dir = Path("source_data")
data_dir = Path("data")
json_dir = Path("constants")
bnd_dir = data_dir / "boundaries"  # used for processing but not as inputs
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps

bnd_dir.mkdir(exist_ok=True, parents=True)
out_dir.mkdir(exist_ok=True, parents=True)


### Extract subregions that define where to expect certain indicators
subregion_df = read_dataframe(
    src_dir / "blueprint/SoutheastBlueprint2023Subregions.shp", columns=["SubRgn"]
).rename(columns={"SubRgn": "subregion"})

subregion_df["geometry"] = shapely.make_valid(subregion_df.geometry.values)

subregion_df.to_feather(bnd_dir / "base_subregions.feather")
write_dataframe(subregion_df, bnd_dir / "base_subregions.fgb")


### Extract Blueprint extent
print("Extracting SE Blueprint extent")
with rasterio.open(src_dir / "blueprint/SoutheastBlueprint2023Extent.tif") as src:
    nodata = int(src.nodata)
    data = src.read(1)

    # uncomment to recalculate
    # window = windows.get_data_window(data, nodata=nodata)
    # print(window)

    window = windows.Window(col_off=901, row_off=901, width=147307, height=71439)
    transform = windows.transform(window, src.transform)

    data = data[window.toslices()]
    outfilename = bnd_dir / "se_blueprint_extent.tif"
    write_raster(
        outfilename,
        data,
        transform,
        crs=src.crs,
        nodata=nodata,
    )

    add_overviews(outfilename)

    # extract boundary polygon
    bnd_geom = pd.Series(dataset_features(src, bidx=1, geographic=False))
    bnd_geom = bnd_geom.apply(lambda x: shapely.geometry.shape(x["geometry"]))
    bnd_geom = shapely.union_all(shapely.make_valid(bnd_geom))
    bnd_df = gp.GeoDataFrame(
        geometry=[bnd_geom],
        index=[0],
        crs=src.crs,
    )
    bnd_df.to_feather(out_dir / "se_boundary.feather")
    write_dataframe(bnd_df, data_dir / "boundaries/se_boundary.fgb")

    # Extract a non-marine mask aligned to the above
    # Note: this is still within the total footprint of the above; it is not
    # a smaller shape
    subregion_df = subregion_df.loc[
        ~subregion_df.subregion.str.contains("Marine")
    ].copy()
    subregion_df["geometry"] = shapely.make_valid(subregion_df.geometry.values)
    shapes = to_dict_all(subregion_df.geometry.values)
    nonmarine_mask = rasterize(
        shapes, data.shape, transform=transform, dtype="uint8", fill=0, default_value=1
    )

    outfilename = out_dir / "nonmarine_mask.tif"
    write_raster(
        outfilename,
        nonmarine_mask,
        transform=transform,
        crs=src.crs,
        nodata=0,
    )

    add_overviews(outfilename)


### Extract SECAS states and counties
# print("Extracting states and counties...")
state_list = ",".join(f"'{state}'" for state in SECAS_STATES)
states = (
    read_dataframe(
        src_dir / "boundaries/tl_2022_us_state.zip",
        columns=["STATEFP", "STUSPS", "NAME"],
        where=f""""STUSPS" in ({state_list})""",
    )
    .rename(columns={"NAME": "state", "STUSPS": "id"})
    .to_crs(DATA_CRS)
)
write_dataframe(states, bnd_dir / "states.fgb")
states.to_feather(out_dir / "states.feather")

fips_list = ",".join(f"'{fips}'" for fips in states.STATEFP.unique())
counties = (
    read_dataframe(
        src_dir / "boundaries/tl_2022_us_county.zip",
        columns=["STATEFP", "GEOID", "NAME", "geometry"],
        where=f""""STATEFP" in ({fips_list})""",
    )
    .rename(columns={"GEOID": "FIPS", "NAME": "county"})
    .to_crs(DATA_CRS)
    .join(states.set_index("STATEFP").drop(columns=["geometry"]), on="STATEFP")
    .drop(columns=["STATEFP"])
    .rename(columns={"id": "state_id"})
)
write_dataframe(counties, bnd_dir / "counties.fgb")
counties.to_feather(out_dir / "counties.feather")


### PARCAs (Amphibian & reptile aras)
# already in EPSG:5070
print("Processing PARCAs...")
df = (
    read_dataframe(
        src_dir / "boundaries/SouthAtlanticPARCAs.gdb",
        columns=["FID", "Name", "Description"],
        force_2d=True,
    )
    .to_crs(DATA_CRS)
    .rename(columns={"FID": "parca_id", "Name": "name", "Description": "description"})
    .explode(ignore_index=True)
)

df["geometry"] = make_valid(df.geometry.values)

write_dataframe(df, bnd_dir / "parca.fgb")
df.to_feather(out_dir / "parca.feather")
