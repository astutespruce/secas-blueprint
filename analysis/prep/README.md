# SECAS Southeast Conservation Blueprint Data Preparation

Source data are stored in `source_data`; see associated README files for data sources there.

## Data processing steps

1. `prepare_boundaries.py`: Prepare SE region boundary and mask for analysis and mapping
2. `prepare_input_areas.py`: Prepare input areas and export to feather / GeoTIFF for later processing
3. `prepare_summary_units.py`: Compile and prepare summary units (HUC12, marine blocks) for analysis and mapping
4. `prepare_ownership.py`: Prepare PAD-US ownership and protection data for analysis and mapping
5. `prepare_blueprint.py`: Prepare SE Blueprint for analysis and mapping
6. `prepare_<input_id>.py`: Prepare each blueprint input dataset
7. `prepare_slr.py`: Prepare SLR data (if needed; can directly copy outputs from sa-blueprint-sv)
8. `prepare_urban.py` Prepare urbanization data
9. `tabulate_area.py`: Tabulate Blueprint, all inputs, and threats by HUC12 and marine lease block
10. `package_unit_data.py`: Restructure data for HUC12 and marine lease blocks to attach to boundary datasets for map tiles
11. `create_tiles.sh`: Create vector tiles from HUC12, marine lease blocks, blueprint region and mask, input areas, and protected areas
12. `render_blueprint_tiles.py`: Create image tiles from Blueprint.

Note: once tiles are rendered, they are moved to `secas-docker/tiles` directory.

## Indicators

The full indicator IDs are prefixed with "sa:" and added to the appropriate
ecosystem indicators list in `constants/ecosystems.json`.
