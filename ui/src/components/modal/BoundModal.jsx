import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import Modal from './Modal'

const BoundModal = ({ anchorNode, children, title }) => {
  const [isOpen, setIsOpen] = useState(false)

  const handleOpen = useCallback(() => {
    setIsOpen(() => true)
  }, [])

  const handleClose = useCallback(() => {
    setIsOpen(() => false)
  }, [])

  return (
    <>
      <Box
        as="span"
        onClick={handleOpen}
        onKeyPress={handleOpen}
        role="button"
        aria-label={`toggle button for ${title} popup`}
        sx={{
          // allow focus for LayerToggle
          '&:focus .map-button': {
            boxShadow: '0 0 2px 2px #0096ff',
          },
        }}
        tabIndex={0}
      >
        {anchorNode}
      </Box>

      {isOpen ? (
        <Modal title={title} onClose={handleClose}>
          {children}
        </Modal>
      ) : null}
    </>
  )
}

BoundModal.propTypes = {
  title: PropTypes.string.isRequired,
  anchorNode: PropTypes.node.isRequired,
  children: PropTypes.node.isRequired,
}

export default BoundModal
