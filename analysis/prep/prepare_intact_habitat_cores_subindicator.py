import warnings
from pathlib import Path

import pandas as pd
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import M2_ACRES

warnings.filterwarnings("ignore", message=".*a polygon with more than 100 parts.*")

src_dir = Path("source_data/subindicators")
data_dir = Path("data")
out_dir = data_dir / "inputs"
subindicators_out_dir = out_dir / "subindicators"
subindicators_out_dir.mkdir(exist_ok=True)
working_dir = src_dir / "derived"
working_dir.mkdir(exist_ok=True)

indicator_id = "t_intacthabitatcores"

bnd = read_dataframe(data_dir / "boundaries/se_boundary.fgb").geometry.values[0]
df = read_dataframe(src_dir / "IntactHabitatCores2023_Export.gdb", columns=[], mask=bnd, use_arrow=True).explode(
    ignore_index=True
)
del bnd

df["acres"] = df.area * M2_ACRES

# create size classes to match the indicator:
# >100-1,000; >1,000-10,000; >10,000
df["size"] = pd.cut(df.acres, [100, 1000, 10000, df.acres.max() + 1], labels=["small", "medium", "large"], right=True)

write_dataframe(df[["acres", "size", "geometry"]], subindicators_out_dir / f"{indicator_id}_size.fgb")
