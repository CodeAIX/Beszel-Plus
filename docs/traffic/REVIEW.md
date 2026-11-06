# Beszel+ 开发规格审查

审查日期：2026-11-06。结论：总体架构合理，v1.0 不能直接作为无歧义的开发/上线契约；已修订为 [SPEC-v1.1.md](SPEC-v1.1.md)。本次属于 S0，不代表流量功能已实现。用户在审查中将后续测试环境改为本机，fnOS暂不测试；当前方案以LOCAL_TESTING为准。

## 可以保留的设计

- vnStat 负责本机持久化，Agent 经现有认证通道上报，Hub 独立表保存；职责清楚、侵入范围小。
- 绝对日值替换、复合唯一键、旧 Agent 降级、失败与原监控隔离，方向正确。
- 单一计费网卡、UTC 日界、账单日 1–28、缺失不填零、与云账单差异说明，适合作为首版边界。
- 保留原 UI、PocketBase、通知与部署架构；P1 告警和 Docker Agent 专门集成不挤入 P0。
- 官方最新稳定版本的 API 查询仍返回 v0.21.1；9 个 Existing 路径已逐项核对存在。

## 必须修正或补充

| 优先级 | 原文定位 | 问题及影响 | v1.1 决策/验收 |
|---|---|---|---|
| P0 | §3.1、§4.1、§6.3 | `--showconfig` 只能说明本次 CLI 配置，不能证明 daemon 用相同配置，更不能证明旧日桶已经 UTC；改 UseUTC 不转换历史 | 对齐配置路径与 daemon，记录可信 UTC 起始日；未知历史不当 UTC 真值导入；新库创建首日也不能声称全天完整 |
| P0 | §2、§3.1、S1 | `gatherStats` 持全局 mutex，直接追加同步 CLI 会卡住 WS/SSH 和正常指标；仅3秒超时不等于无影响 | 独立受控刷新，GetData 取不可变缓存；包括冷启动、cache hit、退出/超时/竞态测试 |
| P0 | §4.1、§6.3 | 观察时间刷新不等于 vnstatd 数据刷新，daemon 停止但 CLI 成功会被误认为 fresh；15m stale 与允许1h刷新冲突 | 每接口源 updated/created、采集刷新间隔；观察/源新鲜度分别判断，阈值与刷新/保存周期匹配 |
| P0 | §5.5 | 同一 observed_at 不同值未定义；来源重建、异常下降和状态乱序需一致处理 | 同时同值 no-op，同时间异值冲突；状态也禁止倒退；reset 诊断保持，不悄悄清除；校验未来时间 |
| P0 | §7.3 | “非成员一律403”与 SHARE_ALL_SYSTEMS 的上游 systems 写规则有冲突 | 当前上游 share-all=true 放行普通认证非成员读写，readonly拒写；新设置沿用这条规则并覆盖测试。离线/暂停系统从 DB 授权 |
| P0 | §11 | 未定义 fnOS Docker 原地升级路径；Hub升级不能代替 Agent升级 | Hub 更换镜像并重建，保留挂载与参数；旧 Agent 正常监控，目标 VPS 另装 vnStat、升级 Plus Agent |
| P0 | §11 | 未定义补丁维护与上游自动跟随；上游复用 key7 即使文本合并成功也可能协议冲突 | 稳定 tag/SHA → 候选分支三方合并 → 语义检查/测试 → 不可变候选镜像；冲突停，stable 与候选区分 |
| P1 | §3.1、§5.5 | CLI JSON 256KiB 与16×400是不同上限；每分钟重传整段历史可能产生写风暴；stderr未限制 | 限制双输出与Hub输入；实际测报文边界；批量写、有界等待、幂等且跳过重复快照，不无限启动goroutine |
| P1 | §5.2 | OnlyInt 不足以证明底层 SQLite 类型为 INTEGER；原始每项安全不等于聚合也安全 | 使用实际 PocketBase 往返验证；日值/求和/API均检查2^53-1边界 |
| P1 | §10.5 | 原测试命令遗漏 `testing` build tag，会跳过大量 Hub 集成测试；Web 无 test/typecheck script | Go 使用 `-tags=testing`；前端已有 bun:test 文件，执行 `bun test ./tests`，正式 build含 tsc；新增套件必须明确入口 |
| P1 | §12 | S0“只阅读不改代码”与要求保存fixture/独立commit表述矛盾 | S0允许文档、隔离采样工具及CI，不改监控业务代码 |

## 实测发现

首轮 GitHub Linux 验证在三种发行版均暴露：`--showconfig` 会用注释形式输出默认项。原规格预检的 `grep -E "^(UseUTC|...)"` 会漏掉默认的 `UseUTC 0`。验证脚本已按真实输出修正；真实结果/版本/运行链接见 [S0_REPORT.md](S0_REPORT.md)，不得用想象的 JSON 结构替代 fixture。

## 未做的工作

本次未修改 Go/React/数据库 migration、未升级 fnOS 容器、未连接或修改 VPS。自动上游跟随和镜像发布流程目前是已明确的实施要求，尚非可用功能。当前唯一新 CI 是手动触发的隔离 vnStat 验证。

## 核验来源

- 固定源码：[v0.21.1 commit](https://github.com/henrygd/beszel/tree/e2ed147a5aa6472e6462521632ccc7101668132c)，具体位置见 IMPLEMENTATION_MAP。
- [官方 Hub Docker 安装](https://beszel.dev/guide/hub-installation)：8090与`/beszel_data`；当前已装环境仍需核对。
- [vnStat CLI](https://humdi.net/vnstat/man/vnstat.html)、[配置](https://humdi.net/vnstat/man/vnstat.conf.html)、[daemon](https://humdi.net/vnstat/man/vnstatd.html)：JSON、UTC、保存时机及历史限制。
- [GitHub schedule](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)、[GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)：默认分支调度、60天无活动停用、包初始可见性及digest拉取。
