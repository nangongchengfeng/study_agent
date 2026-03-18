"""
理解评估Agent
负责理解用户查询并评估其学习需求
"""

import logging
import json
from typing import Any, Dict, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class UnderstandingAgent(BaseAgent):
    """
    理解评估Agent
    """

    def __init__(self):
        super().__init__("UnderstandingAgent")

    def process(
        self,
        user_query: str,
        conversation_history: List[Dict[str, str]],
        user_level: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        处理用户查询理解

        Args:
            user_query: 用户查询
            conversation_history: 对话历史
            user_level: 用户水平

        Returns:
            理解结果
        """
        logger.info(f"处理用户查询理解: {user_query}")

        if not self.validate_input(["user_query", "user_level"],
                                    user_query=user_query, user_level=user_level):
            return {"error": "缺少必需参数"}

        try:
            prompt = self._build_prompt(user_query, conversation_history, user_level)
            response = self._call_llm(prompt)
            result = self._parse_response(response)

            self.log_process(
                {"user_query": user_query, "user_level": user_level},
                result,
            )

            return result
        except Exception as e:
            logger.error(f"UnderstandingAgent 处理失败: {e}")
            return self._get_fallback_result(user_query, user_level)

    def _build_prompt(
        self,
        user_query: str,
        conversation_history: List[Dict[str, str]],
        user_level: str,
    ) -> str:
        """
        构建提示词

        Args:
            user_query: 用户查询
            conversation_history: 对话历史
            user_level: 用户水平

        Returns:
            提示词字符串
        """
        system_prompt = self.prompts.get("system_prompt", "")

        context_summary = ""
        if conversation_history:
            recent = conversation_history[-3:]
            context_summary = "对话历史:\n"
            for msg in recent:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:100]
                context_summary += f"{role}: {content}...\n"

        prompt = f"""{system_prompt}

用户查询: {user_query}
用户水平: {user_level}
{context_summary}

请返回JSON格式的结果，不要包含任何额外的文本或markdown标记。"""

        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM响应

        Args:
            response: LLM响应

        Returns:
            解析后的字典
        """
        try:
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            json_str = json_str.strip()

            result = json.loads(json_str)

            required_fields = ["query_type", "topics", "learning_objective", "difficulty", "keywords"]
            for field in required_fields:
                if field not in result:
                    result[field] = self._get_default_value(field)

            return result
        except Exception as e:
            logger.warning(f"解析响应失败，使用默认值: {e}")
            return self._get_fallback_result("", "")

    def _get_default_value(self, field: str) -> Any:
        """
        获取字段的默认值

        Args:
            field: 字段名

        Returns:
            默认值
        """
        defaults = {
            "query_type": "general",
            "topics": ["general"],
            "learning_objective": "conceptual_understanding",
            "difficulty": "intermediate",
            "keywords": [],
            "confidence": 0.5,
            "requires_clarification": False,
            "clarification_questions": [],
            "context_summary": "",
        }
        return defaults.get(field, "")

    def _get_fallback_result(self, user_query: str, user_level: str) -> Dict[str, Any]:
        """
        获取降级结果

        Args:
            user_query: 用户查询
            user_level: 用户水平

        Returns:
            降级结果
        """
        return {
            "query_type": "general",
            "topics": ["general"],
            "learning_objective": "conceptual_understanding",
            "difficulty": "intermediate" if user_level == "intermediate" else "basic",
            "keywords": [word for word in user_query.split() if len(word) > 1][:10],
            "confidence": 0.5,
            "requires_clarification": False,
            "clarification_questions": [],
            "context_summary": "新对话，无历史上下文",
        }
