[← 附录 C 术语表](appendix-c.md) · [全书目录](../README.md#全书目录) · [附录 E 策略内核完整实现 →](appendix-e.md)

---

# 附录 D 参考资料与源码定位

以下链接用于继续核验与阅读。ShenYu 两个固定标签源码已保存在配套工程 `research/`。官方文档页面可能随时间变化，读者应在实施时切换到目标版本。其余链接作为一手资料入口，不表示书中完成了所有版本、模式与插件的逐项实测。

1.  Apache ShenYu 项目与文档：<https://shenyu.apache.org/>。查看插件、数据同步和部署章节。
2.  ShenYu v2.6.0 请求入口：[ShenyuWebHandler.java](https://github.com/apache/shenyu/blob/v2.6.0/shenyu-web/src/main/java/org/apache/shenyu/web/handler/ShenyuWebHandler.java)。关注 `handle`、`sortPlugins`、`DefaultShenyuPluginChain.execute`。
3.  ShenYu v2.6.0 插件基类：[AbstractShenyuPlugin.java](https://github.com/apache/shenyu/blob/v2.6.0/shenyu-plugin/shenyu-plugin-base/src/main/java/org/apache/shenyu/plugin/base/AbstractShenyuPlugin.java)。关注 `execute`、`manyMatchSelector`、缓存资格与未匹配处理。
4.  Spring Cloud Gateway 官方参考：<https://docs.spring.io/spring-cloud-gateway/reference/>。区分 Server WebFlux 与 Server Web MVC。
5.  Project Reactor 官方参考：<https://projectreactor.io/docs/core/release/reference/>。阅读订阅、调度、错误与资源处理。
6.  Kong Gateway 官方文档：<https://developer.konghq.com/gateway/>。阅读实体、插件作用域与部署拓扑。
7.  Apache APISIX 官方文档：<https://apisix.apache.org/docs/>。阅读架构、路由与插件开发阶段。
8.  Higress 官方文档：<https://higress.io/>。阅读架构、Wasm 插件与 AI 网关。
9.  Envoy Gateway 官方文档：<https://gateway.envoyproxy.io/docs/>。核对版本支持矩阵、Gateway API 与扩展策略。
10. Envoy 官方文档：<https://www.envoyproxy.io/docs/envoy/latest/>。阅读 HTTP 连接管理、过滤器、超时与 xDS。
11. Kubernetes Gateway API：<https://gateway-api.sigs.k8s.io/>。阅读角色、HTTPRoute、ReferenceGrant 与一致性支持。
12. HTTP Semantics，RFC 9110：<https://www.rfc-editor.org/rfc/rfc9110>。核对方法语义、幂等与 Retry-After。
13. HTTP/1.1，RFC 9112：<https://www.rfc-editor.org/rfc/rfc9112>。核对消息解析与请求边界。
14. HTTP 429，RFC 6585：<https://www.rfc-editor.org/rfc/rfc6585>。核对 Too Many Requests 语义。
15. JWT 最佳实践，RFC 8725：<https://www.rfc-editor.org/rfc/rfc8725>。核对算法约束与令牌验证边界。

---

[← 附录 C 术语表](appendix-c.md) · [全书目录](../README.md#全书目录) · [附录 E 策略内核完整实现 →](appendix-e.md)
