# SECAS Southeast Conservation Blueprint Inputs - Appalachian NatureScape

The AppLCC NatureScape dataset was combined with the TNC Resilience dataset

Downloaded 10/14/2020 from USFWS staff MS Teams site.

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
