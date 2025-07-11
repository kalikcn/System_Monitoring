#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ubuntu系统监控工具
专门针对Intel i5-14600KF + RX 9070 XT配置优化
"""

import argparse
import time
import threading
import json
import os
import sys
from datetime import datetime
import subprocess

# 导入监控模块
from core.cpu_monitor import CPUMonitor
from core.memory_monitor import MemoryMonitor
from core.gpu_monitor import GPUMonitor
from core.disk_monitor import DiskMonitor
from core.network_monitor import NetworkMonitor
from utils.helpers import load_config, save_data, get_system_info
from utils.logger import logger

class UbuntuSystemMonitor:
    def __init__(self, config_file="ubuntu_monitor_config.json"):
        """初始化Ubuntu系统监控器"""
        self.config = self.load_ubuntu_config(config_file)
        self.monitors = {
            'cpu': CPUMonitor(),
            'memory': MemoryMonitor(),
            'gpu': GPUMonitor(),
            'disk': DiskMonitor(),
            'network': NetworkMonitor()
        }
        self.running = False
        self.monitoring_thread = None
        self.hardware_info = self.get_hardware_info()
        
        # 初始化硬件特定监控
        self.init_hardware_specific_monitoring()
        
    def load_ubuntu_config(self, config_file):
        """加载Ubuntu专用配置"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"加载Ubuntu配置: {config_file}")
            else:
                # 使用默认配置
                config = {
                    "monitoring": {"interval": 2, "history_size": 2000},
                    "alerts": {
                        "cpu_usage_threshold": 85,
                        "cpu_temp_threshold": 85,
                        "memory_usage_threshold": 80,
                        "gpu_usage_threshold": 90,
                        "gpu_temp_threshold": 85
                    },
                    "web": {"host": "0.0.0.0", "port": 5000},
                    "data": {"save_path": "./data/ubuntu_monitor"}
                }
                logger.info("使用默认Ubuntu配置")
            
            return config
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return {}
    
    def get_hardware_info(self):
        """获取硬件信息"""
        hardware_info = {
            "cpu": {
                "model": "Intel i5-14600KF",
                "cores": 14,
                "threads": 20,
                "base_freq": 3500,
                "max_freq": 5300
            },
            "memory": {
                "total": 32,
                "type": "DDR4",
                "speed": 3200,
                "channels": 2
            },
            "gpu": {
                "model": "AMD RX 9070 XT",
                "memory": 16,
                "memory_type": "GDDR6"
            },
            "storage": {
                "ssd": "ZhiTai 1TB SSD Ti600",
                "hdd": "Western Digital 4TB Blue"
            }
        }
        
        # 尝试获取实际硬件信息
        try:
            # CPU信息
            cpu_info = subprocess.check_output(['lscpu'], text=True)
            if '14600KF' in cpu_info:
                hardware_info["cpu"]["detected"] = True
            
            # 内存信息
            mem_info = subprocess.check_output(['free', '-h'], text=True)
            if '32G' in mem_info:
                hardware_info["memory"]["detected"] = True
            
            # GPU信息
            try:
                gpu_info = subprocess.check_output(['lspci', '-v'], text=True)
                if 'AMD' in gpu_info and '9070' in gpu_info:
                    hardware_info["gpu"]["detected"] = True
            except:
                pass
                
        except Exception as e:
            logger.warning(f"获取硬件信息失败: {e}")
        
        return hardware_info
    
    def init_hardware_specific_monitoring(self):
        """初始化硬件特定监控"""
        # CPU监控优化
        if self.hardware_info["cpu"]["detected"]:
            logger.info("检测到Intel i5-14600KF，启用高级CPU监控")
            self.monitors['cpu'].enable_advanced_monitoring = True
        
        # GPU监控优化
        if self.hardware_info["gpu"]["detected"]:
            logger.info("检测到AMD RX 9070 XT，启用高级GPU监控")
            self.monitors['gpu'].enable_advanced_monitoring = True
        
        # 内存监控优化
        if self.hardware_info["memory"]["detected"]:
            logger.info("检测到32GB DDR4内存，启用双通道监控")
            self.monitors['memory'].enable_dual_channel_monitoring = True
    
    def start_monitoring(self, interval=None):
        """开始监控"""
        if interval is None:
            interval = self.config.get('monitoring', {}).get('interval', 2)
        
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, args=(interval,))
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        logger.info(f"Ubuntu系统监控已启动，监控间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Ubuntu系统监控已停止")
    
    def _monitoring_loop(self, interval):
        """监控循环"""
        while self.running:
            try:
                # 收集所有监控数据
                system_data = self.get_system_data()
                
                # 检查硬件特定告警
                self.check_hardware_specific_alerts()
                
                # 保存数据
                self.save_monitoring_data(system_data)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                time.sleep(interval)
    
    def get_system_data(self):
        """获取系统数据"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "name": "Ubuntu系统监控",
                "hardware": self.hardware_info,
                "os_info": get_system_info()
            },
            "cpu": self.monitors['cpu'].get_detailed_info(),
            "memory": self.monitors['memory'].get_detailed_info(),
            "gpu": self.monitors['gpu'].get_detailed_info(),
            "disk": self.monitors['disk'].get_detailed_info(),
            "network": self.monitors['network'].get_detailed_info()
        }
        return data
    
    def check_hardware_specific_alerts(self):
        """检查硬件特定告警"""
        alerts = self.config.get('alerts', {})
        
        # CPU特定告警
        cpu_data = self.monitors['cpu'].get_detailed_info()
        if cpu_data:
            # CPU温度告警 (i5-14600KF TDP 125W)
            if cpu_data.get('temperature', 0) > alerts.get('cpu_temp_threshold', 85):
                logger.warning(f"CPU温度过高: {cpu_data.get('temperature')}°C")
            
            # CPU使用率告警
            if cpu_data.get('usage_percent', 0) > alerts.get('cpu_usage_threshold', 85):
                logger.warning(f"CPU使用率过高: {cpu_data.get('usage_percent')}%")
        
        # GPU特定告警
        gpu_data = self.monitors['gpu'].get_detailed_info()
        if gpu_data:
            # GPU温度告警 (RX 9070 XT)
            if gpu_data.get('temperature', 0) > alerts.get('gpu_temp_threshold', 85):
                logger.warning(f"GPU温度过高: {gpu_data.get('temperature')}°C")
            
            # GPU内存使用率告警
            if gpu_data.get('memory_usage_percent', 0) > alerts.get('gpu_memory_threshold', 90):
                logger.warning(f"GPU内存使用率过高: {gpu_data.get('memory_usage_percent')}%")
        
        # 内存告警
        memory_data = self.monitors['memory'].get_detailed_info()
        if memory_data:
            if memory_data.get('usage_percent', 0) > alerts.get('memory_usage_threshold', 80):
                logger.warning(f"内存使用率过高: {memory_data.get('usage_percent')}%")
        
        # 磁盘告警
        disk_data = self.monitors['disk'].get_detailed_info()
        if disk_data:
            for disk in disk_data.get('disks', []):
                if disk.get('usage_percent', 0) > alerts.get('disk_usage_threshold', 85):
                    logger.warning(f"磁盘使用率过高: {disk.get('mountpoint')} - {disk.get('usage_percent')}%")
    
    def save_monitoring_data(self, data):
        """保存监控数据"""
        try:
            save_path = self.config.get('data', {}).get('save_path', './data/ubuntu_monitor')
            os.makedirs(save_path, exist_ok=True)
            
            filename = f"ubuntu_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(save_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 清理旧数据
            self.cleanup_old_data(save_path)
            
        except Exception as e:
            logger.error(f"保存监控数据失败: {e}")
    
    def cleanup_old_data(self, data_path):
        """清理旧数据"""
        try:
            retention_days = self.config.get('monitoring', {}).get('data_retention_days', 30)
            current_time = time.time()
            
            for filename in os.listdir(data_path):
                if filename.startswith('ubuntu_monitor_') and filename.endswith('.json'):
                    filepath = os.path.join(data_path, filename)
                    file_time = os.path.getmtime(filepath)
                    
                    if (current_time - file_time) > (retention_days * 24 * 3600):
                        os.remove(filepath)
                        logger.info(f"删除旧数据文件: {filename}")
                        
        except Exception as e:
            logger.error(f"清理旧数据失败: {e}")
    
    def run_cli_mode(self):
        """运行命令行模式"""
        print("🖥️  Ubuntu系统监控工具")
        print("=" * 50)
        print(f"CPU: {self.hardware_info['cpu']['model']}")
        print(f"内存: {self.hardware_info['memory']['total']}GB {self.hardware_info['memory']['type']}")
        print(f"GPU: {self.hardware_info['gpu']['model']}")
        print(f"存储: {self.hardware_info['storage']['ssd']} + {self.hardware_info['storage']['hdd']}")
        print("=" * 50)
        
        try:
            while True:
                data = self.get_system_data()
                
                # 清屏
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print("🖥️  Ubuntu系统监控工具")
                print("=" * 50)
                print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print()
                
                # CPU信息
                if data['cpu']:
                    cpu_info = data['cpu']
                    print(f"CPU使用率: {cpu_info.get('usage_percent', 0):.1f}%")
                    print(f"CPU温度: {cpu_info.get('temperature', 0):.1f}°C")
                    print(f"CPU频率: {cpu_info.get('frequency', 0):.0f}MHz")
                
                # 内存信息
                if data['memory']:
                    mem_info = data['memory']
                    print(f"内存使用率: {mem_info.get('usage_percent', 0):.1f}%")
                    print(f"已用内存: {mem_info.get('used_gb', 0):.1f}GB")
                    print(f"可用内存: {mem_info.get('available_gb', 0):.1f}GB")
                
                # GPU信息
                if data['gpu']:
                    gpu_info = data['gpu']
                    print(f"GPU使用率: {gpu_info.get('usage_percent', 0):.1f}%")
                    print(f"GPU温度: {gpu_info.get('temperature', 0):.1f}°C")
                    print(f"GPU内存: {gpu_info.get('memory_usage_percent', 0):.1f}%")
                
                # 磁盘信息
                if data['disk']:
                    disk_info = data['disk']
                    for disk in disk_info.get('disks', []):
                        print(f"磁盘 {disk.get('mountpoint', 'N/A')}: {disk.get('usage_percent', 0):.1f}%")
                
                # 网络信息
                if data['network']:
                    net_info = data['network']
                    if 'speed' in net_info:
                        speed = net_info['speed']
                        print(f"网络上传: {speed.get('upload_speed_formatted', '0 B/s')}")
                        print(f"网络下载: {speed.get('download_speed_formatted', '0 B/s')}")
                
                print("\n" + "=" * 50)
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n监控已停止")
    
    def run_web_mode(self):
        """运行Web模式"""
        from web.app import create_app
        app = create_app(self)
        
        host = self.config.get('web', {}).get('host', '0.0.0.0')
        port = self.config.get('web', {}).get('port', 5000)
        
        logger.info(f"启动Ubuntu监控Web服务器: http://{host}:{port}")
        app.run(host=host, port=port, debug=False)
    
    def run_api_mode(self):
        """运行API模式"""
        from api.secure_routes import create_secure_api_app
        app = create_secure_api_app(self)
        
        host = self.config.get('web', {}).get('host', '0.0.0.0')
        port = self.config.get('web', {}).get('port', 5000)
        
        logger.info(f"启动Ubuntu监控API服务器: http://{host}:{port}/api")
        app.run(host=host, port=port, debug=False)
    
    def get_hardware_optimization_tips(self):
        """获取硬件优化建议"""
        tips = {
            "cpu": [
                "启用Intel Turbo Boost以获得更好的性能",
                "监控CPU温度，确保散热良好",
                "考虑调整CPU频率缩放策略"
            ],
            "memory": [
                "确保内存运行在3200MHz频率",
                "检查双通道是否正常工作",
                "监控内存使用率，避免过度使用"
            ],
            "gpu": [
                "安装最新的AMD显卡驱动",
                "调整GPU风扇曲线以控制温度",
                "监控GPU内存使用情况"
            ],
            "storage": [
                "定期对SSD进行TRIM操作",
                "监控SSD健康状态",
                "避免HDD频繁读写"
            ]
        }
        return tips

def main():
    parser = argparse.ArgumentParser(description='Ubuntu系统监控工具')
    parser.add_argument('--mode', choices=['cli', 'web', 'api'], default='cli',
                       help='运行模式: cli(命令行), web(Web界面), api(API接口)')
    parser.add_argument('--interval', type=int, default=2,
                       help='监控间隔(秒)')
    parser.add_argument('--config', type=str, default='ubuntu_monitor_config.json',
                       help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建监控实例
    monitor = UbuntuSystemMonitor(args.config)
    
    try:
        if args.mode == 'cli':
            monitor.run_cli_mode()
        elif args.mode == 'web':
            monitor.run_web_mode()
        elif args.mode == 'api':
            monitor.run_api_mode()
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")

if __name__ == "__main__":
    main() 