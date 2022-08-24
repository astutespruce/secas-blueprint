from pathlib import Path
import warnings

import geopandas as gp
import pygeos as pg
from pyogrio.geopandas import read_dataframe, write_dataframe
import rasterio
from rasterio.features import rasterize
from rasterio import windows

from analysis.constants import GEO_CRS, DATA_CRS, SECAS_STATES
from analysis.lib.io import write_raster
from analysis.lib.pygeos_util import to_dict_all

# suppress warnings about writing to feather
warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

src_dir = Path("source_data")
data_dir = Path("data")
bnd_dir = data_dir / "boundaries"  # used for processing but not as inputs
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps
tile_dir = data_dir / "for_tiles"

bnd_dir.mkdir(exist_ok=True, parents=True)
out_dir.mkdir(exist_ok=True, parents=True)
tile_dir.mkdir(exist_ok=True, parents=True)

### Extract the data extent and write to a new raster
print("Extracting Base Blueprint extent")
with rasterio.open(src_dir / "blueprint/BaseBlueprintExtent2022.tif") as src:
    nodata = int(src.nodata)
    data = src.read(1)

    # uncomment to recalculate
    # window = windows.get_data_window(data, nodata=nodata)

    window = windows.Window(col_off=855, row_off=806, width=106719, height=60170)
    transform = windows.transform(window, src.transform)

    data = data[window.toslices()]
    write_raster(
        bnd_dir / "base_blueprint_extent.tif",
        data,
        transform,
        crs=src.crs,
        nodata=nodata,
    )

    ### Extract a non-marine mask aligned to the above
    # Note: this is still within the total footprint of the above; it is not
    # a smaller shape
    df = read_dataframe(
        src_dir / "blueprint/BaseBlueprintSubRgn.shp", columns=["SubRgn"]
    )
    df = df.loc[~df.SubRgn.str.contains("Marine")]
    shapes = to_dict_all(df.geometry.values.data)
    nonmarine_mask = rasterize(
        shapes, data.shape, transform=transform, dtype="uint8", fill=0, default_value=1
    )
    write_raster(
        bnd_dir / "nonmarine_mask.tif",
        nonmarine_mask,
        transform=transform,
        crs=src.crs,
        nodata=0,
    )


# ### TODO: Extract the boundary
# bnd_df = read_dataframe(
#     src_dir / "blueprint/SE_Blueprint_2021_Vectors.gdb",
#     layer="SECAS_Boundary_2021_20211117",
# )[["geometry"]]
# # boundary has multiple geometries, union together and cleanup
# bnd_df = gp.GeoDataFrame(
#     geometry=[pg.union_all(pg.make_valid(bnd_df.geometry.values.data))],
#     index=[0],
#     crs=bnd_df.crs,
# )
# bnd_df.to_feather(out_dir / "se_boundary.feather")
# write_dataframe(bnd_df, data_dir / "boundaries/se_boundary.fgb")

# # create GeoJSON for tiling
# bnd_geo = bnd_df.to_crs(GEO_CRS)
# write_dataframe(bnd_geo, tile_dir / "se_boundary.geojson", driver="GeoJSONSeq")

# ### Create mask by cutting SA bounds out of world bounds
# print("Creating mask...")
# world = pg.box(-180, -85, 180, 85)
# mask = pg.normalize(pg.difference(world, bnd_geo.geometry.values.data))

# write_dataframe(
#     gp.GeoDataFrame({"geometry": mask}, index=[0], crs=GEO_CRS),
#     tile_dir / "se_mask.geojson",
#     driver="GeoJSONSeq",
# )


### Extract SECAS states and counties
print("Extracting states and counties...")
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
