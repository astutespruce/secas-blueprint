import React from 'react'
import { Box, Text } from 'theme-ui'
import { QuestionCircle } from '@emotion-icons/fa-regular'

import { ContactModal } from 'components/modal'

const NeedHelp = () => (
  <Box
    sx={{
      color: 'grey.9',
      fontSize: 1,
      mt: '2rem',
      pt: '2rem',
      borderTop: '1px solid',
      borderTopColor: 'grey.2',
    }}
  >
    <QuestionCircle
      size="1.25em"
      style={{ marginTop: '-0.25em', marginRight: '0.5em' }}
    />
    Need help interpreting these results or applying Blueprint priorities to
    your particular project or location? Please{' '}
    <Box as="span" sx={{ display: 'inline-block' }}>
      <ContactModal>
        <Text
          sx={{
            color: 'primary',
            cursor: 'pointer',
            '&:hover': { textDecoration: 'underline' },
          }}
        >
          Contact Us
        </Text>
      </ContactModal>
    </Box>
    . We are here to help you!
  </Box>
)

export default NeedHelp
