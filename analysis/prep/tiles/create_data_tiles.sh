#!/bin/bash

# takes about 8 hours

../rastertiler-rs/target/release/rastertiler data/for_tiles/se_pixel_layers_0.tif tiles/se_pixel_layers_0.mbtiles -s 512 -Z 3 -z 14
../rastertiler-rs/target/release/rastertiler data/for_tiles/se_pixel_layers_1.tif tiles/se_pixel_layers_1.mbtiles -s 512 -Z 3 -z 14
../rastertiler-rs/target/release/rastertiler data/for_tiles/se_pixel_layers_2.tif tiles/se_pixel_layers_2.mbtiles -s 512 -Z 3 -z 14
../rastertiler-rs/target/release/rastertiler data/for_tiles/se_pixel_layers_3.tif tiles/se_pixel_layers_3.mbtiles -s 512 -Z 3 -z 14
../rastertiler-rs/target/release/rastertiler data/for_tiles/se_pixel_layers_4.tif tiles/se_pixel_layers_4.mbtiles -s 512 -Z 3 -z 14
../rastertiler-rs/target/release/rastertiler data/for_tiles/se_pixel_layers_5.tif tiles/se_pixel_layers_5.mbtiles -s 512 -Z 3 -z 14
