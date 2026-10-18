"""One-time migration from the original static pages. Run before build.py."""

from pathlib import Path
import re, json, html

ROOT = Path(__file__).resolve().parents[1]
if (ROOT / "data/catalog.json").exists():
    raise SystemExit(
        "Migration already completed. Edit data/catalog.json and run scripts/build.py instead."
    )
brands, cars, differences = [], {}, []
classic = set(
    re.findall(r"<h2>(.*?)</h2>", (ROOT / "collection.html").read_text(encoding="utf-8"))
)
for page in sorted((ROOT / "brand").glob("*.html")):
    source = page.read_text(encoding="utf-8")
    name = html.unescape(re.search(r"<h1>(.*?)</h1>", source)[1])
    logo = next(
        (
            p.name
            for p in (ROOT / "logo_image").iterdir()
            if p.stem.lower().replace("_logo", "").replace("_", "").replace("-", "")
            == page.stem
        ),
        None,
    )
    if not logo:
        raise ValueError(f"Missing logo: {name}")
    brands.append(dict(id=page.stem, name=name, logo="logo_image/" + logo))
    for block in source.split('<div class="car"')[1:]:
        title = html.unescape(re.search(r"<h2>(.*?)</h2>", block)[1])
        image = re.search(r'<img src="([^"]+)"', block)[1].removeprefix("../")
        specs = {
            html.unescape(k.strip()): html.unescape(v.strip())
            for k, v in re.findall(r"<th>(.*?)</th>\s*<td>(.*?)</td>", block, re.S)
        }
        power = re.search(r"([\d,]+)\s*bhp", specs.get("Power", ""))
        drive = {
            "Rear-Wheel Drive": "rwd",
            "Front-Wheel Drive": "fwd",
            "All-Wheel Drive": "awd",
            "Four-Wheel Drive": "4wd",
        }.get(specs.get("Drive type"), "other")
        key = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        topics = ["classic"] if title in classic else []
        # Only the AE86 is tagged until other exact variants have been verified.
        if title == "Toyota AE86":
            topics.append("initial-d")
        cars[key] = dict(
            id=key,
            name=title,
            brand=page.stem,
            image=image,
            specs=specs,
            power=int(power[1].replace(",", "")) if power else None,
            drive=drive,
            topics=topics,
        )

for page in [ROOT / "index.html", ROOT / "collection.html"]:
    for block in page.read_text(encoding="utf-8").split('<div class="car"')[1:]:
        title = html.unescape(re.search(r"<h2>(.*?)</h2>", block)[1])
        key = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        specs = {
            html.unescape(k.strip()): html.unescape(v.strip())
            for k, v in re.findall(r"<th>(.*?)</th>\s*<td>(.*?)</td>", block, re.S)
        }
        if key in cars:
            if specs != cars[key]["specs"]:
                differences.append(
                    dict(
                        name=title,
                        page=page.name,
                        resolution="Brand-page specifications retained as the single source of truth.",
                    )
                )
        else:
            cars[key] = dict(
                id=key,
                name=title,
                brand="special",
                image=re.search(r'<img src="([^"]+)"', block)[1],
                specs=specs,
                power=None,
                drive="other",
                topics=["special"],
            )

catalog = dict(
    brands=brands,
    cars=list(cars.values()),
    specificationNotes=differences,
    editorialSources=[
        dict(
            topic="initial-d",
            cars=["toyota-ae86"],
            url="https://licensing.kodansha.com/title/initial-d/",
            note="Confirms the AE86 association; catalogue specifications do not represent a screen-used or modified car.",
        )
    ],
)
(ROOT / "data/catalog.json").write_text(
    json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(
    f"{len(brands)} brands, {len(cars)} vehicles, {len(differences)} duplicate specification differences"
)
