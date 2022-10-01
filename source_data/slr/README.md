# SECAS Southeast Conservation Blueprint Sea Level Rise data

## SLR inundation depth data

The latest SLR data are downloaded on 7/31/2022 from
[NOAA](https://coast.noaa.gov/slrdata/) as polygon extent of inundation per foot
of depth between 0 and 10 feet.

Data are downloaded using `analysis/prep/download_slr.py`.

The latest SLR projections by decade and scenario at 1 degree grid cell
resolution were downloaded on 8/24/2022 from
[NOAA](https://oceanservice.noaa.gov/hazards/sealevelrise/sealevelrise-data.html).

Data are prepared using `analysis/prep/prep_slr.py` and involves the following
major steps:

### Rasterize SLR data

SLR data polygons are rasterized to 30 meter resolution using SE Bluprint
standard projection (EPSG:5070) and snapped to the Blueprint grid so that
everything aligns correctly.

Small isolated polygons and holes less than half a pixel in area are removed.

Values are coded 0 (already inundated) - 10 feet.

Because SLR data covers a relatively small area but a very large extent, data
are retained in their original chunks as delivered by NOAA, and compiled into
a virtual raster table using GDAL.

The final output file of this step is `data/inputs/threats/slr/slr.tif`.

### Create 1-degree grid cells with projection data

1-degree grid cells are extracted from the NOAA CSV downloaded above.

Median projection values for 2020 through 2100 are added to the offset for 2000-2005
as directed in the header of the CSV and converted to feet.

The projection values are available for the following NOAA projections:

- Low
- Intermediate-Low
- Intermediate
- Intermediate-High
- High

Only those cells that intersect with areas where SLR data were available,
according to the coarse-resolution (480m) mask of SLR data, are retained for
analysis.

These are ultimately intersected with a user's area of interest to calculate
the mean of medians (each grid cell is a median) for each NOAA scenario for each
decade.

TODO: decide if statistics should be area-weighted or regular.
