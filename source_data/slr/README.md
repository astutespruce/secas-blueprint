# SECAS Southeast Conservation Blueprint Sea Level Rise data

### Download SLR data

The latest SLR data are downloaded from [NOAA](https://coast.noaa.gov/slrdata/)
as polygon extent of inundation per foot of depth between 0 and 10 feet.

Data downloaded 7/31/2022.

Data are downloaded using `analysis/prep/download_slr.py`.

## Rasterize SLR data

SLR data polygons are rasterized to 15 meter resolution using SE Bluprint
standard projection (EPSG:5070) and snapped to the Blueprint grid so that
everything aligns correctly.

Data are prepared using `analysis/prep/rasterize_slr.py`

Values are coded 0 (already inundated) - 10 feet.

Because SLR data covers a relatively small area but a very large extent, data
are retained in their original chunks as delivered by NOAA, and compiled into
a virtual raster table using GDAL.

This step also creates a polygon boundary dataset of all areas covered by SLR
datasets, which can be intersected with an area of interest to determine if SLR
data are available.

The final output file of this step is `data/inputs/threats/slr/slr.vrt`.

Both the VRT file and the individual GeoTIFFs need to be present for analysis.
