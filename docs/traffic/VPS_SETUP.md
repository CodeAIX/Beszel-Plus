# VPS 上的 vnStat 安装与预检

状态：供用户执行的Ubuntu/Debian原生安装步骤，本次未连接VPS执行。用户已允许协助安装；直接代执行前仍需取得并验证实际目标与登录方式，不使用历史IP猜测身份。Hub不需要安装vnStat。

## 先做只读检查

```sh
cat /etc/os-release
command -v vnstat || true
vnstat --version 2>/dev/null || true
systemctl is-active vnstat || true
ip -brief link
# 只看配置关键项；--showconfig的默认值可能带#。
vnstat --showconfig 2>/dev/null | grep -E '^[#;[:space:]]*(UseUTC|DatabaseDir|DailyDays|SaveInterval|TrafficlessEntries)[[:space:]]' || true
```

本项目已确认VPS Agent采用Docker。只安装vnStat不会升级Agent；后续需使用带vnStat CLI的Plus Agent候选镜像，按DOCKER_AGENT.md合并只读挂载。先本地测试，不自动修改现有VPS。

## Ubuntu 24.04 / Debian 12、13 安装

```sh
sudo apt-get update
sudo apt-get install -y vnstat
sudo systemctl enable --now vnstat
vnstat --version
vnstat --dbiflist
vnstat --json d --limit 0
```

这些命令只安装并启动发行版vnStat，**不保证默认UTC配置已满足Plus要求**。不要反复清库；已有历史需保留并注明采集时间基准。

## UTC与权限核验（必须）

1. 检查`systemctl cat vnstat`确认daemon实际二进制/配置；CLI以Agent服务账号运行，避免用户的`.vnstatrc`、XDG配置或不同`--config`造成假通过。记录双方相同的配置路径与真实版本。
2. 如果已有数据库，先按实际DatabaseDir备份；运行中SQLite需一致性备份或停止vnstatd后完整复制，不能只复制db文件遗漏WAL。停止/重启会有采集窗口，应记录。
3. 确认需启用UTC后备份真实配置文件，通过`sudoedit`将有效`UseUTC`设为1，再重启vnstatd。不得假定当前配置文件必然是`/etc/vnstat.conf`。新安装已开始采集到切换UTC之间的当日也不能当完整UTC日。
4. 用相同配置执行`vnstat --showconfig`确认UseUTC1，并观察daemon重启后的updated与日桶。配置修改不转换旧数据；记录可信UTC起始日，未知历史保留本地、不直接作为UTC可信数据上报。
5. 以真实Agent用户执行固定CLI验证读权限：

```sh
# 替换两个明确占位符后再执行；不把Agent改为root。
sudo -u <实际Agent服务用户> vnstat --config <已核验的绝对配置路径> --showconfig
sudo -u <实际Agent服务用户> vnstat --config <已核验的绝对配置路径> --json d --limit 0
```

Plus Agent已实现`BESZEL_TRAFFIC_VNSTAT_CONFIG`，容器内默认`/etc/vnstat.conf`；模板将实际daemon配置只读挂载到此路径，同时将真实DatabaseDir整个目录挂载至相同绝对路径。配置中的UseUTC1及`BESZEL_TRAFFIC_UTC_VALID_FROM=YYYY-MM-DD`均必需。Docker用户使用`docker exec --user <Agent实际UID:GID> <Agent容器> vnstat --config /etc/vnstat.conf --json d --limit 0`验证权限，无需在宿主安装systemd Agent。网卡计费选择在Hub中单选已上报来源，不能将公网、Tailscale、Docker计数叠加。

只向GitHub提交脱敏fixture/版本/关键配置证明，禁止提交实际IP、主机别名、令牌、SSH密钥、数据库或全量环境。生产VPS权限和24小时灰度与CI测试分别记录。
