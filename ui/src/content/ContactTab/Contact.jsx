import React from 'react'

import { formatPhone } from 'util/format'
import { siteMetadata } from '../../../gatsby-config'

const { contactEmail, contactPhone, title } = siteMetadata

const Contact = () => {
  return (
    <p>
      Do you have a question about the Blueprint? Would you like help using the
      Blueprint to support a proposal or inform a decision? Southeast Blueprint
      staff are here to support you! We really mean it. It is what we do!
      <br />
      <br />
      <b>email</b>{' '}
      <a
        href={`mailto:${contactEmail}?subject=${title} Support (Simple Viewer)`}
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

export default Contact
