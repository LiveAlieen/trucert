# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

"""主入口文件

用于启动证书生成与管理工具的GUI应用程序
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.trucert.gui import MainWindow
from src.trucert.core.utils import initialize_dependencies


def main():
    """主函数，启动应用程序"""
    # 初始化依赖注入容器
    print("Initializing dependencies...")
    initialize_dependencies()
    print("Dependencies initialized successfully!")
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    
    # 显示主窗口
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
