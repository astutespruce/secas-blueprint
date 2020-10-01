import React, { useCallback, useEffect, useState, memo } from 'react'
import { Box } from 'theme-ui'

import { useSearch } from './Provider'
import SearchField from './SearchField'
import Results from './Results'

const Search = () => {
  const [index, setIndex] = useState(null)

  const {
    query,
    setQuery,
    location,
    setLocation,
    isLoading,
    error,
    results,
  } = useSearch()

  const handleKeyDown = useCallback(
    ({ key }) => {
      // escape clears everything
      if (key === 'Escape') {
        setQuery('')
        return
      }

      if (!(results && results.length > 0)) {
        return
      }

      let nextIndex = 0
      if (key === 'ArrowUp' && index !== null) {
        if (index > 0) {
          nextIndex = index - 1
        } else {
          // wrap around
          nextIndex = results.length - 1
        }
        setIndex(() => nextIndex)
      } else if (key === 'ArrowDown') {
        if (index !== null) {
          if (index < results.length - 1) {
            nextIndex = index + 1
          }
          // else wrap around, handled by set = 0 above
        }
        setIndex(() => nextIndex)
      }
    },
    [results, index, setQuery]
  )

  useEffect(() => {
    setIndex(null)
  }, [query])

  return (
    <Box onKeyDown={handleKeyDown}>
      <SearchField value={query} onChange={setQuery} />

      {query && query.length >= 3 ? (
        <Results
          results={results}
          index={index}
          isLoading={isLoading}
          error={error}
          location={location}
          onSetLocation={setLocation}
        />
      ) : null}
    </Box>
  )
}

export default memo(Search)
