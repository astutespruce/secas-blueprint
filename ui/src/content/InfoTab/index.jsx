import React from 'react'
import { Box, Divider } from 'theme-ui'

import Intro from './Intro'
import Blueprint from './Blueprint'
import Instructions from './Instructions'
import Credits from './Credits'

const InfoTab = () => {
  return (
    <Box sx={{ py: '1.5rem', pl: '1rem', pr: '2rem' }}>
      <Intro />
      <Divider />
      <Blueprint />
      <Divider />
      <Instructions />
      <Divider />
      <Credits />
    </Box>
  )
}

export default InfoTab
