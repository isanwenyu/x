# X Tweet Monitor & XTracker Service

一个基于Python的Twitter/X推文监控服务，结合XTracker数据追踪，通过DingTalk机器人发送通知。

## ✨ 功能特性

- **推文监控**: 通过Nitter实例监控指定Twitter用户的最新推文
- **XTracker集成**: 获取用户的XTracker统计数据
- **DingTalk通知**: 通过DingTalk机器人实时推送消息
- **多平台部署**: 支持Docker、Systemd、Vercel等多种部署方式
- **代理支持**: 支持HTTP/HTTPS代理配置
- **数据持久化**: 本地存储最后监控状态
- **灵活配置**: 通过环境变量进行配置

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/isanwenyu/x.git
cd x
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行服务

```bash
python -m x.main
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 描述 | 示例 |
|--------|------|------|
| `DINGTALK_WEBHOOK` | DingTalk机器人Webhook URL | `https://oapi.dingtalk.com/robot/send?access_token=xxx` |
| `DINGTALK_SECRET` | DingTalk机器人密钥 | `SECxxx` |
| `TWITTER_USERNAME` | 要监控的Twitter用户名 | `elonmusk` |
| `NITTER_INSTANCE` | Nitter实例地址 | `https://nitter.net` |
| `XTRACKER_USERNAME` | XTracker用户名 | `your_username` |
| `XTRACKER_API_URL` | XTracker API地址 | `https://xtracker.pro/api/v1` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `LOG_FILE` | 日志文件路径 | `./data/logs/x_monitor.log` |
| `HTTP_PROXY` | HTTP代理地址（可选） | `http://127.0.0.1:1087` |
| `HTTPS_PROXY` | HTTPS代理地址（可选） | `http://127.0.0.1:1087` |
| `MONITOR_INTERVAL` | 监控间隔（分钟） | `5` |

### 获取配置值

#### DingTalk机器人配置
1. 在钉钉群聊中添加自定义机器人
2. 获取Webhook URL和密钥
3. 参考文档：[DingTalk Webhook配置指南](./docs/dingtalk_webhook.md)

#### Nitter实例
- 官方实例：`https://nitter.net`
- 其他可用实例：
  - `https://nitter.it`
  - `https://nitter.pussthecat.org`
  - `https://nitter.cz`

## 🐳 Docker部署

### 使用Docker Compose（推荐）

```bash
docker-compose up -d
```

### 手动构建

```bash
# 构建镜像
docker build -t x-monitor .

# 运行容器
docker run -d \
  --name x-monitor \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  x-monitor
```

## 🖥️ 系统服务部署

### 使用Systemd（Linux）

```bash
# 安装服务
sudo ./scripts/systemd/install.sh

# 启动服务
sudo systemctl start x-monitor
sudo systemctl enable x-monitor

# 查看状态
sudo systemctl status x-monitor

# 查看日志
sudo journalctl -u x-monitor -f
```

### 卸载服务

```bash
sudo ./scripts/systemd/uninstall.sh
```

## ☁️ Vercel Deployment (Serverless)

### 一键部署

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/isanwenyu/x&env=DINGTALK_WEBHOOK,DINGTALK_SECRET,TWITTER_USERNAME,NITTER_INSTANCE,XTRACKER_USERNAME,XTRACKER_API_URL)

### 手动部署

#### 1. 安装Vercel CLI

```bash
npm i -g vercel
```

#### 2. 部署到Vercel

```bash
# 登录
vercel login

# 部署
vercel --prod

# 设置环境变量
vercel env add DINGTALK_WEBHOOK
vercel env add DINGTALK_SECRET
vercel env add TWITTER_USERNAME
# ... 添加其他必要的环境变量
```

#### 3. 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 本地运行Vercel函数
vercel dev
```

### Vercel API端点

部署后，你将获得以下API端点：

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/monitor` | GET | 手动触发推文监控 |
| `/api/xtracker` | GET | 获取XTracker统计 |
| `/api/test` | GET | 发送测试通知 |

### Vercel + Cron Jobs

由于Vercel是serverless平台，需要外部触发监控：

