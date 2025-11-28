#!/bin/bash

mkdir -p tiles/tmp

function rastertiler () {
    ./../rastertiler-rs/target/release/rastertiler "$@"
}

echo "Rendering Blueprint tiles"
rastertiler render data/inputs/blueprint.tif tiles/tmp/blueprint_z3_6.mbtiles -s 512 -n blueprint --colormap "1:#6C6C6C,2:#8C96C6,3:#843F98,4:#4D004B" -Z 3 -z 6
rastertiler render data/inputs/blueprint.tif tiles/tmp/blueprint_z7_14.mbtiles -s 512 -n blueprint --colormap "1:#6C6C6C,2:#8C96C6,3:#843F98,4:#4D004B" -Z 7 -z 14 --disable-overviews
rastertiler merge tiles/tmp/blueprint_z3_6.mbtiles tiles/tmp/blueprint_z7_14.mbtiles tiles/blueprint.mbtiles


# IMPORTANT: all the data tiles need to be rendered without overviews, which cause significant distortion (even at very low overview factors like 2)

echo "Rendering pixel layer 0"
rastertiler render data/for_tiles/se_pixel_layers_0.tif tiles/se_pixel_layers_0.mbtiles -s 512 -n se_pixel_layers_0 -Z 3 -z 14 --disable-overviews

echo "Rendering pixel layer 1"
rastertiler render data/for_tiles/se_pixel_layers_1.tif tiles/se_pixel_layers_1.mbtiles -s 512 -n se_pixel_layers_1 -Z 3 -z 14 --disable-overviews

echo "Rendering pixel layer 2"
rastertiler render data/for_tiles/se_pixel_layers_2.tif tiles/se_pixel_layers_2.mbtiles -s 512 -n se_pixel_layers_2 -Z 3 -z 14 --disable-overviews

echo "Rendering pixel layer 3"
rastertiler render data/for_tiles/se_pixel_layers_3.tif tiles/se_pixel_layers_3.mbtiles -s 512 -n se_pixel_layers_3 -Z 3 -z 14 --disable-overviews

echo "Rendering pixel layer 4"
rastertiler render data/for_tiles/se_pixel_layers_4.tif tiles/se_pixel_layers_4.mbtiles -s 512 -n se_pixel_layers_4 -Z 3 -z 14 --disable-overviews

echo "Rendering pixel layer 5"
rastertiler render data/for_tiles/se_pixel_layers_5.tif tiles/se_pixel_layers_5.mbtiles -s 512 -n se_pixel_layers_5 -Z 3 -z 14 --disable-overviews

echo "Rendering pixel layer 6"
rastertiler render data/for_tiles/se_pixel_layers_6.tif tiles/se_pixel_layers_6.mbtiles -s 512 -n se_pixel_layers_6 -Z 3 -z 14 --disable-overviews

echo "Rendering pixel layer 7"
rastertiler render data/for_tiles/se_pixel_layers_7.tif tiles/se_pixel_layers_7.mbtiles -s 512 -n se_pixel_layers_7 -Z 3 -z 14 --disable-overviews

echo "Rendering pixel layer 8"
rastertiler render data/for_tiles/se_pixel_layers_8.tif tiles/se_pixel_layers_8.mbtiles -s 512 -n se_pixel_layers_8 -Z 3 -z 14 --disable-overviews

echo "Rendering pixel layer 9"
rastertiler render data/for_tiles/se_pixel_layers_9.tif tiles/se_pixel_layers_9.mbtiles -s 512 -n se_pixel_layers_9 -Z 3 -z 14 --disable-overviews
