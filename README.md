# YST5.1 文件加密检测与解密工具

## 概述

YST5.1 是一个模块化的文件加密检测与解密工具，支持多种文件格式的加密状态检测和自动解密功能。

## 主要功能

- 🔍 **文件加密检测**：检测文件是否加密或未识别
- 🔓 **文件解密**：使用外部程序（如WPS）自动解密加密文件
- 📁 **批量处理**：支持目录扫描和批量文件处理
- 🎨 **图形界面**：提供友好的图形用户界面
- 💻 **命令行**：支持命令行操作，便于自动化
- ⚙️ **配置管理**：可扩展的文件类型识别机制
- 📝 **日志记录**：完整的操作日志记录

## 项目结构

```
YST5.1/
├── main.py                    # 原始主程序（保留）
├── check_encryption.py        # 原始加密检测模块（保留）
├── process_encrypted_file.py  # 原始文件处理模块（保留）
├── main_refactored.py         # 重构后的主程序
├── modules/                   # 模块化组件目录
│   ├── __init__.py           # 模块包初始化
│   ├── config.py             # 配置管理模块
│   ├── encryption_detector.py # 文件加密检测模块
│   ├── file_processor.py     # 文件处理模块
│   ├── logger.py             # 日志管理模块
│   ├── gui.py                # 图形界面模块
│   └── cli.py                # 命令行接口模块
└── README.md                 # 项目说明文档
```

## 模块说明

### 1. config.py - 配置管理
- 管理程序配置信息
- 标准文件头和扩展名定义
- 配置文件加载和保存
- 程序设置管理

### 2. encryption_detector.py - 文件加密检测
- 文件头匹配检测
- 扩展名检测
- 加密状态判断
- 批量检测功能

### 3. file_processor.py - 文件处理
- 使用外部程序打开文件
- 临时文件处理和恢复
- 文件格式转换
- 批量处理功能

### 4. logger.py - 日志管理
- 统一的日志配置
- 多级别日志输出
- 文件和控制台日志
- 调试模式控制

### 5. gui.py - 图形界面
- 友好的用户界面
- 文件选择和浏览
- 实时结果显示
- 设置管理界面

### 6. cli.py - 命令行接口
- 完整的命令行参数支持
- 批量操作功能
- 结果输出到文件
- 脚本自动化支持

## 使用方法

### 1. 图形界面模式

```bash
# 启动图形界面
python main_refactored.py
```

### 2. 命令行模式

#### 检查文件加密状态
```bash
# 检查单个文件
python main_refactored.py check file.txt

# 检查多个文件
python main_refactored.py check file1.txt file2.txt

# 递归检查目录
python main_refactored.py check /path/to/directory --recursive

# 输出结果到文件
python main_refactored.py check file.txt --output results.json
```

#### 解密文件
```bash
# 解密单个文件
python main_refactored.py unlock file.txt

# 解密目录（递归）
python main_refactored.py unlock /path/to/directory --recursive

# 指定解密程序
python main_refactored.py unlock file.txt --program /path/to/program.exe

# 批量解密
python main_refactored.py batch-unlock file1.txt file2.txt file3.txt
```

#### 扫描目录
```bash
# 扫描目录中所有文件
python main_refactored.py scan /path/to/directory

# 非递归扫描
python main_refactored.py scan /path/to/directory --no-recursive
```

#### 调试模式
```bash
# 启用调试输出
python main_refactored.py --debug check file.txt
```

### 3. 兼容旧版用法

```bash
# 简化的文件处理（兼容旧版）
python main_refactored.py file1.txt file2.txt
```

### 4. 帮助信息

```bash
# 显示帮助
python main_refactored.py --help

# 显示版本
python main_refactored.py --version
```

## 配置说明

程序使用 `config.json` 文件存储配置信息：

```json
{
  "extensions": [".pdf", ".doc", ".docx", ".dwg"],
  "headers": {
    "25504446": "PDF",
    "d0cf11e0": "WORD"
  },
  "settings": {
    "debug": false,
    "max_threads": 5,
    "timeout": 5,
    "wps_path": "wps.exe"
  }
}
```

## 支持的文件类型

### 默认支持
- **文档文件**：.doc, .docx, .xls, .xlsx, .ppt, .pptx
- **PDF文件**：.pdf
- **压缩文件**：.zip
- **CAD文件**：.dwg

### 扩展支持
通过配置文件可以添加新的文件类型支持：
- 在 `extensions` 中添加新的扩展名
- 在 `headers` 中添加对应的文件头标识

## 日志记录

程序会自动记录操作日志到 `main.log` 文件，包括：
- 文件检测结果
- 解密操作状态
- 错误和异常信息
- 调试信息（调试模式下）

## 开发和集成

### 作为模块使用

```python
# 导入主要组件
from modules.encryption_detector import get_encryption_detector
from modules.file_processor import get_file_processor
from modules.config import get_config_manager

# 使用示例
detector = get_encryption_detector()
result = detector.get_detection_result('file.txt')

processor = get_file_processor()
decrypted_path = processor.process_encrypted_file('encrypted_file.txt')
```

### 扩展功能

1. **添加新的文件类型检测**
   ```python
   config_manager = get_config_manager()
   config_manager.add_header('12345678', 'NEW_TYPE')
   config_manager.add_extension('.newext')
   ```

2. **自定义处理器**
   ```python
   processor = get_file_processor()
   # 继承或扩展 FileProcessor 类
   ```

## 注意事项

1. **程序依赖**：需要安装相应的文件处理程序（如WPS Office）
2. **权限要求**：需要对目标文件和目录有读写权限
3. **临时文件**：处理过程中会生成临时文件，完成后会自动清理
4. **备份建议**：重要文件建议在处理前进行备份

## 版本历史

- **v6.0**：模块化重构，提供完整的GUI和CLI接口
- **v5.x**：原始版本，基础功能实现

## 技术支持

如有问题或建议，请联系开发团队：
- 邮箱：support@yst.com
- 项目地址：https://github.com/yst-team/yyst-file-processor

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。