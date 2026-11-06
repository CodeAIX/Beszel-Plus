#!/usr/bin/env python3
"""Write reviewable release notes for the exact published source and images."""
import json
from pathlib import Path
m = json.loads(Path('.plus-release/source-manifest.json').read_text())
v = m['plus_version']
repo = 'https://github.com/CodeAIX/Beszel-Plus'
hub = 'ghcr.io/codeaix/beszel-plus/beszel:' + v
agent = 'ghcr.io/codeaix/beszel-plus/beszel-agent:' + v
notes = f'''Beszel+ {v}

本次合并发布：

- **已有系统一键导入**：预览原版 YAML 后批量增量导入、去重，保留已有系统。
- **流量设置导入导出**：可单独迁移，也可与系统配置联合导出导入；覆盖已有设置需明确选择。
- **7 天离线缓存**：Plus Agent 每分钟采样并持久化，Hub 重连自动补传 CPU、内存、磁盘、Docker 等指标，保留原时间且不重放告警。

测试源码：`{m['plus_commit']}`，上游 `{m['tag']}`。Hub 与 Agent 均支持 `linux/amd64`、`linux/arm64`，镜像发布在 GHCR。

Hub：
```
{hub}
```
Agent：
```
{agent}
```

固定摘要：
- Hub：`{m['images']['hub']}`
- Agent：`{m['images']['agent']}`

**更新顺序：先 Hub，后逐台 Agent。** 修改原 Compose 中对应 image，保留 Hub 的 `/beszel_data`、Agent 的 `/var/lib/beszel-agent` 原数据卷，以及 KEY/TOKEN/HUB_URL、网络与原有挂载。原版 Agent 仍可连接新 Hub，但缓存需要本版 Plus Agent；仅升级 Hub 无法保存原版 Agent 的离线指标。

例如原服务名为 beszel / beszel-agent 时，分别在它们各自的部署目录执行：
```sh
# Hub 主机：先在原 Compose 中更换上述 Hub 镜像。
docker compose pull beszel
docker compose up -d --no-deps beszel

# 每台 VPS：在原 Compose 中更换上述 Agent 镜像，保留原数据卷。
docker compose pull beszel-agent
docker compose up -d --no-deps beszel-agent
```

服务名以实际部署为准。详细步骤、备份、fnOS 图形界面、docker run 与回退说明见 [Docker 更新指南]({repo}/blob/plus/main/docs/UPGRADE.md)。YAML 导出不含 Hub 私钥或监控历史，不能代替完整数据备份。

默认缓存目标 7 天、压缩容量上限 256 MiB；容量不足会提前清理并提示。不能补回启用之前、Agent/VPS 停机期间或已经淘汰的数据。普通缓存不依赖 vnStat；流量日统计仍需宿主 vnstatd 和原有只读挂载。

候选发布：尚无 stable/latest 别名，不自动部署生产。七天边界与周/月汇总通过受控测试，本地真实断线与重启补传已验证；尚未进行新版连续七天运行验收。附件包含完整补丁、源码清单、迁移/协议版本与校验和。
'''
Path('.plus-release/notes.md').write_text(notes)
