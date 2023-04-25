import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import { Check } from '@emotion-icons/fa-solid'
import { Box, Flex, Text } from 'theme-ui'
import { lighten } from '@theme-ui/color'

import { IndicatorPropType } from './proptypes'

const IndicatorListItem = ({ indicator, onSelect }) => {
  const { label } = indicator

  const handleClick = useCallback(() => {
    onSelect(indicator)
  }, [indicator, onSelect])

  const present = indicator.total > 0

  if (!present) {
    return (
      <Flex
        sx={{
          alignItems: 'baseline',
          justifyContent: 'space-between',
          px: '1rem',
          py: '0.25rem',
          color: 'grey.8',
          cursor: 'default',
          '&:not(:first-of-type)': {
            borderTop: '2px solid',
            borderTopColor: 'grey.1',
          },
        }}
      >
        <Text
          sx={{
            flex: '1 1 auto',
            fontSize: 2,
          }}
        >
          {label}
        </Text>
      </Flex>
    )
  }

  return (
    <Flex
      onClick={handleClick}
      sx={{
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        cursor: 'pointer',
        color: 'primary',
        px: '1rem',
        py: '0.25rem',
        '&:hover': {
          bg: lighten('grey.0', 0.01),
          '& label': {
            display: 'block',
          },
        },
        '&:not(:first-of-type)': {
          borderTop: '2px solid',
          borderTopColor: 'grey.1',
        },
      }}
    >
      <Text
        sx={{
          fontSize: 2,
          mr: '0.5rem',
        }}
      >
        {label}
      </Text>
      <Box>
        <Check size="16px" />
      </Box>
    </Flex>
  )
}

IndicatorListItem.propTypes = {
  indicator: PropTypes.shape(IndicatorPropType).isRequired,
  onSelect: PropTypes.func.isRequired,
}

export default IndicatorListItem
