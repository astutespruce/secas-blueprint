import React, { memo, useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import { Eye, EyeSlash } from '@emotion-icons/fa-solid'
import { Box, Flex, Text } from 'theme-ui'

import { useBlueprintPriorities } from 'components/data'
import LegendElement from './LegendElement'

const Legend = ({ isVisible, onToggleVisibility }) => {
  const [isOpen, setIsOpen] = useState(true)

  const handleClick = useCallback(() => {
    setIsOpen((prevIsOpen) => !prevIsOpen)
  }, [])

  const handleToggleVisibility = useCallback(
    (e) => {
      onToggleVisibility()
      e.stopPropagation()
      e.nativeEvent.stopImmediatePropagation()
    },
    [onToggleVisibility]
  )

  const { categories } = useBlueprintPriorities()

  return (
    <Box
      sx={{
        position: 'absolute',
        color: 'grey.9',
        bg: '#FFF',
        pointerEvents: 'auto',
        cursor: 'pointer',
        bottom: ['40px', '40px', '40px', '24px'],
        right: '10px',
        borderRadius: '0.25rem',
        boxShadow: '2px 2px 6px #333',
        maxWidth: '200px',
      }}
      onClick={handleClick}
    >
      {isOpen ? (
        <Box
          sx={{
            p: '0.5rem',
          }}
          title="Click to hide legend"
        >
          <Flex
            sx={{ justifyContent: 'space-between', alignItems: 'flex-start' }}
          >
            <Text
              sx={{
                flex: '1 1 auto',
                fontWeight: 'bold',
                mr: '0.5em',
                fontSize: 1,
              }}
            >
              Blueprint Priority
            </Text>
            <Box
              sx={{
                flex: '0 0 auto',
                bg: 'grey.0',
                border: '1px solid',
                borderColor: 'grey.7',
                borderRadius: '0.25em',
                padding: '0.25em',
                lineHeight: 1,
              }}
              title={`Click to ${isVisible ? 'hide' : 'show'}`}
              onClick={handleToggleVisibility}
            >
              {isVisible ? <Eye size="1em" /> : <EyeSlash size="1em" />}
            </Box>
          </Flex>
          <Box sx={{ fontSize: 0, mt: '-0.5rem' }}>
            {categories.map((element) => (
              <Box
                key={element.label}
                sx={{
                  mt: '0.5rem',
                }}
              >
                <LegendElement {...element} />
              </Box>
            ))}
          </Box>
        </Box>
      ) : (
        <Text sx={{ py: '0.25rem', px: '0.5rem' }}>Show Legend</Text>
      )}
    </Box>
  )
}

Legend.propTypes = {
  isVisible: PropTypes.bool,
  onToggleVisibility: PropTypes.func.isRequired,
}

Legend.defaultProps = {
  isVisible: true,
}

export default memo(Legend)
