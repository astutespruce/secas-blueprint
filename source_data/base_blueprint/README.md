# SECAS Southeast Conservation Blueprint

## SECAS Base Blueprint

The SECAS Base Blueprint was downloaded 10/6/2022 from https://www.sciencebase.gov/catalog/file/get/62d57290d34e87fffb2dda52?name=Southeast_Blueprint_2022_Data_Download.zip

The extent raster that is used as the master grid to align all other rasters
is `BaseBlueprintExtent2022.tif`.

The data extent of this raster is extracted and used to clip / align all other
inputs.

NOTE: this is the Base Blueprint, which is areas that used the same methods
and stack of indicators. The actual SE Blueprint extent is larger.

## SECAS Subregions

Subregions are contained in a shapefile: BaseBlueprintSubRgn.shp

A non-marine mask was extracted by excluding the two marine subregions and then
rasterizing the remaining subregions to align with the Base Blueprint extent..
