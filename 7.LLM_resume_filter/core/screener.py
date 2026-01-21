#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主筛选器模块
"""

import asyncio
import time
from typing import Dict, List, Optional
from core.models import ScreeningResult
from core.toolkit import ResumeFilterToolkit
from utils.logger_config import setup_logger

logger = setup_logger("resume_screener")


def _format_time(seconds: float) -> str:
    """
    格式化时间显示，如果时间很短则显示毫秒
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串
    """
    milliseconds = seconds * 1000
    if milliseconds < 1:
        # 小于1毫秒，显示 "<1ms"
        return "<1ms"
    elif milliseconds < 10:
        # 小于10毫秒，显示毫秒（整数）
        return f"{milliseconds:.0f}ms"
    elif seconds < 1:
        # 小于1秒，显示毫秒（保留1位小数）
        return f"{milliseconds:.1f}ms"
    else:
        # 大于等于1秒，显示秒（保留2位小数）
        return f"{seconds:.2f}秒"


class ResumeScreener:
    """简历筛选器"""
    
    def __init__(self, model_manager=None, major_library_path: Optional[str] = None, school_library_path: Optional[str] = None):
        """
        初始化筛选器
        
        Args:
            model_manager: 模型管理器
            major_library_path: 专业库.json文件路径
            school_library_path: 院校库.json文件路径
        """
        self.toolkit = ResumeFilterToolkit(model_manager, major_library_path, school_library_path)
    
    async def screen_resume(self, job_data: Dict, resume_data: Dict, resume_index: int = None, resume_file: str = "简历-多行表.json") -> ScreeningResult:
        """
        筛选单个简历（异步方法，支持并发）
        
        Args:
            job_data: 岗位数据
            resume_data: 简历数据
            resume_index: 简历在列表中的索引（用于显示位置信息）
            resume_file: 简历文件名（用于显示位置信息）
        
        Returns:
            ScreeningResult
        """
        resume_id = resume_data.get("序号", "未知")
        job_id = job_data.get("序号", 0)
        job_name = job_data.get('岗位', '')
        
        # 记录开始时间
        start_time = time.time()
        logger.info(f"[并发] 🚀 开始筛选简历 {resume_id} 对岗位 {job_name} (线程ID: {id(asyncio.current_task())})")
        
        # 提取简历关键信息用于显示
        education_info = resume_data.get("学习经历统计信息", {})
        resume_info = self._format_resume_info(resume_data, education_info, resume_index, resume_file)
        
        # 执行所有筛选条件
        filter_results = []
        
        # 1. 学历要求
        filter_start = time.time()
        result1 = await self.toolkit.filter_education(job_data, resume_data)
        logger.debug(f"[并发] 简历 {resume_id} - 学历要求完成，耗时 {time.time() - filter_start:.2f}秒")
        method = result1.details.get("method", "规则匹配") if result1.details else "规则匹配"
        filter_results.append({
            "filter_name": "学历要求",
            "passed": result1.passed,
            "reason": result1.reason,
            "source": result1.source,
            "method": method,
            "details": result1.details,
            "resume_info": resume_info
        })
        
        # 2. 专业要求
        filter_start = time.time()
        result2 = await self.toolkit.filter_major(job_data, resume_data)
        logger.debug(f"[并发] 简历 {resume_id} - 专业要求完成，耗时 {time.time() - filter_start:.2f}秒")
        method2 = result2.details.get("method", "规则匹配") if result2.details else "规则匹配"
        filter_results.append({
            "filter_name": "专业要求",
            "passed": result2.passed,
            "reason": result2.reason,
            "source": result2.source,
            "method": method2,
            "details": result2.details,
            "resume_info": resume_info
        })
        
        # 3. 年龄要求
        filter_start = time.time()
        result3 = await self.toolkit.filter_age(job_data, resume_data)
        logger.debug(f"[并发] 简历 {resume_id} - 年龄要求完成，耗时 {time.time() - filter_start:.2f}秒")
        method3 = result3.details.get("method", "规则匹配") if result3.details else "规则匹配"
        filter_results.append({
            "filter_name": "年龄要求",
            "passed": result3.passed,
            "reason": result3.reason,
            "source": result3.source,
            "method": method3,
            "details": result3.details,
            "resume_info": resume_info
        })
        
        # 4. 绩效要求（异步方法，支持并发LLM调用）
        filter_start = time.time()
        result4 = await self.toolkit.filter_performance(job_data, resume_data)
        filter_time = time.time() - filter_start
        logger.info(f"[并发] 简历 {resume_id} - 绩效要求完成，耗时 {_format_time(filter_time)} (方法: {result4.source})")
        method4 = result4.details.get("method", result4.source) if result4.details else result4.source
        filter_results.append({
            "filter_name": "绩效要求",
            "passed": result4.passed,
            "reason": result4.reason,
            "source": result4.source,
            "method": method4,
            "details": result4.details,
            "resume_info": resume_info
        })
        
        # 5. 工作经历
        filter_start = time.time()
        result5 = await self.toolkit.filter_work_experience(job_data, resume_data)
        logger.debug(f"[并发] 简历 {resume_id} - 工作经历完成，耗时 {time.time() - filter_start:.2f}秒")
        method5 = result5.details.get("method", "规则匹配") if result5.details else "规则匹配"
        filter_results.append({
            "filter_name": "工作经历",
            "passed": result5.passed,
            "reason": result5.reason,
            "source": result5.source,
            "method": method5,
            "details": result5.details,
            "resume_info": resume_info
        })
        
        # 6. 工作经验
        filter_start = time.time()
        result6 = await self.toolkit.filter_work_years(job_data, resume_data)
        logger.debug(f"[并发] 简历 {resume_id} - 工作经验完成，耗时 {time.time() - filter_start:.2f}秒")
        method6 = result6.details.get("method", "规则匹配") if result6.details else "规则匹配"
        filter_results.append({
            "filter_name": "工作经验",
            "passed": result6.passed,
            "reason": result6.reason,
            "source": result6.source,
            "method": method6,
            "details": result6.details,
            "resume_info": resume_info
        })
        
        # 7. 政治面貌
        filter_start = time.time()
        result7 = await self.toolkit.filter_political_status(job_data, resume_data)
        logger.debug(f"[并发] 简历 {resume_id} - 政治面貌完成，耗时 {time.time() - filter_start:.2f}秒")
        method7 = result7.details.get("method", "规则匹配") if result7.details else "规则匹配"
        filter_results.append({
            "filter_name": "政治面貌",
            "passed": result7.passed,
            "reason": result7.reason,
            "source": result7.source,
            "method": method7,
            "details": result7.details,
            "resume_info": resume_info
        })
        
        # 8. 职称要求（异步方法，支持并发LLM调用）
        filter_start = time.time()
        result8 = await self.toolkit.filter_professional_title(job_data, resume_data)
        filter_time = time.time() - filter_start
        logger.info(f"[并发] 简历 {resume_id} - 职称要求完成，耗时 {_format_time(filter_time)} (方法: {result8.source})")
        method8 = result8.details.get("method", result8.source) if result8.details else result8.source
        filter_results.append({
            "filter_name": "职称要求",
            "passed": result8.passed,
            "reason": result8.reason,
            "source": result8.source,
            "method": method8,
            "details": result8.details,
            "resume_info": resume_info
        })
        
        # 判断是否通过（所有条件都必须通过）
        all_passed = all(r["passed"] for r in filter_results)
        
        # 生成总结
        failed_filters = [r for r in filter_results if not r["passed"]]
        if failed_filters:
            summary = f"不通过。未通过条件：{', '.join([f['filter_name'] for f in failed_filters])}"
        else:
            summary = "通过。所有硬性条件均符合要求"
        
        # 记录总耗时
        total_time = time.time() - start_time
        logger.info(f"[并发] ✅ 简历 {resume_id} 筛选完成，总耗时 {_format_time(total_time)}，结果: {'通过' if all_passed else '不通过'}")
        
        return ScreeningResult(
            resume_id=str(resume_id),
            job_id=job_id,
            job_name=job_name,
            passed=all_passed,
            filter_details=filter_results,
            summary=summary
        )
    
    async def screen_batch(self, job_data: Dict, resume_list: List[Dict], resume_file: str = "简历-多行表.json") -> List[ScreeningResult]:
        """
        批量筛选简历（只筛选应聘岗位匹配的简历，支持并发处理）
        
        Args:
            job_data: 岗位数据
            resume_list: 简历列表
            resume_file: 简历文件名（用于显示位置信息）
        
        Returns:
            List[ScreeningResult]
        """
        # 获取岗位名称
        job_name = job_data.get('岗位', '')
        job_id = job_data.get('序号', 0)
        
        # 筛选出应聘岗位匹配的简历
        matched_resumes = []
        for index, resume in enumerate(resume_list):
            # 获取简历中的应聘岗位
            job_info = resume.get('岗位信息', {})
            applied_position = job_info.get('应聘岗位', '')
            
            # 记录每次匹配尝试的详细信息
            logger.info(f"[匹配尝试] 岗位='{job_name}' vs 应聘岗位='{applied_position}' (简历序号: {resume.get('序号', '未知')})")
            
            # 检查是否匹配
            if self._match_position(job_name, applied_position):
                logger.info(f"✅ 岗位匹配：岗位='{job_name}' <-> 应聘岗位='{applied_position}' → 匹配")
                matched_resumes.append((index, resume))
            else:
                logger.debug(f"❌ 岗位不匹配：岗位='{job_name}' <-> 应聘岗位='{applied_position}' → 不匹配")
        
        logger.info(f"岗位：{job_name}：找到 {len(matched_resumes)} 份匹配的简历（总简历数：{len(resume_list)}）")
        
        # 并发筛选匹配的简历
        if not matched_resumes:
            return []
        
        # 记录并发开始时间
        batch_start_time = time.time()
        resume_ids = [str(resume.get("序号", "未知")) for _, resume in matched_resumes]
        logger.info(f"[并发] 🔄 开始并发筛选 {len(matched_resumes)} 份简历: {resume_ids}")
        
        # 使用 asyncio.gather 并发处理所有简历，并实时打印结果
        tasks = {
            asyncio.create_task(
                self.screen_resume(job_data, resume, resume_index=index, resume_file=resume_file)
            ): (index, resume)
            for index, resume in matched_resumes
        }
        
        logger.info(f"[并发] 📋 已创建 {len(tasks)} 个并发任务，开始执行...")
        
        # 实时打印每个完成的结果
        results = []
        for task in asyncio.as_completed(tasks.keys()):
            result = await task
            results.append(result)
            
            # 立即打印该简历的筛选结果
            print(f"\n简历 {result.resume_id} - 岗位 {result.job_name}: {result.summary}")
            for detail in result.filter_details:
                status = "✅通过" if detail['passed'] else "❌不通过"
                method = detail.get('method', detail['source'])
                detail_info = detail.get('details', {})
                
                # 提取筛选详情
                detail_text = ""
                if isinstance(detail_info, dict):
                    if 'detail' in detail_info:
                        detail_text = detail_info['detail']
                
                # 输出格式
                print(f"  {detail['filter_name']}: {status} [{method}]")
                if detail_text:
                    print(f"    筛选详情: {detail_text}")
                else:
                    print(f"    筛选详情: ")
            print()  # 空行分隔
        
        # 按原始顺序排序结果（保持一致性）
        results_dict = {r.resume_id: r for r in results}
        results = [results_dict.get(str(resume.get("序号", "未知")), None) for _, resume in matched_resumes]
        results = [r for r in results if r is not None]
        
        # 记录并发结束时间
        batch_time = time.time() - batch_start_time
        avg_time = batch_time / len(matched_resumes) if matched_resumes else 0
        logger.info(f"[并发] 🎉 并发筛选完成！{len(matched_resumes)} 份简历总耗时 {_format_time(batch_time)}，平均每份 {_format_time(avg_time)}")
        
        return list(results)
    
    def _match_position(self, job_name: str, applied_position: str) -> bool:
        """
        匹配岗位名称和应聘岗位（仅完全匹配，不进行包含匹配）
        
        Args:
            job_name: 岗位名称（来自岗位数据）
            applied_position: 应聘岗位（来自简历数据）
        
        Returns:
            是否匹配
        """
        # 去除首尾空格
        job_name = job_name.strip() if job_name else ""
        applied_position = applied_position.strip() if applied_position else ""
        
        # 如果任一为空，不匹配
        if not job_name or not applied_position:
            logger.debug(f"岗位匹配：岗位名称或应聘岗位为空，不匹配 (岗位='{job_name}', 应聘岗位='{applied_position}')")
            return False
        
        # 完全匹配
        matched = job_name == applied_position
        
        logger.debug(f"岗位匹配：岗位='{job_name}' vs 应聘岗位='{applied_position}' → {'匹配' if matched else '不匹配'}")
        return matched
    
    def _format_resume_info(self, resume_data: Dict, education_info: Dict, resume_index: int = None, resume_file: str = "简历-多行表.json") -> str:
        """
        格式化简历信息用于显示
        
        Args:
            resume_data: 简历数据
            education_info: 学习经历统计信息
            resume_index: 简历索引
            resume_file: 简历文件名
        
        Returns:
            格式化的简历信息字符串
        """
        resume_id = resume_data.get("序号", "未知")
        basic_info = resume_data.get("基本信息", {})
        name = basic_info.get("姓名", "未知")
        highest_education = education_info.get("最高学历", "")
        highest_school = education_info.get("最高学历毕业院校", "")
        
        info_parts = [f"序号={resume_id}", f"姓名={name}"]
        if highest_education:
            info_parts.append(f"学历={highest_education}")
        if highest_school:
            info_parts.append(f"学校={highest_school}")
        
        if resume_index is not None:
            info_parts.append(f"位置=第{resume_index+1}条")
        
        return " | ".join(info_parts)
    
    def _calculate_resume_line_range(self, resume_file: str, resume_index: int, resume_data: Dict) -> Optional[str]:
        """
        计算简历在JSON文件中的行号范围（用于调试）
        
        Args:
            resume_file: 简历文件名
            resume_index: 简历索引
            resume_data: 简历数据
        
        Returns:
            行号范围字符串，格式如 "100-200"
        """
        # 这里可以实现行号计算逻辑，暂时返回None
        return None
