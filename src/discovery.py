"""
测试用例发现模块
"""
from pathlib import Path
from typing import List

from .models import TestCase


class TestDiscovery:
    """测试用例发现器"""
    
    @staticmethod
    def discover_in_dir(test_dir: Path) -> List[TestCase]:
        """
        发现目录下的所有测试用例
        统一格式: testfile1.txt, input1.txt (或 testfile2.txt, input2.txt ...)
        """
        file_cases = []
        
        for testfile in test_dir.glob("testfile*.txt"):
            num_str = testfile.stem.replace("testfile", "")
            if num_str:
                try:
                    num = int(num_str)
                    input_file = test_dir / f"input{num}.txt"
                    file_cases.append((num, TestCase(
                        name=testfile.name,
                        testfile=testfile,
                        input_file=input_file if input_file.exists() else None
                    )))
                except ValueError:
                    pass
        
        file_cases.sort(key=lambda x: x[0])
        return [tc for _, tc in file_cases]
    
    @staticmethod
    def discover_test_libs(testfiles_dir: Path) -> List[Path]:
        """
        发现所有测试库目录（叶子目录，即直接包含 testfile*.txt 的目录）
        支持任意深度的嵌套目录结构
        """
        test_libs = []
        
        if not testfiles_dir.exists():
            return test_libs
        
        def find_test_dirs(directory: Path):
            """递归查找包含测试文件的叶子目录"""
            has_direct_testfiles = list(directory.glob("testfile*.txt"))
            
            if has_direct_testfiles:
                test_libs.append(directory)
            else:
                for subdir in sorted(directory.iterdir()):
                    if subdir.is_dir():
                        find_test_dirs(subdir)
        
        for item in sorted(testfiles_dir.iterdir()):
            if item.is_dir():
                find_test_dirs(item)
        
        return test_libs
    
    @staticmethod
    def get_next_testfile_number(test_dir: Path) -> int:
        """获取下一个测试文件编号"""
        max_num = 0
        for testfile in test_dir.glob("testfile*.txt"):
            num_str = testfile.stem.replace("testfile", "")
            if num_str:
                try:
                    num = int(num_str)
                    max_num = max(max_num, num)
                except ValueError:
                    pass
        return max_num + 1
