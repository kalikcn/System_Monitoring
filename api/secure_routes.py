#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安全的API路由
修复了所有已知的安全漏洞
"""

import os
import logging
from functools import wraps
from flask import Flask, jsonify, request, current_app
from flask_cors import CORS
from security.auth import require_auth, require_admin, rate_limit, auth_manager, init_auth
from security.validators import config_validator, input_validator, command_validator
from utils.logger import logger

def create_secure_api_app(monitor):
    """创建安全的API应用"""
    app = Flask(__name__)
    
    # 安全的CORS配置
    CORS(app, 
          origins=['http://localhost:5000', 'http://127.0.0.1:5000'],
          methods=['GET', 'POST'],
          allow_headers=['Content-Type', 'Authorization'],
          supports_credentials=True)
    
    # 初始化认证系统
    init_auth()
    
    # 安全错误处理装饰器
    def safe_api_response(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"API错误: {str(e)}")
                # 生产环境不返回详细错误信息
                if app.config.get('DEBUG', False):
                    return jsonify({"error": str(e)}), 500
                else:
                    return jsonify({"error": "内部服务器错误"}), 500
        return wrapper
    
    @app.route('/api/status')
    @safe_api_response
    @rate_limit(max_requests=60, window=60)
    def get_status():
        """获取系统状态"""
        data = monitor.get_current_status()
        return jsonify(data)
    
    @app.route('/api/cpu')
    @safe_api_response
    @rate_limit(max_requests=60, window=60)
    def get_cpu():
        """获取CPU信息"""
        data = monitor.monitors['cpu'].get_detailed_info()
        return jsonify(data)
    
    @app.route('/api/memory')
    @safe_api_response
    @rate_limit(max_requests=60, window=60)
    def get_memory():
        """获取内存信息"""
        data = monitor.monitors['memory'].get_detailed_info()
        return jsonify(data)
    
    @app.route('/api/gpu')
    @safe_api_response
    @rate_limit(max_requests=60, window=60)
    def get_gpu():
        """获取GPU信息"""
        data = monitor.monitors['gpu'].get_detailed_info()
        return jsonify(data)
    
    @app.route('/api/disk')
    @safe_api_response
    @rate_limit(max_requests=60, window=60)
    def get_disk():
        """获取磁盘信息"""
        data = monitor.monitors['disk'].get_detailed_info()
        return jsonify(data)
    
    @app.route('/api/network')
    @safe_api_response
    @rate_limit(max_requests=60, window=60)
    def get_network():
        """获取网络信息"""
        data = monitor.monitors['network'].get_detailed_info()
        return jsonify(data)
    
    @app.route('/api/speedtest')
    @safe_api_response
    @rate_limit(max_requests=10, window=300)  # 限制网速测试频率
    def run_speedtest():
        """执行网速测试"""
        result = monitor.monitors['network'].speed_test()
        return jsonify(result if result else {"error": "网速测试失败"})
    
    @app.route('/api/network_test')
    @safe_api_response
    @rate_limit(max_requests=30, window=60)
    def run_network_test():
        """执行简单网络测试"""
        result = monitor.monitors['network'].simple_network_test()
        return jsonify(result)
    
    @app.route('/api/alerts')
    @safe_api_response
    @rate_limit(max_requests=60, window=60)
    def get_alerts():
        """获取告警信息"""
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
    
    @app.route('/api/config')
    @safe_api_response
    @rate_limit(max_requests=30, window=60)
    def get_config():
        """获取配置信息"""
        # 过滤敏感信息
        safe_config = {}
        for key, value in monitor.config.items():
            if key in ['monitoring', 'alerts', 'web', 'data', 'network']:
                safe_config[key] = value
        return jsonify(safe_config)
    
    @app.route('/api/config', methods=['POST'])
    @safe_api_response
    @require_admin  # 需要管理员权限
    @rate_limit(max_requests=10, window=60)
    def update_config():
        """更新配置信息"""
        try:
            new_config = request.get_json()
            if not new_config:
                return jsonify({"error": "无效的配置数据"}), 400
            
            # 验证配置
            is_valid, error_msg = config_validator.validate_config(new_config)
            if not is_valid:
                return jsonify({"error": error_msg}), 400
            
            # 清理配置数据
            sanitized_config = config_validator.sanitize_config(new_config)
            
            # 更新配置
            monitor.config.update(sanitized_config)
            
            logger.info("配置更新成功")
            return jsonify({"message": "配置更新成功"})
            
        except Exception as e:
            logger.error(f"配置更新失败: {e}")
            return jsonify({"error": "配置更新失败"}), 500
    
    @app.route('/api/processes')
    @safe_api_response
    @rate_limit(max_requests=30, window=60)
    def get_processes():
        """获取进程信息"""
        try:
            import psutil
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    # 清理进程名称
                    name = input_validator.sanitize_string(proc_info['name'], max_length=100)
                    
                    processes.append({
                        "pid": proc_info['pid'],
                        "name": name,
                        "cpu_percent": round(proc_info['cpu_percent'], 2),
                        "memory_percent": round(proc_info['memory_percent'], 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 按CPU使用率排序，只返回前20个进程
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return jsonify({"processes": processes[:20]})
            
        except Exception as e:
            logger.error(f"获取进程信息失败: {e}")
            return jsonify({"error": "获取进程信息失败"}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    @safe_api_response
    @rate_limit(max_requests=5, window=300)  # 限制登录尝试
    def login():
        """用户登录"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "缺少登录数据"}), 400
            
            username = input_validator.sanitize_string(data.get('username', ''))
            password = data.get('password', '')
            
            if not username or not password:
                return jsonify({"error": "用户名和密码不能为空"}), 400
            
            # 验证用户
            from security.auth import authenticate_user, create_user_session
            user_info = authenticate_user(username, password)
            
            if not user_info:
                return jsonify({"error": "用户名或密码错误"}), 401
            
            # 创建会话
            session = create_user_session(user_info)
            
            logger.info(f"用户 {username} 登录成功")
            return jsonify(session)
            
        except Exception as e:
            logger.error(f"登录失败: {e}")
            return jsonify({"error": "登录失败"}), 500
    
    @app.route('/api/auth/refresh', methods=['POST'])
    @safe_api_response
    @rate_limit(max_requests=10, window=300)
    def refresh_token():
        """刷新访问令牌"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "缺少刷新令牌"}), 400
            
            refresh_token = data.get('refresh_token', '')
            if not refresh_token:
                return jsonify({"error": "刷新令牌不能为空"}), 400
            
            # 验证刷新令牌
            user_id = auth_manager.validate_refresh_token(refresh_token)
            if not user_id:
                return jsonify({"error": "无效的刷新令牌"}), 401
            
            # 生成新的访问令牌
            access_token = auth_manager.generate_token(user_id)
            
            return jsonify({
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 3600
            })
            
        except Exception as e:
            logger.error(f"令牌刷新失败: {e}")
            return jsonify({"error": "令牌刷新失败"}), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    @safe_api_response
    @require_auth
    def logout():
        """用户登出"""
        try:
            data = request.get_json()
            refresh_token = data.get('refresh_token', '') if data else ''
            
            if refresh_token:
                auth_manager.revoke_token(refresh_token)
            
            logger.info("用户登出成功")
            return jsonify({"message": "登出成功"})
            
        except Exception as e:
            logger.error(f"登出失败: {e}")
            return jsonify({"error": "登出失败"}), 500
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "资源不存在"}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"error": "方法不允许"}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"内部服务器错误: {error}")
        return jsonify({"error": "内部服务器错误"}), 500
    
    return app 