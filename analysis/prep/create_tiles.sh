#!/bin/bash

TMPDIR="/tmp"
TILEDIR="tiles"
TILEINPUTS="data/for_tiles"


# Create tiles from states
echo "Processing states..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq -select STATEFP $TMPDIR/states.geojson source_data/boundaries/tl_2019_us_state.shp
tippecanoe -f -P -pg -Z 0 -z 5 -o $TILEDIR/states.mbtiles -l states /tmp/states.geojson


# Create tiles from protected areas
echo "Processing protected areas..."
tippecanoe -f -pg -P -z 15 -o $TILEDIR/se_ownership.mbtiles -l "ownership" $TILEINPUTS/ownership.geojson


# Create tiles for Caribbean priority watersheds
echo "Processing Caribbean..."
tippecanoe -f -pg -P -Z 4 -z 9 --detect-shared-borders -o $TILEDIR/caribbean.mbtiles -l caribbean $TILEINPUTS/caribbean.geojson


# Create tiles for CHAT ranks
echo "Processing CHAT..."
tippecanoe -f -pg -P -Z 7 -z 9 --detect-shared-borders -o $TMPDIR/okchat.mbtiles -l okchat $TILEINPUTS/okchat.geojson
tippecanoe -f -pg -P -Z 7 -z 9 --detect-shared-borders -o $TMPDIR/txchat.mbtiles -l txchat $TILEINPUTS/txchat.geojson
tile-join -f -pg -o $TILEDIR/chat.mbtiles $TMPDIR/okchat.mbtiles $TMPDIR/txchat.mbtiles


# Create tiles from boundary and mask
echo "Processing boundary..."
tippecanoe -f -pg -P -Z 0 -z 8 -ai -o $TMPDIR/se_mask.mbtiles -l "mask" $TILEINPUTS/se_mask.geojson
tippecanoe -f -pg -P -Z 0 -z 8 -ai -o $TMPDIR/se_boundary.mbtiles -l "boundary" $TILEINPUTS/se_boundary.geojson


# Create tiles from summary units
echo "Processing summary units..."
tippecanoe -f -pg -P -Z 8 -z 14 -ai --detect-shared-borders -o $TMPDIR/units.mbtiles -l "units" $TILEINPUTS/units.geojson

# Merge in attributes
echo "Merging attributes with tiles..."
tile-join -f -pg -o $TMPDIR/unit_atts.mbtiles $TMPDIR/units.mbtiles -c $TILEINPUTS/unit_atts.csv

# Join units and boundaries together
echo "Merging tilesets..."
tile-join -f -pg -o $TILEDIR/se_map_units.mbtiles $TMPDIR/se_mask.mbtiles $TMPDIR/se_boundary.mbtiles $TMPDIR/unit_atts.mbtiles


