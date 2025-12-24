"""
GUI基础组件和工具类
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path
from typing import Optional
import queue

from ..config import get_config, Config
from ..utils import normalize_output


class BaseTab:
    """标签页基类"""
    
    def __init__(self, parent: ttk.Frame, app: 'TestApp'):
        self.parent = parent
        self.app = app
        self.config: Config = get_config()
        self.test_dir: Path = app.test_dir
    
    def build(self):
        """构建界面（子类实现）"""
        raise NotImplementedError


class OutputMixin:
    """输出日志功能混入"""
    
    output_text: scrolledtext.ScrolledText
    config: Config
    
    def _log(self, text: str, tag: str = None):
        """输出日志"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + '\n', tag if tag else ())
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def _log_failure(self, name: str, status: str, message: str, 
                     actual: str = None, expected: str = None, max_diff_lines: int = 10):
        """美观地输出失败信息"""
        self.output_text.config(state=tk.NORMAL)
        
        # 分隔线和标题
        self._log("─" * 60, 'fail')
        self._log(f"✗ 失败: {name}", 'error')
        self._log(f"  状态: {status}", 'fail')
        
        if message:
            self._log(f"  原因: {message}", 'fail')
        
        if actual is not None and expected is not None:
            actual_norm = normalize_output(actual)
            expected_norm = normalize_output(expected)
            actual_lines = actual_norm.split('\n')
            expected_lines = expected_norm.split('\n')
            
            # 输出行数统计
            self._log(f"  输出行数: 实际 {len(actual_lines)} 行, 期望 {len(expected_lines)} 行", 'info')
            
            # 找出差异行
            diff_lines = []
            max_len = max(len(actual_lines), len(expected_lines))
            for i in range(max_len):
                a = actual_lines[i] if i < len(actual_lines) else ""
                e = expected_lines[i] if i < len(expected_lines) else ""
                if a != e:
                    diff_lines.append((i + 1, a, e))
            
            if diff_lines:
                self._log(f"  差异行数: {len(diff_lines)}", 'fail')
                self._log("", None)
                self._log("  【差异详情】", 'info')
                
                for idx, (line_no, actual_line, expected_line) in enumerate(diff_lines[:max_diff_lines]):
                    self._log(f"  第 {line_no} 行:", 'fail')
                    
                    # 截断过长的行
                    actual_display = actual_line[:80] + ("..." if len(actual_line) > 80 else "")
                    expected_display = expected_line[:80] + ("..." if len(expected_line) > 80 else "")
                    
                    if actual_line == "":
                        self._log(f"    实际: <空行>", 'fail')
                    else:
                        self._log(f"    实际: {actual_display}", 'fail')
                    
                    if expected_line == "":
                        self._log(f"    期望: <空行>", 'pass')
                    else:
                        self._log(f"    期望: {expected_display}", 'pass')
                
                if len(diff_lines) > max_diff_lines:
                    self._log(f"  ... 还有 {len(diff_lines) - max_diff_lines} 处差异未显示", 'info')
        
        self._log("", None)
        self.output_text.config(state=tk.DISABLED)
    
    def _log_diff(self, actual: str, expected: str, max_lines: int = 5):
        """输出差异（简化版，保留兼容）"""
        actual_lines = normalize_output(actual).split('\n')
        expected_lines = normalize_output(expected).split('\n')
        
        diff_count = 0
        for i in range(max(len(actual_lines), len(expected_lines))):
            a = actual_lines[i] if i < len(actual_lines) else "<缺失>"
            e = expected_lines[i] if i < len(expected_lines) else "<缺失>"
            
            if a != e:
                diff_count += 1
                self._log(f"    行{i+1}: 实际='{a[:50]}' | 期望='{e[:50]}'", 'fail')
                if diff_count >= max_lines:
                    self._log(f"    ... 更多差异省略", 'fail')
                    break
    
    def _clear_output(self):
        """清空输出"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
