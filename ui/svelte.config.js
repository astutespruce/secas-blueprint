import adapter from '@sveltejs/adapter-static'
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'
import { config as dotEnvConfig } from 'dotenv'

// have to configure dotenv to load correct .env file
dotEnvConfig({ path: `.env.${process.env.NODE_ENV}` })

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),

	kit: {
		adapter: adapter({
			pages: 'public',
			assets: 'public',
			fallback: '404.html',
			precompress: false,
			strict: true
		}),
		paths: {
			base: process.env.DEPLOY_PATH || ''
		},
		alias: {
			$constants: '../constants',
			$images: 'src/images'
		}
	}
}

export default config
