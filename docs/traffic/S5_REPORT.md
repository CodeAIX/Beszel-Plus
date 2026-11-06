# S5 发行与上游维护

2026-11-06。已增加Plus独立版本/commit信息，协议版本仍为上游0.21.1。阻止Hub/Agent命令从官方release自更新二进制，避免覆盖Plus功能；CHECK_UPDATES不再提示官方升级。界面Footer指向Fork。Hub与Docker Agent使用固定Go/Alpine多架构manifest digest，构建时注入Plus身份/OCI标签，发行流水线保留SBOM与provenance。

`plus-release.yml`（手动或可复用）先构建Web/执行前端测试和Go全包race，再以2GB内存启动Hub、停止后完整复制数据目录、恢复至新容器并检查健康；成功后构建linux/amd64与linux/arm64的Hub/带vnStat CLI的Docker Agent。产物为唯一run ID候选tag、两个镜像digest、源码manifest、相对上游的二进制兼容patch、提交清单与SHA256SUMS。没有latest/stable自动别名。

`plus-upstream.yml`每天UTC03:19和手动查询官方稳定release，忽略预发布/草稿/旧版本。固定tag实际SHA，检测上游CombinedData key7占用，再三方合并保留补丁；新增上游workflow、文本冲突或协议测试不兼容则停止。候选分支不覆盖默认分支，显式调用同一验证/发行workflow后生成draft PR，避免依赖GITHUB_TOKEN引发的push触发链。已有同tag分支不重复建分支；失败后可手动对候选分支重跑Plus candidate images。不能承诺任意上游重构无人工适配。

已执行本地：actionlint v1.7.12检查三份Plus workflow无错误；协议枚举0–9与CBOR字段冲突门禁、自更新保护测试通过；上游查询确认当前仍v0.21.1，正确输出build=false；本地新Hub镜像构建与2GB启动/完整目录备份/独立容器恢复成功。跨版本实测：Alpine CLI2.13以UID65534、只读卷读取Debian12/2.10与Ubuntu24.04/2.12数据库，interfaces/jsonversion及日计数逐值一致。导出补丁已在固定upstream SHA的干净源码上实际应用，collector/API/UI/Dockerfile与Plus源码相同。2GB/2CPU Linux容器首次写入3接口×400日共1200行约57.9ms（tmpfs测试，非磁盘性能承诺）。真实本地数据库完整恢复后认证、配额与历史汇总/日数组一致。

常规GitHub回归42167130350成功；手动上游检查42167164084成功并正确跳过当前v0.21.1。本机全包race因119个原有告警测试耗时触及默认10分钟上限，未出现断言/race失败；余下最后测试单独race通过（5.435s），其余包通过。首个Linux全包race同样因原有告警测试触及10分钟上限而中止（42167190007），images job正确跳过。已将预算显式增加至20分钟，第二次完整门禁42168663335进行中；不会绕过失败门禁发布。

24小时稳定性观察和生产VPS账单对账尚未完成，首个发行保持candidate。当前只做本地测试，fnOS/VPS没有自动部署。
