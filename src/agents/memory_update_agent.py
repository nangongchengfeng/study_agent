"""
记忆更新Agent
负责更新用户的学习记忆
"""

import logging
from typing import Any, Dict, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MemoryUpdateAgent(BaseAgent):
    """
    记忆更新Agent
    """

    def __init__(self, memory_system=None):
        super().__init__("MemoryUpdateAgent")
        self.memory_system = memory_system

    def process(
        self,
        user_query: str,
        user_level: str,
        explanation: str,
        example: str,
        practice: str,
        validation_result: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        更新记忆

        Args:
            user_query: 用户查询
            user_level: 用户水平
            explanation: 讲解内容
            example: 示例代码
            practice: 练习题
            validation_result: 验证结果

        Returns:
            更新结果
        """
        logger.info(f"执行记忆更新: {user_query}")

        if not self.validate_input(
            ["user_query", "user_level", "explanation"],
            user_query=user_query,
            user_level=user_level,
            explanation=explanation,
        ):
            return {"error": "缺少必需参数"}

        # 提取新知识
        new_knowledge = self._extract_new_knowledge(
            user_query,
            explanation,
            example,
            practice,
        )

        # 计算掌握程度
        mastery_level = validation_result.get("mastery_level", "beginning")

        # 执行记忆更新
        if self.memory_system:
            try:
                self.memory_system.update(
                    new_knowledge=new_knowledge,
                    user_level=user_level,
                    validation_result=validation_result,
                    mastery_level=mastery_level,
                )
                logger.info("记忆系统更新成功")
            except Exception as e:
                logger.error(f"记忆系统更新失败: {str(e)}")

        # 记录学习进度
        learning_progress = self._record_learning_progress(
            user_query,
            validation_result,
            mastery_level,
        )

        result = {
            "new_knowledge": new_knowledge,
            "learning_progress": learning_progress,
            "mastery_level": mastery_level,
            "update_success": True,
        }

        self.log_process(
            {"user_query": user_query, "mastery_level": mastery_level},
            result,
        )

        return result

    def _extract_new_knowledge(
        self,
        user_query: str,
        explanation: str,
        example: str,
        practice: str,
    ) -> Dict[str, Any]:
        """
        提取新知识

        Args:
            user_query: 用户查询
            explanation: 讲解内容
            example: 示例代码
            practice: 练习题

        Returns:
            新知识字典
        """
        # 识别主题
        topics = self._identify_topics(user_query, explanation)

        return {
            "id": self._generate_knowledge_id(user_query),
            "title": user_query,
            "content": self._extract_content_summary(explanation),
            "topics": topics,
            "example": example,
            "practice": practice,
            "related_knowledge": self._identify_related_knowledge(explanation, topics),
            "keywords": self._extract_keywords(user_query, explanation),
            "difficulty": self._assess_difficulty(user_query, explanation),
            "type": self._determine_content_type(user_query),
            "user_level": "intermediate",  # 默认值
            "creation_time": self._get_current_timestamp(),
            "last_accessed": self._get_current_timestamp(),
            "access_count": 1,
            "importance_score": self._calculate_importance(user_query),
            "mastery_score": 0.5,
            "review_priority": self._determine_review_priority(),
        }

    def _identify_topics(self, user_query: str, explanation: str) -> List[str]:
        """
        识别主题

        Args:
            user_query: 用户查询
            explanation: 讲解内容

        Returns:
            主题列表
        """
        topic_keywords = {
            "装饰器": ["装饰器", "decorator"],
            "迭代器": ["迭代器", "iterator"],
            "生成器": ["生成器", "generator"],
            "闭包": ["闭包", "closure"],
            "函数": ["函数", "function"],
            "类": ["类", "class", "面向对象"],
            "列表": ["列表", "list"],
            "字典": ["字典", "dict"],
        }

        combined_text = (user_query + " " + explanation).lower()
        topics = []

        for topic, keywords in topic_keywords.items():
            if any(kw in combined_text for kw in keywords):
                topics.append(topic)

        if not topics:
            topics.append("general")

        return topics

    def _extract_content_summary(self, explanation: str) -> str:
        """
        提取内容摘要

        Args:
            explanation: 讲解内容

        Returns:
            内容摘要
        """
        # 简单的摘要提取（取前200个字符）
        max_length = 200
        if len(explanation) <= max_length:
            return explanation.strip()
        return explanation[:max_length].strip() + "..."

    def _identify_related_knowledge(self, explanation: str, topics: List[str]) -> List[str]:
        """
        识别相关知识

        Args:
            explanation: 讲解内容
            topics: 主题列表

        Returns:
            相关知识列表
        """
        related = []

        if any(t in ["装饰器", "decorator"] for t in topics):
            related.extend(["函数", "闭包", "高阶函数"])
        elif any(t in ["迭代器", "iterator"] for t in topics):
            related.extend(["可迭代对象", "for循环", "next()"])
        elif any(t in ["生成器", "generator"] for t in topics):
            related.extend(["yield", "内存效率"])

        return related

    def _extract_keywords(self, user_query: str, explanation: str) -> List[str]:
        """
        提取关键词

        Args:
            user_query: 用户查询
            explanation: 讲解内容

        Returns:
            关键词列表
        """
        keywords = []

        tech_terms = [
            "Python", "Java", "JavaScript", "C++", "Go", "Rust",
            "Flask", "Django", "FastAPI", "Vue", "React",
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis",
            "Docker", "Kubernetes", "Git", "Linux",
            "装饰器", "迭代器", "生成器", "闭包", "线程", "进程",
            "API", "HTTP", "REST", "JSON", "XML",
            "变量", "函数", "类", "对象", "循环", "条件",
            "算法", "数据结构", "数组", "链表", "栈", "队列",
        ]

        combined_text = (user_query + " " + explanation).lower()
        for term in tech_terms:
            if term.lower() in combined_text and term not in keywords:
                keywords.append(term)

        return keywords[:10]

    def _assess_difficulty(self, user_query: str, explanation: str) -> str:
        """
        评估难度

        Args:
            user_query: 用户查询
            explanation: 讲解内容

        Returns:
            难度等级
        """
        difficulty_keywords = {
            "basic": ["基础", "简单", "入门", "初级"],
            "intermediate": ["中等", "进阶", "中级"],
            "advanced": ["高级", "深入", "底层", "原理"],
        }

        combined_text = (user_query + " " + explanation).lower()
        for difficulty, keywords in difficulty_keywords.items():
            if any(kw in combined_text for kw in keywords):
                return difficulty

        return "intermediate"

    def _determine_content_type(self, user_query: str) -> str:
        """
        确定内容类型

        Args:
            user_query: 用户查询

        Returns:
            内容类型
        """
        if any(q in user_query for q in ["什么是", "什么叫", "解释", "原理"]):
            return "concept"
        elif any(q in user_query for q in ["如何", "怎么", "实现"]):
            return "how_to"
        elif any(q in user_query for q in ["示例", "例子", "代码"]):
            return "example"
        elif any(q in user_query for q in ["练习", "习题", "题目"]):
            return "practice"
        else:
            return "general"

    def _generate_knowledge_id(self, query: str) -> str:
        """
        生成知识ID

        Args:
            query: 查询内容

        Returns:
            唯一ID
        """
        import hashlib
        return hashlib.md5(query.encode()).hexdigest()

    def _get_current_timestamp(self) -> str:
        """
        获取当前时间戳

        Returns:
            ISO格式时间戳
        """
        from datetime import datetime
        return datetime.now().isoformat()

    def _calculate_importance(self, query: str) -> float:
        """
        计算重要性分数

        Args:
            query: 查询内容

        Returns:
            0-1之间的重要性分数
        """
        important_terms = [
            "核心", "基础", "重要", "关键", "常用", "必须",
            "装饰器", "迭代器", "生成器", "闭包", "算法", "数据结构"
        ]

        count = 0
        for term in important_terms:
            if term in query:
                count += 1

        return min(count * 0.2, 1.0)

    def _determine_review_priority(self) -> str:
        """
        确定复习优先级

        Returns:
            复习优先级
        """
        return "normal"  # high, normal, low

    def _record_learning_progress(
        self,
        user_query: str,
        validation_result: Dict[str, Any],
        mastery_level: str,
    ) -> Dict[str, Any]:
        """
        记录学习进度

        Args:
            user_query: 用户查询
            validation_result: 验证结果
            mastery_level: 掌握程度

        Returns:
            学习进度记录
        """
        score = validation_result.get("score", 0)

        return {
            "topic": user_query,
            "score": score,
            "mastery_level": mastery_level,
            "completion_time": self._get_current_timestamp(),
            "practice_completed": self._count_practice_completed(
                validation_result.get("feedback", "")
            ),
            "needs_review": score < 0.8,
        }

    def _count_practice_completed(self, feedback: str) -> int:
        """
        计算练习完成数量

        Args:
            feedback: 反馈内容

        Returns:
            完成数量
        """
        if not feedback:
            return 0
        return feedback.count("完成") + feedback.count("已完成")
