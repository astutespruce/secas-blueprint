# SECAS Southeast Conservation Blueprint Urban Growth data

Urbanization data were provided by Anna Petrasova (Center for Geospatial Analytics,
North Carolina State University) to USFWS staff on 6/23/2022, and downloaded
from USFWS teams site on 8/2/2022.

Data are processed using `analysis/prep/prepare_urban.py`.

Data are clipped to the inland portion of the Base Blueprint. Data are not
available for Puerto Rico or U.S. Virgin Islands.

Data are first converted from floating point to frequency bins (number of times
out of 50 model runs that predicted urbanization).

Value 51 denotes currently urbanized in NLCD 2019.

# TODO: citation
