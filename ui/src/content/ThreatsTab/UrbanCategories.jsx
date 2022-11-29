import React from 'react'
import PropTypes from 'prop-types'
import { Check } from '@emotion-icons/fa-solid'
import { Box, Flex, Text } from 'theme-ui'

const UrbanCategories = ({ categories, value: currentValue }) => (
  <Box sx={{ ml: '0.5rem', mt: '0.5rem' }}>
    {categories.map(({ value, label }) => (
      <Flex
        key={value}
        sx={{
          alignItems: 'baseline',
          justifyContent: 'space-between',
          pl: '0.5rem',
          borderBottom: '1px solid',
          borderBottomColor: 'grey.2',
          pb: '0.25rem',
          '&:not(:first-of-type)': {
            mt: '0.25rem',
          },
        }}
      >
        <Text
          sx={{
            flex: '1 1 auto',
            color: value === currentValue ? 'text' : 'grey.6',
            fontWeight: value === currentValue ? 'bold' : 'normal',
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
    ))}
  </Box>
)

UrbanCategories.propTypes = {
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
      description: PropTypes.string,
    })
  ).isRequired,
  value: PropTypes.number,
}

UrbanCategories.defaultProps = {
  value: null,
}

export default UrbanCategories
