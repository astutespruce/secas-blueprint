import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { OutboundLink } from 'components/link'

import { formatPercent } from 'util/format'

import InputAreaPriorityChart from './InputAreaPriorityChart'

const InputArea = ({
  label,
  description,
  version,
  percent,
  infoURL,
  dataURL,
  viewerURL,
  viewerName,
  values,
  valueLabel,
  valueCaption,
}) => {
  console.log('values ', values)

  const hasLinks = infoURL || dataURL || viewerURL

  return (
    <Box
      sx={{
        '&:not(:first-of-type)': {
          mt: '2rem',
          pt: '2rem',
          borderTop: '1px solid',
          borderTopColor: 'grey.1',
        },
      }}
    >
      <Flex
        sx={{
          justifyContent: 'space-between',
          width: '100%',
          mb: '1rem',
        }}
      >
        <Text
          sx={{ fontWeight: 'bold', fontSize: 3, lineHeight: 1.2, mr: '1rem' }}
        >
          {label} {version && version}
        </Text>
        <Text
          sx={{
            fontSize: 0,
            color: 'grey.7',
            textAlign: 'right',
            lineHeight: 1,
          }}
        >
          {formatPercent(percent)}% of area
        </Text>
      </Flex>

      <InputAreaPriorityChart
        values={values}
        valueLabel={valueLabel}
        valueCaption={valueCaption}
      />

      <Text as="p" sx={{ mt: '1rem', fontSize: 1 }}>
        {description} <OutboundLink to={infoURL}>Learn more</OutboundLink> or{' '}
        <OutboundLink to={dataURL}>access data</OutboundLink>.{' '}
        {viewerURL ? (
          <>
            More detailed information for {label} indicators is available in the{' '}
            <OutboundLink to={viewerURL}>{viewerName}</OutboundLink>.
          </>
        ) : null}
      </Text>
    </Box>
  )
}

InputArea.propTypes = {
  label: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  version: PropTypes.string,
  percent: PropTypes.number.isRequired,
  infoURL: PropTypes.string.isRequired,
  dataURL: PropTypes.string.isRequired,
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
  valueCaption: PropTypes.string,
}

InputArea.defaultProps = {
  version: null,
  viewerURL: null,
  viewerName: null,
  values: [],
  valueLabel: null,
  valueCaption: null,
}

export default InputArea
