import * as env from '$env/static/public';

export const SENTRY_DSN = env.PUBLIC_SENTRY_DSN || '';
export const GOOGLE_ANALYTICS_ID = env.PUBLIC_GOOGLE_ANALYTICS_ID || '';
export const MAPBOX_TOKEN = env.PUBLIC_MAPBOX_TOKEN;
export const API_HOST = env.PUBLIC_API_HOST;
export const TILE_HOST = env.PUBLIC_TILE_HOST;
export const API_TOKEN = env.PUBLIC_API_TOKEN;
