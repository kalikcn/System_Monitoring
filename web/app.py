from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import threading
import time
from web.ubuntu_blueprint import ubuntu_monitor_bp, register_socketio_events, monitors, check_alerts, config

def create_app(monitor):
    app = Flask(__name__)
    CORS(app)
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # 注册 Ubuntu 监控子系统 Blueprint
    app.register_blueprint(ubuntu_monitor_bp, url_prefix='/ubuntu_monitor')
    # 注册 Ubuntu 监控的 SocketIO 事件
    register_socketio_events(socketio)

    # 启动 Ubuntu 监控推送线程
    def ubuntu_background_monitoring():
        while True:
            try:
                data = {
                    "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "cpu": monitors['cpu'].get_detailed_info(),
                    "memory": monitors['memory'].get_detailed_info(),
                    "gpu": monitors['gpu'].get_detailed_info(),
                    "disk": monitors['disk'].get_detailed_info(),
                    "network": monitors['network'].get_detailed_info(),
                    "alerts": check_alerts()
                }
                socketio.emit('ubuntu_system_update', data, namespace='/ubuntu_monitor')
                time.sleep(config.get('monitoring', {}).get('interval', 2))
            except Exception as e:
                print(f"Ubuntu 监控推送出错: {e}")
                time.sleep(2)
    ubuntu_monitor_thread = threading.Thread(target=ubuntu_background_monitoring)
    ubuntu_monitor_thread.daemon = True
    ubuntu_monitor_thread.start()
    
    @app.route('/')
    def index():
        """主页"""
        return render_template('index.html')
    
    @app.route('/api/status')
    def get_status():
        """获取系统状态API"""
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
    
    @socketio.on('connect')
    def handle_connect():
        """WebSocket连接"""
        print('客户端已连接')
        emit('connected', {'data': '已连接到系统监控'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """WebSocket断开连接"""
        print('客户端已断开连接')
    
    @socketio.on('request_data')
    def handle_request_data():
        """处理数据请求"""
        try:
            data = monitor.get_current_status()
            emit('system_data', data)
        except Exception as e:
            emit('error', {'error': str(e)})
    
    def background_monitoring():
        """后台监控线程"""
        while True:
            try:
                data = monitor.get_current_status()
                socketio.emit('system_data', data)
                time.sleep(2)  # 每2秒发送一次数据
            except Exception as e:
                print(f"后台监控出错: {e}")
                time.sleep(2)
    
    # 启动后台监控线程
    monitor_thread = threading.Thread(target=background_monitoring)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    return app 