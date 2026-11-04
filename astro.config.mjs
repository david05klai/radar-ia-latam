import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
const site = process.env.SITE_URL || 'http://localhost:4321';
if (process.env.CI && !process.env.SITE_URL) throw new Error('Configura SITE_URL antes del despliegue.');
export default defineConfig({site, integrations:[sitemap()]});
