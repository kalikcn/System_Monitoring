# 网络测试功能说明

## 问题描述

网速测试功能可能出现以下错误：
- `Unable to connect to servers to test latency.`
- `speedtest-cli库未安装`
- 网络连接超时

## 解决方案

### 1. 自动降级测试
当speedtest-cli测试失败时，系统会自动降级到ping测试：

```python
# 测试多个服务器的ping延迟
test_hosts = ["8.8.8.8", "114.114.114.114", "1.1.1.1"]
```

### 2. 两种测试模式

#### 完整网速测试 (需要speedtest-cli)
- 下载速度测试
- 上传速度测试  
- 延迟测试
- 服务器信息

#### 简单网络测试 (仅ping)
- 网络连接状态
- 延迟测试
- 不依赖外部库

### 3. API接口

#### 完整网速测试
```bash
GET /api/speedtest
```

返回示例：
```json
{
    "download_speed_mbps": 25.5,
    "upload_speed_mbps": 10.2,
    "ping_ms": 15.3,
    "server": "Speedtest Server"
}
```

#### 简单网络测试
```bash
GET /api/network_test
```

返回示例：
```json
{
    "ping_ms": 12.5,
    "status": "connected",
    "note": "网络连接正常"
}
```

### 4. 安装speedtest-cli (可选)

如果需要完整的网速测试功能：

```bash
# 使用清华镜像源安装
pip install speedtest-cli -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5. 故障排除

#### 问题1: 无法连接到测试服务器
**原因**: 网络环境限制或防火墙阻止
**解决**: 使用简单网络测试，仅测试ping延迟

#### 问题2: speedtest-cli未安装
**原因**: 缺少依赖库
**解决**: 系统会自动使用ping测试作为替代

#### 问题3: 测试超时
**原因**: 网络连接慢或不稳定
**解决**: 系统设置了10秒超时，超时后自动降级

### 6. 测试建议

1. **首次使用**: 先运行简单网络测试确认网络连接
2. **完整测试**: 安装speedtest-cli后进行完整网速测试
3. **定期测试**: 建议定期测试网络状态
4. **故障诊断**: 如果测试失败，查看日志文件获取详细信息

### 7. 日志查看

网络测试的详细日志会记录在：
```
logs/SystemMonitor_YYYYMMDD.log
```

常见日志信息：
- `正在获取服务器列表...`
- `正在选择最佳服务器...`
- `正在测试下载速度...`
- `正在测试上传速度...`
- `网速测试失败: [错误信息]`

### 8. 配置选项

可以在`config/settings.json`中配置网络测试参数：

```json
{
    "network": {
        "speedtest_interval": 300,
        "ping_targets": ["8.8.8.8", "114.114.114.114", "1.1.1.1"],
        "timeout": 10
    }
}
```

### 9. 使用示例

#### Web界面
1. 访问 http://localhost:5000
2. 点击"网速测试"按钮
3. 查看测试结果

#### API调用
```bash
# 完整网速测试
curl http://localhost:5000/api/speedtest

# 简单网络测试
curl http://localhost:5000/api/network_test
```

#### 命令行
```bash
# 启动Web模式
python main.py --mode web

# 启动API模式
python main.py --mode api
``` 