# SECAS Southeast Conservation Blueprint Data Preparation

Source data are stored in `source_data`; see associated README files for data sources there.

## Data processing steps

1. `prepare_boundaries.py`: Prepare SE region boundary and mask for analysis and mapping
2. `prepare_summary_units.py`: Compile and prepare summary units (HUC12, marine blocks) for analysis and mapping
3. `prepare_ownership.py`: Prepare PAD-US ownership and protection data for analysis and mapping

## Indicators

### South Atlantic

These are prepared in the `sa-blueprint-sv` project.

These are copied from `sa-blueprint-sv/data/inputs/indicators` to `data/inputs/indicators/southatlantic` (including masks).

Continuous indicators are copied from `sa-blueprint-sv/data/continuous_indicators`
to `data/continuous/indicators/southatlantic`.

Indicator config is copied from `sa-blueprint-sv/constants/indicators.json`, and wrapped in:

```json
{
    "input": "sa",
    "indicators": <indicators.json contents from sa-blueprint-sv, prefix ids>
}
```

The full indicator IDs are prefixed with "sa:" and added to the appropriate
ecosystem indicators list in `constants/ecosystems.json`.
