import psutil
import time
from datetime import datetime
from utils.helpers import bytes_to_gb, format_speed
from utils.logger import logger

class DiskMonitor:
    def __init__(self):
        self.history = []
        self.max_history = 1000
        self.last_io = None
        
    def get_disk_info(self):
        """获取磁盘基本信息"""
        try:
            disks = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "total": bytes_to_gb(usage.total),
                        "used": bytes_to_gb(usage.used),
                        "free": bytes_to_gb(usage.free),
                        "percent": usage.percent
                    }
                    disks.append(disk_info)
                except (PermissionError, FileNotFoundError):
                    continue
            
            return {
                "timestamp": datetime.now().isoformat(),
                "disks": disks
            }
            
        except Exception as e:
            logger.error(f"获取磁盘信息失败: {e}")
            return None
    
    def get_disk_io(self):
        """获取磁盘IO信息"""
        try:
            current_io = psutil.disk_io_counters()
            
            if current_io is None:
                return {
                    "read_bytes_per_sec": 0,
                    "write_bytes_per_sec": 0,
                    "read_count_per_sec": 0,
                    "write_count_per_sec": 0,
                    "read_speed": "0 B/s",
                    "write_speed": "0 B/s"
                }
            
            if self.last_io is None:
                self.last_io = current_io
                return {
                    "read_bytes_per_sec": 0,
                    "write_bytes_per_sec": 0,
                    "read_count_per_sec": 0,
                    "write_count_per_sec": 0,
                    "read_speed": "0 B/s",
                    "write_speed": "0 B/s"
                }
            
            # 计算每秒IO
            time_diff = 1  # 假设1秒间隔
            read_bytes_per_sec = (current_io.read_bytes - self.last_io.read_bytes) / time_diff
            write_bytes_per_sec = (current_io.write_bytes - self.last_io.write_bytes) / time_diff
            read_count_per_sec = (current_io.read_count - self.last_io.read_count) / time_diff
            write_count_per_sec = (current_io.write_count - self.last_io.write_count) / time_diff
            
            self.last_io = current_io
            
            return {
                "read_bytes_per_sec": read_bytes_per_sec,
                "write_bytes_per_sec": write_bytes_per_sec,
                "read_count_per_sec": read_count_per_sec,
                "write_count_per_sec": write_count_per_sec,
                "read_speed": format_speed(read_bytes_per_sec),
                "write_speed": format_speed(write_bytes_per_sec)
            }
            
        except Exception as e:
            logger.error(f"获取磁盘IO信息失败: {e}")
            return None
    
    def get_disk_temperature(self):
        """获取磁盘温度（需要特定工具支持）"""
        try:
            # 这里可以集成smartctl等工具来获取磁盘温度
            # 目前返回None，需要根据具体平台实现
            return None
        except Exception as e:
            logger.error(f"获取磁盘温度失败: {e}")
            return None
    
    def get_disk_health(self):
        """获取磁盘健康状态"""
        try:
            # 这里可以集成smartctl等工具来获取磁盘健康状态
            # 目前返回基本状态
            return {
                "status": "unknown",
                "smart_status": "unknown"
            }
        except Exception as e:
            logger.error(f"获取磁盘健康状态失败: {e}")
            return None
    
    def get_detailed_info(self):
        """获取详细磁盘信息"""
        disk_info = self.get_disk_info()
        disk_io = self.get_disk_io()
        disk_temp = self.get_disk_temperature()
        disk_health = self.get_disk_health()
        
        detailed_info = {
            "basic_info": disk_info,
            "io_info": disk_io,
            "temperature": disk_temp,
            "health": disk_health
        }
        
        # 添加到历史记录
        self.history.append(detailed_info)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        return {
            **detailed_info,
            "history": self.history[-50:] if self.history else []  # 最近50条记录
        }
    
    def check_alerts(self, threshold=90):
        """检查磁盘告警"""
        disk_info = self.get_disk_info()
        if disk_info:
            for disk in disk_info.get('disks', []):
                if disk.get('percent', 0) > threshold:
                    logger.warning(f"磁盘使用率过高: {disk['mountpoint']} - {disk['percent']}%")
                    return True
        return False
    
    def get_largest_files(self, path="/", limit=10):
        """获取指定路径下最大的文件"""
        try:
            import os
            files = []
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    try:
                        filepath = os.path.join(root, filename)
                        size = os.path.getsize(filepath)
                        files.append({
                            "path": filepath,
                            "size": bytes_to_gb(size),
                            "size_bytes": size
                        })
                    except (OSError, PermissionError):
                        continue
            
            # 按文件大小排序
            files.sort(key=lambda x: x['size_bytes'], reverse=True)
            return files[:limit]
            
        except Exception as e:
            logger.error(f"获取大文件列表失败: {e}")
            return [] 