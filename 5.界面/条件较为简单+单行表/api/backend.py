# -*- coding: utf-8 -*-
"""
AI简历初筛后端服务
FastAPI 后端服务 - 处理简历初筛请求
功能：
1. 接收上传的两个 Excel 文件
2. 调用解析脚本转换为 JSON
3. 直接调用 LLM 筛选模块进行筛选
"""
import os
import json
import shutil
import tempfile
import asyncio
import time
from typing import List
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 导入现有的解析脚本
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # 回到条件较为简单+单行表目录
sys.path.insert(0, parent_dir)

# 导入解析函数（从 parsers 目录）
from parsers.detect_merged_cells_with_accuracy_dan import parse_excel_to_single_row_json
from parsers.detect_merged_cells_with_accuracy_position_adjust import parse_excel_to_position_json

# 导入 LLM 筛选模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
llm_filter_path = os.path.join(project_root, "7.LLM_resume_filter")
sys.path.insert(0, llm_filter_path)

from core.screener import ResumeScreener
from managers.llm_manager import get_model_manager
from utils.logger_config import setup_logger

# 初始化日志
logger = setup_logger("backend_service")

app = FastAPI(title="AI简历初筛系统", version="2.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量：模型管理器和筛选器
model_manager = None
screener = None


@app.on_event("startup")
async def startup_event():
    """服务启动时初始化"""
    global model_manager, screener
    
    logger.info("🚀 正在初始化 AI 简历初筛服务...")
    
    # 获取LLM Studio模型管理器
    model_manager = get_model_manager()
    
    if model_manager:
        logger.info("✅ 已加载模型管理器，可以使用LLM进行筛选")
    else:
        logger.warning("⚠️  模型管理器未初始化，LLM筛选功能不可用")
    
    # 专业库路径
    major_library_path = os.path.join(llm_filter_path, "data/专业库.json")
    
    # 院校库路径
    school_library_path = os.path.join(llm_filter_path, "data/院校库.json")
    
    # 初始化筛选器
    screener = ResumeScreener(model_manager=model_manager, major_library_path=major_library_path, school_library_path=school_library_path)
    
    logger.info("✅ AI 简历初筛服务初始化完成")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI简历初筛系统",
        "version": "2.0.0",
        "llm_available": model_manager is not None,
        "endpoints": {
            "/": "系统信息",
            "/health": "健康检查",
            "/api/screen": "简历初筛接口 (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "message": "服务运行正常",
        "llm_available": model_manager is not None
    }


@app.post("/api/screen")
async def screen_resumes(
    resume_file: UploadFile = File(..., description="简历导入多行表Excel文件"),
    position_file: UploadFile = File(..., description="岗位需求明细表Excel文件")
):
    """
    简历初筛接口
    接收两个 Excel 文件,返回筛选结果
    
    注意：为确保结果一致性，岗位数据直接使用 7.LLM_resume_filter 中的JSON文件
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
        resumes_data = parse_excel_to_single_row_json(resume_path)
        
        if not resumes_data:
            raise HTTPException(status_code=400, detail="简历文件解析失败")
        
        print(f"✅ 简历解析完成，共 {len(resumes_data)} 条记录")
        
        # 保存解析后的JSON到data文件夹
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # 生成简历JSON文件名（基于上传的文件名）
        resume_json_filename = os.path.splitext(resume_file.filename)[0] + ".json"
        resume_json_path = os.path.join(data_dir, resume_json_filename)
        
        with open(resume_json_path, 'w', encoding='utf-8') as f:
            json.dump(resumes_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 简历JSON已保存到: {resume_json_path}")
        
        # 解析岗位文件
        print(f"⏳ 正在解析岗位文件: {position_file.filename}")
        positions_data = parse_excel_to_position_json(position_path)
        
        if not positions_data:
            raise HTTPException(status_code=400, detail="岗位文件解析失败")
        
        print(f"✅ 岗位解析完成，共 {len(positions_data)} 个岗位")
        
        # 生成岗位JSON文件名（基于上传的文件名）
        position_base_name = os.path.splitext(position_file.filename)[0]
        
        # 1. 保存原始文件名（包含原文和规整后）
        position_json_filename = position_base_name + ".json"
        position_json_path = os.path.join(data_dir, position_json_filename)
        
        with open(position_json_path, 'w', encoding='utf-8') as f:
            json.dump(positions_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 岗位JSON已保存到: {position_json_path}")
        
        # 2. 保存带"_规整后"后缀的文件名（同样包含原文和规整后）
        position_normalized_filename = position_base_name + "_规整后.json"
        position_normalized_path = os.path.join(data_dir, position_normalized_filename)
        
        with open(position_normalized_path, 'w', encoding='utf-8') as f:
            json.dump(positions_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 岗位JSON（规整后）已保存到: {position_normalized_path}")
        
        # 直接调用 LLM 筛选模块
        print("⏳ 正在执行 AI 筛选...")
        
        # 记录开始时间
        start_time = time.time()
        
        # 并发筛选所有岗位
        async def screen_job_with_info(job):
            """筛选单个岗位并返回结果"""
            job_name = job.get('岗位', f"岗位{job.get('序号', '未知')}")
            job_id = job.get('序号', 0)
            logger.info(f"[并发] 📌 开始筛选岗位 {job_id}: {job_name}")
            
            results = await screener.screen_batch(job, resumes_data, resume_file="上传文件")
            
            logger.info(f"[并发] ✅ 岗位 {job_name} 筛选完成，共 {len(results)} 份简历")
            return job, results
        
        # 并发执行所有岗位的筛选
        job_results_list = await asyncio.gather(*[screen_job_with_info(job) for job in positions_data])
        
        # 整理结果
        all_results = []
        for job, results in job_results_list:
            all_results.extend(results)
        
        # 调试信息
        logger.info(f"📊 总筛选结果数: {len(all_results)}")
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        # 构建输出结果
        screening_results = []
        
        # 创建一个已处理的简历集合（使用序号+姓名避免重复）
        processed_resumes = set()
        
        for result in all_results:
            resume_id = result.resume_id
            job_name_from_result = result.job_name
            
            logger.info(f"🔍 处理筛选结果: resume_id={resume_id}, job_name={job_name_from_result}")
            
            # 从 filter_details 中提取姓名（如果有的话）
            name_from_result = None
            if result.filter_details and len(result.filter_details) > 0:
                resume_info = result.filter_details[0].get('resume_info', '')
                # resume_info 格式: "序号=2 | 姓名=张三 | 学历=博士研究生 | 学校=清华大学"
                if '姓名=' in resume_info:
                    parts = resume_info.split('|')
                    for part in parts:
                        if '姓名=' in part:
                            name_from_result = part.split('姓名=')[1].strip()
                            break
            
            logger.info(f"   从结果中提取的姓名: {name_from_result}")
            
            # 从resumes列表中查找简历数据
            matching_resumes = [resume for resume in resumes_data if str(resume.get('序号', '')) == resume_id]
            
            logger.info(f"   找到 {len(matching_resumes)} 个匹配的简历记录")
            
            if not matching_resumes:
                logger.warning(f"⚠️  未找到简历数据：resume_id={resume_id}")
                continue
            
            # 找到正确的简历
            resume_data = None
            if len(matching_resumes) == 1:
                resume_data = matching_resumes[0]
                logger.info(f"   唯一匹配，直接使用")
            else:
                # 有多个相同序号的简历，通过姓名匹配
                logger.info(f"   多个匹配，通过姓名匹配: {name_from_result}")
                if name_from_result:
                    for resume in matching_resumes:
                        name = resume.get('基本信息', {}).get('姓名', '')
                        if name == name_from_result:
                            resume_data = resume
                            logger.info(f"     ✅ 找到匹配的简历: {name}")
                            break
                
                # 如果没找到，使用第一个未处理的
                if not resume_data:
                    logger.warning(f"   ⚠️  无法通过姓名匹配，使用第一个未处理的简历")
                    for resume in matching_resumes:
                        name = resume.get('基本信息', {}).get('姓名', '')
                        unique_key = f"{resume_id}_{name}"
                        if unique_key not in processed_resumes:
                            resume_data = resume
                            logger.info(f"     ✅ 使用未处理的简历: {name}")
                            break
                
                # 如果所有都处理过了，跳过
                if not resume_data:
                    logger.warning(f"   ⚠️  所有匹配的简历都已处理过，跳过")
                    continue
            
            # 标记为已处理
            name = resume_data.get('基本信息', {}).get('姓名', '')
            unique_key = f"{resume_id}_{name}"
            processed_resumes.add(unique_key)
            
            # 获取基本信息
            basic_info = resume_data.get('基本信息', {})
            name = basic_info.get('姓名', '')
            resume_number = resume_data.get('序号', '')
            
            # 获取岗位信息
            job_info = resume_data.get('岗位信息', {})
            applied_position = job_info.get('应聘岗位', '')
            
            # 获取学习经历统计信息
            education_info = resume_data.get('学习经历统计信息', {})
            highest_education = education_info.get('最高学历', '')
            highest_school = education_info.get('最高学历毕业院校', '')
            highest_school_type = education_info.get('最高学历毕业院校类型', '')
            
            # 计算年龄
            birth_date = basic_info.get('出生日期', '')
            age = ''
            if birth_date:
                try:
                    date_part = birth_date.split()[0] if ' ' in birth_date else birth_date
                    parts = date_part.split('-')
                    if len(parts) >= 1:
                        year = int(parts[0])
                        month = int(parts[1]) if len(parts) > 1 else 1
                        day = int(parts[2]) if len(parts) > 2 else 1
                        current_date = datetime.now()
                        age_calc = current_date.year - year
                        if (current_date.month, current_date.day) < (month, day):
                            age_calc -= 1
                        age = str(age_calc)
                except:
                    pass
            
            # 构建关键画像
            key_profile_parts = []
            if highest_education:
                key_profile_parts.append(highest_education)
            if highest_school:
                key_profile_parts.append(highest_school)
            if highest_school_type:
                key_profile_parts.append(highest_school_type)
            if age:
                key_profile_parts.append(f"{age}岁")
            
            key_profile = ' | '.join(key_profile_parts) if key_profile_parts else ''
            
            # 获取现职务或岗位
            current_position = basic_info.get('现职务或岗位', '')
            if current_position:
                key_profile += f"\n现任：{current_position}"
            
            # 构建AI初筛结果
            ai_result = "拟通过" if result.passed else "拟淘汰"
            
            # 构建淘汰原因
            failed_filters = [detail.get('filter_name') for detail in result.filter_details if not detail.get('passed')]
            elimination_reason = '/'.join(failed_filters) if failed_filters else ''
            
            # 构建筛选条件详情
            filter_details = []
            for detail in result.filter_details:
                filter_name = detail.get('filter_name', '')
                passed = detail.get('passed', False)
                method = detail.get('method', detail.get('source', '未知'))
                reason = detail.get('reason', '')
                
                # 获取筛选详情
                detail_info = detail.get('details', {})
                detail_text = ''
                if isinstance(detail_info, dict):
                    detail_text = detail_info.get('detail', '')
                
                # 格式化原因说明：去掉"原文"字段
                import re
                # 如果reason中包含requirement字典，去掉"原文"字段
                if "'原文'" in reason or '"原文"' in reason:
                    # 使用正则表达式去掉"原文"字段及其值，并处理多余的逗号
                    reason = re.sub(r"['\"]原文['\"]\s*:\s*[^,}]+,\s*", "", reason)  # 先处理后面有逗号的情况
                    reason = re.sub(r",?\s*['\"]原文['\"]\s*:\s*[^,}]+", "", reason)  # 再处理其他情况
                    # 清理可能留下的多余逗号和空格
                    reason = re.sub(r",\s*,", ",", reason)  # 去掉连续逗号
                    reason = re.sub(r"{\s*,", "{", reason)  # 去掉{后的逗号
                
                # 在筛选详情末尾添加逗号（如果detail_text不为空）
                if detail_text:
                    detail_text = detail_text.rstrip() + ','
                
                # 转换判断方法
                if method == 'rule' or '规则' in str(method):
                    method_display = '规则'
                elif method == 'llm' or 'LLM' in str(method):
                    method_display = 'LLM'
                else:
                    method_display = str(method)
                
                filter_detail = {
                    "筛选条件": filter_name,
                    "是否通过": "通过" if passed else "不通过",
                    "判断方法": method_display,
                    "原因说明": reason,
                    "筛选详情": detail_text
                }
                filter_details.append(filter_detail)
            
            # 构建输出记录
            output_record = {
                "序号": int(resume_number) if str(resume_number).isdigit() else resume_number,
                "姓名": name,
                "关键画像": key_profile,
                "应聘岗位": applied_position,
                "AI初筛结果": ai_result,
                "淘汰原因": elimination_reason,
                "筛选条件详情": filter_details
            }
            
            screening_results.append(output_record)
            logger.info(f"   ✅ 添加到结果列表")
        
        logger.info(f"📊 最终筛选结果数: {len(screening_results)}")
        
        # 按序号排序
        screening_results.sort(key=lambda x: x.get('序号', 0) if isinstance(x.get('序号'), (int, str)) and str(x.get('序号')).isdigit() else 0)
        
        # 统计信息
        total_passed = sum(1 for r in screening_results if r["AI初筛结果"] == "拟通过")
        total_count = len(screening_results)
        
        statistics = {
            "total": total_count,
            "passed": total_passed,
            "rejected": total_count - total_passed,
            "elapsed_time": f"{elapsed_time:.2f}秒"
        }
        
        print(f"✅ AI 初筛完成，共处理 {total_count} 份简历")
        print(f"   通过: {total_passed} 份")
        print(f"   淘汰: {total_count - total_passed} 份")
        print(f"   耗时: {elapsed_time:.2f}秒")
        
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
            "statistics": statistics
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
    print("💡 使用真实的 LLM 筛选引擎")
    print("=" * 80)
    print()
    
    # 启动服务
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )




