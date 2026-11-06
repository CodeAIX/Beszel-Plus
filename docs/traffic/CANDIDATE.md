# 当前测试候选版本

版本：`0.21.1-plus.1-candidate.42217473195.1`，上游 `v0.21.1`；源码 `082cae8ed46597e1c29f731c488b848fd96cc24e`。[GitHub Release](https://github.com/CodeAIX/Beszel-Plus/releases/tag/v0.21.1-plus.1-candidate.42217473195.1) 附带完整补丁、提交清单、源码/镜像 manifest 与 SHA256SUMS。

本轮合并发布：

- [已有系统一键导入与流量设置导入导出](../IMPORT_SYSTEMS.md)：原版 YAML 增量导入；流量设置可单独或联合迁移，明确选择后才覆盖已有设置。
- [七天离线缓存](../OFFLINE_HISTORY.md)：Plus Agent 每分钟持久化资源/Docker 指标，断连后继续采样，重连按原时间自动补传。
- 保留已发布的[紧凑流量列](UI_COMPACT_COLUMN.md)与 vnStat 日值账单功能。

镜像发布在 GHCR（不是 Docker Hub registry），均支持 `linux/amd64`、`linux/arm64`：

```text
# Hub 管理端
ghcr.io/codeaix/beszel-plus/beszel:0.21.1-plus.1-candidate.42217473195.1
# Docker Agent
ghcr.io/codeaix/beszel-plus/beszel-agent:0.21.1-plus.1-candidate.42217473195.1
```

固定摘要：

```text
ghcr.io/codeaix/beszel-plus/beszel@sha256:4e7171aee97e9f1b98210632ed99f93a9ea7925e56acedbfd0572a52a152077a
ghcr.io/codeaix/beszel-plus/beszel-agent@sha256:7eb187810d8fa24b383d24b2c9ca59c5c8f86b137666bc0930f811288a7ffbe6
```

更新步骤见 [Docker Hub / Agent 更新指南](../UPGRADE.md)。先 Hub 后 Agent，保留 Hub 完整原数据与 Agent 原持久卷、KEY/TOKEN/HUB_URL 和原挂载。只有新版 Plus Agent 会采集普通指标缓存。默认缓存目标 7 天、容量上限 256 MiB；容量不足会提前淘汰并提示。普通缓存不依赖 vnStat；日流量仍需宿主 vnstatd 和已验证的 UTC/只读配置。

[发布流水线](https://github.com/CodeAIX/Beszel-Plus/actions/runs/42217473195) 的 verify、images 均成功：前端 38 项回归与生产构建、Go 全包竞态回归、2 GiB Hub 启动/完整备份恢复，以及双架构 Hub/Agent 镜像发布。发布后另验证附件校验和、不可变源码 tag、新历史迁移/协议清单、补丁在固定官方上游的完整回放、匿名读取两个平台的 OCI 清单与标签，并分别实际匿名拉取 amd64/arm64 的两个镜像。公开 Agent 的 vnStat 2.13 CLI 在隔离网络与只读配置/数据库挂载下可成功查询现有测试库。

本机 18091 的原预览已切换为公开 Hub 摘要，10 台既有 VPS 在线，系统配置、用户授权、Hub 密钥、Agent 指纹和流量设置保留；未升级这些 VPS 的 Agent。隔离的 18093 实例已切换为本版公开 Hub/Agent 摘要，原 Agent 缓存保留，新样本继续同步。七天边界使用受控时间和模拟数据验证；真实断线补传已在相同功能源码本地实测约 195 秒，包含 Agent 重启与 Hub 再重启去重；不宣称新版已实际连续运行七天。

仍为候选版，不提供 stable/latest 别名，不自动更新 fnOS/生产 VPS。18090 上的旧候选 `0.21.1-plus.1-candidate.42181555701.1` 与原 24 小时观察继续独立运行，其结果不作为新版本观察结果。
