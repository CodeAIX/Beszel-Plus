# GitHub 补丁维护与镜像发布设计

状态：S5已实现候选验证/双架构发行及上游稳定版定时检查；实际结果见S5_REPORT.md。正式Fork为[CodeAIX/Beszel-Plus](https://github.com/CodeAIX/Beszel-Plus)，展示名Beszel+，默认分支`plus/main`。上游`main`保留但不用于开发基线。

## 补丁式开发

功能模块独立文件、小范围挂载、阶段提交；保留上游module/import和MIT许可证。优先采用Fork内保留功能提交的三方合并维护，不维护另一份整套源码或脆弱的sed替换脚本。每个Plus release同时导出`git diff <upstream_sha> <plus_sha>`补丁、提交清单与来源manifest；不把包含自身的patch反复提交回相同diff目录。

manifest至少记录upstream repo/tag/commit、Plus commit/release、traffic schema、CombinedData traffic key、migration清单、工具链、测试run、镜像平台/digest。可复现的含义是固定源码/依赖/镜像输入可追溯，除非已实测，不宣称每次镜像二进制digest完全一致。

## 上游升级自动流程

1. `plus-upstream.yml`在默认分支定时查询官方稳定release，并提供workflow_dispatch；跳过draft/prerelease，不因日期新旧盲选tag，记录实际commit SHA；workflow concurrency按仓库串行、同一tag幂等。上游仓库发release不会直接触发Fork的release事件。
2. 在临时候选分支从当前Plus稳定点三方合并固定的上游tag提交，保留扩展；没有force-push main、没有在无测试时同步覆盖默认分支。候选必须保留上游提交历史与merge SHA。
3. 若文本冲突、上游已占CBOR key7/已有字段语义变化、schema/权限/工具链迁移未适配，则停止发布，保留运行诊断供维护者处理。编号冲突不能给新流量随意改key再继续，需兼容迁移计划。不能承诺任意官方升级无需人工。
4. 运行原版回归与A/H/C测试、Web测试/build、混合版本WS/SSH、migration副本/恢复、镜像启动/健康检查；构建linux/amd64、linux/arm64。升级差异影响部署/数据库时不能用旧测试报告替代新检查。
5. 全部自动门禁通过后自动发布不可变候选版本和镜像，如`0.21.2-plus.1-candidate.1`，与固定Git SHA相连；生成候选PR。PR合并/标记stable的发布由同一流水线显式串接，防止GITHUB_TOKEN创建的push/PR不触发预期后续workflow而漏测。稳定发布需本次必测和所需灰度均通过。
6. 本机拉取固定候选tag/digest测试（fnOS测试已暂缓）；首次及有协议/DB变化的版本完成灰度后才提升stable别名。自动发布镜像不等于自动更新现有fnOS容器；用户现有监控环境不挂Watchtower latest自动替换链。

workflow schedule可能延迟，公共repo无活动60天会被停用，需可见的最后检查时间和手动入口；不把它描述成保证实时或永久运行。S0未创建Codex提醒/定时任务。

## CI与发布凭证

- 目前启用`Plus regression`、`Plus candidate images`、`Plus upstream stable check`及手动fixture工作流；继承的Docker、GoReleaser、Helm、issue清理等工作流在Fork中先禁用，防误触发上游地址或不必要发布。以后按Plus范围逐一替换/启用。
- 自动验证内容只读权限；发布job才给packages:write；改分支/建PR的job单独给contents/pull-requests权限。第三方action固定已核验commit。来自Fork PR的代码不在有发布secrets的上下文执行，不用pull_request_target执行不可信代码。
- GHCR首选`GITHUB_TOKEN`，不要求用户交出长期PAT。镜像名使用小写，Hub为`ghcr.io/codeaix/beszel-plus/beszel`，Agent为同namespace下beszel-agent；只有发行成功后的固定候选tag/digest可用于测试。
- 固定版如`0.21.1-plus.1`，候选与stable别名分开；部署记录用digest。首次GHCR package可能为private，要验证/设置公开并测试匿名拉取，不能只假设public repo即public镜像。
- 保留SBOM/provenance、commit标签、sha256和测试记录。打tag触发的原上游工作流不作为Plus质量门禁。

## 阶段安排

S1–S4功能和本地验证已完成，S5流水线已实现；24小时观察/生产对账及stable提升为独立后续门禁。当前自动发布候选，不自动合并PR、提升stable或更改运行中的容器。
