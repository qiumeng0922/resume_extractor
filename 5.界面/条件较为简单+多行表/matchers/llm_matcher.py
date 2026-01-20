#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM匹配器模块
"""

import json
import re
import time
from typing import Dict, List, Optional
from utils.logger_config import setup_logger
from core.models import FilterResult

logger = setup_logger("llm_matcher")


class LLMMatcher:
    """LLM匹配器 - 所有LLM匹配逻辑"""
    
    def __init__(self, model_manager=None):
        """
        初始化LLM匹配器
        
        Args:
            model_manager: 模型管理器
        """
        self.model_manager = model_manager
    
    async def match_performance_llm(self, requirement, resume_data: Dict) -> FilterResult:
        """使用LLM匹配绩效要求（异步方法）"""
        if not self.model_manager:
            logger.warning("绩效筛选：模型管理器未初始化，无法使用LLM判断")
            return FilterResult(
                passed=True,
                reason="模型未初始化，无法使用LLM判断绩效要求",
                source="rule",
                details={"method": "规则匹配-模型未初始化"}
            )
        
        try:
            # 只提取绩效相关的字段
            performance_data = {}
            if "年度绩效情况" in resume_data:
                performance_data["年度绩效情况"] = resume_data["年度绩效情况"]
            
            # 如果绩效数据为空，但岗位有绩效要求，判定为不通过
            if not performance_data:
                logger.debug("绩效筛选：岗位有绩效要求，但简历中无绩效信息，判定为不通过")
                return FilterResult(
                    passed=False,
                    reason="岗位要求绩效，但简历中无绩效信息，不符合要求",
                    source="rule",
                    details={"method": "规则匹配-数据缺失"}
                )
            
            # 构建Prompt
            requirement_text = requirement.get("原文", str(requirement)) if isinstance(requirement, dict) else str(requirement)
            
            # 获取当前年份，用于明确"近3年"的定义
            from datetime import datetime
            current_year = datetime.now().year
            recent_3_years = f"{current_year-3}年、{current_year-2}年、{current_year-1}年"
            
            prompt = f"""
# 核心任务
仅做两件事：1. 判断简历是否符合绩效要求；2. 按指定格式输出，无任何其他操作。

# 重要时间定义
当前年份：{current_year}年
"近3年"特指：{recent_3_years}（共3个年度）
⚠️ 注意：只考虑这3个年度的绩效，其他年份的绩效不在判断范围内。

# 岗位绩效要求
{requirement_text}

# 简历绩效信息
{json.dumps(performance_data, ensure_ascii=False, indent=2)}

# 输出格式（生死规则，违反则输出无效）
1. 第一行：仅输出「通过」或「不通过」其中一个词，无空格、无标点、无其他字符；
2. 第二行：仅输出「原因：」+ 简要判断依据（50字内，紧扣规则和信息），无其他内容；
3. 仅输出上述两行，无空行、无额外文字、无注释。

