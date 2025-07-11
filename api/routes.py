from flask import Flask, jsonify, request
from flask_cors import CORS
import json

def create_api_app(monitor):
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/api/status')
    def get_status():
        """获取系统状态"""
        try:
            data = monitor.get_current_status()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/cpu')
    def get_cpu():
        """获取CPU信息"""
        try:
            data = monitor.monitors['cpu'].get_detailed_info()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/memory')
    def get_memory():
        """获取内存信息"""
        try:
            data = monitor.monitors['memory'].get_detailed_info()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/gpu')
    def get_gpu():
        """获取GPU信息"""
        try:
            data = monitor.monitors['gpu'].get_detailed_info()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/disk')
    def get_disk():
        """获取磁盘信息"""
        try:
            data = monitor.monitors['disk'].get_detailed_info()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/network')
    def get_network():
        """获取网络信息"""
        try:
            data = monitor.monitors['network'].get_detailed_info()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/speedtest')
    def run_speedtest():
        """执行网速测试"""
        try:
            result = monitor.monitors['network'].speed_test()
            return jsonify(result if result else {"error": "网速测试失败"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/network_test')
    def run_network_test():
        """执行简单网络测试"""
        try:
            result = monitor.monitors['network'].simple_network_test()
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/alerts')
    def get_alerts():
        """获取告警信息"""
        try:
            alerts = []
            
            # 检查CPU告警
            if monitor.monitors['cpu'].check_alerts():
                alerts.append({
                    "type": "cpu",
                    "message": "CPU使用率过高",
                    "level": "warning"
                })
            
            # 检查内存告警
            if monitor.monitors['memory'].check_alerts():
                alerts.append({
                    "type": "memory",
                    "message": "内存使用率过高",
                    "level": "warning"
                })
            
            # 检查GPU告警
            if monitor.monitors['gpu'].check_alerts():
                alerts.append({
                    "type": "gpu",
                    "message": "GPU使用率过高",
                    "level": "warning"
                })
            
            # 检查磁盘告警
            if monitor.monitors['disk'].check_alerts():
                alerts.append({
                    "type": "disk",
                    "message": "磁盘使用率过高",
                    "level": "warning"
                })
            
            return jsonify({"alerts": alerts})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/config')
    def get_config():
        """获取配置信息"""
        try:
            return jsonify(monitor.config)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/config', methods=['POST'])
    def update_config():
        """更新配置信息"""
        try:
            new_config = request.get_json()
            if new_config:
                # 这里可以添加配置验证逻辑
                monitor.config.update(new_config)
                return jsonify({"message": "配置更新成功"})
            return jsonify({"error": "无效的配置数据"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/processes')
    def get_processes():
        """获取进程信息"""
        try:
            import psutil
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    processes.append({
                        "pid": proc_info['pid'],
                        "name": proc_info['name'],
                        "cpu_percent": proc_info['cpu_percent'],
                        "memory_percent": proc_info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 按CPU使用率排序
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return jsonify({"processes": processes[:20]})  # 返回前20个进程
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/system')
    def get_system():
        """获取系统基本信息"""
        try:
            from utils.helpers import get_system_info
            return jsonify(get_system_info())
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/health')
    def health_check():
        """健康检查"""
        try:
            # 检查各个监控模块是否正常工作
            health_status = {
                "status": "healthy",
                "timestamp": monitor.get_current_status()["timestamp"],
                "modules": {
                    "cpu": "ok",
                    "memory": "ok",
                    "gpu": "ok",
                    "disk": "ok",
                    "network": "ok"
                }
            }
            
            # 检查各个模块
            for module_name, monitor_instance in monitor.monitors.items():
                try:
                    monitor_instance.get_detailed_info()
                except Exception as e:
                    health_status["modules"][module_name] = f"error: {str(e)}"
                    health_status["status"] = "degraded"
            
            return jsonify(health_status)
        except Exception as e:
            return jsonify({"status": "unhealthy", "error": str(e)}), 500
    
    return app 