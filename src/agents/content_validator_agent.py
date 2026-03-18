#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容验证Agent：校验所有输出内容的准确性，验证代码可运行性，保证教学内容正确
"""

from src.agents.base_agent import BaseAgent
import logging
import sys
import subprocess
import tempfile
import os

logger = logging.getLogger(__name__)


class ContentValidatorAgent(BaseAgent):
    """
    内容验证Agent，负责验证代码和内容准确性
    """

    def __init__(self):
        super().__init__("content_validator")

    def validate_code_syntax(self, code: str, language: str = "python") -> dict:
        """
        验证代码语法（使用Python内置编译器）

        Args:
            code: 代码
            language: 编程语言

        Returns:
            验证结果
        """
        if language.lower() != "python":
            return {
                "syntax_ok": False,
                "error": f"暂不支持 {language} 语言的本地验证"
            }

        try:
            # 尝试编译代码
            compile(code, "<string>", "exec")
            return {
                "syntax_ok": True,
                "error": None
            }
        except SyntaxError as e:
            return {
                "syntax_ok": False,
                "error": f"语法错误: 第{e.lineno}行, 第{e.offset}列: {e.msg}"
            }
        except Exception as e:
            return {
                "syntax_ok": False,
                "error": f"编译错误: {str(e)}"
            }

    def validate_code(self, code: str, language: str = "python") -> str:
        """
        验证代码的可运行性

        Args:
            code: 代码
            language: 编程语言

        Returns:
            验证结果
        """
        # 先进行本地语法检查
        local_validation = self.validate_code_syntax(code, language)

        # 再使用LLM进行深度验证
        prompt = self._format_prompt(
            "validate_code_prompt",
            {
                "code": code,
                "language": language
            }
        )
        if not prompt:
            return "提示词配置错误"

        llm_result = self._call_llm(prompt)

        # 合并本地验证和LLM验证结果
        result = f"本地语法检查: {'通过' if local_validation['syntax_ok'] else '失败'}\n"
        if local_validation.get("error"):
            result += f"本地错误信息: {local_validation['error']}\n"
        result += "\n" + "="*50 + "\n\n"
        result += "深度分析:\n"
        result += llm_result

        return result

    def validate_content(self, content: str) -> str:
        """
        验证教学内容的准确性

        Args:
            content: 教学内容

        Returns:
            验证结果
        """
        prompt = self._format_prompt("validate_content_prompt", {"content": content})
        if not prompt:
            return "提示词配置错误"

        return self._call_llm(prompt)

    def run(self, inputs: dict) -> dict:
        """
        执行内容验证任务

        Args:
            inputs: 输入参数
                - action: 动作类型，可选值：validate_code 验证代码，validate_content 验证内容
                - code: 代码（validate_code时需要）
                - language: 编程语言（validate_code时可选，默认python）
                - content: 教学内容（validate_content时需要）

        Returns:
            处理结果
        """
        try:
            action = inputs.get("action", "validate_code")

            if action == "validate_code":
                code = inputs.get("code", "")
                language = inputs.get("language", "python")

                if not code:
                    return {
                        "success": False,
                        "error": "请提供要验证的代码"
                    }

                result = self.validate_code(code, language)
            elif action == "validate_content":
                content = inputs.get("content", "")

                if not content:
                    return {
                        "success": False,
                        "error": "请提供要验证的内容"
                    }

                result = self.validate_content(content)
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
            logger.error(f"ContentValidatorAgent运行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    # 测试ContentValidatorAgent
    agent = ContentValidatorAgent()

    # 测试代码验证（正确代码）
    test_code1 = """
def calculate_average(numbers):
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

print(calculate_average([1, 2, 3, 4, 5]))
    """.strip()

    print("=== 代码验证测试（正确代码）===\n")
    result1 = agent.run({
        "action": "validate_code",
        "code": test_code1,
        "language": "python"
    })
    print(f"成功: {result1['success']}")
    print(f"结果:\n{result1['result']}")
    print("\n" + "="*50 + "\n")

    # 测试代码验证（有语法错误的代码）
    test_code2 = """
def calculate_average(numbers)
    total = 0
    for num in numbers
        total += num
    return total / len(numbers)
    """.strip()

    print("=== 代码验证测试（错误代码）===\n")
    result2 = agent.run({
        "action": "validate_code",
        "code": test_code2,
        "language": "python"
    })
    print(f"成功: {result2['success']}")
    print(f"结果:\n{result2['result']}")
    print("\n" + "="*50 + "\n")

    # 测试内容验证
    test_content = """
    在Python中，变量不需要声明类型，你可以直接赋值。
    例如：
    x = 10
    y = "hello"
    Python使用缩进来表示代码块。
    """.strip()

    print("=== 内容验证测试 ===\n")
    result3 = agent.run({
        "action": "validate_content",
        "content": test_content
    })
    print(f"成功: {result3['success']}")
    print(f"结果:\n{result3['result']}")
