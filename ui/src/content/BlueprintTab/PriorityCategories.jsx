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

const PriorityCategories = ({ categories, value: currentValue }) => (
  <Box sx={{ fontSize: 1, pt: '0.5rem' }}>
    {categories.map(({ value, percent, label, color, description }) => (
      <Box key={value} sx={value === currentValue ? activeCSS : defaultCSS}>
        <Flex
          sx={{ justifyContent: 'space-between', alignItems: 'flex-start' }}
        >
          <Box
            sx={{
              bg: color,
              width: '1rem',
              height: '2rem',
              border: '1px solid #CCC',
              borderRadius: '0.25em',
              mr: '0.5rem',
              flex: '0 0 auto',
            }}
          />

          <Box sx={{ flex: '1 1 auto' }}>
            <Box
              sx={{
                fontWeight: 'bold',
                lineHeight: 1,
              }}
            >
              {label}
            </Box>
            <Text sx={{ fontSize: 0 }}>
              {description} This class covers {percent}% of the Southeast
              Blueprint geography.
            </Text>
          </Box>
          {value === currentValue ? (
            <Box sx={{ flex: '0 0 auto' }}>
              <Check size="1em" />
            </Box>
          ) : null}
        </Flex>
      </Box>
    ))}
  </Box>
)

PriorityCategories.propTypes = {
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
      color: PropTypes.string.isRequired,
      percent: PropTypes.number.isRequired,
      description: PropTypes.string,
    })
  ).isRequired,
  value: PropTypes.number,
}

PriorityCategories.defaultProps = {
  value: null,
}

export default PriorityCategories
