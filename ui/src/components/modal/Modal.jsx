import React, { useEffect } from 'react'
import { createPortal } from 'react-dom'
import PropTypes from 'prop-types'
import { Box, Button, Flex, Heading } from 'theme-ui'
import { TimesCircle } from '@emotion-icons/fa-regular'

import { hasWindow } from 'util/dom'

const absPostionCSS = {
  position: 'absolute',
  top: 0,
  bottom: 0,
  left: 0,
  right: 0,
}

const Modal = ({ children, title, width, onClose }) => {
  const handleClose = () => {
    onClose()
  }

  useEffect(() => {
    const handleEscape = ({ key }) => {
      if (key === 'Escape') {
        onClose()
      }
    }

    if (hasWindow) {
      document.addEventListener('keydown', handleEscape)
    }

    return () => {
      if (hasWindow) {
        document.removeEventListener('keydown', handleEscape)
      }
    }
  })

  return createPortal(
    <Flex
      sx={{
        ...absPostionCSS,
        zIndex: 10000,
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'auto',
      }}
    >
      <Box
        onClick={handleClose}
        sx={{
          ...absPostionCSS,
          zIndex: 1,
          bg: 'rgba(0,0,0,0.5)',
        }}
      />

      <Box
        sx={{
          width: ['100%', width],
          p: '0.5rem',
          background: '#fff',
          zIndex: 2,
          borderRadius: [0, '1rem'],
          boxShadow: ['none', '1px 1px 6px #000'],
        }}
      >
        <Heading
          as="h3"
          sx={{
            pb: '0.5rem',
            borderBottom: '1px solid',
            borderBottomColor: 'grey.3',
          }}
        >
          <Flex
            sx={{
              justifyContent: 'space-between',
              alignItems: 'flex-start',
            }}
          >
            <Box sx={{ p: '0.5rem' }}>{title}</Box>
            <Button
              variant="close"
              onClick={handleClose}
              tabIndex={0}
              sx={{ flex: '0 0 auto', margin: '0' }}
            >
              <TimesCircle size="1.5em" />
            </Button>
          </Flex>
        </Heading>

        <Box sx={{ px: '0.5rem', py: '1rem' }}>{children}</Box>
      </Box>
    </Flex>,
    document.body
  )
}

Modal.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  onClose: PropTypes.func.isRequired,
  width: PropTypes.string,
}

Modal.defaultProps = {
  width: '500px',
}

export default Modal
