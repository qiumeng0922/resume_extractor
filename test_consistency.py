#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试结果一致性脚本
对比 7.LLM_resume_filter 直接运行和 backend.py Web接口的结果
"""

import json
import requests
import subprocess
import time
import os

def run_llm_filter():
    """运行 7.LLM_resume_filter/resume_filter.py"""
    print("=" * 80)
    print("🔍 测试1: 运行 7.LLM_resume_filter/resume_filter.py")
    print("=" * 80)
    
    os.chdir("/Users/ameng/Documents/projects/11.AI简历可行性评估/7.LLM_resume_filter")
    
    result = subprocess.run(
        ["python3", "resume_filter.py"],
        capture_output=True,
        text=True
    )
    
    # 读取输出结果
    with open("筛选结果.json", "r", encoding="utf-8") as f:
        results = json.load(f)
    
    print(f"✅ 完成，共 {len(results)} 条结果")
    
    # 提取简历2的结果
    resume2_result = None
    for r in results:
        if r.get("简历序号") == "2":
            resume2_result = r
            break
    
    if resume2_result:
        print(f"\n📋 简历2(张明)的筛选结果:")
        print(f"   通过: {resume2_result.get('通过', False)}")
        print(f"   未通过原因: {resume2_result.get('未通过原因', [])}")
    
    return results, resume2_result

def test_backend_api():
    """测试 backend.py Web接口"""
    print("\n" + "=" * 80)
    print("🔍 测试2: 通过 Web接口调用 backend.py")
    print("=" * 80)
    
    url = "http://127.0.0.1:8000/api/screen"
    
    # 准备文件
    resume_file_path = "/Users/ameng/Documents/projects/11.AI简历可行性评估/2.（现RPA小工具流程）简历导入多行表/（现RPA小工具流程）简历导入多行表-系统架构师_20260116_v2.xlsx"
    position_file_path = "/Users/ameng/Documents/projects/11.AI简历可行性评估/5.界面/条件较为简单+多行表/条件要求较简单的部分岗位岗位要求-模拟数据.xlsx"
    
    files = {
        'resume_file': open(resume_file_path, 'rb'),
        'position_file': open(position_file_path, 'rb')
    }
    
    try:
        response = requests.post(url, files=files, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("success"):
            data = result.get("data", [])
            print(f"✅ 完成，共 {len(data)} 条结果")
            
            # 提取简历2的结果
            resume2_result = None
            for r in data:
                if r.get("序号") == 2 or r.get("序号") == "2":
                    if r.get("姓名") == "张明":
                        resume2_result = r
                        break
            
            if resume2_result:
                print(f"\n📋 简历2(张明)的筛选结果:")
                print(f"   AI初筛结果: {resume2_result.get('AI初筛结果', '')}")
                print(f"   淘汰原因: {resume2_result.get('淘汰原因', '')}")
                
                # 查看工作经历筛选详情
                for detail in resume2_result.get('筛选条件详情', []):
                    if detail.get('筛选条件') == '工作经历':
                        print(f"   工作经历判断: {detail.get('是否通过', '')}")
                        print(f"   原因说明: {detail.get('原因说明', '')}")
            
            return data, resume2_result
        else:
            print(f"❌ 请求失败: {result.get('message', '未知错误')}")
            return None, None
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return None, None
    finally:
        files['resume_file'].close()
        files['position_file'].close()

def compare_results(llm_result, backend_result):
    """对比两个结果"""
    print("\n" + "=" * 80)
    print("📊 结果对比")
    print("=" * 80)
    
    if not llm_result or not backend_result:
        print("❌ 无法对比，某个结果为空")
        return
    
    # 对比简历2的结果
    llm_passed = llm_result.get('通过', False)
    backend_passed = backend_result.get('AI初筛结果', '') == '拟通过'
    
    print(f"\n简历2(张明)的筛选结果对比:")
    print(f"  7.LLM_resume_filter: {'✅ 通过' if llm_passed else '❌ 不通过'}")
    print(f"  backend.py Web接口: {'✅ 通过' if backend_passed else '❌ 不通过'}")
    
    if llm_passed == backend_passed:
        print(f"\n🎉 结果一致! 两次运行的结果相同")
    else:
        print(f"\n⚠️  结果不一致! 需要进一步调查")
        print(f"\n可能原因:")
        print(f"  1. LLM的随机性(temperature设置)")
        print(f"  2. 数据来源不同")
        print(f"  3. 筛选逻辑版本不同")

if __name__ == "__main__":
    print("🚀 开始测试结果一致性...\n")
    
    # 测试1: 运行 7.LLM_resume_filter
    llm_results, llm_resume2 = run_llm_filter()
    
    # 等待一下
    time.sleep(2)
    
    # 测试2: 调用 backend.py Web接口
    backend_results, backend_resume2 = test_backend_api()
    
    # 对比结果
    compare_results(llm_resume2, backend_resume2)
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)
