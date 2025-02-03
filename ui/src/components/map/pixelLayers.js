import {
  blueprint,
  blueprintCategories,
  corridors,
  ecosystems,
  indicatorsIndex,
  urban,
  slrDepth,
  slrNodata,
  wildfireRisk,
  ownership,
  protection,
} from 'config'
import { indexBy, sortByFunc } from 'util/data'

import { tileHost } from './mapConfig'

const pixelLayerSourceConfig = { tileSize: 512, minzoom: 3, maxzoom: 14 }

// Encoding values are set from `data/for_tiles/se_pixel_layers_<n>.json
export const pixelLayers = [
  {
    ...pixelLayerSourceConfig,
    id: 'pixels0',
    url: `${tileHost}/services/se_pixel_layers_0/tiles/{z}/{x}/{y}.png`,
    bounds: [-108.0227, 16.97285, -57.03082, 41.58111],
    encoding: [
      { id: 'blueprint', offset: 0, bits: 3, valueShift: 1 },
      { id: 'corridors', offset: 3, bits: 2, valueShift: 1 },
      { id: 'urban', offset: 5, bits: 3, valueShift: 0 },
      { id: 'slr', offset: 8, bits: 4, valueShift: 1 },
      {
        id: 'f_imperiledaquaticspecies',
        offset: 12,
        bits: 4,
        valueShift: 1,
      },
      { id: 'f_networkcomplexity', offset: 16, bits: 4, valueShift: 1 },
      {
        id: 't_resilientterrestrialsites',
        offset: 20,
        bits: 4,
        valueShift: 1,
      },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels1',
    url: `${tileHost}/services/se_pixel_layers_1/tiles/{z}/{x}/{y}.png`,
    bounds: [-108.0227, 23.73322, -74.0301, 41.58035],
    encoding: [
      {
        id: 'f_naturallandcoverinfloodplains',
        offset: 0,
        bits: 3,
        valueShift: 1,
      },
      { id: 'f_permeablesurface', offset: 3, bits: 3, valueShift: 0 },
      {
        id: 't_equitableaccesstopotentialparks',
        offset: 6,
        bits: 3,
        valueShift: 1,
      },
      { id: 't_firefrequency', offset: 9, bits: 3, valueShift: 1 },
      { id: 't_intacthabitatcores', offset: 12, bits: 3, valueShift: 1 },
      { id: 't_landscapecondition', offset: 15, bits: 3, valueShift: 0 },
      { id: 't_playas', offset: 18, bits: 3, valueShift: 1 },
      { id: 't_urbanparksize', offset: 21, bits: 3, valueShift: 1 },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels2',
    url: `${tileHost}/services/se_pixel_layers_2/tiles/{z}/{x}/{y}.png`,
    // bounds: [-104.02594, 25.61165, -88.12292, 37.43785],
    bounds: [-98.53344, 22.37943, -70.38168, 40.66711],
    encoding: [
      {
        id: 'f_atlanticmigratoryfishhabitat',
        offset: 0,
        bits: 4,
        valueShift: 1,
      },
      { id: 'm_atlanticmarinebirds', offset: 4, bits: 4, valueShift: 1 },
      { id: 'm_islandhabitat', offset: 8, bits: 2, valueShift: 1 },
      {
        id: 'm_marinehighlymigratoryfish',
        offset: 10,
        bits: 4,
        valueShift: 0,
      },
      { id: 'm_southatlanticbeachbirds', offset: 14, bits: 3, valueShift: 1 },
      {
        id: 'm_southatlanticmaritimeforest',
        offset: 17,
        bits: 2,
        valueShift: 1,
      },
      {
        id: 't_southatlanticforestbirds',
        offset: 19,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 't_southatlanticlowurbanhistoriclandscapes',
        offset: 22,
        bits: 2,
        valueShift: 1,
      },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels3',
    url: `${tileHost}/services/se_pixel_layers_3/tiles/{z}/{x}/{y}.png`,
    bounds: [-108.0227, 22.4353, -70.06457, 41.58092],
    encoding: [
      {
        id: 'm_atlanticcoralandhardbottom',
        offset: 0,
        bits: 4,
        valueShift: 1,
      },
      {
        id: 'm_atlanticdeepseacoralrichness',
        offset: 4,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'm_atlanticestuarinefishhabitat',
        offset: 7,
        bits: 4,
        valueShift: 1,
      },
      { id: 'm_atlanticmarinemammals', offset: 11, bits: 4, valueShift: 1 },
      { id: 'm_resilientcoastalsites', offset: 15, bits: 3, valueShift: 0 },
      { id: 'm_seagrass', offset: 18, bits: 2, valueShift: 0 },
      { id: 'm_stablecoastalwetlands', offset: 20, bits: 2, valueShift: 1 },
      {
        id: 't_amphibianandreptileareas',
        offset: 22,
        bits: 2,
        valueShift: 1,
      },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels4',
    url: `${tileHost}/services/se_pixel_layers_4/tiles/{z}/{x}/{y}.png`,
    bounds: [-108.0227, 23.78806, -74.172, 41.58053],
    encoding: [
      { id: 't_grasslandsandsavannas', offset: 0, bits: 4, valueShift: 1 },
      { id: 't_greenwaysandtrails', offset: 4, bits: 4, valueShift: 1 },
      {
        id: 't_mississippialluvialvalleyforestbirdsprotection',
        offset: 8,
        bits: 4,
        valueShift: 1,
      },
      {
        id: 't_mississippialluvialvalleyforestbirdsreforestation',
        offset: 12,
        bits: 4,
        valueShift: 1,
      },
      {
        id: 't_westcoastalplainandouachitasforestedwetlandbirds',
        offset: 16,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 't_westcoastalplainandouachitasopenpinebirds',
        offset: 19,
        bits: 3,
        valueShift: 1,
      },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels5',
    url: `${tileHost}/services/se_pixel_layers_5/tiles/{z}/{x}/{y}.png`,
    bounds: [-98.26575, 17.10476, -57.73155, 40.36863],
    encoding: [
      {
        id: 'm_coastalshorelinecondition',
        offset: 0,
        bits: 3,
        valueShift: 1,
      },
      { id: 'm_gulfcoralandhardbottom', offset: 3, bits: 4, valueShift: 1 },
      { id: 'm_gulfdeepseacoralrichness', offset: 7, bits: 3, valueShift: 0 },
      { id: 'm_gulfmarinemammals', offset: 10, bits: 4, valueShift: 1 },
      { id: 'm_gulfseaturtles', offset: 14, bits: 3, valueShift: 1 },
      {
        id: 't_caribbeangreenwaysandtrails',
        offset: 17,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 't_westgulfcoastmottledducknesting',
        offset: 20,
        bits: 4,
        valueShift: 1,
      },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels6',
    url: `${tileHost}/services/se_pixel_layers_6/tiles/{z}/{x}/{y}.png`,
    bounds: [-67.97848, 16.97285, -64.29697, 19.34715],
    encoding: [
      {
        id: 'f_caribbeannaturallandcoverinfloodplains',
        offset: 0,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'f_caribbeannetworkcomplexity',
        offset: 3,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'f_caribbeanpermeablesurface',
        offset: 6,
        bits: 3,
        valueShift: 0,
      },
      { id: 'm_caribbeanbeachhabitat', offset: 9, bits: 2, valueShift: 1 },
      {
        id: 'm_caribbeancoastalshorelinecondition',
        offset: 11,
        bits: 2,
        valueShift: 1,
      },
      { id: 'm_caribbeanfishhotspots', offset: 13, bits: 3, valueShift: 1 },
      {
        id: 'm_caribbeanfishnurseryhabitat',
        offset: 16,
        bits: 2,
        valueShift: 1,
      },
      { id: 'm_caribbeanseagrass', offset: 18, bits: 3, valueShift: 1 },
      {
        id: 'm_caribbeanshallowhardbottomandcoral',
        offset: 21,
        bits: 3,
        valueShift: 1,
      },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels7',
    url: `${tileHost}/services/se_pixel_layers_7/tiles/{z}/{x}/{y}.png`,
    bounds: [-67.97848, 16.97285, -64.29697, 19.34715],
    encoding: [
      {
        id: 't_caribbeanhabitatpatchsizelargeislands',
        offset: 0,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 't_caribbeanhabitatpatchsizesmallislands',
        offset: 3,
        bits: 3,
        valueShift: 1,
      },
      { id: 't_caribbeanislandhabitat', offset: 6, bits: 4, valueShift: 1 },
      { id: 't_caribbeankarsthabitat', offset: 10, bits: 3, valueShift: 1 },
      {
        id: 't_caribbeanlandscapecondition',
        offset: 13,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 't_caribbeanlowurbanhistoriclandscapes',
        offset: 16,
        bits: 2,
        valueShift: 1,
      },
      {
        id: 't_caribbeanreforestationpotential',
        offset: 18,
        bits: 3,
        valueShift: 1,
      },
      { id: 't_caribbeanurbanparksize', offset: 21, bits: 3, valueShift: 1 },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels8',
    url: `${tileHost}/services/se_pixel_layers_8/tiles/{z}/{x}/{y}.png`,
    bounds: [-108.0227, 16.98923, -57.08541, 41.58111],
    encoding: [
      { id: 'wildfireRisk', offset: 0, bits: 4, valueShift: 1 },
      { id: 'ownership', offset: 4, bits: 4, valueShift: 0 },
      { id: 'protection', offset: 8, bits: 3, valueShift: 0 },
      {
        id: 'f_gulfmigratoryfishconnectivity',
        offset: 11,
        bits: 2,
        valueShift: 1,
      },
      {
        id: 'm_estuarinecoastalcondition',
        offset: 13,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 't_eastcoastalplainopenpinebirds',
        offset: 16,
        bits: 3,
        valueShift: 1,
      },
    ],
  },
]

// create index of encoded layers
export const pixelLayerIndex = {}
pixelLayers.forEach(({ encoding }, textureIndex) => {
  encoding.forEach(({ id, bits, offset, valueShift }) => {
    pixelLayerIndex[id] = { textureIndex, bits, offset, valueShift }
  })
})

const coreLayers = [
  {
    id: 'blueprint',
    label: 'Blueprint priority',
    valueLabel: 'for a connected network of lands and waters', // used in legend
    // sort colors in ascending value; blueprint is in descending order
    colors: blueprint
      .map(({ color, value }) => (value === 0 ? null : color))
      .reverse(),
    categories: blueprintCategories,
    layer: pixelLayerIndex.blueprint,
  },
  {
    id: 'corridors',
    label: 'Hubs and corridors',
    colors: corridors
      .slice()
      .sort(sortByFunc('value'))
      .map(({ color }) => color),
    categories: corridors
      .filter(({ value }) => value > 0)
      .map(({ value, label, color }) => ({
        value,
        label,
        color,
        type: 'fill',
      })),
    layer: pixelLayerIndex.corridors,
  },
]

const otherInfoLayers = [
  {
    id: 'urban',
    label: 'Probability of urbanization by 2060',
    colors: urban.map(({ color }) => color),
    categories: urban.map(({ color, ...rest }) => ({
      ...rest,
      color: color || '#FFFFFF',
      outlineWidth: 1,
      outlineColor: 'grey.5',
    })),
    layer: pixelLayerIndex.urban,
  },
  {
    id: 'slr',
    label: 'Flooding extent by projected sea-level rise',
    colors: slrDepth.concat(slrNodata).map(({ color }) => color),
    categories: slrDepth
      .concat(slrNodata.filter(({ value }) => value !== 13))
      .map(({ label, ...rest }, i) => ({
        ...rest,
        label:
          /* eslint-disable-next-line no-nested-ternary */
          i === 1 ? `${label} foot` : i <= 10 ? `${label} feet` : label,
        outlineWidth: 1,
        outlineColor: 'grey.5',
      })),
    layer: pixelLayerIndex.slr,
  },
  {
    id: 'wildfireRisk',
    label: 'Wildfire likelihood (annual burn probability)',
    colors: wildfireRisk.map(({ color }) => color),
    // sort in descending order
    // NOTE: this uses a custom legend for simple label values, not the full
    // set of categories
    categories: Object.values(
      Object.fromEntries(
        wildfireRisk
          .map(({ label, color, ...rest }) => ({
            label: label.split(' (')[0],
            color: color || '#FFFFFF',
            outlineWidth: 1,
            outlineColor: 'grey.5',
            ...rest,
          }))
          .map((item) => [item.label, item])
          .reverse()
      )
    ),
    layer: pixelLayerIndex.wildfireRisk,
  },
  {
    id: 'ownership',
    label: 'Conserved lands ownership',
    colors: ownership.map(({ color }) => color),
    categories: ownership
      .filter(({ color }) => color !== null)
      .map(({ code, ...rest }) => ({ ...rest, value: code })),
    layer: pixelLayerIndex.ownership,
  },
  {
    id: 'protection',
    label: 'Protection status',
    colors: protection.map(({ color }) => color),
    categories: protection
      .filter(({ color }) => color !== null)
      .map(({ code, ...rest }) => ({ ...rest, value: code })),
    layer: pixelLayerIndex.protection,
  },
]

const layers = coreLayers.concat(otherInfoLayers)

export const renderLayerGroups = [
  {
    id: 'core',
    label: 'Priorities',
    layers: coreLayers,
  },
]

ecosystems.forEach(
  ({ id: groupId, label: groupLabel, indicators: groupIndicators }) => {
    const group = {
      id: groupId,
      label: `${groupLabel} indicators`,
      layers: groupIndicators.map((id) => {
        const { label, values, valueLabel } = indicatorsIndex[id]
        return {
          id,
          label,
          colors: values.map(({ color }) => color),
          categories: values.filter(({ color }) => color !== null).reverse(),
          valueLabel,
          layer: pixelLayerIndex[id],
        }
      }),
    }

    renderLayerGroups.push(group)
    layers.push(...group.layers)
  }
)

renderLayerGroups.push({
  id: 'otherInfo',
  label: 'More information',
  layers: otherInfoLayers,
})

export const renderLayersIndex = indexBy(layers, 'id')
