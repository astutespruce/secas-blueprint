# SECAS Southeast Conservation Blueprint Ownership datasets

These are used to summarize land ownership types and protection types for
the user interface and custom reports.

PAD-US v3.0 GDB version downloaded 9/21/2022 from: https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download

NOTE: the GPKG version is missing several features, don't use it.

## Data fixes

The original PADUS data contains invalid records. In order to get around this, first create a new geopackage:

```
ogr2ogr source_data/ownership/pad_us3.0.gpkg source_data/ownership/PAD_US3_0.gdb PADUS3_0Combined_Proclamation_Marine_Fee_Designation_Easement -progress -skipfailures
```

Then create index on state name to make query faster:

```
sqlite3 source_data/ownership/pad_us3.0.gpkg 'create index state_idx on PADUS3_0Combined_Proclamation_Marine_Fee_Designation_Easement(State_Nm);'
```

## Data processing

Processed using `analysis/prep/prepare_ownership.py.
