# SECAS Southeast Conservation Blueprint Data Preparation

Source data are stored in `source_data`; see associated README files for data sources there.

## Data processing steps

1. `prepare_boundaries.py`: Prepare SE region boundary and mask for analysis and mapping
2. `prepare_summary_units.py`: Compile and prepare summary units (HUC12, marine hexes) for analysis and mapping
3. `prepare_protected_areas.py`: Prepare PAD-US protected areas data for analysis and mapping
4. `prepare_blueprint.py`: Prepare SE Blueprint, corridors, and indicators for analysis and mapping
5. `prepare_imperiled_amphibians_reptiles_subindicator.py`: Prepare imperiled amphibians & reptiles subindicator
6. `prepare_intact_habitat_cores_subindicator`: Prepare intact habitat cores subindicator
7. `prepare_slr.py`: Prepare SLR data
8. `prepare_nlcd.py`: Prepare NLCD data
9. `prepare_urban.py`: Prepare urbanization data
10. `tabulate_summary_units.py`: Tabulate Blueprint, all inputs, and threats by HUC12 and marine hex
11. `package_unit_data.py`: Restructure data for HUC12 and marine hexes to attach to boundary datasets for map tiles
12. `tiles/create_vector_tiles.py`: Create vector tiles from HUC12, marine hexes, blueprint region and mask, input areas, and protected areas
13. `tiles/encode_pixel_layers.py`: Stack and encode pixel layers for data tiles
14. `tiles/create_raster_tiles.sh`: Create Blueprint and data tiles

Note: once tiles are rendered, they are moved to `secas-docker/tiles` directory.
