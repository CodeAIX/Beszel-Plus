# Beszel+ 流量统计项目

产品名Beszel+；GitHub仓库[CodeAIX/Beszel-Plus](https://github.com/CodeAIX/Beszel-Plus)。已实施S1–S4采集、存储、API和界面；S5候选镜像/上游维护流水线已接入；已发布包含紧凑流量列及磁盘后列顺序的测试候选，本机已升级；stable尚待24小时观察。

| 文档 | 用途 |
|---|---|
| [导入已有系统](../IMPORT_SYSTEMS.md) | YAML 增量导入、去重与已有 Agent 接入边界 |
| [CANDIDATE.md](CANDIDATE.md) | 当前可匿名拉取的固定镜像、源码与验收状态 |
| [UI_COMPACT_COLUMN.md](UI_COMPACT_COLUMN.md) | 已发布的紧凑流量列、双色进度条与列顺序 |
| [CODEX_START.md](CODEX_START.md) | 当前开发入口与阶段约束 |
| [SPEC-v1.1.md](SPEC-v1.1.md) | 唯一当前实施规格；SPEC-v1.0保留历史 |
| [REVIEW.md](REVIEW.md) | 审查结论、原文问题与修订决策 |
| [IMPLEMENTATION_MAP.md](IMPLEMENTATION_MAP.md) | 固定上游源码挂载点、工具链及最小改动 |
| [S5_REPORT.md](S5_REPORT.md) | 候选发行、双架构镜像、补丁与自动上游合并 |
| [S4_REPORT.md](S4_REPORT.md) | 流量界面、精确配额、桌面/窄屏与本地Docker验证 |
| [S3_REPORT.md](S3_REPORT.md) | 认证API、账单周期、权限与数据质量 |
| [S2_REPORT.md](S2_REPORT.md) | Hub独立持久化、队列、幂等及双通道验证 |
| [S1_REPORT.md](S1_REPORT.md) | Agent/协议/Docker只读CLI阶段交付与实测 |
| [DOCKER_AGENT.md](DOCKER_AGENT.md) | 当前VPS Docker Agent的集成与权限/UTC边界 |
| [S0_REPORT.md](S0_REPORT.md) | 实际完成项、CI证据和未验证项 |
| [GITHUB_MAINTENANCE.md](GITHUB_MAINTENANCE.md) | GitHub开发、自动保留补丁、镜像发布设计 |
| [LOCAL_TESTING.md](LOCAL_TESTING.md) | 当前默认本地Docker测试，独立数据与端口 |
| [FNOS_UPGRADE.md](FNOS_UPGRADE.md) | 既有Docker Hub的测试、升级与成套回滚 |
| [VPS_SETUP.md](VPS_SETUP.md) | Ubuntu/Debian的vnStat安装与UTC/权限检查 |
| fixtures/ | 三种Linux环境的真实脱敏JSON、配置与provenance |

首版为UTC日统计、单VPS单计费接口、日值幂等与覆盖质量展示。现有Beszel资源监控保持原语义。Hub更换镜像之外，目标VPS需vnStat与Plus Agent；旧Agent继续监控但不会自动上报Traffic。
