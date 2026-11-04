# Radar IA Latam — MVP

Blog estático en español sobre herramientas de IA. Un proceso diario consulta **feeds oficiales de lanzamientos**, descarta entradas antiguas o duplicadas, comprueba la página y redacta un máximo de una novedad al día. Dos llamadas a Gemini redactan y revisan. Si falla cualquier control, no publica. La guía inicial es atemporal; no declara promociones activas.

## Ejecutar en local

Requisitos: Node 22 y Python 3.12.

```sh
python -m pip install -r requirements.txt
npm install
python scripts/validate.py
SITE_URL=https://tu-dominio.example npm run build
npm run dev
```

En PowerShell: `$env:SITE_URL='https://tu-dominio.example'; npm run build`.

Para probar el proceso: configura `GEMINI_API_KEY` en el entorno y ejecuta `python scripts/daily.py`. Es normal que no publique si no hay una novedad útil en los últimos siete días. El modelo predeterminado es `gemini-2.5-flash-lite`; comprueba en [precios oficiales](https://ai.google.dev/gemini-api/docs/pricing?hl=es) que tu cuenta tenga cuota gratuita antes de activarlo. No actives facturación si quieres mantener el coste en cero.

## Conectar servicios

1. Crea un repositorio GitHub **público** y sube esta carpeta. Los flujos estándar de GitHub Actions para repositorios públicos son gratuitos según la [documentación oficial](https://docs.github.com/en/billing/concepts/product-billing/github-actions). Revisa sus límites actuales.
2. En Settings → Secrets and variables → Actions, crea el secret `GEMINI_API_KEY` y la variable `SITE_URL` con URL final `https://...` sin barra final. Obtén la clave en [Google AI Studio](https://aistudio.google.com/app/apikey). Puedes cambiar `GEMINI_MODEL` como variable. Sin clave, la ejecución no publica nada.
3. En Cloudflare Pages, conecta ese repositorio: comando `npm run build`, directorio de salida `dist`, Node 22. Configura la variable de entorno `SITE_URL` con la misma URL. El despliegue automático de Pages ocurre cuando el flujo guarda un nuevo post en la rama principal. [Guía oficial de Pages](https://developers.cloudflare.com/pages/get-started/git-integration/).
4. Asocia tu dominio a Pages, actualiza `SITE_URL` en GitHub y Cloudflare, y vuelve a desplegar. Antes de publicar, comprueba que canonical, `robots.txt` y sitemap apunten al dominio real. `https://example.com` es solo un marcador y **no debe quedar en producción**.
5. Opcional: crea una propiedad GA4 y configura `PUBLIC_GA_ID` en Cloudflare Pages. Da de alta la URL en Search Console, verifica el dominio y envía `/sitemap-index.xml`. Revisa clics, impresiones y consultas cada mes; GA4 es opcional y puede requerir consentimiento según tu jurisdicción.
6. Opcional: crea un canal Telegram propio, añade el bot como administrador y configura secrets `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID`. El flujo envía un enlace con UTM solo tras guardar una publicación. Si falla Telegram, el post queda publicado y puedes reintentar la difusión manualmente. No envía a grupos ajenos ni compra tráfico.
7. Solicita AdSense solo después de tener dominio, navegación, política editorial y contenido útil suficientes. Sigue la [política oficial de contenido de poco valor](https://support.google.com/adsense/answer/1346295). Este MVP **no integra anuncios** ni garantiza aprobación, visitas o ingresos.

## Qué queda pendiente

- Cuentas y credenciales personales: GitHub, Cloudflare, Gemini, dominio, Analytics/Search Console, Telegram opcional y AdSense posterior.
- Revisar una vez al mes métricas, costes/cuotas, enlaces rotos y cambios en los feeds. Si una oferta exige comprobar términos complejos, el pipeline la omite; este MVP se concentra en lanzamientos oficiales y guías útiles.
- Los feeds iniciales son releases Atom de GitHub para Gemini CLI, MarkItDown y Ollama. Son fuentes públicas oficiales; el proceso lee su feed y una página pública por candidato, sin rastreo masivo. No afirma que sus productos sean gratuitos o estén disponibles en un país salvo prueba explícita.

## Controles y límites

El proceso exige HTTPS y host oficial permitido, fecha reciente, texto suficiente, enlace a fuente, longitud razonable, revisión de afirmaciones y una sola publicación diaria. La revisión de IA no es garantía absoluta: la defensa principal es publicar poco y omitir lo ambiguo. La guía inicial fue contrastada con la [página oficial de precios de Gemini API](https://ai.google.dev/gemini-api/docs/pricing?hl=es) el 4 de noviembre de 2026. El sitio usa sitemap, robots, canonical, metadatos y JSON-LD. No hay tráfico artificial, scraping de resultados de búsqueda ni promesas de posicionamiento.
