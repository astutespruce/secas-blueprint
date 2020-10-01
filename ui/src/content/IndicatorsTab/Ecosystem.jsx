import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import EcosystemHeader from './EcosystemHeader'
import Indicator from './Indicator'
import { EcosystemPropType } from './proptypes'

const Ecosystem = ({
  id,
  label,
  color,
  borderColor,
  indicators,
  onSelectIndicator,
}) => {
  return (
    <Box
      sx={{
        width: '100%',
        flex: '1 0 auto',
        '&:not(:first-of-type)': {
          //   mt: "2rem",
          '&>div:first-of-type': {
            borderTop: '1px solid',
            borderTopColor: borderColor,
          },
        },
      }}
    >
      <EcosystemHeader
        id={id}
        label={label}
        color={color}
        borderColor={borderColor}
      />

      <Box>
        {indicators.map((indicator) => (
          <Indicator
            key={indicator.id}
            indicator={indicator}
            onSelect={onSelectIndicator}
          />
        ))}
      </Box>
    </Box>
  )
}

Ecosystem.propTypes = {
  ...EcosystemPropType,
  onSelectIndicator: PropTypes.func.isRequired,
}

export default Ecosystem
