<script lang="ts">
	import { fromEvent as getFilesFromEvent } from 'file-selector'
	import { superForm, fileProxy, defaults } from 'sveltekit-superforms'
	import { zod4, zod4Client } from 'sveltekit-superforms/adapters'
	import { z } from 'zod'

	import ZipFileIcon from '~icons/fa-solid/file-archive'
	import ExclamationTriangle from '~icons/fa-solid/exclamation-triangle'
	import UploadIcon from '~icons/fa-solid/upload'
	import { cn } from '$lib/utils.js'
	import { Field, Control, Label, Button as SubmitButton } from '$lib/components/ui/form'
	import { RadioGroup, RadioGroupItem } from '$lib/components/ui/radio-group'
	import { Button } from '$lib/components/ui/button'
	import { Input } from '$lib/components/ui/input'
	import { ContactDialog } from '$lib/components/dialog'

	const MAXSIZE_MB = 100
	const MIME_TYPES = new Set([
		'application/zip',
		'application/x-zip-compressed',
		'application/x-compressed',
		'multipart/x-zip'
	])

	const { onSubmit } = $props()
	let isDragValid: boolean | null = $state(null)
	const schema = z.object({
		areaName: z.string().default('').optional(),
		reportType: z.enum(['pdf', 'xlsx']),
		file: z
			.instanceof(File, {
				error: 'Please select a file'
			})
			.refine((f) => f.size < MAXSIZE_MB * 1e6, `File must be less than ${MAXSIZE_MB} MB`)
			.refine(({ type: mimeType }) => MIME_TYPES.has(mimeType), 'File must be a ZIP file')
	})

	const form = superForm(defaults(zod4(schema)), {
		SPA: true,
		validators: zod4Client(schema),
		onUpdate: function ({ form }) {
			const {
				valid,
				data: { areaName = '', file, reportType }
			} = form

			if (!valid) {
				return
			}

			onSubmit(reportType, areaName, file)
		}
	})

	const { form: formData, enhance, errors, validate } = form
	const fileHandle = fileProxy(formData, 'file')

	const handleDragOver = async (e: DragEvent) => {
		e.preventDefault()
		e.stopPropagation()

		const hasFiles =
			e.dataTransfer &&
			Array.prototype.some.call(
				e.dataTransfer.types,
				(type) => type === 'Files' || type === 'application/x-moz-file'
			)

		if (hasFiles) {
			const files = await getFilesFromEvent(e)
			const [file] = files
			// cannot check file size here, it isn't always defined on file
			isDragValid = files.length === 1 && MIME_TYPES.has(file.type)
		}
	}

	const handleDragOut = (e: DragEvent) => {
		e.preventDefault()
		isDragValid = null
	}

	const handleDrop = async (e: DragEvent) => {
		e.preventDefault()
		isDragValid = null

		const hasFiles =
			e.dataTransfer &&
			Array.prototype.some.call(
				e.dataTransfer.types,
				(type) => type === 'Files' || type === 'application/x-moz-file'
			)

		if (hasFiles) {
			const files = await getFilesFromEvent(e)
			const [file] = files

			if (files.length > 1) {
				alert('Multiple files not allowed')
				return
			}

			fileHandle.set(file as File)
			await validate('file')
		}
	}

	const handleResetFile = async () => {
		form.reset({
			newState: {
				areaName: $formData.areaName
			}
		})
	}

	const handleDropZoneClick = () => {
		const fileInputNode = document.getElementById('file')
		if (fileInputNode) {
			fileInputNode.click()
		}
	}

	const handleDropZoneKeyDown = ({ key }: KeyboardEvent) => {
		const fileInputNode = document.getElementById('file')
		if (fileInputNode && key === 'Enter') {
			fileInputNode.click()
		}
	}

	const isFileValid = $derived($formData.file && !$errors.file)
	const isValid = $derived(isFileValid && !$errors.areaName)
</script>

