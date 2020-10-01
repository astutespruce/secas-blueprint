import React from 'react'

import ResponsiveChart from './ResponsiveChart'
import { Chart } from './line'

const LineChart = (props) => {
  return (
    <ResponsiveChart>
      <Chart {...props} />
    </ResponsiveChart>
  )
}

export default LineChart
