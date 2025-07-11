#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统监控工具启动脚本
支持Windows和Ubuntu平台
"""

import sys
import os
import subprocess
import platform

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'psutil',
        'flask',
        'flask-cors',
        'flask-socketio'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        
        install = input("\n是否自动安装依赖包? (y/n): ").lower().strip()
        if install == 'y':
            install_dependencies(missing_packages)
        else:
            print("请手动安装依赖包后重试")
            sys.exit(1)

def install_dependencies(packages):
    """安装依赖包"""
    print("正在安装依赖包...")
    
    # 使用清华镜像源
    mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
    
    for package in packages:
        try:
            print(f"安装 {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                package, "-i", mirror
            ])
            print(f"{package} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"{package} 安装失败: {e}")
            sys.exit(1)

def main():
    """主函数"""
    print("=== 系统监控工具 ===")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print()
    
    # 检查依赖
    check_dependencies()
    
    # 导入主程序
    try:
        from main import main as run_main
        run_main()
    except ImportError as e:
        print(f"导入主程序失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 