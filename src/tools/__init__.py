"""
智能编程学习导师项目 - 工具层核心组件
提供代码解释、静态分析、测试运行和文档检索功能
"""

from typing import Dict, Any, List, Optional
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入工具基类
from .base_tool import BaseTool

# 导入核心工具类
from .code_execution_tool import CodeExecutionTool
from .documentation_retrieval_tool import DocumentationRetrievalTool
from .practice_evaluation_tool import PracticeEvaluationTool

# 导入兼容工具模块
from . import code_interpreter
from . import static_analyzer
from . import test_runner
from . import document_retriever

__all__ = [
    "BaseTool",
    "CodeExecutionTool",
    "DocumentationRetrievalTool",
    "PracticeEvaluationTool",
    "code_interpreter",
    "static_analyzer",
    "test_runner",
    "document_retriever",
]

# 版本信息
__version__ = "2.0.0"