import math
from pathlib import Path
import warnings

from affine import Affine
import geopandas as gp
import numpy as np
import pandas as pd
from pyogrio.geopandas import read_dataframe, write_dataframe
import rasterio
from rasterio.features import rasterize, dataset_features
from rasterio import windows
import shapely

from analysis.constants import DATA_CRS, SECAS_STATES, MASK_RESOLUTION, PARCAS
from analysis.lib.colors import hex_to_uint8
from analysis.lib.geometry import make_valid, to_dict_all, to_dict, dissolve
from analysis.lib.raster import write_raster, add_overviews, create_lowres_mask

warnings.filterwarnings("ignore", message=".*Measured 3D MultiPolygon.*")
warnings.filterwarnings("ignore", message=".*polygon with more than 100 parts.*")

NODATA = 255


src_dir = Path("source_data")
data_dir = Path("data")
constants_dir = Path("constants")
bnd_dir = data_dir / "boundaries"  # used for processing but not as inputs
out_dir = data_dir / "inputs/boundaries"  # used as inputs for other steps

bnd_dir.mkdir(exist_ok=True, parents=True)
out_dir.mkdir(exist_ok=True, parents=True)

################################################################################
### Extract subregions that define where to expect certain indicators
################################################################################

subregion_df = (
    read_dataframe(
        src_dir / "blueprint/SEBlueprintSubregions2025.shp",
        columns=["SubRgn"],
        use_arrow=True,
    )
    .rename(columns={"SubRgn": "subregion"})
    .explode(ignore_index=True)
    # sort by Hilbert distance so that they are geographically ordered
    .sort_values(by="geometry")
)

subregion_df["geometry"] = shapely.make_valid(
    shapely.force_2d(subregion_df.geometry.values)
)

subregion_df = (
    dissolve(subregion_df, by="subregion")
    .reset_index()
    .rename(columns={"index": "value"})
)

subregion_df["region"] = subregion_df.subregion.map(
    {
        "Appalachians": "continental",
        "Atlantic": "marine",
        "Atlantic Coastal Plain": "continental",
        "Chihuahuan Deserts": "continental",
        "East Gulf Coastal Plain": "continental",
        "Edwards Plateau": "continental",
        "Florida Peninsula": "continental",
        "Gulf": "marine",
        "Gulf Coastal Prairies": "continental",
        "High Plains and Tablelands": "continental",
        "Interior Plateau": "continental",
        "Mississippi Alluvial Valley": "continental",
        "North Missouri": "continental",
        "Ouachita": "continental",
        "Ozarks and Plains": "continental",
        "Piedmont": "continental",
        "Plains and Timbers": "continental",
        "Puerto Rico": "caribbean",
        "South Florida Marine": "marine",
        "South Texas Plains": "continental",
        "Texas Blackland Prairies": "continental",
        "US Virgin Islands": "caribbean",
        "West Gulf Coastal Plain": "continental",
    }
).fillna("continental")


################################################################################
### Extract Blueprint extent
################################################################################
print("Extracting SE Blueprint extent")
with rasterio.open(src_dir / "blueprint/SEBlueprintExtent2025.tif") as src:
    nodata = int(src.nodata)
    data = src.read(1)

    # # uncomment to recalculate
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

    del data

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
    bnd_df = gp.GeoDataFrame(geometry=[bnd_geom], index=[0], crs=src.crs)
    bnd_df.to_feather(out_dir / "se_boundary.feather")
    write_dataframe(bnd_df, data_dir / "boundaries/se_boundary.fgb")

    ### Clip subregions to the boundary
    shapely.prepare(bnd_geom)
    contained = shapely.contains_properly(bnd_geom, subregion_df.geometry.values)
    subregion_df.loc[~contained, "geometry"] = shapely.intersection(
        bnd_geom, subregion_df.loc[~contained].geometry.values
    )

    subregion_df.to_feather(out_dir / "subregions.feather")
    write_dataframe(subregion_df, bnd_dir / "subregions.fgb")

    subregion_df[["value", "subregion", "region"]].to_json(
        constants_dir / "subregions.json", orient="records"
    )

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
    del subregion_data

    ### Extract a non-marine mask aligned to the above
    # this mask is used for NLCD and urban, which are currently limited to
    # the contiguous Southeast (so it is also a smaller size but same origin)
    inland_subregions = subregion_df.loc[subregion_df.region == "continental"].copy()
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

    del nonmarine_mask

    add_overviews(outfilename)


