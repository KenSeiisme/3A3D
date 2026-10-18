# 3A3D — Driven by obsession

汽车展示作品集。保留静态 HTML、CSS 和原生 JavaScript，线上不需要框架、Python 或数据库。

## 文件怎么找

```text
css/
  base.css           颜色变量、字体、基础布局、通用按钮
  components.css     导航、车型卡片、品牌卡片、页脚
  home.css           首页与专题展示
  catalog.css        页面标题、搜索筛选、车型目录
  pages.css          About 与 Contact
data/
  catalog.json       所有品牌、车型、参数与分类
  home.json          首页精选车型与品牌 ID
  README.md          新增车型与品牌的完整说明
templates/
  layout.html        所有页面共用的 head、导航与页脚
  components/        卡片、参数行、筛选栏等可复用片段
  pages/             各页面的独立内容模板
scripts/
  build.py           读取数据与模板，生成并排版 HTML
  optimize-assets.cjs 压缩新图片并更新目录中的图片路径
  verify.cjs         浏览器验收测试
  extract-catalog.py 已完成的一次性旧页面迁移，日常无需运行
project.js           手机菜单、车型筛选、视频控制
index.html 等        自动生成的静态页面，供浏览器与 Vercel 使用
```

## 修改与新增车型

首次开发安装工具：

```sh
npm install
```

也可以使用 `pnpm install`，仓库提供 `pnpm-lock.yaml`。

- 改外观：编辑对应的 `css/` 文件。
- 改导航、页脚或 Logo：编辑 `templates/layout.html`。页眉和页脚都使用原始 `image/3A-3D.png`，颜色不会因文字样式而不同。
- 改页面内容：编辑 `templates/pages/` 内对应模板。
- 新增车型：图片放入 `car_vector_image/`，在 `data/catalog.json` 的 `cars` 中增加一条记录。字段与完整步骤见 [车型维护说明](data/README.md)。
- 改首页精选：编辑 `data/home.json` 中的车型与品牌 ID。

更新图片后执行：

```sh
node scripts/optimize-assets.cjs
python scripts/build.py
```

只改数据或模板时，直接运行 `python scripts/build.py`。生成器会自动更新对应品牌页、Collection、车型及品牌数量，并通过 Prettier 保留正常缩进与换行。

**不要直接修改生成后的 HTML**，因为下次构建会覆盖它。只改 CSS 或 JavaScript 时不需要重新生成 HTML。

## 排版与预览

```sh
npm run format
npm run format:check
npm run preview
```

预览地址是 `http://127.0.0.1:8766`。HTML、CSS、JavaScript、JSON 与 Markdown 使用仓库内的 Prettier 配置；Python 使用 Black，配置在 `pyproject.toml`：

```sh
python -m pip install black==25.1.0
python -m black scripts
```

旧的 `style.css`、`nav.css`、各页面同名 CSS 和 `brand/car-brand.css` 已删除；生成器不会再创建它们。每个页面只加载基础、公共组件及自身所需的 CSS 模块。

## 验收与部署

执行 `npm run test:build` 可在临时目录验证新增品牌与车型、自动计数和文字转义，不修改实际数据。

启动预览后执行 `npm test`。测试使用 Playwright Chromium 或已安装的 Microsoft Edge；需要时运行 `npx playwright install chromium`。

检查覆盖页面与资源链接、五种屏幕宽度、搜索筛选、排序、浏览器返回恢复、手机菜单、键盘展开参数、关闭 JavaScript 及视频加载失败。结果和截图保存在不提交的 `_qa/`。设置 `TEST_BASE_URL` 可检查部署地址；`BROWSER_PATH` 可指定浏览器。

Vercel 直接发布提交好的静态文件，不安装开发工具、不运行构建。修改数据或模板后，请将生成的 HTML 一起提交。保留原品牌网址和 `support.html`，后者现在是 Contact 页面。

车型参数沿用原项目，属于参考资料。Initial D 专题目前只标记已核实关联的 AE86，来源为 [Kodansha](https://licensing.kodansha.com/title/initial-d/)，参数不代表故事中的改装车辆。
