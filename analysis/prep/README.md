# SECAS Southeast Conservation Blueprint Data Preparation

Source data are stored in `source_data`; see associated README files for data sources there.

## Data processing steps

1. `prepare_boundaries.py`: Prepare SE region boundary and mask for analysis and mapping
2. `prepare_summary_units.py`: Compile and prepare summary units (HUC12, marine hexes) for analysis and mapping
3. `prepare_protected_areas.py`: Prepare PAD-US protected areas data for analysis and mapping
4. `prepare_blueprint.py`: Prepare SE Blueprint, corridors, and indicators for analysis and mapping
5. `prepare_slr.py`: Prepare SLR data
6. `prepare_nlcd.py`: Prepare NLCD data
7. `prepare_urban.py`: Prepare urbanization data
8. `tabulate_summary_units.py`: Tabulate Blueprint, all inputs, and threats by HUC12 and marine hex
9. `package_unit_data.py`: Restructure data for HUC12 and marine hexes to attach to boundary datasets for map tiles
10. `tiles/create_vector_tiles.py`: Create vector tiles from HUC12, marine hexes, blueprint region and mask, input areas, and protected areas
11. `tiles/encode_pixel_layers.py`: Stack and encode pixel layers for data tiles
12. `tiles/create_raster_tiles.sh`: Create Blueprint and data tiles

Note: once tiles are rendered, they are moved to `secas-docker/tiles` directory.
