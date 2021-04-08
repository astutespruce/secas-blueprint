import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'

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
      <span onClick={handleOpen}>{anchorNode}</span>

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
