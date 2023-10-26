#!/bin/bash

mkdir -p tiles/tmp

function rastertiler () {
    ./../rastertiler-rs/target/release/rastertiler "$@"
}

echo "Rendering Blueprint tiles"
rastertiler render data/inputs/blueprint.tif tiles/tmp/blueprint_z2_7.mbtiles -s 512 -n blueprint --colormap "1:#6C6C6C,2:#8C96C6,3:#843F98,4:#4D004B" -Z 2 -z 7
rastertiler render data/inputs/blueprint.tif tiles/tmp/blueprint_z8_14.mbtiles -s 512 -n blueprint --colormap "1:#6C6C6C,2:#8C96C6,3:#843F98,4:#4D004B" -Z 8 -z 14 --disable-overviews
rastertiler merge tiles/tmp/blueprint_z2_7.mbtiles tiles/tmp/blueprint_z8_14.mbtiles tiles/blueprint.mbtiles

echo "Rendering pixel layer 0"
rastertiler render data/for_tiles/se_pixel_layers_0.tif tiles/tmp/se_pixel_layers_0_z2_7.mbtiles -s 512 -n se_pixel_layers_0 -Z 2 -z 7
rastertiler render data/for_tiles/se_pixel_layers_0.tif tiles/tmp/se_pixel_layers_0_z8_14.mbtiles -s 512 -n se_pixel_layers_0 -Z 8 -z 14 --disable-overviews
rastertiler merge tiles/tmp/se_pixel_layers_0_z2_7.mbtiles tiles/tmp/se_pixel_layers_0_z8_14.mbtiles tiles/se_pixel_layers_0.mbtiles

echo "Rendering pixel layer 1"
rastertiler render data/for_tiles/se_pixel_layers_1.tif tiles/tmp/se_pixel_layers_1_z2_7.mbtiles -s 512 -n se_pixel_layers_1 -Z 2 -z 7
rastertiler render data/for_tiles/se_pixel_layers_1.tif tiles/tmp/se_pixel_layers_1_z8_14.mbtiles -s 512 -n se_pixel_layers_1 -Z 8 -z 14 --disable-overviews
rastertiler merge tiles/tmp/se_pixel_layers_1_z2_7.mbtiles tiles/tmp/se_pixel_layers_1_z8_14.mbtiles tiles/se_pixel_layers_1.mbtiles

echo "Rendering pixel layer 2"
rastertiler render data/for_tiles/se_pixel_layers_2.tif tiles/tmp/se_pixel_layers_2_z2_7.mbtiles -s 512 -n se_pixel_layers_2 -Z 2 -z 7
rastertiler render data/for_tiles/se_pixel_layers_2.tif tiles/tmp/se_pixel_layers_2_z8_14.mbtiles -s 512 -n se_pixel_layers_2 -Z 8 -z 14 --disable-overviews
rastertiler merge tiles/tmp/se_pixel_layers_2_z2_7.mbtiles tiles/tmp/se_pixel_layers_2_z8_14.mbtiles tiles/se_pixel_layers_2.mbtiles

echo "Rendering pixel layer 3"
rastertiler render data/for_tiles/se_pixel_layers_3.tif tiles/tmp/se_pixel_layers_3_z2_7.mbtiles -s 512 -n se_pixel_layers_3 -Z 2 -z 7
rastertiler render data/for_tiles/se_pixel_layers_3.tif tiles/tmp/se_pixel_layers_3_z8_14.mbtiles -s 512 -n se_pixel_layers_3 -Z 8 -z 14 --disable-overviews
rastertiler merge tiles/tmp/se_pixel_layers_3_z2_7.mbtiles tiles/tmp/se_pixel_layers_3_z8_14.mbtiles tiles/se_pixel_layers_3.mbtiles

echo "Rendering pixel layer 4"
rastertiler render data/for_tiles/se_pixel_layers_4.tif tiles/tmp/se_pixel_layers_4_z2_7.mbtiles -s 512 -n se_pixel_layers_4 -Z 2 -z 7
rastertiler render data/for_tiles/se_pixel_layers_4.tif tiles/tmp/se_pixel_layers_4_z8_14.mbtiles -s 512 -n se_pixel_layers_4 -Z 8 -z 14 --disable-overviews
rastertiler merge tiles/tmp/se_pixel_layers_4_z2_7.mbtiles tiles/tmp/se_pixel_layers_4_z8_14.mbtiles tiles/se_pixel_layers_4.mbtiles

echo "Rendering pixel layer 5"
rastertiler render data/for_tiles/se_pixel_layers_5.tif tiles/tmp/se_pixel_layers_5_z2_7.mbtiles -s 512 -n se_pixel_layers_5 -Z 2 -z 7
rastertiler render data/for_tiles/se_pixel_layers_5.tif tiles/tmp/se_pixel_layers_5_z8_14.mbtiles -s 512 -n se_pixel_layers_5 -Z 8 -z 14 --disable-overviews
rastertiler merge tiles/tmp/se_pixel_layers_5_z2_7.mbtiles tiles/tmp/se_pixel_layers_5_z8_14.mbtiles tiles/se_pixel_layers_5.mbtiles

echo "Rendering pixel layer 6"
rastertiler render data/for_tiles/se_pixel_layers_6.tif tiles/tmp/se_pixel_layers_6_z2_7.mbtiles -s 512 -n se_pixel_layers_6 -Z 2 -z 7
rastertiler render data/for_tiles/se_pixel_layers_6.tif tiles/tmp/se_pixel_layers_6_z8_14.mbtiles -s 512 -n se_pixel_layers_6 -Z 8 -z 14 --disable-overviews
rastertiler merge tiles/tmp/se_pixel_layers_6_z2_7.mbtiles tiles/tmp/se_pixel_layers_6_z8_14.mbtiles tiles/se_pixel_layers_6.mbtiles

echo "Rendering pixel layer 7"
rastertiler render data/for_tiles/se_pixel_layers_7.tif tiles/tmp/se_pixel_layers_7_z2_7.mbtiles -s 512 -n se_pixel_layers_7 -Z 2 -z 7
rastertiler render data/for_tiles/se_pixel_layers_7.tif tiles/tmp/se_pixel_layers_7_z8_14.mbtiles -s 512 -n se_pixel_layers_7 -Z 8 -z 14 --disable-overviews
rastertiler merge tiles/tmp/se_pixel_layers_7_z2_7.mbtiles tiles/tmp/se_pixel_layers_7_z8_14.mbtiles tiles/se_pixel_layers_7.mbtiles

echo "Rendering pixel layer 8"
rastertiler render data/for_tiles/se_pixel_layers_8.tif tiles/tmp/se_pixel_layers_8_z2_7.mbtiles -s 512 -n se_pixel_layers_8 -Z 2 -z 7
rastertiler render data/for_tiles/se_pixel_layers_8.tif tiles/tmp/se_pixel_layers_8_z8_14.mbtiles -s 512 -n se_pixel_layers_8 -Z 8 -z 14 --disable-overviews
rastertiler merge tiles/tmp/se_pixel_layers_8_z2_7.mbtiles tiles/tmp/se_pixel_layers_8_z8_14.mbtiles tiles/se_pixel_layers_8.mbtiles
