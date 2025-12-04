"""
图形界面模块

负责提供图形用户界面，包含：
- 主界面
- 设置界面
- 关于界面
- 文件选择和处理
- 结果显示
"""

import os
import sys
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Dict, Optional

# 尝试导入requests，如果失败则提供一个替代方案
try:
    import requests
    import json
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("警告: requests模块未安装，版本检测功能将不可用")
from .config import get_config_manager
from .encryption_detector import get_encryption_detector
from .file_processor import get_file_processor
from .logger import get_logger


class YSTApplication(tk.Tk):
    """YST文件加密检测与解密工具主界面"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化组件
        self.config_manager = get_config_manager()
        self.detector = get_encryption_detector()
        self.processor = get_file_processor()
        self.logger = get_logger()
        
        # 任务管理
        self.task_queue = queue.Queue()
        self.thread_pool = []
        self.max_threads = self.config_manager.get_settings().get('max_threads', 5)
        
        # 初始化界面
        self.setup_window()
        self.setup_styles()
        self.setup_main_frame()  # 先设置主界面
        self.setup_menu()  # 再设置菜单
        
        # 启动任务处理
        self.after(100, self.process_queue)
        
        self.logger.info("图形界面初始化完成")
    
    def setup_window(self) -> None:
        """设置窗口属性"""
        self.title("文件加密检测与解密工具 v5.1")
        self.geometry("800x600")
        self.resizable(True, True)
        self.configure(bg="#f0f0f0")
    
    def setup_styles(self) -> None:
        """设置界面样式"""
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=("Arial", 10), 
                           background="#90EE90", foreground="black")
        self.style.configure("TLabel", font=("Arial", 10), background="#f0f0f0")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabelFrame", font=("Arial", 10, "bold"), 
                           background="#f0f0f0")
    
    def setup_menu(self) -> None:
        """设置菜单栏"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # 主界面菜单
        menubar.add_command(label="主界面", command=self.show_main_frame)
        
        # 设置菜单
        menubar.add_command(label="设置", command=self.show_settings_frame)
        
        # 关于菜单
        menubar.add_command(label="关于", command=self.show_about_frame)
        
        # 退出菜单
        menubar.add_command(label="退出", command=self.quit)
    
    def clear_frames(self) -> None:
        """清除所有界面帧"""
        for frame_name in ['main_frame', 'settings_frame', 'about_frame']:
            frame = getattr(self, frame_name, None)
            if frame:
                frame.destroy()
                setattr(self, frame_name, None)
    
    def show_main_frame(self) -> None:
        """显示主界面"""
        self.setup_main_frame()
    
    def setup_main_frame(self) -> None:
        """设置主界面"""
        self.clear_frames()
        
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(self.main_frame, text="文件加密检测与解密工具", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # 文件选择区域
        self.setup_file_selection()
        
        # 操作按钮区域
        self.setup_action_buttons()
        
        # 结果显示区域
        self.setup_result_display()
    
    def setup_file_selection(self) -> None:
        """设置文件选择区域"""
        file_frame = ttk.Frame(self.main_frame)
        file_frame.pack(pady=10)
        
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=70)
        file_entry.pack(side=tk.LEFT, padx=5)
        
        browse_button = ttk.Button(file_frame, text="选择文件", 
                                 command=self.browse_file)
        browse_button.pack(side=tk.LEFT)
        
        dir_button = ttk.Button(file_frame, text="选择目录", 
                              command=self.browse_directory)
        dir_button.pack(side=tk.LEFT, padx=5)
    
    def setup_action_buttons(self) -> None:
        """设置操作按钮"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        check_button = ttk.Button(button_frame, text="检查加密状态", 
                                command=self.check_encryption)
        check_button.pack(side=tk.LEFT, padx=10)
        
        decrypt_button = ttk.Button(button_frame, text="解密文件", 
                                  command=self.decrypt_file)
        decrypt_button.pack(side=tk.LEFT, padx=10)
        
        clear_button = ttk.Button(button_frame, text="清空结果", 
                                command=self.clear_results)
        clear_button.pack(side=tk.LEFT, padx=10)
    
    def setup_result_display(self) -> None:
        """设置结果显示区域"""
        result_frame = ttk.LabelFrame(self.main_frame, text="检测结果", padding=15)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, height=20, 
                                 font=("Arial", 11), bg="white", fg="#333333")
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置颜色标签
        self.result_text.tag_config("info", foreground="#4CAF50")
        self.result_text.tag_config("warning", foreground="#FF5722")
        self.result_text.tag_config("error", foreground="#F44336")
        self.result_text.tag_config("success", foreground="#4CAF50")
        self.result_text.tag_config("debug", foreground="#9E9E9E")
        
        scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
    
    def show_settings_frame(self) -> None:
        """显示设置界面"""
        self.clear_frames()
        
        self.settings_frame = ttk.Frame(self)
        self.settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(self.settings_frame, text="设置", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # 扩展名管理
        self.setup_extension_settings()
        
        # 文件头管理
        self.setup_header_settings()
        
        # 保存按钮
        save_button = ttk.Button(self.settings_frame, text="保存配置", 
                               command=self.save_settings)
        save_button.pack(pady=20)
    
    def setup_extension_settings(self) -> None:
        """设置扩展名管理区域"""
        extension_frame = ttk.LabelFrame(self.settings_frame, 
                                       text="扩展名管理", padding=10)
        extension_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(extension_frame, text="添加标准扩展名:").pack(side=tk.LEFT)
        self.extension_var = tk.StringVar()
        extension_entry = ttk.Entry(extension_frame, textvariable=self.extension_var, 
                                 width=10)
        extension_entry.pack(side=tk.LEFT, padx=5)
        
        add_button = ttk.Button(extension_frame, text="添加", 
                              command=self.add_extension)
        add_button.pack(side=tk.LEFT, padx=5)
        
        view_button = ttk.Button(extension_frame, text="查看所有", 
                              command=self.view_extensions)
        view_button.pack(side=tk.LEFT, padx=5)
    
    def setup_header_settings(self) -> None:
        """设置文件头管理区域"""
        header_frame = ttk.LabelFrame(self.settings_frame, text="文件头管理", 
                                    padding=10)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(header_frame, text="文件头(HEX):").pack(side=tk.LEFT)
        self.header_var = tk.StringVar()
        header_entry = ttk.Entry(header_frame, textvariable=self.header_var, 
                               width=20)
        header_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(header_frame, text="类型:").pack(side=tk.LEFT)
        self.header_type_var = tk.StringVar()
        header_type_entry = ttk.Entry(header_frame, textvariable=self.header_type_var, 
                                    width=15)
        header_type_entry.pack(side=tk.LEFT, padx=5)
        
        add_button = ttk.Button(header_frame, text="添加", 
                              command=self.add_header)
        add_button.pack(side=tk.LEFT, padx=5)
        
        view_button = ttk.Button(header_frame, text="查看所有", 
                               command=self.view_headers)
        view_button.pack(side=tk.LEFT, padx=5)
    
    def show_about_frame(self) -> None:
        """显示关于界面"""
        self.clear_frames()
        
        self.about_frame = ttk.Frame(self)
        self.about_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(self.about_frame, text="关于", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # 版本信息
        version_frame = ttk.Frame(self.about_frame)
        version_frame.pack(pady=10)
        
        version_label = ttk.Label(version_frame, text="文件加密检测与解密工具 v5.1", 
                                font=("Arial", 12, "bold"))
        version_label.pack()
        
        # 版本检测按钮和信息
        check_frame = ttk.Frame(self.about_frame)
        check_frame.pack(pady=5)
        
        check_button = ttk.Button(check_frame, text="检查新版本", 
                                command=self.check_for_updates)
        check_button.pack(side=tk.LEFT, padx=5)
        
        self.update_status_var = tk.StringVar(value="点击检查新版本")
        status_label = ttk.Label(check_frame, textvariable=self.update_status_var, 
                                font=("Arial", 10), foreground="gray")
        status_label.pack(side=tk.LEFT, padx=10)
        
        # 关于信息
        info_text = """
