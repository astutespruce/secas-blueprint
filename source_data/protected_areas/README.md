# SECAS Southeast Conservation Blueprint Protected Areas datasets

These are used to summarize protected areas for the user interface and custom reports.

PAD-US v4.1 GDB version downloaded 8/19/2025 from: https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download

## Data fixes

The original PAD-US v4.1 data contains invalid records. In order to get around
this, first create a new geopackage and then create index on state name to make
query faster:

```bash
ogr2ogr source_data/protected_areas/pad_us4.1.gpkg source_data/protected_areas/PADUS4_1.gdb PADUS4_1Combined_Proclamation_Marine_Fee_Designation_Easement -progress -skipfailures -nlt CONVERT_TO_LINEAR
sqlite3 source_data/protected_areas/pad_us4.1.gpkg 'create index state_idx on PADUS4_1Combined_Proclamation_Marine_Fee_Designation_Easement(State_Nm);'
```


## Data processing

Processed using `analysis/prep/prepare_protected_areas.py.

Data on protected areas are rasterized into a binary value (protected vs not) and aligned to the Blueprint.
