# 给 Codex 的启动指令｜Beszel+（2026-11-06 修订）

唯一当前实施规格为 `docs/traffic/SPEC-v1.1.md`（工作区根目录同名长文件为副本）；v1.0 保留为历史。先读 `docs/traffic/REVIEW.md`、`IMPLEMENTATION_MAP.md`、`S0_REPORT.md`、`GITHUB_MAINTENANCE.md` 与 `LOCAL_TESTING.md`（当前）与 `FNOS_UPGRADE.md`（以后部署参考）。

- Fork：CodeAIX/Beszel-Plus；默认开发分支 plus/main。origin 为 Fork，upstream 为 henrygd/beszel。
- 实施基线：v0.21.1，commit e2ed147a5aa6472e6462521632ccc7101668132c；不得换成滚动 main。
- 当前仅 S0：允许文档与隔离 Linux 验证 CI，不改监控功能；按 S0_REPORT 的真实完成项与未决项交接。S0 结束后停下；未通过上阶段必测不跨到下一阶段。
- P0：一台 VPS 一个计费网卡、UTC 日粒度、账单日1–28、绝对值幂等 upsert；保留来源与完整性证据，缺失不填0。
- 不修改原网络吞吐、历史采样、既有 CBOR key/动作编号；当前 CombinedData key7可用，每次上游升级重新检查。新增故障不能卡住原采集、使正常指标回滚或误报离线。
- 所有新 API/集合按 systems.users/SHARE_ALL_SYSTEMS 与 readonly 授权；UI 不能写统计真值。
- Hub 镜像更新和 VPS Agent/vnStat 升级是两个步骤。用户最新要求改为本机测试，暂不在fnOS测试；使用独立本地Docker项目/数据卷，不加载生产凭据，不以fnOS信息缺失阻塞开发。以后部署时再核验实际环境与备份/恢复。
- 用户允许协助 VPS 安装 vnStat 或提供代码；先定位并验证目标，使用最小权限，不变更网络/防火墙/代理。安装步骤见 VPS_SETUP.md。CLI/daemon 配置和历史 UTC 边界必须有证据。
- 主要构建/测试/镜像发布放 GitHub Actions；未来上游稳定版自动生成候选+测试+镜像，冲突即停；不声称任意上游改动都能无人工适配。
- 每阶段交付变更、实际测试及退出码、风险、commit SHA；不得把 CI fixture 当生产 VPS 验收或24小时测试。
