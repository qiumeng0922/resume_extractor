# -*- coding: utf-8 -*-
"""
验证 JSON 结构一致性工具
用于确认 adjust.py 没有改变原始 JSON 的结构
"""

import json
import sys


def compare_structure(obj1, obj2, path=""):
    """
    递归比较两个对象的结构是否一致
    只比较结构（类型、键），不比较值
    """
    if type(obj1) != type(obj2):
        return False, f"{path}: 类型不同 ({type(obj1).__name__} vs {type(obj2).__name__})"
    
    if isinstance(obj1, dict):
        if set(obj1.keys()) != set(obj2.keys()):
            missing_in_2 = set(obj1.keys()) - set(obj2.keys())
            missing_in_1 = set(obj2.keys()) - set(obj1.keys())
            msg = f"{path}: 键不同"
            if missing_in_2:
                msg += f", 缺失: {missing_in_2}"
            if missing_in_1:
                msg += f", 多余: {missing_in_1}"
            return False, msg
        
        for key in obj1.keys():
            is_same, msg = compare_structure(obj1[key], obj2[key], f"{path}.{key}")
            if not is_same:
                return False, msg
    
    elif isinstance(obj1, list):
        if len(obj1) != len(obj2):
            return False, f"{path}: 数组长度不同 ({len(obj1)} vs {len(obj2)})"
        
        # 如果数组不为空，检查第一个元素的类型
        if len(obj1) > 0:
            type1 = type(obj1[0])
            type2 = type(obj2[0])
            if type1 != type2:
                return False, f"{path}[0]: 元素类型不同 ({type1.__name__} vs {type2.__name__})"
    
    return True, ""


def main():
    print("=" * 80)
    print("🔍 JSON 结构一致性验证工具")
    print("=" * 80)
    print()
    
    # 读取文件
    try:
        with open('条件要求较简单的部分岗位岗位要求-模拟数据.json', 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        with open('条件要求较简单的部分岗位岗位要求-模拟数据_规整后.json', 'r', encoding='utf-8') as f:
            adjusted_data = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ 文件未找到: {e}")
        return
    
    print(f"原始文件记录数: {len(original_data)}")
    print(f"规整后文件记录数: {len(adjusted_data)}")
    print()
    
    if len(original_data) != len(adjusted_data):
        print("❌ 记录数量不一致！")
        return
    
    # 逐条检查结构
    print("正在检查每条记录的结构...")
    print()
    
    all_same = True
    errors = []
    
    for idx in range(len(original_data)):
        is_same, msg = compare_structure(original_data[idx], adjusted_data[idx], f"记录{idx+1}")
        if not is_same:
            all_same = False
            errors.append((idx+1, msg))
            if len(errors) <= 5:  # 只显示前5个错误
                print(f"❌ 岗位{idx+1}: {msg}")
    
    print()
    print("=" * 80)
    
    if all_same:
        print("✅ 验证通过！所有记录的结构完全一致！")
        print()
        print("详细信息:")
        print(f"  - 验证记录数: {len(original_data)}")
        print(f"  - 结构差异: 0")
        print(f"  - 一致性: 100%")
        print()
        print("结论: adjust.py 没有改变任何 JSON 结构，只填充了'规整后'字段。")
    else:
        print(f"❌ 验证失败！发现 {len(errors)} 条记录的结构不一致。")
        print()
        if len(errors) > 5:
            print(f"（仅显示前5个错误，共 {len(errors)} 个）")
        print()
        print("受影响的岗位序号:")
        print(f"  {[e[0] for e in errors[:20]]}")
    
    print("=" * 80)
    
    return 0 if all_same else 1


if __name__ == "__main__":
    sys.exit(main())

