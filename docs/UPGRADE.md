# Docker Hub 与 Agent 更新

这里的 Hub 指 Beszel 管理端容器。Beszel+ 镜像发布在 **GitHub Container Registry（GHCR）**，无须 Docker Hub 账号。镜像支持 `linux/amd64`、`linux/arm64`；固定版本、摘要与校验附件见 [当前版本](traffic/CANDIDATE.md) 和 [GitHub Releases](https://github.com/CodeAIX/Beszel-Plus/releases)。

本轮发布包含已有系统一键导入、流量设置单独/联合导入导出，以及每分钟采样、最近 7 天的 Agent 离线缓存与自动补传。按 **先 Hub，后逐台 Agent** 更新。原版 Agent 可继续连接新 Hub，但离线缓存需要新版 Plus Agent。

## 更新前保存原数据

保留当前 Compose、环境变量与镜像版本；停下 Hub 后备份 `/beszel_data` 对应的**完整原数据目录或卷**，包含数据库与身份私钥，再进行镜像切换。YAML 导出不能代替完整 Hub 备份，不包含 Hub 私钥或监控历史。对 Agent 保留 `/var/lib/beszel-agent` 原卷，不要重新生成 KEY/TOKEN 或换为空卷。

下文服务名示例为 `beszel` 和 `beszel-agent`；请替换为原 Compose 的实际服务名。只修改列出的字段，其余原配置继续沿用。原来若使用多个 Compose 文件，命令需沿用同一组 `-f` 参数。

## Hub：Compose 更新

在原 Hub Compose 中将管理端的 `image` 改为：

```yaml
services:
  beszel:
    image: ghcr.io/codeaix/beszel-plus/beszel:${BESZEL_PLUS_VERSION:?Set the release version}
    # 保留原 ports、volumes、environment、networks 等所有配置。
```

在该目录的 `.env` 中设置 Release 给出的版本（不带前缀 v），也可在当前终端导出它。保留 `.env` 的其他内容。随后执行：

```sh
docker compose pull beszel
docker compose up -d --no-deps beszel
docker compose ps beszel
docker compose logs --tail=50 beszel
```

Compose 会读取该目录中的 `.env`。升级后用原地址登录，检查原系统是否在线。“添加系统 → 从 YAML 导入已有系统”与“设置 → YAML 配置”提供导入导出入口。迁移到全新 Hub 时，还要保留原 Hub 身份密钥或另行配置 Agent 的信任关系；只导入 YAML 不会自动建立信任。

## Agent：Compose 更新

在每台 VPS 的原 Agent Compose 中更换镜像，并确认原持久卷仍然存在：

```yaml
services:
  beszel-agent:
    image: ghcr.io/codeaix/beszel-plus/beszel-agent:${BESZEL_PLUS_VERSION:?Set the same release version}
    environment:
      BESZEL_HISTORY_ENABLED: "true"
      BESZEL_HISTORY_MAX_BYTES: "268435456"
      # 合并到原 environment 中，继续保留 KEY、TOKEN、HUB_URL 等。
    volumes:
      # 继续使用原来挂载到此目标的目录或命名卷，不要另建空卷。
      - ./beszel_agent_data:/var/lib/beszel-agent
      # 继续保留原 Docker socket、文件系统等其他挂载。
```

环境变量合并时沿用原来 map 或 list 的语法，不能删除旧字段。示例中的 `./beszel_agent_data` 必须换成原部署实际使用的源；如果原 Agent 没有持久卷，应先将旧容器 `/var/lib/beszel-agent` 内容复制到准备使用的目录，再挂载，而不是丢弃容器中的身份数据。

在 VPS 的 Agent Compose 目录中设置与 Hub 相同的 `BESZEL_PLUS_VERSION`，执行：

```sh
docker compose pull beszel-agent
docker compose up -d --no-deps beszel-agent
docker compose ps beszel-agent
docker compose logs --tail=50 beszel-agent
```

等待约 1–2 分钟，Hub 系统详情应显示“Agent 离线缓存：7 天，每分钟采样”和已同步状态。断开连接但 Agent 仍运行时会持续保存；重连后自动补传，只能恢复启用后实际采集且仍保留的样本。默认压缩缓存上限 256 MiB（可配置 8 MiB–1 GiB），容量先满时会提前淘汰旧数据并提示不完整；不是对任意规模保证完整覆盖 7 天。详见 [缓存说明](OFFLINE_HISTORY.md)。

普通资源缓存**不需要 vnStat**。流量日统计还需宿主机 vnstatd 持续运行、正确的 UTC 起始证明与配置/数据库目录只读挂载；仅更换 Agent 镜像不会自动安装或启用宿主 vnStat。已有流量配置与挂载继续沿用；新增采集见 [Docker Agent 流量配置](traffic/DOCKER_AGENT.md)。

## 图形界面部署 / docker run

fnOS 等图形界面可在原容器或原项目中编辑镜像，分别填写 Release 中的 Hub、Agent 完整镜像地址，拉取后重新创建原容器。Hub 保留 `/beszel_data` 原映射；Agent 保留 `/var/lib/beszel-agent` 原映射、KEY/TOKEN/HUB_URL、网络和其他挂载。不要另起一个空数据容器代替原管理端。

原来用 `docker run` 部署的，先保存原启动命令和 `docker inspect` 输出（可能包含密钥，私下保管），拉取新镜像，再用原参数重新创建容器，只替换镜像并增加缓存环境变量；`docker restart` 不会应用新镜像。不要使用删除卷的命令。

## 回退与本轮验证范围

升级前记录原镜像摘要，保留原完整 Hub 备份。回退 Hub 时恢复该备份并使用对应旧镜像；不要假定旧二进制可直接使用已经升级的数据目录。Agent 可切回原镜像，保留原持久卷；原版 Agent 不再采集七天缓存。

公共候选版不设置 stable/latest 别名。使用明确固定版本或 Release 中的固定摘要。本地真实断线、Agent 重启、恢复补传和 Hub 再重启去重已通过，七天边界及周/月汇总使用受控时间和模拟数据验证；尚未完成新版连续七天运行验证。本轮发布不自动更新 fnOS 或生产 VPS。
