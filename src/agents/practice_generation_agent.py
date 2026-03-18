"""
练习生成Agent
负责生成练习题
"""

import logging
from typing import Any, Dict, List, Optional
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PracticeGenerationAgent(BaseAgent):
    """
    练习生成Agent
    """

    def __init__(self):
        super().__init__("PracticeGenerationAgent")

    def process(
        self,
        user_query: str,
        user_level: str,
        explanation: str,
        example: str,
        **kwargs,
    ) -> str:
        """
        生成练习题

        Args:
            user_query: 用户查询
            user_level: 用户水平
            explanation: 讲解内容
            example: 示例代码

        Returns:
            练习题
        """
        logger.info(f"生成练习题: {user_query}")

        if not self.validate_input(["user_query", "explanation"],
                                    user_query=user_query, explanation=explanation):
            return "抱歉，缺少必要信息来生成练习题。"

        try:
            prompt = self._build_prompt(user_query, user_level, explanation, example)
            practice = self._call_llm(prompt)

            self.log_process(
                {"user_query": user_query, "user_level": user_level},
                {"practice_length": len(practice)},
            )

            return practice
        except Exception as e:
            logger.error(f"PracticeGenerationAgent 处理失败: {e}")
            return self._get_fallback_practice(user_query, user_level)

    def _build_prompt(
        self,
        user_query: str,
        user_level: str,
        explanation: str,
        example: str,
    ) -> str:
        """
        构建提示词

        Args:
            user_query: 用户查询
            user_level: 用户水平
            explanation: 讲解内容
            example: 示例代码

        Returns:
            提示词字符串
        """
        system_prompt = self.prompts.get("system_prompt", "")

        prompt = f"""{system_prompt}

用户问题: {user_query}
用户水平: {user_level}
讲解内容:
{explanation}
示例代码:
{example}

请直接给出练习题，不要包含任何额外的说明文字。"""

        return prompt

    def _get_fallback_practice(self, user_query: str, user_level: str) -> str:
        """
        获取降级练习题

        Args:
            user_query: 用户查询
            user_level: 用户水平

        Returns:
            降级练习题
        """
        return f"""## 练习题

### 题目 1：基础练习
请根据刚才学习的内容，完成以下练习：

1. 理解核心概念
2. 尝试修改示例代码
3. 运行并观察结果

### 题目 2：拓展练习
尝试用学到的知识解决一个实际问题：

- 思考这个知识点可以应用在什么场景
- 写一个简单的应用示例
- 测试你的代码

### 提示
- 如果遇到困难，可以回顾讲解内容
- 多动手尝试，不要怕出错
- 有问题随时提问！"""
