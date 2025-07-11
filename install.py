#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统监控工具安装脚本
支持Windows和Ubuntu平台
"""

import os
import sys
import subprocess
import platform
import shutil

def create_directories():
    """创建必要的目录"""
    directories = [
        'logs',
        'data',
        'config'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建目录: {directory}")

def install_requirements():
    """安装依赖包"""
    print("正在安装依赖包...")
    
    # 使用清华镜像源
    mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt", "-i", mirror
        ])
        print("依赖包安装成功")
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        return False
    
    return True

def setup_config():
    """设置配置文件"""
    config_file = "config/settings.json"
    
    if not os.path.exists(config_file):
        print("创建默认配置文件...")
        default_config = {
            "monitoring": {
                "interval": 2,
                "history_size": 1000,
                "log_level": "INFO"
            },
            "alerts": {
                "cpu_usage_threshold": 90,
                "memory_usage_threshold": 85,
                "gpu_usage_threshold": 95,
                "disk_usage_threshold": 90,
                "temperature_threshold": 80
            },
            "web": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False
            },
            "data": {
                "save_path": "./data",
                "export_format": "json"
            },
            "network": {
                "speedtest_interval": 300,
                "ping_targets": ["8.8.8.8", "114.114.114.114"]
            }
        }
        
        import json
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        print("配置文件创建成功")

def check_system_requirements():
    """检查系统要求"""
    print("检查系统要求...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        return False
    
    print(f"Python版本: {platform.python_version()} ✓")
    
    # 检查操作系统
    system = platform.system()
    if system not in ['Windows', 'Linux']:
        print(f"警告: 未测试的操作系统 {system}")
    
    print(f"操作系统: {system} {platform.release()} ✓")
    
    return True

def create_startup_scripts():
    """创建启动脚本"""
    print("创建启动脚本...")
    
    # Windows批处理文件
    if platform.system() == "Windows":
        with open("start_monitor.bat", "w", encoding="gbk") as f:
            f.write("@echo off\n")
            f.write("echo 启动系统监控工具...\n")
            f.write("python main.py --mode cli\n")
            f.write("pause\n")
        print("创建启动脚本: start_monitor.bat")
    
    # Linux shell脚本
    else:
        with open("start_monitor.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("echo '启动系统监控工具...'\n")
            f.write("python3 main.py --mode cli\n")
        
        # 设置执行权限
        os.chmod("start_monitor.sh", 0o755)
        print("创建启动脚本: start_monitor.sh")

def main():
    """主安装函数"""
    print("=== 系统监控工具安装程序 ===")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print()
    
    # 检查系统要求
    if not check_system_requirements():
        sys.exit(1)
    
    # 创建目录
    create_directories()
    
    # 安装依赖
    if not install_requirements():
        print("安装失败，请检查网络连接或手动安装依赖包")
        sys.exit(1)
    
    # 设置配置
    setup_config()
    
    # 创建启动脚本
    create_startup_scripts()
    
    print("\n=== 安装完成 ===")
    print("使用方法:")
    print("1. 命令行模式: python main.py --mode cli")
    print("2. Web界面模式: python main.py --mode web")
    print("3. API模式: python main.py --mode api")
    print("\nWeb界面访问地址: http://localhost:5000")
    print("API接口地址: http://localhost:5000/api")

if __name__ == "__main__":
    main() 