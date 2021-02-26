import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { PercentBarChart } from 'components/chart'
import { useOwnership } from 'components/data'
import { OutboundLink } from 'components/link'

import { sum } from 'util/data'

const Ownership = ({ ownership }) => {
  const { ownership: OWNERSHIP } = useOwnership()

  // handle empty ownership information
  const bars = OWNERSHIP.filter(({ id }) => (ownership || {})[id]).map(
    (category) => ({
      ...category,
      percent: ownership[category.id],
    })
  )

  const total = sum(bars.map(({ percent }) => Math.min(percent, 100)))

  const remainder = 100 - total
  if (remainder > 0) {
    bars.push({
      id: 'not_conserved',
      label: 'Not conserved',
      color: 'grey.5',
      percent: remainder,
    })
  }

  return (
    <>
      {bars.map((bar) => (
        <PercentBarChart
          key={bar.id}
          {...bar}
          sx={{ mt: '0.5rem', mb: '1rem' }}
        />
      ))}

      <Text sx={{ color: 'grey.7', fontSize: 1 }}>
        {total > 100 ? (
          <>
            Note: due to overlapping protected areas compiled from multiple
            sources and designations, the sum of areas in above categories is
            more than 100% of this area.
            <br />
            <br />
          </>
        ) : null}
        Land and marine areas ownership is derived from the{' '}
        <OutboundLink to="https://www.sciencebase.gov/catalog/item/5f186a2082cef313ed843257">
          Protected Areas Database of the United States
        </OutboundLink>{' '}
        (PAD-US v2.1).
      </Text>
    </>
  )
}

Ownership.propTypes = {
  ownership: PropTypes.objectOf(PropTypes.number),
}

Ownership.defaultProps = {
  ownership: {},
}

export default Ownership
