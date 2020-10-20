cimport cython
cimport numpy as np
import numpy as np
from libc.stdio cimport *


from libc.stdint cimport (
  uint8_t, uint16_t, uint32_t, uint64_t,
  int8_t, int16_t, int32_t, int64_t
)

ctypedef fused INTEGER:
  uint8_t
  uint16_t
  uint32_t
  uint64_t
  int8_t
  int16_t
  int32_t
  int64_t


# Inspired by https://github.com/seung-lab/fastremap/blob/master/fastremap.pyx
@cython.boundscheck(False)
@cython.wraparound(False)
# @cython.nonecheck(False)
def remap(INTEGER[:,:] arr, remap_table, int nodata, int fill=0):

    if nodata is None:
        raise ValueError("nodata value must be set")


    cdef int i = 0, j=0
    cdef int rows = arr.shape[0]
    cdef int cols = arr.shape[1]

    # convert potentially sparse table to full for constant
    # time lookups
    cdef int max_value = np.max(remap_table[:,0])
    cdef table = np.ones(shape=(max_value + 1,), dtype=remap_table.dtype) * fill
    for i in range(len(remap_table)):
        if remap_table[i][0] < 0:
            raise ValueError("Remapping negative values not supported")

        table[remap_table[i][0]] = remap_table[i][1]

    cdef INTEGER[:] table_view = table

    cdef out = np.ones_like(arr) * fill
    cdef INTEGER[:,:] out_view = out
    cdef INTEGER value
    cdef INTEGER fill_value = fill
    cdef INTEGER nodata_value = nodata

    with nogil:
        for i in range(rows):
            for j in range(cols):
                value = arr[i,j]
                if value == nodata:
                    out_value = nodata
                elif value > max_value:
                    out_value = fill
                else:
                    out_value = table_view[value]

                out_view[i,j] = out_value

    return out