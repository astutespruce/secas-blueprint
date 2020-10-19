# SECAS Southeast Conservation Blueprint Inputs - Appalachian NatureScape & TNC Resilient and Connected Landscapes

The AppLCC NatureScape dataset was combined with the TNC Resilience dataset

AppLCC NatureScape downloaded 10/14/2020 from USFWS staff MS Teams site.
USFWS staff provided a GeoTIFF version of the TNC resilience dataset on 10/19/2020.

This dataset may be available from:
TNC Resilience downloaded 10/19/2020 from: https://www.conservationgateway.org/ConservationPractices/ClimateChange/Pages/RCN-Downloads.aspx
(it is HUGE - >90GB, did not compare).

Processed using `analysis/prep/prepare_naturescape.py`.

## Priority Categories:

The following 4 bins were used to summarize these datasets for top-level Blueprint input areas.

### High Conservation Value

1. NatureScape: Local Cores, Regional Cores, Other Important Areas
2. TNC Prioritized Network: Resilient Only with Secured Lands (value 33), Resilient Area with Confirmed Diversity (value 12)

### Medium Conservation Value

Pixels that were not classified as High in the mapping steps above were classified as Medium if they fell in the following areas:

3. NatureScape: Local Connectors, Regional Connectors
4. TNC Prioritized Network: Climate Corridor (value 2, 4 and 13), Climate Corridor with Confirmed Diversity (value 11), Climate Flow Zone (value 14) and Climate Flow Zone with Confirmed Diversity (value 112)

## TODO:

use individual categories as indicators

### Possible indicator datasets

https://nalcc.databasin.org/datasets/5d4512416b864ee88da9ed591ee7daea
https://www.conservationgateway.org/ConservationPractices/ClimateChange/Pages/RCN-Downloads.aspx
