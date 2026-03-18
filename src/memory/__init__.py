"""
智能编程学习导师项目 - 记忆系统
三层记忆架构：
- 感觉记忆：管理当前对话的最近10轮上下文，防止超限
- 短期记忆：本地JSON文件存储，保存最近7天的学习会话数据
- 长期记忆：用户知识图谱，永久保存知识点、学习历史、代码作品集
"""

from .memory_system import MemorySystem

__all__ = ["MemorySystem"]
