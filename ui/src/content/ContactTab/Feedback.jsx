import React from 'react'

import { formatPhone } from 'util/format'
import { siteMetadata } from '../../../gatsby-config'

const { contactEmail, contactPhone, title } = siteMetadata

const Feedback = () => {
  return (
    <p>
      The Blueprint and indicators are regularly revised based on input from
      people like you. Have a suggestion on how to improve the priorities? Let
      us know! We also welcome feedback on how to improve the Southeast
      Blueprint Explorer interface. Southeast Blueprint staff will read and
      respond to your comments&mdash;we promise.
      <br />
      <br />
      <b>email</b>{' '}
      <a
        href={`mailto:${contactEmail}?subject=${title} Feedback (Simple Viewer)`}
        target="_blank"
        rel="noopener noreferrer"
      >
        {contactEmail}
      </a>
      <br />
      <b>call</b>{' '}
      <a href={`tel:${contactPhone}`}>{formatPhone(contactPhone)}</a>
    </p>
  )
}

export default Feedback
