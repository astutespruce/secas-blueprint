import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { formatPhone } from 'util/format'
import BoundModal from './BoundModal'

import { siteMetadata } from '../../../gatsby-config'

const { contactEmail, contactPhone, title } = siteMetadata

const ReportProblemModal = ({ children }) => (
  <BoundModal title="Report a Problem" anchorNode={children}>
    <Text as="p">
      Did you encounter an error while using this application? Do you see a
      problem with the Blueprint priorities or indicator areas?
      <br />
      <br />
      We want to hear from you!
      <br />
      <br />
      <b>email</b>{' '}
      <a
        href={`mailto:${contactEmail}?subject=${title} Support (SE Blueprint Explorer) - report a problem`}
        target="_blank"
        rel="noopener noreferrer"
      >
        {contactEmail}
      </a>
      <br />
      <b>call</b>{' '}
      <a href={`tel:${contactPhone}`}>{formatPhone(contactPhone)}</a>
    </Text>
  </BoundModal>
)

ReportProblemModal.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ReportProblemModal
