# 当前测试候选版本

版本：`0.21.1-plus.1-candidate.42181555701.1`，上游 v0.21.1；源码 `452a8221545380cdddb9072888e7855d1064a234`。[候选 Release](https://github.com/CodeAIX/Beszel-Plus/releases/tag/v0.21.1-plus.1-candidate.42181555701.1) 附带源码 manifest、补丁、提交清单与 SHA256SUMS。

本版包含已确认的[紧凑流量列](UI_COMPACT_COLUMN.md)：单行百分比、入站/出站双色进度条，列位置紧随磁盘、位于 GPU/负载之前；表格与网格视图同步。

Hub（linux/amd64、linux/arm64，公开/匿名拉取已验证）：

```
ghcr.io/codeaix/beszel-plus/beszel@sha256:2e2fd6121db132a605288f5ebb5a36ff12aacbc705d4b5558f6d8051f51e3a88
```

Docker Agent（同样支持双架构；内置 vnStat CLI，不启动 daemon）：

```
ghcr.io/codeaix/beszel-plus/beszel-agent@sha256:eeb8c10de0b917feec02e965d5e41888e6d2c36a11eec0a6b313aa6b93cecf1c
```

本机 127.0.0.1:18090 已升级至上述两个固定 digest，独立 Colima context 为 colima-beszel-plus。升级前备份完整 Hub 数据目录与 Agent 数据；4 个系统、各自流量设置、历史样例记录/账单汇总均保留，真实计数单调不减，测试 Agent 在线且流量 fresh。原 Agent 数据卷、宿主 vnStat daemon 与用户显示列设置继续沿用。

[完整测试/镜像/Release 流水线](https://github.com/CodeAIX/Beszel-Plus/actions/runs/42181555701) 的 verify、images 两个任务均成功：前端 33 项测试与生产构建、Go 全包 race、2GB Hub 启动及完整目录备份恢复、双架构镜像发布通过。发布后另验证附件校验和、固定源 tag、补丁在固定上游上的干净回放、匿名 OCI 索引/实际 Docker 拉取、镜像版本/来源标签及本机升级。首次候选的发行与权限修正历史见 [S5_REPORT](S5_REPORT.md)。

当前版本的 24 小时健康/资源观察从 **2026-11-06 08:04:26 UTC（北京时间 16:04:26）** 开始，初始样本 health=true、traffic=ok/fresh。报告在本机 `.plus-local/observation/`，current.txt 指向本次目录，结束后生成 summary.json。旧观察单独保留并标记因升级停止；休眠/断连会记录为空缺，不能当连续通过。**目前未完成 24 小时验收，也没有 stable/latest Docker 别名。**

VPS 先按 [VPS_SETUP](VPS_SETUP.md) 安装并核验 UTC 配置，再按 [Docker Agent 集成](DOCKER_AGENT.md) 合并只读挂载。原 Agent 不会自动获得流量功能。当前不操作 fnOS/生产 VPS；需要部署时先备份，先 Hub 后逐台 Agent。
