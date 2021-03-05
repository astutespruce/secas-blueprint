# Florida Conservation Blueprint 1.3 and Marine Blueprint 1.0

Blueprint 1.3 was downloaded from the MS Teams site.

The Marine Blueprint was obtained directly from Tony Gillis @ FWC on 10/27/2020 as a GeoTIFF (files above are unreadable FGDB rasters): FLBlueprintVer1.tif

Data were processed using `analysis/prep/prepare_florida.py` and `analysis/prep/prepare_florida_marine.py`.

## Indicators

Entries for indicators were added to `constants/indicators/fl.json` and `constants/indicators/fl.json`.

### Inland Indicators

The Conservation Assets dataset includes an attribute table of grid codes to string labels.
These were manually copied from the output of `gdalinfo` and saved to `BlueprintConAsset/bpv1_3ca2_atts.xml'.

These were binned to conservation assets, then binned again to ecosystem.

These were then extracted to separate indicator datasets for all areas within
conservation assets assigned to each ecosystem.

CLIP v4 datasets were requested directly from FWC as GeoTIFF files (public versions are unreadable FGDB rasters).
These were provided by FWC on 3/3/2021.

### Marine Indicators

Indicator datasets were downloaded 3/3/2021 from:

- https://www.sciencebase.gov/catalog/item/5d10d158e4b0941bde55011b
- https://www.sciencebase.gov/catalog/item/5d10df90e4b0941bde550164
- https://www.sciencebase.gov/catalog/item/5d10ed67e4b0941bde550225
- https://www.sciencebase.gov/catalog/item/5d10fc8ee4b0941bde550305
- https://www.sciencebase.gov/catalog/item/5d110d65e4b0941bde550424
- https://www.sciencebase.gov/catalog/item/5d4af60fe4b01d82ce8df1a0

Values for several layers were missing internal values between 0 and the lowest
value: e.g., 0,2,3,4,5

To make this more compact, values were shifted down.
