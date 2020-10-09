# SECAS Southeast Conservation Blueprint Urban - Crucial Habitat Assessment Tool Data

2019 version.

Downloaded from: https://www.wafwachat.org/

Oklahoma and Texas were processed separate for SE Blueprint.  For analysis purposes,
these were split into 2 datasets.

The field "ls_cond" (landscape condition rank) is not present for either of these
states and was dropped.

The field "ls_corr" (landscape connectivity rank) is not present for TX and was dropped
from that state dataset.


All fields are ranks where 0 = NODATA and [1-6] are rank values from highest to lowest rank.



Data are processed using `analysis/prep/prepare_chat.py`.