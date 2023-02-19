import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

const labelCSS = {
  color: 'grey.6',
  fontSize: 0,
  flex: '0 0 auto',
}

const patchCSS = {
  position: 'relative',
  flex: '1 1 auto',
  height: '0.75rem',
  bg: 'grey.0',
  '&:not(:first-of-type)': {
    borderLeft: '1px solid',
    borderLeftColor: 'grey.3',
  },
}

const currentPatchCSS = {
  ...patchCSS,
  bg: 'grey.6',
}

const IndicatorPixelValueChart = ({
  present,
  values,
  valueLabel,
  goodThreshold,
}) => {
  const [currentValue] = values.filter(({ percent }) => percent === 100)

  return (
    <Box sx={{ mt: goodThreshold ? '1.5rem' : '0.25rem' }}>
      {present && valueLabel ? (
        <Text
          sx={{
            fontSize: 0,
            color: 'grey.7',
            mt: '-0.25rem',
            mb: '0.5rem',
            lineHeight: 1.2,
          }}
        >
          {valueLabel}
        </Text>
      ) : null}
      <Flex sx={{ alignItems: 'center', opacity: present ? 1 : 0.25 }}>
        <Text sx={labelCSS}>Low</Text>
        <Flex
          sx={{
            alignItems: 'center',
            flex: '1 1 auto',
            mx: '1rem',
            border: '1px solid',
            borderColor: present ? 'grey.6' : 'grey.4',
          }}
        >
          {/* always have a 0 value bin */}
          {values[0].value > 0 ? <Box sx={patchCSS} /> : null}

          {values.map(({ value, percent }) => (
            <React.Fragment key={value}>
              <Box sx={percent === 100 ? currentPatchCSS : patchCSS}>
                {value === goodThreshold ? (
                  <Text
                    sx={{
                      position: 'absolute',
                      width: '94px',
                      top: '-1.2rem',
                      color: 'grey.6',
                      fontSize: '10px',
                      borderLeft: '1px dashed',
                      borderLeftColor: 'grey.6',
                    }}
                  >
                    &rarr; good condition
                  </Text>
                ) : null}
                {percent === 100 ? (
                  <Box
                    sx={{
                      position: 'absolute',
                      left: '50%',
                      top: '0.8rem',
                      ml: '-0.5rem',
                      borderBottom: '0.6rem solid',
                      borderBottomColor: 'grey.9',
                      borderLeft: '0.5rem solid transparent',
                      borderRight: '0.5rem solid transparent',
                    }}
                  />
                ) : null}
              </Box>
            </React.Fragment>
          ))}
        </Flex>
        <Text sx={labelCSS}>High</Text>
      </Flex>

      <Text sx={{ color: 'grey.7', fontSize: 0, mt: '1rem' }}>
        Value:{' '}
        {present
          ? currentValue.label
          : // <>
            //   {valueLabel
            //     ? `${valueLabel}: ${currentValue.label.toLowerCase()}`
            //     : currentValue.label}
            // </>
            'Not present'}
      </Text>
    </Box>
  )
}

IndicatorPixelValueChart.propTypes = {
  present: PropTypes.bool,
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
      percent: PropTypes.number.isRequired, // will be either 0 (absent) or 100 (present)
    })
  ).isRequired,
  valueLabel: PropTypes.string,
  goodThreshold: PropTypes.number,
}

IndicatorPixelValueChart.defaultProps = {
  valueLabel: null,
  present: false,
  goodThreshold: null,
}

export default IndicatorPixelValueChart
