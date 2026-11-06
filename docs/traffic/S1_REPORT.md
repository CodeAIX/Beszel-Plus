# S1 Agent/协议交付

2026-11-06。用户已授权开始实施，并确认VPS Agent采用Docker；受控Docker集成因此提升到P0。生产VPS/fnOS未操作，测试均为本机隔离环境。

## 变更

- 新traffic共享类型、schema1、日值/日期/源created/updated/UTC可信起点/采集及保存间隔与安全整数校验。
- 新collector：默认off、单后台worker、原子不可变快照、退出取消并join；固定argv、每条命令3秒、stdout256KiB/stderr8KiB、结构化错误。只接受已实测的2.10/2.12/2.13及JSON API2。
- CombinedData追加可选key7；handler只在响应副本上附带Traffic，cache hit也可得到最新状态；不改原gatherStats/带宽/网络采集及已有动作编号。
- 独立Docker Plus Agent变体提供Alpine vnStat CLI，不启动daemon；宿主配置/完整数据库目录只读挂载。DOCKER_AGENT说明UTC_VALID_FROM是管理员明确确认的边界，不能由当前UseUTC反推历史。
- 原Agent仅增加1个字段、1处初始化、1处生命周期挂载、1处响应附加；原镜像定义保留。新增部署覆盖模板，不包含生产凭据。
- Web测试预加载Storage，使既有测试能在非浏览器Bun环境初始化；不改产品存储行为或旧测试断言。

## 已执行验证

| 检查 | 结果 |
|---|---|
| macOS Agent/entities回归（testing tag、短TMPDIR） | 通过，退出0 |
| Linux原Agent整套测试 | 460个顶层测试通过（含子测试1370项），退出0；新增UTC拒绝用例另经最终race运行覆盖 |
| 新采集相关race检查 | 通过，退出0；macOS非Linuxworker测试按平台跳过，Linuxworker另实测 |
| 真实Docker只读CLI | Alpine vnStat2.13；uid65534、cap-drop ALL、no-new-privileges、只读rootfs与只读库卷，查询成功，写探针拒绝；daemon为另一独立容器 |
| 原指标不被CLI阻塞 | Linux真实GetData连续10次读取缓存，初始化状态正常返回、CLI调用数仍1；通过 |
| 真实fixtures/非法及缺字段/溢出/重复/UTC日期 | 3份真实fixture与合成异常变体通过；三个接口只分开保存，不叠加 |
| 子进程超时/双输出上限/缺失/执行权限 | 通过；不会上报stderr原文 |
| 旧wire/新wire | key7默认省略、旧响应可解码、旧类型忽略新key、原CPU/Uptime一致；通过 |
| Linuxarm64镜像及amd64 Agent交叉编译 | 本地构建通过；正式发布镜像尚未推送 |
| 原Hub/migrations/alerts基线 | 对应包全部通过，退出0；迁移包本身无测试，不冒报迁移演练完成 |
| 原Web基线 | npm ci成功；npm run build成功；22项既有测试通过，退出0 |
| Compose | 本机已安装/配置Compose5.7.0，Hub本地compose语义解析通过 |

本机独立Colima profile为beszel-plus；默认旧profile未启动、默认docker context未切换。测试中原宿主TEMP路径过长造成macOS Unix socket用例失败，改短TMPDIR后通过；一次既有listener端口重绑定失败在后续完整回归通过，未为此修改原监控逻辑。

过程发现：嵌入bytes.Buffer的ReadFrom会绕开限流Write，测试暴露后改为组合成员；首次测试卷空目录copy-up重置属主，采用独立初始化标记/volume-nocopy修正；首次全套Linux测试的tmpfs默认noexec导致原套件的临时脚本不能执行，测试tmpfs显式exec后全套通过。生产配置没有因此放开写卷或额外权限。

## 限制与后续

S1尚无Hub流量持久化/API/UI，不能称为可用流量统计产品；生产vnstatd配置/现有库权限/UTC历史仍需部署时确认。旧版真实Hub二进制互操作与完整WS/SSH混合升级测试在S2/S5继续，不把旧类型单测当完整生产验收。最大16×400与256KiB分别限制，不承诺所有组合均能上报。

首轮GitHub CI（42160012233）Agent/race/跨编译通过，Web构建通过、测试失败：既有token测试mock整个utils模块，Linux文件枚举顺序使mock泄漏到后续测试。已增加tests/run.sh逐文件隔离Bun进程，不修改断言；本地隔离执行22项通过。GitHub修复运行通过后进入S2。GitHub工作流`Plus regression`运行原Agent/entities race、跨编译及Web基线。S1报告所在commit及GitHub日志为阶段证据，不记录自引用SHA。
