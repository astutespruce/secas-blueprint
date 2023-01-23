import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import EcosystemHeader from './EcosystemHeader'
import IndicatorFilter from './IndicatorFilter'

const Ecosystem = ({
  id,
  label,
  color,
  borderColor,
  indicators,
  filters,
  onChange,
}) => {
  const filterCount = filters
    ? Object.entries(filters).filter(
        ([indicatorId, { enabled }]) =>
          indicatorId.search(`:${id}_`) !== -1 && enabled
      ).length
    : 0

  return (
    <Box
      sx={{
        width: '100%',
        flex: '0 0 auto',
        '&:not(:first-of-type)': {
          '&>div:first-of-type': {
            borderTop: '1px solid',
            borderTopColor: borderColor,
          },
        },
      }}
    >
      <EcosystemHeader
        id={id}
        filterCount={filterCount}
        label={label}
        color={color}
        borderColor={borderColor}
      />

      <Box sx={{ pb: '2rem' }}>
        {indicators.map((indicator) => (
          <IndicatorFilter
            key={indicator.id}
            {...indicator}
            {...filters[indicator.id]}
            onChange={onChange}
          />
        ))}
      </Box>
    </Box>
  )
}

Ecosystem.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
  borderColor: PropTypes.string.isRequired,
  indicators: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      description: PropTypes.string, // .isRequired,
      values: PropTypes.arrayOf(
        PropTypes.shape({
          value: PropTypes.number.isRequired,
          label: PropTypes.string.isRequired,
        })
      ).isRequired,
      goodThreshold: PropTypes.number,
    })
  ).isRequired,
  filters: PropTypes.objectOf(
    PropTypes.shape({
      enabled: PropTypes.bool,
      range: PropTypes.arrayOf(PropTypes.number).isRequired,
    })
  ).isRequired,
  onChange: PropTypes.func,
}

Ecosystem.defaultProps = {
  onChange: () => {},
}

export default Ecosystem
