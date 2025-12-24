"""
命令行接口模块
"""
import sys
from pathlib import Path

from .gui import run_gui


def main():
    """主入口 - 启动GUI"""
    print("正在启动 SysY编译器测试框架...")
    run_gui()


if __name__ == "__main__":
    main()
