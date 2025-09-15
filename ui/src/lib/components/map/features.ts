import camelCase from 'camelcase'

import {
	applyFactor,
	parsePipeEncodedValues,
	parseDeltaEncodedValues,
	parseDictEncodedValues,
	indexBy,
	setIntersection,
	sum
} from '$lib/util/data'
import type { IndicatorValue } from '$lib/types'

/**
 * Return true if text is null or an empty string or single quote.
 * @param {String} text
 */
const isEmpty = (text: string | null) => {
	if (!text) {
		return true
	}
	if (text === '"') {
		return true
	}

	return false
}

/**
 * Extract dictionary-encoded counts and means
 * @param {Object} packedPercents
 * @param {Array} ecosystemInfo - array of ecosystem info
 * @param {Array} indicatorInfo - array of indicator info
 * @param {Array} subregions - array of subregion names
 */
const extractIndicators = (
	packedPercents: string,
	ecosystemInfo,
	indicatorInfo,
	subregions: Set<string>
) => {
	const ecosystemIndex = indexBy(ecosystemInfo, 'id')

	// merge incoming packed percents with indicator info
	let indicators = indicatorInfo
		// only show indicators that are either present or likely present based on
		// subregion
		.filter(({ subregions: indicatorSubregions }: { subregions: Set<string> }, i: number) => {
			const present = !!packedPercents[i]

			return present || setIntersection(indicatorSubregions, subregions).size > 0
		})
		.map(
			({
				id,
				pos,
				values: valuesInfo,
				...indicator
			}: {
				id: string
				pos: number
				values: IndicatorValue[]
			}) => {
				const present = !!packedPercents[pos]

				const percents = present ? applyFactor(packedPercents[pos], 0.1) : []

				// merge percent into values
				const values = valuesInfo.map((value, j) => ({
					...value,
					percent: present ? percents[j] : 0
				}))

				return {
					percent: percents,
					...indicator,
					id,
					values,
					total: Math.min(sum(percents), 100),
					ecosystem: ecosystemIndex[id.split('_')[0]]
				}
			}
		)

	// aggregate these up by ecosystems for ecosystems that are present
	const ecosystemsPresent = new Set(
		indicators
			.filter(
				({ values }: { values: [{ percent: number }] }) =>
					sum(values.map(({ percent }) => percent)) > 0
			)
			.map(({ ecosystem: { id } }: { ecosystem: { id: string } }) => id)
	)

	indicators = indexBy(indicators, 'id')

	const ecosystems = ecosystemInfo
		.filter(({ id }) => ecosystemsPresent.has(id))
		.map(
			({
				id: ecosystemId,
				label,
				color,
				borderColor,
				indicators: ecosystemIndicators,
				...rest
			}) => {
				const indicatorsPresent = ecosystemIndicators.filter(
					(indicatorId) => indicators[indicatorId]
				)

				return {
					...rest,
					id: ecosystemId,
					label,
					color,
					borderColor,
					indicators: indicatorsPresent.map((indicatorId) => ({
						...indicators[indicatorId]
					}))
				}
			}
		)

	return { ecosystems, indicators }
}

/**
 * Unpack encoded attributes in feature data.
 * @param {Object} properties
 * @param {Array} ecosystemInfo - array of ecosystem info
 * @param {Array} indicatorInfo - array of indicator info
 * @param {Object} subregionIndex - lookup of subregions by value
 */
export const unpackFeatureData = (
	properties: object,
	ecosystemInfo,
	indicatorInfo,
	subregionIndex
) => {
	const values = Object.entries(properties)
		.map(([rawKey, value]) => {
			const key = camelCase(rawKey)

			if (!value || typeof value !== 'string' || key === 'name') {
				return [key, value]
			}

			if (isEmpty(value)) {
				return [key, null]
			}

			if (key === 'protectedAreasList') {
				return [key, value ? value.split('|') : []]
			}

			if (value.indexOf('^') !== -1) {
				return [key, parseDeltaEncodedValues(value)]
			}
			if (value.indexOf(':') !== -1) {
				return [key, parseDictEncodedValues(value)]
			}
			if (value.indexOf('|') !== -1) {
				return [key, parsePipeEncodedValues(value)]
			}

			// everything else
			return [key, value]
		})
		.reduce((prev, [key, value]) => {
			// eslint-disable-next-line no-param-reassign
			prev[key] = value
			return prev
		}, {})

	// calculate area outside SE, rounded to 0 in case it is very small
	values.outsideSEPercent = (100 * values.outsideSe) / values.rasterizedAcres
	if (values.outsideSEPercent < 1) {
		values.outsideSEPercent = 0
	}

	// rescale scaled values from percent * 10 back to percent
	const scaledColumns = [
		'blueprint',
		'corridors',
		'protectedAreas',
		'slrDepth',
		'slrNodata',
		'urban',
		'wildfireRisk'
	]
	scaledColumns.forEach((c) => {
		values[c] = values[c] ? applyFactor(values[c], 0.1) : []
	})

	const subregions = new Set<string>()
	const regions = new Set<string>()

	if (values.subregions) {
		values.subregions.split(',').forEach((v: string) => {
			const { subregion, region } = subregionIndex[v]
			subregions.add(subregion)
			regions.add(region)
		})
	}
	values.subregions = subregions
	values.regions = regions

	values.indicators = extractIndicators(
		values.indicators || {},
		ecosystemInfo,
		indicatorInfo,
		values.subregions
	)

	// rename specific fields for easier use later
	values.unitType = values.type
	values.unitAcres = values.acres

	values.slr = {
		depth: values.slrDepth || [],
		nodata: values.slrNodata || []
	}

	return values
}
