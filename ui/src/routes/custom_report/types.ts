export interface StateType {
	reportURL: string | null
	status: string | null
	progress: number
	queuePosition?: number
	elapsedTime?: number | null
	message?: string | null
	errors?: string[] | null // non-fatal errors
	inProgress: boolean | null
	error?: string | null // if error is non-null, it indicates there was an error
}

export interface UploadResultType {
	error?: string
	result?: string
	errors?: string[]
}

export interface ProgressCallbackType {
	status: string
	progress: number
	queuePosition?: number
	elapsedTime?: number
	message: string | null
	errors: string[] | null
}
