#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算工具模块
"""

from datetime import datetime


class Calculator:
    """计算工具类"""
    
    @staticmethod
    def calculate_age(birth_date: str) -> int:
        """
        计算年龄
        支持格式：
        - "1998-05-10" (只有日期)
        - "1998-05-10 00:00:00" (日期+时间)
        """
        try:
            if isinstance(birth_date, str) and birth_date.strip():
                # 解析日期格式，支持 "1998-05-10" 或 "1998-05-10 00:00:00"
                date_part = birth_date.split()[0]  # 取日期部分
                parts = date_part.split("-")
                if len(parts) >= 1:
                    year = int(parts[0])
                    month = int(parts[1]) if len(parts) > 1 else 1
                    day = int(parts[2]) if len(parts) > 2 else 1
                    
                    # 计算年龄（考虑月份和日期）
                    current_date = datetime.now()
                    age = current_date.year - year
                    if (current_date.month, current_date.day) < (month, day):
                        age -= 1
                    return age
        except Exception as e:
            pass
        return 0
    
    @staticmethod
    def calculate_work_years(join_date: str) -> int:
        """计算工作年限"""
        try:
            if isinstance(join_date, str):
                date_part = join_date.split()[0]
                year = int(date_part.split("-")[0])
                month = int(date_part.split("-")[1])
                current_date = datetime.now()
                years = current_date.year - year
                if current_date.month < month:
                    years -= 1
                return max(0, years)
        except:
            pass
        return 0
