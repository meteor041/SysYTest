# SysY编译器测试框架

用于测试 SysY 到 MIPS 编译器的自动化测试框架，通过与 g++ 编译运行结果对拍验证正确性。

## 快速开始

```text
YourCodesFolder/
├── Compiler/
│   └── src/
│       ├── Compiler.java
│       └── config.json
└── SysYTest/   <- Put this folder here
    ├── config.yaml
    ├── README.md
    └── main.py
```

```bash
pip install pyyaml
python main.py
```

## 功能

- **测试运行**: 批量运行测试，实时显示进度和差异对比
- **用例编写**: 可视化编辑器，自动编号，快速保存
- **灵活配置**: YAML 配置文件

## 配置

编辑 `config.yaml`:

```yaml
compiler_project_dir: "../Compiler" # 或者绝对路径
```

## 测试用例格式

```
测试库/
├── testfile1.txt    # SysY 源代码
├── input1.txt       # 输入
└── ...
```

## 环境要求

- Python 3.7+ (tkinter, pyyaml)
- JDK 8+
- g++