功能：
1. 检测文件是否加密
2. 对加密文件进行解密
3. 支持批量处理文件和目录
4. 可扩展的文件类型识别机制
5. 模块化设计，便于集成和扩展
6. 在线版本检测功能

开发团队：YST技术团队
联系方式：support@yst.com
        """
        
        info_label = ttk.Label(self.about_frame, text=info_text, 
                             font=("Arial", 12), justify=tk.LEFT)
        info_label.pack(pady=20)
    
    def browse_file(self) -> None:
        """选择文件"""
        file_path = filedialog.askopenfilename(title="选择文件")
        if file_path:
            self.file_path.set(file_path)
            self.logger.debug(f"选择文件: {file_path}")
            
            # 记录操作日志
            try:
                from .logger import get_logger_manager
                logger_manager = get_logger_manager()
                
                # 获取文件信息
                file_size = None
                try:
                    file_size = os.path.getsize(file_path)
                except:
                    pass
                
                logger_manager.log_file_operation(
                    "文件选择", file_path, "成功", 
                    file_size=file_size
                )
            except Exception as e:
                self.logger.warning(f"记录操作日志失败: {e}")
    
    def browse_directory(self) -> None:
        """选择目录"""
        dir_path = filedialog.askdirectory(title="选择目录")
        if dir_path:
            self.file_path.set(dir_path)
            self.logger.debug(f"选择目录: {dir_path}")
            
            # 记录操作日志
            try:
                from .logger import get_logger_manager
                logger_manager = get_logger_manager()
                logger_manager.log_operation("目录选择", dir_path, "成功")
            except Exception as e:
                self.logger.warning(f"记录操作日志失败: {e}")
    
    def check_encryption(self) -> None:
        """检查加密状态"""
        path = self.file_path.get()
        if not path:
            messagebox.showwarning("警告", "请先选择文件或目录！")
            return
        
        self.clear_results()
        self.add_result(f"正在检查: {path}")
        
        # 记录操作开始
        try:
            from .logger import get_logger_manager
            logger_manager = get_logger_manager()
            logger_manager.log_operation("加密检测开始", path, "进行中")
        except Exception as e:
            self.logger.warning(f"记录操作日志失败: {e}")
        
        if os.path.isdir(path):
            # 扫描目录
            results = self.detector.scan_directory(path)
            encrypted_count = sum(1 for r in results if r['status_code'] == 1)
            total_count = len(results)
            
            # 记录操作结果
            try:
                logger_manager.log_operation(
                    "目录加密检测", path, "完成", 
                    f"总计{total_count}个文件，加密{encrypted_count}个"
                )
            except Exception as e:
                self.logger.warning(f"记录操作日志失败: {e}")
            
            for result in results:
                self.display_check_result(result)
        else:
            # 检查单个文件
            result = self.detector.get_detection_result(path)
            
            # 记录操作结果
            try:
                file_size = None
                try:
                    file_size = os.path.getsize(path)
                except:
                    pass
                
                logger_manager.log_file_operation(
                    "文件加密检测", path, result['status'], 
                    file_size=file_size, file_type=result.get('file_type')
                )
            except Exception as e:
                self.logger.warning(f"记录操作日志失败: {e}")
            
            self.display_check_result(result)
    
    def decrypt_file(self) -> None:
        """解密文件"""
        path = self.file_path.get()
        if not path:
            messagebox.showwarning("警告", "请先选择文件或目录！")
            return
        
        self.clear_results()
        self.add_result(f"正在解密: {path}")
        
        if os.path.isdir(path):
            # 批量处理目录中的文件
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.task_queue.put(('decrypt', file_path))
        else:
            # 处理单个文件
            self.task_queue.put(('decrypt', path))
    
    def process_queue(self) -> None:
        """处理任务队列"""
        try:
            # 启动新线程处理任务
            while len(self.thread_pool) < self.max_threads and not self.task_queue.empty():
                task_type, file_path = self.task_queue.get()
                
                if task_type == 'decrypt':
                    thread = threading.Thread(
                        target=self.process_decrypt_task,
                        args=(file_path,)
                    )
                else:
                    continue
                
                thread.start()
                self.thread_pool.append(thread)
            
            # 清理已完成的线程
            for thread in self.thread_pool:
                if not thread.is_alive():
                    self.thread_pool.remove(thread)
            
            # 继续检查队列
            self.after(100, self.process_queue)
            
        except Exception as e:
            self.logger.error(f"处理队列时出错: {e}")
            self.after(100, self.process_queue)
    
    def process_decrypt_task(self, file_path: str) -> None:
        """处理解密任务"""
        try:
            # 先检查文件加密状态
            result = self.detector.get_detection_result(file_path)
            
            if result['status_code'] != 1:  # 不是加密文件
                self.after(0, lambda: self.add_result(
                    f"跳过非加密文件: {file_path} ({result['status']})", "info"
                ))
                
                # 记录跳过操作
                try:
                    from .logger import get_logger_manager
                    logger_manager = get_logger_manager()
                    logger_manager.log_file_operation(
                        "解密跳过", file_path, "非加密文件"
                    )
                except Exception as e:
                    self.logger.warning(f"记录操作日志失败: {e}")
                
                return
            
            # 尝试解密
            program_path = self.config_manager.get_settings().get('wps_path')
            decrypted_path = self.processor.process_encrypted_file(file_path, program_path)
            
            if decrypted_path:
                self.after(0, lambda: self.add_result(
                    f"解密成功: {file_path} -> {decrypted_path}", "success"
                ))
                
                # 复核解密结果
                verify_result = self.detector.get_detection_result(decrypted_path)
                
                if verify_result['status_code'] == 0:
                    # 复核成功，记录完整操作
                    self.after(0, lambda: self.add_result(
                        f"复核成功: 文件未加密", "success"
                    ))
                    
                    try:
                        from .logger import get_logger_manager
                        logger_manager = get_logger_manager()
                        
                        # 获取文件大小
                        file_size = None
                        try:
                            file_size = os.path.getsize(file_path)
                        except:
                            pass
                        
                        logger_manager.log_file_operation(
                            "文件解密", file_path, "成功并复核通过", 
                            file_size=file_size, file_type=result.get('file_type')
                        )
                        logger_manager.log_operation(
                            "解密复核", decrypted_path, "通过", "文件已成功解密"
                        )
                    except Exception as e:
                        self.logger.warning(f"记录操作日志失败: {e}")
                        
                else:
                    # 复核失败但仍记录解密操作
                    self.after(0, lambda: self.add_result(
                        f"复核警告: 文件可能仍为加密状态", "warning"
                    ))
                    
                    try:
                        from .logger import get_logger_manager
                        logger_manager = get_logger_manager()
                        
                        file_size = None
                        try:
                            file_size = os.path.getsize(file_path)
                        except:
                            pass
                        
                        logger_manager.log_file_operation(
                            "文件解密", file_path, "部分成功", 
                            file_size=file_size, file_type=result.get('file_type')
                        )
                        logger_manager.log_operation(
                            "解密复核", decrypted_path, "警告", "文件可能仍为加密状态"
                        )
                    except Exception as e:
                        self.logger.warning(f"记录操作日志失败: {e}")
            else:
                self.after(0, lambda: self.add_result(
                    f"解密失败: {file_path}", "error"
                ))
                
                # 记录解密失败
                try:
                    from .logger import get_logger_manager
                    logger_manager = get_logger_manager()
                    logger_manager.log_file_operation(
                        "文件解密", file_path, "失败"
                    )
                except Exception as e:
                    self.logger.warning(f"记录操作日志失败: {e}")
                
        except Exception as e:
            self.after(0, lambda: self.add_result(
                f"处理文件时出错: {file_path} - {e}", "error"
            ))
            
            # 记录处理异常
            try:
                from .logger import get_logger_manager
                logger_manager = get_logger_manager()
                logger_manager.log_operation(
                    "处理异常", file_path, "失败", f"错误: {str(e)}"
                )
            except Exception as log_e:
                self.logger.warning(f"记录操作日志失败: {log_e}")
    
    def display_check_result(self, result: Dict) -> None:
        """显示检查结果"""
        status_map = {
            '未加密': 'info',
            '已加密': 'warning',
            '未识别': 'warning',
            '文件不存在': 'error'
        }
        
        tag = status_map.get(result['status'], 'debug')
        message = f"{result['status']}: {result['file_path']}"
        self.add_result(message, tag)
    
    def add_result(self, message: str, tag: str = "debug") -> None:
        """添加结果到显示区域"""
        if hasattr(self, 'result_text'):
            self.result_text.insert(tk.END, f"{message}\n", tag)
            self.result_text.see(tk.END)
            self.update()
    
    def clear_results(self) -> None:
        """清空结果显示区域"""
        if hasattr(self, 'result_text'):
            self.result_text.delete(1.0, tk.END)
    
    def add_extension(self) -> None:
        """添加扩展名"""
        extension = self.extension_var.get().strip()
        if not extension:
            messagebox.showwarning("警告", "请输入要添加的扩展名！")
            return
        
        self.config_manager.add_extension(extension)
        self.extension_var.set("")
        messagebox.showinfo("成功", f"已添加扩展名: {extension}")
        self.logger.info(f"添加扩展名: {extension}")
    
    def add_header(self) -> None:
        """添加文件头"""
        header_hex = self.header_var.get().strip()
        file_type = self.header_type_var.get().strip()
        
        if not header_hex or not file_type:
            messagebox.showwarning("警告", "请输入文件头和文件类型！")
            return
        
        if self.config_manager.add_header(header_hex, file_type):
            self.header_var.set("")
            self.header_type_var.set("")
            messagebox.showinfo("成功", f"已添加文件头: {header_hex} ({file_type})")
            self.logger.info(f"添加文件头: {header_hex} ({file_type})")
        else:
            messagebox.showwarning("警告", "文件头格式无效，请输入有效的十六进制字符串！")
    
    def view_extensions(self) -> None:
        """查看所有扩展名"""
        extensions = self.config_manager.get_extensions()
        extensions_list = "\n".join(extensions) if extensions else "无"
        messagebox.showinfo("标准扩展名列表", f"当前支持的标准扩展名:\n\n{extensions_list}")
    
    def view_headers(self) -> None:
        """查看所有文件头"""
        headers = self.config_manager.get_headers()
        headers_list = "\n".join([f"{header.hex().upper()} ({file_type})" 
                                 for header, file_type in headers.items()])
        if not headers_list:
            headers_list = "无"
        messagebox.showinfo("标准文件头列表", f"当前支持的标准文件头:\n\n{headers_list}")
    
    def save_settings(self) -> None:
        """保存设置"""
        if self.config_manager.save_config():
            messagebox.showinfo("成功", "配置保存成功！")
            self.logger.info("配置保存成功")
        else:
            messagebox.showerror("错误", "配置保存失败！")
            self.logger.error("配置保存失败")
    
    def check_for_updates(self) -> None:
        """检查新版本"""
        if not REQUESTS_AVAILABLE:
            self.update_status_var.set("功能不可用")
            messagebox.showwarning("功能不可用", 
                "版本检测功能需要requests模块，请先安装：pip install requests")
            return
            
        def check_updates_thread():
            try:
                self.update_status_var.set("正在检查新版本...")
                self.logger.info("开始检查新版本")
                
                # 记录操作日志
                try:
                    from .logger import get_logger_manager
                    logger_manager = get_logger_manager()
                    logger_manager.log_operation("版本检查", "online", "进行中")
                except:
                    pass
                
                # 版本检查API（这里使用GitHub API作为示例）
                # 实际使用时需要替换为真实的版本检查接口
                api_url = "https://api.github.com/repos/YST-Team/file-encryption-tool/releases/latest"
                # 如果使用自己的服务器，可以替换为：
                # api_url = "https://your-server.com/api/version"
                
                # 设置请求超时
                response = requests.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    release_info = response.json()
                    latest_version = release_info.get('tag_name', '').lstrip('v')
                    download_url = release_info.get('html_url', '')
                    release_notes = release_info.get('body', '')
                    
                    current_version = "5.1"
                    
                    if self._compare_versions(latest_version, current_version) > 0:
                        # 有新版本
                        self.update_status_var.set("发现新版本！")
                        message = f"""发现新版本：{latest_version}

