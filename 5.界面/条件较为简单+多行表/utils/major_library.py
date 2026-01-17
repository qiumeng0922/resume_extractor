#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业库管理模块
"""

import json
import os
from typing import Dict, List, Optional
from .logger_config import setup_logger

logger = setup_logger("major_library")


class MajorLibrary:
    """专业库管理器"""
    
    def __init__(self, library_path: Optional[str] = None):
        """
        初始化专业库
        
        Args:
            library_path: 专业库文件路径，如果为None则使用默认路径
        """
        self.library_path = library_path
        self.major_library = self._load_major_library(library_path)
        self.major_to_classes = self._build_major_to_classes_map()
    
    def _load_major_library(self, library_path: Optional[str] = None) -> Dict:
        """
        加载专业库.json
        
        Args:
            library_path: 专业库文件路径，如果为None则使用默认路径
        
        Returns:
            专业库数据字典
        """
        try:
            # 如果没有指定路径，使用默认路径
            if library_path is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # 回到项目根目录
                project_root = os.path.dirname(current_dir)
                library_path = os.path.join(project_root, "专业库.json")
            
            with open(library_path, 'r', encoding='utf-8') as f:
                library = json.load(f)
            logger.debug(f"专业库加载成功：{library_path}，共 {len(library.get('专业分类列表', []))} 个门类")
            return library
        except Exception as e:
            logger.warning(f"专业库加载失败: {e}，将使用空字典")
            return {"专业分类列表": []}
    
    def _build_major_to_classes_map(self) -> Dict[str, List[str]]:
        """
        构建专业名称到专业类名称的映射
        
        Returns:
            字典：{专业名称: [专业类名称列表]}
        """
        major_to_classes = {}
        library = self.major_library
        
        for category in library.get("专业分类列表", []):
            for major_class in category.get("专业类列表", []):
                class_name = major_class.get("专业类名称", "")
                major_names = major_class.get("专业名称列表", [])
                
                for major_name in major_names:
                    if major_name not in major_to_classes:
                        major_to_classes[major_name] = []
                    if class_name and class_name not in major_to_classes[major_name]:
                        major_to_classes[major_name].append(class_name)
        
        logger.debug(f"专业映射构建完成，共 {len(major_to_classes)} 个专业")
        return major_to_classes
    
    def get_major_classes(self, major_names: List[str]) -> List[str]:
        """
        根据专业名称列表查找对应的专业类名称列表
        
        Args:
            major_names: 专业名称列表
        
        Returns:
            专业类名称列表（去重）
        """
        class_names = []
        for major_name in major_names:
            if major_name in self.major_to_classes:
                class_names.extend(self.major_to_classes[major_name])
        
        # 去重并返回
        return list(set(class_names))
