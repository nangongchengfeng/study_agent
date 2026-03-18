# 智能编程学习导师 - 工具层

工具层提供核心工具组件，支持编程学习过程中的代码执行、文档检索和练习评估。

## 目录结构

```
src/tools/
├── __init__.py          # 工具层包入口
├── base_tool.py         # 工具基类（所有工具的通用接口）
├── code_execution_tool.py     # 代码执行工具
├── documentation_retrieval_tool.py  # 文档检索工具
├── practice_evaluation_tool.py     # 练习评估工具
├── code_interpreter.py   # 兼容：代码解释器
├── static_analyzer.py    # 兼容：静态分析工具
├── test_runner.py        # 兼容：测试运行器
├── document_retriever.py # 兼容：文档检索（旧版）
└── test_tools.py         # 单元测试
```

## 核心工具

### 1. CodeExecutionTool（代码执行工具）

安全地执行代码片段，支持多种执行模式。

**主要功能：**
- 执行Python代码并返回输出
- 安全检查（禁止危险操作）
- 超时控制
- 支持Markdown代码块提取

**使用示例：**
```python
from src.tools import CodeExecutionTool

executor = CodeExecutionTool()
result = executor.run_safe('print("Hello!")')
print(result['output'])
```

### 2. DocumentationRetrievalTool（文档检索工具）

检索编程学习相关的文档和资源。

**主要功能：**
- 搜索Python官方文档
- 搜索Stack Overflow问题
- 搜索Medium文章
- 搜索GitHub仓库
- 查找教程和视频教程

**使用示例：**
```python
from src.tools import DocumentationRetrievalTool

retriever = DocumentationRetrievalTool()
result = retriever.run('装饰器')
print(f'找到 {result["result"]["total_results"]} 个结果')
```

### 3. PracticeEvaluationTool（练习评估工具）

评估用户的练习完成情况。

**主要功能：**
- 文本相似度评分
- 代码相似度评分
- 代码执行测试
- 生成个性化反馈

**使用示例：**
```python
from src.tools import PracticeEvaluationTool

evaluator = PracticeEvaluationTool()
result = evaluator.run(user_answer, expected_answer)
print(f'得分: {result["result"]["score"]}')
print(f'反馈: {result["result"]["feedback"]}')
```

## 工具基类

所有工具都继承自 `BaseTool`，提供统一的接口：

- `run(**kwargs)` - 执行工具的核心方法
- `validate_input(required_fields, **kwargs)` - 验证输入参数
- `handle_error(error, input_data)` - 统一错误处理
- `format_output(data)` - 格式化输出

## 兼容性

保留了旧版工具模块以保证兼容性：
- `code_interpreter` - 沙箱代码解释器
- `static_analyzer` - 代码静态分析
- `test_runner` - 测试运行器
- `document_retriever` - 内置文档检索

## 测试

运行单元测试：

```bash
cd D:/tmp/study_agent
python -c "import sys; sys.path.insert(0, '.'); from src.tools.test_tools import run_all_tests; run_all_tests()"
```

## 版本

当前版本：2.0.0
