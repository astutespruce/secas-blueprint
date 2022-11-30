import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Divider, Heading, Paragraph } from 'theme-ui'

import { useMapData, useSLR, useUrban } from 'components/data'
import { PseudoLink } from 'components/link'
import NeedHelp from 'content/NeedHelp'

import SLR from './SLR'
import Urban from './Urban'

const ThreatsTab = ({ type, slr, urban }) => {
  const { renderLayer, setRenderLayer } = useMapData()
  const urbanCategories = useUrban()
  const { depth: depthCategories, nodata: slrNodataCategories } = useSLR()

  const renderUrbanLayer = useCallback(
    () => {
      setRenderLayer({
        id: 'urban',
        label: 'Probability of urbanization by 2060',
        colors: urbanCategories
          .slice()
          .sort(({ value: leftValue }, { value: rightValue }) =>
            leftValue < rightValue ? -1 : 1
          )
          .map(({ color }) => color),
        categories: urbanCategories.filter(({ color }) => color !== null),
      })
    },
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  const renderSLRLayer = useCallback(
    () => {
      setRenderLayer({
        id: 'slr',
        label: 'Flooding extent by projected sea-level rise',
        colors: depthCategories
          .concat(slrNodataCategories)
          .map(({ color }) => color),
        // (color === '#FFFFFF' ? '#ffebc2' : color)
        categories: depthCategories
          .concat(slrNodataCategories)
          .map(({ label, ...rest }, i) => ({
            ...rest,
            label: i === 1 ? `${label} foot` : `${label} feet`,
            outlineWidth: 1,
            outlineColor: 'grey.5',
          })),
      })
    },
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  const handleUnsetRenderLayer = useCallback(
    () => {
      setRenderLayer(null)
    },
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  if (type !== 'pixel' && type !== 'subwatershed') {
    return (
      <Paragraph
        sx={{
          py: '2rem',
          px: '1rem',
          color: 'grey.7',
          textAlign: 'center',
          fontSize: 1,
        }}
      >
        No information on threats is available for marine units.
      </Paragraph>
    )
  }

  let slrLayerToggle = null
  let urbanLayerToggle = null

  if (type === 'pixel') {
    slrLayerToggle =
      renderLayer && renderLayer.id === 'slr' ? (
        <PseudoLink sx={{ fontSize: 0 }} onClick={handleUnsetRenderLayer}>
          hide map layer
        </PseudoLink>
      ) : (
        <PseudoLink sx={{ fontSize: 0 }} onClick={renderSLRLayer}>
          show on map
        </PseudoLink>
      )

    urbanLayerToggle =
      renderLayer && renderLayer.id === 'urban' ? (
        <PseudoLink sx={{ fontSize: 0 }} onClick={handleUnsetRenderLayer}>
          hide map layer
        </PseudoLink>
      ) : (
        <PseudoLink sx={{ fontSize: 0 }} onClick={renderUrbanLayer}>
          show on map
        </PseudoLink>
      )
  }

  return (
    <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
      <Box as="section">
        <Flex sx={{ justifyContent: 'space-between', alignItems: 'baseline' }}>
          <Heading as="h3">Urbanization</Heading>
          {urbanLayerToggle}
        </Flex>
        <Urban type={type} urban={urban} />
      </Box>

      <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

      <Box as="section">
        <Flex sx={{ justifyContent: 'space-between', alignItems: 'baseline' }}>
          <Heading as="h3">Sea Level Rise</Heading>
          {slrLayerToggle}
        </Flex>
        <SLR type={type} {...slr} />
      </Box>

      <NeedHelp />
    </Box>
  )
}

ThreatsTab.propTypes = {
  type: PropTypes.string.isRequired,
  slr: PropTypes.shape({
    depth: PropTypes.oneOfType([
      PropTypes.arrayOf(PropTypes.number),
      PropTypes.number,
    ]),
    nodata: PropTypes.oneOfType([
      PropTypes.arrayOf(PropTypes.number),
      PropTypes.number,
    ]),
  }),
  urban: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
}

ThreatsTab.defaultProps = {
  slr: null,
  urban: null,
}

export default ThreatsTab