# 强制禁令
- 禁止同时输出「通过」和「不通过」；
- 禁止将结果和原因写在同一行；
- 禁止编造未提及的绩效等级或要求；
- 禁止超出50字写原因。
- 禁止结果与原因矛盾（如原因说符合，结果却写不通过）
- 禁止将{recent_3_years}之外的年份纳入"近3年"的判断范围"""
 #           print(prompt)
            
            logger.debug("绩效筛选：使用LLM判断，开始调用模型")
            
            # 直接await异步的LLM调用
            llm_call_start = time.time()
            result_text = await self.model_manager.inference(prompt, enable_thinking=False)
            llm_call_time = time.time() - llm_call_start
            logger.debug(f"绩效筛选：LLM调用总耗时 {llm_call_time:.2f}秒")
            
            logger.debug(f"绩效筛选：LLM返回结果={result_text}")
            
            # 解析LLM结果
            passed = "通过" in result_text or "符合" in result_text
            if "不通过" in result_text or "不符合" in result_text:
                passed = False
            
            return FilterResult(
                passed=passed,
                reason=result_text,
                source="llm",
                details={
                    "method": "LLM判断",
                    "detail": f"使用LLM分析绩效要求，结果：{result_text}",
                    "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt
                }
            )
        except Exception as e:
            logger.error(f"绩效筛选：LLM调用失败，错误={str(e)}")
            return FilterResult(
                passed=True,
                reason=f"LLM调用失败：{str(e)}，默认通过",
                source="rule",
                details={"method": "规则匹配-LLM调用失败", "error": str(e)}
            )
    
    async def match_title_llm(self, requirement, resume_data: Dict) -> FilterResult:
        """使用LLM匹配职称要求（异步方法）"""
        if not self.model_manager:
            logger.warning("职称筛选：模型管理器未初始化，无法使用LLM判断")
            return FilterResult(
                passed=True,
                reason="模型未初始化，无法使用LLM判断职称要求",
                source="rule",
                details={"method": "规则匹配-模型未初始化"}
            )
        
        try:
            # 只提取职称相关的字段
            title_data = {}
            has_title_info = False
            
            # 检查职称证书
            if "职称证书" in resume_data:
                title_certs = resume_data["职称证书"]
                # 检查是否为空列表或None
                if title_certs and isinstance(title_certs, list) and len(title_certs) > 0:
                    title_data["职称证书"] = title_certs
                    has_title_info = True
            
            # 检查证书统计信息
            if "证书统计信息" in resume_data:
                cert_stats = resume_data["证书统计信息"]
                if cert_stats and isinstance(cert_stats, dict):
                    # 只提取职称相关的统计信息
                    title_stats = {}
                    if "职称等级（最高）" in cert_stats and cert_stats["职称等级（最高）"]:
                        title_stats["职称等级（最高）"] = cert_stats["职称等级（最高）"]
                        has_title_info = True
                    if "职称名称" in cert_stats and cert_stats["职称名称"]:
                        title_stats["职称名称"] = cert_stats["职称名称"]
                        has_title_info = True
                    if title_stats:
                        title_data["证书统计信息"] = title_stats
            
            # 如果简历中完全没有职称信息，但岗位有职称要求，判定为不通过
            if not has_title_info:
                logger.debug("职称筛选：岗位有职称要求，但简历中无职称信息，判定为不通过")
                return FilterResult(
                    passed=False,
                    reason="岗位要求职称，但简历中无职称信息，不符合要求",
                    source="rule",
                    details={"method": "规则匹配-数据缺失"}
                )
            
            # 构建Prompt
            requirement_text = ""
            if isinstance(requirement, list):
                requirement_text = "、".join(requirement)
            elif isinstance(requirement, dict) and "原文" in requirement:
                requirement_text = requirement["原文"]
            else:
                requirement_text = str(requirement)
            
            prompt = f"""
# 核心任务
仅做两件事：1. 判断简历是否符合岗位职称要求；2. 按指定格式输出，无任何其他操作。

# 岗位职称要求
{requirement_text}

# 简历职称信息
{json.dumps(title_data, ensure_ascii=False, indent=2)}

# 输出格式（生死规则，违反则输出无效）
1. 第一行：仅输出「通过」或「不通过」其中一个词，无空格、无标点、无其他字符；
2. 第二行：仅输出「原因：」+ 简要判断依据（50字内，紧扣规则和信息），无其他内容；
3. 仅输出上述两行，无空行、无额外文字、无注释。

# 强制禁令
- 禁止同时输出「通过」和「不通过」；
- 禁止将结果和原因写在同一行；
- 禁止编造未提及的岗位职称或要求；
- 禁止超出50字写原因。"""
            
            logger.debug("职称筛选：使用LLM判断，开始调用模型")
            
            # 直接await异步的LLM调用
            llm_call_start = time.time()
            try:
                result_text = await self.model_manager.inference(prompt, enable_thinking=False)
                llm_call_time = time.time() - llm_call_start
                logger.debug(f"职称筛选：LLM调用总耗时 {llm_call_time:.2f}秒")
            except Exception as e:
                logger.error(f"职称筛选：LLM调用异常，错误={str(e)}")
                # 如果是连接错误，返回默认通过
                if "连接" in str(e) or "Connection" in str(e):
                    return FilterResult(
                        passed=True,
                        reason=f"LLM服务连接失败：{str(e)}，默认通过",
                        source="rule",
                        details={"method": "规则匹配-LLM连接失败", "error": str(e)}
                    )
                raise
            
            logger.debug(f"职称筛选：LLM返回结果={result_text}")
            
            # 解析LLM结果
            passed = "通过" in result_text or "符合" in result_text
            if "不通过" in result_text or "不符合" in result_text:
                passed = False
            
            return FilterResult(
                passed=passed,
                reason=result_text,
                source="llm",
                details={
                    "method": "LLM判断",
                    "detail": f"使用LLM分析职称要求，结果：{result_text}",
                    "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt
                }
            )
        except Exception as e:
            logger.error(f"职称筛选：LLM调用失败，错误={str(e)}")
            return FilterResult(
                passed=True,
                reason=f"LLM调用失败：{str(e)}，默认通过",
                source="rule",
                details={"method": "规则匹配-LLM调用失败", "error": str(e)}
            )
    
    async def match_major_llm(self, requirement, major_names: List[str], resume_data: Dict) -> FilterResult:
        """使用LLM判断专业是否相关（异步方法）"""
        if not self.model_manager:
            logger.warning("专业筛选：模型管理器未初始化，无法使用LLM判断")
            return FilterResult(
                passed=True,
                reason="模型未初始化，无法使用LLM判断专业要求",
                source="rule",
                details={"method": "规则匹配-模型未初始化"}
            )
        
        try:
            # 提取岗位要求的专业列表
            required_majors = []
            if isinstance(requirement, dict):
                if "专业" in requirement:
                    required_majors = requirement.get("专业", [])
                elif "原文" in requirement:
                    # 如果只有原文，尝试提取专业类
                    requirement_text = requirement["原文"]
                    # 简单提取专业类（移除"类"和"相关专业"后缀）
                    majors = re.findall(r"([^，,、]+?)(?:类|相关专业)", requirement_text)
                    required_majors = [m.strip() for m in majors]
            
            if not required_majors:
                logger.warning("专业筛选：无法提取岗位专业要求，默认通过")
                return FilterResult(
                    passed=True,
                    reason="无法提取岗位专业要求，默认通过",
                    source="rule",
                    details={"method": "规则匹配-数据缺失"}
                )
            
            # 构建Prompt
            major_names_str = "、".join(major_names)
            required_majors_str = "、".join(required_majors)
            
            prompt = f"""
