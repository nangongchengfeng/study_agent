"""
工具层单元测试
验证所有工具组件功能正常
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tools.code_interpreter import run_code, validate_code
from src.tools.static_analyzer import analyze_code_quality
from src.tools.test_runner import run_tests
from src.tools.document_retriever import (
    search_documents, get_concept, get_categories, get_concepts_by_category
)


def test_code_interpreter():
    """测试代码解释器"""
    print("=== 测试代码解释器 ===")

    # 测试安全代码执行
    safe_code = """
result = 0
for i in range(1, 6):
    result += i
print(f"1-5的和是: {result}")
"""
    result = run_code(safe_code)
    assert result["success"] is True, "安全代码应该成功执行"
    assert "1-5的和是: 15" in result["output"], "输出应该包含计算结果"
    print("安全代码执行成功")

    # 测试危险代码
    dangerous_code = """
import os
os.system("echo dangerous command")
"""
    result = run_code(dangerous_code)
    assert result["success"] is False, "危险代码应该被阻止"
    assert len(result["errors"]) > 0, "应该有错误信息"
    print("危险代码正确阻止")

    # 测试代码验证
    valid_code = "x = 10\ny = 20\nprint(x + y)"
    errors = validate_code(valid_code)
    assert len(errors) == 0, "有效代码应该通过验证"
    print("代码验证功能正常")

    print("代码解释器测试通过\n")
    return True


def test_static_analyzer():
    """测试静态分析工具"""
    print("=== 测试静态分析工具 ===")

    test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def calculate_factorial(n):
    result = 1
    for i in range(1, n+1):
        result *= i
    return result

def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 100:
                if x > 1000:
                    return "very large"
                return "large"
            return "medium"
        return "small"
    return "negative"
"""
    analysis = analyze_code_quality(test_code)
    assert analysis["success"] is True, "分析应该成功"

    metrics = analysis["metrics"]
    assert metrics["lines"]["total"] > 0, "应该有行数统计"
    assert metrics["structure"]["functions"] == 3, "应该识别到3个函数"
    assert metrics["complexity"]["cyclomatic"] >= 1, "应该有圈复杂度计算"

    print(f"代码行数: {metrics['lines']['total']}")
    print(f"函数数量: {metrics['structure']['functions']}")
    print(f"圈复杂度: {metrics['complexity']['cyclomatic']}")
    print(f"质量得分: {metrics['quality_score']}/100")

    if analysis.get("issues"):
        print(f"发现 {len(analysis['issues'])} 个潜在问题")

    print("静态分析工具测试通过\n")
    return True


def test_test_runner():
    """测试测试运行器"""
    print("=== 测试测试运行器 ===")

    test_code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def test_add():
    from src.tools.test_runner import _assert_equal
    _assert_equal(add(2, 3), 5)
    _assert_equal(add(-1, 1), 0)

def test_multiply():
    from src.tools.test_runner import _assert_equal
    _assert_equal(multiply(2, 3), 6)
    _assert_equal(multiply(-2, 3), -6)
"""
    result = run_tests(test_code, collect_coverage=True)
    assert "test_results" in result, "应该有测试结果"
    assert "coverage" in result, "应该有覆盖率信息"

    tr = result["test_results"]
    assert tr["total"] >= 2, "应该至少有2个测试"
    print(f"测试总数: {tr['total']}")
    print(f"通过: {tr['passed']}, 失败: {tr['failed']}, 错误: {tr['errors']}")
    print(f"测试耗时: {tr['duration']:.4f}秒")

    cov = result["coverage"]
    if cov:
        print(f"代码覆盖率: {cov.get('percentage', 0):.2f}%")

    print("测试运行器测试通过\n")
    return True


def test_document_retriever():
    """测试文档检索工具"""
    print("=== 测试文档检索工具 ===")

    # 测试分类获取
    categories = get_categories()
    assert len(categories) > 0, "应该有分类"
    print(f"获取到 {len(categories)} 个分类: {categories[:5]}...")

    # 测试按分类获取概念
    if categories:
        concepts = get_concepts_by_category(categories[0])
        assert len(concepts) > 0, "分类下应该有概念"
        print(f"'{categories[0]}' 分类有 {len(concepts)} 个概念")

    # 测试搜索
    results = search_documents("函数", limit=3)
    assert len(results) > 0, "搜索应该有结果"
    print(f"搜索'函数'找到 {len(results)} 个结果:")
    for r in results:
        print(f"  - {r['name']}")

    # 测试获取单个概念
    concept = get_concept("for循环")
    assert concept is not None, "应该能找到'for循环'概念"
    print("获取'for循环'概念成功")
    assert "description" in concept, "应该有描述"
    assert "examples" in concept, "应该有示例"

    print("文档检索工具测试通过\n")
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("  工具层单元测试")
    print("=" * 50)
    print()

    tests = [
        ("代码解释器", test_code_interpreter),
        ("静态分析工具", test_static_analyzer),
        ("测试运行器", test_test_runner),
        ("文档检索工具", test_document_retriever),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(name + "测试失败:" + str(e))
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 50)
    print("测试结果: {} 通过, {} 失败".format(passed, failed))
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)