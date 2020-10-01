import React, { useState, useCallback } from 'react'
import { Box, Button, Flex } from 'theme-ui'
import { FileAlt } from '@emotion-icons/fa-regular'

import { Link } from 'components/link'
import { Modal } from 'components/modal'
import { Feedback, Contact } from 'content/ContactTab'

const HeaderButtons = () => {
  const [activeModal, setActiveModal] = useState(null)

  const handleClose = useCallback(() => {
    setActiveModal(() => null)
  }, [])

  let modal = null
  if (activeModal === 'feedback') {
    modal = (
      <Modal
        title="Give your feedback to Blueprint staff"
        onClose={handleClose}
      >
        <Feedback />
      </Modal>
    )
  } else if (activeModal === 'contact') {
    modal = (
      <Modal
        title="Contact Blueprint staff for help using the Blueprint"
        onClose={handleClose}
      >
        <Contact />
      </Modal>
    )
  }

  return (
    <Flex sx={{ alignItems: 'center', flex: '0 0 auto' }}>
      <Link to="/custom_report">
        <Button
          variant="header"
          sx={{
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <FileAlt size="1em" />
          <Box
            sx={{ marginLeft: '0.5rem', display: ['none', 'none', 'block'] }}
          >
            Custom Report
          </Box>
        </Button>
      </Link>

      {modal}
    </Flex>
  )
}

export default HeaderButtons