#### 方案1: GitHub Actions（推荐）
项目已包含 `.github/workflows/monitor.yml`，自动每5分钟触发监控。

#### 方案2: 外部Cron服务
使用 [Cron-Job.org](https://cron-job.org) 或 [UptimeRobot](https://uptimerobot.com) 定期访问：
- `https://your-app.vercel.app/api/monitor` - 监控推文
- `https://your-app.vercel.app/api/xtracker` - 获取XTracker数据

### Vercel vs Systemd对比

| 特性 | Vercel | Systemd |
|------|--------|---------|
| **成本** | 免费额度 | 服务器成本 |
| **维护** | 零维护 | 需管理服务器 |
| **扩展性** | 自动扩展 | 手动扩展 |
| **触发方式** | HTTP API | 定时任务 |
| **数据存储** | 临时存储 | 持久存储 |
| **适用场景** | 轻量级监控 | 长期稳定运行 |

## 🔧 开发

### 项目结构

```
x/
├── x/                    # 核心代码
│   ├── __init__.py
│   ├── main.py          # 主程序入口
│   ├── config.py        # 配置管理
│   ├── twitter_monitor.py   # Twitter监控
│   ├── xtracker_client.py   # XTracker客户端
│   ├── dingtalk.py      # DingTalk通知
│   ├── state.py         # 状态管理
│   ├── scheduler.py     # 任务调度
│   ├── proxy_config.py  # 代理配置
│   └── logging_config.py    # 日志配置
├── data/                # 数据目录
│   ├── logs/           # 日志文件
│   └── state/          # 状态文件
├── scripts/            # 部署脚本
├── docs/               # 文档
├── requirements.txt    # Python依赖
├── Dockerfile          # Docker配置
├── docker-compose.yml  # Docker Compose配置
├── vercel.json         # Vercel配置
├── vercel_api.py       # Vercel API函数
└── README.md           # 项目文档
```

### 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行测试
python test_service.py

# 手动触发监控
python -c "from x.twitter_monitor import TwitterMonitor; TwitterMonitor('elonmusk').monitor_once()"
```

## 🧪 测试

### 运行测试

```bash
python test_service.py
```

### 测试通知

```bash
# 测试DingTalk通知
curl -X GET https://your-app.vercel.app/api/test
```

## 📊 监控与日志

### 日志查看

- **本地**: 查看 `data/logs/x_monitor.log`
- **Docker**: `docker logs x-monitor`
- **Systemd**: `sudo journalctl -u x-monitor -f`

### 监控指标

- ✅ 推文监控状态
- ✅ XTracker数据获取
- ✅ DingTalk通知发送
- ✅ 服务健康检查

## 🔍 故障排除

### 常见问题

#### 1. 推文获取失败
- 检查Nitter实例是否可用
- 确认Twitter用户名正确
- 查看代理配置（如使用）

#### 2. DingTalk通知失败
- 验证Webhook URL和密钥
- 检查网络连接
- 查看DingTalk机器人配置

#### 3. 代理配置问题
- 确保代理地址格式正确：`http://host:port`
- 测试代理连通性
- 检查防火墙设置

#### 4. Vercel部署问题
- 确认所有环境变量已设置
- 检查函数日志：Vercel Dashboard > Functions
- 验证API端点响应

### 调试模式

```bash
# 启用调试日志
export LOG_LEVEL=DEBUG
python -m x.main
```

## 🤝 贡献

欢迎提交Issues和Pull Requests！

### 开发规范

1. 代码风格遵循PEP 8
2. 添加必要的注释和文档
3. 更新相关测试
4. 保持向后兼容性

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Nitter](https://github.com/zedeus/nitter) - 提供Twitter数据访问
- [XTracker](https://xtracker.pro) - 提供X平台数据追踪
- [DingTalk](https://open.dingtalk.com) - 提供消息通知服务

## 📞 支持

如有问题，请通过以下方式联系：
- 提交 [GitHub Issue](https://github.com/isanwenyu/x/issues)
- 发送邮件至：isanwenyu@example.com

---

**⭐ 如果这个项目对你有帮助，请给个Star！**