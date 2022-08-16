# SECAS Southeast Conservation Blueprint Urban Growth data

Urbanization data were provided by Anna Petrasova (Center for Geospatial Analytics,
North Carolina State University) to USFWS staff on 6/23/2022, and downloaded
from USFWS teams site on 8/2/2022.

Data are processed using `analysis/prep/prepare_urban.py`.

Data are first converted from floating point to probability bins derived from
SLEUTH as used in prior versions of the Blueprint Explorer:

0: not projected to urbanize
1: already urban in 2019

Probability of urbanization:
2: 0.025
3: 0.05
4: 0.1
5: 0.2
6: 0.3
7: 0.4
8: 0.5
9: 0.6
10: 0.7
11: 0.8,
12: 0.9
13: 0.95
14: 0.975
15: 1

From a review of the data, areas of probability == 1 in 2020 are already urbanized;
these are burned into all the other timesteps.

Data are then warped to match the SE Blueprint grid and clipped to the SE Blueprint
extent.
