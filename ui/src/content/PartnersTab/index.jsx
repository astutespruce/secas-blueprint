import React from 'react'
import PropTypes from 'prop-types'

import { Box, Divider, Heading, Text } from 'theme-ui'

import Ownership from './Ownership'
import Protection from './Protection'
import LTAList from './LTAList'

const PartnersTab = ({
  unitType,
  analysisAcres,
  ownership,
  protection,
  counties,
}) => {
  return (
    <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
      <Box as="section">
        <Heading as="h3">Conserved Lands / Marine Areas Ownership</Heading>
        {ownership === null ? (
          <Text sx={{ color: 'grey.7' }}>No information available.</Text>
        ) : (
          <Ownership analysisAcres={analysisAcres} ownership={ownership} />
        )}
      </Box>

      <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

      <Box as="section">
        <Heading as="h3">Land / Marine Protection Status</Heading>
        {protection === null ? (
          <Text sx={{ color: 'grey.7' }}>No information available.</Text>
        ) : (
          <Protection analysisAcres={analysisAcres} protection={protection} />
        )}
      </Box>

      {unitType === 'subwatershed' ? (
        <>
          <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

          <Box as="section">
            <Heading as="h3">Land Trusts by County</Heading>
            {counties === null ? (
              <Text sx={{ color: 'grey.7' }}>No information available.</Text>
            ) : (
              <LTAList counties={counties} />
            )}
          </Box>
        </>
      ) : null}
    </Box>
  )
}

PartnersTab.propTypes = {
  unitType: PropTypes.string.isRequired,
  analysisAcres: PropTypes.number.isRequired,
  ownership: PropTypes.objectOf(PropTypes.number),
  protection: PropTypes.objectOf(PropTypes.number),
  counties: PropTypes.objectOf(PropTypes.arrayOf(PropTypes.string)),
}

PartnersTab.defaultProps = {
  ownership: null,
  protection: null,
  counties: null,
}

export default PartnersTab
