"""
记忆存储
负责记忆的持久化存储
"""

import logging
import json
import os
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryStore:
    """
    记忆存储类
    """

    def __init__(self, storage_dir: Optional[str] = None):
        """
        初始化记忆存储

        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = storage_dir or "./data/memory"
        self._ensure_storage_dir()
        logger.info(f"初始化记忆存储: {self.storage_dir}")

    def _ensure_storage_dir(self):
        """
        确保存储目录存在
        """
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir, exist_ok=True)

    def save(self, memory_id: str, data: Dict[str, Any]) -> bool:
        """
        保存记忆

        Args:
            memory_id: 记忆ID
            data: 记忆数据

        Returns:
            是否成功
        """
        try:
            file_path = os.path.join(self.storage_dir, f"{memory_id}.json")

            # 添加元数据
            data["_metadata"] = {
                "memory_id": memory_id,
                "saved_at": datetime.now().isoformat(),
                "version": "1.0",
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.debug(f"保存记忆成功: {memory_id}")
            return True

        except Exception as e:
            logger.error(f"保存记忆失败: {memory_id}, 错误: {str(e)}")
            return False

    def load(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        加载记忆

        Args:
            memory_id: 记忆ID

        Returns:
            记忆数据，如果不存在则返回None
        """
        try:
            file_path = os.path.join(self.storage_dir, f"{memory_id}.json")

            if not os.path.exists(file_path):
                logger.debug(f"记忆文件不存在: {memory_id}")
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            logger.debug(f"加载记忆成功: {memory_id}")
            return data

        except Exception as e:
            logger.error(f"加载记忆失败: {memory_id}, 错误: {str(e)}")
            return None

    def delete(self, memory_id: str) -> bool:
        """
        删除记忆

        Args:
            memory_id: 记忆ID

        Returns:
            是否成功
        """
        try:
            file_path = os.path.join(self.storage_dir, f"{memory_id}.json")

            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"删除记忆成功: {memory_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"删除记忆失败: {memory_id}, 错误: {str(e)}")
            return False

    def list_memories(self) -> list:
        """
        列出所有记忆

        Returns:
            记忆ID列表
        """
        try:
            if not os.path.exists(self.storage_dir):
                return []

            memories = []
            for filename in os.listdir(self.storage_dir):
                if filename.endswith(".json"):
                    memory_id = filename[:-5]  # 去掉 .json
                    memories.append(memory_id)

            return memories

        except Exception as e:
            logger.error(f"列出记忆失败: {str(e)}")
            return []

    def exists(self, memory_id: str) -> bool:
        """
        检查记忆是否存在

        Args:
            memory_id: 记忆ID

        Returns:
            是否存在
        """
        file_path = os.path.join(self.storage_dir, f"{memory_id}.json")
        return os.path.exists(file_path)

    def get_metadata(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        获取记忆元数据

        Args:
            memory_id: 记忆ID

        Returns:
            元数据
        """
        data = self.load(memory_id)
        if data and "_metadata" in data:
            return data["_metadata"]
        return None

    def clear_all(self) -> bool:
        """
        清空所有记忆

        Returns:
            是否成功
        """
        try:
            memory_ids = self.list_memories()
            for memory_id in memory_ids:
                self.delete(memory_id)

            logger.info("清空所有记忆成功")
            return True

        except Exception as e:
            logger.error(f"清空所有记忆失败: {str(e)}")
            return False
