# S4 流量界面与本地验证

2026-11-06。原监控表格追加可隐藏/排序的本期流量列；系统页追加独立Traffic面板，含今日/自然月/账单期、30/90日Rx/Tx图表与设置弹窗。中文和英文提供翻译；其余语言采用英文回退。缺失为null，未知为破折号，实际0仍为0。原始字节/UTC日期由服务端返回；不在浏览器累加账单。

设置支持单计费网卡、精确GB/TB配额、Tx或Rx+Tx、UTC账单日1–28、GB/GiB显示、启停。BigInt转换避免大整数在十进制单位往返时损失字节。readonly仅可查看，服务端另有403门禁。页面级批量overview、60秒内存缓存/轮询、并发去重、登录隔离、卸载/切换系统后忽略旧响应；不保存统计到localStorage。批次50台，前端当前上限500台。

已执行：npm ci锁定依赖，npm run build成功；前端31项测试全通过；Hub/migrations全包回归通过。真实本地Docker Agent经SSH向Hub上报，eth0当日Rx=1886B/Tx=84B时与CLI对照；daemon后续仍持续采集。原先Linux Agent完整1370项（含子测试）通过，见S1报告。

浏览器验收：中文表格、90天历史、离线保留数据、无采集状态；历史样例显示42.71GB/20GB（213.5%），实际进度条100%；配额10→20GB保存并刷新；readonly浏览器会话全部设置控件禁用且无保存按钮；390×844窄屏设置完整可操作，测试后恢复桌面尺寸。历史样例和账号均为隔离本地数据，不来自生产。

验收发现并修复：settings在第一条上报前保存时应保持not_enabled；vnStat数据库重建应冻结旧generation及UTC有效起点，不能用新起点遮蔽Hub历史。补充对应回归测试，reset测试race通过。

环境：独立Colima profile/context `beszel-plus`/`colima-beszel-plus`，不切换默认context；Hub限制2GB，127.0.0.1:18090；账号/DB/密钥在.gitignore覆盖的.plus-local内。未连接fnOS或生产VPS。24小时稳定性、生产账单对账和正式stable镜像未完成。
