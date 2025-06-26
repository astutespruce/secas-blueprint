import * as Sentry from '@sentry/svelte'
import { browser } from '$app/environment'
import { SENTRY_DSN } from '$lib/env'

export const prerender = true
export const ssr = false

if (browser && typeof SENTRY_DSN !== 'undefined') {
	Sentry.init({
		dsn: SENTRY_DSN,
		denyUrls: [
			// Chrome extensions
			/extensions\//i,
			/^chrome:\/\//i,
			/^chrome-extension:\/\//i
		]
	})
	// @ts-ignore
	window.Sentry = Sentry
}
