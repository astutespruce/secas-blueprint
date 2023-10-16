import math
from pathlib import Path

from affine import Affine
import geopandas as gp
import pandas as pd
from pyogrio.geopandas import read_dataframe, write_dataframe
import rasterio
from rasterio.features import rasterize, dataset_features
from rasterio import windows
import shapely

from analysis.constants import DATA_CRS, SECAS_STATES, MASK_RESOLUTION
from analysis.lib.geometry import make_valid, to_dict_all, to_dict
from analysis.lib.raster import write_raster, add_overviews, create_lowres_mask

NODATA = 255


src_dir = Path("source_data")
data_dir = Path("data")
json_dir = Path("constants")
bnd_dir = data_dir / "boundaries"  # used for processing but not as inputs
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps

bnd_dir.mkdir(exist_ok=True, parents=True)
out_dir.mkdir(exist_ok=True, parents=True)


### Extract subregions that define where to expect certain indicators
# sort by Hilbert distance so that they are geographically ordered
subregion_df = read_dataframe(
    src_dir / "blueprint/SoutheastBlueprint2023Subregions.shp", columns=["SubRgn"]
).rename(columns={"SubRgn": "subregion"})
subregion_df["marine"] = subregion_df.subregion.isin(
    ["Atlantic Marine", "Gulf of Mexico"]
)
subregion_df["hilbert"] = subregion_df.hilbert_distance()
subregion_df = (
    subregion_df.sort_values(by="hilbert")
    .drop(columns=["hilbert"])
    .reset_index(drop=True)
    .reset_index()
    .rename(columns={"index": "value"})
)

subregion_df["geometry"] = shapely.make_valid(subregion_df.geometry.values)

subregion_df.to_feather(bnd_dir / "subregions.feather")
write_dataframe(subregion_df, bnd_dir / "subregions.fgb")


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
    outfilename = out_dir / "blueprint_extent.tif"
    write_raster(
        outfilename,
        data,
        transform,
        crs=src.crs,
        nodata=nodata,
    )

    add_overviews(outfilename)

    create_lowres_mask(
        outfilename,
        str(outfilename).replace(".tif", "_mask.tif"),
        resolution=MASK_RESOLUTION,
    )

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

    ### Rasterize subregions to 480m resolution to check against indicators
    subregion_transform = Affine(
        a=MASK_RESOLUTION,
        b=0.0,
        c=transform.c,
        d=0.0,
        e=-MASK_RESOLUTION,
        f=transform.f,
    )
    subregion_data = rasterize(
        subregion_df.apply(lambda row: (to_dict(row.geometry), row.value), axis=1),
        out_shape=(math.ceil(window.height / 16), math.ceil(window.width / 16)),
        transform=subregion_transform,
        fill=NODATA,
        all_touched=True,
        dtype="uint8",
    )
    write_raster(
        bnd_dir / "subregion_mask.tif",
        subregion_data,
        transform=subregion_transform,
        crs=src.crs,
        nodata=NODATA,
    )

    ### Extract a non-marine mask aligned to the above
    # this mask is used for NLCD and urban, which are currently limited to
    # the contiguous Southeast (so it is also a smaller size but same origin)
    inland_subregions = subregion_df.loc[
        ~subregion_df.subregion.isin(["Atlantic Marine", "Gulf of Mexico", "Caribbean"])
    ].copy()
    shapes = to_dict_all(inland_subregions.geometry.values)
    bounds = inland_subregions.total_bounds
    rows = math.ceil((bounds[1] - transform.f) / transform.e)
    cols = math.ceil((bounds[2] - transform.c) / transform.a)

    nonmarine_mask = rasterize(
        shapes,
        (rows, cols),
        transform=transform,
        dtype="uint8",
        fill=0,
        default_value=1,
    )

    outfilename = out_dir / "contiguous_southeast_inland_mask.tif"
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
