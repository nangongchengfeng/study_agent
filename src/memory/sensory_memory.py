"""
感觉记忆模块
管理当前对话的最近10轮上下文，提供上下文拼接、截断功能
确保LLM上下文不超限
"""

from typing import Any, List, Dict, Optional


class SensoryMemory:
    """
    感觉记忆类 - 管理当前对话的最近10轮上下文

    特性：
    - 自动截断，保持最近10轮对话
    - 提供上下文拼接和格式化功能
    - 防止上下文超限
    """

    MAX_ROUNDS = 10  # 最多保留10轮对话

    def __init__(self):
        """初始化感觉记忆"""
        self._contexts: List[Dict[str, Any]] = []

    def update(
        self,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        更新感觉记忆

        Args:
            content: 记忆内容（通常是对话轮次）
            metadata: 元数据（如角色、时间戳）

        Returns:
            是否更新成功
        """
        try:
            # 创建记忆条目
            entry = {
                "content": content,
                "metadata": metadata or {},
                "timestamp": metadata.get("timestamp")
                if metadata and "timestamp" in metadata
                else None,
            }

            # 添加到上下文列表
            self._contexts.append(entry)

            # 截断超过MAX_ROUNDS的历史
            if len(self._contexts) > self.MAX_ROUNDS:
                self._contexts = self._contexts[-self.MAX_ROUNDS:]

            return True
        except Exception as e:
            print(f"Error updating sensory memory: {e}")
            return False

    def get(
        self,
        key: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        获取感觉记忆内容

        Args:
            key: 保留参数，用于兼容统一接口
            query: 查询条件（支持type、role等）

        Returns:
            记忆内容（列表形式）
        """
        if query:
            filtered = self._filter_contexts(query)
            return filtered
        return self._contexts

    def delete(
        self,
        key: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        删除感觉记忆内容

        Args:
            key: 保留参数
            query: 删除条件

        Returns:
            是否删除成功
        """
        try:
            if query:
                filtered = self._filter_contexts(query)
                for item in filtered:
                    if item in self._contexts:
                        self._contexts.remove(item)
            else:
                # 如果没有查询条件，清空所有内容
                self._contexts.clear()
            return True
        except Exception as e:
            print(f"Error deleting sensory memory: {e}")
            return False

    def _filter_contexts(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据查询条件过滤上下文

        Args:
            query: 查询条件字典

        Returns:
            匹配的上下文列表
        """
        filtered = self._contexts

        if "type" in query:
            filtered = [
                ctx for ctx in filtered
                if ctx.get("metadata", {}).get("type") == query["type"]
            ]

        if "role" in query:
            filtered = [
                ctx for ctx in filtered
                if ctx.get("metadata", {}).get("role") == query["role"]
            ]

        if "keywords" in query:
            keywords = query["keywords"]
            if not isinstance(keywords, list):
                keywords = [keywords]

            filtered = [
                ctx for ctx in filtered
                if any(keyword in str(ctx.get("content"))
                      for keyword in keywords)
            ]

        return filtered

    def get_status(self) -> Dict[str, Any]:
        """
        获取感觉记忆状态信息

        Returns:
            状态字典
        """
        return {
            "current_rounds": len(self._contexts),
            "max_rounds": self.MAX_ROUNDS,
            "types": list(set(
                ctx.get("metadata", {}).get("type", "unknown")
                for ctx in self._contexts
            )),
            "last_updated": self._contexts[-1]["timestamp"]
            if self._contexts
            else None,
        }

    def to_prompt(self, format_style: str = "simple") -> str:
        """
        将上下文转换为LLM的prompt格式

        Args:
            format_style: 格式风格 ("simple" | "structured")

        Returns:
            格式化后的prompt字符串
        """
        if format_style == "structured":
            return self._to_structured_prompt()
        else:
            return self._to_simple_prompt()

    def _to_simple_prompt(self) -> str:
        """简单格式的prompt（纯文本拼接）"""
        parts = []
        for ctx in self._contexts:
            role = ctx.get("metadata", {}).get("role", "user")
            content = str(ctx.get("content", ""))
            parts.append(f"{role}: {content}")
        return "\n".join(parts)

    def _to_structured_prompt(self) -> str:
        """结构化格式的prompt（包含角色和时间戳）"""
        parts = []
        for ctx in self._contexts:
            role = ctx.get("metadata", {}).get("role", "user")
            content = str(ctx.get("content", ""))
            timestamp = ctx.get("timestamp")

            if timestamp:
                parts.append(
                    f"[{timestamp}] {role.upper()}: {content}"
                )
            else:
                parts.append(f"{role.upper()}: {content}")

        return "\n".join(parts)
