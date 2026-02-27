# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

#!/usr/bin/env python3
"""
证书管理系统 Web 应用启动脚本
"""

import os
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.trucert.web.app import app

if __name__ == '__main__':
    print("=" * 60)
    print("证书管理系统 Web 应用")
    print("=" * 60)
    print("")
    print("访问地址: http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服务")
    print("")
    print("=" * 60)
    print("")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
