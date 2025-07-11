#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安全测试脚本
验证系统监控工具的安全修复是否有效
"""

import requests
import json
import time
import sys
from typing import Dict, List, Tuple

class SecurityTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """记录测试结果"""
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} {test_name}")
        if details:
            print(f"   详情: {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def test_cors_configuration(self) -> bool:
        """测试CORS配置"""
        try:
            # 测试允许的来源
            headers = {"Origin": "http://localhost:5000"}
            response = self.session.get(f"{self.base_url}/api/status", headers=headers)
            
            if "Access-Control-Allow-Origin" in response.headers:
                origin = response.headers["Access-Control-Allow-Origin"]
                if origin == "http://localhost:5000":
                    self.log_test("CORS配置", True, f"允许的来源: {origin}")
                    return True
                else:
                    self.log_test("CORS配置", False, f"意外的来源: {origin}")
                    return False
            else:
                self.log_test("CORS配置", False, "缺少CORS头")
                return False
                
        except Exception as e:
            self.log_test("CORS配置", False, f"测试失败: {e}")
            return False
    
    def test_authentication_required(self) -> bool:
        """测试身份验证要求"""
        try:
            # 测试需要认证的端点
            response = self.session.post(f"{self.base_url}/api/config", 
                                       json={"test": "data"})
            
            if response.status_code == 401:
                self.log_test("身份验证要求", True, "正确返回401状态码")
                return True
            else:
                self.log_test("身份验证要求", False, f"意外状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("身份验证要求", False, f"测试失败: {e}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """测试请求频率限制"""
        try:
            # 快速发送多个请求
            responses = []
            for i in range(10):
                response = self.session.get(f"{self.base_url}/api/status")
                responses.append(response.status_code)
                time.sleep(0.1)
            
            # 检查是否有429状态码（请求过于频繁）
            if 429 in responses:
                self.log_test("请求频率限制", True, "正确触发频率限制")
                return True
            else:
                self.log_test("请求频率限制", False, "未触发频率限制")
                return False
                
        except Exception as e:
            self.log_test("请求频率限制", False, f"测试失败: {e}")
            return False
    
    def test_input_validation(self) -> bool:
        """测试输入验证"""
        try:
            # 测试恶意输入
            malicious_inputs = [
                {"config": "<script>alert('xss')</script>"},
                {"path": "../../../etc/passwd"},
                {"command": "rm -rf /"},
                {"data": {"__proto__": {"admin": True}}}
            ]
            
            for i, malicious_input in enumerate(malicious_inputs):
                response = self.session.post(f"{self.base_url}/api/config", 
                                           json=malicious_input)
                
                # 应该返回400或401状态码
                if response.status_code in [400, 401, 403]:
                    self.log_test(f"输入验证 {i+1}", True, f"正确拒绝恶意输入")
                else:
                    self.log_test(f"输入验证 {i+1}", False, f"未拒绝恶意输入，状态码: {response.status_code}")
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("输入验证", False, f"测试失败: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        try:
            # 测试各种错误情况
            error_tests = [
                ("/api/nonexistent", 404),
                ("/api/status", 200),  # 正常请求
            ]
            
            for endpoint, expected_status in error_tests:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == expected_status:
                    self.log_test(f"错误处理 {endpoint}", True, f"状态码: {response.status_code}")
                else:
                    self.log_test(f"错误处理 {endpoint}", False, f"期望状态码: {expected_status}, 实际: {response.status_code}")
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("错误处理", False, f"测试失败: {e}")
            return False
    
    def test_secure_headers(self) -> bool:
        """测试安全头部"""
        try:
            response = self.session.get(f"{self.base_url}/api/status")
            
            # 检查安全头部
            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection"
            ]
            
            missing_headers = []
            for header in security_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            if not missing_headers:
                self.log_test("安全头部", True, "所有安全头部都已设置")
                return True
            else:
                self.log_test("安全头部", False, f"缺少安全头部: {missing_headers}")
                return False
                
        except Exception as e:
            self.log_test("安全头部", False, f"测试失败: {e}")
            return False
    
    def test_sql_injection_protection(self) -> bool:
        """测试SQL注入防护"""
        try:
            # 测试SQL注入攻击
            sql_injection_payloads = [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "'; INSERT INTO users VALUES ('hacker', 'password'); --"
            ]
            
            for payload in sql_injection_payloads:
                response = self.session.post(f"{self.base_url}/api/config", 
                                           json={"data": payload})
                
                # 应该返回400或401状态码
                if response.status_code in [400, 401, 403]:
                    self.log_test(f"SQL注入防护", True, "正确拒绝SQL注入攻击")
                else:
                    self.log_test(f"SQL注入防护", False, f"未拒绝SQL注入攻击，状态码: {response.status_code}")
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("SQL注入防护", False, f"测试失败: {e}")
            return False
    
    def test_xss_protection(self) -> bool:
        """测试XSS防护"""
        try:
            # 测试XSS攻击
            xss_payloads = [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>"
            ]
            
            for payload in xss_payloads:
                response = self.session.post(f"{self.base_url}/api/config", 
                                           json={"data": payload})
                
                # 检查响应中是否包含恶意脚本
                if payload in response.text:
                    self.log_test("XSS防护", False, f"响应中包含恶意脚本: {payload}")
                    return False
            
            self.log_test("XSS防护", True, "正确过滤XSS攻击")
            return True
                
        except Exception as e:
            self.log_test("XSS防护", False, f"测试失败: {e}")
            return False
    
    def test_command_injection_protection(self) -> bool:
        """测试命令注入防护"""
        try:
            # 测试命令注入攻击
            command_injection_payloads = [
                "ping 127.0.0.1; rm -rf /",
                "ls; cat /etc/passwd",
                "whoami && id"
            ]
            
            for payload in command_injection_payloads:
                response = self.session.post(f"{self.base_url}/api/config", 
                                           json={"command": payload})
                
                # 应该返回400或401状态码
                if response.status_code in [400, 401, 403]:
                    self.log_test(f"命令注入防护", True, "正确拒绝命令注入攻击")
                else:
                    self.log_test(f"命令注入防护", False, f"未拒绝命令注入攻击，状态码: {response.status_code}")
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("命令注入防护", False, f"测试失败: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, any]:
        """运行所有安全测试"""
        print("🔒 开始安全测试...")
        print("=" * 50)
        
        tests = [
            ("CORS配置", self.test_cors_configuration),
            ("身份验证要求", self.test_authentication_required),
            ("请求频率限制", self.test_rate_limiting),
            ("输入验证", self.test_input_validation),
            ("错误处理", self.test_error_handling),
            ("安全头部", self.test_secure_headers),
            ("SQL注入防护", self.test_sql_injection_protection),
            ("XSS防护", self.test_xss_protection),
            ("命令注入防护", self.test_command_injection_protection)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"测试异常: {e}")
        
        print("=" * 50)
        print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
        
        if passed_tests == total_tests:
            print("🎉 所有安全测试通过！")
        else:
            print("⚠️  发现安全漏洞，请检查修复建议")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "results": self.test_results
        }

def main():
    """主函数"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print(f"🔒 安全测试工具")
    print(f"目标URL: {base_url}")
    print()
    
    tester = SecurityTester(base_url)
    results = tester.run_all_tests()
    
    # 保存测试结果
    with open("security_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 测试结果已保存到: security_test_results.json")
    
    # 返回退出码
    if results["passed_tests"] == results["total_tests"]:
        sys.exit(0)  # 成功
    else:
        sys.exit(1)  # 失败

if __name__ == "__main__":
    main() 