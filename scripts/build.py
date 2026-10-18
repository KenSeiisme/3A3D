"""从目录数据和独立模板生成可读的静态 HTML；线上不需要 Python。"""

import json
import subprocess
from functools import lru_cache
from html import escape
from pathlib import Path
from string import Template


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
DRIVE_LABELS = {
    "rwd": "RWD",
    "fwd": "FWD",
    "awd": "AWD",
    "4wd": "4WD",
    "other": "—",
}
NAVIGATION = [
    ("home", "Home", "index.html"),
    ("brands", "Brands", "brand.html"),
    ("collection", "Collection", "collection.html"),
    ("about", "About", "about.html"),
    ("contact", "Contact", "support.html"),
]


def read_json(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


@lru_cache
def load_template(name):
    return Template((TEMPLATES / name).read_text(encoding="utf-8"))


def render(template_name, **values):
    # 模板只接收已转义文本，或由本文件生成的 HTML 片段。
    return load_template(template_name).substitute(values)


def render_navigation(active, prefix):
    links = []
    for key, label, filename in NAVIGATION:
        current = ' aria-current="page"' if active == key else ""
        links.append(f'<a href="{prefix}{filename}"{current}>{label}</a>')
    return "\n".join(links)


def render_car(car, brands, prefix=""):
    brand_name = brands.get(car["brand"], {"name": "Special exhibit"})["name"]
    topics = car["topics"]
    badge = brand_name
    if car["brand"] == "special":
        badge = "Special exhibit"
    elif "initial-d" in topics:
        badge = "Initial D"
    elif "classic" in topics:
        badge = "Classic collection"

    power = car["power"]
    rows = [
        render("components/spec-row.html", label=escape(label), value=escape(value))
        for label, value in car["specs"].items()
    ]
    return render(
        "components/car-card.html",
        name=escape(car["name"]),
        brand_id=escape(car["brand"]),
        brand_name=escape(brand_name),
        drive_id=escape(car["drive"]),
        drive_label=DRIVE_LABELS[car["drive"]],
        topics=escape(" ".join(topics)),
        badge=escape(badge),
        power_value=power if power is not None else "",
        power_label=f"{power} <small>bhp</small>" if power is not None else "—",
        image=escape(prefix + car["image"]),
        width=car.get("width", 840),
        height=car.get("height", 500),
        spec_rows="\n".join(rows),
    )


def render_brand_card(brand, cars):
    count = sum(car["brand"] == brand["id"] for car in cars)
    return render(
        "components/brand-card.html",
        prefix="",
        id=escape(brand["id"]),
        name=escape(brand["name"]),
        logo=escape(brand["logo"]),
        count=f"{count:02}",
    )


def render_catalog(cars, brands, fixed_brand=""):
    prefix = "../" if fixed_brand else ""
    if fixed_brand:
        name = escape(brands[fixed_brand]["name"])
        brand_field = f'<p class="fixed-brand">Brand <strong>{name}</strong></p>'
    else:
        options = "\n".join(
            f'<option value="{escape(brand["id"])}">{escape(brand["name"])}</option>'
            for brand in brands.values()
        )
        brand_field = render("components/brand-filter.html", options=options)

    return render(
        "components/catalog.html",
        fixed_brand=fixed_brand,
        filters=render("components/filters.html", brand_field=brand_field),
        count=len(cars),
        cards="\n".join(render_car(car, brands, prefix) for car in cars),
    )


def write_page(filename, title, description, active, body, page_style):
    prefix = "../" if "/" in filename else ""
    styles = ["base", "components", page_style]
    stylesheets = "\n".join(
        f'<link rel="stylesheet" href="{prefix}css/{name}.css">' for name in styles
    )
    html = render(
        "layout.html",
        title=escape(title),
        description=escape(description),
        prefix=prefix,
        stylesheets=stylesheets,
        navigation=render_navigation(active, prefix),
        body=body,
    )
    (ROOT / filename).write_text(html, encoding="utf-8")
    return filename


def build():
    formatter = ROOT / "node_modules/prettier/bin/prettier.cjs"
    if not formatter.exists():
        raise SystemExit("Run npm install (or pnpm install) before building.")

    data = read_json("data/catalog.json")
    home = read_json("data/home.json")
    brands = {brand["id"]: brand for brand in data["brands"]}
    cars = data["cars"]
    by_id = {car["id"]: car for car in cars}
    passenger_cars = [car for car in cars if car["brand"] != "special"]
    special_cars = [car for car in cars if car["brand"] == "special"]
    brand_count = len(brands)
    pages = []

    home_body = render(
        "pages/home.html",
        vehicle_count=len(passenger_cars),
        brand_count=brand_count,
        featured_cards="\n".join(
            render_car(by_id[key], brands) for key in home["featuredCars"]
        ),
        featured_brands="\n".join(
            render_brand_card(brands[key], passenger_cars)
            for key in home["featuredBrands"]
        ),
        spotlight_image=escape(by_id[home["spotlightCar"]]["image"]),
    )
    pages.append(
        write_page(
            "index.html",
            "Driven by obsession",
            f"Explore 3A3D: an automotive portfolio featuring iconic cars, {brand_count} manufacturers and a passion for design.",
            "home",
            home_body,
            "home",
        )
    )

    brand_body = render(
        "pages/brands.html",
        brand_count=brand_count,
        brand_cards="\n".join(
            render_brand_card(brand, passenger_cars) for brand in brands.values()
        ),
    )
    pages.append(
        write_page(
            "brand.html",
            "Brands",
            f"Explore {brand_count} automotive manufacturers and discover every vehicle in the 3A3D showcase.",
            "brands",
            brand_body,
            "catalog",
        )
    )

    collection_body = render(
        "pages/collection.html",
        catalog=render_catalog(passenger_cars, brands),
        special_cards="\n".join(render_car(car, brands) for car in special_cars),
    )
    pages.append(
        write_page(
            "collection.html",
            "Collection",
            "Browse the complete 3A3D vehicle collection. Search by model, manufacturer, drivetrain or editorial collection.",
            "collection",
            collection_body,
            "catalog",
        )
    )

    for brand in brands.values():
        brand_cars = [car for car in passenger_cars if car["brand"] == brand["id"]]
        body = render(
            "pages/brand.html",
            name=escape(brand["name"]),
            count=f"{len(brand_cars):02}",
            catalog=render_catalog(brand_cars, brands, brand["id"]),
        )
        pages.append(
            write_page(
                f"brand/{brand['id']}.html",
                brand["name"],
                f"Discover {len(brand_cars)} {brand['name']} models in the 3A3D automotive showcase, with specifications and vehicle filters.",
                "brands",
                body,
                "catalog",
            )
        )

    pages.append(
        write_page(
            "about.html",
            "About the project",
            "Learn about 3A3D, a student automotive showcase by KenSei, built with HTML, CSS and vanilla JavaScript.",
            "about",
            render("pages/about.html"),
            "pages",
        )
    )
    pages.append(
        write_page(
            "support.html",
            "Contact & FAQ",
            "Contact the creator of 3A3D, report a vehicle specification correction and learn more about this student showcase.",
            "contact",
            render("pages/contact.html"),
            "pages",
        )
    )

    # 每次生成后自动排版，避免下次更新车型又变回长行。
    subprocess.run(
        ["node", str(formatter), "--write", *pages],
        cwd=ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print(f"Generated and formatted {len(pages)} pages from {len(cars)} vehicles.")


if __name__ == "__main__":
    build()
