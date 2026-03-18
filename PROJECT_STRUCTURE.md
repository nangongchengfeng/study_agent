# 智能编程学习导师项目结构

## 项目概述

使用 LangGraph 实现完整的教学工作流编排，包含记忆系统、功能 Agent、工具层和工作流编排。

## 目录结构

```
study_agent/
├── main.py                          # 入口程序
├── src/
│   ├── __init__.py
│   ├── workflows/                   # 工作流编排
│   │   ├── __init__.py
│   │   └── teaching_workflow.py    # 主教学工作流
│   ├── agents/                      # 功能 Agent
│   │   ├── __init__.py
│   │   ├── base_agent.py            # Agent 基类
│   │   ├── understanding_agent.py   # 理解评估 Agent
│   │   ├── memory_retrieval_agent.py  # 记忆检索 Agent
│   │   ├── explanation_agent.py     # 个性化讲解 Agent
│   │   ├── example_generation_agent.py  # 示例生成 Agent
│   │   ├── practice_generation_agent.py  # 练习生成 Agent
│   │   ├── validation_agent.py      # 验证 Agent
│   │   └── memory_update_agent.py   # 记忆更新 Agent
│   ├── tools/                       # 工具层
│   │   ├── __init__.py
│   │   ├── base_tool.py             # 工具基类
│   │   ├── code_execution_tool.py   # 代码执行工具
│   │   ├── documentation_retrieval_tool.py  # 文档检索工具
│   │   └── practice_evaluation_tool.py  # 练习评估工具
│   └── memory/                      # 记忆系统
│       ├── __init__.py
│       ├── memory_system.py         # 记忆系统统一接口
│       ├── sensory_memory.py        # 感觉记忆（最近对话）
│       ├── short_term_memory.py     # 短期记忆（7天会话）
│       ├── long_term_memory.py      # 长期记忆（知识图谱）
│       ├── memory_store.py          # 记忆存储
│       └── knowledge_base.py        # 知识库
└── tests/
    ├── __init__.py
    └── test_workflow.py             # 工作流测试
```

## 核心模块说明

### 1. 工作流编排 (src/workflows/)

#### TeachingWorkflowState
工作流状态定义，包含：
- 用户输入信息
- 上下文信息
- 记忆数据
- 工具输出
- Agent 输出
- 中间状态

#### TeachingWorkflow
教学工作流主类，实现完整的教学流程：

```
用户查询
    ↓
理解评估 → 记忆检索 → 个性化讲解 → 示例生成 → 练习生成 → 验证环节 → 记忆更新
    ↓                                                                 ↑
    └──────────────────── 条件路由（验证分数低时补充讲解）──────────────┘
```

### 2. 功能 Agent (src/agents/)

| Agent | 职责 |
|-------|------|
| UnderstandingAgent | 理解用户查询，评估学习需求，识别主题和关键词 |
| MemoryRetrievalAgent | 从记忆系统检索相关知识、学习进度、常见错误 |
| ExplanationAgent | 根据用户水平生成个性化讲解内容 |
| ExampleGenerationAgent | 生成教学代码示例 |
| PracticeGenerationAgent | 生成练习题（基础/进阶/高阶） |
| ValidationAgent | 验证学习成果，生成反馈，评估掌握程度 |
| MemoryUpdateAgent | 更新学习记忆，记录学习进度 |

### 3. 工具层 (src/tools/)

| 工具 | 功能 |
|------|------|
| CodeExecutionTool | 安全执行代码片段，支持超时控制 |
| DocumentationRetrievalTool | 检索相关文档、教程、资源链接 |
| PracticeEvaluationTool | 评估练习完成情况，计算分数，生成反馈 |

### 4. 记忆系统 (src/memory/)

| 记忆类型 | 存储 | 用途 |
|---------|------|------|
| SensoryMemory | 内存 | 最近10轮对话上下文 |
| ShortTermMemory | JSON文件 | 最近7天学习会话 |
| LongTermMemory | JSON文件 | 知识点、学习历史、代码作品集 |

## 使用方法

### 快速开始

```bash
# 运行快速演示
python main.py quick

# 交互式使用
python main.py
```

### 直接使用工作流

```python
from src.workflows import TeachingWorkflow

# 创建工作流
workflow = TeachingWorkflow()

# 运行教学流程
result = workflow.run(
    user_query="什么是Python装饰器？",
    user_level="intermediate",
    workflow_id="demo_001",
)

print(result["explanation"])    # 讲解内容
print(result["example"])        # 示例代码
print(result["practice"])       # 练习题
print(result["validation"])     # 验证结果
```

### 运行测试

```bash
# 运行所有测试
python tests/test_workflow.py

# 或使用 pytest
pytest tests/test_workflow.py -v
```

## 特性

1. **完整的教学流程**：理解评估 → 记忆检索 → 讲解 → 示例 → 练习 → 验证 → 记忆更新
2. **个性化内容**：根据用户水平（初级/中级/高级）生成定制化内容
3. **记忆系统**：三层记忆架构，支持长期学习跟踪
4. **可中断恢复**：支持工作流中断和恢复
5. **多轮对话**：支持多轮对话上下文管理
6. **丰富的工具**：代码执行、文档检索、练习评估

## 技术栈

- LangGraph: 工作流编排框架
- Python 3.8+: 编程语言
- JSON: 数据持久化
