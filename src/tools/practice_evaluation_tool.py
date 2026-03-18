"""
练习评估工具
负责评估用户的练习完成情况
"""

import logging
from typing import Any, Dict
from .base_tool import BaseTool

logger = logging.getLogger(__name__)


class PracticeEvaluationTool(BaseTool):
    """
    练习评估工具
    """

    def __init__(self):
        super().__init__("PracticeEvaluationTool")

    def run(self, user_answer: str, expected_answer: str, **kwargs) -> Dict[str, Any]:
        """
        评估练习

        Args:
            user_answer: 用户答案
            expected_answer: 期望答案
            **kwargs: 可选参数

        Returns:
            评估结果
        """
        logger.info("执行练习评估工具")

        if not self.validate_input(["user_answer", "expected_answer"],
                                    user_answer=user_answer, expected_answer=expected_answer):
            return self.handle_error(
                ValueError("缺少答案参数"),
                {"user_answer": user_answer, "expected_answer": expected_answer},
            )

        try:
            score = self._calculate_score(user_answer, expected_answer)
            feedback = self._generate_feedback(user_answer, expected_answer, score)
            correctness = self._assess_correctness(score)

            return self.format_output({
                "score": score,
                "correctness": correctness,
                "feedback": feedback,
                "expected_answer": expected_answer,
                "user_answer": user_answer,
            })

        except Exception as e:
            return self.handle_error(e, {"user_answer": user_answer})

    def _calculate_score(self, user_answer: str, expected_answer: str) -> float:
        """
        计算分数

        Args:
            user_answer: 用户答案
            expected_answer: 期望答案

        Returns:
            分数 (0-1)
        """
        if not user_answer or len(user_answer.strip()) == 0:
            return 0.0

        # 简单的文本相似度计算（基于关键词匹配）
        user_tokens = self._tokenize_text(user_answer)
        expected_tokens = self._tokenize_text(expected_answer)

        matched_tokens = set(user_tokens) & set(expected_tokens)
        if not expected_tokens:
            return 0.0

        return len(matched_tokens) / len(expected_tokens)

    def _generate_feedback(self, user_answer: str, expected_answer: str, score: float) -> str:
        """
        生成反馈

        Args:
            user_answer: 用户答案
            expected_answer: 期望答案
            score: 分数

        Returns:
            反馈文本
        """
        if score >= 0.8:
            return "做得很好！答案非常接近正确答案。"

        elif score >= 0.6:
            return "答案不错，但还有一些要点需要补充。"

        elif score >= 0.4:
            return "答案有部分正确，但需要改进。建议重新检查。"

        else:
            return "答案与正确答案相差较大，建议重新思考和修改。"

    def _assess_correctness(self, score: float) -> str:
        """
        评估正确性

        Args:
            score: 分数

        Returns:
            正确性等级
        """
        if score >= 0.8:
            return "正确"
        elif score >= 0.6:
            return "基本正确"
        elif score >= 0.4:
            return "部分正确"
        else:
            return "不正确"

    def _tokenize_text(self, text: str) -> list:
        """
        文本分词

        Args:
            text: 原始文本

        Returns:
            词列表
        """
        import re

        # 移除标点符号和特殊字符
        text = re.sub(r'[^\w\s]', '', text)

        # 转换为小写
        text = text.lower()

        # 分割成单词
        tokens = text.split()

        # 移除停用词
        stop_words = ["的", "了", "在", "是", "就", "都", "而", "也", "和", "有",
                     "还有", "但是", "或者", "因为", "所以", "对于", "关于",
                     "一个", "这个", "那个"]

        return [token for token in tokens if token not in stop_words and len(token) > 1]

    def evaluate_code_similarity(self, user_code: str, expected_code: str) -> Dict[str, Any]:
        """
        评估代码相似度

        Args:
            user_code: 用户代码
            expected_code: 期望代码

        Returns:
            评估结果
        """
        logger.debug("评估代码相似度")

        try:
            score = self._calculate_code_similarity(user_code, expected_code)
            feedback = self._generate_code_feedback(user_code, expected_code, score)

            return self.format_output({
                "score": score,
                "feedback": feedback,
                "user_code": user_code,
                "expected_code": expected_code,
            })

        except Exception as e:
            return self.handle_error(e, {"user_code": user_code})

    def _calculate_code_similarity(self, code1: str, code2: str) -> float:
        """
        计算代码相似度

        Args:
            code1: 代码 1
            code2: 代码 2

        Returns:
            相似度分数 (0-1)
        """
        # 简单的代码相似度计算
        tokens1 = self._tokenize_code(code1)
        tokens2 = self._tokenize_code(code2)

        matched_tokens = set(tokens1) & set(tokens2)
        if not tokens2:
            return 0.0

        return len(matched_tokens) / len(tokens2)

    def _tokenize_code(self, code: str) -> list:
        """
        代码分词

        Args:
            code: 代码

        Returns:
            词列表
        """
        import re

        # 移除注释
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)

        # 分割成关键字和标识符
        tokens = re.findall(r'\w+', code)

        return [token.lower() for token in tokens if len(token) > 1]

    def _generate_code_feedback(self, user_code: str, expected_code: str, score: float) -> str:
        """
        生成代码评估反馈

        Args:
            user_code: 用户代码
            expected_code: 期望代码
            score: 相似度分数

        Returns:
            反馈文本
        """
        if score >= 0.8:
            return "代码非常接近正确答案，实现了预期功能。"

        elif score >= 0.6:
            return "代码结构和功能基本正确，但可能存在一些细微差别或优化空间。"

        elif score >= 0.4:
            return "代码有一些相关的结构，但可能没有完全实现预期功能。"

        else:
            return "代码与预期实现相差较大，建议重新检查和修改。"

    def run_code_evaluation(self, user_code: str, test_case: str) -> Dict[str, Any]:
        """
        运行代码评估

        Args:
            user_code: 用户代码
            test_case: 测试用例

        Returns:
            评估结果
        """
        logger.info("运行代码评估")

        from src.tools import CodeExecutionTool

        code_executor = CodeExecutionTool()

        try:
            # 执行用户代码
            result = code_executor.run_safe(user_code)

            if result.get("success", False):
                return self.format_output({
                    "score": 1.0,
                    "feedback": "代码执行成功！",
                    "execution_result": result,
                })
            else:
                return self.format_output({
                    "score": 0.0,
                    "feedback": f"代码执行失败: {result.get('stderr', '')}",
                    "execution_result": result,
                })

        except Exception as e:
            return self.handle_error(e, {"user_code": user_code})


# 工具的便捷方法
def evaluate_practice(user_answer: str, expected_answer: str, **kwargs):
    """
    便捷的练习评估方法

    Args:
        user_answer: 用户答案
        expected_answer: 期望答案
        **kwargs: 可选参数

    Returns:
        评估结果
    """
    tool = PracticeEvaluationTool()
    return tool.run(user_answer, expected_answer, **kwargs)


def evaluate_code(code: str, expected_code: str, **kwargs):
    """
    便捷的代码评估方法

    Args:
        code: 用户代码
        expected_code: 期望代码
        **kwargs: 可选参数

    Returns:
        评估结果
    """
    tool = PracticeEvaluationTool()
    return tool.evaluate_code_similarity(code, expected_code, **kwargs)
