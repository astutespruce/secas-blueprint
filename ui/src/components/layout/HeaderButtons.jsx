import React from 'react'
import { Box, Flex } from 'theme-ui'
import { darken } from '@theme-ui/color'
import { FileAlt } from '@emotion-icons/fa-regular'
import { QuestionCircle } from '@emotion-icons/fa-solid'
import { withPrefix } from 'gatsby'

import { Link } from 'components/link'

const HeaderButtons = () => (
  <Flex
    sx={{
      alignItems: 'center',
      flex: '0 0 auto',
      gap: '1rem',
      ml: '1rem',
      'a:hover': {
        textDecoration: 'none',
      },
    }}
  >
    <Box>
      <a href={withPrefix('/help')} target="_blank" rel="noopener noreferrer">
        <Flex
          sx={{
            fontWeight: 700,
            fontSize: 1,
            color: '#FFF',
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
          <QuestionCircle size="1em" />
          <Box
            sx={{ marginLeft: '0.5rem', display: ['none', 'none', 'block'] }}
          >
            How to use this viewer
          </Box>
        </Flex>
      </a>
    </Box>

    <Box>
      <Link to="/custom_report">
        <Flex
          sx={{
            fontWeight: 700,
            fontSize: 1,
            color: '#FFF',
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
            Upload a shapefile
          </Box>
        </Flex>
      </Link>
    </Box>
  </Flex>
)

export default HeaderButtons
