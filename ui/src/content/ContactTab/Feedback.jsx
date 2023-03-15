import React from 'react'

import { Paragraph } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Feedback = () => (
  <Paragraph>
    The Blueprint and its inputs are regularly revised based on input from
    people like you. Have a suggestion on how to improve the priorities? Let us
    know! We also welcome feedback on how to improve the Southeast Blueprint
    Explorer interface. Southeast Blueprint staff will read and respond to your
    comments&mdash;we promise.
    <br />
    <br />
    Please reach out to{' '}
    <OutboundLink to="http://secassoutheast.org/staff">
      Blueprint user support staff
    </OutboundLink>
    .
  </Paragraph>
)

export default Feedback
