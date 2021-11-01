import React from 'react'

import { OutboundLink } from 'components/link'

const Feedback = () => (
  <p>
    The Blueprint and its inputs are regularly revised based on input from
    people like you. Have a suggestion on how to improve the priorities? Let us
    know! We also welcome feedback on how to improve the Southeast Blueprint
    Explorer interface. Southeast Blueprint staff will read and respond to your
    comments&mdash;we promise.
    <br />
    <br />
    Please reach out to the user support contact{' '}
    <OutboundLink to="http://secassoutheast.org/staff">
      {' '}
      for your state
    </OutboundLink>
    .
  </p>
)

export default Feedback
