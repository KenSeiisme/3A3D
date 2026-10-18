# 3A3D — Driven by obsession

A static student automotive showcase: 21 pages, 16 brands, 111 passenger vehicles and one special exhibit. No framework, backend, account or sales system.

## Preview

Run `python -m http.server 8766 --bind 127.0.0.1` from this directory, then open http://127.0.0.1:8766.

## Edit

- `data/catalog.json` is the single source for vehicle names, specifications, images, brands and editorial categories. Original brand-page specifications were retained; this is reference data, not verified inventory.
- `scripts/build.py` contains the shared static-page templates. Run `python scripts/build.py` after changing templates or catalogue data. Commit generated HTML too; the host only needs to serve static files.
- `style.css` and `project.js` are shared by every page. The older page-specific CSS files remain as compatibility placeholders.
- Brand URLs and `support.html` are preserved. Contact replaces commercial support content.
- `scripts/extract-catalog.py` records the one-time migration and refuses to overwrite the migrated catalogue.
- Optimized WebP files live under `assets/`. Original supplied files are preserved. `scripts/optimize-assets.cjs` requires Sharp and processes newly added original paths in the catalogue; regenerate pages afterwards.

The Initial D category currently includes only the AE86. Association source: [Kodansha](https://licensing.kodansha.com/title/initial-d/). Reference specifications do not represent the modified car in the story.

## Verify

Install development tools with `npm install`, then install a Playwright browser (`npx playwright install chromium`) or use an installed Microsoft Edge. With preview running, use `npm test`. Set `TEST_BASE_URL` to test another deployment; set `BROWSER_PATH` to select a browser executable. Screenshots and results are written to ignored `_qa/`.

The check covers all pages and local assets, the five target widths, filters, sorting, browser history, mobile navigation, native detail expansion, no-JavaScript content and video fallbacks.

## Deployment

Serve this directory as a static site, without a framework build step. The existing repository is `KenSeiisme/3A3D`, branch `main`, with a Vercel deployment status on the original commit. Confirm the actual `https://3a3d.vercel.app/` content after publishing; a Git push alone is not a visual verification.
