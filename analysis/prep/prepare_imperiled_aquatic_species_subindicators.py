import warnings
from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
import shapely
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import DATA_CRS, INDICATORS_INDEX

warnings.filterwarnings("ignore", message=".*a polygon with more than 100 parts.*")

src_dir = Path("source_data/subindicators")
data_dir = Path("data")
out_dir = data_dir / "inputs"
subindicators_out_dir = out_dir / "subindicators"
subindicators_out_dir.mkdir(exist_ok=True)
working_dir = src_dir / "derived"
working_dir.mkdir(exist_ok=True)


################################################################################
### Process continental aquatic imperiled species
################################################################################
indicator_id = "f_imperiledaquaticspecies"
indicator = INDICATORS_INDEX[indicator_id]
subindicator = indicator["subindicator"]

df = (
    read_dataframe(src_dir / "SECAS_anon_rsgcn_spp_HUC12.gdb", columns=["HUC12", "species_ids"], use_arrow=True)
    .explode(ignore_index=True)
    .to_crs(DATA_CRS)
    .rename(columns={"species_ids": "species"})
)

# Only keep HUC12s in continental
subregions = read_dataframe(
    data_dir / "boundaries/subregions.fgb", where="subregion not in ('US Virgin Islands', 'Puerto Rico')"
)
ix = np.unique(shapely.STRtree(df.geometry.values).query(subregions.geometry.values, predicate="intersects")[1])
df = df.take(ix).reset_index(drop=True)
df["species"] = df.species.fillna("").str.replace(",", "|")
df.loc[df.species == "", "species"] = None
write_dataframe(df, out_dir / subindicator["filename"])


################################################################################
### Process continental aquatic imperiled species
################################################################################
indicator_id = "f_caribbeanimperiledaquaticspecies"
indicator = INDICATORS_INDEX[indicator_id]
subindicator = indicator["subindicator"]

huc12 = read_dataframe(
    data_dir / "boundaries/huc12.fgb", where="SUBSTR(id, 0, 2) = '21'", columns=["id"], use_arrow=True
).rename(columns={"id": "HUC12"})

reader = pd.ExcelFile(src_dir / "CombinedKwakData_ForSARP.xlsx", engine="calamine")
sites = reader.parse(sheet_name="SamplingSiteCoordinates").rename(
    columns={"Site number": "site", "Latitude (N)": "lat", "Longitude (W)": "lon"}
)

### parse lat / lon from degrees minutes decimal seconds to decimal degrees
dms_regex = r'(\d+)°\s*(\d+)\'\s*([\d.]+)"'
lat_components = sites["lat"].str.extract(dms_regex, expand=True).astype("float64")
lat_components[1] /= 60.0
lat_components[2] /= 3600.0
lon_components = sites["lon"].str.extract(dms_regex, expand=True).astype("float64")
lon_components[1] /= 60.0
lon_components[2] /= 3600.0

sites["lat"] = lat_components.sum(axis=1)
sites["lon"] = -lon_components.sum(axis=1)

sites = gp.GeoDataFrame(
    sites[["site"]], geometry=shapely.points(sites.lon.values, sites.lat.values), crs="EPSG:4326"
).to_crs(DATA_CRS)

species = reader.parse(sheet_name="Combined Species List").rename(
    columns={"Scientific name": "SNAME", "Common Name": "CNAME", "SGCN in 2025?": "SGCN"}
)
species = species.loc[species.SGCN == "Y"].copy()
species["species"] = species.CNAME + " (" + species.SNAME + ")"
species = species.drop(columns=["SNAME", "CNAME", "SGCN"])
# rest of columns are site IDs
cols = [c for c in species.columns if c != "species"]
species = species.melt(id_vars=["species"], var_name="site", value_name="present")
species = species.loc[species.present == "X"].set_index("site").species

### Join to HUC12s
left, right = shapely.STRtree(sites.geometry.values).query(huc12.geometry.values, predicate="intersects")
pr_spp = pd.DataFrame({"HUC12": huc12.HUC12.values.take(left), "site": sites.site.values.take(right)}).join(
    species, on="site", how="inner"
)[["HUC12", "species"]]


### Read USVI data
vi_spp = pd.read_excel(
    src_dir / "Final_Summaries_ForUSVI_March2025.xls", sheet_name="Species_Names_by_HUC12", engine="calamine"
).rename(columns={"Species_Name": "SNAME", "Common_Name": "CNAME", "HUC12_Code": "HUC12"})
vi_spp["HUC12"] = vi_spp.HUC12.astype("str")
vi_spp["species"] = vi_spp.CNAME + " (" + vi_spp.SNAME + ")"
vi_spp = vi_spp.loc[vi_spp.SGCN_Listing == "Yes", ["HUC12", "species"]]

spp = pd.concat([pr_spp, vi_spp], ignore_index=True).groupby("HUC12").species.unique().apply("|".join)

df = huc12.join(spp, on="HUC12")
write_dataframe(df, out_dir / subindicator["filename"])
