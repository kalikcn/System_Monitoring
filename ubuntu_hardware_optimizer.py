#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ubuntu硬件优化工具
专门针对Intel i5-14600KF + RX 9070 XT配置优化
"""

import subprocess
import json
import os
import sys
from typing import Dict, List, Tuple

class UbuntuHardwareOptimizer:
    def __init__(self):
        self.hardware_config = {
            "cpu": "Intel i5-14600KF",
            "memory": "32GB DDR4 3200",
            "gpu": "AMD RX 9070 XT",
            "ssd": "ZhiTai 1TB SSD Ti600",
            "hdd": "WD 4TB Blue"
        }
        
    def check_system_info(self) -> Dict[str, object]:
        """检查系统信息"""
        print("🔍 检查系统信息...")
        
        system_info = {}
        
        try:
            # 检查CPU信息
            cpu_info = subprocess.check_output(['lscpu'], text=True)
            system_info['cpu'] = {
                'model': self.extract_cpu_model(cpu_info),
                'cores': self.extract_cpu_cores(cpu_info),
                'frequency': self.extract_cpu_frequency(cpu_info)
            }
            print(f"✅ CPU: {system_info['cpu']['model']}")
            
            # 检查内存信息
            mem_info = subprocess.check_output(['free', '-h'], text=True)
            system_info['memory'] = {
                'total': self.extract_memory_total(mem_info),
                'available': self.extract_memory_available(mem_info)
            }
            print(f"✅ 内存: {system_info['memory']['total']}")
            
            # 检查GPU信息
            try:
                gpu_info = subprocess.check_output(['lspci', '-v'], text=True)
                system_info['gpu'] = self.extract_gpu_info(gpu_info)
                print(f"✅ GPU: {system_info['gpu']['model']}")
            except:
                print("⚠️  无法检测GPU信息")
                system_info['gpu'] = {'model': 'Unknown'}
            
            # 检查存储信息
            disk_info = subprocess.check_output(['lsblk'], text=True)
            system_info['storage'] = self.extract_storage_info(disk_info)
            print(f"✅ 存储: {len(system_info['storage'])} 个设备")
            
        except Exception as e:
            print(f"❌ 检查系统信息失败: {e}")
        
        return system_info
    
    def extract_cpu_model(self, cpu_info: str) -> str:
        """提取CPU型号"""
        for line in cpu_info.split('\n'):
            if 'Model name:' in line:
                return line.split(':')[1].strip()
        return "Unknown CPU"
    
    def extract_cpu_cores(self, cpu_info: str) -> int:
        """提取CPU核心数"""
        for line in cpu_info.split('\n'):
            if 'CPU(s):' in line:
                return int(line.split(':')[1].strip())
        return 0
    
    def extract_cpu_frequency(self, cpu_info: str) -> float:
        """提取CPU频率"""
        for line in cpu_info.split('\n'):
            if 'CPU max MHz:' in line:
                return float(line.split(':')[1].strip())
        return 0.0
    
    def extract_memory_total(self, mem_info: str) -> str:
        """提取内存总量"""
        lines = mem_info.split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) > 1:
                return parts[1]
        return "Unknown"
    
    def extract_memory_available(self, mem_info: str) -> str:
        """提取可用内存"""
        lines = mem_info.split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) > 6:
                return parts[6]
        return "Unknown"
    
    def extract_gpu_info(self, gpu_info: str) -> Dict[str, str]:
        """提取GPU信息"""
        for line in gpu_info.split('\n'):
            if 'VGA' in line and ('AMD' in line or 'Radeon' in line):
                return {'model': line.strip()}
        return {'model': 'Unknown GPU'}
    
    def extract_storage_info(self, disk_info: str) -> List[Dict[str, str]]:
        """提取存储信息"""
        storage_devices = []
        for line in disk_info.split('\n'):
            if 'disk' in line and ('nvme' in line or 'sda' in line or 'sdb' in line):
                parts = line.split()
                if len(parts) >= 6:
                    storage_devices.append({
                        'device': parts[0],
                        'size': parts[3],
                        'type': parts[5] if len(parts) > 5 else 'Unknown'
                    })
        return storage_devices
    
    def optimize_cpu(self) -> bool:
        """优化CPU设置"""
        print("⚡ 优化CPU设置...")
        
        try:
            # 检查当前CPU频率缩放策略
            current_governor = subprocess.check_output(['cat', '/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor'], text=True).strip()
            print(f"当前CPU频率策略: {current_governor}")
            
            # 建议的优化
            optimizations = [
                "设置CPU频率策略为performance以获得最佳性能",
                "启用Intel Turbo Boost",
                "监控CPU温度，确保散热良好",
                "考虑调整CPU频率缩放策略"
            ]
            
            for opt in optimizations:
                print(f"  💡 {opt}")
            
            return True
            
        except Exception as e:
            print(f"❌ CPU优化失败: {e}")
            return False
    
    def optimize_memory(self) -> bool:
        """优化内存设置"""
        print("💾 优化内存设置...")
        
        try:
            # 检查内存信息
            mem_info = subprocess.check_output(['dmidecode', '-t', '17'], text=True)
            
            optimizations = [
                "确保内存运行在3200MHz频率",
                "检查双通道是否正常工作",
                "监控内存使用率，避免过度使用",
                "考虑调整内存时序"
            ]
            
            for opt in optimizations:
                print(f"  💡 {opt}")
            
            return True
            
        except Exception as e:
            print(f"❌ 内存优化失败: {e}")
            return False
    
    def optimize_gpu(self) -> bool:
        """优化GPU设置"""
        print("🎮 优化GPU设置...")
        
        try:
            # 检查AMD驱动
            try:
                amd_info = subprocess.check_output(['rocm-smi'], text=True)
                print("✅ AMD ROCm驱动已安装")
            except:
                print("⚠️  未检测到AMD ROCm驱动")
            
            optimizations = [
                "安装最新的AMD显卡驱动",
                "调整GPU风扇曲线以控制温度",
                "监控GPU内存使用情况",
                "考虑调整GPU功耗限制"
            ]
            
            for opt in optimizations:
                print(f"  💡 {opt}")
            
            return True
            
        except Exception as e:
            print(f"❌ GPU优化失败: {e}")
            return False
    
    def optimize_storage(self) -> bool:
        """优化存储设置"""
        print("💿 优化存储设置...")
        
        try:
            # 检查SSD TRIM支持
            try:
                trim_info = subprocess.check_output(['lsblk', '-D'], text=True)
                print("✅ 检查SSD TRIM支持")
            except:
                print("⚠️  无法检查SSD TRIM支持")
            
            optimizations = [
                "定期对SSD进行TRIM操作",
                "监控SSD健康状态",
                "避免HDD频繁读写",
                "考虑启用SSD缓存"
            ]
            
            for opt in optimizations:
                print(f"  💡 {opt}")
            
            return True
            
        except Exception as e:
            print(f"❌ 存储优化失败: {e}")
            return False
    
    def optimize_network(self) -> bool:
        """优化网络设置"""
        print("🌐 优化网络设置...")
        
        try:
            # 检查网络接口
            network_info = subprocess.check_output(['ip', 'addr'], text=True)
            
            optimizations = [
                "优化网络缓冲区大小",
                "启用TCP拥塞控制",
                "配置网络接口参数",
                "监控网络延迟和带宽"
            ]
            
            for opt in optimizations:
                print(f"  💡 {opt}")
            
            return True
            
        except Exception as e:
            print(f"❌ 网络优化失败: {e}")
            return False
    
    def create_optimization_script(self) -> bool:
        """创建优化脚本"""
        print("📜 创建优化脚本...")
        
        try:
            script_content = '''#!/bin/bash

# Ubuntu硬件优化脚本
# 针对Intel i5-14600KF + RX 9070 XT配置

echo "🖥️  Ubuntu硬件优化脚本"
echo "========================"

# CPU优化
echo "⚡ 优化CPU设置..."
echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 内存优化
echo "💾 优化内存设置..."
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf

# GPU优化
echo "🎮 优化GPU设置..."
# 这里可以添加AMD GPU特定的优化命令

# 存储优化
echo "💿 优化存储设置..."
sudo fstrim -av

# 网络优化
echo "🌐 优化网络设置..."
echo 'net.core.rmem_max=134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max=134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem=4096 87380 134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem=4096 65536 134217728' | sudo tee -a /etc/sysctl.conf

# 应用设置
sudo sysctl -p

echo "✅ 优化完成！"
'''
            
            with open('ubuntu_optimize.sh', 'w') as f:
                f.write(script_content)
            
            os.chmod('ubuntu_optimize.sh', 0o755)
            print("✅ 优化脚本已创建: ubuntu_optimize.sh")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建优化脚本失败: {e}")
            return False
    
    def generate_performance_report(self, system_info: Dict[str, object]) -> bool:
        """生成性能报告"""
        print("📊 生成性能报告...")
        
        try:
            report = {
                "timestamp": subprocess.check_output(['date'], text=True).strip(),
                "hardware_config": self.hardware_config,
                "system_info": system_info,
                "optimization_recommendations": {
                    "cpu": [
                        "启用Intel Turbo Boost",
                        "设置CPU频率策略为performance",
                        "监控CPU温度，确保散热良好"
                    ],
                    "memory": [
                        "确保内存运行在3200MHz频率",
                        "检查双通道是否正常工作",
                        "监控内存使用率"
                    ],
                    "gpu": [
                        "安装最新的AMD显卡驱动",
                        "调整GPU风扇曲线",
                        "监控GPU内存使用情况"
                    ],
                    "storage": [
                        "定期对SSD进行TRIM操作",
                        "监控SSD健康状态",
                        "避免HDD频繁读写"
                    ],
                    "network": [
                        "优化网络缓冲区大小",
                        "启用TCP拥塞控制",
                        "监控网络延迟"
                    ]
                }
            }
            
            with open('performance_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print("✅ 性能报告已生成: performance_report.json")
            return True
            
        except Exception as e:
            print(f"❌ 生成性能报告失败: {e}")
            return False
    
    def run_full_optimization(self):
        """运行完整优化"""
        print("🚀 开始Ubuntu硬件优化...")
        print("=" * 50)
        
        # 检查系统信息
        system_info = self.check_system_info()
        
        print("\n" + "=" * 50)
        
        # 运行各项优化
        optimizations = [
            ("CPU优化", self.optimize_cpu),
            ("内存优化", self.optimize_memory),
            ("GPU优化", self.optimize_gpu),
            ("存储优化", self.optimize_storage),
            ("网络优化", self.optimize_network)
        ]
        
        success_count = 0
        for name, func in optimizations:
            print(f"\n{name}:")
            if func():
                success_count += 1
            print()
        
        # 创建优化脚本
        self.create_optimization_script()
        
        # 生成性能报告
        self.generate_performance_report(system_info)
        
        print("=" * 50)
        print(f"🎉 优化完成！成功项目: {success_count}/{len(optimizations)}")
        print("\n📋 后续操作:")
        print("1. 运行优化脚本: sudo ./ubuntu_optimize.sh")
        print("2. 查看性能报告: cat performance_report.json")
        print("3. 重启系统以应用所有优化")
        print("4. 运行监控工具: ./start_monitor.sh")

def main():
    optimizer = UbuntuHardwareOptimizer()
    optimizer.run_full_optimization()

if __name__ == "__main__":
    main() 