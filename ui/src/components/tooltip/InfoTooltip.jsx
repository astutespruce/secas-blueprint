import React, { useState, useRef } from 'react'
import PropTypes from 'prop-types'
import {
  arrow,
  flip,
  shift,
  autoUpdate,
  useFloating,
  useInteractions,
  useHover,
  useFocus,
  useRole,
  useDismiss,
} from '@floating-ui/react-dom-interactions'
import { Box, Flex } from 'theme-ui'

const arrowBaseCSS = {
  position: 'absolute',
  zIndex: 1,
  width: '0.75rem',
  height: '0.75rem',
  bg: 'grey.9',
  transform: 'rotate(45deg)',
}

const bottomArrowCSS = {
  ...arrowBaseCSS,
  top: '0.375rem',
}

const topArrowCSS = {
  ...arrowBaseCSS,
  bottom: '0.375rem',
}

const InfoTooltip = ({ content }) => {
  // FIXME:
  const [open, setOpen] = useState(true)
  const arrowRef = useRef(null)
  const {
    context,
    x,
    y,
    reference,
    floating,
    strategy,
    placement,
    middlewareData: { arrow: { x: arrowX } = {}, shift: { x: shiftX } = {} },
  } = useFloating({
    placement: 'top',
    open,
    onOpenChange: setOpen,
    whileElementsMounted: autoUpdate,
    middleware: [arrow({ element: arrowRef }), flip(), shift()],
  })
  const { getReferenceProps, getFloatingProps } = useInteractions([
    useHover(context),
    useFocus(context),
    useRole(context, { role: 'tooltip' }),
    useDismiss(context),
  ])

  return (
    <>
      <Flex
        ref={reference}
        {...getReferenceProps()}
        sx={{
          flex: '0 0 auto',
          ml: '0.5em',
          justifyContent: 'center',
          alignItems: 'center',
          height: '1em',
          width: '1em',
          borderRadius: '2em',
          border: '1px solid',
          borderColor: 'grey.3',
          cursor: 'default',
          '&:hover': {
            bg: 'grey.1',
            borderColor: 'grey.4',
          },
        }}
      >
        i
      </Flex>
      {open && (
        <Box
          ref={floating}
          {...getFloatingProps()}
          sx={{
            position: strategy,
            top: y ?? 0,
            left: x ?? 0,
            p: '0.75rem',
            zIndex: 10000,
          }}
        >
          <Box
            sx={{
              position: 'relative',
              zIndex: 2,
              bg: '#FFF',
              p: '0.5em',
              borderRadius: '0.5em',
              boxShadow: '1px 1px 3px #333',
              border: '1px solid',
              borderColor: 'grey.3',
              overflow: 'hidden',
              maxWidth: '28rem',
              fontSize: 1,
            }}
          >
            {content}
          </Box>
          <Box
            ref={arrowRef}
            sx={
              placement === 'top'
                ? {
                    ...topArrowCSS,
                    left: `${arrowX - (shiftX || 0)}px`,
                  }
                : {
                    ...bottomArrowCSS,
                    left: `${arrowX - (shiftX || 0)}px`,
                  }
            }
          />
        </Box>
      )}
    </>
  )
}

InfoTooltip.propTypes = {
  content: PropTypes.string.isRequired,
}

export default InfoTooltip
