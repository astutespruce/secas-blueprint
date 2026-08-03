<script lang="ts">
	import { Footer, Header } from '$lib/components/layout'
</script>

<svelte:head>
	<title>How to use the Blueprint Explorer</title>
</svelte:head>

<Header />
<main class="h-full w-full flex-auto overflow-auto">
	<div class="relative z-0 w-full overflow-hidden h-60">
		<div class="z-1 absolute top-[-50%]">
			<enhanced:img
				src="$images/26871026541_48a8096dd9_o.jpg"
				class="h-auto min-w-[720px] object-cover brightness-60"
				alt=""
				fetchpriority="high"
			/>
		</div>
		<div class="container mt-14">
			<h1 class="text-7xl relative text-white z-2 text-shadow-sm text-shadow-black">
				How to use this viewer
			</h1>
		</div>
	</div>
	<div class="text-sm text-grey-8 text-right pr-1">
		Photo: Black Skimmers, <a
			href="https://www.flickr.com/photos/usfwssoutheast/26871026541/"
			target="_blank"
			tabindex="-1"
			class="text-grey-8">U.S. Fish and Wildlife Service Southeast Region</a
		>
	</div>

	<div class="container text-lg pt-4 pb-16 [&_img]:border [&_img]:border-grey-2">
		<h2 class="text-4xl">Summarize data:</h2>
		<p class="pt-2">
			This mode allows you to select a subwatershed or marine hexagon and view data summaries and
			charts for the Blueprint, indicators, threats, and protected areas.
		</p>

		<div class="mt-8 grid grid-cols-0 md:grid-cols-2 gap-8">
			<div class="flex flex-col justify-center">
				<p>
					Choose <b>Summarize data</b> from the button bar above the map. Click on any subwatershed or
					marine hexagon for details. You may need to zoom in to select an area.
				</p>
			</div>
			<div>
				<enhanced:img src="$images/help-summarize.png" alt="Shows summarize data button" />
			</div>
		</div>

		<div class="mt-16 grid grid-cols-0 md:grid-cols-[1fr_1.5fr] gap-8">
			<div>
				<enhanced:img
					src="$images/help-summarize-tabs.png"
					alt="Shows tabs in sidebar for a selected summary unit"
				/>
			</div>
			<div class="flex flex-col justify-center">
				<p>
					Use the tabs in the sidebar to navigate the different types of summary information
					available for priorities, indicators, threats, and partners.
					<br />
					<br />
					The indicators tab shows which indicators are present in the selected summary unit. Click on
					an indicator for more information and to see the range of values that occur that area.
				</p>
			</div>
		</div>

		<p class="mt-16">
			You can download a detailed PDF report of the Blueprint, hubs and corridors, underlying
			indicators, and landscape-level threats for the selected summary unit. Click the
			<b>Export detailed maps and analysis</b> link below the area name. To unselect the area, click
			the <b>X</b> in the upper right of the sidebar.
		</p>

		<hr />

		<h2 class="text-4xl">View point data:</h2>
		<p class="mt-2">
			This mode allows you to show values at a specific point for the Blueprint, indicators,
			threats, and more by drilling into a single 30 meter pixel, the smallest unit of the Blueprint
			analysis.
		</p>

		<div class="grid grid-cols-0 md:grid-cols-2 gap-8 mt-16">
			<div class="flex-col justify-center">
				<p>
					Choose <b>View point data</b> from the button bar above the map. The crosshairs in the
					center of the map will pinpoint a specific place and show details for that location in the
					sidebar.
					<br />
					<br />
					<br />
					You may have to zoom in for the crosshairs to appear. Zoom in further to choose a more precise
					location, especially in areas that are highly pixelated.
				</p>
			</div>
			<div>
				<enhanced:img
					src="$images/help-point-data.png"
					alt="Shows point data mode"
					loading="lazy"
				/>
			</div>
		</div>

		<div class="grid grid-cols-0 md:grid-cols-[1fr_2fr] mt-16 gap-8">
			<div>
				<enhanced:img
					src="$images/help-point-data-tabs.png"
					alt="Shows tabs when viewing point data"
					loading="lazy"
				/>
			</div>
			<div class="flex flex-col justify-center">
				<p>
					Use the tabs in the sidebar to navigate the different types of point-level information
					available for priorities, indicators, threats, and partners.
					<br />
					<br />
					The indicators tab shows the pixel value for each indicator present at that point. Click on
					an indicator for more information about it.
				</p>
			</div>
		</div>

		<p class="mt-16">
			Note: this approach uses pixels that have been resampled and reprojected for each zoom level.
			This means that the values shown in the tool may not exactly match the Blueprint and indicator
			data for that specific ground location, especially in areas of high variability in the data.
			<br />
			<br />
			To view and / or download more precise spatial data, please visit the
			<a href="https://secas-fws.hub.arcgis.com/pages/blueprint" target="_blank">
				Blueprint page of the SECAS Atlas
			</a>
		</p>

		<hr />

		<h2 class="text-4xl">Filter the Blueprint:</h2>
		<p class="mt-2">
			Filters can help you find the part of the Blueprint that aligns with your mission, interests,
			or specific question. Use the filters to show areas on the map that fall within a range of
			values for one or more layers, including the Blueprint, hubs and corridors, underlying
			indicators, and threats.
		</p>

		<div class="grid grid-cols-0 md:grid-cols-2 gap-8 mt-16">
			<div class="flex flex-col justify-center">
				<p>
					Choose <b>Filter the Blueprint</b> from the button bar above the map.
					<br />
					<br />
					Click the checkbox for a given layer to enable it for filtering the map. Use the next level
					of checkboxes to select the specific values that you want to display.
				</p>
			</div>
			<div>
				<enhanced:img
					src="$images/help-filter.png"
					alt="Shows filtering the Blueprint"
					loading="lazy"
				/>
			</div>
		</div>

		<p class="mt-16">
			You can select more than one layer. By default, filters are evaluated using AND logic, which
			means that in order for a pixel to display on the map, it must meet all the selected criteria.
			If you filter by layers that do not co-occur at the same location, such as estuarine coastal
			condition and playas, nothing will display on the map.
		</p>

		<div class="grid grid-cols-0 md:grid-cols-2 gap-8 mt-16">
			<div>
				<enhanced:img
					src="$images/help-filter-before.png"
					alt="Shows filtering the Blueprint showing before filters are applied"
					loading="lazy"
				/>
			</div>
			<div>
				<enhanced:img
					src="$images/help-filter-after.png"
					alt="Shows filtering the Blueprint showing after filters are applied"
					loading="lazy"
				/>
			</div>
		</div>

		<p class="mt-16">
			Alternatively, you can use OR logic to select all areas where any of your selected criteria
			are present.
			<br /><br />
			Use the <b>Change filter overlay method</b> dropdown to change the logic being applied to your filters.
			This can be especially helpful for identifying areas across indicators that do not spatially co-occur.
			This mode starts from a blank map, and adds areas as you specify filters.
		</p>

		<div class="grid grid-cols-0 md:grid-cols-[1fr_2fr] gap-8 mt-16">
			<div>
				<enhanced:img
					src="$images/help-filter-mode.png"
					alt="Shows dropdown to select filter mode"
					loading="lazy"
				/>
			</div>
			<div>
				<figure>
					<enhanced:img
						src="$images/help-filter-OR-after.png"
						alt="Shows filtering the Blueprint with OR filter logic applied to indicators that do not co-occur"
						loading="lazy"
					/>
					<figcaption class="text-sm text-muted-foreground">
						Example showing OR logic applied to two indicators that do not spatially co-occur.
					</figcaption>
				</figure>
			</div>
		</div>

		<p class="mt-8">
			Note: pixel filters may take a few moments to display within your browser, especially as you
			pan or zoom the map. You may need to zoom in to see areas that meet your filters.
		</p>

		<div class="grid grid-cols-0 md:grid-cols-[2fr_1fr] gap-8 mt-16">
			<p>
				You can save a PDF with a snapshot of your filtered map and information about the filters
				you've selected using the <b>Print / save map to PDF</b> button. This will use your
				browser's print dialog, where you can choose PDF as an option.
				<br /><br />
				The map snapshot is based on the dimensions of your browser window and view of the map that is
				currently visible in your browser window. You may need to adjust the map or the size of your browser
				window to better focus on your area of interest.
			</p>
			<div>
				<enhanced:img
					src="$images/help-filter-print-1.png"
					alt="Filtered map print button"
					loading="lazy"
				/>
			</div>
		</div>

		<div class="grid grid-cols-0 md:grid-cols-[2fr_1fr] gap-8 mt-16">
			<div>
				<enhanced:img
					src="$images/help-filter-print-2.png"
					alt="Browser print dialog"
					loading="lazy"
				/>
			</div>
			<div>
				<figure>
					<enhanced:img
						src="$images/help-filter-print-3.png"
						alt="Shows second page of filter PDF"
						loading="lazy"
					/>
					<figcaption class="text-sm text-muted-foreground">
						Example of information about active filters saved in the PDF.
					</figcaption>
				</figure>
			</div>
		</div>

		<p class="mt-8">
			Note: this PDF file is intended to help save information about your active filters for later
			reference. It is entirely different from the data-rich PDF reports you can create by selecting
			a watershed or by uploading a shapefile, which include maps of the Blueprint and all
			indicators present in your area of interest.
		</p>

		<hr />

		<h2 class="text-4xl">Create a custom report for a specific area of interest:</h2>
		<p class="mt-2">
			Click on the <b>Upload a shapefile</b> button in the upper right. You will be able to upload
			your area of interest and create a detailed PDF report of the Blueprint, hubs and corridors,
			underlying indicators, and landscape-level threats in that area.
			<br />
			<br />
			Examples of what is inside:
		</p>

		<div class="grid grid-cols-2 md:grid-cols-5 mt-2 gap-4">
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

		<hr />

		<h2 class="text-4xl">Display different map layers:</h2>
		<p class="mt-2">
			You can display map layers other than the Blueprint. Choose
			<b>View point data</b> or <b>Filter the Blueprint</b> from the button bar above the map, and then
			click the button in the upper right of the map to display the list of available layers.
		</p>

		<div class="grid grid-cols-0 md:grid-cols-[1.5fr_1fr] gap-8 mt-16">
			<div>
				<enhanced:img
					src="$images/help-toggle-layers-button.png"
					alt="Shows toggle layers button"
					loading="lazy"
				/>
			</div>
			<div>
				<enhanced:img
					src="$images/help-toggle-layers-modal.png"
					alt="Shows toggle layers modal popup"
					loading="lazy"
				/>
			</div>
		</div>

		<hr />

		<h2 class="text-4xl">Find a specific location:</h2>
		<p class="mt-2">
			You can use the search bar in the upper right of the map to search by place name, address, or
			latitude and longitude coordinates.
		</p>

		<div class="grid gap-8 mt-16 grid-cols-[2fr_1fr_1.5fr]">
			<div class="flex flex-col justify-center">
				<p>
					Click in the search field to expand it. Use the dropdown on the left of the search bar to
					switch between search by placename and search by latitude and longitude.
				</p>
			</div>
			<div>
				<enhanced:img src="$images/help-search-field.png" alt="Shows search field" loading="lazy" />
			</div>
			<div>
				<enhanced:img
					src="$images/help-search-options.png"
					alt="Shows search field options"
					loading="lazy"
				/>
			</div>
		</div>

		<div class="grid grid-cols-0 md:grid-cols-3 gap-8 mt-16">
			<div class="flex flex-col justify-center">
				<p>
					You can search by place name or address, or enter latitude and longitude coordinates
					directly.
					<br />
					<br />
					Once you have selected a location from the list of results, or clicked the <b>Go</b> button
					for latitude and longitude, it will show a marker at that location on the map.
				</p>
			</div>
			<div>
				<enhanced:img
					src="$images/help-search-results.png"
					alt="Shows search results for placename search"
					loading="lazy"
				/>
			</div>
			<div>
				<enhanced:img
					src="$images/help-search-lat-long.png"
					alt="Shows latitude / longitude search"
					loading="lazy"
				/>
			</div>
		</div>
		<p class="mt-2">
			To remove the marker, click the <b>X</b> in the search field to clear the search.
		</p>
	</div>
</main>
<Footer />
