#!/bin/bash

# Ubuntu系统监控工具安装脚本
# 专门针对Intel i5-14600KF + RX 9070 XT配置

echo "🖥️  Ubuntu系统监控工具安装脚本"
echo "=================================="
echo "目标硬件配置:"
echo "- CPU: Intel i5-14600KF"
echo "- 内存: Crucial 32GB DDR4 3200"
echo "- GPU: Sapphire RX 9070 XT Pulse 16GB"
echo "- 主板: MSI PRO B760M-A WIFI DDR4 II"
echo "- 存储: ZhiTai 1TB SSD + WD 4TB Blue"
echo "=================================="

# 检查是否为Ubuntu系统
if ! grep -q "Ubuntu" /etc/os-release; then
    echo "❌ 此脚本仅支持Ubuntu系统"
    exit 1
fi

echo "✅ 检测到Ubuntu系统"

# 更新系统包
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装Python依赖
echo "🐍 安装Python依赖..."
sudo apt install -y python3 python3-pip python3-venv

# 安装系统监控工具
echo "🔧 安装系统监控工具..."
sudo apt install -y htop iotop nethogs lm-sensors

# 安装AMD GPU驱动支持
echo "🎮 安装AMD GPU支持..."
sudo apt install -y rocm-opencl-runtime mesa-utils

# 安装网络工具
echo "🌐 安装网络工具..."
sudo apt install -y speedtest-cli net-tools

# 安装开发工具
echo "🛠️ 安装开发工具..."
sudo apt install -y build-essential git curl wget

# 配置lm-sensors
echo "🌡️ 配置温度传感器..."
sudo sensors-detect --auto

# 创建虚拟环境
echo "📁 创建Python虚拟环境..."
python3 -m venv ubuntu_monitor_env
source ubuntu_monitor_env/bin/activate

# 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装Python依赖包
echo "📦 安装Python依赖包..."
pip install -r requirements.txt

# 创建数据目录
echo "📂 创建数据目录..."
mkdir -p data/ubuntu_monitor
mkdir -p logs

# 设置权限
echo "🔐 设置文件权限..."
chmod +x ubuntu_monitor.py
chmod +x security_test.py

# 创建系统服务
echo "⚙️ 创建系统服务..."
sudo tee /etc/systemd/system/ubuntu-monitor.service > /dev/null <<EOF
[Unit]
Description=Ubuntu System Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/ubuntu_monitor_env/bin
ExecStart=$(pwd)/ubuntu_monitor_env/bin/python ubuntu_monitor.py --mode web
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
echo "🚀 启用系统服务..."
sudo systemctl daemon-reload
sudo systemctl enable ubuntu-monitor.service

# 创建桌面快捷方式
echo "🖥️ 创建桌面快捷方式..."
cat > ~/Desktop/Ubuntu监控.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Ubuntu系统监控
Comment=Intel i5-14600KF + RX 9070 XT 系统监控工具
Exec=$(pwd)/ubuntu_monitor_env/bin/python $(pwd)/ubuntu_monitor.py --mode web
Icon=utilities-system-monitor
Terminal=false
Categories=System;Monitor;
EOF

chmod +x ~/Desktop/Ubuntu监控.desktop

# 创建启动脚本
echo "📜 创建启动脚本..."
cat > start_monitor.sh <<EOF
#!/bin/bash
cd $(pwd)
source ubuntu_monitor_env/bin/activate
python ubuntu_monitor.py \$@
EOF

chmod +x start_monitor.sh

# 创建卸载脚本
echo "🗑️ 创建卸载脚本..."
cat > uninstall.sh <<EOF
#!/bin/bash
echo "正在卸载Ubuntu系统监控工具..."

# 停止服务
sudo systemctl stop ubuntu-monitor.service
sudo systemctl disable ubuntu-monitor.service

# 删除服务文件
sudo rm -f /etc/systemd/system/ubuntu-monitor.service
sudo systemctl daemon-reload

# 删除桌面快捷方式
rm -f ~/Desktop/Ubuntu监控.desktop

# 删除虚拟环境
rm -rf ubuntu_monitor_env

# 删除数据目录
rm -rf data/ubuntu_monitor

echo "卸载完成！"
EOF

chmod +x uninstall.sh

# 运行硬件检测
echo "🔍 运行硬件检测..."
python3 -c "
import subprocess
import sys

