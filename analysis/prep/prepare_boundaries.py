from pathlib import Path
import warnings

import geopandas as gp
import pandas as pd
import pygeos as pg
from pyogrio.geopandas import read_dataframe, write_dataframe
import rasterio
from rasterio.features import rasterize
from rasterio import windows

from analysis.constants import DATA_CRS, SECAS_STATES, MASK_RESOLUTION, INPUTS
from analysis.lib.geometry import dissolve, make_valid, to_dict_all, to_dict
from analysis.lib.raster import write_raster, add_overviews, create_lowres_mask

# suppress warnings about writing to feather
warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

src_dir = Path("source_data")
data_dir = Path("data")
json_dir = Path("constants")
bnd_dir = data_dir / "boundaries"  # used for processing but not as inputs
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps

bnd_dir.mkdir(exist_ok=True, parents=True)
out_dir.mkdir(exist_ok=True, parents=True)


### Extract Blueprint boundary polygon
bnd_df = read_dataframe(src_dir / "blueprint/SE_Blueprint_Extent.shp")[["geometry"]]
# boundary has multiple geometries, union together and cleanup
bnd_df = gp.GeoDataFrame(
    geometry=[pg.union_all(pg.make_valid(bnd_df.geometry.values.data))],
    index=[0],
    crs=bnd_df.crs,
)
bnd_df.to_feather(out_dir / "se_boundary.feather")
write_dataframe(bnd_df, data_dir / "boundaries/se_boundary.fgb")


### Extract Blueprint extent
print("Extracting SE Blueprint extent")
with rasterio.open(src_dir / "blueprint/SE_Blueprint_2022.tif") as src:
    nodata = int(src.nodata)
    data = src.read(1)

    data[data != nodata] = 1

    # uncomment to recalculate
    # window = windows.get_data_window(data, nodata=nodata)
    # print(window)

    window = windows.Window(col_off=855, row_off=294, width=144065, height=71409)
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


### Extract input areas
df = read_dataframe(src_dir / "blueprint/InputAreas.shp", columns=["gridcode"]).rename(
    columns={"gridcode": "value"}
)

df["geometry"] = make_valid(df.geometry.values.data)
df = dissolve(df, by="value")

inputs = {e["value"]: e["id"] for e in INPUTS}
df["id"] = df["value"].map(inputs)

write_dataframe(df, bnd_dir / "input_areas.fgb")
df.to_feather(out_dir / "input_areas.feather")

# rasterize to match the blueprint
# convert to pairs of GeoJSON , value
df = pd.DataFrame(df[["geometry", "value"]].copy())
df.geometry = df.geometry.values.data
shapes = df.apply(lambda row: (to_dict(row.geometry), row.value), axis=1)

print("Rasterizing inputs...")
with rasterio.open(bnd_dir / "se_blueprint_extent.tif") as src:
    data = rasterize(
        shapes.values, src.shape, transform=src.transform, dtype="uint8", fill=255
    )

    outfilename = out_dir / "input_areas.tif"
    write_raster(
        outfilename,
        data,
        src.transform,
        crs=src.crs,
        nodata=255,
    )

    add_overviews(outfilename)

    create_lowres_mask(
        outfilename,
        str(outfilename).replace(".tif", "_mask.tif"),
        resolution=MASK_RESOLUTION,
        ignore_zero=True,
    )


### Extract the Base Blueprint data extent and write to a new raster
# NOTE: the data extent transform is exactly the same as the data extent transform
# for full SE Blueprint (above)
print("Extracting Base Blueprint extent")
with rasterio.open(src_dir / "blueprint/BaseBlueprintExtent2022.tif") as src:
    nodata = int(src.nodata)
    data = src.read(1)

    # uncomment to recalculate
    window = windows.get_data_window(data, nodata=nodata)
    print(window)

    # window = windows.Window(col_off=855, row_off=806, width=106719, height=60170)
    transform = windows.transform(window, src.transform)

    data = data[window.toslices()]
    outfilename = bnd_dir / "base_blueprint_extent.tif"
    write_raster(
        outfilename,
        data,
        transform,
        crs=src.crs,
        nodata=nodata,
    )

    add_overviews(outfilename)

    ### Extract a non-marine mask aligned to the above
    # Note: this is still within the total footprint of the above; it is not
    # a smaller shape
    df = read_dataframe(
        src_dir / "base_blueprint/BaseBlueprintSubRgn.shp", columns=["SubRgn"]
    )
    df = df.loc[~df.SubRgn.str.contains("Marine")]
    shapes = to_dict_all(df.geometry.values.data)
    nonmarine_mask = rasterize(
        shapes, data.shape, transform=transform, dtype="uint8", fill=0, default_value=1
    )

    outfilename = bnd_dir / "nonmarine_mask.tif"
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
        src_dir / "boundaries/tl_2021_us_state.shp",
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
        src_dir / "boundaries/tl_2021_us_county.shp",
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
