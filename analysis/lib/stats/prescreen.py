from pathlib import Path

import geopandas as gp
import rasterio

from analysis.constants import REPORT_DATASETS, BLUEPRINT, CORRIDORS, URBAN_BY_DECADE, SLR_DEPTH, SLR_PROJ

from analysis.lib.geometry import to_dict_all
from analysis.lib.raster import WindowGeometryMask, get_window, window_overlaps
from analysis.lib.stats.rasterized_geometry import extent_mask_filename


data_dir = Path("data/inputs")


def get_available_datasets(df: gp.GeoDataFrame) -> list[str]:
    """Find all datasets that overlap features in df

    Parameters
    ----------
    df : gp.GeoDataFrame

    Returns
    -------
    list[str]
    """

    datasets = []

    with rasterio.open(extent_mask_filename) as src:
        window = get_window(src, df.total_bounds)

        if not window_overlaps(window, src):
            return datasets

        shapes = to_dict_all(df.geometry.values)
        lowres_mask = WindowGeometryMask(src, window, shapes, all_touched=True)

        # use the lowres extent to determine overlap with blueprint
        if lowres_mask.detect_data(src):
            datasets.extend([BLUEPRINT["id"], CORRIDORS["id"]])

    for dataset_id, dataset in REPORT_DATASETS.items():
        if dataset_id in {BLUEPRINT["id"], CORRIDORS["id"]}:
            continue  # checked above

        if dataset["filename"].endswith(".tif"):
            filename = dataset["filename"].replace(".tif", "_mask.tif")

            if dataset_id == URBAN_BY_DECADE["id"]:
                filename = filename.replace("_{year}", "")

            with rasterio.open(data_dir / filename) as src:
                if lowres_mask.detect_data(src):
                    datasets.append(dataset_id)

                    if dataset_id == SLR_DEPTH["id"]:
                        # SLR projections available where SLR depth is available
                        datasets.append(SLR_PROJ["id"])

    return datasets