def check_hardware():
    print('检测硬件配置...')
    
    # 检查CPU
    try:
        cpu_info = subprocess.check_output(['lscpu'], text=True)
        if '14600KF' in cpu_info:
            print('✅ 检测到Intel i5-14600KF')
        else:
            print('⚠️  未检测到目标CPU型号')
    except:
        print('❌ 无法检测CPU信息')
    
    # 检查内存
    try:
        mem_info = subprocess.check_output(['free', '-h'], text=True)
        if '32G' in mem_info:
            print('✅ 检测到32GB内存')
        else:
            print('⚠️  内存容量可能不匹配')
    except:
        print('❌ 无法检测内存信息')
    
    # 检查GPU
    try:
        gpu_info = subprocess.check_output(['lspci', '-v'], text=True)
        if 'AMD' in gpu_info:
            print('✅ 检测到AMD显卡')
        else:
            print('⚠️  未检测到AMD显卡')
    except:
        print('❌ 无法检测GPU信息')
    
    # 检查存储
    try:
        disk_info = subprocess.check_output(['lsblk'], text=True)
        print('✅ 存储设备检测完成')
    except:
        print('❌ 无法检测存储设备')

check_hardware()
"

# 创建使用说明
echo "📖 创建使用说明..."
cat > README_UBUNTU.md <<EOF
# Ubuntu系统监控工具使用说明

## 🖥️ 硬件配置
- CPU: Intel i5-14600KF (14核20线程)
- 内存: Crucial 32GB DDR4 3200 (双通道)
- GPU: Sapphire RX 9070 XT Pulse 16GB
- 主板: MSI PRO B760M-A WIFI DDR4 II
- 存储: ZhiTai 1TB SSD Ti600 + WD 4TB Blue
- 散热: Thermalright AK90 V2 + TL-C12C

## 🚀 快速启动

### 命令行模式
\`\`\`bash
./start_monitor.sh --mode cli
\`\`\`

### Web界面模式
\`\`\`bash
./start_monitor.sh --mode web
\`\`\`
然后在浏览器访问: http://localhost:5000

### API模式
\`\`\`bash
./start_monitor.sh --mode api
\`\`\`
API端点: http://localhost:5000/api

## ⚙️ 系统服务

### 启动服务
\`\`\`bash
sudo systemctl start ubuntu-monitor
\`\`\`

### 停止服务
\`\`\`bash
sudo systemctl stop ubuntu-monitor
\`\`\`

### 查看状态
\`\`\`bash
sudo systemctl status ubuntu-monitor
\`\`\`

## 🔧 配置说明

配置文件: \`ubuntu_monitor_config.json\`

主要配置项:
- 监控间隔: 2秒
- 数据保留: 30天
- 告警阈值: CPU 85°C, GPU 85°C, 内存 80%

## 📊 监控功能

### CPU监控
- 使用率监控 (14核20线程)
- 温度监控 (TDP 125W)
- 频率监控 (3.5GHz-5.3GHz)
- 功耗监控

### 内存监控
- 使用率监控 (32GB)
- 双通道监控
- 频率监控 (3200MHz)

### GPU监控
- 使用率监控 (RX 9070 XT)
- 温度监控
- 内存监控 (16GB GDDR6)
- 风扇转速监控

### 存储监控
- SSD健康监控 (ZhiTai Ti600)
- HDD健康监控 (WD Blue 4TB)
- SMART属性监控
- 温度监控

### 网络监控
- 带宽监控
- 延迟监控
- 网速测试

## 🔍 故障排除

### 温度传感器问题
\`\`\`bash
sudo sensors-detect --auto
sudo modprobe coretemp
sudo modprobe k10temp
\`\`\`

### GPU监控问题
\`\`\`bash
sudo apt install rocm-opencl-runtime
\`\`\`

### 权限问题
\`\`\`bash
sudo chmod +x start_monitor.sh
sudo chown -R \$USER:\$USER .
\`\`\`

## 🗑️ 卸载

运行卸载脚本:
\`\`\`bash
./uninstall.sh
\`\`\`

## 📞 技术支持

如遇问题，请检查:
1. 硬件是否匹配
2. 驱动是否正确安装
3. 权限是否正确设置
4. 日志文件: \`logs/SystemMonitor_*.log\`

EOF

echo "✅ 安装完成！"
echo ""
echo "🎉 Ubuntu系统监控工具安装成功！"
echo ""
echo "📋 安装内容:"
echo "- Python虚拟环境: ubuntu_monitor_env"
echo "- 系统服务: ubuntu-monitor.service"
echo "- 桌面快捷方式: Ubuntu监控"
echo "- 启动脚本: start_monitor.sh"
echo "- 卸载脚本: uninstall.sh"
echo "- 使用说明: README_UBUNTU.md"
echo ""
echo "🚀 快速启动:"
echo "- 命令行模式: ./start_monitor.sh --mode cli"
echo "- Web界面: ./start_monitor.sh --mode web"
echo "- 系统服务: sudo systemctl start ubuntu-monitor"
echo ""
echo "📖 详细说明请查看: README_UBUNTU.md" 