import React from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Flex, Heading, Text } from 'theme-ui'
import { TimesCircle } from '@emotion-icons/fa-regular'

import { formatNumber } from 'util/format'

const SelectedUnitHeader = ({ name, acres, onClose }) => {
  return (
    <Flex
      sx={{
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        p: '1rem',
        minHeight: '7rem',
      }}
    >
      <Box sx={{ mr: '1rem' }}>
        <Heading as="h3">{name}</Heading>
        <Text sx={{ color: 'grey.7', fontSize: [0, 1] }}>
          {formatNumber(acres)} acres
        </Text>
      </Box>

      <Button
        variant="close"
        onClick={onClose}
        sx={{ flex: '0 0 auto', margin: 0, padding: 0 }}
      >
        <TimesCircle size="1.5em" />
      </Button>
    </Flex>
  )
}

SelectedUnitHeader.propTypes = {
  name: PropTypes.string.isRequired,
  acres: PropTypes.number.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default SelectedUnitHeader
