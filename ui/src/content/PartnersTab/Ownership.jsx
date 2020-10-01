import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { PercentBarChart } from 'components/chart'
import { useOwnership } from 'components/data'
import { OutboundLink } from 'components/link'

import { sum } from 'util/data'

const Ownership = ({ ownership }) => {
  const { ownership: OWNERSHIP } = useOwnership()

  const bars = OWNERSHIP.filter(({ id }) => ownership[id]).map((category) => ({
    ...category,
    percent: ownership[category.id],
  }))

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
        Land ownership is derived from the TNC{' '}
        <OutboundLink to="https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/edc/reportsdata/terrestrial/secured/Pages/default.aspx">
          Secured Lands Database
        </OutboundLink>{' '}
        (2018 Edition).
      </Text>
    </>
  )
}

Ownership.propTypes = {
  ownership: PropTypes.objectOf(PropTypes.number).isRequired,
}

export default Ownership
