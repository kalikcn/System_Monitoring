#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time
import threading
import json
import os
from datetime import datetime

# 导入监控模块
from core.cpu_monitor import CPUMonitor
from core.memory_monitor import MemoryMonitor
from core.gpu_monitor import GPUMonitor
from core.disk_monitor import DiskMonitor
from core.network_monitor import NetworkMonitor
from utils.helpers import load_config, save_data, get_system_info
from utils.logger import logger

class SystemMonitor:
    def __init__(self):
        self.config = load_config()
        self.monitors = {
            'cpu': CPUMonitor(),
            'memory': MemoryMonitor(),
            'gpu': GPUMonitor(),
            'disk': DiskMonitor(),
            'network': NetworkMonitor()
        }
        self.running = False
        self.monitoring_thread = None
        
    def start_monitoring(self, interval=2):
        """开始监控"""
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, args=(interval,))
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        logger.info(f"系统监控已启动，监控间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("系统监控已停止")
    
    def _monitoring_loop(self, interval):
        """监控循环"""
        while self.running:
            try:
                # 收集所有监控数据
                system_data = self.get_system_data()
                
                # 检查告警
                self.check_alerts()
                
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
            "system_info": get_system_info(),
            "cpu": self.monitors['cpu'].get_detailed_info(),
            "memory": self.monitors['memory'].get_detailed_info(),
            "gpu": self.monitors['gpu'].get_detailed_info(),
            "disk": self.monitors['disk'].get_detailed_info(),
            "network": self.monitors['network'].get_detailed_info()
        }
        return data
    
    def check_alerts(self):
        """检查告警"""
        alerts = self.config.get('alerts', {})
        
        # CPU告警
        if self.monitors['cpu'].check_alerts(alerts.get('cpu_usage_threshold', 90)):
            logger.warning("CPU使用率告警触发")
        
        # 内存告警
        if self.monitors['memory'].check_alerts(alerts.get('memory_usage_threshold', 85)):
            logger.warning("内存使用率告警触发")
        
        # GPU告警
        if self.monitors['gpu'].check_alerts(alerts.get('gpu_usage_threshold', 95)):
            logger.warning("GPU使用率告警触发")
        
        # 磁盘告警
        if self.monitors['disk'].check_alerts(alerts.get('disk_usage_threshold', 90)):
            logger.warning("磁盘使用率告警触发")
    
    def save_monitoring_data(self, data):
        """保存监控数据"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"monitoring_data_{timestamp}.json"
            save_data(data, filename)
        except Exception as e:
            logger.error(f"保存监控数据失败: {e}")
    
    def get_current_status(self):
        """获取当前状态"""
        return self.get_system_data()
    
    def run_cli_mode(self):
        """运行命令行模式"""
        print("=== 系统监控工具 ===")
        print("按 Ctrl+C 停止监控")
        
        try:
            while True:
                data = self.get_system_data()
                
                # 清屏
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # 显示基本信息
                print(f"时间: {data['timestamp']}")
                print(f"系统: {data['system_info']['platform']} {data['system_info']['platform_version']}")
                print()
                
                # CPU信息
                if data['cpu'] and data['cpu'].get('basic_info'):
                    cpu_info = data['cpu']['basic_info']
                    print(f"CPU使用率: {cpu_info.get('cpu_usage_percent', 0):.1f}%")
                    if cpu_info.get('cpu_temperature'):
                        print(f"CPU温度: {cpu_info['cpu_temperature']:.1f}°C")
                
                # 内存信息
                if data['memory'] and data['memory'].get('basic_info'):
                    mem_info = data['memory']['basic_info']
                    print(f"内存使用率: {mem_info.get('percent', 0):.1f}%")
                    print(f"内存: {mem_info.get('used', 0):.1f}GB / {mem_info.get('total', 0):.1f}GB")
                
                # 磁盘信息
                if data['disk'] and data['disk'].get('basic_info'):
                    disk_info = data['disk']['basic_info']
                    for disk in disk_info.get('disks', []):
                        print(f"磁盘 {disk['mountpoint']}: {disk.get('percent', 0):.1f}%")
                
                # 网络信息
                if data['network'] and data['network'].get('speed'):
                    net_speed = data['network']['speed']
                    print(f"网络上传: {net_speed.get('upload_speed_formatted', '0 B/s')}")
                    print(f"网络下载: {net_speed.get('download_speed_formatted', '0 B/s')}")
                
                print("\n" + "="*50)
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n监控已停止")
    
    def run_web_mode(self):
        """运行Web模式"""
        from web.app import create_app
        app = create_app(self)
        
        host = self.config.get('web', {}).get('host', '0.0.0.0')
        port = self.config.get('web', {}).get('port', 5000)
        
        logger.info(f"启动Web服务器: http://{host}:{port}")
        app.run(host=host, port=port, debug=False)
    
    def run_api_mode(self):
        """运行API模式"""
        from api.routes import create_api_app
        app = create_api_app(self)
        
        host = self.config.get('web', {}).get('host', '0.0.0.0')
        port = self.config.get('web', {}).get('port', 5000)
        
        logger.info(f"启动API服务器: http://{host}:{port}/api")
        app.run(host=host, port=port, debug=False)

def main():
    parser = argparse.ArgumentParser(description='系统监控工具')
    parser.add_argument('--mode', choices=['cli', 'web', 'api'], default='cli',
                       help='运行模式: cli(命令行), web(Web界面), api(API接口)')
    parser.add_argument('--interval', type=int, default=2,
                       help='监控间隔(秒)')
    
    args = parser.parse_args()
    
    # 创建监控实例
    monitor = SystemMonitor()
    
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