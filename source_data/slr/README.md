# SECAS Southeast Conservation Blueprint Sea Level Rise data

NOTE: this is not aligned to the blueprint grid.

Data were obtained from Amy Keister on 3/10/2020. She exported individual
Geotiffs created from the source files created in her processing chain for
mosiacking SLR data obtained from NOAA (https://coast.noaa.gov/slrdata/).

These are a series of GeoTIFF files
for small areas along the coast, with varying footprints and resolution. To use
here, we constructed a VRT using GDAL, and used the average resolution.

Values are coded 0-6 for the amount of sea level rise that would impact a given
area. Values are cumulative, so a value of 6 means that the area is also
inundated by 1-5 meters.

From within `data/threats/slr` directory:

```
gdalbuildvrt -overwrite -resolution lowest slr.vrt *.tif
```

To assist with checking if a given area of interest overlaps SLR data, the
bounds of all SLR files are extracted to a dataset using
`util/prepare_slr.py`.
