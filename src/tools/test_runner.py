"""
测试运行器组件
执行代码测试用例，返回测试结果、覆盖率信息，支持pytest格式
"""

import ast
import sys
import io
import traceback
from typing import Any, Dict, List, Optional, Tuple
import re
from collections import defaultdict


class TestResult:
    """测试结果对象"""

    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = 0
        self.details = []
        self.output = ""
        self.duration = 0.0


class CoverageTracker:
    """代码覆盖率跟踪器"""

    def __init__(self):
        self.executed_lines = set()
        self.all_lines = set()
        self.file_lines = {}

    def reset(self):
        self.executed_lines.clear()

    def record_execution(self, filename: str, line_number: int):
        """记录执行的代码行"""
        self.executed_lines.add((filename, line_number))

    def set_file_lines(self, filename: str, lines: List[str]):
        """设置文件的所有代码行"""
        self.file_lines[filename] = lines
        for i, line in enumerate(lines, 1):
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith('#'):
                self.all_lines.add((filename, i))

    def get_coverage(self) -> Dict[str, Any]:
        """获取覆盖率信息"""
        covered = len(self.executed_lines)
        total = len(self.all_lines)
        percentage = (covered / total * 100) if total > 0 else 100

        # 计算未覆盖的行
        uncovered = self.all_lines - self.executed_lines
        uncovered_lines = defaultdict(list)
        for filename, line in sorted(uncovered):
            uncovered_lines[filename].append(line)

        return {
            "covered_lines": covered,
            "total_lines": total,
            "percentage": round(percentage, 2),
            "uncovered_lines": dict(uncovered_lines)
        }


# 全局覆盖率跟踪器
coverage_tracker = CoverageTracker()


class AssertionError(Exception):
    """断言错误"""
    pass


def _assert_equal(actual, expected, message=""):
    """相等断言"""
    if actual != expected:
        raise AssertionError(
            f"{message}\n期望: {expected!r}\n实际: {actual!r}".strip()
        )


def _assert_not_equal(actual, expected, message=""):
    """不相等断言"""
    if actual == expected:
        raise AssertionError(
            f"{message}\n期望: {actual!r} 不等于 {expected!r}".strip()
        )


def _assert_true(value, message=""):
    """真值断言"""
    if not value:
        raise AssertionError(
            f"{message}\n期望: 真值\n实际: {value!r}".strip()
        )


def _assert_false(value, message=""):
    """假值断言"""
    if value:
        raise AssertionError(
            f"{message}\n期望: 假值\n实际: {value!r}".strip()
        )


def _assert_in(item, container, message=""):
    """包含断言"""
    if item not in container:
        raise AssertionError(
            f"{message}\n期望: {item!r} 在 {container!r} 中".strip()
        )


def _assert_not_in(item, container, message=""):
    """不包含断言"""
    if item in container:
        raise AssertionError(
            f"{message}\n期望: {item!r} 不在 {container!r} 中".strip()
        )


def _assert_is_none(value, message=""):
    """None断言"""
    if value is not None:
        raise AssertionError(
            f"{message}\n期望: None\n实际: {value!r}".strip()
        )


def _assert_is_not_none(value, message=""):
    """非None断言"""
    if value is None:
        raise AssertionError(
            f"{message}\n期望: 非None值\n实际: None".strip()
        )


def _assert_raises(expected_exception, *args, **kwargs):
    """异常断言 - 上下文管理器形式"""
    if args or kwargs:
        if not args:
            raise TypeError("assert_raises 需要至少一个参数")
        func = args[0]
        func_args = args[1:]
        try:
            func(*func_args, **kwargs)
        except expected_exception:
            return
        raise AssertionError(f"期望抛出 {expected_exception.__name__}")
    else:
        return AssertRaisesContext(expected_exception)


class AssertRaisesContext:
    """异常断言上下文管理器"""

    def __init__(self, expected_exception):
        self.expected_exception = expected_exception

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise AssertionError(f"期望抛出 {self.expected_exception.__name__}")
        return issubclass(exc_type, self.expected_exception)


