import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

const PseudoLink = ({ onClick, children, sx }) => (
  <Text
    sx={{
      ...sx,
      cursor: 'pointer',
      color: 'link',
      '&:hover': {
        textDecoration: 'underline',
      },
    }}
    onClick={onClick}
  >
    {children}
  </Text>
)

PseudoLink.propTypes = {
  children: PropTypes.node.isRequired,
  onClick: PropTypes.func.isRequired,
  sx: PropTypes.object,
}

PseudoLink.defaultProps = {
  sx: {},
}

export default PseudoLink
