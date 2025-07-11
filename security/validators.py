#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
输入验证模块
提供数据验证和清理功能
"""

import re
import json
from typing import Dict, Any, Optional, Tuple
from utils.logger import logger

class ValidationError(Exception):
    """验证错误异常"""
    pass

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.allowed_keys = {
            'monitoring': ['interval', 'history_size', 'log_level'],
            'alerts': ['cpu_usage_threshold', 'memory_usage_threshold', 
                      'gpu_usage_threshold', 'disk_usage_threshold', 'temperature_threshold'],
            'web': ['host', 'port', 'debug'],
            'data': ['save_path', 'export_format'],
            'network': ['speedtest_interval', 'ping_targets']
        }
        
        self.value_ranges = {
            'monitoring.interval': (1, 60),
            'monitoring.history_size': (100, 10000),
            'alerts.cpu_usage_threshold': (0, 100),
            'alerts.memory_usage_threshold': (0, 100),
            'alerts.gpu_usage_threshold': (0, 100),
            'alerts.disk_usage_threshold': (0, 100),
            'alerts.temperature_threshold': (0, 150),
            'web.port': (1024, 65535),
            'network.speedtest_interval': (60, 3600)
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """验证配置数据"""
        try:
            # 检查顶层键
            for key in config:
                if key not in self.allowed_keys:
                    return False, f"不允许的配置键: {key}"
            
            # 验证每个部分
            for section, section_config in config.items():
                if not isinstance(section_config, dict):
                    return False, f"配置部分 {section} 必须是字典"
                
                # 检查允许的键
                for key in section_config:
                    if key not in self.allowed_keys[section]:
                        return False, f"配置部分 {section} 中不允许的键: {key}"
                
                # 验证数值范围
                for key, value in section_config.items():
                    config_key = f"{section}.{key}"
                    if config_key in self.value_ranges:
                        min_val, max_val = self.value_ranges[config_key]
                        if not isinstance(value, (int, float)) or not (min_val <= value <= max_val):
                            return False, f"{config_key} 的值必须在 {min_val} 和 {max_val} 之间"
            
            return True, None
            
        except Exception as e:
            logger.error(f"配置验证错误: {e}")
            return False, f"配置验证失败: {str(e)}"
    
    def sanitize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """清理配置数据"""
        sanitized = {}
        
        for section, section_config in config.items():
            if section in self.allowed_keys:
                sanitized[section] = {}
                for key, value in section_config.items():
                    if key in self.allowed_keys[section]:
                        # 类型转换和验证
                        config_key = f"{section}.{key}"
                        if config_key in self.value_ranges:
                            min_val, max_val = self.value_ranges[config_key]
                            try:
                                value = float(value)
                                value = max(min_val, min(max_val, value))
                            except (ValueError, TypeError):
                                value = min_val
                        sanitized[section][key] = value
        
        return sanitized

class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_hostname(hostname: str) -> bool:
        """验证主机名"""
        if not hostname:
            return False
        
        # 简单的IP地址验证
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ip_pattern, hostname):
            parts = hostname.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        
        # 主机名验证
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
        return bool(re.match(hostname_pattern, hostname))
    
    @staticmethod
    def validate_port(port: Any) -> bool:
        """验证端口号"""
        try:
            port_num = int(port)
            return 1024 <= port_num <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_interval(interval: Any) -> bool:
        """验证时间间隔"""
        try:
            interval_num = float(interval)
            return 1 <= interval_num <= 60
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_threshold(threshold: Any) -> bool:
        """验证阈值"""
        try:
            threshold_num = float(threshold)
            return 0 <= threshold_num <= 100
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def sanitize_string(value: Any, max_length: int = 1000) -> str:
        """清理字符串输入"""
        if not isinstance(value, str):
            value = str(value)
        
        # 移除危险字符
        value = re.sub(r'[<>"\']', '', value)
        
        # 限制长度
        if len(value) > max_length:
            value = value[:max_length]
        
        return value.strip()
    
    @staticmethod
    def sanitize_json(data: str) -> Optional[Dict[str, Any]]:
        """清理JSON输入"""
        try:
            # 解析JSON
            parsed = json.loads(data)
            
            # 确保是字典
            if not isinstance(parsed, dict):
                return None
            
            # 递归清理字符串值
            def clean_dict(obj):
                if isinstance(obj, dict):
                    return {k: clean_dict(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [clean_dict(item) for item in obj]
                elif isinstance(obj, str):
                    return InputValidator.sanitize_string(obj)
                else:
                    return obj
            
            return clean_dict(parsed)
            
        except (json.JSONDecodeError, TypeError):
            return None

class CommandValidator:
    """命令验证器"""
    
    def __init__(self):
        self.allowed_commands = {
            'ping': ['ping', '-n', '-c', '-W', '-t'],
            'lspci': ['lspci'],
            'ls': ['ls', '-la', '-l'],
            'cat': ['cat'],
            'head': ['head', '-n'],
            'tail': ['tail', '-n']
        }
    
    def validate_command(self, command: str) -> bool:
        """验证命令是否安全"""
        if not command:
            return False
        
        # 分割命令
        parts = command.split()
        if not parts:
            return False
        
        cmd = parts[0]
        
        # 检查是否在允许的命令列表中
        if cmd not in self.allowed_commands:
            return False
        
        # 检查参数
        allowed_args = self.allowed_commands[cmd]
        for arg in parts[1:]:
            if arg not in allowed_args and not arg.startswith('-'):
                return False
        
        return True
    
    def sanitize_command(self, command: str) -> Optional[str]:
        """清理命令"""
        if not self.validate_command(command):
            return None
        
        # 移除危险字符
        command = re.sub(r'[;&|`$(){}]', '', command)
        
        return command.strip()

# 全局验证器实例
config_validator = ConfigValidator()
input_validator = InputValidator()
command_validator = CommandValidator()

def validate_api_input(data: Dict[str, Any], required_fields: list = None) -> Tuple[bool, Optional[str]]:
    """验证API输入"""
    try:
        if not isinstance(data, dict):
            return False, "输入必须是JSON对象"
        
        # 检查必需字段
        if required_fields:
            for field in required_fields:
                if field not in data:
                    return False, f"缺少必需字段: {field}"
        
        # 清理字符串值
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = input_validator.sanitize_string(value)
        
        return True, None
        
    except Exception as e:
        logger.error(f"API输入验证错误: {e}")
        return False, f"输入验证失败: {str(e)}"

def safe_json_response(data: Any) -> str:
    """安全的JSON响应"""
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except Exception as e:
        logger.error(f"JSON序列化错误: {e}")
        return json.dumps({"error": "数据序列化失败"})

def validate_file_path(path: str) -> bool:
    """验证文件路径"""
    if not path:
        return False
    
    # 检查路径遍历攻击
    if '..' in path or path.startswith('/'):
        return False
    
    # 检查危险字符
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    if any(char in path for char in dangerous_chars):
        return False
    
    return True 