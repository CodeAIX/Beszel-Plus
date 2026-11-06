# 导入已有系统

Beszel+ 在“添加系统”中提供“从 YAML 导入已有系统”入口，也可直接打开“设置 → YAML 配置”。选择原版 Beszel 导出的 `.yml`、`.yaml`，或粘贴相同内容，预览后确认批量导入。扩展名为 `.md`、`.txt` 的纯 YAML 文件也可选择；Markdown 代码围栏不属于 YAML。

当前实现在 plus/main，独立本地预览为 `http://127.0.0.1:18091/settings/config`，版本 `0.21.1-plus.1-import.1-local`。此前公开候选 `0.21.1-plus.1-candidate.42181555701.1` 尚不包含此功能；18090 的候选版及其观察任务继续运行。

## 导入行为

- 仅管理员可预览和执行。每次最多 1 MiB、1000 个系统，支持原版的 name、host、port、token、users 字段；端口缺省为 45876。
- 根据主机地址与端口去重，Unix socket 按路径去重；同一文件中的重复项也跳过。不会修改或删除已有系统，不覆盖其名称、Token、用户、告警、配额或历史数据。
- 新系统保留原 Token；缺省时生成新 Token，预览会提醒在 Agent 中配置。Token 被另一地址使用时整批阻止，避免连接到错误系统。
- 默认归属当前管理员。可选择按邮箱保留原用户分配；找不到用户时显示错误，不会静默丢弃授权。未提供用户列表时归属当前管理员。
- 有任何错误时不能确认；确认前重新验证文件、用户映射与重复状态。数据变化会要求重新核对预览。系统与 fingerprint 同一事务写入，任何保存失败整批回滚。
- 不写入 config.yml，也不调用原版的覆盖同步。若数据目录已经存在 config.yml，导入会阻止并提示先迁移该配置，避免下次启动同步删除新增系统。

API 为 `POST /api/beszel/config-yaml/import`；先提交 `config` 和 `user_mode`（current 或 match）获取预览，再以相同输入、`apply: true` 和 `preview_id` 确认。预览与错误响应不返回 Token；解析错误也不回显 YAML 内容。请求不进入 URL，响应标记 no-store。

## 已有 Agent 与迁移边界

原版“添加系统”会生成安装示例，但填写连接参数并不要求重新安装 Agent；原版也支持通用 Token 自动注册。原版 config.yml 在 Hub 启动时执行覆盖同步，未列出的系统会被删除，和本功能的增量导入不同。

YAML 导出只包含系统清单、地址、端口、Token 和用户邮箱，**不包含 Hub 私钥、监控历史、Agent 指纹、告警或 Beszel+ 流量配额**。因此：

- 在原 Hub 数据目录上升级 Beszel+，Hub 身份密钥沿用，已有 Agent 通常无需重新安装。
- 迁移到一个全新 Hub 时，只有导入 YAML 并不足以让原 Agent 自动信任它。SSH 需 Agent 的 KEY 信任当前 Hub 公钥；WebSocket 还需正确的 HUB_URL、TOKEN 与可达性。可修改现有 Docker Agent 环境变量并重新创建容器，保留 Agent 数据卷，无需先卸载 Agent。
- 本功能导入系统记录，不执行 VPS 安装或改配置，也不保证连接立即成功。需要完整保留原监控历史时应迁移/恢复完整 Hub 数据。
- 原版 Agent 导入后仍可做资源监控；流量日统计仍需宿主 vnStat、Plus Agent 及只读挂载，不能通过 YAML 自动补齐。

官方参考：[Agent 安装](https://beszel.dev/guide/agent-installation)、[认证机制](https://beszel.dev/guide/security)。

## 验证

新增 API 回归覆盖未登录/普通用户/只读用户拒绝、只预览不写入、原 Token 与 fingerprint/流量历史保留、重复文件/重复请求、用户邮箱映射、字段与 Token 冲突、失效预览、实际保存失败的整批回滚、文件大小/端口/未知字段/多文档限制和 config.yml 防护。Hub 与 config 包 race 回归通过；前端 33 项测试和生产构建通过。

用户提供的本地导出文件已仅通过预览检查：10 个系统均可解析，未创建系统或发起远程连接，真实文件及 Token 未加入仓库。浏览器使用独立实例与回环地址样例完成粘贴预览、确认新增 2 台/跳过 1 台、文件选择后重复导入全部跳过的验证。

[GitHub 完整回归 42192569636](https://github.com/CodeAIX/Beszel-Plus/actions/runs/42192569636) 的 Agent、Web/Hub 两项任务均成功；对应功能源码 `04f2350c549515b0b7424a32063d939d7a3c8046`，本机预览镜像标注同一源码。此功能尚未发布新公共镜像。

![已有系统导入预览，使用回环地址样例；重复项全部跳过](images/import-systems.png)
