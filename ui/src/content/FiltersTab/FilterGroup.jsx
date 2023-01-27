import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import FilterGroupHeader from './FilterGroupHeader'
import Filter from './Filter'

const FilterGroup = ({
  id,
  label,
  color,
  borderColor,
  entries,
  filters,
  onChange,
}) => (
  // const filterCount = filters
  //   ? Object.entries(filters).filter(
  //       ([indicatorId, { enabled }]) =>
  //         indicatorId.search(`:${id}_`) !== -1 && enabled
  //     ).length
  //   : 0

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
    <FilterGroupHeader
      id={id}
      // filterCount={filterCount}
      label={label}
      color={color}
      borderColor={borderColor}
    />

    <Box sx={{ mb: '1rem' }}>
      {entries.map((entry) => (
        <Filter
          key={entry.id}
          {...entry}
          {...filters[entry.id]}
          onChange={onChange}
        />
      ))}
    </Box>
  </Box>
)

FilterGroup.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
  borderColor: PropTypes.string.isRequired,
  entries: PropTypes.arrayOf(
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

FilterGroup.defaultProps = {
  onChange: () => {},
}

export default FilterGroup
