from pathlib import Path

from analysis.lib.raster import add_overviews

src_dir = Path("data/inputs")
blueprint_filename = src_dir / "se_blueprint2021.tif"

add_overviews(blueprint_filename)
