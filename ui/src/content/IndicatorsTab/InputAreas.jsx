import React from 'react'
import PropTypes from 'prop-types'
import { Text, Box, Flex } from 'theme-ui'

import { formatPercent } from 'util/format'

import Ecosystem from './Ecosystem'

const InputAreas = ({ type, inputs, onSelectIndicator }) => {
  if (inputs.length === 0) {
    return (
      <Text sx={{ color: 'grey.8', textAlign: 'center' }}>
        No input areas present.
      </Text>
    )
  }

  return (
    <>
      {inputs.map(({ id, version, label, percent, ecosystems }) => (
        <Box
          key={id}
          sx={{
            '&:not(:first-of-type)': {
              mt: '1rem',
              pt: '1rem',
            },
          }}
        >
          <Flex
            sx={{
              justifyContent: 'space-between',
              alignItems: 'baseline',
              width: '100%',
              p: '1rem',
            }}
          >
            <Text
              sx={{
                flex: '1 1 auto',
                fontWeight: 'bold',
                fontSize: 3,
                lineHeight: 1.2,
                mr: '1rem',
              }}
            >
              {label} {version && version}
            </Text>
            <Text
              sx={{
                flex: '0 0 auto',
                fontSize: 0,
                color: 'grey.7',
                textAlign: 'right',
                lineHeight: 1,
              }}
            >
              {formatPercent(percent)}% of area
            </Text>
          </Flex>

          {/* <Flex
            sx={{
              justifyContent: 'space-around',
              py: '0.5rem',
              px: '1rem',
              mb: '1rem',
            }}
          >
            <Text sx={{ color: 'accent', fontWeight: 'bold' }}>
              South Atlantic
            </Text>
            <Text sx={{ color: 'grey.3' }}>&nbsp;|&nbsp;</Text>
            <Text>Middle Southeast</Text>
            <Text sx={{ color: 'grey.3' }}>&nbsp;|&nbsp;</Text>
            <Text>Florida</Text>
          </Flex> */}

          {ecosystems.map((ecosystem) => (
            <Ecosystem
              key={ecosystem.id}
              type={type}
              onSelectIndicator={onSelectIndicator}
              {...ecosystem}
            />
          ))}
        </Box>
      ))}
    </>
  )
}

InputAreas.propTypes = {
  type: PropTypes.string.isRequired,
  inputs: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      percent: PropTypes.number.isRequired,
    })
  ),
  onSelectIndicator: PropTypes.func.isRequired,
}

InputAreas.defaultProps = {
  inputs: [],
}

export default InputAreas
