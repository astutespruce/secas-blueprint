import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text, Heading, Image } from 'theme-ui'
import { Reply } from '@emotion-icons/fa-solid'

import { OutboundLink } from 'components/link'
import { formatPercent } from 'util/format'
import { sum } from 'util/data'
import theme from 'theme'

import IndicatorPercentTable from './IndicatorPercentTable'
import { IndicatorPropType } from './proptypes'

const IndicatorDetails = ({
  type,
  label,
  input: { label: inputLabel, percent: inputPercent },
  ecosystem: { id: ecosystemId, label: ecosystemLabel, color, borderColor },
  description,
  datasetID,
  goodThreshold,
  values,
  analysisAcres,
  blueprintAcres,
  outsideSEPercent,
  onClose,
}) => {
  console.log(
    'incoming values',
    inputLabel,
    inputPercent,
    values,
    analysisAcres,
    blueprintAcres
  )

  // eslint-disable-next-line global-require,import/no-dynamic-require
  const icon = require(`images/${ecosystemId}.svg`)

  const totalIndicatorPercent = sum(values.map(({ percent }) => percent))

  const percentTableValues = values
    .map((value, i) => ({
      ...value,
      isHighValue: i === values.length - 1,
      isLowValue: i === 0,
    }))
    .reverse()

  const notEvaluatedPercent = inputPercent - totalIndicatorPercent
  if (notEvaluatedPercent >= 1) {
    percentTableValues.push({
      value: -1,
      label: 'Not evaluated for this indicator',
      percent: notEvaluatedPercent,
    })
  }

  const outsideInputPercent = 100 - outsideSEPercent - inputPercent
  if (outsideInputPercent >= 1) {
    percentTableValues.push({
      value: -2,
      percent: outsideInputPercent,
      label: `Outside ${inputLabel} input area`,
    })
  }

  if (outsideSEPercent >= 1) {
    percentTableValues.push({
      value: -3,
      label: 'Outside Southeast Blueprint',
      percent: outsideSEPercent,
    })
  }

  return (
    <Flex
      sx={{
        flexDirection: 'column',
        height: '100%',
        overflowY: 'hidden',
      }}
    >
      <Box
        sx={{
          cursor: 'pointer',
          bg: color,
          py: ['1rem', '0.5rem'],
          pl: '0.25rem',
          pr: '1rem',
          borderBottom: '1px solid',
          borderBottomColor: borderColor,
        }}
      >
        <Flex
          onClick={onClose}
          sx={{
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Flex>
            <Text sx={{ color: theme.colors.grey[7], flex: '0 0 auto' }}>
              <Reply
                size="0.75em"
                style={{
                  display: 'block',
                  margin: 0,
                }}
              />
            </Text>

            <Flex sx={{ alignItems: 'center' }}>
              <Image
                src={icon}
                sx={{
                  width: '2.5em',
                  height: '2.5em',
                  mr: '0.5em',
                  bg: '#FFF',
                  borderRadius: '2.5em',
                }}
              />
              <Box>
                <Text sx={{ fontSize: 0, color: 'grey.8' }}>
                  {ecosystemLabel}
                </Text>
                <Heading as="h4">{label}</Heading>
              </Box>
            </Flex>
          </Flex>

          {type !== 'pixel' ? (
            <Box sx={{ color: 'grey.8', fontSize: 0, textAlign: 'right' }}>
              <b>{formatPercent(totalIndicatorPercent)}%</b>
              <br />
              of area
            </Box>
          ) : null}
        </Flex>
      </Box>

      <Box
        sx={{
          pt: '0.5rem',
          px: '1rem',
          pb: '1rem',
          height: '100%',
          flex: '1 1 auto',
          overflowY: 'auto',
        }}
      >
        <Text as="p">
          Part of {inputLabel}.
          <br />
          <br />
          {description}
        </Text>

        <IndicatorPercentTable
          type={type}
          values={percentTableValues}
          goodThreshold={goodThreshold}
        />

        <Box sx={{ mt: '2rem' }}>
          <OutboundLink
            to={`https://seregion.databasin.org/datasets/${datasetID}`}
          >
            View this indicator in the Conservation Planning Atlas
          </OutboundLink>
        </Box>
      </Box>
    </Flex>
  )
}

IndicatorDetails.propTypes = {
  type: PropTypes.string.isRequired,
  ...IndicatorPropType,
  analysisAcres: PropTypes.number.isRequired,
  blueprintAcres: PropTypes.number.isRequired,
  outsideSEPercent: PropTypes.number,
  onClose: PropTypes.func.isRequired,
}

IndicatorDetails.defaultProps = {
  outsideSEPercent: 0,
}

export default IndicatorDetails