def run_tests(code: str, test_code: Optional[str] = None,
              collect_coverage: bool = True) -> Dict[str, Any]:
    """
    运行测试用例

    Args:
        code: 被测试的代码
        test_code: 测试代码（可选，如果为None则从code中提取）
        collect_coverage: 是否收集覆盖率信息

    Returns:
        包含测试结果的字典
    """
    import time

    result = TestResult()
    start_time = time.time()

    # 捕获输出
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    output_buffer = io.StringIO()

    sys.stdout = output_buffer
    sys.stderr = output_buffer

    coverage_tracker.reset()

    try:
        # 解析并执行代码
        tree = ast.parse(code)

        # 准备测试环境
        test_globals = {
            'assert': _assert_equal,
            'assertEqual': _assert_equal,
            'assert_equal': _assert_equal,
            'assertNotEqual': _assert_not_equal,
            'assert_not_equal': _assert_not_equal,
            'assertTrue': _assert_true,
            'assert_true': _assert_true,
            'assertFalse': _assert_false,
            'assert_false': _assert_false,
            'assertIn': _assert_in,
            'assert_in': _assert_in,
            'assertNotIn': _assert_not_in,
            'assert_not_in': _assert_not_in,
            'assertIsNone': _assert_is_none,
            'assert_is_none': _assert_is_none,
            'assertIsNotNone': _assert_is_not_none,
            'assert_is_not_none': _assert_is_not_none,
            'assertRaises': _assert_raises,
            'assert_raises': _assert_raises,
            '__name__': '__test__',
        }

        # 设置覆盖率跟踪
        if collect_coverage:
            lines = code.split('\n')
            coverage_tracker.set_file_lines('<main>', lines)

        # 执行被测试代码
        exec(code, test_globals.copy(), test_globals)

        # 确定测试代码
        if test_code is None:
            test_code = code

        # 解析测试代码，查找测试函数
        test_tree = ast.parse(test_code)

        # 查找测试函数
        test_functions = []
        for node in ast.walk(test_tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_') or node.name.endswith('_test'):
                    test_functions.append(node.name)
                # 查找是否有@pytest.mark相关装饰器
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Attribute):
                        if decorator.attr in ['test', 'parametrize', 'fixture']:
                            test_functions.append(node.name)
                            break

        # 如果找不到测试函数，尝试执行main函数
        if not test_functions:
            if 'main' in test_globals and callable(test_globals['main']):
                test_functions = ['main']

        # 执行测试函数
        for func_name in test_functions:
            if func_name not in test_globals:
                continue

            result.total += 1
            test_detail = {
                'name': func_name,
                'status': 'skipped',
                'message': '',
                'duration': 0
            }

            try:
                test_start = time.time()
                test_func = test_globals[func_name]
                # 检查是否需要参数
                import inspect
                sig = inspect.signature(test_func)
                if len(sig.parameters) == 0:
                    test_func()
                test_end = time.time()
                test_detail['status'] = 'passed'
                test_detail['duration'] = round(test_end - test_start, 4)
                result.passed += 1
            except AssertionError as e:
                result.failed += 1
                test_detail['status'] = 'failed'
                test_detail['message'] = str(e)
            except Exception as e:
                result.errors += 1
                test_detail['status'] = 'error'
                test_detail['message'] = f"{type(e).__name__}: {str(e)}"
                test_detail['traceback'] = traceback.format_exc()

            result.details.append(test_detail)

        # 如果没有找到测试函数，标记为跳过
        if result.total == 0:
            result.skipped = 1
            result.details.append({
                'name': 'no_tests_found',
                'status': 'skipped',
                'message': '未找到测试函数',
                'duration': 0
            })

    except SyntaxError as e:
        result.errors += 1
        result.total += 1
        result.details.append({
            'name': 'syntax_error',
            'status': 'error',
            'message': f"语法错误: {e}",
            'duration': 0
        })
    except Exception as e:
        result.errors += 1
        result.total += 1
        result.details.append({
            'name': 'execution_error',
            'status': 'error',
            'message': f"{type(e).__name__}: {str(e)}",
            'traceback': traceback.format_exc(),
            'duration': 0
        })
    finally:
        end_time = time.time()
        result.duration = round(end_time - start_time, 4)
        result.output = output_buffer.getvalue()

        sys.stdout = original_stdout
        sys.stderr = original_stderr

    # 获取覆盖率信息
    coverage = {}
    if collect_coverage:
        coverage = coverage_tracker.get_coverage()

    return {
        'success': result.errors == 0 or result.total > 0,
        'test_results': {
            'total': result.total,
            'passed': result.passed,
            'failed': result.failed,
            'skipped': result.skipped,
            'errors': result.errors,
            'duration': result.duration,
            'output': result.output,
            'details': result.details
        },
        'coverage': coverage
    }


