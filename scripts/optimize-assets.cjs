// Build-time image optimization; the deployed website has no dependencies.
const sharp = require('sharp');
const fs = require('node:fs/promises');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
(async () => {
  const catalog = JSON.parse(
    await fs.readFile(path.join(root, 'data/catalog.json'), 'utf8'),
  );
  await fs.mkdir(path.join(root, 'assets/cars'), { recursive: true });
  await fs.mkdir(path.join(root, 'assets/logos'), { recursive: true });
  for (const car of catalog.cars) {
    if (car.image.startsWith('assets/cars/')) continue;
    const input = path.join(root, car.image);
    const output = `assets/cars/${car.id}.webp`;
    await sharp(input)
      .trim({ threshold: 8 })
      .resize({ width: 840, height: 500, fit: 'inside', withoutEnlargement: true })
      .webp({ quality: 82 })
      .toFile(path.join(root, output));
    car.image = output;
    const meta = await sharp(path.join(root, output)).metadata();
    car.width = meta.width;
    car.height = meta.height;
  }
  for (const brand of catalog.brands) {
    if (brand.logo.startsWith('assets/logos/')) continue;
    const output = `assets/logos/${brand.id}.webp`;
    await sharp(path.join(root, brand.logo))
      .trim({ threshold: 8 })
      .resize({ width: 200, height: 100, fit: 'inside', withoutEnlargement: true })
      .webp({ quality: 88 })
      .toFile(path.join(root, output));
    brand.logo = output;
  }
  await sharp(path.join(root, 'image/profile_picture.png'))
    .resize({ width: 480, withoutEnlargement: true })
    .webp({ quality: 85 })
    .toFile(path.join(root, 'assets/author.webp'));
  await fs.writeFile(
    path.join(root, 'data/catalog.json'),
    JSON.stringify(catalog, null, 2) + '\n',
  );
  console.log(
    `Optimized ${catalog.cars.length} vehicle images and ${catalog.brands.length} logos.`,
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
