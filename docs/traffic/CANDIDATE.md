# 当前测试候选版本

版本：`0.21.1-plus.1-candidate.42168663335.1`，上游v0.21.1；源码`85425f0da8ffa85d10fe1e11fc174e801f0abf5d`。[候选Release](https://github.com/CodeAIX/Beszel-Plus/releases/tag/v0.21.1-plus.1-candidate.42168663335.1)附带源码manifest、补丁、提交清单与SHA256SUMS。最新plus/main另含发行维护修正，不改变本候选的功能代码。

Hub（linux/amd64、linux/arm64，公开/匿名拉取已验证）：

```
ghcr.io/codeaix/beszel-plus/beszel@sha256:e3d15380641e8bdb4430acc34af780bba034933958803da21771bb0d917fdf2a
```

Docker Agent（同样支持双架构；内置vnStat CLI，不启动daemon）：

```
ghcr.io/codeaix/beszel-plus/beszel-agent@sha256:865c0dfe925778bdd052ed0dd0ebf39275ed277692815885e46dea30289947b3
```

本机127.0.0.1:18090已运行这组固定digest，独立Colima context为colima-beszel-plus。Hub数据与原Agent数据卷均已保留；真实测试Agent在线且流量fresh，90天历史样例及20GB配额保持不变。Docker空白凭据配置、匿名registry请求均已验证可拉取；OCI标签/Hub信息与源码对应。

证据：[完整测试/镜像构建](https://github.com/CodeAIX/Beszel-Plus/actions/runs/42168663335)（verify成功、两个镜像发布成功，首次Release收尾遇权限限制）；[验证产物后完成Release](https://github.com/CodeAIX/Beszel-Plus/actions/runs/42171231148)；[GITHUB_TOKEN合并/标签/Release权限实测](https://github.com/CodeAIX/Beszel-Plus/actions/runs/42171535509)。维护修正解决了workflow文件权限及重跑不可变版本的问题。

24小时健康/资源观察从2026-11-06 06:04:43 UTC开始，预计次日同一时间结束；报告在本机`.plus-local/observation/`，current.txt指向本次目录，结束后生成summary.json。休眠/断连会记录为观察空缺，不能当连续通过。目前未完成24小时验收，也没有stable/latest Docker别名。

VPS先按[VPS_SETUP](VPS_SETUP.md)安装并核验UTC配置，再按[Docker Agent集成](DOCKER_AGENT.md)合并只读挂载。原Agent不会自动获得流量功能。当前不操作fnOS/生产VPS；需要部署时先备份，先Hub后逐台Agent。
