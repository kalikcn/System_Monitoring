# 系统监控工具 (System Monitoring Tool)

一个跨平台的系统监控工具，支持Windows和Ubuntu平台，提供实时硬件监控和网络状态检测。

## 🚀 功能特性

### 硬件监控
- **CPU监控**: 使用率、温度、频率、核心数
- **内存监控**: 使用率、可用内存、交换空间
- **GPU监控**: 使用率、温度、内存使用、风扇转速
- **磁盘监控**: 读写速度、使用率、温度、健康状态
- **网络监控**: 上传/下载速度、延迟、连接状态

### 平台支持
- ✅ Windows 10/11
- ✅ Ubuntu 18.04+
- ✅ 其他Linux发行版

## 📦 安装

### 1. 克隆项目
```bash
git clone <repository-url>
cd System_Monitoring
```

### 2. 安装依赖
```bash
# 使用清华镜像源加速下载
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 运行应用
```bash
python main.py
```

## 🖥️ 使用方法

### 命令行模式
```bash
python main.py --mode cli
```

### Web界面模式
```bash
python main.py --mode web
```
然后在浏览器中访问: http://localhost:5000

### API模式
```bash
python main.py --mode api
```
API端点: http://localhost:5000/api

## 📊 监控指标

### CPU指标
- 总体使用率 (%)
- 各核心使用率 (%)
- 当前频率 (MHz)
- 温度 (°C)
- 核心数量

### 内存指标
- 总内存 (GB)
- 已使用内存 (GB)
- 可用内存 (GB)
- 内存使用率 (%)
- 交换空间使用情况

### GPU指标
- GPU使用率 (%)
- 内存使用率 (%)
- 温度 (°C)
- 风扇转速 (RPM)
- 功耗 (W)

### 磁盘指标
- 读写速度 (MB/s)
- 磁盘使用率 (%)
- 磁盘温度 (°C)
- 健康状态
- 剩余空间

### 网络指标
- 上传速度 (Mbps)
- 下载速度 (Mbps)
- 延迟 (ms)
- 数据包丢失率 (%)

## 🔧 配置

配置文件位于 `config/settings.json`，可以自定义：
- 监控间隔时间
- 数据保存路径
- 告警阈值
- 日志级别

## 📈 数据可视化

- 实时图表显示
- 历史数据趋势
- 告警通知
- 数据导出功能

## 🛠️ 开发

### 项目结构
```
System_Monitoring/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖包
├── config/                # 配置文件
├── core/                  # 核心监控模块
│   ├── cpu_monitor.py     # CPU监控
│   ├── memory_monitor.py  # 内存监控
│   ├── gpu_monitor.py     # GPU监控
│   ├── disk_monitor.py    # 磁盘监控
│   └── network_monitor.py # 网络监控
├── web/                   # Web界面
│   ├── app.py            # Flask应用
│   ├── templates/        # HTML模板
│   └── static/           # 静态文件
├── api/                   # API接口
│   └── routes.py         # API路由
└── utils/                 # 工具函数
    ├── logger.py         # 日志工具
    └── helpers.py        # 辅助函数
```

## 📝 许可证

MIT License

## 🤝 贡献
作者：kalikcn

联系方式：K36@LIVE.CN


欢迎提交Issue和Pull Request！ 