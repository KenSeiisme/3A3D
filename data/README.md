# Maintaining the vehicle catalogue

`catalog.json` is the single source of truth. Generated HTML is output, so edit the catalogue or templates instead of copying cards between pages.

## Add a vehicle

1. Place the original image under `car_vector_image/`.
2. Add an object to the `cars` array in `catalog.json`:

```json
{
  "id": "toyota-example",
  "name": "Toyota Example",
  "brand": "toyota",
  "image": "car_vector_image/Toyota_Example.png",
  "specs": {
    "Engine": "Add verified engine information",
    "Power": "Add verified power information",
    "Drive type": "Rear-Wheel Drive"
  },
  "power": null,
  "drive": "rwd",
  "topics": []
}
```

Replace the example with actual information. Use a unique lowercase, hyphen-separated `id`; `brand` must match a brand ID. `power` is numeric bhp for sorting, or `null` when unknown; keep it consistent with `specs.Power`. `drive` is `rwd`, `fwd`, `awd`, `4wd` or `other`. Unknown specifications can be omitted.

`topics` can include `classic` or `initial-d`. Add `initial-d` only after verifying the exact model association, and record the reference under `editorialSources`. Use an empty array for the general collection. The reserved brand `special` puts an entry in the separate special exhibit.

3. After the initial `npm install` or `pnpm install`, run:

```sh
node scripts/optimize-assets.cjs
python scripts/build.py
```

The optimizer creates a smaller WebP image, records its dimensions and updates the path in the catalogue. The builder updates the complete collection, brand page and counts, then formats every generated page. Existing optimized images are left alone.

## Add a brand

Add an object to the `brands` array with `id`, `name` and `logo` (an original image path). Use that ID for the brand's vehicles, then run the commands above. The directory, search options, brand page and manufacturer counts are generated automatically.

## Choose homepage highlights

Edit `home.json`: `featuredCars` contains vehicle IDs, `featuredBrands` contains brand IDs, and `spotlightCar` supplies the AE86 editorial image. The editorial text is maintained separately in `templates/pages/home.html`; update it too if you change the spotlight's subject.

## Before publishing

Run the preview and `npm test`, then commit `data/`, optimized images, templates and generated HTML together. `npm run format:check` checks HTML, CSS, JavaScript and JSON formatting. Python sources use Black with the settings in `pyproject.toml`.
