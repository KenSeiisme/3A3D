"""Generate the static site from one catalogue. No runtime or build step on Vercel."""
from pathlib import Path
from html import escape as esc
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
BRANDS = {b['id']: b for b in DATA['brands']}
CARS = DATA['cars']
NORMAL = [c for c in CARS if c['brand'] != 'special']
DRIVES = {'rwd':'RWD','fwd':'FWD','awd':'AWD','4wd':'4WD','other':'—'}
ARROW = '<span aria-hidden="true">↗</span>'

def card(c, prefix=''):
    brand = BRANDS.get(c['brand'], {'name':'Special exhibit'})['name']
    topics = ' '.join(c['topics'])
    badge = 'Special exhibit' if c['brand']=='special' else 'Initial D' if 'initial-d' in c['topics'] else 'Classic collection' if 'classic' in c['topics'] else brand
    specs = ''.join(f'<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k,v in c['specs'].items())
    power = f"{c['power']} <small>bhp</small>" if c['power'] is not None else '—'
    return f'''<article class="car-card" data-car data-name="{esc(c['name'],quote=True)}" data-brand="{c['brand']}" data-drive="{c['drive']}" data-topics="{topics}" data-power="{c['power'] if c['power'] is not None else ''}">
      <div class="car-stage"><span class="card-tag">{badge}</span><img src="{prefix}{c['image']}" width="{c.get('width',840)}" height="{c.get('height',500)}" alt="{esc(c['name'])}" loading="lazy" decoding="async"></div>
      <div class="card-body"><p class="eyebrow">{esc(brand)}</p><h3>{esc(c['name'])}</h3>
      <div class="quick-specs"><span>{power}</span><span>{DRIVES[c['drive']]}</span></div>
      <details class="specs"><summary><span class="closed-label">View specs</span><span class="open-label">Hide specs</span><span aria-hidden="true">+</span></summary><dl>{specs}</dl><p class="spec-note">Reference specifications from the original project. Variants may differ.</p></details></div></article>'''

def brand_card(b,prefix=''):
    count = sum(c['brand']==b['id'] for c in NORMAL)
    return f'''<a class="brand-card" href="{prefix}brand/{b['id']}.html"><div class="brand-logo"><img src="{prefix}{b['logo']}" width="200" height="100" alt="" loading="lazy"></div><div><h3>{esc(b['name'])}</h3><span>{count:02} vehicles</span></div>{ARROW}</a>'''

def section_head(kicker,title,link='',label='View all'):
    return f'<div class="section-heading"><div><p class="eyebrow">{kicker}</p><h2>{title}</h2></div>'+ (f'<a class="text-link" href="{link}">{label} {ARROW}</a>' if link else '')+'</div>'

def shell(title,description,active,body,path):
    prefix = '../' if '/' in path else ''
    nav = ''.join(f'<a href="{prefix}{p}"'+(' aria-current="page"' if active==key else '')+f'>{label}</a>' for key,label,p in [('home','Home','index.html'),('brands','Brands','brand.html'),('collection','Collection','collection.html'),('about','About','about.html'),('contact','Contact','support.html')])
    doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | 3A3D</title><meta name="description" content="{esc(description,quote=True)}"><meta name="theme-color" content="#090909"><meta property="og:title" content="{esc(title,quote=True)} | 3A3D"><meta property="og:description" content="{esc(description,quote=True)}"><meta property="og:type" content="website"><meta property="og:image" content="https://3a3d.vercel.app/assets/hero-poster.jpg"><link rel="icon" href="{prefix}image/3A-3D.png"><link rel="stylesheet" href="{prefix}style.css"><script src="{prefix}project.js" defer></script></head>
<body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="container header-inner"><a class="logo" href="{prefix}index.html" aria-label="3A3D home"><img src="{prefix}image/3A-3D.png" width="88" height="50" alt="3A3D"></a><button class="menu-toggle" type="button" aria-controls="main-nav" aria-expanded="false" hidden>Menu <span aria-hidden="true">☰</span></button><nav id="main-nav" aria-label="Main navigation">{nav}</nav><span class="header-note"><i></i> An automotive showcase</span></div></header>
<main id="main">{body}</main>
<footer class="site-footer"><div class="container"><div class="footer-top"><div><a class="footer-wordmark" href="{prefix}index.html">3A<span>3D</span></a><p>For the love of the drive.</p></div><nav aria-label="Footer navigation">{nav}</nav><a class="text-link" href="https://kensei-eta.vercel.app/" target="_blank" rel="noopener noreferrer">Created by KenSei {ARROW}</a></div><div class="footer-bottom"><p>© 2026 3A3D · Student portfolio project</p><p>A showcase of automotive design. No vehicle sales or bookings.</p></div></div></footer></body></html>'''
    (ROOT/path).write_text(doc+'\n',encoding='utf-8')

def intro(kicker,title,description,crumb=''):
    return f'<div class="container page-intro">{crumb}<p class="eyebrow">{kicker}</p><h1>{title}</h1><p class="lead">{description}</p></div>'

def catalog(cars,fixed=''):
    brand_options=''.join(f'<option value="{b["id"]}">{esc(b["name"])}</option>' for b in BRANDS.values())
    brand_field = f'<label>Brand<select name="brand" aria-label="Brand"><option value="">All brands</option>{brand_options}</select></label>' if not fixed else f'<p class="fixed-brand">Brand <strong>{esc(BRANDS[fixed]["name"])}</strong></p>'
    filters=f'''<form class="filter-bar" role="search" aria-label="Filter vehicles" hidden><label class="search-field">Search vehicles<input type="search" name="q" placeholder="Search a model or brand…" autocomplete="off"></label>{brand_field}<label>Drivetrain<select name="drive"><option value="">All drivetrains</option><option value="rwd">Rear-wheel drive</option><option value="fwd">Front-wheel drive</option><option value="awd">All-wheel drive</option><option value="4wd">Four-wheel drive</option></select></label><label>Collection<select name="topic"><option value="">All vehicles</option><option value="classic">Classics</option><option value="initial-d">Initial D</option></select></label><label>Sort by<select name="sort"><option value="">Curated order</option><option value="name">Name A–Z</option><option value="power">Power: high to low</option></select></label><button class="reset-button" type="reset">Clear filters</button></form>'''
    for name, label in [('drive','Drivetrain'),('topic','Collection'),('sort','Sort by')]:
        filters = filters.replace(f'<select name="{name}">', f'<select name="{name}" aria-label="{label}">')
    return f'''<section class="container catalog-section" data-catalog data-fixed-brand="{fixed}">{filters}<noscript><p class="notice">All vehicles and specifications are available below. Enable JavaScript to search and filter.</p></noscript><div class="results-bar"><p data-count role="status" aria-live="polite">{len(cars)} vehicles to discover</p><span>Find your next obsession.</span></div><div class="car-grid" data-grid>{''.join(card(c,'../' if fixed else '') for c in cars)}</div><div class="empty-state" data-empty hidden><span aria-hidden="true">↗</span><h2>No vehicles found.</h2><p>Try another model name or clear your filters.</p><button class="button" data-clear type="button">Clear filters</button></div></section>'''

featured_names=['toyota-ae86','mazda-rx-7','nissan-gt-r-r32']
featured=[next(c for c in CARS if c['id']==key) for key in featured_names]
home=f'''<section class="hero container"><div class="hero-media"><img class="hero-poster" src="assets/hero-poster.jpg" width="1600" height="900" alt="White Toyota AE86 Trueno with its pop-up headlights raised" fetchpriority="high"><video class="hero-video" muted loop playsinline preload="none" poster="assets/hero-poster.jpg" aria-hidden="true" tabindex="-1" data-src="assets/hero.mp4"></video></div><div class="hero-shade"></div><div class="hero-content"><p class="eyebrow"><span class="accent-line"></span> The 3A3D collection</p><h1>Driven by<br><em>obsession.</em></h1><p>Iconic machines. Unforgettable stories.<br>A collection built for people who love the drive.</p><div class="hero-actions"><a class="button" href="collection.html">Explore Collection {ARROW}</a><a class="button button-outline" href="brand.html">Browse Brands {ARROW}</a></div></div><div class="hero-bottom"><span>01 / THE ART OF AUTOMOTIVE</span><button class="video-toggle" type="button" hidden aria-pressed="false">Play film <span aria-hidden="true">▷</span></button></div><p class="video-status" role="status" hidden></p></section>
<div class="container stats-strip"><div><strong>{len(NORMAL)}</strong><span>Vehicles to discover</span></div><div><strong>16</strong><span>Iconic manufacturers</span></div><div><strong>∞</strong><span>Passion for the drive</span></div><p>From everyday icons<br>to bedroom-wall legends.</p></div>
<section class="container section">{section_head('Selected for the spotlight','Icons never fade.','collection.html','Explore all vehicles')}<div class="car-grid">{''.join(card(c) for c in featured)}</div></section>
<section class="brands-section section"><div class="container">{section_head('Find your marque','Different badges. Same passion.','brand.html','All 16 brands')}<div class="brand-grid featured-brands">{''.join(brand_card(BRANDS[b]) for b in ['toyota','porsche','ferrari','nissan'])}</div></div></section>
<section class="container section"><div class="editorial"><div class="editorial-art"><span class="editorial-number" aria-hidden="true">86</span><img src="{featured[0]['image']}" width="840" height="500" alt="Toyota AE86" loading="lazy"></div><div class="editorial-copy"><p class="eyebrow">The culture behind the cars</p><h2>A small car.<br>A lasting legend.</h2><p>The AE86 sits at the heart of Initial D. Discover the car that connects this collection to a story of mountain roads, tofu deliveries and a passion for driving.</p><a class="text-link" href="collection.html?topic=initial-d">Explore the Initial D spotlight {ARROW}</a><p class="editorial-note">Model association verified with <a href="https://licensing.kodansha.com/title/initial-d/" target="_blank" rel="noopener noreferrer">Kodansha</a>. Reference specs are not those of the modified story car.</p></div></div></section>
<section class="container about-banner"><p class="eyebrow">Made out of curiosity</p><h2>A passion project.<br>With a point of view.</h2><p>3A3D is KenSei’s exploration of automotive culture, thoughtful web design and the details that make a machine memorable.</p><a class="button button-outline" href="about.html">Behind the project {ARROW}</a></section>'''
shell('Driven by obsession','Explore 3A3D: an automotive portfolio featuring iconic cars, 16 manufacturers and a passion for design.','home',home,'index.html')

body=intro('The manufacturers','Find your marque.','Sixteen manufacturers. Decades of design. Start with the badge that speaks to you.')+f'<section class="container section brand-directory"><div class="brand-grid">{"".join(brand_card(b) for b in BRANDS.values())}</div></section>'
shell('Brands','Explore 16 automotive manufacturers and discover every vehicle in the 3A3D showcase.','brands',body,'brand.html')

body=intro('The complete collection','Every car has a story.','Discover iconic machines, compare their character and get to know the details.')+'''<div class="container topic-links"><a href="collection.html">The full collection ↗</a><a href="collection.html?topic=classic">Classic collection ↗</a><a href="collection.html?topic=initial-d">Initial D spotlight ↗</a></div>'''+catalog(NORMAL)
special=[c for c in CARS if c['brand']=='special']
body+=f'<section class="container section special-section">{section_head("A little off the beaten track","The unexpected exhibit.")}<p class="lead">A playful piece of the original project, parked in its own corner.</p><div class="car-grid">{"".join(card(c) for c in special)}</div></section>'
shell('Collection','Browse the complete 3A3D vehicle collection. Search by model, manufacturer, drivetrain or editorial collection.','collection',body,'collection.html')

for brand in BRANDS.values():
    cars=[c for c in NORMAL if c['brand']==brand['id']]
    crumb='<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../brand.html">Brands</a><span aria-hidden="true">/</span><span aria-current="page">'+esc(brand['name'])+'</span></nav>'
    body=intro(f'{len(cars):02} vehicles · The manufacturer series',esc(brand['name']),f'Explore the {esc(brand["name"])} selection. A closer look at the machines behind the badge.',crumb)+catalog(cars,brand['id'])
    shell(brand['name'],f'Discover {len(cars)} {brand["name"]} models in the 3A3D automotive showcase, with specifications and vehicle filters.','brands',body,f'brand/{brand["id"]}.html')

body=intro('Behind the collection','Built for the love<br>of the drive.','A student portfolio project exploring the intersection of automotive culture and web design.')+'''<section class="container section story-grid"><div><p class="eyebrow">Why 3A3D exists</p><h2>Great machines<br>deserve a closer look.</h2></div><div class="prose"><p>3A3D began as a way to bring a personal interest in cars into a web project. It brings together manufacturers, classic designs and performance icons in one place.</p><p>The goal is simple: make discovery enjoyable. Give every vehicle room to breathe, make specifications easy to read, and build an experience that works just as well on a phone as on a desktop.</p><p>This is an independent student showcase, not a commercial dealership. Vehicles are presented for exploration; there are no sales, inventory claims or booking services.</p></div></section>
<section class="container principles"><article><span>01 / DISCOVER</span><h3>Design with character.</h3><p>A restrained black-and-orange identity keeps the focus on the vehicles.</p></article><article><span>02 / EXPLORE</span><h3>Details within reach.</h3><p>Searchable collections and readable specifications make browsing purposeful.</p></article><article><span>03 / BUILD</span><h3>Simple by design.</h3><p>Semantic HTML, shared CSS and vanilla JavaScript. No framework required.</p></article></section>
<section class="container section"><div class="author-panel"><img src="assets/author.webp" width="480" height="480" alt="KenSei’s illustrated profile" loading="lazy"><div><p class="eyebrow">Meet the creator</p><h2>Hey, I’m KenSei.</h2><p>A TAR UMT student in Malaysia, exploring software development, design and the things that make technology interesting. 3A3D is one of those explorations.</p><div class="author-links"><a class="button" href="https://kensei-eta.vercel.app/" target="_blank" rel="noopener noreferrer">Portfolio ↗</a><a class="text-link" href="https://github.com/KenSeiisme" target="_blank" rel="noopener noreferrer">GitHub ↗</a><a class="text-link" href="mailto:haozheng00910@gmail.com">Email ↗</a></div></div></div></section>'''
shell('About the project','Learn about 3A3D, a student automotive showcase by KenSei, built with HTML, CSS and vanilla JavaScript.','about',body,'about.html')

faqs=[('Is 3A3D a real dealership?','No. This is an independent student portfolio project. The collection is for exploration and does not represent vehicles available for purchase.'),('Can I buy a car or book a test drive?','There are no sales, payment or booking services on this website.'),('Where do the specifications come from?','The specifications were carried over from the original project and consolidated across pages. They are reference information, not independently verified manufacturer specifications. Output and equipment can vary by model year, market and variant.'),('Why is the Initial D spotlight focused on the AE86?','The AE86 association is confirmed by the series publisher. Other models are kept in the general collection until their exact variants can be checked. The displayed specifications do not describe a modified story car.'),('How can I report a mistake?','Email the creator with the model name, the detail to correct and a reliable reference. Feedback on accessibility or the site experience is welcome too.'),('Does browsing require an account?','No. You can explore every vehicle without signing in. Filtering happens in your browser; the site has no account or reservation system.')]
faq_html=''.join(f'<details class="faq-item"><summary>{q}<span aria-hidden="true">+</span></summary><p>{a}</p></details>' for q,a in faqs)
body=intro('Questions, ideas, feedback','Let’s talk cars.<br>And good design.','Found a detail worth correcting, or want to talk about the project? Get in touch.')+f'''<section class="container contact-layout"><aside class="contact-panel"><p class="eyebrow">Reach the creator</p><h2>Say hello.</h2><p>Project feedback and thoughtful conversations are always welcome.</p><a class="contact-email" href="mailto:haozheng00910@gmail.com">haozheng00910@gmail.com {ARROW}</a><a class="text-link" href="https://github.com/KenSeiisme/3A3D" target="_blank" rel="noopener noreferrer">Explore the source on GitHub {ARROW}</a><div class="project-note"><span class="status-dot"></span> Independent student project<br><span>Created in Malaysia · Built for curious minds.</span></div></aside><div class="faq-list"><p class="eyebrow">Good to know</p><h2>A few answers.</h2>{faq_html}</div></section>'''
shell('Contact & FAQ','Contact the creator of 3A3D, report a vehicle specification correction and learn more about this student showcase.','contact',body,'support.html')
for file in ['nav.css','index.css','brand.css','collection.css','about.css','support.css','brand/car-brand.css']:
    (ROOT/file).write_text('/* Shared styles are maintained in '+('../style.css' if '/' in file else 'style.css')+'. */\n',encoding='utf-8')
print(f'Generated {5+len(BRANDS)} static pages from {len(CARS)} catalogue entries.')
