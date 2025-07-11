import psutil
import time
from datetime import datetime
from utils.helpers import bytes_to_gb
from utils.logger import logger

class MemoryMonitor:
    def __init__(self):
        self.history = []
        self.max_history = 1000
        
    def get_memory_info(self):
        """获取内存基本信息"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_info = {
                "timestamp": datetime.now().isoformat(),
                "total": bytes_to_gb(memory.total),
                "available": bytes_to_gb(memory.available),
                "used": bytes_to_gb(memory.used),
                "free": bytes_to_gb(memory.free),
                "percent": memory.percent,
                "swap_total": bytes_to_gb(swap.total),
                "swap_used": bytes_to_gb(swap.used),
                "swap_free": bytes_to_gb(swap.free),
                "swap_percent": swap.percent
            }
            
            # 添加到历史记录
            self.history.append(memory_info)
            if len(self.history) > self.max_history:
                self.history.pop(0)
                
            return memory_info
            
        except Exception as e:
            logger.error(f"获取内存信息失败: {e}")
            return None
    
    def get_memory_details(self):
        """获取内存详细信息"""
        try:
            memory = psutil.virtual_memory()
            details = {}
            
            # 安全地获取内存详细信息，不同平台属性可能不同
            if hasattr(memory, 'active'):
                details["active"] = bytes_to_gb(memory.active)
            if hasattr(memory, 'inactive'):
                details["inactive"] = bytes_to_gb(memory.inactive)
            if hasattr(memory, 'buffers'):
                details["buffers"] = bytes_to_gb(memory.buffers)
            if hasattr(memory, 'cached'):
                details["cached"] = bytes_to_gb(memory.cached)
            if hasattr(memory, 'shared'):
                details["shared"] = bytes_to_gb(memory.shared)
            if hasattr(memory, 'slab'):
                details["slab"] = bytes_to_gb(memory.slab)
            
            return details
        except Exception as e:
            logger.error(f"获取内存详细信息失败: {e}")
            return None
    
    def get_memory_processes(self, limit=10):
        """获取占用内存最多的进程"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    proc_info = proc.info
                    memory_mb = proc_info['memory_info'].rss / (1024 * 1024)
                    processes.append({
                        "pid": proc_info['pid'],
                        "name": proc_info['name'],
                        "memory_mb": round(memory_mb, 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 按内存使用量排序
            processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            return processes[:limit]
            
        except Exception as e:
            logger.error(f"获取进程内存信息失败: {e}")
            return []
    
    def get_detailed_info(self):
        """获取详细内存信息"""
        memory_info = self.get_memory_info()
        memory_details = self.get_memory_details()
        top_processes = self.get_memory_processes()
        
        return {
            "basic_info": memory_info,
            "details": memory_details,
            "top_processes": top_processes,
            "history": self.history[-50:] if self.history else []  # 最近50条记录
        }
    
    def check_alerts(self, threshold=85):
        """检查内存告警"""
        memory_info = self.get_memory_info()
        if memory_info and memory_info.get('percent', 0) > threshold:
            logger.warning(f"内存使用率过高: {memory_info['percent']}%")
            return True
        return False 