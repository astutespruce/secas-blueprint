import React, { useCallback, useRef, useState, useMemo } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex } from 'theme-ui'

const thumbStyle = {
  appearance: 'none',
  backgroundColor: 'blue.6',
  border: 'none',
  borderRadius: '50%',
  boxShadow: '0 0 1px #333',
  height: '1.25rem',
  width: '1.25rem',
  pointerEvents: 'all',
  position: 'relative',
  cursor: 'pointer',
  outline: 'none',
  '&:hover': {
    backgroundColor: 'blue.9',
  },
}

const RangeSlider = ({ values, range: [initMin, initMax], onChange }) => {
  const { domain, intervals } = useMemo(
    () => {
      const valueRange = [values[0].value, values[values.length - 1].value]
      return {
        domain: valueRange,
        intervals: Array.from(
          { length: valueRange[1] - valueRange[0] },
          (_, i) => i + valueRange[0]
        ),
      }
    },
    // values do not change after mount
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  const [{ min, max }, setState] = useState({ min: initMin, max: initMax })

  const minRef = useRef(null)
  const maxRef = useRef(null)

  const handleMinChange = useCallback(
    ({ target: { value: rawValue } }) => {
      // clip to [domain[0], max]
      const value = Math.min(rawValue, max)
      setState((prevState) => ({
        ...prevState,
        min: value,
      }))
      onChange([value, max])
    },
    [max, onChange]
  )

  const handleMaxChange = useCallback(
    ({ target: { value: rawValue } }) => {
      // clip to [min, domain[1]]
      const value = Math.max(rawValue, min)
      setState((prevState) => ({
        ...prevState,
        max: value,
      }))
      onChange([min, value])
    },
    [min, onChange]
  )

  return (
    <Box>
      <Box
        sx={{
          position: 'relative',
          zIndex: 1,
          py: '1rem',
          'input[type="range"]': {
            zIndex: 1,
            appearance: 'none',
            pointerEvents: 'none',
            position: 'absolute',
            height: 0,
            width: '100%',
            outline: 'none',
            background: 'transparent',
          },
          'input[type="range"]::-webkit-slider-thumb': thumbStyle,
          'input[type="range"]::-moz-range-thumb': thumbStyle,
          'input[type="range"]::-ms-thumb': thumbStyle,
        }}
      >
        <input
          type="range"
          min={domain[0]}
          max={domain[1]}
          value={min}
          step={1}
          ref={minRef}
          onChange={handleMinChange}
          style={{
            zIndex: max < domain[1] ? 1 : 3,
          }}
        />
        <input
          type="range"
          min={domain[0]}
          max={domain[1]}
          value={max}
          step={1}
          ref={maxRef}
          onChange={handleMaxChange}
          style={{
            zIndex: 2,
          }}
        />
        <Box
          sx={{
            position: 'relative',
            ml: '0.65rem',
            mr: '0.35rem',
            zIndex: 0,
            '&>div': {
              borderRadius: 3,
              height: 5,
              position: 'absolute',
            },
          }}
        >
          {/* track */}
          <Flex
            sx={{
              zIndex: 1,
              backgroundColor: 'grey.1',
              width: '100%',
            }}
          >
            {intervals.map((v) => (
              <Box
                key={v}
                sx={{
                  backgroundColor: v >= min && v < max ? 'primary' : 'grey.2',
                  flex: '1 1 auto',
                  mx: '0.1em',
                  height: '100%',
                }}
              />
            ))}
          </Flex>
        </Box>
      </Box>
    </Box>
  )
}

RangeSlider.propTypes = {
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  range: PropTypes.arrayOf(PropTypes.number).isRequired,
  onChange: PropTypes.func,
}

RangeSlider.defaultProps = {
  onChange: () => {},
}

export default RangeSlider
