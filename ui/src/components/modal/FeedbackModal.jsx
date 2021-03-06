import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { OutboundLink } from 'components/link'
import BoundModal from './BoundModal'

const FeedbackModal = ({ children }) => (
  <BoundModal
    title="Give your feedback to Blueprint Staff"
    anchorNode={children}
  >
    <Text as="p">
      The Blueprint and its inputs are regularly revised based on input from
      people like you. Have a suggestion on how to improve the priorities? Let
      us know! We also welcome feedback on how to improve the Southeast
      Blueprint Explorer interface. Southeast Blueprint staff will read and
      respond to your comments&mdash;we promise.
      <br />
      <br />
      Please reach out to the user support contact{' '}
      <OutboundLink to="http://secassoutheast.org/contact">
        {' '}
        for your state
      </OutboundLink>
      .
    </Text>
  </BoundModal>
)

FeedbackModal.propTypes = {
  children: PropTypes.node.isRequired,
}

export default FeedbackModal
