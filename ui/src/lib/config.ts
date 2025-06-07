import { indexBy } from '$lib/util/data';

import rawBlueprint from '../../../constants/blueprint.json';
import rawCorridors from '../../../constants/corridors.json';
import ecosystems from '../../../constants/ecosystems.json';
import rawIndicators from '../../../constants/indicators.json';
import protectedAreas from '../../../constants/protected_areas.json';
import rawSLR from '../../../constants/slr.json';
import subregions from '../../../constants/subregions.json';
import urban from '../../../constants/urban.json';
import wildfireRisk from '../../../constants/wildfire_risk.json';

// export unmodified values directly
export { ecosystems, protectedAreas, subregions, urban, wildfireRisk };

// Sort by descending value
export const blueprint = rawBlueprint.sort(({ value: leftValue }, { value: rightValue }) =>
	rightValue > leftValue ? 1 : -1
);
// skip the first value
export const blueprintCategories = blueprint.slice(0, blueprint.length - 1);

// put 0 value at end
export const corridors = rawCorridors.slice(1).concat(rawCorridors.slice(0, 1));

// select subset of fields and add position within list
export const indicators = rawIndicators.map(
	(
		{
			id,
			label,
			url,
			description,
			goodThreshold,
			values,
			valueLabel,
			subregions: indicatorSubregions
		},
		i
	) => ({
		id,
		label,
		url,
		description,
		goodThreshold,
		values,
		valueLabel,
		subregions: new Set(indicatorSubregions),
		pos: i // position within list of indicators, used to unpack packed indicator values
	})
);

export const indicatorsIndex = indexBy(indicators, 'id');

// split depth and NODATA values
export const slrDepth = rawSLR.slice(0, 11);
export const slrNodata = rawSLR.slice(11);

export const subregionIndex = indexBy(subregions, 'value');
