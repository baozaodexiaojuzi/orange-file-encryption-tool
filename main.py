"""
YST5.1 文件加密检测与解密工具

基于模块化设计的文件加密检测与解密工具

功能：
1. 检测文件或目录中的文件是否加密或未识别
2. 若文件已加密，尝试使用外部程序解密
3. 支持图形界面和命令行两种模式
4. 提供完整的日志记录和配置管理

使用方法：
1. 图形界面模式：python main.py
2. 命令行模式：python main.py <命令> <参数>
3. 兼容旧版用法：python main.py <文件路径>

架构设计：
- modules.config: 配置管理
- modules.encryption_detector: 文件加密检测
- modules.file_processor: 文件处理
- modules.logger: 日志管理
- modules.gui: 图形界面
- modules.cli: 命令行接口
"""

import sys
import os

# 添加模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(current_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)

try:
    from modules.config import get_config_manager
    from modules.logger import get_logger
    from modules.gui import run_gui
    from modules.cli import run_cli
    from modules.encryption_detector import check_file_encryption, check_file_encryption_with_feedback
    from modules.file_processor import open_and_process_file
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保 modules 目录存在且包含所有必要的模块文件")
    sys.exit(1)


def print_usage():
    """打印使用说明"""
    print("""
YST5.1 文件加密检测与解密工具

使用方法：
1. 图形界面模式：
   python main.py

2. 命令行模式：
   python main.py <命令> [参数]
   
   可用命令：
     check <路径>              检查文件加密状态
     unlock <路径>             解密文件
     scan <目录>               扫描目录
     batch-unlock <文件列表>   批量解密
     --help                    显示帮助信息
     --version                 显示版本信息

3. 兼容旧版用法：
   python main.py <文件路径>

示例：
   python main.py check file.txt
   python main.py unlock file.txt --recursive
   python main.py scan /path/to/directory
   python main.py batch-unlock file1.txt file2.txt

更多信息请使用 --help 参数查看详细帮助。
    """)


def main():
    """主函数"""
    config_manager = None
    logger = None
    
    try:
        # 初始化配置和日志
        config_manager = get_config_manager()
        logger = get_logger()
        
        logger.info("程序启动")
        
        # 检查命令行参数
        if len(sys.argv) > 1:
            first_arg = sys.argv[1].lower()
            
            # 帮助和版本信息
            if first_arg in ('-h', '--help', 'help'):
                print_usage()
                return
            elif first_arg in ('-v', '--version', 'version'):
                print("YST5.1 文件加密检测与解密工具 v6.0")
                return
            
            # 检查是否是模块化命令
            if first_arg in ('check', 'unlock', 'scan', 'batch-unlock'):
                # 使用新的命令行接口
                run_cli()
            else:
                # 兼容旧版用法：直接处理文件路径
                logger.info("使用兼容模式处理文件")
                
                paths = sys.argv[1:]
                for path in paths:
                    if os.path.exists(path):
                        # 检查文件
                        result = check_file_encryption_with_feedback(path)
                        print(f"{result['status']}: {path}")
                        logger.info(f"{result['status']}: {path}")
                        
                        # 如果是加密文件，尝试解密
                        if result['status_code'] == 1:
                            print(f"尝试解密: {path}")
                            logger.info(f"尝试解密: {path}")
                            
                            program_path = config_manager.get_settings().get('wps_path')
                            decrypted_path = open_and_process_file(path, program_path)
                            
                            if decrypted_path:
                                print(f"解密成功: {decrypted_path}")
                                logger.info(f"解密成功: {path} -> {decrypted_path}")
                                
                                # 复核结果
                                verify_result = check_file_encryption_with_feedback(decrypted_path)
                                if verify_result['status_code'] == 0:
                                    print("复核成功: 文件未加密")
                                    logger.info(f"复核成功: {decrypted_path}")
                                else:
                                    print("复核警告: 文件可能仍为加密状态")
                                    logger.warning(f"复核警告: {decrypted_path}")
                            else:
                                print("解密失败")
                                logger.error(f"解密失败: {path}")
                        elif result['status_code'] == 0:
                            print("文件未加密，跳过解密")
                            logger.info(f"文件未加密，跳过解密: {path}")
                        else:
                            print("文件未识别，跳过处理")
                            logger.warning(f"文件未识别，跳过处理: {path}")
                    else:
                        print(f"文件不存在: {path}")
                        logger.error(f"文件不存在: {path}")
        else:
            # 没有参数，启动图形界面
            logger.info("启动图形界面")
            run_gui()
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        if logger:
            logger.info("程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
        if logger:
            logger.error(f"程序运行出错: {e}")
        
        # 在调试模式下显示详细错误信息
        if config_manager and config_manager.get_settings().get('debug', False):
            import traceback
            traceback.print_exc()
    finally:
        if logger:
            logger.info("程序结束")


if __name__ == "__main__":
    main()