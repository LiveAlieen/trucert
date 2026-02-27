# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

import os

# 版权声明内容
copyright_header = """# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

"""

def add_copyright_to_file(file_path):
    """为单个文件添加版权声明"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查文件是否已经有版权声明
        if not content.startswith('# Copyright'):
            new_content = copyright_header + content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"已为文件添加版权声明: {file_path}")
        else:
            print(f"文件已包含版权声明: {file_path}")
    except Exception as e:
        print(f"处理文件时出错 {file_path}: {e}")

def main():
    """遍历所有Python文件并添加版权声明"""
    root_dir = "f:\\Users\\LiveA\\Desktop\\新建文件夹 (7)"
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                add_copyright_to_file(file_path)

if __name__ == "__main__":
    main()
