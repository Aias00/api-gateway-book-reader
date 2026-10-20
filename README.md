# 《API 网关设计与实现》

在 GitHub 中点击下方章节即可直接阅读，无需下载或启动服务。

[在线阅读](https://aias00.github.io/api-gateway-book-reader/) · [GitHub 章节阅读](chapters/00-preface.md) · [下载 EPUB](dist/API网关设计与实现.epub)

<!-- BOOK_TOC_START -->
## 全书目录

- [前言：从一次请求走进网关](chapters/00-preface.md)
- [第 1 章 网关边界与请求生命周期](chapters/ch01.md)
- [第 2 章 ShenYu 的模块地图与阅读方法](chapters/ch02.md)
- [第 3 章 插件链：顺序、异步与短路](chapters/ch03.md)
- [第 4 章 选择器、规则与确定性匹配](chapters/ch04.md)
- [第 5 章 匹配性能与缓存一致性](chapters/ch05.md)
- [第 6 章 限流：从令牌桶到租户配额](chapters/ch06.md)
- [第 7 章 熔断、隔离、超时与重试](chapters/ch07.md)
- [第 8 章 动态配置：把发布当作分布式协议](chapters/ch08.md)
- [第 9 章 安全边界与协议处理](chapters/ch09.md)
- [第 10 章 六种网关的共同坐标系](chapters/ch10.md)
- [第 11 章 Spring Cloud Gateway：应用式网关的取舍](chapters/ch11.md)
- [第 12 章 Kong：围绕 API 实体组织治理](chapters/ch12.md)
- [第 13 章 APISIX：动态路由与插件执行阶段](chapters/ch13.md)
- [第 14 章 Higress：Envoy、Wasm 与 AI 流量](chapters/ch14.md)
- [第 15 章 Envoy Gateway 与 Kubernetes Gateway API](chapters/ch15.md)
- [第 16 章 可观测、容量与性能实验](chapters/ch16.md)
- [第 17 章 选型与迁移：用约束收敛答案](chapters/ch17.md)
- [第 18 章 综合设计：电商平台网关方案](chapters/ch18.md)
- [第 19 章 实现一个可验证的最小网关内核](chapters/ch19.md)
- [第 20 章 故障案例与排障路径](chapters/ch20.md)
- [附录 A 思考题参考答案](chapters/appendix-a.md)
- [附录 B 设计评审清单](chapters/appendix-b.md)
- [附录 C 术语表](chapters/appendix-c.md)
- [附录 D 参考资料与源码定位](chapters/appendix-d.md)
- [附录 E 策略内核完整实现](chapters/appendix-e.md)
- [结语：设计的目标是可解释的行为](chapters/99-afterword.md)
<!-- BOOK_TOC_END -->

电子书： [dist/API网关设计与实现.epub](dist/API网关设计与实现.epub)

20 章正文、5 个附录，以 ShenYu v2.6.0 固定源码为主线，讨论插件链、选择器与规则、限流、熔断、动态配置，对比 Spring Cloud Gateway、Kong、APISIX、Higress 与 Envoy Gateway。另含安全、容量、迁移、故障案例和 Python 教学内核。

## 文件

- `manuscript/book.md`：可编辑正文。
- `dist/完整书稿.md`：构建时合入插图和完整实验代码的书稿。
- `examples/`：标准库实验和 6 项确定性测试。
- `assets/`：SVG 封面和三幅流程图。
- `tools/`：构建、内容审计与样式。
- `research/`：两份固定版本源码、文档抓取与校验记录。

## 重建

需要 Python 3.10+ 与 Pandoc 3.x：

```sh
python3 tools/make_assets.py
python3 -m unittest discover -s examples -v
python3 tools/build.py
python3 tools/audit.py
```

使用官方 EPUBCheck 5.3.0 与 Java 运行时校验：

```sh
java -jar /path/to/epubcheck.jar dist/API网关设计与实现.epub
```

`tools/render.cjs` 为本机排版检查脚本，使用已安装的 Playwright 和 Chromium；迁移环境时需调整模块与浏览器路径。`research/render-audit.json` 保存桌面与手机宽度检查结果，`dist/` 中有章节截图。渲染检查使用解包后的实际 EPUB 内容，不等同于所有阅读器兼容性认证。

## 验证范围

EPUBCheck：0 fatals / 0 errors / 0 warnings。所有内部链接和 XML 已检查。6 项策略测试通过。教学模型不是 HTTP 代理；未声称在真实集群部署六种产品，也未给出虚构性能排名。产品架构入口使用一手文档，实际配置须锁定产品版本。

## GitHub Pages 网页阅读

网页版位于 `site/`，包含完整书稿、目录、全文搜索、章节与小节链接、阅读位置记忆、字号调整、深浅主题和 EPUB 下载，支持手机阅读。阅读位置保存在当前浏览器的本地存储。页面采用与 JVM 故障排查书站一致的长页阅读方式，另支持纸色主题、跟随系统主题和代码复制；正文不依赖 JavaScript 加载。

构建和启动：

```sh
python3 tools/build.py       # 更新完整书稿及 EPUB
python3 tools/build_web.py   # 从完整书稿生成静态阅读站
python3 -m http.server 8878 --bind 127.0.0.1 --directory site
```

本地预览时打开 http://127.0.0.1:8878/ 。`site/index.html` 也可直接打开；网站无需后端或外部 CDN。公网访问可把整个 `site/` 目录上传至静态网站托管服务（如 GitHub Pages、Cloudflare Pages、Nginx）；入口文件为 `index.html`，无需 SPA 重写，章节链接使用 URL fragment。托管到子路径也可使用相对资源路径。公开阅读站地址：https://aias00.github.io/api-gateway-book-reader/ 。

浏览器验收脚本为 `tools/test_web.cjs`，可通过 `PLAYWRIGHT_MODULE`、`CHROMIUM_PATH` 与 `BOOK_URL` 指定本机依赖和站点地址。结果保存到 `research/web-audit.json`。


## 发布到 GitHub

仓库首页上方的目录链接直接指向 `chapters/` 内的 Markdown，上传仓库后即可在 GitHub 阅读，保留插图、代码高亮、表格和上一章／下一章导航，无需 GitHub Pages。

如需带搜索、主题和进度记忆的网页阅读器，在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**，再运行 **Actions → Publish book to GitHub Pages → Run workflow**。推送到 `main` 或 `master` 且修改 `site/` 时也会自动发布。实际网页地址以部署作业输出为准。独立阅读站仓库：https://github.com/Aias00/api-gateway-book-reader 。

统一更新所有阅读格式：

```sh
python3 tools/build.py  # EPUB、静态阅读站、GitHub Markdown 章节
python3 tools/audit_github.py
```

只重新生成 GitHub 章节：`python3 tools/build_github.py`。生成结果已保留在仓库中，读者无需运行构建工具。
