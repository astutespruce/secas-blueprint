<script lang="ts">
	import { uploadFile } from '$lib/api'
	import { captureException, logGAEvent } from '$lib/util/log'
	import Done from './Done.svelte'
	import UploadError from './UploadError.svelte'
	import Progress from './Progress.svelte'
	import Queued from './Queued.svelte'
	import UploadForm from './UploadForm.svelte'
	import type { StateType, UploadResultType, ProgressCallbackType } from './types'

	const initState: StateType = {
		reportURL: null,
		status: null,
		progress: 0,
		queuePosition: 0,
		elapsedTime: null,
		message: null,
		errors: null, // non-fatal errors reported to user
		inProgress: false,
		error: null // if error is non-null, it indicates there was an error
	}

	let state: StateType = $state(initState)

	const handleUpload = async (areaName: string, file: File) => {
		console.log('do upload', areaName, file)

		state = {
			...state,
			inProgress: true,
			progress: 0,
			queuePosition: 0,
			elapsedTime: null,
			message: null,
			errors: null,
			error: null,
			reportURL: null
		}

		logGAEvent('create-custom-report', {
			name: areaName,
			file: file.name,
			sizeKB: file.size / 1024
		})

		try {
			// upload file and update progress
			const {
				error: uploadError,
				result,
				errors: finalErrors
			}: UploadResultType = await uploadFile(
				file,
				areaName,
				({
					status: nextStatus,
					progress: nextProgress,
					queuePosition: nextQueuePosition,
					elapsedTime: nextElapsedTime,
					message: nextMessage = null,
					errors: nextErrors = null
				}: ProgressCallbackType) => {
					state = {
						...state,
						status: nextStatus,
						inProgress:
							nextStatus === 'in_progress' ||
							(nextStatus === 'queued' && nextElapsedTime !== undefined && nextElapsedTime < 5),
						progress: nextProgress,
						queuePosition: nextQueuePosition,
						elapsedTime: nextElapsedTime,
						message: nextMessage || state.message,
						errors: nextErrors || state.errors
					}
				}
			)

			if (uploadError) {
				// eslint-disable-next-line no-console
				console.error(uploadError)

				state = {
					...state,
					inProgress: false,
					status: null,
					progress: 0,
					queuePosition: 0,
					elapsedTime: null,
					message: null,
					errors: null,
					error: uploadError,
					reportURL: null
				}

				logGAEvent('file-upload-error')

				return
			}

			// upload and processing completed successfully
			state = {
				...state,
				status: null,
				progress: 100,
				queuePosition: 0,
				elapsedTime: null,
				message: null,
				errors: finalErrors, // there may be non-fatal errors (e.g., errors rendering maps)
				inProgress: false,
				reportURL: result as string
			}

			window.location.href = result as string
		} catch (ex) {
			captureException('File upload failed', ex)
			// eslint-disable-next-line no-console
			console.error('Caught unhandled error from uploadFile', ex)

			state = {
				...state,
				inProgress: false,
				status: null,
				progress: 0,
				queuePosition: 0,
				elapsedTime: null,
				message: null,
				errors: null,
				error: '', // no meaningful error to show to user, but needs to be non-null}
				reportURL: null
			}
		}
	}

	const handleReset = () => {
		state = initState
	}
</script>

<svelte:head>
	<title>Create a custom Blueprint report</title>
</svelte:head>

<svelte:document
	ondragover={(e) => {
		e.preventDefault()
	}}
	ondrop={(e) => {
		e.preventDefault()
	}}
/>

<div class="relative z-0 w-full overflow-hidden h-56">
	<div class="z-1 absolute top-[-20%]">
		<enhanced:img
			src="$images/26871026541_48a8096dd9_o.jpg"
			class="h-auto min-w-[720px] object-cover brightness-60"
			alt=""
		/>
	</div>
	<div class="container mt-14">
		<h1 class="text-7xl relative text-white z-2 text-shadow-sm text-shadow-black">
			Create a custom Blueprint report
		</h1>
	</div>
</div>
<div class="text-sm text-grey-8 text-right pr-1">
	Photo: Black Skimmers, <a
		href="https://www.flickr.com/photos/usfwssoutheast/26871026541/"
		target="_blank"
		class="text-grey-8">U.S. Fish and Wildlife Service Southeast Region</a
	>
</div>

{#if state.error !== null}
	<UploadError error={state.error} onReset={handleReset} />
{:else if state.reportURL !== null}
	<Done reportURL={state.reportURL} errors={state.errors} onReset={handleReset} />
{:else if state.inProgress}
	<Progress message={state.message} progress={state.progress} />
{:else if state.status === 'queued'}
	<Queued
		message={state.message}
		queuePosition={state.queuePosition}
		elapsedTime={state.elapsedTime}
	/>
{:else}
	<UploadForm onSubmit={handleUpload} />
{/if}
