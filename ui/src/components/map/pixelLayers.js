import { siteMetadata } from '../../../gatsby-config'

const { tileHost } = siteMetadata

const pixelLayerSourceConfig = { tileSize: 512, minzoom: 3, maxzoom: 14 }

// Encoding values are set from `data/for_tiles/se_pixel_layers_<n>.json
export const pixelLayers = [
  {
    ...pixelLayerSourceConfig,
    id: 'pixels0',
    url: `${tileHost}/services/se_pixel_layers_0/tiles/{z}/{x}/{y}.png`,
    encoding: [
      { id: 'blueprint', offset: 0, bits: 3, valueShift: 1 },
      { id: 'inland_corridors', offset: 3, bits: 2, valueShift: 1 },
      { id: 'urban', offset: 5, bits: 3, valueShift: 0 },
      { id: 'slr', offset: 8, bits: 4, valueShift: 1 },
      {
        id: 'base:freshwater_imperiledaquaticspecies',
        offset: 12,
        bits: 4,
        valueShift: 1,
      },
      {
        id: 'base:land_intacthabitatcores',
        offset: 16,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'base:land_resilientterrestrialsites',
        offset: 19,
        bits: 4,
        valueShift: 1,
      },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels1',
    url: `${tileHost}/services/se_pixel_layers_1/tiles/{z}/{x}/{y}.png`,
    encoding: [
      {
        id: 'base:freshwater_naturallandcoverinfloodplains',
        offset: 0,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:freshwater_networkcomplexity',
        offset: 3,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:freshwater_permeablesurface',
        offset: 6,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:land_equitableaccesstopotentialparks',
        offset: 9,
        bits: 2,
        valueShift: 0,
      },
      { id: 'base:land_firefrequency', offset: 11, bits: 3, valueShift: 1 },
      {
        id: 'base:land_greenwaysandtrails',
        offset: 14,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:land_saamphibianandreptileareas',
        offset: 17,
        bits: 2,
        valueShift: 1,
      },
      {
        id: 'base:land_salowurbanhistoric',
        offset: 19,
        bits: 2,
        valueShift: 1,
      },
      { id: 'base:land_urbanparksize', offset: 21, bits: 3, valueShift: 0 },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels2',
    url: `${tileHost}/services/se_pixel_layers_2/tiles/{z}/{x}/{y}.png`,
    encoding: [
      {
        id: 'base:freshwater_wvimperiledaquaticspecies',
        offset: 0,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'base:land_eastcoastalplainopenpinebirds',
        offset: 3,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:marine_coastalshorelinecondition',
        offset: 6,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'base:marine_estuarinecoastalcondition',
        offset: 9,
        bits: 3,
        valueShift: 0,
      },
      { id: 'base:marine_islands', offset: 12, bits: 2, valueShift: 0 },
      {
        id: 'base:marine_resilientcoastalsites',
        offset: 14,
        bits: 3,
        valueShift: 0,
      },
      { id: 'base:marine_seagrasses', offset: 17, bits: 2, valueShift: 0 },
      { id: 'base:marine_sabeachbirds', offset: 19, bits: 3, valueShift: 0 },
      {
        id: 'base:marine_stablecoastalwetlands',
        offset: 22,
        bits: 2,
        valueShift: 0,
      },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels3',
    url: `${tileHost}/services/se_pixel_layers_3/tiles/{z}/{x}/{y}.png`,
    encoding: [
      {
        id: 'base:freshwater_gulfmigratoryfishconnectivity',
        offset: 0,
        bits: 2,
        valueShift: 0,
      },
      {
        id: 'base:land_mavforestbirds_protection',
        offset: 2,
        bits: 4,
        valueShift: 0,
      },
      {
        id: 'base:land_mavforestbirds_reforestation',
        offset: 6,
        bits: 4,
        valueShift: 0,
      },
      { id: 'base:land_playas', offset: 10, bits: 2, valueShift: 0 },
      {
        id: 'base:land_wcpforestedwetlandbirds',
        offset: 12,
        bits: 3,
        valueShift: 0,
      },
      { id: 'base:land_wcpopenpinebirds', offset: 15, bits: 3, valueShift: 1 },
      {
        id: 'base:land_wgcmottledducknesting',
        offset: 18,
        bits: 4,
        valueShift: 0,
      },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels4',
    url: `${tileHost}/services/se_pixel_layers_4/tiles/{z}/{x}/{y}.png`,
    encoding: [
      { id: 'marine_corridors', offset: 0, bits: 2, valueShift: 1 },
      {
        id: 'base:freshwater_atlanticmigratoryfishhabitat',
        offset: 2,
        bits: 4,
        valueShift: 1,
      },
      { id: 'base:land_saforestbirds', offset: 6, bits: 3, valueShift: 1 },
      {
        id: 'base:marine_atlanticestuarinefishhabitat',
        offset: 9,
        bits: 4,
        valueShift: 1,
      },
      {
        id: 'base:marine_sahardbottomanddeepseacoral',
        offset: 13,
        bits: 3,
        valueShift: 0,
      },
      { id: 'base:marine_samarinebirds', offset: 16, bits: 3, valueShift: 0 },
      { id: 'base:marine_samammals', offset: 19, bits: 3, valueShift: 0 },
      {
        id: 'base:marine_samaritimeforest',
        offset: 22,
        bits: 2,
        valueShift: 0,
      },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels5',
    url: `${tileHost}/services/se_pixel_layers_5/tiles/{z}/{x}/{y}.png`,
    encoding: [
      {
        id: 'base:land_greatplainsperennialgrasslands',
        offset: 0,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:land_interiorsoutheastgrasslands',
        offset: 3,
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
