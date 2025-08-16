/* eslint-disable no-console */
import * as Sentry from '@sentry/browser'

import { hasWindow } from './dom'

export const captureException = (err: Error | string, data: object | null = null) => {
	// @ts-ignore
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

export const logGAEvent = (event: string, data: object | null = null) => {
	// NOTE: window.gtag only available in build mode
	// @ts-ignore
	if (!hasWindow || !window.gtag) {
		return
	}

	try {
		// @ts-ignore
		window.gtag('event', event, data)
	} catch (ex) {
		console.error('Could not log event to google', ex)
	}
}
