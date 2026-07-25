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
            write_dataframe(df, filename, driver=drivers[filename.suffix], layer=layer, append=(filename).exists())

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
                    np.repeat(0.0001, MAX_POLYGONS + 10),
                    np.repeat(0.0001, MAX_POLYGONS + 10),
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

    save_to_zip(
        {
            f"poly_z_no_overlap.{format}": gp.GeoDataFrame(
                geometry=[shapely.Polygon(((0, 0, 1), (0, 1, 2), (1, 1, 3), (1, 0, 2), (0, 0, 1)))], crs=GEO_CRS
            )
        },
        out_dir / f"{format}_poly_z_no_overlap.zip",
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
        {
            f"poly_small.{format}": gp.GeoDataFrame(
                [{"ID": np.int8(1), "Name": "first"}],
                geometry=[shapely.box(-85.98, 33.340, -85.975, 33.344)],
                crs=GEO_CRS,
            )
        },
        out_dir / f"{format}_poly_small.zip",
    )

    # large overlapping rect that is bigger than default limit of 5M acres
    save_to_zip(
        {
            f"poly_large.{format}": gp.GeoDataFrame(
                [{"ID": np.int8(1), "Name": "first"}], geometry=[shapely.box(-88, 32, -80, 35)], crs=GEO_CRS
            )
        },
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

# create invalid shapefile
with TemporaryDirectory(dir="/tmp") as tmp:
    tmpdir = Path(tmp)
    tmpdir.mkdir(exist_ok=True)
    write_dataframe(gp.GeoDataFrame(geometry=[shapely.box(0, 0, 1, 1)], crs=GEO_CRS), tmpdir / "missing_shx.shp")

    with ZipFile(out_dir / "shp_missing_shx.zip", "w", compression=ZIP_DEFLATED) as zipfile:
        filename = tmpdir / "missing_shx.shp"
        zipfile.write(filename, str(filename.relative_to(tmpdir)))


# test with small rectangles created via geojson.io
df = gp.GeoDataFrame(
    [
        {
            "ID": 1,
            "Name": "first",
            "Region": "continental",
            "Common": "A",
            "geometry": shapely.box(-85.5717, 34.9635, -85.5599, 34.9741),
        },
        {
            "ID": 2,
            "Name": "second",
            "Region": "continental",
            "Common": "A",
            "geometry": shapely.box(-82.6885, 28.8070, -82.6844, 28.8107),
        },
        {
            "ID": 3,
            "Name": "third",
            "Region": "continental",
            "Common": "A",
            "geometry": shapely.box(-91.0470, 33.8705, -91.0399, 33.8760),
        },
        {
            "ID": 4,
            "Name": "five",
            "Region": "caribbean",
            "Common": "A",
            "geometry": shapely.box(-66.5655, 18.3474, -66.5579, 18.3541),
        },
        {
            "ID": 5,
            "Name": "six",
            "Region": "marine",
            "Common": "A",
            "geometry": shapely.box(-80.9222, 31.6965, -80.8734, 31.7390),
        },
    ],
    geometry="geometry",
    crs=GEO_CRS,
)
df["ID"] = df.ID.astype("int8")

for format in ["shp", "gdb"]:
    save_to_zip({f"poly_multiple.{format}": df}, out_dir / f"{format}_poly_multiple.zip")


# one area in Southeast, one in Midwest, one shared by both
df = gp.GeoDataFrame(
    [
        {
            "ID": 1,
            "Name": "first",
            "Blueprint": "Southeast",
            "Common": "A",
            "geometry": shapely.box(-79.5952, 35.0428, -79.5841, 35.0529),
        },
        {
            "ID": 2,
            "Name": "second",
            "Blueprint": "Midwest",
            "Common": "A",
            "geometry": shapely.box(-94.4318, 47.6882, -94.4144, 47.6992),
        },
        {
            "ID": 3,
            "Name": "third",
            "Blueprint": "Southeast,Midwest",
            "Common": "A",
            "geometry": shapely.box(-91.8829, 37.9214, -91.8761, 37.9256),
        },
    ],
    geometry="geometry",
    crs=GEO_CRS,
)
df["ID"] = df.ID.astype("int8")

for format in ["shp", "gdb"]:
    save_to_zip(
        {f"poly_multiple_partial_overlap.{format}": df}, out_dir / f"{format}_poly_multiple_partial_overlap.zip"
    )
