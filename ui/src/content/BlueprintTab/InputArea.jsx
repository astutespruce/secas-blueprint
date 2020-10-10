import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { OutboundLink } from 'components/link'

import { formatPercent } from 'util/format'

import InputAreaPriorityChart from './InputAreaPriorityChart'

const InputArea = ({
  label,
  version,
  percent,
  infoURL,
  dataURL,
  viewerURL,
  viewerName,
  values,
  valueLabel,
}) => {
  console.log('values ', values)

  const hasLinks = infoURL || dataURL || viewerURL

  return (
    <Box
      sx={{
        '&:not(:first-of-type)': {
          mt: '2rem',
        },
      }}
    >
      <Flex sx={{ justifyContent: 'space-between', width: '100%' }}>
        <Text sx={{ fontWeight: 'bold', fontSize: 3 }}>
          {label} {version && version}
        </Text>
        <Text sx={{ fontSize: 0, color: 'grey.7', textAlign: 'right' }}>
          {formatPercent(percent)}% of area
        </Text>
      </Flex>

      {hasLinks ? (
        <Box sx={{ ml: '1rem' }}>
          {infoURL || dataURL ? (
            <Flex>
              {infoURL ? (
                <OutboundLink to={infoURL}>more information</OutboundLink>
              ) : null}

              {infoURL && dataURL ? (
                <Text as="span">&nbsp;&nbsp;|&nbsp;&nbsp;</Text>
              ) : null}
              {dataURL ? (
                <OutboundLink to={dataURL}>access data</OutboundLink>
              ) : null}
            </Flex>
          ) : null}

          {viewerURL ? (
            <Text sx={{ fontSize: 0, mt: '0.5rem' }}>
              More detailed information for Blueprint indicators is available in
              the <OutboundLink to={viewerURL}>{viewerName}</OutboundLink>
            </Text>
          ) : null}
        </Box>
      ) : null}

      <InputAreaPriorityChart
        inputLabel={label}
        values={values}
        valueLabel={valueLabel}
      />
    </Box>
  )
}

InputArea.propTypes = {
  label: PropTypes.string.isRequired,
  version: PropTypes.string,
  percent: PropTypes.number.isRequired,
  infoURL: PropTypes.string,
  dataURL: PropTypes.string,
  viewerURL: PropTypes.string,
  viewerName: PropTypes.string,
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
      color: PropTypes.string.isRequired,
      percent: PropTypes.number,
    })
  ),
  valueLabel: PropTypes.string,
}

InputArea.defaultProps = {
  version: null,
  infoURL: null,
  dataURL: null,
  viewerURL: null,
  viewerName: null,
  values: [],
  valueLabel: null,
}

export default InputArea
