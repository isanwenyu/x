# X Tweet Monitor & XTracker Service

A Python service that monitors Twitter/X tweets for a specific user and pushes notifications to DingTalk. Uses Nitter mirrors for scraping tweets without requiring official API access.

## ✨ Features

- **Real-time Monitoring**: Monitors Twitter/X accounts for new tweets
- **DingTalk Integration**: Sends rich markdown notifications to DingTalk groups
- **Nitter Support**: Uses Nitter mirrors to avoid Twitter API limitations
- **XTracker Stats**: Fetches daily statistics from XTracker API
- **Scheduled Tasks**: Configurable polling intervals and hourly stats
- **Robust Error Handling**: Comprehensive error handling with retry logic
- **State Persistence**: File-based tracking of processed tweets
- **Systemd Service**: Ready for production deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- Systemd (for production deployment)

### Installation

1. **Clone and setup**:
   ```bash
   git clone https://github.com/isanwenyu/x.git
   cd x
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   # Copy and edit environment file
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the service**:
   ```bash
   python -m x.main
   ```

### Configuration (.env)

```bash
# DingTalk机器人配置
DINGTALK_ACCESS_TOKEN=your-dingtalk-token-here

# Twitter/X监控配置
X_USERNAME=elonmusk
X_POLL_SECONDS=60

# Nitter镜像站点列表（逗号分隔）
NITTER_BASE_URLS=https://nitter.poast.org,https://nitter.privacydev.net,https://nitter.cz

# XTracker API配置
XTRACKER_URL=https://www.xtracker.io/api/users?stats=true&platform=X

# 时区设置
TIMEZONE=Asia/Shanghai

# 数据存储路径
STATE_DIR=./data/state
LOG_DIR=./data/logs

# 首次运行时是否推送历史推文
ON_FIRST_RUN_PUSH_ALL=false
```

## 📋 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DINGTALK_ACCESS_TOKEN` | **Required** DingTalk webhook token | - |
| `X_USERNAME` | Twitter username to monitor | `elonmusk` |
| `X_POLL_SECONDS` | Polling interval in seconds | `60` |
| `NITTER_BASE_URLS` | Comma-separated Nitter mirror URLs | `https://nitter.poast.org` |
| `XTRACKER_URL` | XTracker API endpoint | XTracker default |
| `TIMEZONE` | Timezone for scheduling | `Asia/Shanghai` |
| `STATE_DIR` | State file directory | `./data/state` |
| `LOG_DIR` | Log file directory | `./data/logs` |
| `ON_FIRST_RUN_PUSH_ALL` | Push all tweets on first run | `false` |

## 🏗️ Project Structure

```
x/
├── x/                     # Python package
│   ├── __init__.py       # Package initialization
│   ├── config.py         # Configuration management
│   ├── dingtalk.py       # DingTalk client
│   ├── logging_config.py # Logging setup
│   ├── main.py           # Main entry point
│   ├── scheduler.py      # Task scheduling
│   ├── state.py          # State management
│   ├── twitter_monitor.py # Twitter monitoring
│   └── xtracker_client.py # XTracker client
├── data/                 # Data storage
│   ├── logs/            # Application logs
│   └── state/           # State files
├── docs/                # Documentation
├── scripts/             # Deployment scripts
│   └── systemd/         # Systemd service files
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
└── README.md           # This file
```

## 🛠️ Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run the service
python -m x.main
```

### Testing

```bash
# Test DingTalk connection
python -c "from x.dingtalk import test_dingtalk; test_dingtalk()"

# Test XTracker connection  
python -c "from x.xtracker_client import test_xtracker; test_xtracker()"

# Test configuration loading
python -c "from x.config import load_settings; print(load_settings())"
```

## 🚀 Production Deployment

### Systemd Service

1. **Install service**:
   ```bash
   sudo ./scripts/systemd/install.sh
   ```

2. **Configure service**:
   Edit `/opt/x-monitor/.env` with your actual configuration

3. **Manage service**:
   ```bash
   # Start service
   sudo systemctl start x-monitor.service
   
   # Stop service
   sudo systemctl stop x-monitor.service
   
   # View logs
   journalctl -u x-monitor.service -f
   
   # Check status
   systemctl status x-monitor.service
   ```

4. **Uninstall**:
   ```bash
   sudo ./scripts/systemd/uninstall.sh
   ```

### Manual Deployment

1. **Create service user**:
   ```bash
   sudo useradd --system --shell /bin/false --home-dir /opt/x-monitor xmonitor
   ```

2. **Install application**:
   ```bash
   sudo mkdir -p /opt/x-monitor
   sudo cp -r x/ requirements.txt .env /opt/x-monitor/
   sudo chown -R xmonitor: /opt/x-monitor
   ```

3. **Setup virtual environment**:
   ```bash
   sudo -u xmonitor python -m venv /opt/x-monitor/venv
   sudo -u xmonitor /opt/x-monitor/venv/bin/pip install -r /opt/x-monitor/requirements.txt
   ```

4. **Create systemd service**:
   Copy `scripts/systemd/x-monitor.service` to `/etc/systemd/system/`

5. **Start service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable x-monitor.service
   sudo systemctl start x-monitor.service
   ```