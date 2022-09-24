# Southeast Blueprint Explorer Tileset Creation

## Vector tilesets

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

The indicators are encoded for data tiles using `analysis/prep/tiles/encode_data_tiles.py`.
