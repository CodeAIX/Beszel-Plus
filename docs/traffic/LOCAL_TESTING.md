# 本地测试方案（当前默认）

2026-11-06用户调整：新版Beszel+在本机测试，暂时不需要fnOS环境。GitHub继续承担源码、自动验证与镜像构建；交互验收在本机完成。FNOS_UPGRADE仅保留为以后部署参考，不是当前前置条件。

## 隔离边界

- 本机Docker的独立项目、独立新数据卷、仅绑定127.0.0.1测试端口；不加载fnOS数据/凭据，不自动连接真实VPS。
- 已安装Compose插件，运行独立Colima profile `beszel-plus`，context `colima-beszel-plus`。默认Docker context和原Colima profile未切换。所有命令显式指定context。
- macOS主机不承担Linux collector。Linux Agent/vnstatd在Docker Linux VM/专门测试容器中运行；宿主macOS Agent的非Linuxstub需单独编译验证。
- 本地Hub用于模拟系统、角色、数据缺失、账单周期、图表、响应/权限和WS/SSH；真实格式fixture来自已运行的三发行版CI。collector执行和计数连续性需在Linux环境实际运行，不用mock宣称完成。

## 分阶段测试

1. S1：Go collector/protocol测试、race/超时/大输出、Linux真实vnStat、非Linux构建；不依赖fnOS。
2. S2/S3：临时PocketBase数据库；重复/乱序/reset/权限/覆盖率；用测试数据副本验证迁移与回滚，不接生产库。
3. S4：本地Hub + 受控Linux测试Agent；桌面/窄屏、只读/非成员/share-all、loading/error/null柱；同一日期对照CLI。
4. S5：本地构建Hub镜像与Linux Agent；2GB内存限制、长时资源/重启/补传/混合版本；镜像可拉取和本地成套恢复。本地结果记录为本地，不声称生产VPS/fnOS已验收。

## Hub运行入口

S4已构建本地功能镜像并完成隔离验证，详情见S4_REPORT。以下从源码构建新的独立测试实例。

```sh
# 先生成Go嵌入的真实前端；不要修改lockfile后假装frozen构建。
cd internal/site
npm ci --ignore-scripts
npm run build
sh tests/run.sh
cd ../..
docker --context colima-beszel-plus build -f internal/dockerfile_hub_plus -t beszel-plus:local .
docker --context colima-beszel-plus compose -f supplemental/traffic/compose.local.yml up -d
docker --context colima-beszel-plus compose -f supplemental/traffic/compose.local.yml ps
```

打开 http://127.0.0.1:18090 并创建本地测试账号。首次需确认端口空闲；任何测试账号/Agent token只放本地私有配置，不提交GitHub。停止测试使用相同compose文件的`down`，不默认加`-v`删除测试历史。

上述compose仅启动Hub；带vnStat的Linux测试Agent/固定镜像/配置与非root权限在S1完成实现时再加入，不用宿主二进制随意挂载进scratch镜像。需要netns/宿主计数的用例采用专门测试镜像与最小权限，不接入生产网络。
