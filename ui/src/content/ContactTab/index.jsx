import React from 'react'
import { Box, Heading, Divider } from 'theme-ui'

import Feedback from './Feedback'
import Contact from './Contact'

export { Feedback, Contact }

const index = () => (
  <Box sx={{ py: '1.5rem', pl: '1rem', pr: '2rem' }}>
    <Box as="section">
      <Heading as="h3" sx={{ mb: '0.5rem' }}>
        Give your feedback to Blueprint staff
      </Heading>
      <Feedback />
    </Box>

    <Divider />

    <Box as="section">
      <Heading as="h3" sx={{ mb: '0.5rem' }}>
        Contact Blueprint staff for help using the Blueprint
      </Heading>
      <Contact />
    </Box>
  </Box>
)

export default index