# 核心任务
仅做两件事：1. 判断简历专业是否与岗位要求的专业相关；2. 按指定格式输出，无任何其他操作。

# 岗位专业要求
{required_majors_str}

# 简历专业
{major_names_str}

# 判断标准
判断简历中的专业是否与岗位要求的专业类相关。如果简历专业属于岗位要求的专业类，或者与岗位要求的专业类在学科领域上相关，则判定为相关。

# 输出格式（生死规则，违反则输出无效）
1. 第一行：仅输出「通过」或「不通过」其中一个词，无空格、无标点、无其他字符；
2. 第二行：仅输出「原因：」+ 简要判断依据（50字内，说明专业是否相关），无其他内容；
3. 仅输出上述两行，无空行、无额外文字、无注释。

# 强制禁令
- 禁止同时输出「通过」和「不通过」；
- 禁止将结果和原因写在同一行；
- 禁止编造未提及的专业或专业类；
- 禁止超出50字写原因。
- 禁止结果与原因矛盾（如原因说相关，结果却写不通过）"""
            
            logger.debug("专业筛选：使用LLM判断，开始调用模型")
            result_text = await self.model_manager.inference(prompt, enable_thinking=False)
            logger.debug(f"专业筛选：LLM返回结果={result_text}")
            
            # 解析LLM结果
            passed = "通过" in result_text or "相关" in result_text or "符合" in result_text
            if "不通过" in result_text or "不相关" in result_text or "不符合" in result_text:
                passed = False
            
            return FilterResult(
                passed=passed,
                reason=result_text,
                source="llm",
                details={
                    "method": "LLM判断",
                    "detail": f"使用LLM分析专业要求，结果：{result_text}",
                    "resume_majors": major_names,
                    "required_majors": required_majors,
                    "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt
                }
            )
        except Exception as e:
            logger.error(f"专业筛选：LLM调用失败，错误={str(e)}")
            return FilterResult(
                passed=True,
                reason=f"LLM调用失败：{str(e)}，默认通过",
                source="rule",
                details={"method": "规则匹配-LLM调用失败", "error": str(e)}
            )
    
    async def match_work_experience_llm(self, requirement, resume_data: Dict) -> FilterResult:
        """使用LLM匹配工作经历要求（异步方法）"""
        if not self.model_manager:
            logger.warning("工作经历筛选：模型管理器未初始化，无法使用LLM判断")
            return FilterResult(
                passed=True,
                reason="模型未初始化，无法使用LLM判断工作经历要求",
                source="rule",
                details={"method": "规则匹配-模型未初始化"}
            )
        
        try:
            # 提取简历相关数据
            resume_extract = {}
            
            # 主要工作经历
            if "主要工作经历" in resume_data:
                resume_extract["主要工作经历"] = resume_data["主要工作经历"]
            
            # 学习经历统计信息
            if "学习经历统计信息" in resume_data:
                resume_extract["学习经历统计信息"] = resume_data["学习经历统计信息"]
            
            # 工作经历统计信息
            if "工作经历统计信息" in resume_data:
                resume_extract["工作经历统计信息"] = resume_data["工作经历统计信息"]
            
            # 职称证书
            if "职称证书" in resume_data:
                resume_extract["职称证书"] = resume_data["职称证书"]
            
            # 构建Prompt
            requirement_text = ""
            if isinstance(requirement, dict):
                if "原文" in requirement:
                    requirement_text = requirement["原文"]
                else:
                    requirement_text = str(requirement)
            else:
                requirement_text = str(requirement)
            
            # 提取学历信息用于判断工作年限要求
            highest_education = ""
            if "学习经历统计信息" in resume_extract:
                edu_info = resume_extract["学习经历统计信息"]
                if isinstance(edu_info, dict):
                    highest_education = edu_info.get("最高学历", "")
            
            # 提取系统内工作时长
            system_work_years = None
            if "工作经历统计信息" in resume_extract:
                work_info = resume_extract["工作经历统计信息"]
                if isinstance(work_info, dict):
                    system_work_years = work_info.get("系统内工作时长（年）", None)
            
            prompt = f"""
