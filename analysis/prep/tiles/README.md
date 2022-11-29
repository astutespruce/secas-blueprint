# Southeast Blueprint Explorer Tileset Creation

## Vector tilesets

The Southeast boundary, mask, summary units, state boundaries, and protected areas
are converted to vector tiles for use in the frontend or for PDF maps.

Summary units are first prepared for tiling using `analysis/prep/package_unit_data.py`,
which creates a Feather file with encoded attributes for the Blueprint,
Base Blueprint and indicators, other Blueprint inputs, sea-level rise, and
urbanization.

Vector tiles are then created using `analysis/prep/tiles/create_vector_tiles.py`.

## Raster tilesets

Raster tiles for the Blueprint and data tiles are created using `rastertiler-rs`, which is built from source:

- clone rastertiler-rs repository using Git
- in rastertiler-rs root directory, run `cargo build --release`
- executable is located at <rastertiler-rs root>/target/realease/rastertiler

### Blueprint image tiles

The Blueprint is rendered to paletted image tiles for display:

TODO: maybe can split this up; zooms <= 7-8 can use overviews and complete much faster,
only slight pixel shifting vs without?

```bash
../rastertiler-rs/target/release/rastertiler data/inputs/se_blueprint_2022.tif tiles/se_blueprint_2022.mbtiles -s 512 --colormap "1:#6C6C6C,2:#8C96C6,3:#843F98,4:#4D004B" -Z 2 -z 14 --disable-overviews
```

NOTE: the colormap will need to be updated if colors change. 0 values are omitted.

This takes about 3 hours for zooms 2-14.

### Indicator data tiles

The data tiles approach generally consists of:

- each layer takes up a known number of bits to represent its full range of values
- 0 is set as NODATA for all layers; any layers that have a valid value of 0 are shifted up to 1..n
- layers are grouped such that no group requires more than 24 bits (for RGB PNG); these are selected manually in part to group layers with similar extents together
- each layer is assigned a particular bit range within its group
- each layer in the group is read from its data source, and bit-shifted to the correct position, then combined with other layers in the group
- the group is output as an encoded GeoTIFF
- the GeoTIFF is encoded to RGB PNG image tiles
- each tile is decoded in the user interface and values are bit-masked and shifted to extract the original values for each layer

The indicators are encoded for data tiles using `analysis/prep/tiles/encode_pixel_layers.py`.

This creates an encoded GeoTIFF for each group of layers.

These layers are then converted into PNG tiles using `rastertiler-rs`:

```bash
../rastertiler-rs/target/release/rastertiler data/for_tiles/se_pixel_layers_<n>.tif tiles/se_pixel_layers_<n>.mbtiles -s 512 -Z 5 -z 14
```

(where `n` refers to group index 0..n)

Note: tiles are generated at 512px size to match the standard tile size in the
user interface (smaller tile sizes are fetched at the next higher zoom, which
leads to many more requests).