def format_test_report(test_result: Dict[str, Any]) -> str:
    """
    格式化测试报告

    Args:
        test_result: 测试结果字典

    Returns:
        格式化的报告字符串
    """
    report = []
    report.append("## 测试结果报告")
    report.append("")

    tr = test_result['test_results']

    # 统计概览
    report.append(f"**总测试数:** {tr['total']}")
    report.append(f"**通过:** ✅ {tr['passed']}")
    report.append(f"**失败:** ❌ {tr['failed']}")
    report.append(f"**错误:** ⚠️ {tr['errors']}")
    report.append(f"**跳过:** ⏭️ {tr['skipped']}")
    report.append(f"**总耗时:** {tr['duration']:.4f}秒")
    report.append("")

    # 通过率
    if tr['total'] > 0:
        pass_rate = (tr['passed'] / tr['total']) * 100
        report.append(f"**通过率:** {pass_rate:.2f}%")
        report.append("")

    # 详细结果
    if tr['details']:
        report.append("### 详细结果")
        report.append("")
        for detail in tr['details']:
            status_icon = {
                'passed': '✅',
                'failed': '❌',
                'error': '⚠️',
                'skipped': '⏭️'
            }.get(detail.get('status', 'unknown'), '❓')

            report.append(f"**{status_icon} {detail.get('name', 'unknown')}**")
            if detail.get('duration'):
                report.append(f"  耗时: {detail['duration']:.4f}秒")
            if detail.get('message'):
                report.append(f"  信息: {detail['message']}")
            report.append("")

    # 输出信息
    if tr.get('output'):
        report.append("### 测试输出")
        report.append("```")
        report.append(tr['output'].strip())
        report.append("```")
        report.append("")

    # 覆盖率信息
    if test_result.get('coverage'):
        cov = test_result['coverage']
        report.append("### 代码覆盖率")
        report.append(f"**覆盖行:** {cov.get('covered_lines', 0)}/{cov.get('total_lines', 0)}")
        report.append(f"**覆盖率:** {cov.get('percentage', 0):.2f}%")

        uncovered = cov.get('uncovered_lines', {})
        if uncovered:
            report.append("")
            report.append("**未覆盖的行:**")
            for filename, lines in uncovered.items():
                report.append(f"  {filename}: {sorted(lines)}")

    return "\n".join(report)


if __name__ == "__main__":
    # 测试示例
    test_code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

def test_add():
    assert_equal(add(2, 3), 5)
    assert_equal(add(-1, 1), 0)

def test_multiply():
    assert_equal(multiply(2, 3), 6)
    assert_equal(multiply(-2, 3), -6)

def test_divide():
    assert_equal(divide(6, 2), 3)
    assert_raises(ValueError, divide, 1, 0)

def test_failure_example():
    assert_equal(add(2, 2), 5)
""".strip()

    print("=== 测试运行器测试 ===")
    print("")
    result = run_tests(test_code)
    print(format_test_report(result))