当前版本：{current_version}
最新版本：{latest_version}

更新说明：
{release_notes[:200]}...

是否前往下载页面？"""
                        
                        # 记录新版本发现
                        try:
                            logger_manager.log_operation(
                                "版本检查", "online", "发现新版本", 
                                f"当前: {current_version}, 最新: {latest_version}"
                            )
                        except:
                            pass
                        
                        # 在主线程中显示消息框
                        self.after(0, lambda: self.show_update_dialog(message, download_url))
                    else:
                        # 已是最新版本
                        self.update_status_var.set("已是最新版本")
                        self.after(0, lambda: messagebox.showinfo("版本检查", 
                            f"当前版本 {current_version} 已是最新版本！"))
                        
                        # 记录检查结果
                        try:
                            logger_manager.log_operation(
                                "版本检查", "online", "已是最新版本", 
                                f"当前版本: {current_version}"
                            )
                        except:
                            pass
                else:
                    # 网络请求失败
                    self.update_status_var.set("检查失败")
                    self.after(0, lambda: messagebox.showwarning("检查失败", 
                        f"无法连接到版本检查服务器，状态码：{response.status_code}"))
                    
                    # 记录检查失败
                    try:
                        logger_manager.log_operation(
                            "版本检查", "online", "失败", 
                            f"HTTP状态码: {response.status_code}"
                        )
                    except:
                        pass
                    
            except requests.exceptions.Timeout:
                self.update_status_var.set("检查超时")
                self.after(0, lambda: messagebox.showwarning("检查超时", 
                    "网络连接超时，请检查网络连接后重试。"))
                
                # 记录超时
                try:
                    logger_manager.log_operation("版本检查", "online", "超时", "网络连接超时")
                except:
                    pass
                    
            except requests.exceptions.ConnectionError:
                self.update_status_var.set("网络错误")
                self.after(0, lambda: messagebox.showwarning("网络错误", 
                    "网络连接错误，请检查网络连接。"))
                
                # 记录网络错误
                try:
                    logger_manager.log_operation("版本检查", "online", "网络错误", "连接失败")
                except:
                    pass
                    
            except Exception as e:
                self.update_status_var.set("检查失败")
                self.after(0, lambda: messagebox.showerror("检查失败", 
                    f"版本检查时发生错误：{str(e)}"))
                
                # 记录异常
                try:
                    logger_manager.log_operation(
                        "版本检查", "online", "异常", 
                        f"错误: {str(e)}"
                    )
                except:
                    pass
        
        # 在新线程中执行版本检查
        thread = threading.Thread(target=check_updates_thread, daemon=True)
        thread.start()
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """比较版本号
        Args:
            version1: 版本1
            version2: 版本2
        Returns:
            int: 0=相等, 1=version1>version2, -1=version1<version2
        """
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # 补齐长度
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            
            return 0
        except:
            return 0
    
    def show_update_dialog(self, message: str, download_url: str) -> None:
        """显示更新对话框"""
        result = messagebox.askyesno("发现新版本", message)
        if result and download_url:
            # 记录用户选择前往下载
            try:
                from .logger import get_logger_manager
                logger_manager = get_logger_manager()
                logger_manager.log_operation("版本更新", "download", "用户选择前往下载", 
                                           f"下载页面: {download_url}")
            except:
                pass
            
            # 打开下载链接（可选功能）
            try:
                import webbrowser
                webbrowser.open(download_url)
            except:
                messagebox.showinfo("下载链接", f"请手动访问以下链接下载新版本：\n{download_url}")


def run_gui() -> None:
    """运行图形界面"""
    try:
        app = YSTApplication()
        app.mainloop()
    except Exception as e:
        print(f"图形界面启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_gui()