"""
GUI模块 - 向后兼容入口
实际实现已拆分到 src/gui/ 目录下
"""
from .gui import TestApp, run_gui

__all__ = ['TestApp', 'run_gui']
