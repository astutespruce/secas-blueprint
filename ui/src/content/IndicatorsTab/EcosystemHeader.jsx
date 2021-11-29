import React from 'react'
import PropTypes from 'prop-types'

import { Flex, Heading, Image } from 'theme-ui'

const EcosystemHeader = ({ id, label, color, borderColor }) => {
  // eslint-disable-next-line global-require, import/no-dynamic-require
  const icon = require(`images/${id}.svg`).default

  return (
    <Flex
      sx={{
        alignItems: 'center',
        justifyContent: 'space-between',
        bg: color,
        py: ['1rem', '0.5rem'],
        px: '1rem',
        borderBottom: '1px solid',
        borderBottomColor: borderColor,
      }}
    >
      <Flex sx={{ alignItems: 'center' }}>
        <Image
          src={icon}
          sx={{
            width: '2.5em',
            height: '2.5em',
            mr: '0.5em',
            bg: '#FFF',
            borderRadius: '2.5em',
          }}
        />

        <Heading as="h4">{label}</Heading>
      </Flex>
    </Flex>
  )
}

EcosystemHeader.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
  borderColor: PropTypes.string.isRequired,
}

export default EcosystemHeader
