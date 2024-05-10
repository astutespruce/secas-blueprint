import {
  blueprint,
  blueprintCategories,
  corridors,
  ecosystems,
  indicatorsIndex,
  urban,
  slrDepth,
  slrNodata,
} from 'config'
import { indexBy, sortByFunc } from 'util/data'

import { siteMetadata } from '../../../gatsby-config'

const { tileHost } = siteMetadata

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
      { id: 'corridors', offset: 3, bits: 3, valueShift: 1 },
      { id: 'urban', offset: 6, bits: 3, valueShift: 0 },
      { id: 'slr', offset: 9, bits: 4, valueShift: 1 },
      { id: 't_firefrequency', offset: 13, bits: 3, valueShift: 1 },
      { id: 't_greenwaysandtrails', offset: 16, bits: 4, valueShift: 1 },
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
    bounds: [-108.0227, 23.78806, -74.172, 41.58053],
    encoding: [
      {
        id: 'f_imperiledaquaticspecies',
        offset: 0,
        bits: 4,
        valueShift: 1,
      },
      {
        id: 'f_naturallandcoverinfloodplains',
        offset: 4,
        bits: 3,
        valueShift: 1,
      },
      { id: 'f_networkcomplexity', offset: 7, bits: 4, valueShift: 1 },
      { id: 'f_permeablesurface', offset: 11, bits: 3, valueShift: 0 },
      {
        id: 't_equitableaccesstopotentialparks',
        offset: 14,
        bits: 3,
        valueShift: 1,
      },
      { id: 't_intacthabitatcores', offset: 17, bits: 3, valueShift: 1 },
      { id: 't_urbanparksize', offset: 20, bits: 3, valueShift: 1 },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels2',
    url: `${tileHost}/services/se_pixel_layers_2/tiles/{z}/{x}/{y}.png`,
    bounds: [-104.02594, 25.61165, -88.12292, 37.43785],
    encoding: [
      {
        id: 't_greatplainsperennialgrasslands',
        offset: 0,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 't_mississippialluvialvalleyforestbirdsprotection',
        offset: 3,
        bits: 4,
        valueShift: 1,
      },
      {
        id: 't_mississippialluvialvalleyforestbirdsreforestation',
        offset: 7,
        bits: 4,
        valueShift: 1,
      },
      { id: 't_playas', offset: 11, bits: 3, valueShift: 1 },
      {
        id: 't_westcoastalplainandouachitasforestedwetlandbirds',
        offset: 14,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 't_westcoastalplainandouachitasopenpinebirds',
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
    id: 'pixels3',
    url: `${tileHost}/services/se_pixel_layers_3/tiles/{z}/{x}/{y}.png`,
    bounds: [-96.19012, 23.87306, -74.14382, 41.58098],
    encoding: [
      {
        id: 'f_atlanticmigratoryfishhabitat',
        offset: 0,
        bits: 4,
        valueShift: 1,
      },
      {
        id: 'f_westvirginiaimperiledaquaticspecies',
        offset: 4,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'm_atlanticestuarinefishhabitat',
        offset: 7,
        bits: 4,
        valueShift: 1,
      },
      {
        id: 't_eastcoastalplainopenpinebirds',
        offset: 11,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 't_interiorsoutheastgrasslands',
        offset: 14,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 't_southatlanticamphibianandreptileareas',
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
    id: 'pixels4',
    url: `${tileHost}/services/se_pixel_layers_4/tiles/{z}/{x}/{y}.png`,
    bounds: [-98.78124, 22.37943, -70.45039, 40.46617],
    encoding: [
      {
        id: 'm_coastalshorelinecondition',
        offset: 0,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'm_estuarinecoastalcondition',
        offset: 3,
        bits: 3,
        valueShift: 1,
      },
      { id: 'm_islandhabitat', offset: 6, bits: 2, valueShift: 1 },
      {
        id: 'm_marinehighlymigratoryfish',
        offset: 8,
        bits: 4,
        valueShift: 0,
      },
      { id: 'm_resilientcoastalsites', offset: 12, bits: 3, valueShift: 0 },
      { id: 'm_seagrass', offset: 15, bits: 2, valueShift: 0 },
      {
        id: 'm_southatlanticbeachbirds',
        offset: 17,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'm_southatlanticmaritimeforest',
        offset: 20,
        bits: 2,
        valueShift: 1,
      },
      { id: 'm_stablecoastalwetlands', offset: 22, bits: 2, valueShift: 1 },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels5',
    url: `${tileHost}/services/se_pixel_layers_5/tiles/{z}/{x}/{y}.png`,
    bounds: [-98.58603, 16.97285, -59.75763, 35.67848],
    encoding: [
      {
        id: 'f_gulfmigratoryfishconnectivity',
        offset: 0,
        bits: 2,
        valueShift: 1,
      },
      { id: 'm_gulfcoralandhardbottom', offset: 2, bits: 3, valueShift: 1 },
      {
        id: 'm_gulfdeepseacoralrichness',
        offset: 5,
        bits: 3,
        valueShift: 0,
      },
      { id: 'm_gulfmarinemammals', offset: 8, bits: 4, valueShift: 1 },
      { id: 'm_gulfseaturtles', offset: 12, bits: 3, valueShift: 1 },
      { id: 't_caribbeanurbanparksize', offset: 15, bits: 3, valueShift: 1 },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels6',
    url: `${tileHost}/services/se_pixel_layers_6/tiles/{z}/{x}/{y}.png`,
    bounds: [-84.0406, 22.37943, -70.45003, 39.62234],
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
      { id: 'm_atlanticmarinebirds', offset: 7, bits: 4, valueShift: 1 },
      { id: 'm_atlanticmarinemammals', offset: 11, bits: 4, valueShift: 1 },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels7',
    url: `${tileHost}/services/se_pixel_layers_7/tiles/{z}/{x}/{y}.png`,
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
    id: 'pixels8',
    url: `${tileHost}/services/se_pixel_layers_8/tiles/{z}/{x}/{y}.png`,
    bounds: [-67.97848, 16.97285, -64.29697, 19.34715],
    encoding: [
      {
        id: 't_caribbeangreenwaysandtrails',
        offset: 0,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 't_caribbeanhabitatpatchsizelargeislands',
        offset: 3,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 't_caribbeanhabitatpatchsizesmallislands',
        offset: 6,
        bits: 3,
        valueShift: 1,
      },
      { id: 't_caribbeanislandhabitat', offset: 9, bits: 4, valueShift: 1 },
      { id: 't_caribbeankarsthabitat', offset: 13, bits: 3, valueShift: 1 },
      {
        id: 't_caribbeanlandscapecondition',
        offset: 16,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 't_caribbeanlowurbanhistoriclandscapes',
        offset: 19,
        bits: 2,
        valueShift: 1,
      },
      {
        id: 't_caribbeanreforestationpotential',
        offset: 21,
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

const threatLayers = [
  {
    id: 'urban',
    label: 'Probability of urbanization by 2060',
    colors: urban.map(({ color }) => color),
    categories: urban.filter(({ color }) => color !== null),
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
]

const layers = coreLayers.concat(threatLayers)

export const renderLayerGroups = [
  {
    id: 'core',
    label: 'Priorities',
    layers: coreLayers,
  },
  {
    id: 'threats',
    label: 'Threats',
    layers: threatLayers,
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

export const renderLayersIndex = indexBy(layers, 'id')