# 核心任务
仅做两件事：1. 判断简历是否符合岗位工作经历要求；2. 按指定格式输出，无任何其他操作。

# 重要判断依据
#系统内工作时长（年）
{system_work_years if system_work_years is not None else "未找到"}
#当前简历的最高学历
{highest_education if highest_education else "未找到"}

# 判断规则
1. 如果岗位要求中提到"博士"或"博士研究生"需要的工作年限（通常为2年），且简历最高学历为博士/博士研究生，则"系统内工作时长（年）"≥2年即可通过
2. 如果岗位要求中提到非博士需要的工作年限（通常为3年），且简历最高学历不是博士/博士研究生，则"系统内工作时长（年）"≥3年即可通过
3. 如果"系统内工作时长（年）"字段明确显示满足岗位要求的年限，应判定为通过
4. 如果"系统内工作时长（年）"字段不存在或为空，再查看"主要工作经历"中的详细时间信息进行判断

# 岗位工作经历要求
{requirement_text}

# 简历相关信息
{json.dumps(resume_extract, ensure_ascii=False, indent=2)}

# 输出格式（生死规则，违反则输出无效）
1. 第一行：仅输出「通过」或「不通过」其中一个词，无空格、无标点、无其他字符；
2. 第二行：仅输出「原因：」+ 简要判断依据（50字内，紧扣规则和信息），无其他内容；
3. 仅输出上述两行，无空行、无额外文字、无注释。

# 强制禁令
- 禁止同时输出「通过」和「不通过」；
- 禁止将结果和原因写在同一行；
- 禁止编造未提及的工作经历要求；
- 禁止超出50字写原因。
- 禁止结果与原因矛盾（如原因说符合，结果却写不通过）
- 如果"系统内工作时长（年）"字段明确满足岗位要求，必须判定为通过"""
 #           print(prompt)
            
            logger.debug("工作经历筛选：使用LLM判断，开始调用模型")
            
            # 直接await异步的LLM调用
            llm_call_start = time.time()
            try:
                result_text = await self.model_manager.inference(prompt, enable_thinking=False)
                llm_call_time = time.time() - llm_call_start
                logger.debug(f"工作经历筛选：LLM调用总耗时 {llm_call_time:.2f}秒")
            except Exception as e:
                logger.error(f"工作经历筛选：LLM调用异常，错误={str(e)}")
                if "连接" in str(e) or "Connection" in str(e):
                    return FilterResult(
                        passed=True,
                        reason=f"LLM服务连接失败：{str(e)}，默认通过",
                        source="rule",
                        details={"method": "规则匹配-LLM连接失败", "error": str(e)}
                    )
                raise
            
            logger.debug(f"工作经历筛选：LLM返回结果={result_text}")
            
            # 解析LLM结果
            passed = "通过" in result_text or "符合" in result_text
            if "不通过" in result_text or "不符合" in result_text:
                passed = False
            
            return FilterResult(
                passed=passed,
                reason=result_text,
                source="llm",
                details={
                    "method": "LLM判断",
                    "detail": f"使用LLM分析工作经历要求，结果：{result_text}",
                    "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt
                }
            )
        except Exception as e:
            logger.error(f"工作经历筛选：LLM调用失败，错误={str(e)}")
            return FilterResult(
                passed=True,
                reason=f"LLM调用失败：{str(e)}，默认通过",
                source="rule",
                details={"method": "规则匹配-LLM调用失败", "error": str(e)}
            )
    
    async def match_work_years_llm(self, requirement, job_data: Dict, resume_data: Dict) -> FilterResult:
        """使用LLM匹配工作经验要求（异步方法）"""
        if not self.model_manager:
            logger.warning("工作经验筛选：模型管理器未初始化，无法使用LLM判断")
            return FilterResult(
                passed=True,
                reason="模型未初始化，无法使用LLM判断工作经验要求",
                source="rule",
                details={"method": "规则匹配-模型未初始化"}
            )
        
        try:
            # 提取岗位相关数据
            job_duty = job_data.get("岗位职责", [])
            job_requirement = job_data.get("岗位任职条件", [])
            
            # 提取简历相关数据
            resume_extract = {}
            
            # 主要工作经历
            if "主要工作经历" in resume_data:
                resume_extract["主要工作经历"] = resume_data["主要工作经历"]
            
            # 工作经历统计信息
            if "工作经历统计信息" in resume_data:
                resume_extract["工作经历统计信息"] = resume_data["工作经历统计信息"]
            
            # 学习经历统计信息
            if "学习经历统计信息" in resume_data:
                resume_extract["学习经历统计信息"] = resume_data["学习经历统计信息"]
            
            # 构建Prompt
            prompt = f"""
