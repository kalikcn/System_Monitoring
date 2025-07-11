from flask import Blueprint, render_template, jsonify, current_app, request
from flask_socketio import emit
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

ubuntu_monitor_bp = Blueprint('ubuntu_monitor', __name__, template_folder='templates')

# 全局监控器和硬件信息
monitors = {
    'cpu': CPUMonitor(),
    'memory': MemoryMonitor(),
    'gpu': GPUMonitor(),
    'disk': DiskMonitor(),
    'network': NetworkMonitor()
}

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

def load_config(config_file="ubuntu_monitor_config.json"):
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

config = load_config()

@ubuntu_monitor_bp.route('/')
def index():
    return render_template('ubuntu_index.html', hardware_info=hardware_info, config=config)

@ubuntu_monitor_bp.route('/api/system_info')
def get_system_info():
    return jsonify({
        "hardware": hardware_info,
        "timestamp": datetime.now().isoformat(),
        "config": config
    })

@ubuntu_monitor_bp.route('/api/cpu')
def get_cpu_info():
    try:
        cpu_data = monitors['cpu'].get_detailed_info()
        return jsonify(cpu_data)
    except Exception as e:
        logger.error(f"获取CPU信息失败: {e}")
        return jsonify({"error": str(e)}), 500

@ubuntu_monitor_bp.route('/api/memory')
def get_memory_info():
    try:
        memory_data = monitors['memory'].get_detailed_info()
        return jsonify(memory_data)
    except Exception as e:
        logger.error(f"获取内存信息失败: {e}")
        return jsonify({"error": str(e)}), 500

@ubuntu_monitor_bp.route('/api/gpu')
def get_gpu_info():
    try:
        gpu_data = monitors['gpu'].get_detailed_info()
        return jsonify(gpu_data)
    except Exception as e:
        logger.error(f"获取GPU信息失败: {e}")
        return jsonify({"error": str(e)}), 500

@ubuntu_monitor_bp.route('/api/disk')
def get_disk_info():
    try:
        disk_data = monitors['disk'].get_detailed_info()
        return jsonify(disk_data)
    except Exception as e:
        logger.error(f"获取磁盘信息失败: {e}")
        return jsonify({"error": str(e)}), 500

@ubuntu_monitor_bp.route('/api/network')
def get_network_info():
    try:
        network_data = monitors['network'].get_detailed_info()
        return jsonify(network_data)
    except Exception as e:
        logger.error(f"获取网络信息失败: {e}")
        return jsonify({"error": str(e)}), 500

@ubuntu_monitor_bp.route('/api/all')
def get_all_info():
    try:
        data = {
            "timestamp": datetime.now().isoformat(),
            "cpu": monitors['cpu'].get_detailed_info(),
            "memory": monitors['memory'].get_detailed_info(),
            "gpu": monitors['gpu'].get_detailed_info(),
            "disk": monitors['disk'].get_detailed_info(),
            "network": monitors['network'].get_detailed_info()
        }
        return jsonify(data)
    except Exception as e:
        logger.error(f"获取所有信息失败: {e}")
        return jsonify({"error": str(e)}), 500

@ubuntu_monitor_bp.route('/api/alerts')
def get_alerts():
    try:
        alerts = check_alerts()
        return jsonify(alerts)
    except Exception as e:
        logger.error(f"获取告警信息失败: {e}")
        return jsonify({"error": str(e)}), 500

@ubuntu_monitor_bp.route('/api/optimization_tips')
def get_optimization_tips():
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

def check_alerts():
    alerts = []
    alerts_config = config.get('alerts', {})
    try:
        cpu_data = monitors['cpu'].get_detailed_info()
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
        gpu_data = monitors['gpu'].get_detailed_info()
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
        memory_data = monitors['memory'].get_detailed_info()
        if memory_data:
            if memory_data.get('usage_percent', 0) > alerts_config.get('memory_usage_threshold', 80):
                alerts.append({
                    "type": "memory_usage",
                    "level": "warning",
                    "message": f"内存使用率过高: {memory_data.get('usage_percent', 0):.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
        disk_data = monitors['disk'].get_detailed_info()
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

def register_socketio_events(socketio):
    @socketio.on('connect', namespace='/ubuntu_monitor')
    def handle_connect():
        emit('connected', {'data': '已连接到 Ubuntu 监控子系统'}, namespace='/ubuntu_monitor')

    @socketio.on('request_ubuntu_data', namespace='/ubuntu_monitor')
    def handle_request_ubuntu_data():
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "cpu": monitors['cpu'].get_detailed_info(),
                "memory": monitors['memory'].get_detailed_info(),
                "gpu": monitors['gpu'].get_detailed_info(),
                "disk": monitors['disk'].get_detailed_info(),
                "network": monitors['network'].get_detailed_info(),
                "alerts": check_alerts()
            }
            emit('ubuntu_system_update', data, namespace='/ubuntu_monitor')
        except Exception as e:
            emit('error', {'error': str(e)}, namespace='/ubuntu_monitor')

# 导出 monitors、check_alerts、config 供主应用调用
__all__ = ['ubuntu_monitor_bp', 'register_socketio_events', 'monitors', 'check_alerts', 'config'] 