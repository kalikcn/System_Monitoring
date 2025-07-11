#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AMD GPU 检测测试脚本
"""

import sys
import os
import platform

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gputil():
    """测试GPUtil库"""
    print("=== 测试GPUtil库 ===")
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        print(f"检测到 {len(gpus)} 个GPU:")
        for i, gpu in enumerate(gpus):
            print(f"  GPU {i}: {gpu.name}")
            print(f"    使用率: {gpu.load * 100:.1f}%" if gpu.load else "    使用率: 未知")
            print(f"    内存: {gpu.memoryUsed}/{gpu.memoryTotal} MB")
            print(f"    温度: {gpu.temperature}°C" if gpu.temperature else "    温度: 未知")
        return True
    except ImportError:
        print("GPUtil库未安装")
        return False
    except Exception as e:
        print(f"GPUtil测试失败: {e}")
        return False

def test_wmi_windows():
    """测试Windows WMI"""
    if platform.system() != "Windows":
        print("WMI测试仅适用于Windows系统")
        return False
    
    print("=== 测试Windows WMI ===")
    try:
        import wmi
        w = wmi.WMI()
        amd_gpus = []
        for gpu in w.Win32_VideoController():
            if "AMD" in gpu.Name or "Radeon" in gpu.Name:
                amd_gpus.append(gpu)
        
        print(f"检测到 {len(amd_gpus)} 个AMD GPU:")
        for gpu in amd_gpus:
            print(f"  GPU: {gpu.Name}")
            if gpu.AdapterRAM:
                print(f"    显存: {gpu.AdapterRAM // (1024*1024)} MB")
            else:
                print("    显存: 未知")
        return len(amd_gpus) > 0
    except ImportError:
        print("wmi库未安装")
        return False
    except Exception as e:
        print(f"WMI测试失败: {e}")
        return False

def test_lspci_linux():
    """测试Linux lspci"""
    if platform.system() != "Linux":
        print("lspci测试仅适用于Linux系统")
        return False
    
    print("=== 测试Linux lspci ===")
    try:
        import subprocess
        result = subprocess.run(['lspci'], capture_output=True, text=True)
        if result.returncode == 0:
            amd_gpus = []
            for line in result.stdout.split('\n'):
                if 'VGA' in line and ('AMD' in line or 'Radeon' in line):
                    amd_gpus.append(line)
            
            print(f"检测到 {len(amd_gpus)} 个AMD GPU:")
            for gpu in amd_gpus:
                print(f"  GPU: {gpu.split(':')[-1].strip()}")
            return len(amd_gpus) > 0
        else:
            print("lspci命令执行失败")
            return False
    except Exception as e:
        print(f"lspci测试失败: {e}")
        return False

def test_our_monitor():
    """测试我们的GPU监控模块"""
    print("=== 测试GPU监控模块 ===")
    try:
        from core.gpu_monitor import GPUMonitor
        monitor = GPUMonitor()
        gpu_info = monitor.get_gpu_info()
        
        if gpu_info and gpu_info.get('gpus'):
            print(f"检测到 {len(gpu_info['gpus'])} 个GPU:")
            for gpu in gpu_info['gpus']:
                print(f"  GPU {gpu['id']}: {gpu['name']}")
                print(f"    使用率: {gpu['load_percent']:.1f}%")
                print(f"    内存: {gpu['memory_used_mb']}/{gpu['memory_total_mb']} MB")
                print(f"    温度: {gpu['temperature']}°C" if gpu['temperature'] else "    温度: 未知")
            return True
        else:
            print("未检测到GPU")
            return False
    except Exception as e:
        print(f"GPU监控模块测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=== AMD GPU 检测测试 ===")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print()
    
    results = []
    
    # 测试GPUtil
    results.append(("GPUtil", test_gputil()))
    
    # 测试WMI (Windows)
    if platform.system() == "Windows":
        results.append(("Windows WMI", test_wmi_windows()))
    
    # 测试lspci (Linux)
    if platform.system() == "Linux":
        results.append(("Linux lspci", test_lspci_linux()))
    
    # 测试我们的监控模块
    results.append(("GPU监控模块", test_our_monitor()))
    
    print("\n=== 测试结果汇总 ===")
    for method, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{method}: {status}")
    
    # 给出建议
    print("\n=== 建议 ===")
    if any(success for _, success in results):
        print("✅ GPU检测功能正常工作")
        if not results[0][1]:  # GPUtil失败
            print("💡 建议安装GPUtil库获得完整功能:")
            print("   pip install GPUtil -i https://pypi.tuna.tsinghua.edu.cn/simple")
    else:
        print("❌ 所有GPU检测方法都失败了")
        print("💡 请检查:")
        print("   1. 是否安装了显卡驱动")
        print("   2. 是否安装了必要的Python库")
        print("   3. 是否有足够的权限")

if __name__ == "__main__":
    main() 