import React from 'react'
import { Box } from 'theme-ui'

import Intro from './Intro'
import Credits from './Credits'

const InfoTab = () => (
  <Box sx={{ py: '1.5rem', pl: '1rem', pr: '2rem' }}>
    <Intro />
    <Credits />
  </Box>
)

export default InfoTab
