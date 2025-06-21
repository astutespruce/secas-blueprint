<script lang="ts">
	import { base } from '$app/paths'

	import FileUpload from '~icons/fa-solid/file-upload'
	import QuestionCircle from '~icons/fa-solid/question-circle'
	import { cn } from '$lib/utils'

	let { hasData = false } = $props()
</script>

<header
	class={cn(
		'flex-none leading-none drop-shadow-sm drop-shadow-black z-10000 bg-primary text-white',
		{
			'hidden md:block': hasData
		}
	)}
>
	<div class="sm:flex flex-auto justify-between items-center gap-3 pl-2 pr-4 py-1">
		<a
			href={`${base}/`}
			class="lg:flex gap-1.5 flex-wrap items-center hover:no-underline text-white hover:text-white"
		>
			<h1
				class="m-0 font-normal md:font-bold leading-none text-[0.8rem] md:text-[1rem] lg:text-2xl"
			>
				Southeast
			</h1>
			<h1 class="m-0 font-normal md:font-bold text-lg md:text-2xl leading-none">
				Conservation Blueprint Explorer
			</h1>
		</a>
		<div class="hidden flex-none md:flex gap-3 lg:gap-5">
			<a
				href="/help"
				target="_blank"
				class="flex gap-1.5 items-center flex-none font-bold text-md bg-transparent hover:bg-black/20 hover:no-underline px-2 py-1.5 border border-white cursor-pointer rounded-sm hover text-white"
			>
				<QuestionCircle />
				<div class="hidden lg:block">How to use this viewer</div>
			</a>

			<a
				href="/custom_report"
				class="flex gap-1.5 items-center flex-none font-bold text-md bg-transparent hover:bg-black/20 hover:no-underline px-2 py-1.5 border border-white cursor-pointer rounded-sm text-white"
			>
				<FileUpload />
				Upload a shapefile
			</a>
		</div>
	</div>
</header>
