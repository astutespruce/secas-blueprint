export const hasWindow = typeof window !== 'undefined' && window

export const hasGeolocation = hasWindow && navigator && 'geolocation' in navigator

export const saveToStorage = (key: string, data: object) => {
	if (!hasWindow) return

	window.localStorage.setItem(key, JSON.stringify(data))
}

export const getFromStorage = (key: string) => {
	if (!hasWindow) return null

	const value = window.localStorage.getItem(key)

	return value !== undefined && value !== null ? JSON.parse(value) : null
}
