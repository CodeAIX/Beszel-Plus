# S3 API与账单算法

2026-11-06。S2稳定化后的GitHub CI：[42163178025](https://github.com/CodeAIX/Beszel-Plus/actions/runs/42163178025)，Agent、Web、Hub/migrations均通过。

新增三个认证API：GET `/api/beszel/traffic/overview`、GET `/api/beszel/traffic/detail`、PATCH `/api/beszel/traffic/settings`。Overview单请求返回最多50台有权系统，可分页；详情范围1–366个UTC日；设置仅显式白名单。接口不接收Agent上报、不接受前端修改日统计或collector状态。

权限从数据库读取systems.users，支持暂停/离线系统；与上游SHARE_ALL_SYSTEMS写规则一致，readonly始终拒绝写。未知/无权限系统统一404；统计原始集合的客户端写入关闭；响应no-store。

算法：UTC左闭右开周期、账单日1–28、自然月/今日/账单期独立求和、Tx或Rx+Tx、十进制配额，0配额percent=null。Go端求和及返回值检查安全整数；缺失日期返回null，原始字节不由浏览器累计。来源/观察更新时间共同决定freshness，阈值考虑刷新与保存间隔，1h刷新不套固定15m。

质量维度独立：collector status、freshness、quality、coverage。日桶日期齐全仍不足以证明全天daemon连续运行，P0保守返回unknown；确认有缺失/起点晚于周期则partial。不会用日期数量冒充准确完整。进度条超过100%的视觉截断属于S4，后端保留真实百分比。

已执行：账单C01–C05、当天ongoing、缺5日partial、Tx20%/双向30%、0配额、120%、安全整数溢出；匿名401/非成员404/readonly403/共享开关/暂停系统/非法网卡与字段/原始值禁止写；源数据库旧而观察时间新仍stale；1h刷新阈值；缺日期null；Hub停机区间重传补齐不累加。新增API/算法race及Hub/migrations全包回归通过，退出0。

本阶段还未接入前端。生产云厂商账单对账、真实多VPS、24小时观察与成套容器恢复不属于已经通过的用例。
