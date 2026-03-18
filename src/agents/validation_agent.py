"""
验证Agent
负责验证用户的学习成果
"""

import logging
import json
from typing import Any, Dict, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ValidationAgent(BaseAgent):
    """
    验证Agent
    """

    def __init__(self):
        super().__init__("ValidationAgent")

    def process(
        self,
        user_query: str,
        user_level: str,
        practice_result: str,
        explanation: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        验证学习成果

        Args:
            user_query: 用户查询
            user_level: 用户水平
            practice_result: 练习结果
            explanation: 讲解内容

        Returns:
            验证结果
        """
        logger.info(f"执行学习验证: {user_query}")

        if not self.validate_input(["user_query", "practice_result"],
                                    user_query=user_query, practice_result=practice_result):
            return {"error": "缺少必需参数"}

        try:
            prompt = self._build_prompt(user_query, user_level, practice_result, explanation)
            response = self._call_llm(prompt)
            result = self._parse_response(response, user_query, user_level)

            self.log_process(
                {"user_query": user_query, "user_level": user_level},
                result,
            )

            return result
        except Exception as e:
            logger.error(f"ValidationAgent 处理失败: {e}")
            return self._get_fallback_result(user_query, user_level)

    def _build_prompt(
        self,
        user_query: str,
        user_level: str,
        practice_result: str,
        explanation: str,
    ) -> str:
        """
        构建提示词

        Args:
            user_query: 用户查询
            user_level: 用户水平
            practice_result: 练习结果
            explanation: 讲解内容

        Returns:
            提示词字符串
        """
        system_prompt = self.prompts.get("system_prompt", "")

        prompt = f"""{system_prompt}

用户问题: {user_query}
用户水平: {user_level}
讲解内容:
{explanation}
练习题:
{practice_result}

请返回JSON格式的结果，包含以下字段：
- score: 掌握分数（0-1的浮点数）
- feedback: 反馈文本
- needs_supplement: 是否需要补充讲解（true/false）
- suggestions: 建议列表（字符串数组）
- next_steps: 下一步学习建议列表（字符串数组）
- mastery_level: 掌握程度（mastered/proficient/developing/beginning）

请只返回JSON，不要包含任何额外的文本。"""

        return prompt

    def _parse_response(
        self,
        response: str,
        user_query: str,
        user_level: str,
    ) -> Dict[str, Any]:
        """
        解析LLM响应

        Args:
            response: LLM响应
            user_query: 用户查询
            user_level: 用户水平

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

            required_fields = ["score", "feedback", "needs_supplement", "suggestions", "next_steps", "mastery_level"]
            for field in required_fields:
                if field not in result:
                    result[field] = self._get_default_value(field, user_query, user_level)

            result["completion_score"] = result.get("score", 0.5)
            result["understanding_score"] = result.get("score", 0.5)

            return result
        except Exception as e:
            logger.warning(f"解析响应失败，使用默认值: {e}")
            return self._get_fallback_result(user_query, user_level)

    def _get_default_value(self, field: str, user_query: str, user_level: str) -> Any:
        """
        获取字段的默认值

        Args:
            field: 字段名
            user_query: 用户查询
            user_level: 用户水平

        Returns:
            默认值
        """
        defaults = {
            "score": 0.5,
            "feedback": "继续努力，你做得不错！",
            "needs_supplement": False,
            "suggestions": ["继续学习", "多做练习"],
            "next_steps": ["继续深入学习当前主题"],
            "mastery_level": "developing",
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
            "score": 0.5,
            "completion_score": 0.5,
            "understanding_score": 0.5,
            "feedback": "你有一定的基础，但还需要更多练习。💪\n\n建议：\n- 重新阅读讲解内容\n- 一步步完成每个练习\n- 不要着急，理解每个概念\n\n有任何问题随时问我！",
            "needs_supplement": False,
            "suggestions": [
                "建议完成所有练习题，动手写代码是最好的学习方式",
                "可以先从简单的题目开始，逐步增加难度",
                "定期复习，巩固记忆",
                "建立自己的代码笔记和示例库",
            ],
            "next_steps": [
                "继续深入学习当前主题",
                "寻找相关的实战项目",
                "定期复习已学内容",
            ],
            "mastery_level": "developing",
        }
