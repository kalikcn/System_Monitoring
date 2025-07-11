import psutil
import time
import platform
from datetime import datetime
from utils.logger import logger

class GPUMonitor:
    def __init__(self):
        self.history = []
        self.max_history = 1000
        self.gpus = []
        self._init_gpus()
        
    def _init_gpus(self):
        """初始化GPU检测"""
        try:
            # 尝试使用GPUtil库
            import GPUtil
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                self.gpus.append({
                    "id": gpu.id,
                    "name": gpu.name,
                    "load": gpu.load,
                    "memory_total": gpu.memoryTotal,
                    "memory_used": gpu.memoryUsed,
                    "memory_free": gpu.memoryFree,
                    "temperature": gpu.temperature
                })
            logger.info(f"检测到 {len(self.gpus)} 个GPU")
        except ImportError:
            logger.warning("GPUtil库未安装，尝试其他方法检测GPU")
            self._init_gpus_alternative()
        except Exception as e:
            logger.error(f"GPUtil初始化GPU失败: {e}")
            self._init_gpus_alternative()
    
    def _init_gpus_alternative(self):
        """备用GPU检测方法"""
        try:
            # 尝试使用nvidia-ml-py (仅NVIDIA)
            try:
                import pynvml
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle)
                    self.gpus.append({
                        "id": i,
                        "name": name.decode('utf-8'),
                        "load": 0,  # 需要单独获取
                        "memory_total": 0,  # 需要单独获取
                        "memory_used": 0,
                        "memory_free": 0,
                        "temperature": 0
                    })
                logger.info(f"通过NVIDIA-ML检测到 {len(self.gpus)} 个NVIDIA GPU")
            except ImportError:
                logger.warning("pynvml库未安装，无法检测NVIDIA GPU")
            except Exception as e:
                logger.warning(f"NVIDIA GPU检测失败: {e}")
            
            # 尝试检测AMD GPU (Windows)
            if platform.system() == "Windows":
                self._detect_amd_gpu_windows()
            
            # 尝试检测AMD GPU (Linux)
            elif platform.system() == "Linux":
                self._detect_amd_gpu_linux()
                
        except Exception as e:
            logger.error(f"备用GPU检测失败: {e}")
    
    def _detect_amd_gpu_windows(self):
        """Windows下检测AMD GPU"""
        try:
            import wmi
            w = wmi.WMI()
            for gpu in w.Win32_VideoController():
                if "AMD" in gpu.Name or "Radeon" in gpu.Name:
                    self.gpus.append({
                        "id": len(self.gpus),
                        "name": gpu.Name,
                        "load": 0,  # WMI无法直接获取GPU使用率
                        "memory_total": gpu.AdapterRAM // (1024*1024) if gpu.AdapterRAM else 0,
                        "memory_used": 0,
                        "memory_free": 0,
                        "temperature": 0
                    })
            logger.info(f"Windows下检测到 {len([g for g in self.gpus if 'AMD' in g['name'] or 'Radeon' in g['name']])} 个AMD GPU")
        except Exception as e:
            logger.warning(f"Windows AMD GPU检测失败: {e}")
    
    def _detect_amd_gpu_linux(self):
        """Linux下检测AMD GPU"""
        try:
            import subprocess
            # 检查是否有AMD GPU
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'VGA' in line and ('AMD' in line or 'Radeon' in line):
                        # 提取GPU名称
                        gpu_name = line.split(':')[-1].strip()
                        self.gpus.append({
                            "id": len(self.gpus),
                            "name": gpu_name,
                            "load": 0,
                            "memory_total": 0,
                            "memory_used": 0,
                            "memory_free": 0,
                            "temperature": 0
                        })
            logger.info(f"Linux下检测到 {len([g for g in self.gpus if 'AMD' in g['name'] or 'Radeon' in g['name']])} 个AMD GPU")
        except Exception as e:
            logger.warning(f"Linux AMD GPU检测失败: {e}")
    
    def get_gpu_info(self):
        """获取GPU基本信息"""
        try:
            gpu_info = {
                "timestamp": datetime.now().isoformat(),
                "gpu_count": len(self.gpus),
                "gpus": []
            }
            
            for gpu in self.gpus:
                gpu_data = {
                    "id": gpu["id"],
                    "name": gpu["name"],
                    "load_percent": gpu["load"] * 100 if gpu["load"] else 0,
                    "memory_total_mb": gpu["memory_total"],
                    "memory_used_mb": gpu["memory_used"],
                    "memory_free_mb": gpu["memory_free"],
                    "memory_percent": (gpu["memory_used"] / gpu["memory_total"] * 100) if gpu["memory_total"] > 0 else 0,
                    "temperature": gpu["temperature"]
                }
                gpu_info["gpus"].append(gpu_data)
            
            # 添加到历史记录
            self.history.append(gpu_info)
            if len(self.history) > self.max_history:
                self.history.pop(0)
                
            return gpu_info
            
        except Exception as e:
            logger.error(f"获取GPU信息失败: {e}")
            return None
    
    def get_gpu_detailed_info(self):
        """获取GPU详细信息"""
        try:
            detailed_info = {
                "basic_info": self.get_gpu_info(),
                "driver_info": self._get_driver_info(),
                "processes": self._get_gpu_processes()
            }
            
            return detailed_info
            
        except Exception as e:
            logger.error(f"获取GPU详细信息失败: {e}")
            return None
    
    def _get_driver_info(self):
        """获取GPU驱动信息"""
        try:
            # 这里可以添加获取驱动信息的代码
            # 不同平台需要不同的实现
            return {
                "driver_version": "unknown",
                "cuda_version": "unknown",
                "opencl_version": "unknown"
            }
        except Exception as e:
            logger.error(f"获取驱动信息失败: {e}")
            return None
    
    def _get_gpu_processes(self):
        """获取GPU进程信息"""
        try:
            # 这里可以添加获取GPU进程的代码
            # 需要特定工具支持
            return []
        except Exception as e:
            logger.error(f"获取GPU进程信息失败: {e}")
            return []
    
    def get_gpu_temperature(self):
        """获取GPU温度"""
        try:
            temperatures = []
            for gpu in self.gpus:
                if gpu["temperature"]:
                    temperatures.append({
                        "gpu_id": gpu["id"],
                        "temperature": gpu["temperature"]
                    })
            return temperatures
        except Exception as e:
            logger.error(f"获取GPU温度失败: {e}")
            return []
    
    def get_gpu_memory_usage(self):
        """获取GPU内存使用情况"""
        try:
            memory_info = []
            for gpu in self.gpus:
                memory_info.append({
                    "gpu_id": gpu["id"],
                    "total_mb": gpu["memory_total"],
                    "used_mb": gpu["memory_used"],
                    "free_mb": gpu["memory_free"],
                    "usage_percent": (gpu["memory_used"] / gpu["memory_total"] * 100) if gpu["memory_total"] > 0 else 0
                })
            return memory_info
        except Exception as e:
            logger.error(f"获取GPU内存使用情况失败: {e}")
            return []
    
    def check_alerts(self, threshold=95):
        """检查GPU告警"""
        gpu_info = self.get_gpu_info()
        if gpu_info:
            for gpu in gpu_info.get('gpus', []):
                if gpu.get('load_percent', 0) > threshold:
                    logger.warning(f"GPU使用率过高: {gpu['name']} - {gpu['load_percent']}%")
                    return True
                if gpu.get('temperature', 0) > 85:
                    logger.warning(f"GPU温度过高: {gpu['name']} - {gpu['temperature']}°C")
                    return True
        return False
    
    def get_detailed_info(self):
        """获取详细GPU信息"""
        gpu_info = self.get_gpu_info()
        gpu_temp = self.get_gpu_temperature()
        gpu_memory = self.get_gpu_memory_usage()
        
        return {
            "basic_info": gpu_info,
            "temperature": gpu_temp,
            "memory_usage": gpu_memory,
            "history": self.history[-50:] if self.history else []  # 最近50条记录
        } 