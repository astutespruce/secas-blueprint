import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import EcosystemHeader from './EcosystemHeader'
import Indicator from './Indicator'
import { EcosystemPropType } from './proptypes'

const Ecosystem = ({
  type,
  id,
  label,
  color,
  borderColor,
  indicators,
  onSelectIndicator,
}) => (
  <Box
    sx={{
      width: '100%',
      flex: '1 0 auto',
      '&:not(:first-of-type)': {
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
          type={type}
          indicator={indicator}
          onSelect={onSelectIndicator}
        />
      ))}
    </Box>
  </Box>
)

Ecosystem.propTypes = {
  type: PropTypes.string.isRequired,
  ...EcosystemPropType,
  onSelectIndicator: PropTypes.func.isRequired,
}

export default Ecosystem
