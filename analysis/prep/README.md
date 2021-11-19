# SECAS Southeast Conservation Blueprint Data Preparation

Source data are stored in `source_data`; see associated README files for data sources there.

## Data processing steps

1. `prepare_boundaries.py`: Prepare SE region boundary and mask for analysis and mapping
2. `prepare_input_areas.py`: Prepare input areas and export to feather / GeoTIFF for later processing
3. `prepare_summary_units.py`: Compile and prepare summary units (HUC12, marine blocks) for analysis and mapping
4. `prepare_ownership.py`: Prepare PAD-US ownership and protection data for analysis and mapping
5. `prepare_<input_id>.py`: Prepare each blueprint input dataset
6. `prepare_slr.py`: Prepare SLR data
7. `prepare_urban.py` Prepare urbanization data

## Indicators

### South Atlantic

These are prepared in the `sa-blueprint-sv` project, and then further processed using `prepare_southatlantic.py`.

These are warped and masked from `sa-blueprint-sv/data/inputs/indicators` to `data/inputs/indicators/southatlantic`

Indicator config is copied from `sa-blueprint-sv/constants/indicators.json`, and wrapped in:

```json
{
    "input": "sa",
    "indicators": <indicators.json contents from sa-blueprint-sv, prefix ids>
}
```

The full indicator IDs are prefixed with "sa:" and added to the appropriate
ecosystem indicators list in `constants/ecosystems.json`.
