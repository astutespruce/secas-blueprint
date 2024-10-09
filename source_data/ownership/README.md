# SECAS Southeast Conservation Blueprint Ownership datasets

These are used to summarize land ownership types and protection types for
the user interface and custom reports.

PAD-US v4.0 GDB version downloaded 6/4/2024 from: https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download

PAD-US v3.0 GDB version was downloaded 9/21/2022. This version was used to
provide Wildlife Management Areas in Oklahoma, which were incorrectly omitted
from PAD-US v4.0.

## Data fixes

The original PAD-US v3.0 data contains invalid records. In order to get around
this, first create a new geopackage and then create index on state name to make
query faster:

```bash
ogr2ogr source_data/ownership/pad_us3.0.gpkg source_data/ownership/PAD_US3_0.gdb PADUS3_0Combined_Proclamation_Marine_Fee_Designation_Easement -progress -skipfailures
sqlite3 source_data/ownership/pad_us3.0.gpkg 'create index state_idx on PADUS3_0Combined_Proclamation_Marine_Fee_Designation_Easement(State_Nm);'
```

Do the same thing for PAD-US v4.0 because it also contains invalid records and need to force MultiSurface geometries to MultiPolygon:

```bash
ogr2ogr source_data/ownership/pad_us4.0.gpkg source_data/ownership/PADUS4_0_Geodatabase.gdb PADUS4_0Combined_Proclamation_Marine_Fee_Designation_Easement -progress -skipfailures -nlt MultiPolygon
sqlite3 source_data/ownership/pad_us4.0.gpkg 'create index state_idx on PADUS4_0Combined_Proclamation_Marine_Fee_Designation_Easement(State_Nm);'
```

## Data processing

Processed using `analysis/prep/prepare_ownership.py.
