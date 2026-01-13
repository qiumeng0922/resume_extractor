# -*- coding: utf-8 -*-
"""
AI简历初筛后端服务
FastAPI 后端服务 - 处理简历初筛请求
功能：
1. 接收上传的两个 Excel 文件
2. 调用解析脚本转换为 JSON
3. 模拟 AI 初筛并返回结果
"""
import os
import json
import shutil
import tempfile
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 导入现有的解析脚本
import sys
sys.path.append(os.path.dirname(__file__))

# 导入解析函数
from detect_merged_cells_with_accuracy import parse_excel_to_multirow_json
from detect_merged_cells_with_accuracy_position_adjust import parse_excel_to_position_json

app = FastAPI(title="AI简历初筛系统", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def simulate_screening(resumes_data: list, positions_data: list) -> list:
    """
    模拟 AI 简历初筛逻辑
    这里使用简单的规则模拟,实际项目中应该接入真实的 AI 筛选逻辑
    """
    results = []
    
    for idx, resume in enumerate(resumes_data, 1):
        # 提取简历基本信息
        basic_info = resume.get("基本信息", {})
        education_info = resume.get("学习经历统计信息", {})
        work_info = resume.get("工作经历统计信息", {})
        position_info = resume.get("岗位信息", {})
        
        # 构建关键画像
        name = basic_info.get("姓名", "未知")
        education = education_info.get("最高学历", "")
        school = education_info.get("最高学历毕业院校", "")
        
        # 计算年龄
        age_str = basic_info.get("出生日期", "")
        age = "N/A"
        if age_str:
            try:
                from datetime import datetime
                birth_year = int(str(age_str).split("-")[0]) if "-" in str(age_str) else int(str(age_str)[:4])
                age = datetime.now().year - birth_year
            except:
                age = "N/A"
        
        current_company = basic_info.get("现工作单位", "")
        apply_position = position_info.get("应聘岗位", "")
        
        key_profile = f"{education} | {school} | {age}岁\n现任：{current_company}"
        
        # 简单的筛选逻辑
        is_passed = True
        reject_reason = ""
        
        # 1. 检查回避原则
        if basic_info.get("是否满足回避原则", "").strip() == "否":
            is_passed = False
            reject_reason = "亲属回避未通过"
        
        # 2. 检查年龄 (假设超过 45 岁不通过)
        elif isinstance(age, int) and age > 45:
            is_passed = False
            reject_reason = "年龄超出限制"
        
        # 3. 检查学历 (假设要求本科以上)
        elif education and education not in ["本科", "硕士", "博士"]:
            is_passed = False
            reject_reason = "学历不符合要求"
        
        # 4. 检查工作年限 (假设要求3年以上)
        elif work_info.get("系统内工作时长（年）"):
            try:
                years = float(work_info.get("系统内工作时长（年）", 0))
                if years < 3:
                    is_passed = False
                    reject_reason = "工作年限不足"
            except:
                pass
        
        result = {
            "序号": idx,
            "姓名": name,
            "关键画像": key_profile,
            "应聘岗位": apply_position,
            "AI初筛结果": "拟通过" if is_passed else "拟淘汰",
            "淘汰原因": reject_reason
        }
        
        results.append(result)
    
    return results


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI简历初筛系统 API",
        "version": "1.0.0",
        "endpoints": {
            "/": "系统信息",
            "/health": "健康检查",
            "/api/screen": "简历初筛接口 (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "服务运行正常"}


@app.post("/api/screen")
async def screen_resumes(
    resume_file: UploadFile = File(..., description="简历导入多行表Excel文件"),
    position_file: UploadFile = File(..., description="岗位需求明细表Excel文件")
):
    """
    简历初筛接口
    接收两个 Excel 文件,返回筛选结果
    """
    temp_dir = None
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        # 保存上传的文件
        resume_path = os.path.join(temp_dir, resume_file.filename)
        position_path = os.path.join(temp_dir, position_file.filename)
        
        with open(resume_path, "wb") as f:
            shutil.copyfileobj(resume_file.file, f)
        
        with open(position_path, "wb") as f:
            shutil.copyfileobj(position_file.file, f)
        
        # 解析简历文件
        print(f"⏳ 正在解析简历文件: {resume_file.filename}")
        resumes_data = parse_excel_to_multirow_json(resume_path)
        
        if not resumes_data:
            raise HTTPException(status_code=400, detail="简历文件解析失败")
        
        print(f"✅ 简历解析完成，共 {len(resumes_data)} 条记录")
        
        # 解析岗位需求文件
        print(f"⏳ 正在解析岗位需求文件: {position_file.filename}")
        positions_data = parse_excel_to_position_json(position_path)
        
        if not positions_data:
            raise HTTPException(status_code=400, detail="岗位需求文件解析失败")
        
        print(f"✅ 岗位需求解析完成，共 {len(positions_data)} 个岗位")
        
        # 执行初筛
        print("⏳ 正在执行 AI 初筛...")
        screening_results = simulate_screening(resumes_data, positions_data)
        
        print(f"✅ 初筛完成，共处理 {len(screening_results)} 份简历")
        
        # 保存结果到文件（可选）
        output_path = os.path.join(os.path.dirname(__file__), "简历初筛结果.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(screening_results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 结果已保存到: {output_path}")
        
        # 返回结果
        return JSONResponse(content={
            "success": True,
            "message": "简历初筛完成",
            "data": screening_results,
            "statistics": {
                "total": len(screening_results),
                "passed": sum(1 for r in screening_results if r["AI初筛结果"] == "拟通过"),
                "rejected": sum(1 for r in screening_results if r["AI初筛结果"] == "拟淘汰")
            }
        })
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


@app.post("/")
async def screen_resumes_root(
    resume_file: UploadFile = File(...),
    position_file: UploadFile = File(...)
):
    """
    根路径的 POST 请求（兼容原有接口）
    """
    return await screen_resumes(resume_file, position_file)


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 AI简历初筛系统 - 后端服务")
    print("=" * 80)
    print("📍 服务地址: http://127.0.0.1:8000")
    print("📖 API 文档: http://127.0.0.1:8000/docs")
    print("=" * 80)
    print()
    
    # 启动服务
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )




