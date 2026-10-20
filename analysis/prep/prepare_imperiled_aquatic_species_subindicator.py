import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import shapely
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import DATA_CRS, INDICATORS_INDEX, M2_ACRES

warnings.filterwarnings("ignore", message=".*a polygon with more than 100 parts.*")

src_dir = Path("source_data/subindicators")
data_dir = Path("data")
out_dir = data_dir / "inputs"
subindicators_out_dir = out_dir / "subindicators"
subindicators_out_dir.mkdir(exist_ok=True)
working_dir = src_dir / "derived"
working_dir.mkdir(exist_ok=True)

indicator_id = "f_imperiledaquaticspecies"
indicator = INDICATORS_INDEX[indicator_id]
subindicator = indicator["subindicator"]

### Only keep HUC12s in continental
subregions = read_dataframe(
    data_dir / "boundaries/subregions.fgb", where="subregion not in ('US Virgin Islands', 'Puerto Rico')"
)

df = (
    read_dataframe(src_dir / "SECAS_anon_rsgcn_spp_HUC12.gdb", columns=["HUC12", "species_ids"], use_arrow=True)
    .explode(ignore_index=True)
    .to_crs(DATA_CRS)
)
ix = np.unique(shapely.STRtree(df.geometry.values).query(subregions.geometry.values, predicate="intersects")[1])
df = df.take(ix).reset_index(drop=True)
df["acres"] = (df.area * M2_ACRES).astype("float32")
write_dataframe(df, out_dir / subindicator["filename"])
