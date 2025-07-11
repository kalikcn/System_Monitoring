import platform
import psutil
import json
import os
from datetime import datetime

def get_system_info():
    """获取系统基本信息"""
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "hostname": platform.node(),
        "python_version": platform.python_version()
    }

def bytes_to_mb(bytes_value):
    """将字节转换为MB"""
    return round(bytes_value / (1024 * 1024), 2)

def bytes_to_gb(bytes_value):
    """将字节转换为GB"""
    return round(bytes_value / (1024 * 1024 * 1024), 2)

def format_speed(bytes_per_sec):
    """格式化速度显示"""
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.1f} B/s"
    elif bytes_per_sec < 1024 * 1024:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    elif bytes_per_sec < 1024 * 1024 * 1024:
        return f"{bytes_per_sec / (1024 * 1024):.1f} MB/s"
    else:
        return f"{bytes_per_sec / (1024 * 1024 * 1024):.1f} GB/s"

def get_temperature():
    """获取CPU温度（跨平台）"""
    try:
        if platform.system() == "Windows":
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            temperature_infos = w.Sensor()
            for sensor in temperature_infos:
                if sensor.SensorType == 'Temperature':
                    return sensor.Value
        elif platform.system() == "Linux":
            # 尝试读取/sys/class/thermal/thermal_zone*/temp
            import glob
            thermal_zones = glob.glob("/sys/class/thermal/thermal_zone*/temp")
            if thermal_zones:
                with open(thermal_zones[0], 'r') as f:
                    temp = int(f.read()) / 1000.0
                    return temp
    except Exception as e:
        pass
    return None

def load_config():
    """加载配置文件"""
    config_path = "config/settings.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data, filename):
    """保存数据到文件"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    filepath = os.path.join(data_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_disk_io():
    """获取磁盘IO信息"""
    try:
        disk_io = psutil.disk_io_counters()
        return {
            "read_bytes": disk_io.read_bytes,
            "write_bytes": disk_io.write_bytes,
            "read_count": disk_io.read_count,
            "write_count": disk_io.write_count
        }
    except:
        return None

def get_network_io():
    """获取网络IO信息"""
    try:
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
    except:
        return None

def is_windows():
    """检查是否为Windows系统"""
    return platform.system() == "Windows"

def is_linux():
    """检查是否为Linux系统"""
    return platform.system() == "Linux" 