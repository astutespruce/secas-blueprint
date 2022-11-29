import { siteMetadata } from '../../../gatsby-config'

const { tileHost } = siteMetadata

export const mapConfig = {
  bounds: [-106.66188036, 17.92676033, -65.22106481, 40.638801],

  // TEMP: testing only
  // bounds: [
  //   -82.60386551952661, 30.279148227225917, -81.30046782109937,
  //   31.25495730451503,
  // ],
  maxBounds: [-180, -80, 180, 80],
  minZoom: 3,
  maxZoom: 14,
}

export const sources = {
  blueprint: {
    type: 'raster',
    // tiles are at 512, but using 256 forces higher resolution
    tileSize: 256,
    minzoom: 3,
    maxzoom: 14,
    bounds: [-106.66188036, 17.92676033, -65.22106481, 40.638801],
    tiles: [`${tileHost}/services/se_blueprint_2022/tiles/{z}/{x}/{y}.png`],
  },
  mapUnits: {
    type: 'vector',
    minzoom: 3,
    maxzoom: 14,
    bounds: [-106.66188036, 17.92676033, -65.22106481, 40.6388013],
    tiles: [`${tileHost}/services/se_map_units/tiles/{z}/{x}/{y}.pbf`],
    // note: can use promoteId: 'id' to promote feature properties ID to feature ID
    promoteId: 'id',
  },
  ownership: {
    type: 'vector',
    minzoom: 3,
    maxzoom: 14,
    bounds: [-86.470357, 27.546173, -70.816397, 38.932193],
    tiles: [`${tileHost}/services/se_ownership/tiles/{z}/{x}/{y}.pbf`],
  },
}

export const layers = [
  // ownership is added with no fill in order to detect ownership types for pixel mode
  {
    id: 'ownership',
    source: 'ownership',
    'source-layer': 'ownership',
    type: 'fill',
    layout: {
      visibility: 'none',
    },
    paint: {
      'fill-color': '#FFF',
      'fill-opacity': 0,
    },
  },
  {
    id: 'blueprint',
    source: 'blueprint',
    type: 'raster',
    minzoom: 3,
    maxzoom: 21,
    paint: {
      'raster-opacity': {
        stops: [
          [10, 0.8],
          [12, 0.6],
        ],
      },
    },
  },
  {
    id: 'se-boundary-outline',
    source: 'mapUnits',
    'source-layer': 'boundary',
    minzoom: 3,
    maxzoom: 21,
    type: 'line',
    paint: {
      'line-color': '#000',
      'line-width': {
        stops: [
          [6, 1],
          [8, 0.1],
        ],
      },
    },
  },

  {
    id: 'unit-fill',
    source: 'mapUnits',
    'source-layer': 'units',
    minzoom: 8,
    type: 'fill',
    paint: {
      'fill-color': '#0892D0',
      'fill-opacity': [
        'case',
        ['boolean', ['feature-state', 'highlight'], false],
        0.3,
        0,
      ],
    },
  },
  {
    id: 'unit-outline',
    source: 'mapUnits',
    'source-layer': 'units',
    minzoom: 8,
    type: 'line',
    paint: {
      'line-opacity': 1,
      'line-color': '#000',
      'line-width': [
        'interpolate',
        ['linear'],
        ['zoom'],
        8,
        0.25,
        10,
        1,
        13,
        4,
      ],
    },
  },
  {
    id: 'unit-outline-highlight',
    source: 'mapUnits',
    'source-layer': 'units',
    type: 'line',
    filter: ['==', 'id', Infinity],
    paint: {
      'line-opacity': 1,
      'line-color': '#000000',
      'line-width': {
        stops: [
          [8, 3],
          [12, 6],
        ],
      },
    },
  },
]
