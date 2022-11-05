import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { Flex, Box, Text } from 'theme-ui'

const LegendElement = ({
  label,
  shortLabel,
  type,
  color,
  outlineColor,
  outlineWidth,
}) => (
  <Flex
    sx={{
      alignItems: 'center',
      lineHeight: 1,
    }}
  >
    {type === 'fill' && (
      <Box
        sx={{
          flex: '0 0 auto',
          width: '1.25em',
          height: '1em',
          borderRadius: '0.25em',
          mr: '0.25rem',
          // set transparency to match map
          bg: `${color}b3`,
          border: outlineWidth !== 0 ? `${outlineWidth}px solid` : 'none',
          borderColor: outlineColor,
        }}
      />
    )}
    <Text>{shortLabel || label}</Text>
  </Flex>
)

LegendElement.propTypes = {
  label: PropTypes.string.isRequired,
  shortLabel: PropTypes.string,
  type: PropTypes.string,
  color: PropTypes.oneOfType([PropTypes.string, PropTypes.func]).isRequired,
  outlineColor: PropTypes.oneOfType([PropTypes.string, PropTypes.func]),
  outlineWidth: PropTypes.number,
}

LegendElement.defaultProps = {
  shortLabel: null,
  type: 'fill',
  outlineColor: null,
  outlineWidth: 0,
}

export default memo(LegendElement, () => true)
