# -*- coding: utf-8 -*-
"""
规整结果查看工具
快速查看指定岗位的规整前后对比
"""

import json
import sys


def display_qualification_field(record, field_name):
    """显示资格条件中的某个字段"""
    print(f"\n{'='*60}")
    print(f"【{field_name}】")
    print('='*60)
    
    for condition in record["资格条件"]:
        if field_name in condition:
            field_data = condition[field_name]
            
            # 获取原文
            original = ""
            adjusted = None
            for item in field_data:
                if isinstance(item, dict):
                    if "原文" in item:
                        original = item["原文"]
                    if "规整后" in item:
                        adjusted = item["规整后"]
            
            print(f"\n📄 原文:")
            if len(original) > 100:
                print(f"  {original[:100]}...")
                print(f"  {original[100:]}")
            else:
                print(f"  {original}")
            
            print(f"\n✨ 规整后:")
            print(f"  {json.dumps(adjusted, ensure_ascii=False, indent=4)}")
            break


def display_position_field(record, field_name):
    """显示岗位任职条件中的某个字段"""
    print(f"\n{'='*60}")
    print(f"【{field_name}】")
    print('='*60)
    
    for condition in record["岗位任职条件"]:
        if field_name in condition:
            field_data = condition[field_name]
            
            if field_name == "能力要求":
                print(f"\n能力要求 (数组，共 {len(field_data)} 项):")
                for idx, item in enumerate(field_data, 1):
                    print(f"  {idx}. {item}")
            else:
                # 获取原文和规整后
                original = ""
                adjusted = None
                for item in field_data:
                    if isinstance(item, dict):
                        if "原文" in item:
                            original = item["原文"]
                        if "规整后" in item:
                            adjusted = item["规整后"]
                
                print(f"\n📄 原文:")
                if len(original) > 100:
                    print(f"  {original[:100]}...")
                else:
                    print(f"  {original}")
                
                print(f"\n✨ 规整后:")
                print(f"  {adjusted}")
            break


def main():
    # 读取调整后的 JSON 文件
    try:
        with open('条件要求较简单的部分岗位岗位要求-模拟数据_调整后.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ 未找到文件: 条件要求较简单的部分岗位岗位要求-模拟数据_调整后.json")
        print("请先运行 adjust.py 生成调整后的文件")
        return
    
    print("=" * 80)
    print("📊 规整结果查看工具")
    print("=" * 80)
    print(f"总共 {len(data)} 条岗位记录")
    print()
    
    # 获取用户输入
    if len(sys.argv) > 1:
        try:
            position_idx = int(sys.argv[1]) - 1
        except ValueError:
            print("❌ 请输入有效的岗位序号（数字）")
            return
    else:
        try:
            position_idx = int(input("请输入要查看的岗位序号 (1-30): ")) - 1
        except ValueError:
            print("❌ 请输入有效的岗位序号（数字）")
            return
    
    if position_idx < 0 or position_idx >= len(data):
        print(f"❌ 岗位序号超出范围，请输入 1-{len(data)} 之间的数字")
        return
    
    record = data[position_idx]
    
    print(f"\n{'='*80}")
    print(f"【岗位 {record['序号']} - {record['岗位']}】")
    print(f"{'='*80}")
    print(f"单位: {record['二级单位']} > {record['三级单位']}")
    print(f"部门: {record['部门']}")
    print(f"工作地点: {record['工作地点']}")
    print(f"招聘人数: {record['招聘人数']}")
    
    # 显示资格条件
    print(f"\n{'#'*80}")
    print("一、资格条件")
    print('#'*80)
    
    display_qualification_field(record, "学历要求")
    display_qualification_field(record, "专业要求")
    display_qualification_field(record, "年龄要求")
    display_qualification_field(record, "绩效要求")
    display_qualification_field(record, "职称要求")
    display_qualification_field(record, "工作经历")
    
    # 显示岗位任职条件
    print(f"\n{'#'*80}")
    print("二、岗位任职条件")
    print('#'*80)
    
    display_position_field(record, "工作经验")
    display_position_field(record, "能力要求")
    
    # 检查是否有持证要求
    has_cert = False
    for condition in record["岗位任职条件"]:
        if "持证要求" in condition:
            has_cert = True
            break
    
    if has_cert:
        display_position_field(record, "持证要求")
    
    print(f"\n{'='*80}")
    print("✅ 查看完成")
    print("=" * 80)


if __name__ == "__main__":
    main()

