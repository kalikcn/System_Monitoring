#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统监控工具测试脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from core.cpu_monitor import CPUMonitor
        print("✓ CPU监控模块导入成功")
    except Exception as e:
        print(f"✗ CPU监控模块导入失败: {e}")
    
    try:
        from core.memory_monitor import MemoryMonitor
        print("✓ 内存监控模块导入成功")
    except Exception as e:
        print(f"✗ 内存监控模块导入失败: {e}")
    
    try:
        from core.gpu_monitor import GPUMonitor
        print("✓ GPU监控模块导入成功")
    except Exception as e:
        print(f"✗ GPU监控模块导入失败: {e}")
    
    try:
        from core.disk_monitor import DiskMonitor
        print("✓ 磁盘监控模块导入成功")
    except Exception as e:
        print(f"✗ 磁盘监控模块导入失败: {e}")
    
    try:
        from core.network_monitor import NetworkMonitor
        print("✓ 网络监控模块导入成功")
    except Exception as e:
        print(f"✗ 网络监控模块导入失败: {e}")
    
    try:
        from utils.helpers import get_system_info
        print("✓ 工具函数模块导入成功")
    except Exception as e:
        print(f"✗ 工具函数模块导入失败: {e}")

def test_monitors():
    """测试监控功能"""
    print("\n测试监控功能...")
    
    try:
        from core.cpu_monitor import CPUMonitor
        cpu_monitor = CPUMonitor()
        cpu_info = cpu_monitor.get_cpu_info()
        if cpu_info:
            print(f"✓ CPU信息获取成功: {cpu_info.get('cpu_usage_percent', 0):.1f}%")
        else:
            print("✗ CPU信息获取失败")
    except Exception as e:
        print(f"✗ CPU监控测试失败: {e}")
    
    try:
        from core.memory_monitor import MemoryMonitor
        memory_monitor = MemoryMonitor()
        memory_info = memory_monitor.get_memory_info()
        if memory_info:
            print(f"✓ 内存信息获取成功: {memory_info.get('percent', 0):.1f}%")
        else:
            print("✗ 内存信息获取失败")
    except Exception as e:
        print(f"✗ 内存监控测试失败: {e}")
    
    try:
        from core.disk_monitor import DiskMonitor
        disk_monitor = DiskMonitor()
        disk_info = disk_monitor.get_disk_info()
        if disk_info:
            print(f"✓ 磁盘信息获取成功: {len(disk_info.get('disks', []))} 个分区")
        else:
            print("✗ 磁盘信息获取失败")
    except Exception as e:
        print(f"✗ 磁盘监控测试失败: {e}")
    
    try:
        from core.network_monitor import NetworkMonitor
        network_monitor = NetworkMonitor()
        network_info = network_monitor.get_network_info()
        if network_info:
            print(f"✓ 网络信息获取成功: {len(network_info.get('interfaces', []))} 个接口")
        else:
            print("✗ 网络信息获取失败")
    except Exception as e:
        print(f"✗ 网络监控测试失败: {e}")

def test_helpers():
    """测试工具函数"""
    print("\n测试工具函数...")
    
    try:
        from utils.helpers import get_system_info, bytes_to_gb, format_speed
        system_info = get_system_info()
        print(f"✓ 系统信息获取成功: {system_info['platform']}")
        
        # 测试格式化函数
        test_bytes = 1024 * 1024 * 1024  # 1GB
        gb_result = bytes_to_gb(test_bytes)
        speed_result = format_speed(test_bytes)
        print(f"✓ 格式化函数测试成功: {gb_result}GB, {speed_result}")
        
    except Exception as e:
        print(f"✗ 工具函数测试失败: {e}")

def main():
    """主测试函数"""
    print("=== 系统监控工具测试 ===")
    print()
    
    test_imports()
    test_monitors()
    test_helpers()
    
    print("\n=== 测试完成 ===")
    print("如果所有测试都通过，说明系统监控工具可以正常运行")

if __name__ == "__main__":
    main() 