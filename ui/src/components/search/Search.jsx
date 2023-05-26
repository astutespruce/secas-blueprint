import React, {
  useCallback,
  useEffect,
  useState,
  memo,
  forwardRef,
} from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { useSearch } from './Provider'
import SearchField from './SearchField'
import Results from './Results'

/* eslint-disable-next-line react/display-name */
const Search = forwardRef(({ onSelect, ...props }, ref) => {
  const [index, setIndex] = useState(null)

  const {
    query,
    setQuery,
    selectedId,
    setSelectedId,
    isLoading,
    error,
    results,
  } = useSearch()

  const handleKeyDown = useCallback(
    ({ key }) => {
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
    [results, index]
  )

  useEffect(() => {
    setIndex(null)
  }, [query])

  const handleSelectId = useCallback(
    (id) => {
      setSelectedId(id)
      onSelect(id)
    },
    [setSelectedId, onSelect]
  )

  return (
    <Box onKeyDown={handleKeyDown}>
      <SearchField ref={ref} value={query} onChange={setQuery} {...props} />

      {query && query.length >= 3 ? (
        <Results
          results={results}
          index={index}
          isLoading={isLoading}
          error={error}
          selectedId={selectedId}
          setSelectedId={handleSelectId}
        />
      ) : null}
    </Box>
  )
})

Search.propTypes = {
  onSelect: PropTypes.func,
}

Search.defaultProps = {
  onSelect: () => {},
}

export default memo(Search)
