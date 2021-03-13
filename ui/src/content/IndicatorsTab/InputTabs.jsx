import React from 'react'
import PropTypes from 'prop-types'
import { Grid, Box, Text } from 'theme-ui'

import { formatPercent } from 'util/format'

const subTabCSS = {
  cursor: 'pointer',
  p: '0.5rem',
}

const inactiveSubTabCSS = {
  ...subTabCSS,
  '&:hover': {
    bg: 'grey.0',
  },
}

const activeSubTabCSS = {
  ...subTabCSS,
  color: 'accent',
}

const InputTabs = ({ inputs, selectedInput, onSelectInput }) => {
  const handleSelectInput = (id) => () => {
    if (id !== selectedInput) {
      onSelectInput(id)
    }
  }

  return (
    <Grid
      columns={inputs.length}
      gap={0}
      sx={{
        justifyContent: 'space-around',
        // py: '0.5rem',
        // px: '1rem',
        mb: '1rem',
        lineHeight: 1.2,
        textAlign: 'center',
      }}
    >
      {inputs.map(({ id, shortLabel, percent }, i) => (
        <React.Fragment key={id}>
          <Box
            sx={id === selectedInput ? activeSubTabCSS : inactiveSubTabCSS}
            onClick={handleSelectInput(id)}
          >
            <Text sx={{ fontWeight: 'bold' }}>{shortLabel}</Text>
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
    </Grid>
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
