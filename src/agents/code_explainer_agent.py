#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码审查解释Agent：分析代码逻辑，生成生活化类比解释，输出易懂的代码解释
"""

from src.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class CodeExplainerAgent(BaseAgent):
    """
    代码审查解释Agent，负责分析代码逻辑，生成生活化类比解释
    """

    def __init__(self):
        super().__init__("code_explainer")

    def explain_code(self, code: str) -> str:
        """
        解释代码逻辑，生成生活化类比

        Args:
            code: 要解释的代码

        Returns:
            代码解释
        """
        prompt = self._format_prompt("explain_prompt", {"code": code})
        if not prompt:
            return "提示词配置错误"

        return self._call_llm(prompt)

    def review_code(self, code: str) -> str:
        """
        审查代码，分析逻辑和改进建议

        Args:
            code: 要审查的代码

        Returns:
            代码审查结果
        """
        prompt = self._format_prompt("review_prompt", {"code": code})
        if not prompt:
            return "提示词配置错误"

        return self._call_llm(prompt)

    def run(self, inputs: dict) -> dict:
        """
        执行代码解释或审查任务

        Args:
            inputs: 输入参数
                - code: 要处理的代码
                - action: 动作类型，可选值：explain 解释，review 审查

        Returns:
            处理结果
        """
        try:
            code = inputs.get("code", "")
            action = inputs.get("action", "explain")

            if not code:
                return {
                    "success": False,
                    "error": "请提供要分析的代码"
                }

            if action == "explain":
                result = self.explain_code(code)
            elif action == "review":
                result = self.review_code(code)
            else:
                return {
                    "success": False,
                    "error": "无效的动作类型"
                }

            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"CodeExplainerAgent运行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    # 测试CodeExplainerAgent
    agent = CodeExplainerAgent()

    # 测试代码解释
    test_code1 = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(5))
    """.strip()

    result1 = agent.run({"code": test_code1, "action": "explain"})
    print("=== 代码解释测试 ===\n")
    print(f"成功: {result1['success']}")
    print(f"结果:\n{result1['result']}")
    print("\n" + "="*50 + "\n")

    # 测试代码审查
    test_code2 = """
def calculate_average(numbers):
    sum = 0
    for i in numbers:
        sum += i
    return sum / len(numbers)

data = [1, 2, 3, 4, 5]
print(calculate_average(data))
    """.strip()

    result2 = agent.run({"code": test_code2, "action": "review"})
    print("=== 代码审查测试 ===\n")
    print(f"成功: {result2['success']}")
    print(f"结果:\n{result2['result']}")
