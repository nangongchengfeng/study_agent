# 🎓 教学工作流 (Teaching Workflow)

本模块使用 LangGraph 实现完整的智能编程教学工作流编排。

## 📋 目录

- [工作流概述](#工作流概述)
- [核心类](#核心类)
- [工作流状态](#工作流状态)
- [工作流节点](#工作流节点)
- [条件路由](#条件路由)
- [使用方法](#使用方法)
- [执行流程](#执行流程)

---

## 🎯 工作流概述

教学工作流是一个基于 LangGraph 的状态机，编排完整的编程教学流程：

```
用户查询
    ↓
📊 理解评估 → 🔍 记忆检索 → 📚 个性化讲解 → 💻 示例生成 → 📝 练习生成 → 🎯 学习验证 → 💾 记忆更新
    ↓                                                                 ↑
    └──────────────────── 条件路由（验证分数低时补充讲解）──────────────┘
```

---

## 🏗️ 核心类

### TeachingWorkflow

教学工作流的主类，负责：
- 初始化各功能 Agent 和工具
- 构建 LangGraph 状态图
- 执行工作流
- 支持中断和恢复
- 支持分步执行

**主要方法：**

| 方法 | 说明 |
|------|------|
| `__init__()` | 初始化工作流，创建 Agent 和工具实例 |
| `_build_workflow_graph()` | 构建 LangGraph 状态图 |
| `run()` | 完整执行工作流 |
| `run_step_by_step()` | 分步执行工作流，每步后等待用户确认 |
| `resume()` | 恢复中断的工作流 |

---

## 📊 工作流状态 (TeachingWorkflowState)

使用 `TypedDict` 定义工作流状态，包含以下字段：

### 用户输入
- `user_input`: 用户原始输入
- `user_query`: 处理后的用户查询
- `user_level`: 用户水平（`beginner`/`intermediate`/`advanced`）

### 上下文信息
- `conversation_history`: 对话历史记录
- `current_step`: 当前执行步骤（使用 `Annotated` 确保取最后一次更新）
- `workflow_id`: 工作流唯一标识
- `supplement_count`: 补充讲解次数（避免无限循环）

### 记忆数据
- `existing_knowledge`: 从记忆系统检索的现有知识
- `new_knowledge`: 本次学习的新知识

### 工具输出
- `code_execution_result`: 代码执行工具输出
- `documentation_result`: 文档检索工具输出
- `practice_evaluation_result`: 练习评估工具输出

### Agent 输出
- `understanding_result`: 理解评估结果
- `memory_retrieval_result`: 记忆检索结果
- `explanation_result`: 个性化讲解内容
- `example_result`: 代码示例
- `practice_result`: 练习题
- `validation_result`: 学习验证结果
- `memory_update_result`: 记忆更新结果

### 中间状态
- `is_complete`: 工作流是否完成
- `error_message`: 错误信息（如有）
- `feedback`: 用户反馈

---

## 🔄 工作流节点

### 1. 理解评估 (understanding)

**职责：** 分析用户查询，识别学习需求

**调用 Agent：** `UnderstandingAgent`

**输入：**
- `user_query`: 用户查询
- `conversation_history`: 对话历史
- `user_level`: 用户水平

**输出：**
```python
{
    "understanding_result": {
        "query_type": "explanation",  # 查询类型
        "topics": ["Python", "装饰器"],  # 主题
        "keywords": ["装饰器", "Python"],  # 关键词
        "learning_objective": "conceptual_understanding",  # 学习目标
        "difficulty": "intermediate",  # 难度
        "confidence": 0.95  # 置信度
    },
    "current_step": "understanding_completed"
}
```

---

### 2. 记忆检索 (memory_retrieval)

**职责：** 从记忆系统检索相关知识

**调用 Agent：** `MemoryRetrievalAgent`

**输入：**
- `user_query`: 用户查询
- `user_level`: 用户水平

**输出：**
```python
{
    "memory_retrieval_result": {
        "related_knowledge": [
            {
                "title": "Python装饰器基础",
                "content": "...",
                "confidence": 0.85
            }
        ]
    },
    "existing_knowledge": [...],  # 相关知识列表
    "current_step": "memory_retrieval_completed"
}
```

---

### 3. 个性化讲解 (explanation)

**职责：** 根据用户水平生成个性化讲解

**调用 Agent：** `ExplanationAgent`

**输入：**
- `user_query`: 用户查询
- `user_level`: 用户水平
- `related_knowledge`: 相关知识
- `understanding_result`: 理解评估结果

**输出：**
```python
{
    "explanation_result": "## Python装饰器详解\n\n...",  # Markdown格式讲解
    "current_step": "explanation_completed",
    "supplement_count": 0  # 补充讲解计数器
}
```

---

### 4. 示例生成 (example_generation)

**职责：** 生成教学代码示例

**调用 Agent：** `ExampleGenerationAgent`

**输入：**
- `user_query`: 用户查询
- `user_level`: 用户水平
- `explanation`: 讲解内容
- `related_knowledge`: 相关知识

**输出：**
```python
{
    "example_result": "def my_decorator(func):\n    def wrapper():\n        ...\n    return wrapper",
    "current_step": "example_generation_completed"
}
```

---

### 5. 练习生成 (practice_generation)

**职责：** 生成练习题

**调用 Agent：** `PracticeGenerationAgent`

**输入：**
- `user_query`: 用户查询
- `user_level`: 用户水平
- `explanation`: 讲解内容
- `example`: 代码示例

**输出：**
```python
{
    "practice_result": "## 练习题\n\n1. 创建一个装饰器...\n2. ...",
    "current_step": "practice_generation_completed"
}
```

---

### 6. 学习验证 (validation)

**职责：** 评估学习成果，判断是否需要补充讲解

**调用 Agent：** `ValidationAgent`

**输入：**
- `user_query`: 用户查询
- `user_level`: 用户水平
- `practice_result`: 练习题
- `explanation`: 讲解内容

**输出：**
```python
{
    "validation_result": {
        "score": 0.85,  # 掌握分数 (0-1)
        "mastery_level": "proficient",  # 掌握程度
        "feedback": "很好，你已经掌握了...",  # 反馈
        "suggestions": ["建议学习..."],  # 建议
        "needs_supplement": False  # 是否需要补充讲解
    },
    "current_step": "validation_completed"
}
```

---

### 7. 记忆更新 (memory_update)

**职责：** 更新学习记忆

**调用 Agent：** `MemoryUpdateAgent`

**输入：**
- `user_query`: 用户查询
- `user_level`: 用户水平
- `explanation`: 讲解内容
- `example`: 代码示例
- `practice`: 练习题
- `validation_result`: 验证结果

**输出：**
```python
{
    "memory_update_result": {"success": True},
    "new_knowledge": {...},  # 新知识
    "current_step": "memory_update_completed",
    "is_complete": True  # 标记工作流完成
}
```

---

## 🔀 条件路由

工作流在验证节点后有条件路由逻辑：

```python
def _should_supplement_explanation(self, state):
    """判断是否需要补充讲解"""
    validation_result = state.get("validation_result", {})
    score = validation_result.get("score", 0)
    needs_supplement = validation_result.get("needs_supplement", False)
    supplement_count = state.get("supplement_count", 0)

    # 最多补充讲解1次，避免无限循环
    if (score < 0.7 or needs_supplement) and supplement_count < 1:
        return "supplement"  # 返回讲解节点
    return "continue"  # 继续记忆更新
```

**路由条件：**
- 验证分数 < 0.7 或 `needs_supplement=True`
- 补充讲解次数 < 1（避免无限循环）

满足条件时，跳回 `explanation` 节点重新生成讲解。

---

## 💻 使用方法

### 基本使用

```python
from src.workflows import TeachingWorkflow

# 创建工作流实例
workflow = TeachingWorkflow()

# 完整执行工作流
result = workflow.run(
    user_query="什么是Python的装饰器？",
    user_level="intermediate",
    workflow_id="demo_001",
)

# 获取结果
print(result["explanation"])    # 讲解内容
print(result["example"])        # 示例代码
print(result["practice"])       # 练习题
print(result["validation"])     # 验证结果
```

### 分步执行

```python
# 分步执行，每步后等待用户确认
workflow.run_step_by_step(
    user_query="什么是Python的装饰器？",
    user_level="intermediate",
    workflow_id="demo_001",
)
```

### 中断和恢复

```python
# 创建时启用检查点
workflow = TeachingWorkflow(checkpoint_path="./checkpoints")

# 执行工作流
result = workflow.run(..., workflow_id="my_workflow")

# 之后可以恢复
result = workflow.resume("my_workflow")
```

---

## 🔄 执行流程详解

### 完整执行流程

```
1. 初始化状态
   ↓
2. 理解评估 (understanding)
   ↓
3. 记忆检索 (memory_retrieval)
   ↓
4. 个性化讲解 (explanation)
   ↓
5. 示例生成 (example_generation)
   ↓
6. 练习生成 (practice_generation)
   ↓
7. 学习验证 (validation)
   ↓
   ┌─────────────────┐
   │ 分数 ≥ 0.7?    │
   └────────┬────────┘
            │ 是
            ↓
8. 记忆更新 (memory_update)
   ↓
   结束
```

### 条件分支流程

```
7. 学习验证 (validation)
   ↓
   ┌─────────────────┐
   │ 分数 < 0.7?     │
   └────────┬────────┘
            │ 是
            ↓
4. 个性化讲解 (explanation)  [补充讲解]
   ↓
5. 示例生成 (example_generation)
   ↓
6. 练习生成 (practice_generation)
   ↓
7. 学习验证 (validation)
   ↓
   ┌─────────────────┐
   │ 分数 ≥ 0.7?    │
   └────────┬────────┘
            │ 是
            ↓
8. 记忆更新 (memory_update)
   ↓
   结束
```

---

## 📝 状态流转示例

以下是一个完整的状态流转示例：

```python
# 初始状态
state = {
    "user_query": "什么是Python的装饰器？",
    "user_level": "intermediate",
    "current_step": "start",
    "is_complete": False,
    ...
}

# 执行理解评估后
state.update({
    "understanding_result": {...},
    "current_step": "understanding_completed",
})

# 执行记忆检索后
state.update({
    "memory_retrieval_result": {...},
    "existing_knowledge": [...],
    "current_step": "memory_retrieval_completed",
})

# ... 继续执行其他节点 ...

# 最终状态
state.update({
    "is_complete": True,
    "current_step": "memory_update_completed",
})
```

---

## 🎯 关键设计要点

### 1. 状态管理
- 使用 `TypedDict` 定义类型安全的状态
- 使用 `Annotated` 处理冲突的字段更新
- 所有节点通过返回字典更新状态

### 2. 可观测性
- 每个节点都有详细的日志记录
- 状态变更可追踪
- 支持检查点和恢复

### 3. 灵活性
- 条件路由支持动态流程调整
- 分步执行支持交互式学习
- 记忆系统支持长期学习跟踪

### 4. 扩展性
- 新节点可以轻松添加
- Agent 和工具可以独立替换
- 状态结构可以灵活扩展

---

## 🧪 测试

模块包含内置测试：

```python
if __name__ == "__main__":
    workflow = TeachingWorkflow()
    result = workflow.run(
        user_query="什么是Python的装饰器？",
        user_level="intermediate",
    )
    print(result)
```

运行测试：

```bash
python src/workflows/teaching_workflow.py
```

---

## 📚 相关模块

- [Agents](../agents/) - 功能 Agent 实现
- [Tools](../tools/) - 工具层实现
- [Memory](../memory/) - 记忆系统实现
- [Prompts](../../config/prompts/) - Agent 提示词配置
