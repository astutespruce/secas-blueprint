# SECAS Southeast Conservation Blueprint Ownership datasets

These are used to summarize land ownership types and protection types for
the user interface and custom reports.

PAD-US v2.1 downloaded 10/2/2020 from: https://www.sciencebase.gov/catalog/item/5f186a2082cef313ed843257

## Data fixes

The original PADUS data contains invalid records. In order to get around this, first run:

```
ogr2ogr source_data/ownership/pad_us2_1.gpkg source_data/ownership/PAD_US2_1.gdb PADUS2_1Combined_Marine_Fee_Designation_Easement -progress
```

Then create index on state name to make query faster:

```
sqlite3 source_data/ownership/pad_us2_1.gpkg 'create index state_idx on PADUS2_1Combined_Marine_Fee_Designation_Easement(State_Nm);'
```

## Data processing

Processed using `analysis/prep/prepare_ownership.py.
