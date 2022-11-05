import React from 'react'
import PropTypes from 'prop-types'
import { Check } from '@emotion-icons/fa-solid'
import { Box, Flex, Text } from 'theme-ui'

const defaultCSS = {
  color: 'grey.8',
  border: '1px solid transparent',
  py: '0.5rem',
  px: '1rem',
}

const activeCSS = {
  ...defaultCSS,
  borderRadius: '0.5rem',
  bg: '#FFF',
  borderColor: 'grey.2',
  boxShadow: '1px 1px 6px #dce2e3',
  color: 'text',
}

const CorridorCategories = ({ categories, value: currentValue }) => (
  <Box sx={{ fontSize: 1, pt: '0.5rem' }}>
    {categories.map(({ value, label, description }) => (
      <Box key={value} sx={value === currentValue ? activeCSS : defaultCSS}>
        <Flex
          sx={{ justifyContent: 'space-between', alignItems: 'flex-start' }}
        >
          <Text
            sx={{
              fontWeight: 'bold',
              flex: '1 1 auto',
            }}
          >
            {label}
          </Text>
          {value === currentValue ? (
            <Box sx={{ flex: '0 0 auto' }}>
              <Check size="1em" />
            </Box>
          ) : null}
        </Flex>
        {description ? <Text sx={{ fontSize: 0 }}>{description}</Text> : null}
      </Box>
    ))}
  </Box>
)

CorridorCategories.propTypes = {
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
      description: PropTypes.string,
    })
  ).isRequired,
  value: PropTypes.number,
}

CorridorCategories.defaultProps = {
  value: null,
}

export default CorridorCategories
