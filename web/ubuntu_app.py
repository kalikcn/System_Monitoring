#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ubuntu系统监控Web应用
专门针对Intel i5-14600KF + RX 9070 XT配置
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import os
import time
from datetime import datetime
import threading

# 导入监控模块
from core.cpu_monitor import CPUMonitor
from core.memory_monitor import MemoryMonitor
from core.gpu_monitor import GPUMonitor
from core.disk_monitor import DiskMonitor
from core.network_monitor import NetworkMonitor
from utils.logger import logger

class UbuntuWebApp:
    def __init__(self, config_file="ubuntu_monitor_config.json"):
        """初始化Ubuntu Web应用"""
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'ubuntu_monitor_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # 加载配置
        self.config = self.load_config(config_file)
        
        # 初始化监控器
        self.monitors = {
            'cpu': CPUMonitor(),
            'memory': MemoryMonitor(),
            'gpu': GPUMonitor(),
            'disk': DiskMonitor(),
            'network': NetworkMonitor()
        }
        
        # 硬件信息
        self.hardware_info = {
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
        
        # 设置路由
        self.setup_routes()
        
        # 启动实时数据更新
        self.start_realtime_updates()
    
    def load_config(self, config_file):
        """加载配置"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "web": {"host": "0.0.0.0", "port": 5000},
                    "monitoring": {"interval": 2}
                }
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return {}
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.route('/')
        def index():
            """主页"""
            return render_template('ubuntu_index.html', 
                                hardware_info=self.hardware_info,
                                config=self.config)
        
        @self.app.route('/api/system_info')
        def get_system_info():
            """获取系统信息"""
            return jsonify({
                "hardware": self.hardware_info,
                "timestamp": datetime.now().isoformat(),
                "config": self.config
            })
        
        @self.app.route('/api/cpu')
        def get_cpu_info():
            """获取CPU信息"""
            try:
                cpu_data = self.monitors['cpu'].get_detailed_info()
                return jsonify(cpu_data)
            except Exception as e:
                logger.error(f"获取CPU信息失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/memory')
        def get_memory_info():
            """获取内存信息"""
            try:
                memory_data = self.monitors['memory'].get_detailed_info()
                return jsonify(memory_data)
            except Exception as e:
                logger.error(f"获取内存信息失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/gpu')
        def get_gpu_info():
            """获取GPU信息"""
            try:
                gpu_data = self.monitors['gpu'].get_detailed_info()
                return jsonify(gpu_data)
            except Exception as e:
                logger.error(f"获取GPU信息失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/disk')
        def get_disk_info():
            """获取磁盘信息"""
            try:
                disk_data = self.monitors['disk'].get_detailed_info()
                return jsonify(disk_data)
            except Exception as e:
                logger.error(f"获取磁盘信息失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/network')
        def get_network_info():
            """获取网络信息"""
            try:
                network_data = self.monitors['network'].get_detailed_info()
                return jsonify(network_data)
            except Exception as e:
                logger.error(f"获取网络信息失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/all')
        def get_all_info():
            """获取所有监控信息"""
            try:
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu": self.monitors['cpu'].get_detailed_info(),
                    "memory": self.monitors['memory'].get_detailed_info(),
                    "gpu": self.monitors['gpu'].get_detailed_info(),
                    "disk": self.monitors['disk'].get_detailed_info(),
                    "network": self.monitors['network'].get_detailed_info()
                }
                return jsonify(data)
            except Exception as e:
                logger.error(f"获取所有信息失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/alerts')
        def get_alerts():
            """获取告警信息"""
            try:
                alerts = self.check_alerts()
                return jsonify(alerts)
            except Exception as e:
                logger.error(f"获取告警信息失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/optimization_tips')
        def get_optimization_tips():
            """获取优化建议"""
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
            return jsonify(tips)
    
    def check_alerts(self):
        """检查告警"""
        alerts = []
        alerts_config = self.config.get('alerts', {})
        
        try:
            # CPU告警
            cpu_data = self.monitors['cpu'].get_detailed_info()
            if cpu_data:
                if cpu_data.get('temperature', 0) > alerts_config.get('cpu_temp_threshold', 85):
                    alerts.append({
                        "type": "cpu_temperature",
                        "level": "warning",
                        "message": f"CPU温度过高: {cpu_data.get('temperature', 0):.1f}°C",
                        "timestamp": datetime.now().isoformat()
                    })
                
                if cpu_data.get('usage_percent', 0) > alerts_config.get('cpu_usage_threshold', 85):
                    alerts.append({
                        "type": "cpu_usage",
                        "level": "warning",
                        "message": f"CPU使用率过高: {cpu_data.get('usage_percent', 0):.1f}%",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # GPU告警
            gpu_data = self.monitors['gpu'].get_detailed_info()
            if gpu_data:
                if gpu_data.get('temperature', 0) > alerts_config.get('gpu_temp_threshold', 85):
                    alerts.append({
                        "type": "gpu_temperature",
                        "level": "warning",
                        "message": f"GPU温度过高: {gpu_data.get('temperature', 0):.1f}°C",
                        "timestamp": datetime.now().isoformat()
                    })
                
                if gpu_data.get('memory_usage_percent', 0) > alerts_config.get('gpu_memory_threshold', 90):
                    alerts.append({
                        "type": "gpu_memory",
                        "level": "warning",
                        "message": f"GPU内存使用率过高: {gpu_data.get('memory_usage_percent', 0):.1f}%",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # 内存告警
            memory_data = self.monitors['memory'].get_detailed_info()
            if memory_data:
                if memory_data.get('usage_percent', 0) > alerts_config.get('memory_usage_threshold', 80):
                    alerts.append({
                        "type": "memory_usage",
                        "level": "warning",
                        "message": f"内存使用率过高: {memory_data.get('usage_percent', 0):.1f}%",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # 磁盘告警
            disk_data = self.monitors['disk'].get_detailed_info()
            if disk_data:
                for disk in disk_data.get('disks', []):
                    if disk.get('usage_percent', 0) > alerts_config.get('disk_usage_threshold', 85):
                        alerts.append({
                            "type": "disk_usage",
                            "level": "warning",
                            "message": f"磁盘使用率过高: {disk.get('mountpoint')} - {disk.get('usage_percent', 0):.1f}%",
                            "timestamp": datetime.now().isoformat()
                        })
        
        except Exception as e:
            logger.error(f"检查告警失败: {e}")
        
        return alerts
    
    def start_realtime_updates(self):
        """启动实时数据更新"""
        def update_data():
            while True:
                try:
                    data = {
                        "timestamp": datetime.now().isoformat(),
                        "cpu": self.monitors['cpu'].get_detailed_info(),
                        "memory": self.monitors['memory'].get_detailed_info(),
                        "gpu": self.monitors['gpu'].get_detailed_info(),
                        "disk": self.monitors['disk'].get_detailed_info(),
                        "network": self.monitors['network'].get_detailed_info(),
                        "alerts": self.check_alerts()
                    }
                    
                    self.socketio.emit('system_update', data)
                    
                    # 保存数据
                    self.save_monitoring_data(data)
                    
                    time.sleep(self.config.get('monitoring', {}).get('interval', 2))
                    
                except Exception as e:
                    logger.error(f"实时数据更新失败: {e}")
                    time.sleep(5)
        
        # 启动后台线程
        update_thread = threading.Thread(target=update_data, daemon=True)
        update_thread.start()
    
    def save_monitoring_data(self, data):
        """保存监控数据"""
        try:
            save_path = self.config.get('data', {}).get('save_path', './data/ubuntu_monitor')
            os.makedirs(save_path, exist_ok=True)
            
            filename = f"ubuntu_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(save_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"保存监控数据失败: {e}")
    
    def run(self, host=None, port=None, debug=False):
        """运行Web应用"""
        if host is None:
            host = self.config.get('web', {}).get('host', '0.0.0.0')
        if port is None:
            port = self.config.get('web', {}).get('port', 5000)
        
        logger.info(f"启动Ubuntu监控Web服务器: http://{host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)

def create_ubuntu_app(config_file="ubuntu_monitor_config.json"):
    """创建Ubuntu Web应用实例"""
    return UbuntuWebApp(config_file)

if __name__ == "__main__":
    app = create_ubuntu_app()
    app.run() 