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
      { id: 'blueprint', position: 0, offset: 0, bits: 3, valueShift: 1 },
      { id: 'corridors', position: 1, offset: 3, bits: 3, valueShift: 1 },
      { id: 'urban', position: 2, offset: 6, bits: 3, valueShift: 1 },
      { id: 'slr', position: 3, offset: 9, bits: 4, valueShift: 1 },
      {
        id: 'base:freshwater_imperiledaquaticspecies',
        position: 4,
        offset: 13,
        bits: 4,
        valueShift: 1,
      },
      {
        id: 'base:land_intacthabitatcores',
        position: 5,
        offset: 17,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'base:land_resilientterrestrialsites',
        position: 6,
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
    encoding: [
      {
        id: 'base:freshwater_naturallandcoverinfloodplains',
        position: 0,
        offset: 0,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:freshwater_networkcomplexity',
        position: 1,
        offset: 3,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:freshwater_permeablesurface',
        position: 2,
        offset: 6,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:land_equitableaccesstopotentialparks',
        position: 3,
        offset: 9,
        bits: 2,
        valueShift: 0,
      },
      {
        id: 'base:land_firefrequency',
        position: 4,
        offset: 11,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'base:land_greenwaysandtrails',
        position: 5,
        offset: 14,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:land_saamphibianandreptileareas',
        position: 6,
        offset: 17,
        bits: 2,
        valueShift: 1,
      },
      {
        id: 'base:land_salowurbanhistoric',
        position: 7,
        offset: 19,
        bits: 2,
        valueShift: 1,
      },
      {
        id: 'base:land_urbanparksize',
        position: 8,
        offset: 21,
        bits: 3,
        valueShift: 0,
      },
    ],
  },
  {
    ...pixelLayerSourceConfig,
    id: 'pixels2',
    url: `${tileHost}/services/se_pixel_layers_2/tiles/{z}/{x}/{y}.png`,
    encoding: [
      {
        id: 'base:freshwater_wvimperiledaquaticspecies',
        position: 0,
        offset: 0,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'base:land_eastcoastalplainopenpinebirds',
        position: 1,
        offset: 3,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:marine_coastalshorelinecondition',
        position: 2,
        offset: 6,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'base:marine_estuarinecoastalcondition',
        position: 3,
        offset: 9,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:marine_islands',
        position: 4,
        offset: 12,
        bits: 2,
        valueShift: 0,
      },
      {
        id: 'base:marine_resilientcoastalsites',
        position: 5,
        offset: 14,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:marine_seagrasses',
        position: 6,
        offset: 17,
        bits: 2,
        valueShift: 0,
      },
      {
        id: 'base:marine_sabeachbirds',
        position: 7,
        offset: 19,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:marine_stablecoastalwetlands',
        position: 8,
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
        position: 0,
        offset: 0,
        bits: 2,
        valueShift: 0,
      },
      {
        id: 'base:land_mavforestbirds_protection',
        position: 1,
        offset: 2,
        bits: 4,
        valueShift: 0,
      },
      {
        id: 'base:land_mavforestbirds_reforestation',
        position: 2,
        offset: 6,
        bits: 4,
        valueShift: 0,
      },
      {
        id: 'base:land_playas',
        position: 3,
        offset: 10,
        bits: 2,
        valueShift: 0,
      },
      {
        id: 'base:land_wcpforestedwetlandbirds',
        position: 4,
        offset: 12,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:land_wcpopenpinebirds',
        position: 5,
        offset: 15,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'base:land_wgcmottledducknesting',
        position: 6,
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
      {
        id: 'base:freshwater_atlanticmigratoryfishhabitat',
        position: 0,
        offset: 0,
        bits: 4,
        valueShift: 1,
      },
      {
        id: 'base:land_saforestbirds',
        position: 1,
        offset: 4,
        bits: 3,
        valueShift: 1,
      },
      {
        id: 'base:marine_atlanticestuarinefishhabitat',
        position: 2,
        offset: 7,
        bits: 4,
        valueShift: 1,
      },
      {
        id: 'base:marine_sahardbottomanddeepseacoral',
        position: 3,
        offset: 11,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:marine_samarinebirds',
        position: 4,
        offset: 14,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:marine_samammals',
        position: 5,
        offset: 17,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:marine_samaritimeforest',
        position: 6,
        offset: 20,
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
        position: 0,
        offset: 0,
        bits: 3,
        valueShift: 0,
      },
      {
        id: 'base:land_interiorsoutheastgrasslands',
        position: 1,
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
