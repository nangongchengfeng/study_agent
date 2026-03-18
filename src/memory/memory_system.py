"""
记忆系统核心模块 - 统一接口实现
提供三层记忆的统一管理和访问接口
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Any, List, Dict, Optional, Union

from .sensory_memory import SensoryMemory
from .short_term_memory import ShortTermMemory
from .long_term_memory import LongTermMemory


class MemorySystem:
    """
    记忆系统统一接口类
    提供get_memory、update_memory、delete_memory等统一方法
    """

    def __init__(self, base_dir: str = "data"):
        """
        初始化记忆系统

        Args:
            base_dir: 数据存储根目录
        """
        self.sensory_memory = SensoryMemory()
        self.short_term_memory = ShortTermMemory(
            os.path.join(base_dir, "short_term")
        )
        self.long_term_memory = LongTermMemory(
            os.path.join(base_dir, "long_term")
        )

    def update_memory(
        self,
        memory_type: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        更新记忆内容

        Args:
            memory_type: 记忆类型 ("sensory" | "short" | "long")
            content: 记忆内容
            metadata: 元数据（如时间戳、会话ID、标签等）

        Returns:
            是否更新成功
        """
        try:
            if memory_type == "sensory":
                return self.sensory_memory.update(content, metadata)
            elif memory_type == "short":
                return self.short_term_memory.update(content, metadata)
            elif memory_type == "long":
                return self.long_term_memory.update(content, metadata)
            else:
                raise ValueError(f"Invalid memory type: {memory_type}")
        except Exception as e:
            print(f"Error updating {memory_type} memory: {e}")
            return False

    def get_memory(
        self,
        memory_type: str,
        key: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        获取记忆内容

        Args:
            memory_type: 记忆类型 ("sensory" | "short" | "long")
            key: 记忆键值（如会话ID、知识点ID）
            query: 查询条件（用于复杂查询）

        Returns:
            记忆内容
        """
        try:
            if memory_type == "sensory":
                return self.sensory_memory.get(key, query)
            elif memory_type == "short":
                return self.short_term_memory.get(key, query)
            elif memory_type == "long":
                return self.long_term_memory.get(key, query)
            else:
                raise ValueError(f"Invalid memory type: {memory_type}")
        except Exception as e:
            print(f"Error getting {memory_type} memory: {e}")
            return None

    def delete_memory(
        self,
        memory_type: str,
        key: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        删除记忆内容

        Args:
            memory_type: 记忆类型 ("sensory" | "short" | "long")
            key: 记忆键值
            query: 查询条件

        Returns:
            是否删除成功
        """
        try:
            if memory_type == "sensory":
                return self.sensory_memory.delete(key, query)
            elif memory_type == "short":
                return self.short_term_memory.delete(key, query)
            elif memory_type == "long":
                return self.long_term_memory.delete(key, query)
            else:
                raise ValueError(f"Invalid memory type: {memory_type}")
        except Exception as e:
            print(f"Error deleting {memory_type} memory: {e}")
            return False

    def clear_expired_memory(self) -> int:
        """
        清理过期的短期记忆（保留最近7天）

        Returns:
            清理的记录数量
        """
        return self.short_term_memory.clear_expired()

    def get_all_memory_types(self) -> Dict[str, Any]:
        """
        获取所有记忆类型的状态信息

        Returns:
            各记忆类型的状态字典
        """
        return {
            "sensory": self.sensory_memory.get_status(),
            "short": self.short_term_memory.get_status(),
            "long": self.long_term_memory.get_status(),
        }

    def retrieve(self, *args, **kwargs):
        """别名方法，兼容Agent的retrieve调用"""
        # 适配不同的参数形式
        if len(args) == 0:
            memory_type = kwargs.pop("memory_type", "short")
            key = kwargs.pop("key", kwargs.pop("session_id", None))
            # 把其他参数放到query里
            query = kwargs.pop("query", kwargs)
            return self.get_memory(memory_type, key, query)
        return self.get_memory(*args, **kwargs)

    def update(self, *args, **kwargs):
        """别名方法，兼容Agent的update调用"""
        # 适配不同的参数形式
        if len(args) == 0:
            # 提取参数
            memory_type = kwargs.pop("memory_type", "long")
            content = kwargs.pop("content", kwargs.pop("new_knowledge", None))
            metadata = kwargs.pop("metadata", {})
            # 如果content仍为None，合并kwargs作为content
            if content is None:
                content = kwargs
            else:
                # 将剩余的kwargs合并到metadata中
                metadata.update(kwargs)
            return self.update_memory(memory_type, content, metadata)
        return self.update_memory(*args, **kwargs)
