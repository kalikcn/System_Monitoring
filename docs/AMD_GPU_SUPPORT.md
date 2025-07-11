# AMD GPU 支持说明

## 支持情况

系统监控工具现在支持检测AMD显卡，但功能支持程度取决于不同的检测方法：

### 1. GPUtil库检测 (推荐)
- **支持**: 使用率、内存使用、温度
- **要求**: 安装GPUtil库
- **安装**: `pip install GPUtil`

### 2. Windows WMI检测
- **支持**: 显卡名称、显存大小
- **限制**: 无法获取实时使用率和温度
- **要求**: Windows系统 + wmi库

### 3. Linux lspci检测
- **支持**: 显卡名称
- **限制**: 无法获取使用率、内存、温度
- **要求**: Linux系统

## 安装依赖

### 完整GPU监控支持
```bash
# 安装所有GPU监控依赖
pip install GPUtil pynvml wmi -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 仅AMD GPU检测
```bash
# Windows系统
pip install wmi -i https://pypi.tuna.tsinghua.edu.cn/simple

# Linux系统
# 通常lspci命令已预装
```

## 检测方法

### 方法1: GPUtil (最全面)
```python
import GPUtil
gpus = GPUtil.getGPUs()
for gpu in gpus:
    print(f"GPU: {gpu.name}")
    print(f"使用率: {gpu.load * 100}%")
    print(f"内存: {gpu.memoryUsed}/{gpu.memoryTotal} MB")
    print(f"温度: {gpu.temperature}°C")
```

### 方法2: Windows WMI
```python
import wmi
w = wmi.WMI()
for gpu in w.Win32_VideoController():
    if "AMD" in gpu.Name or "Radeon" in gpu.Name:
        print(f"AMD GPU: {gpu.Name}")
        print(f"显存: {gpu.AdapterRAM // (1024*1024)} MB")
```

### 方法3: Linux lspci
```bash
lspci | grep -i vga
```

## 功能对比

| 功能 | GPUtil | Windows WMI | Linux lspci |
|------|--------|-------------|-------------|
| 显卡名称 | ✅ | ✅ | ✅ |
| 使用率 | ✅ | ❌ | ❌ |
| 内存使用 | ✅ | ✅ | ❌ |
| 温度 | ✅ | ❌ | ❌ |
| 风扇转速 | ✅ | ❌ | ❌ |

## 常见问题

### 问题1: 无法检测到AMD GPU
**解决方案**:
1. 确认已安装AMD显卡驱动
2. 检查GPUtil库是否正确安装
3. 在Windows上尝试WMI方法
4. 在Linux上检查lspci输出

### 问题2: 检测到GPU但无法获取使用率
**原因**: 某些检测方法只能获取基本信息
**解决**: 安装GPUtil库获得完整功能

### 问题3: 温度显示为0
**原因**: AMD显卡温度检测需要特定驱动支持
**解决**: 确保安装了最新的AMD显卡驱动

## 测试AMD GPU检测

### 命令行测试
```bash
python test_monitor.py
```

### 手动测试
```python
from core.gpu_monitor import GPUMonitor

monitor = GPUMonitor()
gpu_info = monitor.get_gpu_info()
print(gpu_info)
```

## 配置选项

在`config/settings.json`中可以配置GPU监控：

```json
{
  "gpu": {
    "detection_method": "auto",  // auto, gputil, wmi, lspci
    "update_interval": 2,
    "temperature_threshold": 85
  }
}
```

## 日志查看

GPU检测的详细日志：
```
logs/SystemMonitor_YYYYMMDD.log
```

常见日志信息：
- `检测到 X 个GPU`
- `GPUtil库未安装，尝试其他方法检测GPU`
- `Windows下检测到 X 个AMD GPU`
- `Linux下检测到 X 个AMD GPU`

## 使用建议

1. **首次使用**: 运行测试脚本确认GPU检测
2. **完整功能**: 安装GPUtil库获得最佳体验
3. **Windows用户**: 确保安装了wmi库
4. **Linux用户**: 检查lspci命令是否可用

## 故障排除

### Windows系统
1. 以管理员身份运行程序
2. 确保AMD显卡驱动已安装
3. 检查Windows Management Instrumentation服务

### Linux系统
1. 确保有lspci命令
2. 检查显卡驱动是否正确安装
3. 尝试安装GPUtil库

### 通用问题
1. 查看日志文件获取详细错误信息
2. 确认Python环境正确
3. 检查依赖库是否正确安装 