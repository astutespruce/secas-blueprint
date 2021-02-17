import React, { memo } from 'react'
import { Box, Heading } from 'theme-ui'

import { Search } from 'components/search'

const FindLocationTab = () => (
  <Box as="section" sx={{ py: '1.5rem' }}>
    <Heading as="h3" sx={{ mb: '0.5rem', pl: '1rem', pr: '2rem' }}>
      Find a location on the map
    </Heading>
    <Search />
  </Box>
)

export default memo(FindLocationTab)
