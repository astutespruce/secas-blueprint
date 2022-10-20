import React from 'react'
import { Box, Flex } from 'theme-ui'
import { darken } from '@theme-ui/color'
import { FileAlt } from '@emotion-icons/fa-regular'

import { Link } from 'components/link'

const HeaderButtons = () => (
  <Flex sx={{ alignItems: 'center', flex: '0 0 auto' }}>
    <Box sx={{ ml: '1rem' }}>
      <Link tabIndex="0" to="/custom_report">
        <Box
          sx={{
            fontWeight: 700,
            fontSize: 1,
            color: '#FFF',
            display: 'flex',
            alignItems: 'center',
            cursor: 'pointer',
            border: '1px solid #FFF',
            borderRadius: '0.25rem',
            p: '0.25em 0.5em',
            '&:hover': {
              bg: darken('primary', 0.1),
            },
          }}
        >
          <FileAlt size="1em" />
          <Box
            sx={{ marginLeft: '0.5rem', display: ['none', 'none', 'block'] }}
          >
            Upload Shapefile
          </Box>
        </Box>
      </Link>
    </Box>
  </Flex>
)

export default HeaderButtons
