# fnOS 现有 Beszel 的测试与升级

**当前不执行：用户最新要求改为本机测试；本文仅作后续部署参考，不是当前开发的前置条件。**

已知用户已用Docker安装Hub并添加VPS；当前镜像版本、架构、实际挂载、Compose服务名与VPS Agent方式尚未核验。以下是操作契约，不是本次已执行记录。

## 可以原部署升级，但需更换镜像并重建容器

官方Hub使用`/beszel_data`持久化、默认8090；Plus保持这些运行约定。符合前置条件时保留已有数据卷、环境、命令/entrypoint、网络、端口、socket挂载、重启策略及身份文件，只更换Hub镜像即可重建容器测试。不是在旧容器中apt安装或覆盖/beszel。

保留数据通常可保留用户、VPS、历史与密钥，但必须实测迁移，不能提前保证任意旧Beszel版本都能直接跳升。当前Hub若比0.21.1更新，禁止用旧基线Plus对其数据库降级打开；需先适配相同或更新基线。若更旧，先在副本验证支持的升级路径。

## 更新前核验

1. 取得脱敏部署配置：Hub版本/tag/digest、fnOS CPU架构、容器服务名、数据目录实际路径和持久化情况、socket/反向代理/环境及启动参数；不要把完整docker inspect或含密钥的compose提交GitHub。
2. 记录旧镜像digest，保存旧compose/环境文件与权限，验证可重拉旧镜像。不要`docker compose down -v`，不要删除数据卷。
3. 停止Hub再完整备份实际数据卷及相关密钥/config，保留所有者与权限；若不停机只能使用已验证的一致性备份，不能复制活跃SQLite一个db文件而漏掉WAL。
4. 用备份副本启动新镜像测试migration；测试容器用独立数据卷、端口和隔离网络。不要让副本Hub同时连接真实Agent、执行同步配置或发送真实告警；使用受控假Agent/禁外联测试网络。不能两个Hub同时写同一数据卷。
5. 副本迁移/原监控回归通过、备份可恢复后，在已授权fnOS环境替换现有Hub镜像并重建。目标VPS Agent仍分批升级；未升级节点仍应正常显示原指标。

## Compose操作模板

只适用于已经确认使用Compose且知道服务名的环境。先按上节完成备份和副本测试，再在**原Compose项目目录**将Hub的image改成发布报告给出的实际固定Plus镜像/digest，保留其他参数。当前没有可拉取的Plus功能镜像，不提供伪造tag。

```sh
# 用实际Hub服务名替换下面的 beszel；禁止对整套项目down -v。
docker compose pull beszel
docker compose up -d --no-deps beszel
docker compose ps beszel
docker compose logs --since 10m --tail 100 beszel
```

如果是fnOS图形界面创建容器，则在原应用管理中修改镜像并重建；不要无依据地另建不同挂载的新实例。首次验证原用户登录、VPS数量及在线状态、原CPU/内存/磁盘/网络/Docker历史、通知设置，再验证Traffic。

## 回滚

关闭Plus Hub，保存新版本数据以便诊断，使用**旧镜像digest + 升级前完整备份 + 旧配置**恢复。只退回镜像不等于数据库可回退；不把down migration当默认生产回滚。流量缺口仅在vnStat保留窗口内重导，无法补齐的标partial。

## 两条升级链

- fnOS：Plus Hub容器，聚合/展示/持久化；Hub不安装vnStat。
- 每台需要流量的VPS：vnstatd采集并保存，Plus Agent只读CLI经原通道上报。只装vnStat或只升级Hub都不能让旧Agent自动上报。

P0首选原生systemd Agent。如果既有VPS使用Docker Agent，宿主安装vnStat并不会使scratch镜像拥有该CLI；不要给容器root/privileged绕过。需先选择受控集成或单机迁移方案，不能自动改变全部Agent部署方式。
