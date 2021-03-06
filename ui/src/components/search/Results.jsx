import React, { useCallback, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { OutboundLink } from 'components/link'
import LoadingIcon from './LoadingIcon'
import { siteMetadata } from '../../../gatsby-config'

const { contactEmail } = siteMetadata

const highlightCSS = {
  fontWeight: 'bold',
  bg: 'grey.0',
  '&:hover': {
    bg: 'grey.0',
  },
}

const Results = ({
  results,
  index,
  isLoading,
  error,
  location,
  onSetLocation,
}) => {
  const listNode = useRef(null)

  useEffect(() => {
    // make sure that all nodes are created first
    if (
      listNode.current &&
      listNode.current.children &&
      listNode.current.children.length > index &&
      listNode.current.children[index]
    ) {
      listNode.current.children[index].focus()
    }
  }, [index])

  const handleSetLocation = useCallback(
    (nextIndex) => {
      const { id, name, longitude, latitude } = results[nextIndex]

      onSetLocation({
        id,
        name,
        longitude,
        latitude,
      })
    },
    [results, onSetLocation]
  )

  const handleClick = useCallback(
    ({
      target: {
        dataset: { index: nextIndex },
      },
    }) => {
      if (nextIndex !== undefined) {
        handleSetLocation(nextIndex)
      }
    },
    [handleSetLocation]
  )

  const handleKeyDown = useCallback(
    ({
      key,
      target: {
        dataset: { index: nextIndex },
      },
    }) => {
      if (key === 'Enter' && nextIndex !== undefined) {
        handleSetLocation(nextIndex)
      }
    },
    [handleSetLocation]
  )

  if (error) {
    return (
      <Box
        sx={{
          color: 'grey.7',
          pl: '1rem',
          pr: '1.5rem',
          py: '2rem',
        }}
      >
        <Text>
          <Flex sx={{ alignItems: 'center' }}>
            <ExclamationTriangle
              size="1.5rem"
              style={{ margin: '0 0.5rem 0 0' }}
            />
            <Text sx={{ fontSize: [2, 3] }}>Error loading search results.</Text>
          </Flex>

          <Text sx={{ mt: '1rem' }}>
            Please try a different search term. If the error continues, please{' '}
            <OutboundLink to={`mailto:${contactEmail}`}>
              let us know
            </OutboundLink>
            .
          </Text>
        </Text>
      </Box>
    )
  }

  if (isLoading) {
    return (
      <Flex
        sx={{
          alignItems: 'center',
          justifyContent: 'center',
          color: 'grey.7',
          px: '1rem',
          py: '2rem',
        }}
      >
        <LoadingIcon
          sx={{
            width: '2rem',
            height: '2rem',
            margin: '0 0.5rem 0 0',
            color: 'grey.5',
          }}
        />
        <Text>Loading...</Text>
      </Flex>
    )
  }

  if (!(results && results.length > 0)) {
    return (
      <Flex
        sx={{
          alignItems: 'center',
          justifyContent: 'center',
          color: 'grey.7',
          px: '1rem',
          py: '2rem',
        }}
      >
        No results found
      </Flex>
    )
  }

  return (
    <Box ref={listNode}>
      {results.map(({ id, name, address }, i) => (
        <Box
          key={id}
          data-index={i}
          tabIndex="0"
          onKeyDown={handleKeyDown}
          onClick={handleClick}
          sx={{
            cursor: 'pointer',
            borderBottom: '1px solid',
            borderBottomColor: 'grey.1',
            py: '0.75rem',
            pl: '1rem',
            pr: '1.5rem',
            '&:hover': {
              bg: 'grey.0',
            },
            ...(location && id === location.id ? highlightCSS : {}),
          }}
        >
          <Box sx={{ pointerEvents: 'none' }}>
            <Text>{name}</Text>
            {address ? (
              <Text sx={{ fontSize: [0, 1], color: 'grey.7' }}>{address}</Text>
            ) : null}
          </Box>
        </Box>
      ))}
    </Box>
  )
}

Results.propTypes = {
  results: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      latitude: PropTypes.number.isRequired,
      longitude: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
      address: PropTypes.string,
    })
  ),
  index: PropTypes.number,
  isLoading: PropTypes.bool,
  error: PropTypes.object,
  location: PropTypes.shape({
    id: PropTypes.string.isRequired,
    latitude: PropTypes.number.isRequired,
    longitude: PropTypes.number.isRequired,
    name: PropTypes.string,
  }),
  onSetLocation: PropTypes.func.isRequired,
}

Results.defaultProps = {
  index: null,
  isLoading: false,
  error: null,
  results: [],
  location: null,
}

export default Results
