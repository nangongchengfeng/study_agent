"""
记忆检索Agent
负责从记忆系统中检索相关知识
"""

import logging
from typing import Any, Dict, List, Optional
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MemoryRetrievalAgent(BaseAgent):
    """
    记忆检索Agent
    """

    def __init__(self, memory_system=None):
        super().__init__("MemoryRetrievalAgent")
        self.memory_system = memory_system

    def process(
        self,
        user_query: str,
        user_level: str,
        understanding_result: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        检索相关记忆

        Args:
            user_query: 用户查询
            user_level: 用户水平
            understanding_result: 理解结果

        Returns:
            检索结果
        """
        logger.info(f"执行记忆检索: {user_query}")

        if not self.validate_input(["user_query"], user_query=user_query):
            return {"error": "缺少必需参数"}

        # 提取关键词用于检索
        keywords = self._extract_keywords(user_query, understanding_result)

        # 执行检索
        related_knowledge = self._retrieve_related_knowledge(keywords, user_level)

        # 检索学习进度
        learning_progress = self._retrieve_learning_progress(keywords)

        # 检索常见错误
        common_mistakes = self._retrieve_common_mistakes(keywords, user_level)

        # 检索前置知识
        prerequisites = self._retrieve_prerequisites(keywords)

        result = {
            "related_knowledge": related_knowledge,
            "learning_progress": learning_progress,
            "common_mistakes": common_mistakes,
            "prerequisites": prerequisites,
            "keywords": keywords,
            "has_prior_learning": len(learning_progress) > 0,
            "confidence": 0.8,
        }

        self.log_process(
            {"user_query": user_query, "keywords": keywords},
            result,
        )

        return result

    def _extract_keywords(
        self,
        user_query: str,
        understanding_result: Optional[Dict[str, Any]],
    ) -> List[str]:
        """
        提取检索关键词

        Args:
            user_query: 用户查询
            understanding_result: 理解结果

        Returns:
            关键词列表
        """
        keywords = []

        # 从理解结果中获取
        if understanding_result:
            keywords.extend(understanding_result.get("keywords", []))
            keywords.extend(understanding_result.get("topics", []))

        # 从查询中简单提取
        tech_terms = ["Python", "Java", "JavaScript", "C++", "Go", "Rust",
                     "Flask", "Django", "FastAPI", "Vue", "React",
                     "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis",
                     "Docker", "Kubernetes", "Git", "Linux",
                     "装饰器", "迭代器", "生成器", "闭包", "线程", "进程",
                     "API", "HTTP", "REST", "JSON", "XML",
                     "变量", "函数", "类", "对象", "循环", "条件",
                     "算法", "数据结构", "数组", "链表", "栈", "队列"]

        for term in tech_terms:
            if term in user_query and term not in keywords:
                keywords.append(term)

        return keywords[:15]  # 限制关键词数量

    def _retrieve_related_knowledge(
        self,
        keywords: List[str],
        user_level: str,
    ) -> List[Dict[str, Any]]:
        """
        检索相关知识

        Args:
            keywords: 关键词
            user_level: 用户水平

        Returns:
            相关知识列表
        """
        if not self.memory_system:
            # 如果没有记忆系统，返回模拟数据
            return self._get_mock_related_knowledge(keywords, user_level)

        # 调用记忆系统检索
        try:
            return self.memory_system.retrieve(
                keywords=keywords,
                user_level=user_level,
                limit=5,
            )
        except Exception as e:
            logger.error(f"从记忆系统检索失败: {str(e)}")
            return self._get_mock_related_knowledge(keywords, user_level)

    def _get_mock_related_knowledge(
        self,
        keywords: List[str],
        user_level: str,
    ) -> List[Dict[str, Any]]:
        """
        获取模拟的相关知识数据

        Args:
            keywords: 关键词
            user_level: 用户水平

        Returns:
            模拟知识列表
        """
        mock_knowledge = []

        # 装饰器相关模拟知识
        if any(k in ["装饰器", "decorator", "Python"] for k in keywords):
            mock_knowledge.append({
                "id": "knowledge_decorator_1",
                "title": "Python装饰器基础概念",
                "content": "装饰器是Python中用于修改函数或类行为的设计模式...",
                "type": "concept",
                "difficulty": "intermediate",
                "relevance": 0.95,
                "last_accessed": "2024-01-15",
            })
            mock_knowledge.append({
                "id": "knowledge_decorator_2",
                "title": "装饰器的实际应用场景",
                "content": "日志记录、性能计时、权限验证、缓存...",
                "type": "application",
                "difficulty": "intermediate",
                "relevance": 0.85,
                "last_accessed": "2024-01-10",
            })

        # 迭代器相关模拟知识
        if any(k in ["迭代器", "生成器", "iterator", "generator"] for k in keywords):
            mock_knowledge.append({
                "id": "knowledge_iterator_1",
                "title": "Python迭代器协议",
                "content": "__iter__和__next__方法...",
                "type": "concept",
                "difficulty": "intermediate",
                "relevance": 0.9,
                "last_accessed": "2024-01-12",
            })

        # 数据结构相关模拟知识
        if any(k in ["算法", "数据结构", "数组", "链表"] for k in keywords):
            mock_knowledge.append({
                "id": "knowledge_ds_1",
                "title": "常用数据结构比较",
                "content": "数组、链表、栈、队列的优缺点...",
                "type": "comparison",
                "difficulty": "intermediate",
                "relevance": 0.88,
                "last_accessed": "2024-01-08",
            })

        return mock_knowledge[:5]  # 限制返回数量

    def _retrieve_learning_progress(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        检索学习进度

        Args:
            keywords: 关键词

        Returns:
            学习进度列表
        """
        # 模拟学习进度数据
        mock_progress = []

        if any(k in ["装饰器", "decorator"] for k in keywords):
            mock_progress.append({
                "topic": "Python装饰器",
                "status": "in_progress",  # not_started, in_progress, completed, mastered
                "completion_percent": 60,
                "last_studied": "2024-01-15",
                "mastery_level": 0.6,
                "practice_completed": 3,
                "practice_total": 5,
            })

        return mock_progress

    def _retrieve_common_mistakes(
        self,
        keywords: List[str],
        user_level: str,
    ) -> List[Dict[str, Any]]:
        """
        检索常见错误

        Args:
            keywords: 关键词
            user_level: 用户水平

        Returns:
            常见错误列表
        """
        mock_mistakes = []

        if any(k in ["装饰器", "decorator"] for k in keywords):
            mock_mistakes.append({
                "id": "mistake_decorator_1",
                "title": "忘记使用functools.wraps",
                "description": "装饰器会丢失原函数的元信息",
                "example": "错误代码示例",
                "solution": "使用@functools.wraps装饰内部函数",
                "frequency": "high",
            })
            mock_mistakes.append({
                "id": "mistake_decorator_2",
                "title": "装饰带参数的函数时处理不当",
                "description": "需要使用*args和**kwargs来传递参数",
                "example": "def wrapper(*args, **kwargs): return func(*args, **kwargs)",
                "solution": "正确处理位置参数和关键字参数",
                "frequency": "medium",
            })

        return mock_mistakes

    def _retrieve_prerequisites(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        检索前置知识

        Args:
            keywords: 关键词

        Returns:
            前置知识列表
        """
        mock_prerequisites = []

        if any(k in ["装饰器", "decorator"] for k in keywords):
            mock_prerequisites.append({
                "topic": "Python函数基础",
                "description": "理解函数作为一等公民的概念",
                "status": "required",  # required, recommended
                "mastery_required": 0.7,
            })
            mock_prerequisites.append({
                "topic": "闭包（Closure）",
                "description": "理解嵌套函数和变量作用域",
                "status": "required",
                "mastery_required": 0.6,
            })
            mock_prerequisites.append({
                "topic": "*args和**kwargs",
                "description": "理解可变参数的使用",
                "status": "recommended",
                "mastery_required": 0.5,
            })

        return mock_prerequisites
