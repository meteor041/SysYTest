"""
用例编写标签页
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from datetime import datetime
from typing import TYPE_CHECKING

from .base import BaseTab
from ..discovery import TestDiscovery

if TYPE_CHECKING:
    from .app import TestApp


class EditorTab(BaseTab):
    """用例编写标签页"""
    
    def build(self):
        """构建用例编写标签页"""
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._build_dir_section(main_frame)
        self._build_editor_section(main_frame)
        self._build_button_section(main_frame)
    
    def _build_dir_section(self, parent):
        """目标目录选择区"""
        dir_frame = ttk.LabelFrame(parent, text="目标测试库", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dir_frame, text="保存到:").pack(side=tk.LEFT)
        self.editor_dir_var = tk.StringVar()
        self.editor_dir_combo = ttk.Combobox(dir_frame, textvariable=self.editor_dir_var, width=40)
        self.editor_dir_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(dir_frame, text="新建测试库", command=self._create_new_lib).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_frame, text="刷新", command=self.refresh_libs).pack(side=tk.LEFT)
    
    def _build_editor_section(self, parent):
        """编辑区"""
        edit_paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        edit_paned.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 左侧：源代码编辑
        code_frame = ttk.LabelFrame(edit_paned, text="SysY源代码 (testfile)", padding="5")
        edit_paned.add(code_frame, weight=3)
        
        self.code_text = scrolledtext.ScrolledText(
            code_frame, 
            font=(self.config.gui.get_font(), self.config.gui.font_size),
            wrap=tk.NONE, undo=True)
        self.code_text.pack(fill=tk.BOTH, expand=True)
        
        # 右侧：输入数据编辑
        input_frame = ttk.LabelFrame(edit_paned, text="输入数据 (input)", padding="5")
        edit_paned.add(input_frame, weight=1)
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame, 
            font=(self.config.gui.get_font(), self.config.gui.font_size),
            wrap=tk.NONE, undo=True)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(input_frame, text="每行一个整数", foreground='gray').pack(anchor=tk.W)
    
    def _build_button_section(self, parent):
        """操作按钮区"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X)
        
        self.editor_num_var = tk.StringVar(value="1")
        ttk.Label(btn_frame, text="编号:").pack(side=tk.LEFT)
        ttk.Entry(btn_frame, textvariable=self.editor_num_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="自动编号", command=self._auto_number).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="保存测试用例", command=self._save_testcase).pack(side=tk.LEFT, padx=20)
        ttk.Button(btn_frame, text="保存并新建下一个", command=self._save_and_next).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空", command=self._clear_editor).pack(side=tk.LEFT, padx=5)
        
        self.editor_status_var = tk.StringVar(value="")
        ttk.Label(btn_frame, textvariable=self.editor_status_var, foreground='green').pack(side=tk.RIGHT)

    # ========== 事件处理 ==========
    
    def refresh_libs(self, set_default: bool = False):
        """刷新测试库列表"""
        testfiles_dir = self.test_dir / "testfiles"
        libs = TestDiscovery.discover_test_libs(testfiles_dir)
        
        lib_names = [str(lib.relative_to(testfiles_dir)) for lib in libs]
        
        # 生成基于当前时间的默认目录名
        default_name = datetime.now().strftime("%Y%m%d_%H%M")
        if default_name not in lib_names:
            lib_names.insert(0, default_name)
        
        self.editor_dir_combo['values'] = lib_names
        
        if set_default or not self.editor_dir_var.get():
            self.editor_dir_combo.set(default_name)
    
    def _create_new_lib(self):
        """创建新测试库"""
        name = simpledialog.askstring("新建测试库", "请输入测试库名称:")
        if not name:
            return
        
        new_dir = self.test_dir / "testfiles" / name
        if new_dir.exists():
            messagebox.showerror("错误", f"测试库 '{name}' 已存在")
            return
        
        new_dir.mkdir(parents=True)
        self.refresh_libs()
        self.app.test_tab.refresh_lists()
        self.editor_dir_combo.set(name)
        self.editor_status_var.set(f"已创建: {name}")
    
    def _auto_number(self):
        """自动获取下一个编号"""
        lib_name = self.editor_dir_var.get()
        if not lib_name:
            messagebox.showwarning("提示", "请先选择测试库")
            return
        
        lib_path = self.test_dir / "testfiles" / lib_name
        next_num = TestDiscovery.get_next_testfile_number(lib_path)
        self.editor_num_var.set(str(next_num))
    
    def _save_testcase(self) -> bool:
        """保存测试用例"""
        lib_name = self.editor_dir_var.get()
        if not lib_name:
            messagebox.showwarning("提示", "请先选择测试库")
            return False
        
        try:
            num = int(self.editor_num_var.get())
        except ValueError:
            messagebox.showerror("错误", "编号必须是数字")
            return False
        
        code = self.code_text.get(1.0, tk.END).rstrip()
        if not code:
            messagebox.showwarning("提示", "请输入源代码")
            return False
        
        lib_path = self.test_dir / "testfiles" / lib_name
        lib_path.mkdir(parents=True, exist_ok=True)
        
        # 保存testfile
        testfile_path = lib_path / f"testfile{num}.txt"
        testfile_path.write_text(code, encoding='utf-8', newline='\n')
        
        # 保存input
        input_data = self.input_text.get(1.0, tk.END).rstrip()
        input_path = lib_path / f"input{num}.txt"
        input_path.write_text(input_data, encoding='utf-8', newline='\n')
        
        self.editor_status_var.set(f"已保存: testfile{num}.txt")
        self.app.test_tab.refresh_lists()
        return True
    
    def _save_and_next(self):
        """保存并新建下一个"""
        if self._save_testcase():
            try:
                num = int(self.editor_num_var.get())
                self.editor_num_var.set(str(num + 1))
            except ValueError:
                pass
            self._clear_editor()
    
    def _clear_editor(self):
        """清空编辑器"""
        self.code_text.delete(1.0, tk.END)
        self.input_text.delete(1.0, tk.END)
        self.editor_status_var.set("")
