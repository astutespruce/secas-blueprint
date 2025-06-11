<script>
	import { base } from '$app/paths';

	import FileUpload from '~icons/fa-solid/file-upload';
	import QuestionCircle from '~icons/fa-solid/question-circle';

	// TODO: fetch mobile state, mapdata state from context
</script>

<header class="flex-none leading-none drop-shadow-md drop-shadow-black z-10">
	<!-- desktop header -->
	<div class="hidden sm:flex flex-auto justify-between items-center gap-3 pl-2 pr-4 py-1">
		<a href={`${base}/`} class="lg:flex gap-1.5 flex-wrap items-center hover:no-underline">
			<h1 class="m-0 leading-none text-[1rem] lg:text-2xl">Southeast</h1>
			<h1 class="m-0 text-2xl leading-none">Conservation Blueprint Explorer</h1>
		</a>
		<div class="flex-none flex gap-3 lg:gap-5">
			<a
				href="/help"
				target="_blank"
				class="flex gap-1.5 items-center flex-none font-bold text-md bg-transparent hover:bg-black/20 hover:no-underline px-2 py-1.5 border border-white cursor-pointer rounded-sm hover"
			>
				<QuestionCircle />
				<div class="hidden lg:block">How to use this viewer</div>
			</a>

			<a
				href="/custom_report"
				class="flex gap-1.5 items-center flex-none font-bold text-md bg-transparent hover:bg-black/20 hover:no-underline px-2 py-1.5 border border-white cursor-pointer rounded-sm"
			>
				<FileUpload />
				Upload a shapefile
			</a>
		</div>
	</div>

	<!-- mobile header -->
	<div class="flex sm:hidden">TODO: mobile header</div>
</header>

<style>
	header {
		background-color: #4279a6;
		color: #fff;
		/* border-bottom: 2px solid #444; */

		a {
			color: #fff;
		}
	}
</style>
