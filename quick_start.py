#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统监控工具快速启动脚本
"""

import sys
import os
import subprocess
import platform

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {platform.python_version()}")
        return False
    return True

def install_dependencies():
    """安装依赖包"""
    print("检查并安装依赖包...")
    
    try:
        # 使用清华镜像源安装依赖
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt", 
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
        print("依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        return False

def run_monitor(mode="cli"):
    """运行监控程序"""
    print(f"启动系统监控工具 ({mode} 模式)...")
    
    try:
        # 导入并运行主程序
        from main import main as run_main
        
        # 设置命令行参数
        sys.argv = ['main.py', '--mode', mode]
        
        run_main()
    except ImportError as e:
        print(f"导入主程序失败: {e}")
        return False
    except Exception as e:
        print(f"程序运行出错: {e}")
        return False

def main():
    """主函数"""
    print("=== 系统监控工具快速启动 ===")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print()
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        print("依赖安装失败，请检查网络连接")
        sys.exit(1)
    
    # 选择运行模式
    print("请选择运行模式:")
    print("1. 命令行模式 (cli)")
    print("2. Web界面模式 (web)")
    print("3. API接口模式 (api)")
    print("4. 测试模式 (test)")
    
    while True:
        choice = input("\n请输入选择 (1-4, 默认1): ").strip()
        
        if not choice:
            choice = "1"
        
        mode_map = {
            "1": "cli",
            "2": "web", 
            "3": "api",
            "4": "test"
        }
        
        if choice in mode_map:
            mode = mode_map[choice]
            break
        else:
            print("无效选择，请输入1-4")
    
    # 运行监控程序
    if mode == "test":
        print("运行测试模式...")
        subprocess.run([sys.executable, "test_monitor.py"])
    else:
        run_monitor(mode)

if __name__ == "__main__":
    main() 