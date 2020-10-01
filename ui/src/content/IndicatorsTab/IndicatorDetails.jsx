import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text, Heading, Image } from 'theme-ui'
import { Reply } from '@emotion-icons/fa-solid'

import { OutboundLink } from 'components/link'
import { formatPercent } from 'util/format'
import theme from 'theme'

import IndicatorPercentTable from './IndicatorPercentTable'
import { IndicatorPropType } from './proptypes'

const IndicatorDetails = ({
  id,
  label,
  ecosystem: { label: ecosystemLabel, color, borderColor },
  description,
  datasetID,
  goodThreshold,
  total,
  values,
  analysisAcres,
  blueprintAcres,
  onClose,
}) => {
  const ecosystemId = id.split('_')[0]
  // eslint-disable-next-line global-require,import/no-dynamic-require
  const icon = require(`images/${ecosystemId}.svg`)

  const remainder =
    (100 * Math.abs(analysisAcres - blueprintAcres)) / analysisAcres

  const percentTableValues = values
    .map((value, i) => ({
      ...value,
      isHighValue: i === values.length - 1,
      isLowValue: i === 0,
    }))
    .reverse()

  // remainder value for areas not analyzed for this indicator
  if (total + remainder < 100) {
    percentTableValues.push({
      value: null,
      label: 'Not evaluated for this indicator',
      percent: 100 - total - remainder,
    })
  }

  if (remainder >= 1) {
    percentTableValues.push({
      value: null,
      label: 'Outside Southeast Blueprint',
      percent: remainder,
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
      <Flex
        onClick={onClose}
        sx={{
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          bg: color,
          py: ['1rem', '0.5rem'],
          pl: '0.25rem',
          pr: '1rem',
          borderBottom: '1px solid',
          borderBottomColor: borderColor,
        }}
      >
        <Flex sx={{}}>
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
        <Box sx={{ color: 'grey.8', fontSize: 0, textAlign: 'right' }}>
          <b>{formatPercent(total)}%</b>
          <br />
          of area
        </Box>
      </Flex>

      <Box
        sx={{ p: '1rem', height: '100%', flex: '1 1 auto', overflowY: 'auto' }}
      >
        <Text as="p">{description}</Text>

        <IndicatorPercentTable
          values={percentTableValues}
          goodThreshold={goodThreshold}
        />

        <Box sx={{ mt: '2rem' }}>
          <OutboundLink
            to={`https://salcc.databasin.org/datasets/${datasetID}`}
          >
            View this indicator in the Conservation Planning Atlas
          </OutboundLink>
        </Box>
      </Box>
    </Flex>
  )
}

IndicatorDetails.propTypes = {
  ...IndicatorPropType,
  analysisAcres: PropTypes.number.isRequired,
  blueprintAcres: PropTypes.number.isRequired,
  total: PropTypes.number,
  onClose: PropTypes.func.isRequired,
}

IndicatorDetails.defaultProps = {
  total: 0,
}

export default IndicatorDetails
