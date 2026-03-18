"""
静态分析工具组件
基于AST分析代码结构、复杂度、潜在bug，给出代码质量评估
"""

import ast
import math
from typing import Any, Dict, List, Optional, Tuple
import statistics


class CodeMetrics:
    """代码指标计算器"""

    def __init__(self):
        self.total_lines = 0
        self.comment_lines = 0
        self.blank_lines = 0
        self.function_count = 0
        self.class_count = 0
        self.cyclomatic_complexity = 0
        self.max_nesting_depth = 0
        self.variables = set()
        self.functions = {}
        self.classes = {}
        self.code_lines = []

    def add_function(self, name: str, complexity: int, lines: int, nesting_depth: int):
        """添加函数信息"""
        self.functions[name] = {
            'complexity': complexity,
            'lines': lines,
            'nesting_depth': nesting_depth
        }

    def add_class(self, name: str, method_count: int):
        """添加类信息"""
        self.classes[name] = {
            'method_count': method_count
        }


class CyclomaticComplexityCalculator(ast.NodeVisitor):
    """圈复杂度计算器"""

    def __init__(self):
        self.complexity = 1
        self.nesting_depth = 0
        self.max_depth = 0

    def visit_If(self, node: ast.If):
        self.complexity += 1
        self.nesting_depth += 1
        if self.nesting_depth > self.max_depth:
            self.max_depth = self.nesting_depth
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_For(self, node: ast.For):
        self.complexity += 1
        self.nesting_depth += 1
        if self.nesting_depth > self.max_depth:
            self.max_depth = self.nesting_depth
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_While(self, node: ast.While):
        self.complexity += 1
        self.nesting_depth += 1
        if self.nesting_depth > self.max_depth:
            self.max_depth = self.nesting_depth
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_Try(self, node: ast.Try):
        self.complexity += len(node.handlers)
        self.nesting_depth += 1
        if self.nesting_depth > self.max_depth:
            self.max_depth = self.nesting_depth
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_Assert(self, node: ast.Assert):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp):
        if isinstance(node.op, ast.And) or isinstance(node.op, ast.Or):
            self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare):
        self.complexity += len(node.ops) - 1
        self.generic_visit(node)


class VariableVisitor(ast.NodeVisitor):
    """变量访问器"""

    def __init__(self):
        self.variables = set()

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Store):
            self.variables.add(node.id)
        self.generic_visit(node)


class FunctionVisitor(ast.NodeVisitor):
    """函数访问器"""

    def __init__(self, metrics: CodeMetrics):
        self.metrics = metrics
        self.current_class = None

    def visit_ClassDef(self, node: ast.ClassDef):
        self.current_class = node.name
        self.metrics.class_count += 1
        method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef) or
                         isinstance(n, ast.AsyncFunctionDef))
        self.metrics.add_class(node.name, method_count)
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        function_name = node.name
        if self.current_class:
            function_name = f"{self.current_class}.{node.name}"

        self.metrics.function_count += 1

        # 计算函数复杂度
        complexity_calculator = CyclomaticComplexityCalculator()
        complexity_calculator.visit(node)

        # 计算函数行数
        lines = node.end_lineno - node.lineno + 1 if node.end_lineno and node.lineno else 0

        # 收集变量信息
        variable_visitor = VariableVisitor()
        variable_visitor.visit(node)
        for var in variable_visitor.variables:
            self.metrics.variables.add(var)

        self.metrics.add_function(
            function_name,
            complexity_calculator.complexity,
            lines,
            complexity_calculator.max_depth
        )

        # 更新全局复杂度和嵌套深度
        if complexity_calculator.complexity > self.metrics.cyclomatic_complexity:
            self.metrics.cyclomatic_complexity = complexity_calculator.complexity
        if complexity_calculator.max_depth > self.metrics.max_nesting_depth:
            self.metrics.max_nesting_depth = complexity_calculator.max_depth


