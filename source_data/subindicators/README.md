# Sub-indicator data

These are select datasets that add additional detail for select indicators.

## Source data

### Imperiled amphibians and reptiles

These data are preprared using `analysis/prep/prepare_imperiled_amphibians_reptiles_subindicator.py`.

Amphibian GAP models were provided by Rua Mordecai via email on 9/2/2026 and
reptiles on 10/6/2026. Rua also provided the RSGCN species list.

All RSGCN species identified as amphibians or reptiles in the spreadsheet that
had a model available for their ID were extracted to Blueprint-aligned rasters
at their minimum data extent instead of the large standardized model extent.
Some species had multiple rows in the RSGCN spreadsheet but a single ID; these
were lumped together and listed as a single record with all species names for
the corresponding species. Some species did not have models available.

Species were grouped into groups of 64 species and stacked into a 64 bit unsigned
integer grid, where each species was assigned 0 or 1 for a particular bit position
within that grid.

This subindicator is used to identify the unique list of species present for a
given area of interest.

To calculate this value, we read the raw unsigned integer values and bitwise-OR
them together to get a single value representing all bits turned on for every
species present in that area. We then identify which bits are turned on and use
that to look up the species by bit position for each group of species.

### Intact habitat core size

These data are prepared using `prepare_intact_habitat_cores_subindicator.py`.

Intact habitat core polygons were provided by Hilary Morris via email on 8/11/2026.
We assigned cores to the size classes used by the indicator.

This subindicator is used to find the number of overlapping cores of each size
class, and minimum, mean, and maximum core size for overlapping cores of each
size class.

### Coastal shoreline condition (continental)

These data are prepared using `prepare_coastal_shoreline_condition_subindicators.py`.

Environmental Sensitivity Index (ESI) shoreline data were downloaded from
https://response.restoration.noaa.gov/sites/default/files/esimaps/gisdata/NationalESI_Shoreline.zip
on 8/12/2026.

Coastal Barrier Resource System (CBRS) data were downloaded from https://www.fws.gov/media/digital-coastal-barrier-resources-system-boundaries
on 8/12/2026.

ESI data were extracted where `LINE != 'H' AND ENVIR = 'E'` and clipped to the
Blueprint extent. ESI data were intersected with CBRS polygons. Data were
classified into the same values as the indicator based on `GENERALIZED_ESI_TYPE`
and overlap with CBRS:

- 0: `GENERALIZED_ESI_TYPE` is only `1: Armored`
- 1: `GENERALIZED_ESI_TYPE` contains multiple types at least one of which is armored
- 2: same as above but within CBRS polygons
- 3: `GENERALIZED_ESI_TYPE` does not contain any armored types
- 4: same as above but within CBRS polygons

Small line fragments <0.1 meters were dropped.

This subindicator is used to find the length by indicator value within an area
of interest.

### Caribbean coastal shoreline condition

These data are prepared using `prepare_coastal_shoreline_condition_subindicators.py`.

Continually Updated Shoreline Product (CUSP) data were downloaded for Puerto Rico
and the U.S. Virgin Islands from https://nsde.ngs.noaa.gov/ on 10/19/2026. Download
was limited to data available up through 2023 to align with the indicator.

CUSP data were classified acording to `Attribute`:

- 0: default
- 1: `Attribute` contains the word "natural"

CUSP data were clipped to the Puerto Rico and US Virgin Islands subregion boundary
and clipped again to the Blueprint extent.

This subindicator is used to find the length by indicator value within an area
of interest.
