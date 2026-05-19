#!/usr/bin/env python3
"""
修复模型文件中的注释问题
"""

import os
import re

models_dir = "d:/Client Projects/WxVinBot Por/backend/app/models"

def fix_file(filepath):
    """修复单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复错误的 String(..., comment="...") 格式
    # 将 String(length, comment="...") 改为 String(length)
    content = re.sub(
        r'String\((\d+),\s*comment="[^"]*"\)',
        r'String(\1)',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已修复: {os.path.basename(filepath)}")

# 处理所有模型文件
for filename in os.listdir(models_dir):
    if filename.endswith('.py') and filename not in ['__init__.py', 'base.py']:
        filepath = os.path.join(models_dir, filename)
        fix_file(filepath)

print("\n所有模型文件已修复！")
