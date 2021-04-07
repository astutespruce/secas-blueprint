import React from 'react'
import { Box, Divider } from 'theme-ui'

import Intro from './Intro'
import Instructions from './Instructions'
import Credits from './Credits'

const InfoTab = () => (
  <Box sx={{ py: '1.5rem', pl: '1rem', pr: '2rem' }}>
    <Intro />
    <Divider />
    <Instructions />
    <Divider />
    <Credits />
  </Box>
)

export default InfoTab
