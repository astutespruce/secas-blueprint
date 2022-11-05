import React from 'react'
import PropTypes from 'prop-types'
import { Paragraph } from 'theme-ui'

import { OutboundLink } from 'components/link'

import BoundModal from './BoundModal'

const ContactModal = ({ children }) => (
  <BoundModal title="Contact Us" anchorNode={children}>
    <Paragraph>
      Do you have a question about the Blueprint? Would you like help using the
      Blueprint to support a proposal or inform a decision? Southeast Blueprint
      staff are here to support you! We really mean it. It is what we do!
      <br />
      <br />
      Please reach out to the user support contact{' '}
      <OutboundLink to="http://secassoutheast.org/staff">
        {' '}
        for your state
      </OutboundLink>
      .
    </Paragraph>
  </BoundModal>
)

ContactModal.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ContactModal
