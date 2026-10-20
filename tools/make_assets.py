from pathlib import Path
from html import escape
A=Path('assets')
A.joinpath('cover.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600" viewBox="0 0 1200 1600">
<rect width="1200" height="1600" fill="#102b46"/>
<path d="M0 1160 L1200 700 L1200 1600 L0 1600Z" fill="#174965"/>
<g fill="none" stroke="#54c8c5" stroke-width="5"><path d="M160 1000H440V850H750V1000H1050"/><path d="M440 1000V1150H750V1000"/><circle cx="160" cy="1000" r="28"/><circle cx="1050" cy="1000" r="28"/></g>
<g fill="#fff" font-family="sans-serif"><text x="100" y="290" font-size="84" font-weight="bold">API 网关</text><text x="100" y="410" font-size="84" font-weight="bold">设计与实现</text><text x="104" y="525" font-size="30">从 ShenYu 核心机制到六种网关的工程实践</text><text x="104" y="650" font-size="26" fill="#97d8dd">插件链 · 路由匹配 · 限流熔断 · 动态配置</text><text x="104" y="1360" font-size="24">ShenYu / Spring Cloud Gateway / Kong</text><text x="104" y="1410" font-size="24">APISIX / Higress / Envoy Gateway</text><text x="104" y="1500" font-size="22" fill="#97d8dd">技术实践版 · 2026</text></g></svg>''')
def diagram(name,title,labels,caption):
    w=1000; parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="300" viewBox="0 0 1000 300"><rect width="1000" height="300" fill="#f3f7fa"/><g font-family="sans-serif"><text x="35" y="45" font-size="25" fill="#102b46">{escape(title)}</text>']
    n=len(labels); step=930/n
    for i,label in enumerate(labels):
        x=35+i*step
        parts.append(f'<rect x="{x}" y="90" width="{step-28}" height="80" rx="8" fill="#174965"/><text x="{x+(step-28)/2}" y="138" text-anchor="middle" font-size="21" fill="white">{escape(label)}</text>')
        if i<n-1:parts.append(f'<path d="M{x+step-25} 130h20m-6 -6l6 6l-6 6" stroke="#174965" stroke-width="3" fill="none"/>')
    parts.append(f'<text x="35" y="230" font-size="20" fill="#24475e">{escape(caption)}</text></g></svg>')
    A.joinpath(name+'.svg').write_text(''.join(parts))
diagram('request','请求路径与可信身份的形成',['接入校验','匹配路由','验证身份','治理预算','代理上游'],'身份验证后生成可信租户；响应、错误与取消沿生命周期回收资源。')
diagram('config','配置发布是一个有确认的过程',['保存意图','校验构建','分发版本','原子应用','生效确认'],'数据面报告 applied revision；断线恢复需要快照校准与缓存失效。')
diagram('breaker','熔断器的受控恢复',['关闭统计','达到阈值','打开拒绝','半开探测','恢复关闭'],'半开探测失败则重新打开；旧请求的迟到结果不得改变新状态。')
