#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据加载工具模块
"""

import json
from typing import Dict, List


def load_job_data(file_path: str) -> List[Dict]:
    """加载岗位数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_resume_data(file_path: str) -> List[Dict]:
    """加载简历数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
