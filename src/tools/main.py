"""
智能编程学习导师项目 - 工具层主入口
提供统一的工具调用接口
"""

from typing import Any, Dict, Optional
import sys
import os

# 确保能导入同级模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tools.code_interpreter import run_code, validate_code
from src.tools.static_analyzer import analyze_code_quality, format_analysis_report
from src.tools.test_runner import run_tests, format_test_report
from src.tools.document_retriever import (
    search_documents, get_concept, get_categories,
    get_concepts_by_category, format_document_result
)


def execute_tool(tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    统一的工具执行接口

    Args:
        tool_name: 工具名称（code_interpreter/static_analyzer/test_runner/document_retriever）
        input_data: 工具输入数据

    Returns:
        工具执行结果
    """
    try:
        if tool_name == "code_interpreter":
            return run_code(**input_data)
        elif tool_name == "static_analyzer":
            return analyze_code_quality(**input_data)
        elif tool_name == "test_runner":
            return run_tests(**input_data)
        elif tool_name == "document_retriever":
            return _run_document_retriever(**input_data)
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _run_document_retriever(action: str, **kwargs) -> Dict[str, Any]:
    """
    文档检索工具的统一接口

    Args:
        action: 操作类型（search/get/...）
        **kwargs: 其他参数

    Returns:
        工具执行结果
    """
    if action == "search":
        results = search_documents(**kwargs)
        return {
            "success": True,
            "action": "search",
            "results": results
        }
    elif action == "get":
        name = kwargs.get("name")
        if not name:
            return {
                "success": False,
                "error": "Name parameter required"
            }
        concept = get_concept(name)
        return {
            "success": True,
            "action": "get",
            "result": concept
        }
    elif action == "categories":
        categories = get_categories()
        return {
            "success": True,
            "action": "categories",
            "results": categories
        }
    elif action == "category_concepts":
        category = kwargs.get("category")
        if not category:
            return {
                "success": False,
                "error": "Category parameter required"
            }
        concepts = get_concepts_by_category(category)
        return {
            "success": True,
            "action": "category_concepts",
            "results": concepts
        }
    else:
        return {
            "success": False,
            "error": f"Unknown document retriever action: {action}"
        }


def main():
    """主函数（用于测试）"""
    print("=== 智能编程学习导师工具层 ===")

    # 测试代码解释器
    print("\n1. 代码解释器测试:")
    code = """
x = 10
y = 20
print(f"x + y = {x + y}")
"""
    result = run_code(code)
    print(f"成功: {result['success']}")
    print(f"输出: {result['output']}")

    # 测试静态分析工具
    print("\n2. 静态分析工具测试:")
    code = """
def calculate_average(numbers):
    sum = 0
    count = 0
    for num in numbers:
        if num > 0:
            sum += num
            count += 1
    if count > 0:
        return sum / count
    else:
        return 0
"""
    analysis = analyze_code_quality(code)
    print(format_analysis_report(analysis))

    # 测试测试运行器
    print("\n3. 测试运行器测试:")
    code = """
def add(a, b):
    return a + b

def test_add():
    from src.tools.test_runner import _assert_equal
    _assert_equal(add(2, 3), 5)
    _assert_equal(add(-1, 1), 0)
"""
    test_result = run_tests(code, collect_coverage=True)
    print(format_test_report(test_result))

    # 测试文档检索工具
    print("\n4. 文档检索工具测试:")
    results = search_documents("函数", limit=2)
    for result in results:
        print(f"- {result['name']}: {result['description']}")

    print("\n=== 所有工具测试完成 ===")


if __name__ == "__main__":
    main()