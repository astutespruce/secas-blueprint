import React, { memo, useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import { Eye, EyeSlash } from '@emotion-icons/fa-solid'
import { Box, Button, Flex, Text } from 'theme-ui'

import LegendElement from './LegendElement'

const Legend = ({
  title,
  subtitle,
  categories,
  isVisible,
  onToggleVisibility,
}) => {
  const [isOpen, setIsOpen] = useState(true)

  const handleClick = useCallback(() => {
    setIsOpen((prevIsOpen) => !prevIsOpen)
  }, [])

  const handleKeyDown = useCallback(({ target: { role }, key }) => {
    if (key === 'Enter' && role === 'button') {
      setIsOpen((prevIsOpen) => !prevIsOpen)
    }
  }, [])

  const handleToggleVisibility = useCallback(
    (e) => {
      onToggleVisibility()
      e.stopPropagation()
      e.nativeEvent.stopImmediatePropagation()
    },
    [onToggleVisibility]
  )

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
        userSelect: 'none',
      }}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
    >
      {isOpen ? (
        <Box
          sx={{
            pt: '0.5rem',
            px: '0.5rem',
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
                lineHeight: 1.1,
              }}
            >
              {title}
              {subtitle ? (
                <Text
                  sx={{ fontWeight: 'normal', fontSize: 0, color: 'grey.8' }}
                >
                  {subtitle}
                </Text>
              ) : null}
            </Text>
            <Button
              sx={{
                flex: '0 0 auto',
                bg: 'grey.0',
                color: 'text',
                border: '1px solid',
                borderColor: 'grey.7',
                borderRadius: '0.25em',
                padding: '0.25em',
                lineHeight: 1,
                '&:hover': {
                  bg: 'grey.1',
                },
              }}
              title={`Click to ${isVisible ? 'hide' : 'show'}`}
              onClick={handleToggleVisibility}
              tabIndex={0}
            >
              {isVisible ? <Eye size="1em" /> : <EyeSlash size="1em" />}
            </Button>
          </Flex>
          <Box sx={{ fontSize: 0, mt: '0.5em' }}>
            {categories.map((element) => (
              <Box
                key={element.label}
                sx={{
                  mb: '0.5rem',
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
  title: PropTypes.string.isRequired,
  subtitle: PropTypes.string,
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      color: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  isVisible: PropTypes.bool,
  onToggleVisibility: PropTypes.func.isRequired,
}

Legend.defaultProps = {
  subtitle: null,
  isVisible: true,
}

export default memo(Legend)
