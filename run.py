# -*- coding: utf-8 -*-
"""
NeuroPrime 启动脚本

使用方法:
    python run.py

此脚本用于启动NeuroPrime主程序
"""

import sys
import traceback
from pathlib import Path

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加src到Python路径
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# 设置项目根目录环境变量，供scheduler使用
import os
os.environ['NEUROPRIME_ROOT'] = str(project_root)

try:
    # 导入并运行主程序
    from ui.main_window import main
    
    if __name__ == "__main__":
        main()
except Exception as e:
    print("=" * 60, file=sys.stderr)
    print("启动失败!", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"错误信息: {e}", file=sys.stderr)
    print("\n详细错误堆栈:", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    input("\n按回车键退出...")
