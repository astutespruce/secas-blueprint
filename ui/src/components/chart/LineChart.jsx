import React from 'react'

import ResponsiveChart from './ResponsiveChart'
import { Chart } from './line'

const LineChart = (props) => (
  <ResponsiveChart>
    <Chart {...props} />
  </ResponsiveChart>
)

export default LineChart
