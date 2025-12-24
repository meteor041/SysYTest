"""
主应用类
"""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional

from ..config import get_config
from .test_tab import TestTab
from .editor_tab import EditorTab


class TestApp:
    """测试应用GUI"""
    
    def __init__(self):
        self.config = get_config()
        self.root = tk.Tk()
        self.root.title("SysY编译器测试框架")
        self.root.geometry(f"{self.config.gui.window_width}x{self.config.gui.window_height}")
        self.root.minsize(800, 600)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 共享状态
        self.test_dir = Path(__file__).parent.parent.parent.resolve()
        self.project_dir: Optional[Path] = None
        
        # 标签页引用
        self.test_tab: Optional[TestTab] = None
        self.editor_tab: Optional[EditorTab] = None
        
        # 构建界面
        self._build_ui()
        self._setup()
        
        # 定时检查消息队列
        self.root.after(100, self._process_queue)
    
    def _build_ui(self):
        """构建界面"""
        # 创建Notebook（标签页）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 标签页1: 测试运行
        test_frame = ttk.Frame(self.notebook)
        self.notebook.add(test_frame, text="  测试运行  ")
        self.test_tab = TestTab(test_frame, self)
        self.test_tab.build()
        
        # 标签页2: 用例编写
        editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(editor_frame, text="  用例编写  ")
        self.editor_tab = EditorTab(editor_frame, self)
        self.editor_tab.build()
    
    def _setup(self):
        """初始化设置"""
        self.test_tab.setup_default_project()
        self.editor_tab.refresh_libs(set_default=True)
    
    def _process_queue(self):
        """处理消息队列"""
        if self.test_tab:
            self.test_tab.process_queue()
        self.root.after(100, self._process_queue)
    
    def run(self):
        """运行应用"""
        self.root.mainloop()


def run_gui():
    """启动GUI"""
    app = TestApp()
    app.run()
