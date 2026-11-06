# S2 Hub持久化交付

2026-11-06。前置S1 GitHub CI：[42160256816](https://github.com/CodeAIX/Beszel-Plus/actions/runs/42160256816)最终Agent/Web均通过。该运行Agent首次因原有重连端口用例偶发失败，重跑通过；本地重复运行也能复现，作为发布前风险保留，未删减原断言或忽略失败。

## 变更

- 独立migration新增traffic_sources/daily/settings、复合唯一键/范围索引及systems级联删除，原migration和system_stats/container_stats语义不变。内部时间使用UTC epoch秒NumberField，字节OnlyInt且0..2^53-1；已验证最大安全整数往返。
- 仅在原createRecords成功后入有界后台写队列：单writer、每系统一个待处理快照、最多50个待处理系统，按新时间合并；原updater不等待流量事务，关闭时取消并join。写失败等下一次绝对快照重试。
- 独立事务按日替换，来源水位防乱序；相同快照完全跳过；相同时间不同内容拒绝并记录冲突。历史日值相同不重写，查询仅限本次最多400日列表，保留Hub旧历史边界。
- 计数下降保留旧值并sticky suspected_reset；来源created变化冻结该来源直至明确恢复操作，不能自动混合不同代数据库。source updated回退也形成诊断。
- 首次失败只建默认settings、不伪造网卡；来源/原始值均禁止客户端直写，读规则遵循systems.users/SHARE_ALL_SYSTEMS。

## 真实挂载差异：SSH通用响应

本阶段双通道测试发现固定v0.21.1的`fetchDataViaSSH`只处理AgentResponse.SystemData，Agent的新响应实际走Data。已在原条件分支复用现有`transport.UnmarshalResponse`，同时支持typed/generic响应并处理Error；旧raw CBOR/JSON分支保持。此为满足原通道兼容所需的小范围修复，不新增协议动作/编号。测试用模拟Agent走真实本地WS/SSH连接，含无Traffic与有Traffic，以及typed/generic封装。

## 验证与边界

- 首次30日导入、10次重传、日值更新、旧时间/旧错误状态、同时间冲突：通过。
- 下降/reset sticky、数据库代际变更冻结、失败历史保留、无假接口：通过。
- 最大安全整数往返、非法值拒绝、删系统级联：通过。
- 流量事务失败不回滚已保存正常指标：通过。
- 独立临时数据库上撤销/重做新增migration，并验证已有系统/指标行保留：通过；没有对真实生产数据库执行down。
- WS/SSH、无扩展/有扩展、typed/generic响应：通过。
- Hub全包/migrations回归：通过，退出0；新增持久化/通道用例race通过。最终有界队列/合并/停止及全部新增用例race已通过（22.944秒，退出0）；GitHub结果以阶段提交后的运行记录为准。

没有承诺旧二进制可打开新schema；部署仍成套备份恢复。还未有Traffic API/UI，尚不能在页面查看用量。大规模性能与2GB长时观察留到S5，不能把短时数据库用例写成灰度完成。
