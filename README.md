# System_Monitoring 系统监控平台

## 项目简介
System_Monitoring 是一款跨平台（Windows、Ubuntu）高性能主机系统资源监控与可视化平台。支持 CPU、内存、GPU、磁盘、网络等多维度实时监控，集成 Web 大屏、API、告警推送、优化建议和自定义硬件配置，适用于服务器、工作站和个人电脑。

---

## 主要功能
- 实时监控 CPU、内存、GPU、磁盘、网络等资源
- 高科技感 Web 大屏可视化，支持 SocketIO 实时推送
- 多平台/多硬件支持，专为 AMD/NVIDIA GPU 优化
- RESTful API 数据接口，便于系统集成
- 告警推送与优化建议
- 日志记录与历史数据存储
- 用户认证与安全控制
- 灵活的自定义配置，适合批量部署

---

## 技术特性
- Python 3.9+，Flask + Flask-SocketIO
- 前端响应式大屏，支持动态粒子、流光动效
- 支持 AMD/NVIDIA GPU、DDR4/DDR5、SSD/HDD 等主流硬件
- 配置文件 JSON 格式，易于修改和迁移
- 支持桌面、邮件、Webhook 等多种告警通知方式

---

## 安装与部署

### 1. 克隆项目
```bash
git clone https://github.com/kalikcn/System_Monitoring.git
cd System_Monitoring
```

### 2. 安装依赖（推荐虚拟环境）
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 3. 配置参数
- 修改 `config/settings.json` 或 `ubuntu_monitor_config.json`，根据自己电脑硬件和需求自定义参数（详见 docs/自定义监控配置教程.md）

### 4. 启动主系统
```bash
python web/app.py
```

### 5. 访问 Web 大屏
- 主系统首页：http://localhost:5000/
- Ubuntu 专用监控大屏：http://localhost:5000/ubuntu_monitor/

---

## 目录结构
```
System_Monitoring/
├── README.md                  # 项目说明
├── requirements.txt           # 依赖包清单
├── .gitignore                 # Git忽略文件
├── main.py                    # 主入口（如有）
├── install.py                 # 一键安装脚本
├── config/                    # 配置文件
│   └── settings.json
├── core/                      # 监控核心模块
│   ├── cpu_monitor.py
│   ├── memory_monitor.py
│   ├── gpu_monitor.py
│   ├── disk_monitor.py
│   └── network_monitor.py
├── api/                       # API 路由
│   └── routes.py
├── security/                  # 安全与认证
├── utils/                     # 工具与日志
├── web/                       # Web 前端与蓝图
│   ├── app.py
│   ├── ubuntu_blueprint.py
│   ├── templates/
│   │   ├── index.html
│   │   └── ubuntu_index.html
│   └── static/
├── data/                      # 监控数据（建议 .gitignore）
├── logs/                      # 日志（建议 .gitignore）
├── docs/
│   └── 自定义监控配置教程.md
└── ubuntu_monitor_config.json # Ubuntu专用配置
```

---

## 配置与自定义
- 所有监控参数、告警阈值、通知方式等均可在 JSON 配置文件中自定义
- 支持多台主机批量部署，每台可用不同配置
- 详细教程见 `docs/自定义监控配置教程.md`

---

## 常见问题
- **依赖安装慢/失败**：请使用国内镜像源
- **端口冲突**：请在配置文件中修改端口
- **GPU 监控无数据**：请确认已安装对应驱动和依赖库
- **Web 页面无数据刷新**：请检查 SocketIO 服务是否正常

---

## 贡献与反馈
- 欢迎提交 Issue 和 Pull Request
- 如有建议或需求，请在 GitHub 讨论区留言

---

## 许可证

本项目采用 MIT License 开源，详见 LICENSE 文件。 

---

## 解决步骤

1. **拉取远程仓库内容并自动合并：**

```bash
git pull --rebase origin main
```

- 如果提示有冲突，按提示解决冲突后，使用 `git add .` 和 `git rebase --continue` 直到完成。

2. **再次推送到 GitHub：**

```bash
<code_block_to_apply_changes_from>
```

---

## 说明

- `git pull --rebase` 会把你的提交“叠加”到远程已有内容之后，历史更清晰。
- 如果你只想用本地内容覆盖远程（不推荐，除非远程内容可以丢弃），可以用 `git push -f origin main` 强制推送。但**一般建议先合并**，避免丢失远程内容。

---

## 🤝 贡献
作者：kalikcn

联系方式：K36@LIVE.CN


欢迎提交Issue和Pull Request！ 
