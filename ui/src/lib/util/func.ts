/**
 * Call a function after a delay
 * @param f - function to call
 * @param delay - delay time, in milliseconds
 */
// adapted from https://stackoverflow.com/a/79329336
export function debounce<T>(f: (...args: T[]) => any, delay: number) {
	let id: ReturnType<typeof setTimeout>

	return (...args: T[]) => {
		if (id) {
			clearTimeout(id)
		}
		id = setTimeout(() => {
			f(...args)
		}, delay)
	}
}

export const eventHandler = (delay: number) => {
	let onceCallback: Function | null = null

	const once = (callback: Function) => {
		// ignore any prior callbacks
		console.log('once called')
		onceCallback = callback
	}

	const handler = debounce(() => {
		console.log('debounce ended')
		if (onceCallback) {
			console.log('once callback called')
			onceCallback()
			onceCallback = null
		}
	}, delay)

	return {
		once,
		handler
	}
}
