"""
SysY编译器测试框架

用于测试SysY到MIPS编译器的自动化测试框架，
通过与g++编译运行结果对拍验证正确性。
"""

__version__ = "1.0.0"
__author__ = "BUAA Compiler Course"

from .config import Config, get_config
from .models import TestCase, TestResult, TestStatus
from .tester import CompilerTester
from .discovery import TestDiscovery

__all__ = [
    "Config",
    "get_config", 
    "TestCase",
    "TestResult",
    "TestStatus",
    "CompilerTester",
    "TestDiscovery",
]
