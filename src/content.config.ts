import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
const posts = defineCollection({loader:glob({pattern:'**/*.md',base:'./src/content/posts'}),schema:z.object({title:z.string(),description:z.string(),pubDate:z.coerce.date(),sourceUrl:z.string().url(),sourceDate:z.string(),kind:z.enum(['guia','novedad']),verifiedAt:z.string(),tags:z.array(z.string())})});
export const collections={posts};
