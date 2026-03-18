"""
知识库
管理静态的学习资源和知识
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    知识库类
    """

    def __init__(self):
        """
        初始化知识库
        """
        self.knowledge_items: List[Dict[str, Any]] = []
        self._initialize_default_knowledge()

        logger.info("初始化知识库")

    def _initialize_default_knowledge(self):
        """
        初始化默认知识
        """
        # 添加 Python 基础概念
        self._add_python_basics()

        # 添加装饰器知识
        self._add_decorator_knowledge()

        # 添加迭代器知识
        self._add_iterator_knowledge()

        # 添加生成器知识
        self._add_generator_knowledge()

    def _add_python_basics(self):
        """
        添加 Python 基础知识
        """
        self.knowledge_items.extend([
            {
                "id": "python_variables",
                "title": "Python 变量和数据类型",
                "content": "Python 是动态类型语言，变量不需要声明类型...",
                "topics": ["Python", "基础"],
                "keywords": ["变量", "类型", "整数", "字符串", "列表", "字典"],
                "difficulty": "basic",
                "type": "concept",
            },
            {
                "id": "python_functions",
                "title": "Python 函数",
                "content": "函数是组织好的、可重复使用的代码块...",
                "topics": ["Python", "函数"],
                "keywords": ["函数", "def", "参数", "返回值"],
                "difficulty": "basic",
                "type": "concept",
            },
        ])

    def _add_decorator_knowledge(self):
        """
        添加装饰器知识
        """
        self.knowledge_items.extend([
            {
                "id": "decorator_concept",
                "title": "Python 装饰器基础概念",
                "content": "装饰器是 Python 中用于修改函数或类行为的设计模式。"
                           "它允许在不修改原函数代码的情况下，给函数添加额外功能。",
                "topics": ["Python", "装饰器", "高级特性"],
                "keywords": ["装饰器", "decorator", "@", "wrapper"],
                "difficulty": "intermediate",
                "type": "concept",
            },
            {
                "id": "decorator_syntax",
                "title": "装饰器语法",
                "content": "使用 @ 符号来应用装饰器。装饰器本质上是一个接受函数作为"
                           "参数并返回一个新函数的函数。",
                "topics": ["Python", "装饰器", "语法"],
                "keywords": ["@", "语法", "函数", "嵌套"],
                "difficulty": "intermediate",
                "type": "syntax",
            },
            {
                "id": "decorator_use_cases",
                "title": "装饰器应用场景",
                "content": "装饰器的常见应用包括：日志记录、性能计时、权限验证、"
                           "输入验证、缓存、重试机制等。",
                "topics": ["Python", "装饰器", "应用"],
                "keywords": ["日志", "计时", "权限", "缓存", "重试"],
                "difficulty": "intermediate",
                "type": "application",
            },
            {
                "id": "decorator_functools_wraps",
                "title": "使用 functools.wraps",
                "content": "使用 @functools.wraps 来保留原函数的元信息，如名称、"
                           "文档字符串等。",
                "topics": ["Python", "装饰器", "最佳实践"],
                "keywords": ["functools", "wraps", "元信息"],
                "difficulty": "intermediate",
                "type": "best_practice",
            },
            {
                "id": "decorator_with_params",
                "title": "带参数的装饰器",
                "content": "带参数的装饰器需要三层嵌套：最外层接收参数，中间层接收"
                           "函数，最内层是包装函数。",
                "topics": ["Python", "装饰器", "高级"],
                "keywords": ["参数", "三层嵌套", "工厂函数"],
                "difficulty": "advanced",
                "type": "advanced",
            },
            {
                "id": "decorator_class",
                "title": "类装饰器",
                "content": "除了函数装饰器，还可以使用类来实现装饰器。类装饰器"
                           "需要实现 __call__ 方法。",
                "topics": ["Python", "装饰器", "类"],
                "keywords": ["类", "__call__", "状态管理"],
                "difficulty": "advanced",
                "type": "advanced",
            },
        ])

    def _add_iterator_knowledge(self):
        """
        添加迭代器知识
        """
        self.knowledge_items.extend([
            {
                "id": "iterator_concept",
                "title": "迭代器概念",
                "content": "迭代器是实现了迭代器协议的对象，包含 __iter__ 和 __next__ 方法。",
                "topics": ["Python", "迭代器"],
                "keywords": ["迭代器", "iterator", "__iter__", "__next__"],
                "difficulty": "intermediate",
                "type": "concept",
            },
            {
                "id": "iterator_protocol",
                "title": "迭代器协议",
                "content": "迭代器协议要求实现两个方法：__iter__ 返回迭代器自身，"
                           "__next__ 返回下一个元素或抛出 StopIteration。",
                "topics": ["Python", "迭代器", "协议"],
                "keywords": ["协议", "StopIteration"],
                "difficulty": "intermediate",
                "type": "concept",
            },
            {
                "id": "iterator_vs_iterable",
                "title": "迭代器 vs 可迭代对象",
                "content": "可迭代对象是可以被遍历的对象（如列表、字符串），"
                           "迭代器是实际执行遍历的对象。",
                "topics": ["Python", "迭代器"],
                "keywords": ["可迭代对象", "iter()", "next()"],
                "difficulty": "intermediate",
                "type": "comparison",
            },
        ])

    def _add_generator_knowledge(self):
        """
        添加生成器知识
        """
        self.knowledge_items.extend([
            {
                "id": "generator_concept",
                "title": "生成器概念",
                "content": "生成器是一种特殊的迭代器，使用 yield 关键字来产生值。",
                "topics": ["Python", "生成器"],
                "keywords": ["生成器", "generator", "yield"],
                "difficulty": "intermediate",
                "type": "concept",
            },
            {
                "id": "generator_functions",
                "title": "生成器函数",
                "content": "生成器函数使用 yield 而不是 return 来返回值。"
                           "每次调用 next() 时，函数从上次暂停的地方继续执行。",
                "topics": ["Python", "生成器", "函数"],
                "keywords": ["yield", "暂停", "继续"],
                "difficulty": "intermediate",
                "type": "concept",
            },
            {
                "id": "generator_expressions",
                "title": "生成器表达式",
                "content": "生成器表达式使用圆括号语法，是创建简单生成器的便捷方式。"
                           "与列表推导式不同，它是惰性计算的。",
                "topics": ["Python", "生成器", "表达式"],
                "keywords": ["生成器表达式", "惰性计算", "内存效率"],
                "difficulty": "intermediate",
                "type": "syntax",
            },
        ])

    def add(self, item: Dict[str, Any]):
        """
        添加知识项

        Args:
            item: 知识项
        """
        if "id" not in item:
            item["id"] = f"knowledge_{len(self.knowledge_items)}"

        self.knowledge_items.append(item)
        logger.debug(f"添加知识: {item.get('title', 'Untitled')}")

    def get(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """
        获取知识项

        Args:
            knowledge_id: 知识ID

        Returns:
            知识项
        """
        for item in self.knowledge_items:
            if item.get("id") == knowledge_id:
                return item.copy()
        return None

    def search(
        self,
        keywords: List[str],
        difficulty: Optional[str] = None,
        knowledge_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        搜索知识

        Args:
            keywords: 关键词列表
            difficulty: 难度过滤
            knowledge_type: 类型过滤
            limit: 返回结果数量限制

        Returns:
            搜索结果
        """
        results = []

        for item in self.knowledge_items:
            # 应用过滤条件
            if difficulty and item.get("difficulty") != difficulty:
                continue

            if knowledge_type and item.get("type") != knowledge_type:
                continue

            # 计算相关性
            relevance = self._calculate_relevance(item, keywords)
            if relevance > 0 or not keywords:
                item_copy = item.copy()
                item_copy["relevance"] = relevance if keywords else 1.0
                results.append(item_copy)

        # 按相关性排序
        results.sort(key=lambda x: x.get("relevance", 0), reverse=True)

        return results[:limit]

    def get_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """
        按主题获取知识

        Args:
            topic: 主题

        Returns:
            知识列表
        """
        results = []

        for item in self.knowledge_items:
            topics = item.get("topics", [])
            if topic in topics or topic.lower() in [t.lower() for t in topics]:
                results.append(item.copy())

        return results

    def get_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """
        按难度获取知识

        Args:
            difficulty: 难度

        Returns:
            知识列表
        """
        results = []

        for item in self.knowledge_items:
            if item.get("difficulty") == difficulty:
                results.append(item.copy())

        return results

    def update(self, knowledge_id: str, updates: Dict[str, Any]):
        """
        更新知识项

        Args:
            knowledge_id: 知识ID
            updates: 更新内容
        """
        for item in self.knowledge_items:
            if item.get("id") == knowledge_id:
                item.update(updates)
                logger.debug(f"更新知识: {knowledge_id}")
                break

    def delete(self, knowledge_id: str) -> bool:
        """
        删除知识项

        Args:
            knowledge_id: 知识ID

        Returns:
            是否成功
        """
        for i, item in enumerate(self.knowledge_items):
            if item.get("id") == knowledge_id:
                del self.knowledge_items[i]
                logger.debug(f"删除知识: {knowledge_id}")
                return True
        return False

    def get_all_topics(self) -> List[str]:
        """
        获取所有主题

        Returns:
            主题列表
        """
        topics = set()
        for item in self.knowledge_items:
            for topic in item.get("topics", []):
                topics.add(topic)
        return sorted(list(topics))

    def size(self) -> int:
        """
        获取知识数量

        Returns:
            知识数量
        """
        return len(self.knowledge_items)

    def _calculate_relevance(self, item: Dict[str, Any], keywords: List[str]) -> float:
        """
        计算相关性

        Args:
            item: 知识项
            keywords: 关键词

        Returns:
            相关性分数
        """
        if not keywords:
            return 1.0

        item_text = (
            item.get("title", "") + " " +
            item.get("content", "") + " " +
            " ".join(item.get("topics", [])) + " " +
            " ".join(item.get("keywords", []))
        ).lower()

        match_count = 0
        for keyword in keywords:
            if keyword.lower() in item_text:
                match_count += 1

        return match_count / len(keywords) if keywords else 0.0

    def export(self) -> List[Dict[str, Any]]:
        """
        导出知识库

        Returns:
            知识列表
        """
        return self.knowledge_items.copy()

    def import_(self, items: List[Dict[str, Any]]):
        """
        导入知识

        Args:
            items: 知识列表
        """
        for item in items:
            self.add(item)

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息
        """
        total = len(self.knowledge_items)

        # 按难度统计
        difficulty_stats = {}
        for item in self.knowledge_items:
            diff = item.get("difficulty", "unknown")
            difficulty_stats[diff] = difficulty_stats.get(diff, 0) + 1

        # 按类型统计
        type_stats = {}
        for item in self.knowledge_items:
            t = item.get("type", "unknown")
            type_stats[t] = type_stats.get(t, 0) + 1

        return {
            "total_items": total,
            "difficulty_stats": difficulty_stats,
            "type_stats": type_stats,
            "topics": self.get_all_topics(),
        }
