#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历筛选主流程
"""

import asyncio
import os
import time
from core.screener import ResumeScreener
from core.models import ScreeningResult
from managers.llm_manager import get_model_manager
from utils.data_loader import load_job_data, load_resume_data
from exporters.result_exporter import export_screening_results
from utils.logger_config import setup_logger

# 初始化日志
logger = setup_logger("resume_screener")


async def main():
    """主函数（异步）"""
    # 获取LLM Studio模型管理器
    model_mgr = get_model_manager()
    
    if model_mgr:
        logger.info("已加载模型管理器，可以使用LLM进行筛选")
    else:
        logger.warning("模型管理器未初始化，LLM筛选功能不可用")
    
    # 加载数据（使用新的简单岗位数据）
    jobs = load_job_data("./data/条件要求较简单的部分岗位岗位要求-模拟数据_规整后.json")
    resumes = load_resume_data("./data/（现RPA小工具流程）简历导入多行表-系统架构师.json")
    # 专业库路径（使用当前目录下的专业库.json）
    major_library_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./data/专业库.json")
    
    screener = ResumeScreener(model_manager=model_mgr, major_library_path=major_library_path)
    
    # 筛选所有岗位的所有简历
    if jobs and resumes:
        # 记录所有岗位并发筛选的开始时间
        all_jobs_start_time = time.time()
        logger.info(f"[并发] 🚀 开始并发筛选所有岗位，共 {len(jobs)} 个岗位")
        
        # 创建所有岗位的筛选任务（并发执行），并实时打印结果
        async def screen_job_with_info(job):
            """筛选单个岗位并返回岗位信息和结果，实时打印"""
            job_name = job.get('岗位', f"岗位{job.get('序号', '未知')}")
            job_id = job.get('序号', 0)
            logger.info(f"[并发] 📌 开始筛选岗位 {job_id}: {job_name}")
            
            # 打印岗位标题
            print(f"\n{'='*70}")
            print(f"筛选岗位：{job_name}")
            print(f"{'='*70}")
            
            results = await screener.screen_batch(job, resumes, resume_file="简历-多行表.json")
            
            # 统计并打印该岗位的结果
            passed_count = sum(1 for r in results if r.passed)
            total_count = len(results)
            
            if total_count == 0:
                print(f"\n⚠️  该岗位没有匹配的简历（没有简历的应聘岗位与此岗位匹配）")
            else:
                print(f"\n筛选完成：{passed_count}/{total_count} 份简历通过")
            
            logger.info(f"[并发] ✅ 岗位 {job_name} 筛选完成，共 {len(results)} 份简历")
            return job, results
        
        # 并发执行所有岗位的筛选，实时打印每个岗位的结果
        job_results_list = await asyncio.gather(*[screen_job_with_info(job) for job in jobs])
        
        # 记录所有岗位并发筛选的结束时间
        all_jobs_time = time.time() - all_jobs_start_time
        logger.info(f"[并发] 🎉 所有岗位并发筛选完成！{len(jobs)} 个岗位总耗时 {all_jobs_time:.2f}秒")
        
        # 整理结果（结果已经在筛选过程中实时打印了）
        all_results = []
        for job, results in job_results_list:
            all_results.extend(results)
        
        # 输出总体统计
        print(f"\n{'='*70}")
        print(f"总体统计")
        print(f"{'='*70}")
        total_passed = sum(1 for r in all_results if r.passed)
        total_count = len(all_results)
        print(f"总岗位数：{len(jobs)}")
        print(f"总简历数：{len(resumes)}")
        print(f"总筛选结果：{total_count}")
        print(f"总通过数：{total_passed}")
        print(f"总通过率：{total_passed/total_count*100:.1f}%" if total_count > 0 else "0%")
        
        # 导出筛选结果为JSON
        export_screening_results(all_results, jobs, resumes, output_file="筛选结果.json")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