### Extract SECAS states and counties
# print("Extracting states and counties...")
state_list = ",".join(f"'{state}'" for state in SECAS_STATES)
states = (
    read_dataframe(
        src_dir / "boundaries/tl_2024_us_state.zip",
        columns=["STATEFP", "STUSPS", "NAME"],
        where=f""""STUSPS" in ({state_list})""",
        use_arrow=True,
    )
    .rename(columns={"NAME": "state", "STUSPS": "id"})
    .to_crs(DATA_CRS)
)
write_dataframe(states, bnd_dir / "states.fgb")
states.to_feather(out_dir / "states.feather")

fips_list = ",".join(f"'{fips}'" for fips in states.STATEFP.unique())
counties = (
    read_dataframe(
        src_dir / "boundaries/tl_2024_us_county.zip",
        columns=["STATEFP", "GEOID", "NAME", "geometry"],
        where=f""""STATEFP" in ({fips_list})""",
        use_arrow=True,
    )
    .rename(columns={"GEOID": "FIPS", "NAME": "county"})
    .to_crs(DATA_CRS)
    .join(states.set_index("STATEFP").drop(columns=["geometry"]), on="STATEFP")
    .drop(columns=["STATEFP"])
    .rename(columns={"id": "state_id"})
)
write_dataframe(counties, bnd_dir / "counties.fgb")
counties.to_feather(out_dir / "counties.feather")


################################################################################
### PARCAs (Amphibian & reptile aras)
################################################################################
# NOTE: already in EPSG:5070
print("Processing PARCAs...")

df = (
    read_dataframe(
        src_dir / "boundaries/PublicPARCAsOnly.gdb",
        columns=["PARCA", "Description"],
        use_arrow=True,
    )
    .to_crs(DATA_CRS)
    .rename(columns={"PARCA": "name", "Description": "description"})
)
df["parca_id"] = df.index.values
df["geometry"] = shapely.force_2d(df.geometry.values)


# Keep Neuse Tar River from previous, per direction from Hilary on 8/30/2024
prev = (
    read_dataframe(
        src_dir / "boundaries/SouthAtlanticPARCAs.gdb",
        columns=["FID", "Name", "Description"],
        where="""Name = 'Neuse Tar River'""",
        use_arrow=True,
    )
    .to_crs(DATA_CRS)
    .rename(columns={"FID": "parca_id", "Name": "name", "Description": "description"})
    .explode(ignore_index=True)
)
prev["parca_id"] += 200
prev["geometry"] = shapely.force_2d(prev.geometry.values)

df = pd.concat([df, prev], ignore_index=True)
df["name"] = df.name.str.strip()
df["description"] = df.description.str.strip()

df = df.explode(ignore_index=True)
df["geometry"] = make_valid(df.geometry.values)

write_dataframe(df, bnd_dir / "parca.fgb")
df.to_feather(out_dir / "parca.feather")


### Rasterize PARCAs to in PARCA (1) or not (0)
parcas_colormap = (
    pd.DataFrame(PARCAS)
    .set_index("value")
    .color.apply(lambda x: hex_to_uint8(x) + (255,) if x else (255, 255, 255, 0))
    .to_dict()
)

# use the contiguous southeast grid to derive the master offset coordinates
# so that everything is correctly aligned; these do not occur in Caribbean
# or marine areas
extent = rasterio.open(out_dir / "contiguous_southeast_inland_mask.tif")
extent_data = extent.read(1)

align_ul = np.take(extent.transform, [2, 5]).tolist()


print("Rasterizing PARCAs")
data = rasterize(
    to_dict_all(df.geometry.values),
    transform=extent.transform,
    out_shape=extent.shape,
    fill=0,
    default_value=1,
    dtype="uint8",
)

data = np.where(extent_data == 1, data, NODATA)

outfilename = out_dir / "parcas.tif"
write_raster(
    outfilename,
    data,
    extent.transform,
    crs=extent.crs,
    nodata=NODATA,
)

del data

with rasterio.open(outfilename, "r+") as out:
    out.write_colormap(1, parcas_colormap)

add_overviews(outfilename)

create_lowres_mask(
    outfilename,
    out_dir / "parcas_mask.tif",
    resolution=MASK_RESOLUTION,
    ignore_zero=False,
)
