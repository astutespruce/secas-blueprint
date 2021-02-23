import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text, Divider } from 'theme-ui'
import {
  ArrowUp as ArrowUpIcon,
  ArrowDown as ArrowDownIcon,
} from '@emotion-icons/fa-solid'
import styled from '@emotion/styled'

import { sum } from 'util/data'
import { formatPercent } from 'util/format'

import IndicatorPercentChart from './IndicatorPercentChart'

const labelCSS = {
  flex: '0 0 auto',
  width: '5em',
  fontWeight: 'bold',
  fontSize: 0,
}

const ArrowUp = styled(ArrowUpIcon)({
  width: '1em',
  height: '1em',
  margin: 0,
  flex: '0 0 auto',
})

const ArrowDown = styled(ArrowDownIcon)({
  width: '1em',
  height: '1em',
  margin: 0,
  flex: '0 0 auto',
})

const IndicatorPercentTable = ({ type, values, goodThreshold }) => {
  // remainder values, like area outside SE, are assigned values < 0
  const remainders = values.filter(({ value }) => value < 0)

  if (goodThreshold === null) {
    return (
      <Box sx={{ my: '2rem' }}>
        {values
          .filter(({ value }) => value >= 0)
          .map(({ value, label, percent, isHighValue, isLowValue }) => (
            <Flex
              key={value || label}
              sx={{
                alignItems: isLowValue ? 'flex-end' : 'flex-start',
                '&:not(:first-of-type)': { mt: '1rem' },
              }}
            >
              <Text sx={labelCSS}>
                {isHighValue && (
                  <Flex sx={{ alignItems: 'center' }}>
                    <ArrowUp />
                    <Text sx={{ ml: '0.1rem' }}>High:</Text>
                  </Flex>
                )}
                {isLowValue && (
                  <Flex sx={{ alignItems: 'center' }}>
                    <ArrowDown />
                    <Text sx={{ ml: '0.1rem' }}>Low:</Text>
                  </Flex>
                )}
              </Text>
              <IndicatorPercentChart
                value={value}
                label={label}
                percent={percent}
              />
            </Flex>
          ))}

        {remainders.length > 0 ? (
          <>
            <Divider variant="styles.hr.dashed" sx={{ mb: '1.5rem' }} />
            <Box>
              {remainders.map(({ value, label, percent }) => (
                <Flex key={value} sx={{ mt: '1rem' }}>
                  <Text sx={labelCSS} />
                  <IndicatorPercentChart
                    value={value}
                    label={label}
                    percent={percent}
                  />
                </Flex>
              ))}
            </Box>
          </>
        ) : null}
      </Box>
    )
  }

  const goodPercents = values.filter(({ value }) => value >= goodThreshold)
  const notGoodPercents = values.filter(
    ({ value }) => value >= 0 && value < goodThreshold
  )

  const totalGoodPercent = sum(goodPercents.map(({ percent }) => percent))
  const totalNotGoodPercent = sum(notGoodPercents.map(({ percent }) => percent))

  return (
    <Box sx={{ my: '2rem' }}>
      {goodPercents.map(({ value, label, percent, isHighValue }) => (
        <Flex key={value} sx={{ '&:not(:first-of-type)': { mt: '1rem' } }}>
          <Text sx={labelCSS}>
            {isHighValue && (
              <Flex sx={{ alignItems: 'center' }}>
                <ArrowUp />
                <Text sx={{ ml: '0.1rem' }}>High:</Text>
              </Flex>
            )}
          </Text>
          <IndicatorPercentChart
            value={value}
            label={label}
            percent={percent}
            isGood
          />
        </Flex>
      ))}

      <Box sx={{ mt: '1.5rem', color: 'grey.7', fontSize: 0 }}>
        <Flex sx={{ justifyContent: 'center', alignItems: 'center' }}>
          <ArrowUp />
          <Text sx={{ width: '14em', ml: '0.1em' }}>
            {formatPercent(totalGoodPercent)}% in good condition
          </Text>
        </Flex>

        <Box
          sx={{
            borderBottom: '1px dashed',
            borderBottomColor: 'grey.6',
            height: '1px',
            my: '0.25rem',
          }}
        />

        <Flex sx={{ justifyContent: 'center', alignItems: 'center' }}>
          <ArrowDown />
          <Text sx={{ width: '14em', ml: '0.1em' }}>
            {formatPercent(totalNotGoodPercent)}% not in good condition
          </Text>
        </Flex>
      </Box>

      {notGoodPercents.map(({ value, label, percent, isLowValue }) => (
        <Flex key={value} sx={{ mt: '1rem', alignItems: 'flex-end' }}>
          <Text sx={labelCSS}>
            {isLowValue && (
              <Flex sx={{ alignItems: 'center' }}>
                <ArrowDown />
                <Text sx={{ ml: '0.1rem' }}>Low:</Text>
              </Flex>
            )}
          </Text>
          <IndicatorPercentChart
            value={value}
            label={label}
            percent={percent}
            isGood={false}
          />
        </Flex>
      ))}

      {remainders.length > 0 ? (
        <>
          <Divider variant="styles.hr.dashed" sx={{ mb: '1.5rem' }} />
          <Box>
            {remainders.map(({ value, label, percent }) => (
              <Flex key={value} sx={{ mt: '1rem' }}>
                <Text sx={labelCSS} />
                <IndicatorPercentChart
                  value={value}
                  label={label}
                  percent={percent}
                  percentSuffix={type === 'pixel' ? '' : 'of area'}
                />
              </Flex>
            ))}
          </Box>
        </>
      ) : null}
    </Box>
  )
}

IndicatorPercentTable.propTypes = {
  type: PropTypes.string.isRequired,
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number, // if <0, it is a remainder value
      label: PropTypes.string.isRequired,
      percent: PropTypes.number.isRequired,
      isHighValue: PropTypes.bool,
      isLowValue: PropTypes.bool,
    })
  ).isRequired,
  goodThreshold: PropTypes.number,
}

IndicatorPercentTable.defaultProps = {
  goodThreshold: null,
}

export default IndicatorPercentTable
