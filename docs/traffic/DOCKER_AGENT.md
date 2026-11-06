# Docker Agent 集成

用户确认VPS Agent使用Docker，此需求将“受控Docker CLI集成”提升到P0；不再要求迁移systemd Agent。仅增加显式Plus镜像`internal/dockerfile_agent_plus`，原scratch/Alpine/GPU镜像定义保持不变。

## 运行结构

宿主系统的vnstatd负责采集、持久化；Plus Agent镜像内安装发行版vnStat CLI，不启动第二个daemon。宿主vnStat配置和**完整DatabaseDir目录**按只读挂载到容器，CLI使用固定`--config ... --json d --limit 0`查询。不能只挂载单个SQLite主文件而漏掉WAL/SHM，也不能用`immutable=1`忽略正在变化的WAL。

默认关闭，开启时需要：

| 环境变量 | 说明 |
|---|---|
| BESZEL_TRAFFIC_ENABLED | true显式启用 |
| BESZEL_TRAFFIC_REFRESH | 1m–1h，默认5m；无效回退5m并警告 |
| BESZEL_TRAFFIC_VNSTAT_CONFIG | 默认/etc/vnstat.conf；显式绝对路径，CLI每次同时校验UseUTC和SaveInterval |
| BESZEL_TRAFFIC_VNSTAT_PATH | 可选绝对可执行路径，默认LookPath(vnstat) |
| BESZEL_TRAFFIC_TIMEBASE | 仅utc；不是历史UTC证明 |
| BESZEL_TRAFFIC_UTC_VALID_FROM | 必填YYYY-MM-DD；管理员对daemon配置、重启生效与数据历史的UTC起始日确认；此前日桶不导入 |

`UTC_VALID_FROM`是显式部署证明的时间边界，不能随意填为数据库最早日期。当前CLI的UseUTC1仍不足以独立证明已有库/正在运行daemon的历史配置。创建/切换当天不是完整日；后续Hub按source_created、来源更新时间与coverage保守展示。

采集是单后台worker，GetData仅附带原子读取的不可变快照，不等待CLI；错误只返回结构化状态，不携带stderr。未启用不发送Traffic字段，非Linux启用返回unsupported_platform。

## 接入既有Docker部署

先按VPS_SETUP安装/验证宿主vnStat，再保留现有Agent的网络、KEY/TOKEN/HUB_URL、Docker socket与数据卷。使用`supplemental/traffic/compose.agent-traffic.override.yml`作为覆盖配置，服务名需与实际compose一致。

- 设置实际已发布且测试通过的Plus Agent镜像/digest；当前公开候选digest见CANDIDATE.md，尚未提升stable。
- `VNSTAT_CONFIG_PATH`是daemon实际使用的宿主配置文件；容器内固定挂到/etc/vnstat.conf。如配置中DatabaseDir=/custom/path，则宿主目录与容器目标都要为该路径，不能不经核验硬改配置。
- 共享目录需要服务账号可遍历、主库及现有WAL/SHM可读；按实际UID/GID或只读ACL授予权限，不chmod777，不为此添加privileged/root/NET_ADMIN。只读SQLite在部分权限/日志模式下可能失败，先运行CLI预检；失败不放开写挂载，保留原监控并报告permission_denied/exec_failed。
- 原Agent默认运行用户不因本功能强制修改，以免破坏现有Docker socket/GPU读取。新增功能的非root、cap-drop ALL、no-new-privileges、只读卷能力必须独立实测。
- 不自动重启生产容器、改vnstat.conf、改网络或替换自动更新源；部署前保留当前镜像/配置，以便退回。Hub先升级，之后逐台Agent。

参考：[vnStat命令](https://humdi.net/vnstat/man/vnstat.html)、[UseUTC历史限制](https://humdi.net/vnstat/man/vnstat.conf.html)、[Docker只读挂载](https://docs.docker.com/engine/storage/bind-mounts/#use-a-read-only-bind-mount)。本地实测证据归入S1_REPORT；不将容器测试冒充生产VPS已验收。

## 切换前只读预检

设置模板所需变量并备份原Compose后，先运行一次CLI，不启动第二个Agent/daemon：

```sh
# 服务名/文件名需匹配真实部署；保留原用户与其他配置。
docker compose -f compose.yml -f compose.agent-traffic.override.yml run --rm --no-deps --entrypoint vnstat beszel-agent --config /etc/vnstat.conf --showconfig
docker compose -f compose.yml -f compose.agent-traffic.override.yml run --rm --no-deps --entrypoint vnstat beszel-agent --config /etc/vnstat.conf --json d --limit 0
```

确认UseUTC1、真实接口/updated、完整目录只读可读及可信UTC起始日后，才按部署计划切换。当前没有代用户执行生产切换。
