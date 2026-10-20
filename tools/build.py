from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent.parent
book=root.joinpath('manuscript/book.md').read_text()
insertions={
'## 1.2 数据平面与控制平面':'![图 1：一次请求的主要处理阶段](assets/request.svg)\n\n',
'## 7.2 超时是一条预算链':'![图 2：熔断状态转换的主要路径](assets/breaker.svg)\n\n',
'## 8.2 乱序、重复、断线与删除':'![图 3：配置发布与应用确认](assets/config.svg)\n\n'}
for target,content in insertions.items():book=book.replace(target,content+target)
appendix='\n# 附录 E 策略内核完整实现\n\n本附录与配套工程文件同步生成，方便仅持有 EPUB 的读者复制实验。需要 Python 3.10 或以上版本。熔断模型采用连续失败阈值，不是滚动窗口错误率模型；同一时刻仅允许一个半开探测。生产代码需要并发同步与取消策略。\n\n'
for name in ('gateway_core.py','test_gateway_core.py'):
    appendix+=f'## {name}\n\n```python\n'+root.joinpath('examples',name).read_text()+'```\n\n'
book=book.replace('# 结语：设计的目标是可解释的行为',appendix+'# 结语：设计的目标是可解释的行为')
root.joinpath('dist').mkdir(exist_ok=True)
root.joinpath('dist/完整书稿.md').write_text(book)
subprocess.run(['pandoc','dist/完整书稿.md','--from=markdown','--to=epub3','--toc','--toc-depth=2','--split-level=1','--css=tools/book.css','--epub-cover-image=assets/cover.svg','--resource-path=.:assets','-o','dist/API网关设计与实现.epub'],cwd=root,check=True)

# Keep the browser reader synchronized with the EPUB.
subprocess.run(['python3', 'tools/build_web.py'], cwd=root, check=True)

# GitHub Markdown uses the same manuscript and diagrams.
subprocess.run(['python3', 'tools/build_github.py'], cwd=root, check=True)
