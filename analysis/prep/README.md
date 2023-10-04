# SECAS Southeast Conservation Blueprint Data Preparation

Source data are stored in `source_data`; see associated README files for data sources there.

## Data processing steps

1. `prepare_boundaries.py`: Prepare SE region boundary and mask for analysis and mapping
2. `prepare_summary_units.py`: Compile and prepare summary units (HUC12, marine blocks) for analysis and mapping
3. `prepare_ownership.py`: Prepare PAD-US ownership and protection data for analysis and mapping
4. `prepare_blueprint.py`: Prepare SE Blueprint for analysis and mapping
5. `prepare_<input_id>.py`: Prepare each blueprint input dataset
6. `prepare_slr.py`: Prepare SLR data
7. `prepare_urban.py` Prepare urbanization data
8. `tabulate_summary_units.py`: Tabulate Blueprint, all inputs, and threats by HUC12 and marine lease block
9. `package_unit_data.py`: Restructure data for HUC12 and marine lease blocks to attach to boundary datasets for map tiles
10. `create_tiles.sh`: Create vector tiles from HUC12, marine lease blocks, blueprint region and mask, input areas, and protected areas
11. `render_blueprint_tiles.py`: Create image tiles from Blueprint.

Note: once tiles are rendered, they are moved to `secas-docker/tiles` directory.

## Indicators

The full indicator IDs are prefixed with "sa:" and added to the appropriate
ecosystem indicators list in `constants/ecosystems.json`.
