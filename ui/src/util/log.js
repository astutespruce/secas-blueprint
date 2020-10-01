/* eslint-disable no-console */
import * as Sentry from '@sentry/browser'

import { hasWindow } from './dom'

export const captureException = (err, data) => {
  if (hasWindow && window.Sentry) {
    Sentry.withScope((scope) => {
      // capture location where error occurred
      scope.setFingerprint([window.location.pathname])
      if (data) {
        scope.setExtra('data', data)
      }
      Sentry.captureException(err)
    })
  }
}
