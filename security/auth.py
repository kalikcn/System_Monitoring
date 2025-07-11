#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
身份验证模块
提供JWT令牌生成和验证功能
"""

import jwt
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from utils.logger import logger

class AuthManager:
    def __init__(self, secret_key=None):
        """初始化认证管理器"""
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY') or secrets.token_hex(32)
        self.tokens = {}  # 简单的令牌存储，生产环境应使用Redis
        self.refresh_tokens = {}
    
    def generate_token(self, user_id, expires_in=3600):
        """生成JWT访问令牌"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def generate_refresh_token(self, user_id, expires_in=86400):
        """生成刷新令牌"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        refresh_token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        self.refresh_tokens[refresh_token] = user_id
        return refresh_token
    
    def validate_token(self, token):
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # 检查令牌类型
            if payload.get('type') != 'access':
                return None
            
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效令牌: {e}")
            return None
        except Exception as e:
            logger.error(f"令牌验证错误: {e}")
            return None
    
    def validate_refresh_token(self, refresh_token):
        """验证刷新令牌"""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=['HS256'])
            
            if payload.get('type') != 'refresh':
                return None
            
            user_id = payload['user_id']
            if refresh_token in self.refresh_tokens and self.refresh_tokens[refresh_token] == user_id:
                return user_id
            return None
        except jwt.ExpiredSignatureError:
            # 清理过期的刷新令牌
            if refresh_token in self.refresh_tokens:
                del self.refresh_tokens[refresh_token]
            return None
        except jwt.InvalidTokenError:
            return None
    
    def revoke_token(self, refresh_token):
        """撤销刷新令牌"""
        if refresh_token in self.refresh_tokens:
            del self.refresh_tokens[refresh_token]
            return True
        return False
    
    def hash_password(self, password):
        """哈希密码"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def verify_password(self, password, hashed_password):
        """验证密码"""
        try:
            salt, hash_hex = hashed_password.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return hash_obj.hex() == hash_hex
        except Exception:
            return False

# 全局认证管理器实例
auth_manager = AuthManager()

def require_auth(f):
    """身份验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "缺少认证头"}), 401
        
        # 支持Bearer令牌和API密钥
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user_id = auth_manager.validate_token(token)
            if not user_id:
                return jsonify({"error": "无效的访问令牌"}), 401
        elif auth_header.startswith('ApiKey '):
            api_key = auth_header.split(' ')[1]
            if api_key != os.getenv('API_KEY', 'default_key'):
                return jsonify({"error": "无效的API密钥"}), 401
        else:
            return jsonify({"error": "无效的认证格式"}), 401
        
        return f(*args, **kwargs)
    return decorated

def require_admin(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "缺少认证头"}), 401
        
        # 检查管理员权限
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user_id = auth_manager.validate_token(token)
            if not user_id:
                return jsonify({"error": "无效的访问令牌"}), 401
            
            # 这里可以添加管理员检查逻辑
            # 例如从数据库检查用户角色
            if user_id != 'admin':
                return jsonify({"error": "需要管理员权限"}), 403
        
        return f(*args, **kwargs)
    return decorated

def rate_limit(max_requests=100, window=60):
    """请求频率限制装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            client_ip = request.remote_addr
            
            # 简单的内存存储，生产环境应使用Redis
            if not hasattr(current_app, 'rate_limit'):
                current_app.rate_limit = {}
            
            now = datetime.utcnow()
            if client_ip not in current_app.rate_limit:
                current_app.rate_limit[client_ip] = []
            
            # 清理过期的请求记录
            current_app.rate_limit[client_ip] = [
                req_time for req_time in current_app.rate_limit[client_ip]
                if (now - req_time).seconds < window
            ]
            
            # 检查请求频率
            if len(current_app.rate_limit[client_ip]) >= max_requests:
                return jsonify({"error": "请求过于频繁，请稍后再试"}), 429
            
            # 记录当前请求
            current_app.rate_limit[client_ip].append(now)
            
            return f(*args, **kwargs)
        return decorated
    return decorator

# 简单的用户存储，生产环境应使用数据库
USERS = {
    'admin': {
        'password': None,  # 将在初始化时设置
        'role': 'admin',
        'created_at': datetime.utcnow()
    },
    'user': {
        'password': None,
        'role': 'user',
        'created_at': datetime.utcnow()
    }
}

def init_auth():
    """初始化认证系统"""
    # 设置默认密码
    USERS['admin']['password'] = auth_manager.hash_password('admin123')
    USERS['user']['password'] = auth_manager.hash_password('user123')
    
    logger.info("认证系统初始化完成")

def authenticate_user(username, password):
    """用户认证"""
    if username not in USERS:
        return None
    
    user = USERS[username]
    if auth_manager.verify_password(password, user['password']):
        return {
            'user_id': username,
            'role': user['role']
        }
    return None

def create_user_session(user_info):
    """创建用户会话"""
    access_token = auth_manager.generate_token(user_info['user_id'])
    refresh_token = auth_manager.generate_refresh_token(user_info['user_id'])
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': 3600,
        'user_id': user_info['user_id'],
        'role': user_info['role']
    } 