def analyze_code_quality(code: str) -> Dict[str, Any]:
    """
    分析代码质量

    Args:
        code: 要分析的Python代码

    Returns:
        包含分析结果的字典
    """
    metrics = CodeMetrics()

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "success": False,
            "errors": [f"语法错误: {e}"],
            "metrics": {}
        }

    # 逐行分析代码
    lines = code.split('\n')
    metrics.total_lines = len(lines)

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            metrics.blank_lines += 1
        elif stripped_line.startswith('#'):
            metrics.comment_lines += 1
        else:
            metrics.code_lines.append(line)

    # 访问抽象语法树
    function_visitor = FunctionVisitor(metrics)
    function_visitor.visit(tree)

    # 计算各种指标
    code_lines_count = len(metrics.code_lines)
    comment_density = 0
    if code_lines_count > 0:
        comment_density = (metrics.comment_lines / code_lines_count) * 100

    # 计算函数复杂度分布
    function_complexities = [func['complexity'] for func in metrics.functions.values()]
    avg_complexity = statistics.mean(function_complexities) if function_complexities else 0
    median_complexity = statistics.median(function_complexities) if function_complexities else 0

    # 找出高复杂度函数
    high_complexity_functions = []
    for name, info in metrics.functions.items():
        if info['complexity'] > 10:
            high_complexity_functions.append(name)

    # 分析潜在问题
    issues = analyze_potential_bugs(code, tree, metrics)

    # 评估代码质量
    quality_score = calculate_quality_score(metrics, len(issues))

    return {
        "success": True,
        "errors": [],
        "metrics": {
            "lines": {
                "total": metrics.total_lines,
                "code": code_lines_count,
                "comments": metrics.comment_lines,
                "blank": metrics.blank_lines,
                "comment_density": round(comment_density, 2)
            },
            "structure": {
                "classes": metrics.class_count,
                "functions": metrics.function_count,
                "methods_per_class": [
                    cls['method_count'] for cls in metrics.classes.values()
                ]
            },
            "complexity": {
                "cyclomatic": metrics.cyclomatic_complexity,
                "max_nesting_depth": metrics.max_nesting_depth,
                "avg_function_complexity": round(avg_complexity, 2),
                "median_function_complexity": round(median_complexity, 2),
                "high_complexity_functions": high_complexity_functions
            },
            "variables": {
                "total": len(metrics.variables),
                "names": list(metrics.variables)
            },
            "quality_score": quality_score
        },
        "issues": issues
    }


