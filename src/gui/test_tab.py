"""
测试运行标签页
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
from typing import Optional, TYPE_CHECKING
import threading
import queue

from .base import BaseTab, OutputMixin
from ..discovery import TestDiscovery
from ..tester import CompilerTester

if TYPE_CHECKING:
    from .app import TestApp


class TestTab(BaseTab, OutputMixin):
    """测试运行标签页"""
    
    def __init__(self, parent: ttk.Frame, app: 'TestApp'):
        super().__init__(parent, app)
        self.tester: Optional[CompilerTester] = None
        self.is_running = False
        self.message_queue = queue.Queue()
        self.current_lib_path: Optional[Path] = None  # 记住当前选中的测试库
    
    def build(self):
        """构建测试运行标签页"""
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._build_config_section(main_frame)
        self._build_selection_section(main_frame)
        self._build_button_section(main_frame)
        self._build_progress_section(main_frame)
        self._build_output_section(main_frame)
    
    def _build_config_section(self, parent):
        """项目配置区"""
        config_frame = ttk.LabelFrame(parent, text="项目配置", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(config_frame, text="编译器项目:").pack(side=tk.LEFT)
        self.project_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.project_var, width=50).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(config_frame, text="浏览", command=self._browse_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(config_frame, text="编译项目", command=self._compile_project).pack(side=tk.LEFT)
    
    def _build_selection_section(self, parent):
        """测试选择区"""
        select_frame = ttk.Frame(parent)
        select_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 左侧：测试库列表
        left_frame = ttk.LabelFrame(select_frame, text="测试库", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.lib_listbox = tk.Listbox(
            left_frame, selectmode=tk.SINGLE, exportselection=False,
            font=(self.config.gui.get_font(), self.config.gui.font_size))
        self.lib_listbox.pack(fill=tk.BOTH, expand=True)
        self.lib_listbox.bind('<<ListboxSelect>>', self._on_lib_select)
        
        # 右侧：测试用例列表
        right_frame = ttk.LabelFrame(select_frame, text="测试用例", padding="5")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.case_listbox = tk.Listbox(
            right_frame, selectmode=tk.EXTENDED, exportselection=False,
            font=(self.config.gui.get_font(), self.config.gui.font_size))
        self.case_listbox.pack(fill=tk.BOTH, expand=True)

    def _build_button_section(self, parent):
        """按钮区"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="刷新", command=self.refresh_lists).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="全选", command=self._select_all_cases).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="运行选中", command=self._run_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="运行当前库", command=self._run_current_lib).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="运行全部", command=self._run_all).pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self._stop_test, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.RIGHT, padx=2)
    
    def _build_progress_section(self, parent):
        """进度和状态区"""
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(parent, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        self.result_var = tk.StringVar(value="")
        ttk.Label(status_frame, textvariable=self.result_var, 
                  font=('微软雅黑', 10, 'bold')).pack(side=tk.RIGHT)
    
    def _build_output_section(self, parent):
        """输出日志区"""
        output_frame = ttk.LabelFrame(parent, text="输出日志", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            font=(self.config.gui.get_font(), self.config.gui.font_size - 1),
            wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        self.output_text.tag_configure('pass', foreground='green')
        self.output_text.tag_configure('fail', foreground='red')
        self.output_text.tag_configure('info', foreground='blue')
        self.output_text.tag_configure('error', foreground='red', 
            font=(self.config.gui.get_font(), self.config.gui.font_size - 1, 'bold'))
    
    # ========== 事件处理 ==========
    
    def setup_default_project(self):
        """设置默认项目路径"""
        default_path = (self.test_dir / self.config.compiler_project_dir).resolve()
        if default_path.exists():
            self.project_var.set(str(default_path))
            self.app.project_dir = default_path
        self.refresh_lists()
    
    def _browse_project(self):
        """浏览选择项目目录"""
        path = filedialog.askdirectory(title="选择编译器项目目录")
        if path:
            self.project_var.set(path)
            self.app.project_dir = Path(path)
    
    def _compile_project(self):
        """编译项目（根据config.json自动选择语言）"""
        if not self.app.project_dir:
            messagebox.showerror("错误", "请先选择项目目录")
            return
        
        self.tester = CompilerTester(self.app.project_dir, self.test_dir)
        lang = self.tester.get_compiler_language().upper()
        self._log(f"正在编译{lang}项目...", 'info')
        
        def compile_task():
            success, msg = self.tester.compile_project()
            self.message_queue.put(('compile_done', success, msg))
        
        threading.Thread(target=compile_task, daemon=True).start()
    
    def refresh_lists(self):
        """刷新测试库列表"""
        self.lib_listbox.delete(0, tk.END)
        self.case_listbox.delete(0, tk.END)
        
        testfiles_dir = self.test_dir / "testfiles"
        libs = TestDiscovery.discover_test_libs(testfiles_dir)
        
        for lib in libs:
            rel_path = lib.relative_to(testfiles_dir)
            cases = TestDiscovery.discover_in_dir(lib)
            self.lib_listbox.insert(tk.END, f"{rel_path} ({len(cases)})")
        
        self._log(f"发现 {len(libs)} 个测试库", 'info')
    
    def _on_lib_select(self, event):
        """选择测试库时更新用例列表"""
        selection = self.lib_listbox.curselection()
        if not selection:
            return
        
        self.case_listbox.delete(0, tk.END)
        lib_name = self.lib_listbox.get(selection[0]).split(' (')[0]
        self.current_lib_path = self.test_dir / "testfiles" / lib_name
        
        cases = TestDiscovery.discover_in_dir(self.current_lib_path)
        for case in cases:
            self.case_listbox.insert(tk.END, case.name)
    
    def _select_all_cases(self):
        """全选测试用例"""
        self.case_listbox.select_set(0, tk.END)
    
    def _get_current_lib_path(self) -> Optional[Path]:
        """获取当前测试库路径"""
        return self.current_lib_path

    # ========== 测试运行 ==========
    
    def _run_selected(self):
        """运行选中的测试用例"""
        lib_path = self._get_current_lib_path()
        if not lib_path:
            messagebox.showwarning("提示", "请先选择测试库")
            return
        
        case_selection = self.case_listbox.curselection()
        if not case_selection:
            messagebox.showwarning("提示", "请选择要运行的测试用例")
            return
        
        all_cases = TestDiscovery.discover_in_dir(lib_path)
        selected_cases = [all_cases[i] for i in case_selection]
        self._run_tests(selected_cases, f"运行 {len(selected_cases)} 个选中测试")
    
    def _run_current_lib(self):
        """运行当前测试库的所有测试"""
        lib_path = self._get_current_lib_path()
        if not lib_path:
            messagebox.showwarning("提示", "请先选择测试库")
            return
        
        cases = TestDiscovery.discover_in_dir(lib_path)
        self._run_tests(cases, f"运行测试库: {lib_path.name}")
    
    def _run_all(self):
        """运行所有测试"""
        testfiles_dir = self.test_dir / "testfiles"
        libs = TestDiscovery.discover_test_libs(testfiles_dir)
        
        all_cases = []
        for lib in libs:
            cases = TestDiscovery.discover_in_dir(lib)
            for case in cases:
                case.name = f"{lib.name}/{case.name}"
            all_cases.extend(cases)
        
        self._run_tests(all_cases, f"运行所有测试 ({len(all_cases)} 个)")
    
    def _run_tests(self, cases: list, title: str):
        """运行测试（每次都重新编译，并行执行）"""
        if self.is_running:
            messagebox.showwarning("提示", "测试正在运行中")
            return
        
        if not self.app.project_dir:
            messagebox.showerror("错误", "请先选择项目目录")
            return
        
        self.is_running = True
        self.stop_btn.config(state=tk.NORMAL)
        self._clear_output()
        self.progress_var.set(0)
        self.result_var.set("")
        
        max_workers = self.config.parallel.max_workers
        self._log(f"=== {title} (并行: {max_workers} 线程) ===", 'info')
        
        def test_task():
            # 每次运行测试前都重新编译
            self.tester = CompilerTester(self.app.project_dir, self.test_dir)
            lang = self.tester.get_compiler_language().upper()
            self.message_queue.put(('status', f"正在编译{lang}项目..."))
            
            success, msg = self.tester.compile_project()
            if not success:
                self.message_queue.put(('compile_failed', msg))
                return
            
            self.message_queue.put(('compile_done', True, msg))
            
            if not self.is_running:
                self.message_queue.put(('stopped', 0, 0))
                return
            
            passed, failed = 0, 0
            
            def on_result(case, result, progress):
                nonlocal passed, failed
                if not self.is_running:
                    return
                
                if result.passed:
                    passed += 1
                    self.message_queue.put(('result', case.name, result, True))
                else:
                    failed += 1
                    self.message_queue.put(('result', case.name, result, False))
                
                self.message_queue.put(('progress', progress, f"已完成: {passed + failed}/{len(cases)}"))
            
            try:
                self.tester.test_parallel(cases, max_workers, callback=on_result)
            except Exception as e:
                self.message_queue.put(('error', str(e)))
                return
            
            if self.is_running:
                self.message_queue.put(('done', passed, failed))
            else:
                self.message_queue.put(('stopped', passed, failed))
        
        threading.Thread(target=test_task, daemon=True).start()
    
    def _stop_test(self):
        """停止测试"""
        self.is_running = False
    
    # ========== 消息处理 ==========
    
    def process_queue(self):
        """处理消息队列"""
        try:
            while True:
                msg = self.message_queue.get_nowait()
                
                if msg[0] == 'status':
                    _, status = msg
                    self.status_var.set(status)
                    self._log(status, 'info')
                
                elif msg[0] == 'compile_done':
                    _, success, text = msg
                    self._log(f"{'✓' if success else '✗'} {text}", 'pass' if success else 'error')
                
                elif msg[0] == 'compile_failed':
                    _, error_msg = msg
                    self._log(f"✗ 编译失败: {error_msg}", 'error')
                    self._finish_test(0, 0, stopped=True)
                
                elif msg[0] == 'progress':
                    _, progress, status = msg
                    self.progress_var.set(progress)
                    self.status_var.set(status)
                
                elif msg[0] == 'result':
                    _, name, result, passed = msg
                    if passed:
                        self._log(f"✓ {name}", 'pass')
                    else:
                        self._log_failure(
                            name=name,
                            status=result.status.value,
                            message=result.message or "",
                            actual=result.actual_output,
                            expected=result.expected_output
                        )
                
                elif msg[0] == 'error':
                    _, error_msg = msg
                    self._log(f"✗ 错误: {error_msg}", 'error')
                    self._finish_test(0, 0, stopped=True)
                
                elif msg[0] == 'done':
                    _, passed, failed = msg
                    self._finish_test(passed, failed)
                
                elif msg[0] == 'stopped':
                    _, passed, failed = msg
                    self._log("测试已停止", 'info')
                    self._finish_test(passed, failed, stopped=True)
                
        except queue.Empty:
            pass
    
    def _finish_test(self, passed: int, failed: int, stopped: bool = False):
        """完成测试"""
        self.is_running = False
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_var.set(100)
        
        total = passed + failed
        self.status_var.set("已停止" if stopped else "完成")
        
        if failed == 0:
            self.result_var.set(f"✓ 全部通过 ({passed}/{total})")
            self._log(f"\n=== 结果: {passed}/{total} 通过 ===", 'pass')
        else:
            self.result_var.set(f"✗ {failed} 个失败 ({passed}/{total})")
            self._log(f"\n=== 结果: {passed} 通过, {failed} 失败 ===", 'fail')
