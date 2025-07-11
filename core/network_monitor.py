import psutil
import time
import subprocess
import platform
from datetime import datetime
from utils.helpers import format_speed
from utils.logger import logger

class NetworkMonitor:
    def __init__(self):
        self.history = []
        self.max_history = 1000
        self.last_net_io = None
        
    def get_network_info(self):
        """获取网络基本信息"""
        try:
            net_io = psutil.net_io_counters()
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            interfaces = []
            for interface, addrs in net_if_addrs.items():
                if interface in net_if_stats:
                    stats = net_if_stats[interface]
                    interface_info = {
                        "name": interface,
                        "is_up": stats.isup,
                        "speed": stats.speed,
                        "mtu": stats.mtu,
                        "addresses": []
                    }
                    
                    for addr in addrs:
                        interface_info["addresses"].append({
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast
                        })
                    
                    interfaces.append(interface_info)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "interfaces": interfaces,
                "total_bytes_sent": net_io.bytes_sent,
                "total_bytes_recv": net_io.bytes_recv,
                "total_packets_sent": net_io.packets_sent,
                "total_packets_recv": net_io.packets_recv
            }
            
        except Exception as e:
            logger.error(f"获取网络信息失败: {e}")
            return None
    
    def get_network_speed(self):
        """获取网络速度"""
        try:
            current_net_io = psutil.net_io_counters()
            
            if current_net_io is None:
                return {
                    "upload_speed": 0,
                    "download_speed": 0,
                    "upload_speed_formatted": "0 B/s",
                    "download_speed_formatted": "0 B/s"
                }
            
            if self.last_net_io is None:
                self.last_net_io = current_net_io
                return {
                    "upload_speed": 0,
                    "download_speed": 0,
                    "upload_speed_formatted": "0 B/s",
                    "download_speed_formatted": "0 B/s"
                }
            
            # 计算每秒速度
            time_diff = 1  # 假设1秒间隔
            upload_speed = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
            download_speed = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff
            
            self.last_net_io = current_net_io
            
            return {
                "upload_speed": upload_speed,
                "download_speed": download_speed,
                "upload_speed_formatted": format_speed(upload_speed),
                "download_speed_formatted": format_speed(download_speed)
            }
            
        except Exception as e:
            logger.error(f"获取网络速度失败: {e}")
            return None
    
    def ping_host(self, host="8.8.8.8"):
        """Ping指定主机"""
        try:
            if platform.system() == "Windows":
                cmd = ["ping", "-n", "1", host]
            else:
                cmd = ["ping", "-c", "1", host]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # 解析ping结果
                output = result.stdout
                if platform.system() == "Windows":
                    # Windows ping输出解析
                    if "时间=" in output:
                        time_str = output.split("时间=")[1].split("ms")[0]
                        return float(time_str)
                else:
                    # Linux ping输出解析
                    if "time=" in output:
                        time_str = output.split("time=")[1].split(" ms")[0]
                        return float(time_str)
            
            return None
            
        except Exception as e:
            logger.error(f"Ping {host} 失败: {e}")
            return None
    
    def get_network_connections(self):
        """获取网络连接信息"""
        try:
            connections = []
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED':
                    try:
                        local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                        remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                        
                        connections.append({
                            "local_address": local_addr,
                            "remote_address": remote_addr,
                            "status": conn.status,
                            "pid": conn.pid
                        })
                    except (AttributeError, TypeError):
                        # 跳过无效的连接
                        continue
            
            return connections[:20]  # 只返回前20个连接
            
        except Exception as e:
            logger.error(f"获取网络连接信息失败: {e}")
            return []
    
    def speed_test(self):
        """执行网速测试"""
        try:
            # 检查speedtest模块是否可用
            import importlib.util
            spec = importlib.util.find_spec("speedtest")
            if spec is None:
                logger.warning("speedtest-cli库未安装，使用ping测试")
                return self._fallback_speed_test()
            
            # 动态导入speedtest
            speedtest_module = importlib.import_module("speedtest")
            st = speedtest_module.Speedtest()
            
            # 设置超时时间
            st.timeout = 10
            
            # 获取服务器列表
            logger.info("正在获取服务器列表...")
            st.get_servers()
            
            # 选择最佳服务器
            logger.info("正在选择最佳服务器...")
            st.get_best_server()
            
            # 测试下载速度
            logger.info("正在测试下载速度...")
            download_speed = st.download() / 1_000_000  # 转换为Mbps
            
            # 测试上传速度
            logger.info("正在测试上传速度...")
            upload_speed = st.upload() / 1_000_000  # 转换为Mbps
            
            # 获取延迟
            ping = st.results.ping
            
            return {
                "download_speed_mbps": round(download_speed, 2),
                "upload_speed_mbps": round(upload_speed, 2),
                "ping_ms": round(ping, 2),
                "server": st.results.server["name"] if st.results.server else "Unknown"
            }
            
        except ImportError:
            logger.warning("speedtest-cli库未安装，使用ping测试")
            return self._fallback_speed_test()
        except Exception as e:
            logger.error(f"网速测试失败: {e}")
            # 如果speedtest失败，尝试使用ping测试
            return self._fallback_speed_test()
    
    def _fallback_speed_test(self):
        """备用网速测试方法"""
        try:
            # 测试多个服务器的ping延迟
            test_hosts = ["8.8.8.8", "114.114.114.114", "1.1.1.1"]
            ping_results = []
            
            for host in test_hosts:
                ping_time = self.ping_host(host)
                if ping_time:
                    ping_results.append(ping_time)
            
            if ping_results:
                avg_ping = sum(ping_results) / len(ping_results)
                return {
                    "download_speed_mbps": 0,  # 无法测试
                    "upload_speed_mbps": 0,     # 无法测试
                    "ping_ms": round(avg_ping, 2),
                    "server": "Ping测试",
                    "note": "仅测试网络延迟，速度测试失败"
                }
            else:
                return {"error": "网络连接测试失败"}
                
        except Exception as e:
            logger.error(f"备用网速测试失败: {e}")
            return {"error": "网络测试完全失败"}
    
    def simple_network_test(self):
        """简单的网络测试"""
        try:
            # 测试网络连接
            test_hosts = ["8.8.8.8", "114.114.114.114", "1.1.1.1"]
            ping_results = []
            
            for host in test_hosts:
                ping_time = self.ping_host(host)
                if ping_time:
                    ping_results.append(ping_time)
            
            if ping_results:
                avg_ping = sum(ping_results) / len(ping_results)
                return {
                    "ping_ms": round(avg_ping, 2),
                    "status": "connected",
                    "note": "网络连接正常"
                }
            else:
                return {
                    "ping_ms": 0,
                    "status": "disconnected", 
                    "note": "网络连接异常"
                }
                
        except Exception as e:
            logger.error(f"简单网络测试失败: {e}")
            return {
                "ping_ms": 0,
                "status": "error",
                "note": f"测试失败: {str(e)}"
            }
    
    def get_detailed_info(self):
        """获取详细网络信息"""
        network_info = self.get_network_info()
        network_speed = self.get_network_speed()
        connections = self.get_network_connections()
        
        detailed_info = {
            "basic_info": network_info,
            "speed": network_speed,
            "connections": connections
        }
        
        # 添加到历史记录
        self.history.append(detailed_info)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        return {
            **detailed_info,
            "history": self.history[-50:] if self.history else []  # 最近50条记录
        }
    
    def check_network_health(self):
        """检查网络健康状态"""
        try:
            # 检查基本连接
            ping_result = self.ping_host("8.8.8.8")
            if ping_result is None:
                logger.warning("网络连接异常")
                return False
            
            # 检查网络速度
            speed_info = self.get_network_speed()
            if speed_info:
                upload_speed = speed_info.get('upload_speed', 0)
                download_speed = speed_info.get('download_speed', 0)
                
                # 如果速度过低，可能是网络问题
                if upload_speed < 1000 and download_speed < 1000:  # 小于1KB/s
                    logger.warning("网络速度异常低")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"检查网络健康状态失败: {e}")
            return False 