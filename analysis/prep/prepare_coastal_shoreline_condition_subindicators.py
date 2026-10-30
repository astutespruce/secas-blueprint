from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
import shapely
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import DATA_CRS, INDICATORS_INDEX, M_MILES

src_dir = Path("source_data/subindicators")
data_dir = Path("data")
out_dir = data_dir / "inputs"
subindicators_out_dir = out_dir / "subindicators"
subindicators_out_dir.mkdir(exist_ok=True)
working_dir = src_dir / "derived"
working_dir.mkdir(exist_ok=True)


bnd = read_dataframe(data_dir / "boundaries/se_boundary.fgb").geometry.values[0]
shapely.prepare(bnd)

################################################################################
### Extract continental coastal shoreline condition
################################################################################
print("Extracting continental coastal shoreline condition length")

indicator_id = "m_coastalshorelinecondition"
indicator = INDICATORS_INDEX[indicator_id]
subindicator = indicator["subindicator"]


### extract saline estuarine shorelines, where LINE field is not ‘H’ and ENVIR field is ‘E’.
esi = (
    read_dataframe(
        src_dir / "NationalESI_Shoreline/GULF_ATLANTIC_ESI.gdb",
        where="LINE != 'H' AND ENVIR = 'E'",
        columns=["LINE", "ENVIR", "GENERALIZED_ESI_TYPE"],
    )
    .to_crs(DATA_CRS)
    .rename(columns={"GENERALIZED_ESI_TYPE": "esi_type"})
    .explode(ignore_index=True)
    .drop(columns=["LINE", "ENVIR"])
)

esi = esi.take(shapely.STRtree(esi.geometry.values).query(bnd, predicate="intersects"))

### assign initial values
esi["value"] = np.uint8(3)
esi.loc[esi.esi_type.str.contains("Armored"), "value"] = np.uint8(1)
esi.loc[esi.esi_type == "1: Armored", "value"] = np.uint8(0)
esi = esi.drop(columns=["esi_type"])

### clip to boundary
contained = shapely.contains_properly(bnd, esi.geometry.values)
esi.loc[~contained, "geometry"] = shapely.intersection(bnd, esi.loc[~contained].geometry.values)
esi = esi.explode(ignore_index=True)

### intersect with CBRS
cbrs = (
    read_dataframe(src_dir / "20241219-cbrs-boundaries/20241219_CBRS_Polygons.shp", columns=[], use_arrow=True)
    .to_crs(DATA_CRS)
    .explode(ignore_index=True)
)

left, right = shapely.STRtree(esi.geometry.values).query(cbrs.geometry.values, predicate="intersects")
outside = esi.take(np.setdiff1d(esi.index.values, np.unique(right)))
outside["cbrs"] = False

pairs = pd.DataFrame(
    {
        "cbrs_geometry": cbrs.geometry.values.take(left),
        "geometry": esi.geometry.values.take(right),
        "value": esi.value.take(right),
    }
)
shapely.prepare(pairs.cbrs_geometry.values)
pairs["contained"] = shapely.contains_properly(pairs.cbrs_geometry.values, pairs.geometry.values)

inside = pairs.loc[pairs.contained].copy()
inside["cbrs"] = True

inside_part = pairs.loc[~pairs.contained].copy()
inside_part["geometry"] = shapely.intersection(inside_part.geometry.values, inside_part.cbrs_geometry.values)
inside_part["cbrs"] = True

outside_part = pairs.loc[~pairs.contained].copy()
outside_part["geometry"] = shapely.difference(outside_part.geometry.values, outside_part.cbrs_geometry.values)
outside_part["cbrs"] = False

esi = gp.GeoDataFrame(
    pd.concat(
        [
            outside,
            inside[["geometry", "value", "cbrs"]],
            inside_part[["geometry", "value", "cbrs"]],
            outside_part[["geometry", "value", "cbrs"]],
        ]
    ),
    geometry="geometry",
    crs=DATA_CRS,
).explode(ignore_index=True)

del pairs

### Bump values within CBRS
esi.loc[(esi.value == 1) & (esi.cbrs), "value"] = 2
esi.loc[(esi.value == 3) & (esi.cbrs), "value"] = 4
esi = esi.drop(columns=["cbrs"])

# drop short lines < 0.1 meters
esi = esi.loc[esi.length >= 0.1].sort_values(by="geometry").reset_index(drop=True)
esi["miles"] = (esi.length * M_MILES).astype("float32")

write_dataframe(esi, out_dir / subindicator["filename"])


################################################################################
### Extract Caribbean coastal shoreline condition
################################################################################
print("Extracting Caribbean coastal shoreline condition length")

indicator_id = "m_caribbeancoastalshorelinecondition"
indicator = INDICATORS_INDEX[indicator_id]
subindicator = indicator["subindicator"]


columns = ["ATTRIBUTE"]
files = ["N15W065.zip", "N15W070.zip"]
cusp = pd.concat(
    [read_dataframe(src_dir / "CUSP" / filename, columns=columns, use_arrow=True) for filename in files],
    ignore_index=True,
).to_crs(DATA_CRS)
cusp["value"] = np.uint8(0)
cusp.loc[cusp.ATTRIBUTE.str.lower().str.contains("natural"), "value"] = np.uint8(1)
cusp = cusp[["value", "geometry"]].copy()

### clip to the caribbean
subregions = read_dataframe(
    data_dir / "boundaries/subregions.fgb", where="subregion in ('US Virgin Islands', 'Puerto Rico')"
)
caribbean = shapely.union_all(subregions.geometry.values)
shapely.prepare(caribbean)

cusp = cusp.take(shapely.STRtree(cusp.geometry.values).query(caribbean, predicate="intersects"))
contained = shapely.contains_properly(caribbean, cusp.geometry.values)
cusp.loc[~contained, "geometry"] = shapely.intersection(caribbean, cusp.loc[~contained].geometry.values)

### clip to the boundary
cusp = cusp.take(shapely.STRtree(cusp.geometry.values).query(bnd, predicate="intersects"))
contained = shapely.contains_properly(bnd, cusp.geometry.values)
cusp.loc[~contained, "geometry"] = shapely.intersection(bnd, cusp.loc[~contained].geometry.values)

cusp = cusp.loc[cusp.length >= 0.1].sort_values(by="geometry").reset_index(drop=True)
cusp["miles"] = (cusp.length * M_MILES).astype("float32")

write_dataframe(cusp, out_dir / subindicator["filename"])