<div class="container text-lg pt-6 pb-16 leading-snug">
	<p>
		Upload a zipped shapefile or ESRI File Geodatabase Feature Class containing your area of
		interest to generate a detailed PDF or XLSX report of the Blueprint, underlying indicators, and
		other contextual information for your area of interest. The PDF report includes a map and
		summary table for every indicator present in the area, as well as additional information about
		urbanization and sea-level rise. The XLSX report includes detailed statistics for each of the
		analysis units in your area of interest dataset, for all datasets that you choose to include in
		your analysis.
	</p>

	<hr />

	<form enctype="multipart/form-data" use:enhance class="grid sm:grid-cols-2 gap-16">
		<div>
			<Field {form} name="areaName">
				<Control>
					{#snippet children({ props })}
						<Label for="areaName" class="text-2xl font-bold">Area Name (optional):</Label>
						<Input {...props} bind:value={$formData.areaName} class="mt-2" />
					{/snippet}
				</Control>
			</Field>

			<Field {form} name="file" class="mt-6">
				<Control>
					{#snippet children({ props })}
						<Label
							for="file"
							class="block"
							ondragover={handleDragOver}
							ondrop={handleDrop}
							ondragleave={handleDragOut}
						>
							<div class="text-2xl font-bold">Area of Interest:</div>
							<Input
								type="file"
								{...props}
								id="file"
								bind:files={$fileHandle}
								accept={[...MIME_TYPES].join(',')}
								multiple={false}
								class="mt-2 hidden"
							/>
							<div
								class={cn(
									'border-2 border-grey-8/50 rounded-lg bg-grey-1/40 border-dashed p-6 flex flex-col justify-center cursor-pointer mt-2',
									{
										'border-error': isDragValid === false || $errors.file,
										'bg-error/10': isDragValid === false || $errors.file,
										'cursor-not-allowed': isDragValid === false,
										'border-ok': isDragValid === true,
										'bg-ok/10': isDragValid === true,
										hidden: isFileValid
									}
								)}
								onclick={handleDropZoneClick}
								onkeydown={handleDropZoneKeyDown}
								role="button"
								aria-label="Click to browse for files or drop file over this area"
								tabindex={0}
							>
								<div class="flex gap-2 items-center">
									<ZipFileIcon class="size-6 flex-none" aria-hidden="true" />
									<div class="text-2xl font-bold">Drop your zip file here</div>
								</div>

								<p class="text-base text-grey-8 leading-tight mt-4">
									Your zip file must contain all associated files for a shapefile (at least .shp,
									.prj, .shx) or file geodatabase (.gdb).
									<br />
									<br />
									Max size: {MAXSIZE_MB} MB.
								</p>
							</div>

							{#if isFileValid}
								<div class="text-lg">
									Selected: {$formData.file.name}
								</div>
							{/if}
						</Label>

						{#if $errors.file}
							<div class="flex items-center gap-2 text-accent ml-2 mt-4 mb-8">
								<ExclamationTriangle width="1em" height="1em" />
								{$errors.file}
							</div>
						{/if}
					{/snippet}
				</Control>

				{#if isFileValid}
					<div class="flex justify-center mt-8">
						<Button onclick={handleResetFile} variant="destructive" class="text-base"
							>Choose a different file</Button
						>
					</div>
				{:else}
					<p class="text-sm text-grey-8 mx-4">
						Note: your files must be in a zip file, and can include only one shapefile or Feature
						Class, and should represent a relatively small area. For help analyzing larger areas,
						please <ContactDialog>
							<span class="text-link hover:underline cursor-pointer"> contact us</span>
						</ContactDialog>.
					</p>
				{/if}
			</Field>
		</div>
		<div>
			<Field {form} name="reportType">
				<div class="text-2xl font-bold">Report Type:</div>
				<Control>
					{#snippet children({ props })}
						<RadioGroup
							{...props}
							bind:value={$formData.reportType}
							class="space-y-4 [&_label]:text-base [&_label]:cursor-pointer [&>label]:flex [&>label]:gap-2"
						>
							<label for="reportType-pdf">
								<RadioGroupItem id="reportType-pdf" value="pdf" />
								<div class="-mt-1">
									<div class="font-bold">PDF</div>
									<div class="text-lg text-muted-foreground leading-tight">
										Create a detailed report including a map and summary table for every indicator
										present in the area as well as additional information about urbanization,
										sea-level rise, and more. All uploaded areas will be treated as a single area of
										interest.
									</div>
								</div>
							</label>

							<label for="reportType-xlsx" class="flex gap-2">
								<RadioGroupItem id="reportType-xlsx" value="xlsx" />
								<div class="-mt-1">
									<div class="font-bold">XLSX</div>
									<p class="text-lg text-muted-foreground leading-tight">
										Create a detailed data report including a summary table for each selected
										dataset present in your areas of interest. You can select the datasets you are
										interested in for your report. You can choose to treat each area you upload as
										an individual area of interest for reporting results.
									</p>
								</div>
							</label>
						</RadioGroup>
					{/snippet}
				</Control>
			</Field>
			<div class="flex justify-end mt-8">
				<SubmitButton disabled={!isValid} class="text-xl gap-2">
					<UploadIcon class="size-5" /> Upload file
				</SubmitButton>
			</div>
		</div>
	</form>

	<hr />

	<div>
		<p>
			Don't have a shapefile? You can create one using
			<a href="https://geojson.io/" target="_blank"> geojson.io </a>
			to draw your area of interest, save as a shapefile, then upload here.
			<br />
			<br />
			<ContactDialog>
				<span class="text-link hover:underline cursor-pointer">We are here</span>
			</ContactDialog>
			to help you interpret and apply this information to your particular application!
			<br />
			<br />
			We are working on resolving some technical challenges to make these these automatically generated
			reports more accessible to people with disabilities. In the meantime, to request an accessible PDF
			or other assistance, please contact Hilary Morris at
			<a href="mailto:hilary_morris@fws.gov"> hilary_morris@fws.gov </a>.
			<br />
			<br />
			You can help us improve the Blueprint and this report by helping us understand your use case: we
			use this information to provide statistics about how the Blueprint is being used and to prioritize
			improvements.
		</p>
	</div>

	<hr />

	<h2 class="text-2xl">Examples of what is inside</h2>

	{#if $formData.reportType === 'pdf'}
		<div class="grid grid-cols-2 md:grid-cols-5 mt-2 gap-4 [&_img]:border [&_img]:border-grey-2">
			<enhanced:img
				src="$images/report/report_sm_1.png"
				alt="Tool report example screenshot 1"
				loading="lazy"
			/>
			<enhanced:img
				src="$images/report/report_sm_2.png"
				alt="Tool report example screenshot 2"
				loading="lazy"
			/>
			<enhanced:img
				src="$images/report/report_sm_3.png"
				alt="Tool report example screenshot 3"
				loading="lazy"
			/>
			<enhanced:img
				src="$images/report/report_sm_4.png"
				alt="Tool report example screenshot 4"
				loading="lazy"
			/>
			<enhanced:img
				src="$images/report/report_sm_5.png"
				alt="Tool report example screenshot 5"
				loading="lazy"
			/>
		</div>
		<p class="mt-2 text-lg">...and much more!</p>
	{/if}
</div>
