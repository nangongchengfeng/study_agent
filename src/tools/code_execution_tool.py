"""
代码执行工具
负责安全地执行代码片段
"""

import logging
import subprocess
import tempfile
import os
import sys
from typing import Any, Dict
from .base_tool import BaseTool

logger = logging.getLogger(__name__)


class CodeExecutionTool(BaseTool):
    """
    代码执行工具
    """

    def __init__(self):
        super().__init__("CodeExecutionTool")
        self.timeout = 10  # 默认超时时间（秒）
        self.max_memory = 512 * 1024 * 1024  # 512MB 内存限制

    def run(self, code: str, **kwargs) -> Dict[str, Any]:
        """
        执行代码

        Args:
            code: 要执行的代码
            **kwargs: 可选参数（如超时时间）

        Returns:
            执行结果
        """
        logger.info("执行代码执行工具")

        if not self.validate_input(["code"], code=code):
            return self.handle_error(
                ValueError("缺少代码参数"),
                {"code": code},
            )

        timeout = kwargs.get("timeout", self.timeout)

        try:
            return self._execute_python_code(code, timeout)
        except Exception as e:
            return self.handle_error(e, {"code": code})

    def _execute_python_code(self, code: str, timeout: int) -> Dict[str, Any]:
        """
        执行 Python 代码

        Args:
            code: 要执行的 Python 代码
            timeout: 超时时间

        Returns:
            执行结果
        """
        # 安全的临时文件创建
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "temp_code.py")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code)

            # 执行代码
            try:
                # 使用 subprocess 执行代码
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=temp_dir,
                )

                output = ""
                if result.stdout:
                    output += result.stdout
                if result.stderr:
                    output += result.stderr

                return {
                    "success": result.returncode == 0,
                    "tool": self.name,
                    "output": output,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "code": code,
                }

            except subprocess.TimeoutExpired:
                return self.handle_error(
                    TimeoutError(f"代码执行超时（{timeout}秒）"),
                    {"code": code, "timeout": timeout},
                )

    def run_safe(self, code: str, **kwargs) -> Dict[str, Any]:
        """
        安全执行代码（受限环境）

        Args:
            code: 要执行的代码
            **kwargs: 可选参数

        Returns:
            执行结果
        """
        logger.info("执行安全代码执行工具")

        # 添加安全检查
        if self._contains_dangerous_code(code):
            return self.handle_error(
                ValueError("代码包含不安全内容"),
                {"code": code},
            )

        # 使用沙箱或限制执行
        return self.run(code, **kwargs)

    def _contains_dangerous_code(self, code: str) -> bool:
        """
        检查代码是否包含危险内容

        Args:
            code: 要检查的代码

        Returns:
            是否包含危险内容
        """
        dangerous_patterns = [
            "import.*os",
            "import.*sys",
            "import.*subprocess",
            "import.*socket",
            "import.*threading",
            "import.*multiprocessing",
            "__import__",
            "eval\\(",
            "exec\\(",
            "open\\(",
            "input\\(",
            "sys\\.exit",
            "os\\.system",
            "os\\.popen",
            "subprocess\\.",
        ]

        import re

        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                logger.warning(f"代码包含危险模式: {pattern}")
                return True

        return False

    def execute_code_block(self, code_block: str, **kwargs) -> Dict[str, Any]:
        """
        执行代码块（去除Markdown格式）

        Args:
            code_block: 包含代码块的文本
            **kwargs: 可选参数

        Returns:
            执行结果
        """
        # 提取 Python 代码块
        import re

        # 匹配 ```python ... ``` 格式
        python_match = re.search(r"```python\s*(.*?)\s*```", code_block, re.DOTALL)
        if python_match:
            code = python_match.group(1).strip()
        else:
            # 匹配 ``` ... ``` 格式
            match = re.search(r"```\s*(.*?)\s*```", code_block, re.DOTALL)
            if match:
                code = match.group(1).strip()
            else:
                # 直接使用整个文本
                code = code_block.strip()

        # 去除注释或不需要的内容
        code = self._clean_code(code)

        return self.run_safe(code, **kwargs)

    def _clean_code(self, code: str) -> str:
        """
        清理代码

        Args:
            code: 原始代码

        Returns:
            清理后的代码
        """
        # 去除以 # 开头的行（简单实现）
        lines = []
        for line in code.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                lines.append(line)
        return "\n".join(lines)

    def run_interactive(self, code: str, variables: Dict[str, Any] = None, **kwargs):
        """
        交互式执行代码（用于教学场景）

        Args:
            code: 要执行的代码
            variables: 要传入的变量
            **kwargs: 可选参数

        Returns:
            执行结果
        """
        logger.info("执行交互式代码执行")

        # 创建临时模块
        import sys
        import importlib.util

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "temp_module.py")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code)

            # 导入临时模块
            spec = importlib.util.spec_from_file_location("temp_module", temp_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules["temp_module"] = module

            try:
                # 执行模块
                spec.loader.exec_module(module)

                # 收集变量
                result_vars = {}
                if variables:
                    for var_name, var_value in variables.items():
                        setattr(module, var_name, var_value)

                return self.format_output({
                    "module": module,
                    "variables": {
                        name: value
                        for name, value in module.__dict__.items()
                        if not name.startswith("__")
                    },
                    "code": code,
                })

            except Exception as e:
                return self.handle_error(e, {"code": code})

    def run_code_with_timeout(self, code: str, timeout: int) -> Dict[str, Any]:
        """
        带超时的代码执行

        Args:
            code: 要执行的代码
            timeout: 超时时间（秒）

        Returns:
            执行结果
        """
        return self.run(code, timeout=timeout)


# 工具的便捷方法
def run_code(code: str, **kwargs):
    """
    便捷的代码执行方法

    Args:
        code: 要执行的代码
        **kwargs: 可选参数

    Returns:
        执行结果
    """
    tool = CodeExecutionTool()
    return tool.run(code, **kwargs)


def safe_execute(code: str, **kwargs):
    """
    便捷的安全代码执行方法

    Args:
        code: 要执行的代码
        **kwargs: 可选参数

    Returns:
        执行结果
    """
    tool = CodeExecutionTool()
    return tool.run_safe(code, **kwargs)
