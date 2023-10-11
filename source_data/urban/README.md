# SECAS Southeast Conservation Blueprint Urban Growth data

Urbanization data were downloaded from https://www.sciencebase.gov/catalog/item/63f50297d34efa0476b04cf7
on 10/5/2023.

## Data processing

Data are processed using `analysis/prep/prepare_urban.py`.

Data are clipped to the inland portion of the Base Blueprint. Data are not
available for Puerto Rico or U.S. Virgin Islands.

Data are first converted from floating point to frequency bins (number of times
out of 50 model runs that predicted urbanization).

Value 51 denotes currently urbanized in NLCD 2019. NLCD 2019 data were prepared
separately for use in this tool; see `source_data/nlcd/README.md`.
