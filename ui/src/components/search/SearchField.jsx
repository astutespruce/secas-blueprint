import React, { useEffect, useState, useCallback, useRef } from 'react'
import PropTypes from 'prop-types'
import { Search, Times } from '@emotion-icons/fa-solid'
import { Box, Flex, Input } from 'theme-ui'

const SearchField = ({ value, onChange }) => {
  const [internalValue, setInternalValue] = useState('')
  const timeoutRef = useRef(null)

  const handleChange = useCallback(
    ({ target: { value: newValue } }) => {
      setInternalValue(() => newValue)

      // debounce call to onChange
      if (timeoutRef.current !== null) {
        clearTimeout(timeoutRef.current)
      }
      timeoutRef.current = setTimeout(() => {
        onChange(newValue)
        clearTimeout(timeoutRef.current)
      }, 250)
    },
    [onChange]
  )

  const handleReset = useCallback(() => {
    setInternalValue(() => '')
    onChange('')
  }, [onChange])

  useEffect(() => {
    // set value on mount if context has a previous value
    if (value !== '') {
      setInternalValue(value)
    }
  }, [value])

  return (
    <Box
      sx={{
        py: '0.5rem',
        px: '1rem',
      }}
    >
      <Flex
        sx={{
          border: '1px solid',
          borderColor: 'grey.1',
          px: '0.5rem',
          borderRadius: '0.5rem',
          color: value === '' ? 'grey.4' : 'grey.9',
          alignItems: 'center',
          '&:focus, &:focus-within': {
            color: 'grey.9',
            borderColor: 'grey.9',
          },
        }}
      >
        <Search size="1em" style={{ flex: '0 0 auto' }} />
        <Input
          autoFocus
          sx={{
            width: '100%',
            flex: '1 1 auto',
            border: 'none',
            outline: 'none',
            '&::placeholder': {
              color: 'grey.4',
            },
          }}
          placeholder="Enter a location name"
          value={internalValue}
          onChange={handleChange}
        />
        {value !== '' && (
          <Box
            sx={{
              color: 'grey.5',
              '&:hover': {
                color: 'grey.9',
              },
            }}
          >
            <Times
              size="1.25em"
              style={{
                flex: '0 0 auto',
                cursor: 'pointer',
                display: 'block',
              }}
              onClick={handleReset}
            />
          </Box>
        )}
      </Flex>
    </Box>
  )
}

SearchField.propTypes = {
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
}

SearchField.defaultProps = {
  value: '',
}

export default SearchField
