#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误调试指导Agent：分析代码bug原因，给出修复建议和调试方法
"""

from src.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class DebuggingGuideAgent(BaseAgent):
    """
    错误调试指导Agent，负责分析bug和给出调试建议
    """

    def __init__(self):
        super().__init__("debugging_guide")

    def debug_error(self, code: str, error_message: str = "") -> str:
        """
        分析代码错误，找出问题并给出修复建议

        Args:
            code: 有bug的代码
            error_message: 错误信息（可选）

        Returns:
            调试建议
        """
        prompt = self._format_prompt(
            "debug_prompt",
            {
                "code": code,
                "error_message": error_message or "未提供错误信息"
            }
        )
        if not prompt:
            return "提示词配置错误"

        return self._call_llm(prompt)

    def optimize_code(self, code: str) -> str:
        """
        分析代码，找出优化点并提供优化方案

        Args:
            code: 要优化的代码

        Returns:
            优化建议
        """
        prompt = self._format_prompt("optimize_prompt", {"code": code})
        if not prompt:
            return "提示词配置错误"

        return self._call_llm(prompt)

    def run(self, inputs: dict) -> dict:
        """
        执行错误调试或代码优化任务

        Args:
            inputs: 输入参数
                - action: 动作类型，可选值：debug 调试，optimize 优化
                - code: 代码
                - error_message: 错误信息（debug时可选）

        Returns:
            处理结果
        """
        try:
            action = inputs.get("action", "debug")
            code = inputs.get("code", "")

            if not code:
                return {
                    "success": False,
                    "error": "请提供要处理的代码"
                }

            if action == "debug":
                error_message = inputs.get("error_message", "")
                result = self.debug_error(code, error_message)
            elif action == "optimize":
                result = self.optimize_code(code)
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
            logger.error(f"DebuggingGuideAgent运行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    # 测试DebuggingGuideAgent
    agent = DebuggingGuideAgent()

    # 测试错误调试
    test_code1 = """
def divide(a, b):
    return a / b

result = divide(10, 0)
print(result)
    """.strip()

    test_error = """
Traceback (most recent call last):
  File "test.py", line 5, in <module>
    result = divide(10, 0)
  File "test.py", line 3, in divide
    return a / b
ZeroDivisionError: division by zero
    """.strip()

    print("=== 错误调试测试 ===\n")
    result1 = agent.run({
        "action": "debug",
        "code": test_code1,
        "error_message": test_error
    })
    print(f"成功: {result1['success']}")
    print(f"结果:\n{result1['result']}")
    print("\n" + "="*50 + "\n")

    # 测试代码优化
    test_code2 = """
def find_max(numbers):
    max_num = numbers[0]
    for i in range(len(numbers)):
        if numbers[i] > max_num:
            max_num = numbers[i]
    return max_num

data = [3, 1, 4, 1, 5, 9, 2, 6]
print(find_max(data))
    """.strip()

    print("=== 代码优化测试 ===\n")
    result2 = agent.run({
        "action": "optimize",
        "code": test_code2
    })
    print(f"成功: {result2['success']}")
    print(f"结果:\n{result2['result']}")
