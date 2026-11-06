# v0.21.1 源码挂载映射

上游：henrygd/beszel。tag：v0.21.1。commit：`e2ed147a5aa6472e6462521632ccc7101668132c`。tag对象：`bd1197b2648258b9ac8ece4f8e7f0890cdce5797`。路径和行号均来自此 commit，不能移植到新上游时直接信任旧行号。

## 已核验挂载点

| 现有路径/符号 | 观察与最小建议 |
|---|---|
| `internal/entities/system/system.go:CombinedData` | 已有key0..6；追加可选Traffic key7；只在本结构内分配，AgentResponse自身key7是另一层、无需修改 |
| `agent/agent.go:NewAgent` / `Start` / `gatherStats`（207行） | 初始化/退出管理collector；gatherStats全局mutex且cache hit早返回，不能锁内执行CLI；仅附带不可变缓存 |
| `agent/handlers.go:GetDataHandler.Handle`（102行） | 调gatherStats，随后copy响应修改ConnectionType；保留该机制，Traffic嵌套指针必须只读 |
| `agent/client.go`、`agent/server.go` | 保留WS/SSH响应与旧版本路径；S1/H08实测新optional字段与响应大小 |
| `internal/common/common-ws.go:WebSocketAction` | GetData动作保持0，其他枚举顺序不改；`DataRequestOptions`不引入客户端命令参数 |
| `internal/hub/systems/system.go:update`（162行） | fetch→migrateDeprecatedFields→createRecords；仅在原createRecords成功后单独处理Traffic，失败不影响原返回值 |
| 同文件 `createRecords`（258行） | 原指标/关联记录事务保持；Traffic不得加入原事务；单独文件使用core.App，不扩大hubLike接口 |
| 同文件 `HasUser`（641行） | SHARE_ALL_SYSTEMS=true时认证用户可读；活跃SystemManager不能覆盖所有暂停/离线情形，API必要时DB加载systems关系 |
| `internal/hub/collections.go:setCollectionAuthSettings`（17行） | 动态规则含SHARE_ALL_SYSTEMS与readonly；新增三表list/view受限，客户端统计与settings写规则为nil；自定义API显式授权 |
| `internal/hub/api.go:registerApiRoutes`（165行） | apiAuth认证分组登记3条API，PATCH加excludeReadOnlyRole和systems写权限；统计真值不接受前端写 |
| `internal/migrations/1792309602_system_details_sockets.go` | 当前m.Register(up,down)、collection.Fields.Add、app.Save样例；新增timestamp独立文件，cascade与索引用实际PB API |
| `internal/site/src/types.d.ts` | 增加新响应类型；不改原Stats定义 |
| `internal/site/src/components/systems-table/systems-table.tsx` | 系统Map/用户设置/缓存体系；页面一次overview，按ID派发；同步更新行和grid显示/排序 |
| 同目录 `systems-table-columns.tsx` | 追加可隐藏列，复用显示组件；不要按行发请求 |
| `internal/site/src/components/routes/system.tsx` | 存在tabs及连续布局；Traffic入口同时考虑两种布局和`use-system-data.ts`的tab状态，不能只加一个TabsTrigger |
| `internal/hub/api.go`、`internal/hub/update.go`、`agent/update.go`、`internal/ghupdate/*` | CHECK_UPDATES只影响提示，不等于禁用CLI更新；更新器默认henrygd/beszel。Plus需单独禁用替换路径/安装timer，固定Agent产物，不全局重写更新框架 |
| `internal/dockerfile_hub` | scratch；/beszel、/beszel_data、8090与serve参数可保留；前端dist在构建镜像前生成；不需vnstat |
| `internal/dockerfile_agent` | scratch内没有vnstat；宿主apt安装不使容器Agent可调用；P0使用原生Agent |
| `.github/workflows/docker-images.yml` / `release.yml` | 上游tag v*触发，不做业务测试门禁；镜像含上游Docker Hub目标和多种GPU变体，不直接启用为Plus发行 |

9个规格 Existing 路径均存在。规格描述的主要函数均存在，实际增加挂载点为 lifecycle/cache、双布局与更新入口；不是整体路径失配。

## 新文件边界

按SPEC-v1.1 §2新增：`internal/entities/traffic/traffic.go`，`agent/traffic_vnstat*.go`及fixture/tests，`internal/hub/systems/traffic.go`，独立traffic migration，`internal/hub/traffic_api.go`/`traffic_calc.go`，`lib/traffic-api.ts`，Traffic面板/设置/用量组件。若采集生命周期需轻微调整Agent struct/cleanup，只增必要字段与调用。

独立Plus工作流后续使用 `.github/workflows/plus-upstream.yml`、`plus-ci.yml`、`plus-release.yml`；不复制上游所有发行矩阵。新同步版本需比较CombinedData字段唯一性、动作值、GetData封装、权限与migration API，而不只检查git merge是否无冲突。

## 工具链和测试

- `go.mod`：Go 1.27.2、PocketBase 0.40.5、fxamacker/cbor 2.9.6；module仍为github.com/henrygd/beszel，无需随仓库改名。
- package.json：React ^19.1.2、TypeScript ^5.9.2、Vite ^7.3.5、Recharts ^2.15.4；这是声明范围，锁定版本以bun.lock为准。
- `Makefile:test`：`go test -tags='testing no_ui' ./...`。testing关键；本tag源码未发现no_ui条件编译，不应当它能自动绕过dist嵌入。
- `internal/site/embed.go`嵌入dist；Go全量测试前先生成真实Web构建（或仅作纯Go预检时使用明确记录的占位目录，不能声称UI通过）。
- 前端scripts只有dev/build/preview/sync等，没有npm test/typecheck。已有`internal/site/tests/*.test.ts`使用bun:test，明确运行`bun test ./tests`及`bun run build`；新增前端测试目录需纳入命令。
- 当前S0未运行整套Go/Web基线，不将静态核验写成测试通过。

## 必须保持原样的区域

`agent/network.go`、`internal/records/records.go`、`records_deletion.go`、现有network-sheet、Stats带宽/接口语义、原Docker采集、旧migration、既有协议编号与历史压缩。不得为品牌命名全局替换module、所有imports或已有数据库目录。
