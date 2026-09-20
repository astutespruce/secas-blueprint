import path from 'path'
import { sveltekit } from '@sveltejs/kit/vite'
import { defineConfig } from 'vite'
import { enhancedImages } from '@sveltejs/enhanced-img'
import Icons from 'unplugin-icons/vite'
import tailwindcss from '@tailwindcss/vite'
import { config as dotEnvConfig } from 'dotenv'
import { VitePWA } from 'vite-plugin-pwa'
import send from 'send'

// have to configure dotenv to load correct .env file
dotEnvConfig({ path: `.env.${process.env.NODE_ENV}` })

const servePMTilesMiddleware = (server) => {
	server.middlewares.use('/tiles', (req, res, next) => {
		// hardcode root to prevent traversal
		const fileStream = send(req, req.url, {
			root: path.resolve(process.env.VITE_TILE_DIR as string)
		})

		// CORS must be set
		fileStream.on('headers', (res) => {
			res.setHeader('Access-Control-Allow-Origin', '*')
			res.setHeader('Access-Control-Allow-Headers', '*')
			res.setHeader('Access-Control-Allow-Method', '*')
			res.setHeader('Vary', 'Accept-Encoding')
		})

		fileStream.on('error', (err) => {
			if (err.status === 404) {
				// allow vite to handle 404s
				next()
			} else {
				res.statusCode = err.status || 500
				res.end(err.message)
			}
		})
		fileStream.pipe(res)
	})
}

export default defineConfig(({ command }) => {
	// only serve PMTiles through vite in local development; they are served
	// by Caddy in production
	const servePMTiles = command === 'serve' && !!process.env.VITE_TILE_DIR

	return {
		build: {
			rolldownOptions: {
				output: {
					codeSplitting: {
						groups: [
							{
								test: (id) => id.includes('mapbox-gl') || id.includes('deck.gl'),
								name: 'map-vendor'
							}
						]
					}
				}
			}
		},
		server: {
			fs: {
				allow: servePMTiles ? [path.resolve(process.env.VITE_TILE_DIR as string)] : undefined
			},
			proxy: {
				// proxy API endpoint to FastAPI
				'/api': {
					target: 'http://localhost:5000',
					changeOrigin: true
				}
			}
		},
		plugins: [
			VitePWA({
				manifest: {
					name: 'Southeast Conservation Blueprint Explorer',
					short_name: 'Southeast Blueprint Explorer',
					start_url: process.env.PUBLIC_DEPLOY_PATH || '/',
					scope: process.env.PUBLIC_DEPLOY_PATH || '/',
					background_color: '#4279A6',
					theme_color: '#4279A6',
					display: 'minimal-ui',
					icons: [
						{
							src: 'favicon-16x16.png',
							sizes: '16x16',
							type: 'image/png'
						},
						{
							src: 'favicon-32x32.png',
							sizes: '32x32',
							type: 'image/png'
						},
						{
							src: 'favicon-64x64.png',
							sizes: '64x64',
							type: 'image/png'
						},
						{
							src: 'favicon-192x192.png',
							sizes: '192x192',
							type: 'image/png'
						},
						{
							src: 'favicon-512x512.png',
							sizes: '512x512',
							type: 'image/png'
						},
						{
							src: 'favicon-64x64.svg',
							sizes: '64x64',
							type: 'image/svg'
						}
					]
				},
				// create empty self-destroying service worker; can't seem to disable it
				// this still creates registerSW.js and sw.js files in output, but
				// we don't include them in app.html, so they shouldn't be used
				selfDestroying: true,
				strategies: 'injectManifest',
				injectManifest: {
					injectionPoint: undefined
				}
			}),
			tailwindcss(),
			enhancedImages(),
			sveltekit(),
			Icons({ compiler: 'svelte' }),
			// middleware to serve PMTtiles in development mode
			servePMTiles
				? {
						name: 'serve-pmtiles',
						configureServer(server) {
							servePMTilesMiddleware(server)
						},
						configurePreviewServer(server) {
							servePMTilesMiddleware(server)
						}
					}
				: undefined
		]
	}
})
