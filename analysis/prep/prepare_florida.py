from pathlib import Path
import os
from xml.etree import ElementTree

import pandas as pd
import numpy as np
import rasterio

from analysis.constants import DATA_CRS, MASK_FACTOR
from analysis.lib.io import write_raster
from analysis.lib.input_areas import get_input_area_mask
from analysis.lib.raster import add_overviews, create_lowres_mask, extract_window
from analysis.lib.speedups import remap


src_dir = Path("source_data/florida/inland")
bnd_dir = Path("data/boundaries")
data_dir = Path("data/inputs")
out_dir = data_dir / "indicators/florida"
outfilename = out_dir / "fl_blueprint.tif"

if not out_dir.exists():
    os.makedirs(out_dir)


print("Extracting Florida inland input area mask...")
mask, transform, window = get_input_area_mask("fl")

# ### Extract FL Blueprint
# print("Reading and warping Florida Blueprint...")
# with rasterio.open(src_dir / "HubsData&Blueprint/Blueprint_V_1_3.tif") as src:
#     nodata = int(src.nodata)
#     data = extract_window(src, window, transform, nodata=nodata)

# # fill with 0 where not 1 or 2
# data[data == nodata] = 0

# # apply mask
# data = np.where(mask == 1, data, nodata).astype("uint8")

# write_raster(outfilename, data, transform=transform, crs=DATA_CRS, nodata=nodata)
# add_overviews(outfilename)

# create_lowres_mask(
#     outfilename,
#     str(outfilename).replace(".tif", "_mask.tif"),
#     factor=MASK_FACTOR,
#     ignore_zero=False,
# )


# ### Extract FL indicators from CLIP v4
# indicators = {
#     "clip4_aggregate": "Priority_CLIP4.tif",
#     "clip4_fnai_habitat": "fhab_clip41.tif",
#     "clip4_landscape_resource": "landscape_rp_CLIP4.tif",
#     "clip4_natural_communities": "natcom_CLIP4.tif",
#     "clip4_floodplains": "fldpln_CLIP4.tif",
#     "clip4_surface_water": "srfwtr_CLIP4.tif",
#     "clip4_wetlands": "wetlds_CLIP4.tif",
# }


# for id, indicator_filename in indicators.items():
#     print(f"Reading and warping Florida Blueprint Indicator {id}..")
#     with rasterio.open(src_dir / "indicators" / indicator_filename) as src:
#         nodata = 255
#         data = extract_window(src, window, transform, nodata=nodata)

#     # apply input area mask
#     data = np.where(mask == 1, data, nodata).astype("uint8")

#     outfilename = out_dir / f"{id}.tif"
#     write_raster(outfilename, data, transform=transform, crs=DATA_CRS, nodata=nodata)
#     add_overviews(outfilename)
#     create_lowres_mask(
#         outfilename,
#         str(outfilename).replace(".tif", "_mask.tif"),
#         factor=MASK_FACTOR,
#         ignore_zero=False,
#     )


### Extract FL Conservation assets and summarize

# process attribute table
xml = ElementTree.parse(src_dir / "indicators/BlueprintConAsset/bpv1_3ca2_atts.xml")
root = xml.getroot()
columns = [n.find("Name").text.lower() for n in root.findall("FieldDefn")]
rows = [[n.text for n in row.findall("F")] for row in root.findall("Row")]
atts = (
    pd.DataFrame(rows, columns=columns)
    .drop(columns=["count", "site", "legend", "area_acres"])
    .rename(columns={"name_site": "site", "conser_asset": "asset"})
)

# map to ecosystem
asset_ecosystems = {
    "Coastal Uplands": "land",
    "Freshwater Forested Wetlands": "freshwater",
    "Freshwater Non-forested Wetlands": "freshwater",
    "Hardwod Forested Upland": "land",
    "High Pine and Scrub": "land",
    "Mangrove Swamp": "marine",
    "Pine Flatwoods and Dry Prairie": "land",
    "Ponds and Lakes": "freshwater",
    "Rivers and Streams": "freshwater",
    "Saltwater Marsh": "marine",
    "Springs": "freshwater",
    "Working Lands 1": "land",
    "Working Lands 2": "land",
}

atts["ecosystem"] = atts.asset.map(asset_ecosystems)

# group up to ecosystem, such 1..n is ecosystem ID
ecosystem_ids = {
    ecosystem: i + 1 for i, ecosystem in enumerate(sorted(atts.ecosystem.unique()))
}
atts["new_value"] = atts.ecosystem.map(ecosystem_ids)

atts[["new_value", "asset", "ecosystem"]].rename(
    columns={"new_value": "value"}
).to_feather(out_dir / "ca_atts.feather")

# create remap table
remap_table = atts[["value", "new_value"]].values.astype("uint16")


print("Reading and warping Florida Conservation Assets")
with rasterio.open(src_dir / "indicators/BlueprintConAsset/bpv1_3ca2") as src:
    nodata = int(src.nodata)
    raw_data = extract_window(src, window, transform, nodata=nodata)

# reassign nodata to 255
raw_data[raw_data == nodata] = 255
nodata = 255

raw_data = raw_data.astype("uint16")
data = remap(raw_data, remap_table, nodata=nodata)

# Split each ecosystem into a separate indicator
ecosystems = (
    atts[["new_value", "ecosystem"]]
    .groupby(["new_value", "ecosystem"])
    .first()
    .reset_index()
)
for index, row in ecosystems.iterrows():
    print(f"Writing {row.ecosystem} conservation assets")
    indicator_data = np.where(data == row.new_value, 1, 0).astype("uint8")

    # apply input area mask
    indicator_data = np.where(mask == 1, indicator_data, nodata).astype("uint8")

    outfilename = out_dir / f"{row.ecosystem}_conservation_assets.tif"

    write_raster(
        outfilename, indicator_data, transform=transform, crs=DATA_CRS, nodata=nodata
    )
    add_overviews(outfilename)

    create_lowres_mask(
        outfilename,
        str(outfilename).replace(".tif", "_mask.tif"),
        factor=MASK_FACTOR,
        ignore_zero=False,
    )
