"""在临时目录验证新增品牌与车型，不修改实际项目数据。"""

import copy
import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("site_builder", ROOT / "scripts/build.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

with tempfile.TemporaryDirectory(prefix="3a3d-build-") as directory:
    sandbox = Path(directory)
    (sandbox / "data").mkdir()
    (sandbox / "brand").mkdir()

    catalog = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))
    original_count = sum(car["brand"] != "special" for car in catalog["cars"])
    catalog["brands"].append(
        {
            "id": "test-marque",
            "name": "Test & Marque",
            "logo": "image/3A-3D.png",
        }
    )
    added_car = copy.deepcopy(catalog["cars"][0])
    added_car.update(
        {
            "id": "test-marque-example",
            "name": "Test <Example>",
            "brand": "test-marque",
        }
    )
    catalog["cars"].append(added_car)
    (sandbox / "data/catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
    (sandbox / "data/home.json").write_text(
        (ROOT / "data/home.json").read_text(encoding="utf-8"), encoding="utf-8"
    )

    # 临时构建复用已经安装的格式化工具，不复制整个 node_modules。
    formatter = sandbox / "node_modules/prettier/bin/prettier.cjs"
    formatter.parent.mkdir(parents=True)
    formatter.write_text(
        "require("
        + json.dumps(str(ROOT / "node_modules/prettier/bin/prettier.cjs"))
        + ");",
        encoding="utf-8",
    )
    builder.ROOT = sandbox
    builder.build()

    brand_page = (sandbox / "brand/test-marque.html").read_text(encoding="utf-8")
    directory_page = (sandbox / "brand.html").read_text(encoding="utf-8")
    collection = (sandbox / "collection.html").read_text(encoding="utf-8")
    home = (sandbox / "index.html").read_text(encoding="utf-8")
    assert "Test &amp; Marque" in brand_page
    assert "Test &lt;Example&gt;" in brand_page
    assert 'value="test-marque"' in collection
    assert 'href="brand/test-marque.html"' in directory_page
    assert f"{original_count + 1} vehicles to discover" in collection
    assert f'<strong>{len(catalog["brands"])}</strong>' in home
    assert 'class="logo footer-logo"' in brand_page
    assert 'src="../image/3A-3D.png"' in brand_page
    assert not list(sandbox.glob("*.css")), "Build must not recreate obsolete CSS files."

print("PASS isolated build: new brand, vehicle, counts, escaping and no obsolete CSS.")