def analyze_potential_bugs(code: str, tree: ast.AST, metrics: CodeMetrics) -> List[Dict[str, Any]]:
    """分析潜在的代码问题"""
    issues = []

    class BugVisitor(ast.NodeVisitor):
        def visit_Assign(self, node: ast.Assign):
            # 检查未使用的变量
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variable_name = target.id
                    # 简单的未使用变量检测
                    if variable_name not in ['_', '__'] and variable_name not in code.split(variable_name, 1)[1]:
                        issues.append({
                            "type": "warning",
                            "code": "unused_variable",
                            "description": f"变量 '{variable_name}' 可能未被使用",
                            "line": node.lineno
                        })

        def visit_FunctionDef(self, node: ast.FunctionDef):
            self._check_function(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
            self._check_function(node)

        def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
            # 检查函数参数未使用
            for arg in node.args.args:
                arg_name = arg.arg
                if arg_name not in ['_', '__']:
                    # 简单的参数使用检测
                    if arg_name not in ast.dump(node):
                        issues.append({
                            "type": "warning",
                            "code": "unused_argument",
                            "description": f"函数 '{node.name}' 的参数 '{arg_name}' 未被使用",
                            "line": node.lineno
                        })

        def visit_If(self, node: ast.If):
            # 检查深度嵌套
            nesting_depth = 0
            parent = node
            while parent:
                if isinstance(parent, ast.If) or isinstance(parent, ast.For) or isinstance(parent, ast.While):
                    nesting_depth += 1
                if hasattr(parent, 'parent'):
                    parent = parent.parent
                else:
                    parent = None

            if nesting_depth > 4:
                issues.append({
                    "type": "warning",
                    "code": "deep_nesting",
                    "description": f"条件语句嵌套过深 (深度 {nesting_depth})",
                    "line": node.lineno
                })

        def visit_Assert(self, node: ast.Assert):
            # 检查断言语句
            issues.append({
                "type": "warning",
                "code": "assert_statement",
                "description": "使用断言语句，在生产环境可能被禁用",
                "line": node.lineno
            })

    # 为所有节点添加parent属性
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    visitor = BugVisitor()
    visitor.visit(tree)

    return issues


def calculate_quality_score(metrics: CodeMetrics, issue_count: int) -> int:
    """计算代码质量得分"""
    score = 100

    # 基于代码行数调整
    if metrics.total_lines > 1000:
        score -= 10
    elif metrics.total_lines < 50:
        score -= 5

    # 基于注释密度调整
    comment_density = 0
    code_lines = metrics.total_lines - metrics.comment_lines - metrics.blank_lines
    if code_lines > 0:
        comment_density = (metrics.comment_lines / code_lines) * 100

    if comment_density < 5:
        score -= 15
    elif comment_density < 10:
        score -= 10

    # 基于圈复杂度调整
    if metrics.cyclomatic_complexity > 20:
        score -= 20
    elif metrics.cyclomatic_complexity > 10:
        score -= 10

    # 基于嵌套深度调整
    if metrics.max_nesting_depth > 6:
        score -= 15
    elif metrics.max_nesting_depth > 4:
        score -= 10

    # 基于问题数量调整
    score -= min(issue_count * 5, 40)

    return max(0, score)


def format_analysis_report(analysis_result: Dict[str, Any]) -> str:
    """
    格式化分析报告

    Args:
        analysis_result: 分析结果字典

    Returns:
        格式化的报告字符串
    """
    if not analysis_result["success"]:
        return "\n".join([f"❌ {error}" for error in analysis_result["errors"]])

    metrics = analysis_result["metrics"]

    report = []
    report.append("## 代码质量分析报告")
    report.append("")
    report.append(f"**代码行数:** {metrics['lines']['total']}")
    report.append(f"**有效代码:** {metrics['lines']['code']}")
    report.append(f"**注释数量:** {metrics['lines']['comments']}")
    report.append(f"**注释密度:** {metrics['lines']['comment_density']:.2f}%")
    report.append("")
    report.append("### 代码结构")
    report.append(f"**类数量:** {metrics['structure']['classes']}")
    report.append(f"**函数数量:** {metrics['structure']['functions']}")
    if metrics['structure']['classes'] > 0:
        avg_methods = sum(metrics['structure']['methods_per_class']) / metrics['structure']['classes']
        report.append(f"**平均每个类的方法数:** {avg_methods:.2f}")
    report.append("")
    report.append("### 代码复杂度")
    report.append(f"**圈复杂度:** {metrics['complexity']['cyclomatic']}")
    report.append(f"**最大嵌套深度:** {metrics['complexity']['max_nesting_depth']}")
    report.append(f"**平均函数复杂度:** {metrics['complexity']['avg_function_complexity']:.2f}")
    report.append(f"**中位数函数复杂度:** {metrics['complexity']['median_function_complexity']:.2f}")
    if metrics['complexity']['high_complexity_functions']:
        report.append(f"**高复杂度函数:** {len(metrics['complexity']['high_complexity_functions'])}")
        for func in metrics['complexity']['high_complexity_functions']:
            report.append(f"  - {func}")
    report.append("")
    report.append(f"**变量数量:** {metrics['variables']['total']}")
    report.append(f"**质量得分:** {metrics['quality_score']}/100")
    report.append("")

    if analysis_result.get("issues"):
        report.append("### 潜在问题")
        for issue in analysis_result["issues"]:
            severity = "⚠️" if issue['type'] == "warning" else "❌"
            report.append(f"**{severity} {issue['description']}** (第 {issue['line']} 行)")

    return "\n".join(report)


if __name__ == "__main__":
    # 测试示例
    test_code = """
def calculate_average(numbers):
    \"\"\"计算平均值\"\"\"
    sum = 0
    count = 0
    for num in numbers:
        if num > 0:
            sum += num
            count += 1
        elif num < 0:
            continue
        else:
            pass
    if count > 0:
        return sum / count
    else:
        return 0


def main():
    data = [1, 2, 3, 4, 5]
    average = calculate_average(data)
    print(f"平均值: {average}")


if __name__ == "__main__":
    main()
""".strip()

    print("=== 代码质量分析测试 ===")
    print("")
    analysis = analyze_code_quality(test_code)
    print(format_analysis_report(analysis))