"""
代码解释器组件
提供沙箱环境运行Python代码，返回执行结果、错误信息
禁止危险操作（文件删除、系统命令执行等）
"""

import ast
import sys
import io
from typing import Any, Dict, List, Optional
import re


class SecurityRestrictions(ast.NodeTransformer):
    """安全限制检查器，禁止危险的语法结构"""

    def __init__(self):
        # 禁止的函数调用
        self.forbidden_funcs = [
            'eval', 'exec', 'compile', 'globals', 'locals', 'vars',
            'open', 'file', '__import__', 'input', 'raw_input',
            'os', 'sys', 'subprocess', 'shutil', 'socket', 'pickle',
            'cPickle', 'marshal', 'struct', 'hashlib', 'hmac', 'base64',
            'binascii', 'crypt', 'random', 'timeit', 'threading', 'multiprocessing',
            'ssl', 'urllib', 'urllib2', 'httplib', 'ftplib', 'smtplib', 'email',
            'xml', 'json', 'yaml', 'csv', 'sqlite3', 'dbm', 'gdbm', 'bz2', 'zipfile',
            'tarfile', 'lzma', 'zlib', 'sysconfig', 'platform', 'resource', 'gc',
            'inspect', 'dis', 'code', 'codeop', 'traceback', 'linecache', 'weakref',
            'copy', 'deepcopy', 'functools', 'itertools', 'operator', 'collections',
            'heapq', 'bisect', 'array', 'math', 'cmath', 'decimal', 'fractions',
            'random', 'statistics', 'string', 're', 'unicodedata', 'tokenize',
            'token', 'keyword', 'pprint', 'reprlib', 'textwrap', 'stringprep',
            'readline', 'rlcompleter', 'atexit', 'trace', 'profile', 'pstats',
            'time', 'datetime', 'calendar', 'zoneinfo', 'argparse', 'getopt',
            'logging', 'getpass', 'curses', 'termios', 'tty', 'pty', 'fcntl',
            'select', 'poll', 'epoll', 'kqueue', 'selectors', 'asyncio',
            'concurrent', 'queue', 'sched', 'errno', 'signal', 'faulthandler',
            'syslog', 'pwd', 'grp', 'spwd', 'crypt', 'getent', 'nis', 'ipaddress',
            'socket', 'ssl', 'asyncore', 'asynchat', 'ftplib', 'gopherlib',
            'httplib', 'imaplib', 'nntplib', 'poplib', 'smtplib', 'telnetlib',
            'urllib', 'urllib2', 'urlparse', 'robotparser', 'cgi', 'cgitb',
            'wsgiref', 'webbrowser', 'xml', 'xmlrpc', 'email', 'mailbox',
            'mimetypes', 'base64', 'binascii', 'codecs', 'quopri', 'uu',
            'zipfile', 'tarfile', 'bz2', 'gzip', 'lzma', 'zlib', 'shutil',
            'glob', 'fnmatch', 'filecmp', 'tempfile', 'io', 'os', 'os.path',
            'stat', 'statvfs', 'fcntl', 'flock', 'chmod', 'chown', 'umask',
            'utime', 'vfork', 'fork', 'execv', 'execve', 'execl', 'execle',
            'execvp', 'execvpe', 'execlp', 'execlpe', 'spawnv', 'spawnve',
            'spawnl', 'spawnle', 'spawnvp', 'spawnvpe', 'spawnlp', 'spawnlpe',
            'posix', 'nt', 'os2', 'ce', 'riscos', 'atheos'
        ]

        # 禁止的属性访问
        self.forbidden_attrs = [
            '__import__', '__name__', '__file__', '__path__', '__dict__',
            '__module__', '__class__', '__bases__', '__mro__', '__subclasses__',
            '__init_subclass__', '__new__', '__init__', '__del__', '__str__',
            '__repr__', '__bytes__', '__format__', '__lt__', '__le__', '__eq__',
            '__ne__', '__gt__', '__ge__', '__hash__', '__bool__', '__nonzero__',
            '__add__', '__sub__', '__mul__', '__matmul__', '__truediv__',
            '__floordiv__', '__mod__', '__divmod__', '__pow__', '__lshift__',
            '__rshift__', '__and__', '__xor__', '__or__', '__neg__', '__pos__',
            '__abs__', '__invert__', '__complex__', '__int__', '__float__',
            '__index__', '__round__', '__floor__', '__ceil__', '__trunc__',
            '__getattr__', '__getattribute__', '__setattr__', '__delattr__',
            '__dir__', '__get__', '__set__', '__delete__', '__call__',
            '__len__', '__getitem__', '__setitem__', '__delitem__', '__iter__',
            '__next__', '__contains__', '__getslice__', '__setslice__',
            '__delslice__', '__enter__', '__exit__', '__await__', '__aiter__',
            '__anext__', '__aenter__', '__aexit__'
        ]

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """检查函数调用是否安全"""
        func_name = self._get_func_name(node.func)
        if func_name in self.forbidden_funcs:
            raise SecurityError(f"禁止使用危险函数: {func_name}")
        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
        """检查属性访问是否安全"""
        attr_name = node.attr
        if attr_name in self.forbidden_attrs:
            raise SecurityError(f"禁止访问危险属性: {attr_name}")
        return node

    def visit_Import(self, node: ast.Import) -> ast.Import:
        """检查import语句是否安全"""
        for name in node.names:
            if name.name in self.forbidden_funcs:
                raise SecurityError(f"禁止导入危险模块: {name.name}")
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """检查from ... import语句是否安全"""
        if node.module in self.forbidden_funcs:
            raise SecurityError(f"禁止导入危险模块: {node.module}")
        for name in node.names:
            if name.name in self.forbidden_funcs:
                raise SecurityError(f"禁止导入危险模块: {name.name}")
        return node

    def _get_func_name(self, node: ast.expr) -> str:
        """获取函数名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_func_name(node.value)}.{node.attr}"
        else:
            return ""


class SecurityError(Exception):
    """安全错误异常"""
    pass


def validate_code(code: str) -> List[str]:
    """
    验证代码安全性

    Args:
        code: 要验证的Python代码

    Returns:
        错误列表，为空表示安全
    """
    errors = []
    try:
        tree = ast.parse(code)
        checker = SecurityRestrictions()
        checker.visit(tree)
    except SecurityError as e:
        errors.append(str(e))
    except SyntaxError as e:
        errors.append(f"语法错误: {e}")
    except Exception as e:
        errors.append(f"验证失败: {e}")
    return errors


def run_code(code: str, timeout: int = 5) -> Dict[str, Any]:
    """
    运行Python代码并返回结果

    Args:
        code: 要运行的代码
        timeout: 超时时间（秒）

    Returns:
        包含执行结果的字典
    """
    # 首先验证代码安全性
    errors = validate_code(code)
    if errors:
        return {
            "success": False,
            "errors": errors,
            "output": "",
            "execution_time": 0
        }

    # 捕获标准输出和错误
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    output_buffer = io.StringIO()
    error_buffer = io.StringIO()

    sys.stdout = output_buffer
    sys.stderr = error_buffer

    result = {
        "success": True,
        "errors": [],
        "output": "",
        "execution_time": 0
    }

    try:
        # 编译代码
        compiled_code = compile(code, "<string>", "exec")

        # 创建安全的全局环境
        safe_globals = {
            "__builtins__": {
                'abs': abs, 'all': all, 'any': any, 'ascii': ascii, 'bin': bin,
                'bool': bool, 'bytes': bytes, 'callable': callable, 'chr': chr,
                'complex': complex, 'dict': dict, 'dir': dir, 'divmod': divmod,
                'enumerate': enumerate, 'filter': filter, 'float': float,
                'format': format, 'frozenset': frozenset, 'getattr': getattr,
                'globals': lambda: {}, 'hasattr': hasattr, 'hash': hash, 'hex': hex,
                'id': id, 'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
                'iter': iter, 'len': len, 'list': list, 'map': map, 'max': max,
                'min': min, 'next': next, 'object': object, 'oct': oct, 'ord': ord,
                'pow': pow, 'print': print, 'range': range, 'repr': repr, 'reversed': reversed,
                'round': round, 'set': set, 'slice': slice, 'sorted': sorted,
                'str': str, 'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip
            }
        }

        # 执行代码
        import time
        start_time = time.time()
        exec(compiled_code, safe_globals, {})
        end_time = time.time()

        result["execution_time"] = round(end_time - start_time, 3)

    except Exception as e:
        result["success"] = False
        result["errors"].append(str(e))
    finally:
        # 恢复标准输出
        sys.stdout = original_stdout
        sys.stderr = original_stderr

        result["output"] = output_buffer.getvalue()
        if error_buffer.getvalue():
            if not result["errors"]:
                result["success"] = False
            result["errors"].append(error_buffer.getvalue())

    return result


if __name__ == "__main__":
    # 测试示例
    test_code1 = """
x = 10
y = 20
print(f"x + y = {x + y}")
print(f"x * y = {x * y}")
    """.strip()

    test_code2 = """
import os
os.system("rm -rf /")
    """.strip()

    print("=== 测试代码解释器 ===")
    print("\n1. 安全代码测试:")
    result = run_code(test_code1)
    print(f"成功: {result['success']}")
    print(f"输出: {result['output']}")
    print(f"错误: {result['errors']}")
    print(f"执行时间: {result['execution_time']}秒")

    print("\n2. 危险代码测试:")
    result = run_code(test_code2)
    print(f"成功: {result['success']}")
    print(f"输出: {result['output']}")
    print(f"错误: {result['errors']}")
    print(f"执行时间: {result['execution_time']}秒")