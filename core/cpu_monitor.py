import psutil
import time
from datetime import datetime
from utils.helpers import get_temperature, bytes_to_mb
from utils.logger import logger

class CPUMonitor:
    def __init__(self):
        self.cpu_count = psutil.cpu_count()
        self.cpu_freq = psutil.cpu_freq()
        self.history = []
        self.max_history = 1000
        
    def get_cpu_info(self):
        """获取CPU基本信息"""
        try:
            cpu_info = {
                "timestamp": datetime.now().isoformat(),
                "cpu_count": self.cpu_count,
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "cpu_freq_current": self.cpu_freq.current if self.cpu_freq else None,
                "cpu_freq_min": self.cpu_freq.min if self.cpu_freq else None,
                "cpu_freq_max": self.cpu_freq.max if self.cpu_freq else None,
                "cpu_usage_percent": psutil.cpu_percent(interval=1),
                "cpu_usage_per_core": psutil.cpu_percent(interval=1, percpu=True),
                "cpu_temperature": get_temperature(),
                "cpu_load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
            
            # 添加到历史记录
            self.history.append(cpu_info)
            if len(self.history) > self.max_history:
                self.history.pop(0)
                
            return cpu_info
            
        except Exception as e:
            logger.error(f"获取CPU信息失败: {e}")
            return None
    
    def get_cpu_stats(self):
        """获取CPU统计信息"""
        try:
            cpu_stats = psutil.cpu_stats()
            return {
                "ctx_switches": cpu_stats.ctx_switches,
                "interrupts": cpu_stats.interrupts,
                "soft_interrupts": cpu_stats.soft_interrupts,
                "syscalls": cpu_stats.syscalls
            }
        except Exception as e:
            logger.error(f"获取CPU统计信息失败: {e}")
            return None
    
    def get_cpu_times(self):
        """获取CPU时间信息"""
        try:
            cpu_times = psutil.cpu_times()
            return {
                "user": cpu_times.user,
                "system": cpu_times.system,
                "idle": cpu_times.idle,
                "nice": cpu_times.nice if hasattr(cpu_times, 'nice') else 0,
                "iowait": cpu_times.iowait if hasattr(cpu_times, 'iowait') else 0,
                "irq": cpu_times.irq if hasattr(cpu_times, 'irq') else 0,
                "softirq": cpu_times.softirq if hasattr(cpu_times, 'softirq') else 0,
                "steal": cpu_times.steal if hasattr(cpu_times, 'steal') else 0
            }
        except Exception as e:
            logger.error(f"获取CPU时间信息失败: {e}")
            return None
    
    def get_detailed_info(self):
        """获取详细CPU信息"""
        cpu_info = self.get_cpu_info()
        cpu_stats = self.get_cpu_stats()
        cpu_times = self.get_cpu_times()
        
        return {
            "basic_info": cpu_info,
            "stats": cpu_stats,
            "times": cpu_times,
            "history": self.history[-50:] if self.history else []  # 最近50条记录
        }
    
    def check_alerts(self, threshold=90):
        """检查CPU告警"""
        cpu_info = self.get_cpu_info()
        if cpu_info and cpu_info.get('cpu_usage_percent', 0) > threshold:
            logger.warning(f"CPU使用率过高: {cpu_info['cpu_usage_percent']}%")
            return True
        return False 