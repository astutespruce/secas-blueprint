import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Heading, Image, Text } from 'theme-ui'

const FilterGroupHeader = ({ id, filterCount, label, color, borderColor }) => {
  // eslint-disable-next-line global-require, import/no-dynamic-require
  const icon = require(`images/${id}.svg`).default

  return (
    <Box
      sx={{
        bg: color,
        py: ['1rem', '0.5rem'],
        px: '1rem',
        borderBottom: '1px solid',
        borderBottomColor: borderColor,
      }}
    >
      <Flex sx={{ alignItems: 'center', justifyContent: 'space-between' }}>
        <Flex sx={{ alignItems: 'center' }}>
          <Image
            src={icon}
            alt=""
            sx={{
              width: '2em',
              height: '2em',
              mr: '0.5em',
              bg: '#FFF',
              borderRadius: '2.5em',
            }}
          />

          <Heading as="h4">{label}</Heading>
        </Flex>
        {filterCount > 0 ? (
          <Text sx={{ fontSize: 0 }}>
            {filterCount} {filterCount === 1 ? 'filter' : 'filters'}
          </Text>
        ) : null}
      </Flex>
    </Box>
  )
}

FilterGroupHeader.propTypes = {
  id: PropTypes.string.isRequired,
  filterCount: PropTypes.number,
  label: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
  borderColor: PropTypes.string.isRequired,
}

FilterGroupHeader.defaultProps = {
  filterCount: 0,
}

export default FilterGroupHeader
