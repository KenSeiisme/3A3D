/* Browser acceptance checks for the actual generated site. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const base = (process.env.TEST_BASE_URL || 'http://127.0.0.1:8766').replace(/\/$/, '');
const data = JSON.parse(fs.readFileSync(path.join(root, 'data/catalog.json'), 'utf8'));
const pages = [
  'index.html',
  'brand.html',
  'collection.html',
  'about.html',
  'support.html',
  ...data.brands.map((b) => `brand/${b.id}.html`),
];
const out = path.join(root, '_qa');
fs.mkdirSync(out, { recursive: true });
const vehicleCount = data.cars.filter((car) => car.brand !== 'special').length;
const brandCount = (id) => data.cars.filter((car) => car.brand === id).length;
const results = [];
async function check(name, fn) {
  await fn();
  results.push(name);
  console.log('PASS', name);
}
async function capture(page, file) {
  // Trigger lazy images before taking a full-page screenshot.
  const images = page.locator('img:visible');
  for (const img of await images.all()) {
    await img.scrollIntoViewIfNeeded();
    await img.evaluate((el) => el.decode().catch(() => {}));
    assert(
      await img.evaluate((el) => el.complete && el.naturalWidth > 0),
      'Image must decode before capture',
    );
  }
  await page.evaluate(() => scrollTo({ top: 0, behavior: 'instant' }));
  await page.screenshot({ path: path.join(out, file), fullPage: true });
}
(async () => {
  const edge = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
  const executablePath =
    process.env.BROWSER_PATH || (fs.existsSync(edge) ? edge : undefined);
  const browser = await chromium.launch({ headless: true, executablePath });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    reducedMotion: 'reduce',
  });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  try {
    await check('21 pages, metadata and every referenced local asset', async () => {
      const resources = new Set();
      for (const file of pages) {
        const response = await context.request.get(`${base}/${file}`);
        assert.equal(response.status(), 200, file);
        const text = await response.text();
        assert(text.includes('project.js'));
        assert(text.includes('name="description"'));
        assert.equal((text.match(/<h1[ >]/g) || []).length, 1, file);
        for (const match of text.matchAll(/(?:src|href)="([^"]+)"/g)) {
          const link = new URL(match[1], `${base}/${file}`);
          if (link.origin === new URL(base).origin && !link.hash)
            resources.add(link.origin + link.pathname);
        }
      }
      for (const url of resources) {
        const response = await context.request.head(url);
        assert.equal(response.status(), 200, url);
      }
      results.push(`${resources.size} unique local resource URLs verified`);
    });
    await check(
      '105 responsive layouts: 21 pages × 360/390/768/1024/1440px',
      async () => {
        for (const file of pages) {
          await page.goto(`${base}/${file}`);
          for (const width of [360, 390, 768, 1024, 1440]) {
            await page.setViewportSize({ width, height: 1000 });
            const layout = await page.evaluate(() => ({
              viewport: innerWidth,
              width: document.documentElement.scrollWidth,
              body: document.body.scrollWidth,
              overflows: [
                ...document.querySelectorAll(
                  'h1,h2,h3,.button,.car-card,.brand-card,.filter-bar',
                ),
              ]
                .filter((e) => e.getBoundingClientRect().right > innerWidth + 1)
                .map((e) => e.tagName + ':' + e.className),
            }));
            assert(
              layout.width <= width + 1,
              `${file}@${width}: document width ${layout.width}`,
            );
            assert(layout.body <= width + 1, `${file}@${width}: body overflow`);
            assert.deepEqual(layout.overflows, [], `${file}@${width}`);
          }
        }
      },
    );
    const visible = () => page.locator('[data-grid] [data-car]:visible');
    await check(
      'search, combined filters, empty state, reset and URL restoration',
      async () => {
        await page.goto(`${base}/collection.html`);
        assert.equal(await visible().count(), vehicleCount);
        await page.getByLabel('Search vehicles', { exact: true }).fill('AE86');
        await page.getByLabel('Search vehicles', { exact: true }).press('Enter');
        await page.waitForFunction(() =>
          document.querySelector('[data-count]').textContent.startsWith('1 vehicle'),
        );
        assert.equal(await visible().count(), 1);
        assert(new URL(page.url()).searchParams.get('q') === 'AE86');
        await page.getByLabel('Brand', { exact: true }).selectOption('toyota');
        await page.getByLabel('Drivetrain', { exact: true }).selectOption('rwd');
        assert.equal(await visible().count(), 1);
        await page.reload();
        assert.equal(await visible().count(), 1);
        assert.equal(
          await page.getByLabel('Search vehicles', { exact: true }).inputValue(),
          'AE86',
        );
        await page.getByLabel('Drivetrain', { exact: true }).selectOption('fwd');
        assert.equal(await visible().count(), 0);
        assert(await page.locator('[data-empty]').isVisible());
        await page
          .getByRole('button', { name: 'Clear filters', exact: true })
          .last()
          .click();
        await page.waitForFunction(
          (count) =>
            document.querySelector('[data-count]').textContent.startsWith(String(count)),
          vehicleCount,
        );
        await page.getByLabel('Brand', { exact: true }).selectOption('audi');
        assert.equal(await visible().count(), brandCount('audi'));
        await page.getByLabel('Brand', { exact: true }).selectOption('toyota');
        assert.equal(await visible().count(), brandCount('toyota'));
        await page.goBack();
        assert.equal(await visible().count(), brandCount('audi'));
        assert.equal(
          await page.getByLabel('Brand', { exact: true }).inputValue(),
          'audi',
        );
        await page.goForward();
        assert.equal(await visible().count(), brandCount('toyota'));
      },
    );
    await check('alphabetical/power/default sorting and topic filters', async () => {
      await page.goto(`${base}/collection.html?sort=power`);
      let powers = await visible().evaluateAll((cards) =>
        cards.map((c) => Number(c.dataset.power) || -Infinity),
      );
      assert(powers.every((p, i) => !i || powers[i - 1] >= p));
      await page.getByLabel('Sort by', { exact: true }).selectOption('name');
      let names = await visible().evaluateAll((cards) =>
        cards.map((c) => c.dataset.name),
      );
      assert.deepEqual(
        names,
        [...names].sort((a, b) => a.localeCompare(b, 'en')),
      );
      await page.getByLabel('Sort by', { exact: true }).selectOption('');
      assert.equal(
        await visible().first().getAttribute('data-name'),
        data.cars.find((c) => c.brand !== 'special').name,
      );
      await page.getByLabel('Collection', { exact: true }).selectOption('classic');
      assert.equal(
        await visible().count(),
        data.cars.filter((c) => c.topics.includes('classic')).length,
      );
      await page.getByLabel('Collection', { exact: true }).selectOption('initial-d');
      assert.equal(await visible().count(), 1);
      await page.goto(`${base}/collection.html?sort=invalid&brand=unknown`);
      assert.equal(await visible().count(), vehicleCount);
      assert.equal(await page.locator('.special-section [data-car]').count(), 1);
    });
    await check(
      'all 16 fixed-brand pages and native keyboard-operated specifications',
      async () => {
        for (const brand of data.brands) {
          await page.goto(`${base}/brand/${brand.id}.html?brand=toyota`);
          assert.equal(
            await visible().count(),
            data.cars.filter((c) => c.brand === brand.id).length,
          );
          assert.equal(
            await page.locator('#main-nav a[aria-current]').innerText(),
            'Brands',
          );
        }
        await page.goto(`${base}/brand/toyota.html`);
        const details = page.locator('.specs').first(),
          summary = details.locator('summary');
        await summary.focus();
        await summary.press('Enter');
        assert(await details.evaluate((e) => e.open));
        assert(await page.locator('.car-stage img').first().isVisible());
        await summary.press('Space');
        assert.equal(await details.evaluate((e) => e.open), false);
      },
    );
    await check(
      'mobile menu, Escape focus and no automatic mobile video download',
      async () => {
        await page.setViewportSize({ width: 390, height: 844 });
        await page.goto(`${base}/index.html`);
        const menu = page.getByRole('button', { name: /Menu/ });
        assert.equal(await menu.getAttribute('aria-expanded'), 'false');
        assert.equal(await page.locator('#main-nav').isVisible(), false);
        await menu.click();
        assert(await page.locator('#main-nav').isVisible());
        await page.keyboard.press('Escape');
        assert.equal(await page.locator('#main-nav').isVisible(), false);
        assert(await menu.evaluate((e) => document.activeElement === e));
        assert.equal(await page.locator('video').getAttribute('src'), null);
        await capture(page, 'home-mobile.png');
      },
    );
    await check('desktop reduced-motion poster and screenshots', async () => {
      await page.setViewportSize({ width: 1440, height: 1000 });
      await page.goto(`${base}/index.html`);
      assert.equal(await page.locator('video').getAttribute('src'), null);
      await capture(page, 'home-desktop.png');
      await page.goto(`${base}/collection.html?brand=porsche`);
      await capture(page, 'collection-desktop.png');
      assert.deepEqual(errors, []);
    });
    await check(
      'no JavaScript: full catalogue, navigation and expandable parameters',
      async () => {
        const nojs = await browser.newContext({
          javaScriptEnabled: false,
          viewport: { width: 390, height: 844 },
        });
        const p = await nojs.newPage();
        await p.goto(`${base}/collection.html`);
        assert.equal(await p.locator('[data-grid] [data-car]').count(), vehicleCount);
        assert(await p.locator('#main-nav').isVisible());
        assert.equal(await p.locator('.filter-bar').isVisible(), false);
        await p.locator('.specs summary').first().click();
        assert.equal(await p.locator('.specs[open]').count(), 1);
        await nojs.close();
      },
    );
    await check('blocked autoplay and failed video preserve complete hero', async () => {
      const c = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
      await c.addInitScript(() => {
        HTMLMediaElement.prototype.play = () =>
          Promise.reject(new DOMException('Autoplay blocked', 'NotAllowedError'));
      });
      const p = await c.newPage();
      await p.goto(`${base}/index.html`);
      assert(await p.locator('.hero-poster').isVisible());
      assert(
        await p
          .getByRole('link', { name: 'Explore Collection', exact: true })
          .isVisible(),
      );
      assert.equal(
        await p.locator('.video-toggle').getAttribute('aria-pressed'),
        'false',
      );
      await c.close();
      const f = await browser.newContext({ viewport: { width: 390, height: 844 } });
      await f.route('**/assets/hero.mp4', (route) => route.abort());
      const fp = await f.newPage();
      await fp.goto(`${base}/index.html`);
      await fp.locator('.video-toggle').click();
      await fp.locator('.video-status').waitFor({ state: 'visible' });
      assert(await fp.locator('.hero-poster').isVisible());
      await f.close();
    });
    fs.writeFileSync(
      path.join(out, 'results.json'),
      JSON.stringify({ base, passed: results }, null, 2),
    );
    console.log(`Completed ${results.length} checks. Screenshots: ${out}`);
  } finally {
    await context.close();
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
