import { siteMetadata } from '../../../gatsby-config'

const { tileHost } = siteMetadata

export const config = {
  bounds: [-106.66188036, 17.92676033, -65.22106481, 40.638801],
  maxBounds: [-180, -80, 180, 80],
  minZoom: 0,
  maxZoom: 16,
}

export const sources = {
  blueprint: {
    type: 'raster',
    // tiles are at 512, but using 256 forces higher resolution
    tileSize: 256,
    minzoom: 0,
    maxzoom: 14,
    bounds: [-106.66188036, 17.92676033, -65.22106481, 40.638801],
    tiles: [`${tileHost}/services/southeast/blueprint_4/tiles/{z}/{x}/{y}.png`],
  },
  mapUnits: {
    type: 'vector',
    minzoom: 0,
    maxzoom: 14,
    bounds: [-106.66188036, 17.92676033, -65.22106481, 40.6388013],
    tiles: [`${tileHost}/services/southeast/map_units/tiles/{z}/{x}/{y}.pbf`],
    // note: can use promoteId: 'id' to promote feature properties ID to feature ID
    promoteId: 'id',
  },
}

// layer in Mapbox Light that we want to come AFTER our layers here
const beforeLayer = 'waterway-label'

export const layers = [
  {
    id: 'blueprint',
    source: 'blueprint',
    type: 'raster',
    minzoom: 0,
    maxzoom: 21,
    paint: {
      'raster-opacity': {
        stops: [
          [10, 0.8],
          [12, 0.6],
        ],
      },
    },
    before: beforeLayer,
  },
  {
    id: 'region-outline',
    source: 'mapUnits',
    'source-layer': 'boundary',
    maxzoom: 8,
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
    before: beforeLayer,
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
    before: beforeLayer,
  },
  {
    id: 'unit-outline',
    source: 'mapUnits',
    'source-layer': 'units',
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
    before: beforeLayer,
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
    before: beforeLayer,
  },
]
