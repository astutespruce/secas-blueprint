from glob import glob
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED

import geopandas as gp
import numpy as np
from pyogrio import write_dataframe
import shapely

from analysis.constants import GEO_CRS
from api.settings import MAX_POLYGONS


drivers = {".geojson": "GeoJSON", ".shp": "ESRI Shapefile", ".gdb": "OpenFileGDB"}

out_dir = Path("tests/fixtures")


def save_to_zip(files: dict[str | Path, gp.GeoDataFrame], outfilename: str):
    with TemporaryDirectory(dir="/tmp") as tmp:
        tmpdir = Path(tmp)
        tmpdir.mkdir(exist_ok=True)

        for filename, df in files.items():
            if "!" in filename:
                filename, layer = filename.split("!")
            else:
                layer = None

            filename = tmpdir / Path(filename)
            write_dataframe(
                df, tmpdir / filename, driver=drivers[filename.suffix], layer=layer, append=(filename).exists()
            )

        with ZipFile(outfilename, "w", compression=ZIP_DEFLATED) as zipfile:
            for filename in glob(f"{tmpdir}/**", recursive=True):
                filename = Path(filename)
                if filename.is_dir():
                    continue

                zipfile.write(filename, str(filename.relative_to(tmpdir)))


# GeoJSON (unsupported format)
save_to_zip({"test.geojson": gp.GeoDataFrame(geometry=[shapely.box(0, 0, 1, 1)], crs=GEO_CRS)}, out_dir / "geojson.zip")

for format in ["shp", "gdb"]:
    # point (unsupported geometry type)
    save_to_zip(
        {f"point.{format}": gp.GeoDataFrame(geometry=[shapely.Point(0, 0)], crs=GEO_CRS)},
        out_dir / f"{format}_point.zip",
    )

    # line (unsupported geometry type)
    save_to_zip(
        {f"line.{format}": gp.GeoDataFrame(geometry=[shapely.LineString([(0, 0), (1, 1)])], crs=GEO_CRS)},
        out_dir / f"{format}_line.zip",
    )

    # multiple files of format (unsupported)
    save_to_zip(
        {
            f"poly1.{format}": gp.GeoDataFrame(geometry=[shapely.box(0, 0, 1, 1)], crs=GEO_CRS),
            f"poly2.{format}": gp.GeoDataFrame(geometry=[shapely.box(1, 1, 2, 2)], crs=GEO_CRS),
        },
        out_dir / f"{format}_poly_multiple_files.zip",
    )

    # too many polygons
    save_to_zip(
        {
            f"poly_too_many.{format}": gp.GeoDataFrame(
                geometry=shapely.box(
                    np.repeat(0, MAX_POLYGONS + 10),
                    np.repeat(0, MAX_POLYGONS + 10),
                    np.repeat(1, MAX_POLYGONS + 10),
                    np.repeat(1, MAX_POLYGONS + 10),
                ),
                crs=GEO_CRS,
            )
        },
        out_dir / f"{format}_poly_too_many.zip",
    )

    # NOTE: the following are specific to the spatial footprint of the Southeast Blueprint
    # no overlap with Blueprint
    save_to_zip(
        {f"poly_no_overlap.{format}": gp.GeoDataFrame(geometry=[shapely.box(0, 0, 1, 1)], crs=GEO_CRS)},
        out_dir / f"{format}_poly_no_overlap.zip",
    )

    # very small overlapping rect less than 1px area
    save_to_zip(
        {
            f"poly_tiny.{format}": gp.GeoDataFrame(
                geometry=[shapely.box(-85.980971, 33.3451, -85.980970, 33.3450)], crs=GEO_CRS
            )
        },
        out_dir / f"{format}_poly_tiny.zip",
    )

    # small overlapping rect
    save_to_zip(
        {f"poly_small.{format}": gp.GeoDataFrame(geometry=[shapely.box(-85.98, 33.340, -85.975, 33.344)], crs=GEO_CRS)},
        out_dir / f"{format}_poly_small.zip",
    )

    # large overlapping rect that is bigger than default limit of 5M acres
    save_to_zip(
        {f"poly_large.{format}": gp.GeoDataFrame(geometry=[shapely.box(-88, 32, -80, 35)], crs=GEO_CRS)},
        out_dir / f"{format}_poly_large.zip",
    )

# multiple layers - FGDB only (unsupported)
save_to_zip(
    {
        "poly.gdb!layer1": gp.GeoDataFrame(geometry=[shapely.box(0, 0, 1, 1)], crs=GEO_CRS),
        "poly.gdb!layer2": gp.GeoDataFrame(geometry=[shapely.box(1, 1, 2, 2)], crs=GEO_CRS),
    },
    out_dir / "gdb_poly_multiple_layers.zip",
)