# 核心任务
仅做两件事：1. 判断简历是否符合岗位工作经验要求；2. 按指定格式输出，无任何其他操作。

# 岗位职责（硬性条件，必须全部满足）
{json.dumps(job_duty, ensure_ascii=False, indent=2) if job_duty else "无"}

# 岗位任职条件（需要区分硬性和软性）
{json.dumps(job_requirement, ensure_ascii=False, indent=2) if job_requirement else "无"}

# 简历相关信息
{json.dumps(resume_extract, ensure_ascii=False, indent=2)}

# 判断规则（生死规则，违反则输出无效）
1. **岗位职责**：都是硬性条件，必须全部满足。根据简历的主要工作经历、工作经历统计信息、学习经历统计信息判断能否胜任这些职责。如果任何一条职责无法胜任，则判定为不通过。

2. **岗位任职条件**：需要区分硬性和软性条件
   - **硬性条件**：不包含"优先"、"者优先"、"优先考虑"等字样的条件，必须满足，不满足则判定为不通过
   - **软性条件**：包含"优先"、"者优先"、"优先考虑"等字样的条件，不作为否决条件，不满足不影响结果

3. **判断标准**：
   - 岗位职责必须全部满足（硬性）
   - 岗位任职条件中的硬性条件必须满足
   - 岗位任职条件中的软性条件（优先类）不满足不影响结果

# 输出格式（生死规则，违反则输出无效）
1. 第一行：仅输出「通过」或「不通过」其中一个词，无空格、无标点、无其他字符；
2. 第二行：仅输出「原因：」+ 简要判断依据（50字内，说明哪些硬性条件满足或不满足），无其他内容；
3. 仅输出上述两行，无空行、无额外文字、无注释。

# 强制禁令
- 禁止同时输出「通过」和「不通过」；
- 禁止将结果和原因写在同一行；
- 禁止将软性条件（优先类）作为否决条件；
- 禁止忽略岗位职责中的硬性条件；
- 禁止超出50字写原因。
- 禁止结果与原因矛盾（如原因说符合，结果却写不通过）"""
            
            logger.debug("工作经验筛选：使用LLM判断，开始调用模型")
            
            # 直接await异步的LLM调用
            llm_call_start = time.time()
            try:
                result_text = await self.model_manager.inference(prompt, enable_thinking=False)
                llm_call_time = time.time() - llm_call_start
                logger.debug(f"工作经验筛选：LLM调用总耗时 {llm_call_time:.2f}秒")
            except Exception as e:
                logger.error(f"工作经验筛选：LLM调用异常，错误={str(e)}")
                if "连接" in str(e) or "Connection" in str(e):
                    return FilterResult(
                        passed=True,
                        reason=f"LLM服务连接失败：{str(e)}，默认通过",
                        source="rule",
                        details={"method": "规则匹配-LLM连接失败", "error": str(e)}
                    )
                raise
            
            logger.debug(f"工作经验筛选：LLM返回结果={result_text}")
            
            # 解析LLM结果
            passed = "通过" in result_text or "符合" in result_text
            if "不通过" in result_text or "不符合" in result_text:
                passed = False
            
            return FilterResult(
                passed=passed,
                reason=result_text,
                source="llm",
                details={
                    "method": "LLM判断",
                    "detail": f"使用LLM分析工作经验要求，结果：{result_text}",
                    "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt
                }
            )
        except Exception as e:
            logger.error(f"工作经验筛选：LLM调用失败，错误={str(e)}")
            return FilterResult(
                passed=True,
                reason=f"LLM调用失败：{str(e)}，默认通过",
                source="rule",
                details={"method": "规则匹配-LLM调用失败", "error": str(e)}
            )
