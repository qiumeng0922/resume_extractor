#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM模型管理器模块 - 使用阿里云 DashScope
"""

import asyncio
import time
from typing import Dict, Optional
from utils.logger_config import setup_logger

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    raise ImportError("请安装 langchain-openai: pip install langchain-openai")

logger = setup_logger("llm_manager")


class LLMStudioModelManager:
    """LLM 模型管理器 - 使用阿里云 DashScope"""
    
    def __init__(self, api_key: str = None, model_name: str = None, base_url: str = None):
        """
        初始化LLM模型管理器
        
        Args:
            api_key: DashScope API Key，如果为None则使用config中的配置
            model_name: 模型名称，如果为None则使用config中的配置
            base_url: Base URL，如果为None则使用config中的配置
        """
        from config import DASHSCOPE_API_KEY, LLM_MODEL, DASHSCOPE_BASE_URL
        
        self.api_key = api_key or DASHSCOPE_API_KEY
        self.model_name = model_name or LLM_MODEL
        self.base_url = base_url or DASHSCOPE_BASE_URL
        
        # 初始化 ChatOpenAI 实例
        self.llm = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0,  # 设置为0以确保结果一致性
            max_tokens=2048,
            timeout=300
        )
        
        logger.info(f"已初始化 DashScope LLM: 模型={self.model_name}, base_url={self.base_url}")
    
    async def inference(self, prompt: str, model_path: Optional[str] = None, enable_thinking: bool = True) -> str:
        """
        通过阿里云 DashScope API 调用模型推理（异步）
        
        Args:
            prompt: 输入提示词
            model_path: 模型路径（可选，不使用）
            enable_thinking: 是否启用思考输出（DashScope 可能不支持此参数）
        
        Returns:
            完整响应内容
        """
        try:
            request_start = time.time()
            logger.debug(f"[LLM 请求] 开始发送请求到 DashScope，模型: {self.model_name}")
            
            # 使用 asyncio.to_thread 在线程池中运行同步的 invoke 调用
            # ChatOpenAI 的 invoke 方法是同步的，需要在线程池中运行
            response = await asyncio.to_thread(self.llm.invoke, prompt)
            
            request_time = time.time() - request_start
            logger.debug(f"[LLM 请求] 请求完成，耗时 {request_time:.2f}秒")
            
            # 提取响应内容
            if hasattr(response, 'content'):
                return response.content
            elif isinstance(response, str):
                return response
            else:
                return str(response)
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"DashScope LLM 调用失败: {error_msg}")
            
            # 提供更友好的错误信息
            if "connection" in error_msg.lower() or "connect" in error_msg.lower():
                raise Exception(f"无法连接到 DashScope 服务: {error_msg}，请检查网络连接和 API Key")
            elif "timeout" in error_msg.lower():
                raise Exception("DashScope 服务请求超时")
            elif "api" in error_msg.lower() or "key" in error_msg.lower():
                raise Exception(f"DashScope API Key 错误: {error_msg}，请检查 API Key 是否正确")
            else:
                raise Exception(f"DashScope 服务调用失败: {error_msg}")
    
    async def close(self):
        """关闭HTTP会话（ChatOpenAI 会自动管理连接）"""
        pass
    
    def get_stats(self) -> Dict:
        """获取模型统计信息"""
        return {
            "model": self.model_name,
            "base_url": self.base_url,
            "provider": "DashScope"
        }


def get_model_manager():
    """
    获取 LLM 模型管理器（阿里云 DashScope）
    
    Returns:
        LLMStudioModelManager实例
    """
    from config import DASHSCOPE_API_KEY, LLM_MODEL, DASHSCOPE_BASE_URL
    
    logger.info(f"使用 DashScope LLM: 模型={LLM_MODEL}, base_url={DASHSCOPE_BASE_URL}")
    
    try:
        # 创建模型管理器实例
        manager = LLMStudioModelManager(
            api_key=DASHSCOPE_API_KEY,
            model_name=LLM_MODEL,
            base_url=DASHSCOPE_BASE_URL
        )
        
        # 简单测试连接（可选，发送一个测试请求）
        logger.info("✅ DashScope LLM 管理器初始化成功")
        return manager
        
    except Exception as e:
        logger.error(f"初始化 DashScope LLM 管理器失败: {str(e)}")
        logger.warning("将尝试继续运行，但 LLM 功能可能不可用")
        # 即使初始化失败，也返回实例，让调用方处理错误
        return LLMStudioModelManager(
            api_key=DASHSCOPE_API_KEY,
            model_name=LLM_MODEL,
            base_url=DASHSCOPE_BASE_URL
        )
