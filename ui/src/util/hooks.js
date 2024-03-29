import {
  useState,
  useRef,
  useEffect,
  useLayoutEffect,
  useMemo,
  useCallback,
} from 'react'
import { dequal as deepEqual } from 'dequal'
import { useDebouncedCallback } from 'use-debounce'

const isSetEqual = (setA, setB) => {
  if (setA === setB) {
    // same instance or both are null
    return true
  }
  if (setA === null || setB === null) {
    return false
  }
  // if they have the same members but are different instances, equality
  // check above fails
  if (setA.size !== setB.size) {
    return false
  }

  return Array.from(setA).filter((d) => !setB.has(d)).length === 0
}

// ideas adapted from: https://github.com/kentcdodds/use-deep-compare-effect/blob/master/src/index.js
/**
 * Return the previous instance of the value if the incoming value is equal to it.
 *
 * @param {any} value
 */
export const memoizedIsEqual = (value) => {
  /* eslint-disable-next-line react-hooks/rules-of-hooks */
  const ref = useRef(null)

  if (value instanceof Set) {
    if (!isSetEqual(value, ref.current)) {
      ref.current = value
    }
  } else if (!deepEqual(value, ref.current)) {
    ref.current = value
  }

  return ref.current
}

/**
 * Same as native useEffect, but compare dependencies on deep rather than shallow equality.
 * @param {function} callback
 * @param {Array} dependencies
 */
export const useIsEqualEffect = (callback, dependencies) => {
  useEffect(
    callback,
    dependencies.map((d) => memoizedIsEqual(d))
  )
}

/**
 * Same as native useLayoutEffect, but compare dependencies on deep rather than shallow equality.
 * @param {function} callback
 * @param {Array} dependencies
 */
export const useIsEqualLayoutEffect = (callback, dependencies) => {
  useLayoutEffect(
    callback,
    dependencies.map((d) => memoizedIsEqual(d))
  )
}

/**
 * Same as native useMemo, but compare dependencies on deep rather than shallow equality.
 * @param {function} callback
 * @param {Array} dependencies
 */

export const useIsEqualMemo = (callback, dependencies) =>
  useMemo(
    callback,
    dependencies.map((d) => memoizedIsEqual(d))
  )

export const useIsEqualCallback = (callback, dependencies) =>
  useCallback(
    callback,
    dependencies.map((d) => memoizedIsEqual(d))
  )

/**
 * Function that is triggered on mount of component in UI.  Useful for handling
 * client-only components.
 * From: https://www.joshwcomeau.com/react/the-perils-of-rehydration/
 */
export const useHasMounted = () => {
  const [hasMounted, setHasMounted] = useState(false)
  useEffect(() => {
    setHasMounted(true)
  }, [])
  return hasMounted
}

// modeled off https://github.com/mapbox/mapbox-gl-js/blob/main/src/util/evented.js
export const useEventHandler = (delay) => {
  const onceCallback = useRef(null)

  const once = (callback) => {
    // previous listeners are ignored
    onceCallback.current = callback
  }

  const handler = useDebouncedCallback(() => {
    const { current: callback } = onceCallback
    if (callback) {
      callback()
      onceCallback.current = null
    }
  }, delay)

  return {
    once,
    handler,
  }
}
