# Beszel+ 流量统计项目

产品名Beszel+；GitHub仓库[CodeAIX/Beszel-Plus](https://github.com/CodeAIX/Beszel-Plus)。当前为S0审查阶段，还没有可部署的流量功能镜像。

| 文档 | 用途 |
|---|---|
| [CODEX_START.md](CODEX_START.md) | 当前开发入口与阶段约束 |
| [SPEC-v1.1.md](SPEC-v1.1.md) | 唯一当前实施规格；SPEC-v1.0保留历史 |
| [REVIEW.md](REVIEW.md) | 审查结论、原文问题与修订决策 |
| [IMPLEMENTATION_MAP.md](IMPLEMENTATION_MAP.md) | 固定上游源码挂载点、工具链及最小改动 |
| [S0_REPORT.md](S0_REPORT.md) | 实际完成项、CI证据和未验证项 |
| [GITHUB_MAINTENANCE.md](GITHUB_MAINTENANCE.md) | GitHub开发、自动保留补丁、镜像发布设计 |
| [LOCAL_TESTING.md](LOCAL_TESTING.md) | 当前默认本地Docker测试，独立数据与端口 |
| [FNOS_UPGRADE.md](FNOS_UPGRADE.md) | 既有Docker Hub的测试、升级与成套回滚 |
| [VPS_SETUP.md](VPS_SETUP.md) | Ubuntu/Debian的vnStat安装与UTC/权限检查 |
| fixtures/ | 三种Linux环境的真实脱敏JSON、配置与provenance |

首版为UTC日统计、单VPS单计费接口、日值幂等与覆盖质量展示。现有Beszel资源监控保持原语义。Hub更换镜像之外，目标VPS需vnStat与Plus Agent；旧Agent继续监控但不会自动上报Traffic。
