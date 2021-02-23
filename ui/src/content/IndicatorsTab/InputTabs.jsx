import React from 'react'
import PropTypes from 'prop-types'
import { Flex, Box, Text } from 'theme-ui'

import { formatPercent } from 'util/format'

const subTabCSS = {
  cursor: 'pointer',
  fontWeight: 'bold',
  '&:hover': {
    textDecoration: 'underline',
  },
}

const activeSubTabCSS = {
  fontWeight: 'bold',
  color: 'accent',
}

const InputTabs = ({ inputs, selectedInput, onSelectInput }) => {
  const handleSelectInput = (id) => () => {
    if (id !== selectedInput) {
      onSelectInput(id)
    }
  }

  return (
    <Flex
      sx={{
        justifyContent: 'space-around',
        py: '0.5rem',
        px: '1rem',
        mb: '1rem',
      }}
    >
      {inputs.map(({ id, shortLabel, percent }, i) => (
        <React.Fragment key={id}>
          {i > 0 ? <Text sx={{ color: 'grey.3' }}>&nbsp;|&nbsp;</Text> : null}
          <Box sx={{ lineHeight: 1.2, textAlign: 'center' }}>
            <Text
              sx={id === selectedInput ? activeSubTabCSS : subTabCSS}
              onClick={handleSelectInput(id)}
            >
              {shortLabel}
            </Text>
            <Text
              sx={{
                fontSize: '0.8rem',
                color: 'grey.8',
              }}
            >
              ({formatPercent(percent)}% of area)
            </Text>
          </Box>
        </React.Fragment>
      ))}
    </Flex>
  )
}

InputTabs.propTypes = {
  inputs: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      shortLabel: PropTypes.string.isRequired,
      percent: PropTypes.number,
    })
  ).isRequired,
  selectedInput: PropTypes.string.isRequired,
  onSelectInput: PropTypes.func.isRequired,
}

export default InputTabs
