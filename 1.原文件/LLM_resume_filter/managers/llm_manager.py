#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM模型管理器模块
"""

import json
import requests
import asyncio
import time
from typing import Dict, Optional
from utils.logger_config import setup_logger

logger = setup_logger("llm_manager")


class LLMStudioModelManager:
    """LLM """
    
    def __init__(self, base_url: str = None, model_name: str = None):
        """
        初始化LLM模型管理器
        
        Args:
            base_url: LLM 服务地址，如果为None则使用config中的配置
            model_name: 模型名称，如果为None则使用config中的配置
        """
        from config import LLM_URL, LLM_MODEL
        self.base_url = (base_url or LLM_URL).rstrip('/')
        self.model_name = model_name or LLM_MODEL
        self.timeout_seconds = 300
    
    def _sync_request(self, url: str, data: Dict) -> str:
        """同步HTTP请求（在线程池中运行）"""
        request_start = time.time()
        logger.debug(f"[LLM 请求] 开始发送请求到 {url}")
        response = requests.post(url, json=data, timeout=self.timeout_seconds)
        request_time = time.time() - request_start
        logger.debug(f"[LLM 请求] 请求完成，耗时 {request_time:.2f}秒，状态码: {response.status_code}")
        response.raise_for_status()
        result = response.json()
        
        # 解析OpenAI兼容格式的响应
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        elif "content" in result:
            return result["content"]
        else:
            raise Exception(f"无法解析LLM 响应: {result}")
    
    async def inference(self, prompt: str, model_path: Optional[str] = None, enable_thinking: bool = True) -> str:
        """
        通过LLM  API调用模型推理（异步，使用线程池运行同步请求）
        
        Args:
            prompt: 输入提示词
            model_path: 模型路径（可选，不使用）
            enable_thinking: 是否启用思考输出（LLM 可能不支持此参数）
        
        Returns:
            完整响应内容
        """
        # 构造OpenAI兼容格式的请求数据
        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        # LLM 通常使用 /v1/chat/completions 端点
        url = f"{self.base_url}/v1/chat/completions"
        
        try:
            # 使用 asyncio.to_thread 在线程池中运行同步请求
            result_text = await asyncio.to_thread(self._sync_request, url, data)
            return result_text
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"无法连接到LLM 服务: {str(e)}，请确保LLM 已启动")
        except requests.exceptions.Timeout:
            raise Exception("LLM 服务请求超时")
        except Exception as e:
            raise Exception(f"LLM 服务调用失败: {str(e)}")
    
    async def close(self):
        """关闭HTTP会话（使用requests时不需要关闭）"""
        pass
    
    def get_stats(self) -> Dict:
        """获取模型统计信息（LLM 可能不支持此接口）"""
        return {
            "model": self.model_name,
            "base_url": self.base_url
        }


def get_model_manager():
    """
    获取LLM 模型管理器
    
    Returns:
        LLMStudioModelManager实例，如果连接失败则返回None
    """
    from config import LLM_URL, LLM_MODEL
    
    logger.info(f"使用LLM : {LLM_URL}, 模型: {LLM_MODEL}")
    try:
        # 简单测试连接（可选）
        test_url = f"{LLM_URL}/v1/models"
        response = requests.get(test_url, timeout=5)
        if response.status_code == 200:
            logger.info("✅ LLM 连接正常")
        else:
            logger.warning(f"LLM 连接测试失败，状态码: {response.status_code}")
    except requests.exceptions.ConnectionError:
        logger.warning(f"无法连接到LLM （{LLM_URL}），将尝试连接...")
    except Exception as e:
        logger.warning(f"检查LLM 时出错: {str(e)}")
    
    return LLMStudioModelManager(base_url=LLM_URL, model_name=LLM_MODEL)
