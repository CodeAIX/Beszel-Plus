# S5 发行与上游维护

2026-11-06。已发布[首个测试候选](https://github.com/CodeAIX/Beszel-Plus/releases/tag/v0.21.1-plus.1-candidate.42168663335.1)，完整镜像digest/源码/测试链接见[CANDIDATE.md](CANDIDATE.md)。源码`85425f0da8ffa85d10fe1e11fc174e801f0abf5d`；后续先修正维护工作流与文档，再加入紧凑流量列及顺序优化。

## 产品与验证

Plus独立版本/commit信息与上游协议版本分离，避免破坏semver能力门槛。Hub/Agent拒绝通过官方二进制自更新覆盖定制功能，关闭官方升级提示；Footer指向Fork。Go/Alpine基础镜像固定多架构manifest digest；两种镜像均提供linux/amd64、linux/arm64、OCI来源标签、SBOM/provenance。

前端31项测试、构建与Hub/迁移回归通过；本机完整Go race退出0（原有告警包606.263秒，首次默认600秒预算不足，显式20分钟后完整通过）。GitHub run42168663335的完整Go/Web门禁和镜像构建/启动/恢复均成功。只读CLI跨数据库版本：Alpine2.13读取Debian12/2.10、Ubuntu24.04/2.12，interfaces/jsonversion及日值一致。2GB/2CPU Linux容器首次写3接口×400日约57.9ms（tmpfs，非磁盘性能保证）。

完整目录一致性备份恢复后认证、20GB配额、90天中的88条记录与2个空缺、账单汇总逐值相同。导出的patch已干净应用至固定上游SHA，collector/API/UI/Dockerfile与Plus一致。公开包页面、匿名OCI索引和空白Docker凭据的实际pull均通过，双平台齐全。本地已用公开digest替换测试Hub与Agent，版本/源码吻合、Agent up、traffic fresh、历史/配额保留。

## 自动维护与权限修正

plus-upstream每天UTC03:19检查官方稳定release，跳过草稿/预发布/旧版本，固定真实SHA。key7被占用或三方合并/语义测试冲突即停，不覆盖默认分支。合并使用--no-commit，在生成merge commit前保留Fork已审查的workflow树；官方workflow差异存入supplemental/traffic/upstream-workflows.diff供审查，不激活继承的发布任务。保留官方提交父历史。已有同tag候选分支幂等跳过，失败时可手动重跑候选发行。

候选在同一显式可复用流水线完成测试、2GB容器启动/完整目录恢复、镜像发行和draft PR流程，不依赖push/PR触发链。镜像版本由当前run/attempt生成，重跑不覆盖旧tag；artifact也按attempt分名。先核对workflow树与默认分支一致，再保留固定源tag，Release使用--verify-tag确认已有tag。发行记录含镜像digest、来源manifest、相对官方patch、提交列表与SHA256SUMS，不把patch自身反复提交回源码。

首次镜像已发布后，Release API因源提交workflow与开发期间更新后的默认分支不同而403。[官方权限说明](https://docs.github.com/en/rest/releases/releases)明确GITHUB_TOKEN不能额外获得workflow写权限。已验证原测试/镜像/校验和与固定源tag，通过独立恢复工作流42171231148完成Release，没有重新构建或覆盖镜像。工作流修正通过actionlint/py_compile；权限实测42171535509以真实GITHUB_TOKEN完成含workflow变化的模拟上游三方合并、保留Fork工作流、push、固定tag和draft Release，再删除全部临时refs/draft。此后正常自动维护无需长期PAT。仓库默认token权限仍为read，只给对应维护/发行job所需写权限。

上游当前仍v0.21.1，实际检查42167164084正确跳过；未伪造一次官方升级。不能承诺任意官方重构都无需人工。没有自动合并PR、提升stable或更新fnOS/生产VPS。

## 观察状态

24小时健康/资源观察已经在公开候选digest上启动（2026-11-06 06:04:43 UTC），最初样本health=true、traffic=ok。结束后生成本地summary.json，休眠/采样空缺会使连续观察不通过。当前尚未完成24小时、生产VPS账单对账或stable提升。

## 紧凑流量列候选更新

已发布 [0.21.1-plus.1-candidate.42181555701.1](https://github.com/CodeAIX/Beszel-Plus/releases/tag/v0.21.1-plus.1-candidate.42181555701.1)，源码 `452a8221545380cdddb9072888e7855d1064a234`；[测试、镜像和 Release 流水线](https://github.com/CodeAIX/Beszel-Plus/actions/runs/42181555701) 两个任务均成功，全程正常发行，无需恢复流程。前端现为 33 项测试，完整 Go race、2GB Hub 启动/目录恢复与双架构构建通过。附件校验和、固定 tag、补丁回放、公开匿名拉取及来源标签均验证通过。

本机已备份并将 Hub/Agent 升级至新候选固定 digest，4 个系统及设置/历史保留，真实 Agent 在线、流量 fresh。新观察从 2026-11-06 08:04:26 UTC 开始，旧观察未计为完成；当前镜像与验收边界见 [CANDIDATE](CANDIDATE.md)。
