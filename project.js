/* Progressive enhancement: content remains available without JavaScript. */
(() => {
  'use strict';
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#main-nav');
  const mobile = matchMedia('(max-width: 767px)');
  function closeMenu() {
    menu.setAttribute('aria-expanded', 'false');
    nav.hidden = mobile.matches;
  }
  if (menu && nav) {
    menu.hidden = !mobile.matches;
    closeMenu();
    menu.addEventListener('click', () => {
      const open = menu.getAttribute('aria-expanded') !== 'true';
      menu.setAttribute('aria-expanded', String(open));
      nav.hidden = !open;
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && mobile.matches && !nav.hidden) {
        closeMenu();
        menu.focus();
      }
    });
    mobile.addEventListener('change', () => {
      menu.hidden = !mobile.matches;
      closeMenu();
    });
  }
  const catalog = document.querySelector('[data-catalog]');
  if (catalog) {
    const form = catalog.querySelector('form');
    const grid = catalog.querySelector('[data-grid]');
    const cards = [...grid.querySelectorAll('[data-car]')];
    const fixedBrand = catalog.dataset.fixedBrand;
    const keys = ['q', 'brand', 'drive', 'topic', 'sort'];
    form.hidden = false;
    const field = (key) => form.elements.namedItem(key);
    function readURL() {
      const params = new URLSearchParams(location.search);
      for (const key of keys) {
        const control = field(key);
        if (control) {
          control.value = params.get(key) || '';
          if (control.tagName === 'SELECT' && control.selectedIndex < 0)
            control.value = '';
        }
      }
      apply(false);
    }
    function apply(updateURL = true) {
      const values = Object.fromEntries(
        keys.map((key) => [key, field(key)?.value || '']),
      );
      const search = values.q.trim().toLocaleLowerCase();
      const brand = fixedBrand || values.brand;
      let count = 0;
      const ordered = [...cards];
      if (values.sort === 'name')
        ordered.sort((a, b) => a.dataset.name.localeCompare(b.dataset.name, 'en'));
      if (values.sort === 'power')
        ordered.sort(
          (a, b) =>
            (b.dataset.power === '' ? -Infinity : Number(b.dataset.power)) -
            (a.dataset.power === '' ? -Infinity : Number(a.dataset.power)),
        );
      for (const card of ordered) {
        const data = card.dataset;
        const searchable = (data.name + ' ' + data.brand).toLocaleLowerCase();
        const visible =
          (!search || searchable.includes(search)) &&
          (!brand || data.brand === brand) &&
          (!values.drive || data.drive === values.drive) &&
          (!values.topic || data.topics.split(' ').includes(values.topic));
        card.hidden = !visible;
        if (visible) count++;
        grid.append(card);
      }
      catalog.querySelector('[data-count]').textContent =
        `${count} ${count === 1 ? 'vehicle' : 'vehicles'} to discover`;
      catalog.querySelector('[data-empty]').hidden = count !== 0;
      grid.hidden = count === 0;
      document.querySelectorAll('.topic-links a').forEach((link) => {
        const topic = new URL(link.href).searchParams.get('topic') || '';
        if (values.topic === topic) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
      if (updateURL) {
        const url = new URL(location.href);
        for (const key of keys) {
          url.searchParams.delete(key);
          if (values[key] && !(fixedBrand && key === 'brand'))
            url.searchParams.set(key, values[key]);
        }
        if (url.href !== location.href) history.pushState(null, '', url);
      }
    }
    let typing;
    form.addEventListener('input', (event) => {
      if (event.target.name === 'q') {
        clearTimeout(typing);
        typing = setTimeout(() => apply(), 250);
      }
    });
    form.addEventListener('change', () => {
      clearTimeout(typing);
      apply();
    });
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      clearTimeout(typing);
      apply();
    });
    form.addEventListener('reset', () => {
      clearTimeout(typing);
      setTimeout(() => apply(), 0);
    });
    catalog.querySelector('[data-clear]').addEventListener('click', () => {
      form.reset();
      field('q').focus();
    });
    window.addEventListener('popstate', () => {
      clearTimeout(typing);
      readURL();
    });
    readURL();
  }
  const video = document.querySelector('.hero-video');
  const toggle = document.querySelector('.video-toggle');
  if (video && toggle) {
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const status = document.querySelector('.video-status');
    let failed = false;
    toggle.hidden = false;
    function display(playing) {
      video.classList.toggle('is-playing', playing);
      toggle.setAttribute('aria-pressed', String(playing));
      toggle.textContent = playing
        ? 'Pause film Ⅱ'
        : failed
          ? 'Film unavailable'
          : 'Play film ▷';
    }
    async function play() {
      if (failed) return;
      if (!video.getAttribute('src')) {
        video.src = video.dataset.src;
        video.load();
      }
      try {
        await video.play();
      } catch {
        display(false);
      }
    }
    toggle.addEventListener('click', () => {
      if (video.paused) play();
      else video.pause();
    });
    video.addEventListener('playing', () => display(true));
    video.addEventListener('pause', () => display(false));
    video.addEventListener('error', () => {
      failed = true;
      display(false);
      toggle.disabled = true;
      status.textContent =
        'The film could not load. You can still explore the full collection.';
      status.hidden = false;
    });
    reduced.addEventListener('change', () => {
      if (reduced.matches) video.pause();
    });
    mobile.addEventListener('change', () => {
      if (mobile.matches) video.pause();
    });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) video.pause();
    });
    if (!mobile.matches && !reduced.matches && !navigator.connection?.saveData) play();
  }
})();
