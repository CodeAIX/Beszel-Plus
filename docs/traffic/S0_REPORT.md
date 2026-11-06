# S0 审查与预检报告

日期：2026-11-06（北京时间）。用户已将后续新版测试环境改为本机，暂不需要fnOS；本地为当前默认。当前停在S0，未实现/发布流量功能。

## 基线与仓库

- Fork：[CodeAIX/Beszel-Plus](https://github.com/CodeAIX/Beszel-Plus)，parent为henrygd/beszel；默认分支plus/main。
- 开发基线v0.21.1，commit `e2ed147a5aa6472e6462521632ccc7101668132c`；annotated tag对象 `bd1197b2648258b9ac8ece4f8e7f0890cdce5797`。
- 官方releases/latest查询仍为v0.21.1，发布时间2026-10-22T17:24:08Z；未使用滚动main。
- 源码Existing路径9/9存在、主要函数/协议/迁移/页面入口已检查。映射与风险见IMPLEMENTATION_MAP。
- S0 CI初始提交`a8c00ed`，实测解析修正`da4a48f79a60d6db4fce0acc819bea3765d057e9`；本报告所在文档commit可由Git历史取得，避免自引用SHA。

## 真实 Linux 验证

成功运行：[42157366521](https://github.com/CodeAIX/Beszel-Plus/actions/runs/42157366521)，源码为da4a48f；3/3 matrix jobs成功，命令退出0。CI时间03:34–03:35 UTC，即北京时间11:34–11:35。

| 环境 | vnStat | JSON API | 非root采样/读库 | UTC1/默认UTC0配置识别 | fixture |
|---|---|---|---|---|---|
| Debian12 | 2.10 | `jsonversion="2"` | 通过 | 通过 | fixtures/vnstat-debian12 |
| Debian13 | 2.13 | `jsonversion="2"` | 通过 | 通过 | fixtures/vnstat-debian13 |
| Ubuntu24.04 | 2.12 | `jsonversion="2"` | 通过 | 通过 | fixtures/vnstat-ubuntu24 |

每个环境创建独立临时数据库、同一份UseUTC1配置传给CLI/daemon，vnstatd运行后通过SIGTERM保存、实际执行`vnstat --config <isolated-config> --json d --limit 0`。每份样本含一个真实接口和一个真实日桶，原始输出395–397字节。仅替换接口名和清空alias，字节量/日期/时间戳/结构不造数。保留effective/non-UTC配置、OS、provenance和SHA256；没有上传数据库、原始网卡名或宿主信息。

实测结构含`vnstatversion`、字符串`jsonversion`、`interfaces[].created.timestamp`、`updated.timestamp`、`traffic.day[].date/timestamp/rx/tx`。标准fixtures是实测输出；恶意/边界变体以后另行标为合成测试数据。

首轮[42157217892](https://github.com/CodeAIX/Beszel-Plus/actions/runs/42157217892)失败，3个job均在UTC0断言处退出1：默认配置实际输出`;UseUTC 0`，裸split/只匹配行首关键字无法识别。脚本修正后重跑通过。保留失败原因，不写成首轮全过。

限制：这是临时Linux容器内的短时采样；没有覆盖多接口400天、daemon停机freshness、跨日、原Agent服务账号访问生产库、24小时资源灰度。它验证格式与基本读取方式，不是A01–A09全部通过，也不是生产VPS已就绪。vnStat伪接口不保证参与采集，不把测试中的loopback数据伪装为公网计费。

## 已确定的实施计划

- 使用独立vnStat CLI/可选Traffic/三表/API/UI增量方案；日粒度UTC、单计费接口、账单日1–28、严格幂等。
- S1先冻结JSON version2、来源created/updated、UTC可信边界、collector后台生命周期/缓存契约，再实现Agent；关键原文件保持原样。
- Hub保存独立事务、有界处理/失败隔离，重传不重复计费；API角色、暂停/离线与SHARE_ALL_SYSTEMS分别测试。
- 本机独立Docker项目/数据卷进行新版测试；生产fnOS/VPS暂不连接。fnOS镜像升级与备份文档保留作以后部署参考，不作为当前开发阻塞。
- GitHub作为主要验证/构建场所；未来稳定上游tag自动候选合并、测试及镜像，冲突或语义不兼容则停。S5前不提前声称此流水线可用。

## 当前环境与未决项

| 项目 | 状态与下一步 |
|---|---|
| 本地工具 | GitHub CLI已授权CodeAIX；Go1.27.3 darwin/arm64、bun可用；本地Docker colima未运行且Compose缺失，未启动/安装；改用GitHub临时Linux环境完成采样 |
| 原版测试基线 | 未执行完整Go/Web构建回归；命令和真实scripts已核对，S1前建立基线，不冒报通过 |
| fnOS当前镜像/架构/持久化 | 后续部署再核验；用户改为本地测试，当前不再需要提供 |
| VPS Agent部署方式/目标身份 | 生产未核验，当前使用本地Linux测试Agent，不阻塞开发；未来生产接入再确认。安装命令已备于VPS_SETUP |
| 生产UTC历史与读取权限 | 未验证；上线前检查真实daemon配置/数据库起点与实际Agent账号，旧历史不追认UTC |
| Plus GHCR镜像/自动同步 | 尚未实现或发布；GITHUB_MAINTENANCE已明确设计，继承发行工作流先禁用 |

## 实际检查与结果

- Fork parent/default branch、origin/upstream、tag对象与commit：通过（CLI退出0）。
- 9条Existing文件存在性、关键函数/Go依赖/前端scripts/Dockerfile：通过静态核验；不是运行回归。
- Linux真实fixture/config/nonroot：3/3通过，见成功run；首次失败及修复如上。
- 采样脚本Python语法及`git diff --check`：通过。已下载fixture的JSON解析、SHA256与敏感字段筛查在最终提交前执行，三份JSON/元数据、SHA256一致性、接口匿名化和基本敏感模式筛查均通过；Markdown本地链接/文档副本一致性检查通过。
- A/H/C功能测试、migration/回滚、镜像构建/匿名拉取、fnOS更新、生产VPS安装、E2E/24小时灰度：未执行，功能尚未开发。

本地测试入口见LOCAL_TESTING.md及supplemental/traffic/compose.local.yml；compose及workflow已用Ruby Psych通过YAML语法解析；实际`docker compose config`因本机缺插件失败，语义验证和容器启动尚未完成。

下一阶段为S1；按照原规格S0检查点停下，不自动跨阶段。S0可进行源码设计审查，生产部署证据不因CI成功而自动补齐。
