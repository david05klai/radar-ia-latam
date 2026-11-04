export function GET({site}) {
  return new Response(`User-agent: *\nAllow: /\nSitemap: ${new URL('/sitemap-index.xml', site).href}\n`, {headers:{'Content-Type':'text/plain; charset=utf-8'}});
}
