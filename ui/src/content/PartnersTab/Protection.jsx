import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { PercentBarChart } from 'components/chart'
import { useOwnership } from 'components/data'
import { OutboundLink } from 'components/link'
import { sum } from 'util/data'

const Protection = ({ protection }) => {
  const { protection: PROTECTION } = useOwnership()

  const bars = PROTECTION.filter(({ id }) => protection[id]).map(
    (category) => ({
      ...category,
      percent: protection[category.id],
    })
  )

  const remainder = 100 - sum(bars.map(({ percent }) => percent))
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
        Land and marine protectection status is derived from the{' '}
        <OutboundLink to="https://www.sciencebase.gov/catalog/item/5f186a2082cef313ed843257">
          Protected Areas Database of the United States
        </OutboundLink>{' '}
        (PAD-US v2.1).
      </Text>
    </>
  )
}

Protection.propTypes = {
  protection: PropTypes.objectOf(PropTypes.number).isRequired,
}

export default Protection
