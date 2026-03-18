"""
个性化讲解Agent
负责根据用户水平生成个性化的讲解内容
"""

import logging
from typing import Any, Dict, List, Optional
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ExplanationAgent(BaseAgent):
    """
    个性化讲解Agent
    """

    def __init__(self):
        super().__init__("ExplanationAgent")

    def process(
        self,
        user_query: str,
        user_level: str,
        related_knowledge: Optional[List[Dict[str, Any]]] = None,
        understanding_result: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """
        生成个性化讲解

        Args:
            user_query: 用户查询
            user_level: 用户水平
            related_knowledge: 相关知识
            understanding_result: 理解结果

        Returns:
            讲解内容
        """
        logger.info(f"生成个性化讲解: {user_query}")

        if not self.validate_input(["user_query", "user_level"],
                                    user_query=user_query, user_level=user_level):
            return "抱歉，缺少必要的信息来生成讲解。"

        try:
            prompt = self._build_prompt(
                user_query, user_level, related_knowledge, understanding_result
            )
            explanation = self._call_llm(prompt)

            self.log_process(
                {"user_query": user_query, "user_level": user_level},
                {"explanation_length": len(explanation)},
            )

            return explanation
        except Exception as e:
            logger.error(f"ExplanationAgent 处理失败: {e}")
            return self._get_fallback_explanation(user_query, user_level)

    def _build_prompt(
        self,
        user_query: str,
        user_level: str,
        related_knowledge: Optional[List[Dict[str, Any]]],
        understanding_result: Optional[Dict[str, Any]],
    ) -> str:
        """
        构建提示词

        Args:
            user_query: 用户查询
            user_level: 用户水平
            related_knowledge: 相关知识
            understanding_result: 理解结果

        Returns:
            提示词字符串
        """
        system_prompt = self.prompts.get("system_prompt", "")

        related_knowledge_str = ""
        if related_knowledge and len(related_knowledge) > 0:
            related_knowledge_str = "用户已掌握的相关知识:\n"
            for i, knowledge in enumerate(related_knowledge[:3]):
                title = knowledge.get("title", "未知")
                content = knowledge.get("content", "")[:200]
                related_knowledge_str += f"{i+1}. {title}: {content}...\n"

        understanding_str = ""
        if understanding_result:
            understanding_str = f"理解评估结果:\n{json.dumps(understanding_result, ensure_ascii=False, indent=2)}\n"

        prompt = f"""{system_prompt}

用户问题: {user_query}
用户水平: {user_level}
{related_knowledge_str}
{understanding_str}

请直接给出讲解内容，不要包含任何额外的说明文字。"""

        return prompt

    def _get_fallback_explanation(self, user_query: str, user_level: str) -> str:
        """
        获取降级讲解内容

        Args:
            user_query: 用户查询
            user_level: 用户水平

        Returns:
            降级讲解内容
        """
        return f"""## 关于 "{user_query}" 的讲解

感谢您的提问！这是一个关于编程学习的好问题。

### 学习建议

1. **从基础开始**：确保理解核心概念
2. **动手实践**：编写代码是最好的学习方式
3. **阅读文档**：官方文档是最权威的资料
4. **多做练习**：通过练习巩固知识
5. **查看优秀代码**：学习他人的编码风格

### 下一步

基于您的问题，我建议：
- 先了解基本概念
- 然后看一些示例代码
- 最后动手做一些练习

请告诉我您具体想了解哪方面，我可以提供更有针对性的讲解！"""


import json
