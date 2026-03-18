"""
教学工作流实现
使用LangGraph编排完整的教学流程
"""

import logging
import operator
from typing import Any, Dict, List, Optional, TypedDict
from typing_extensions import Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.agents import (
    UnderstandingAgent,
    MemoryRetrievalAgent,
    ExplanationAgent,
    ExampleGenerationAgent,
    PracticeGenerationAgent,
    ValidationAgent,
    MemoryUpdateAgent,
)
from src.tools import (
    CodeExecutionTool,
    DocumentationRetrievalTool,
    PracticeEvaluationTool,
)
from src.memory import MemorySystem

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TeachingWorkflowState(TypedDict):
    """
    教学工作流状态定义
    """

    # 用户输入
    user_input: str
    user_query: str
    user_level: str  # 初级/中级/高级

    # 上下文信息
    conversation_history: List[Dict[str, str]]
    current_step: Annotated[str, lambda x, y: y]  # 取最后一次更新的值
    workflow_id: str
    supplement_count: int  # 补充讲解次数，避免无限循环

    # 记忆数据
    existing_knowledge: List[Dict[str, Any]]  # 从记忆系统检索的知识
    new_knowledge: Dict[str, Any]  # 新学习的知识

    # 工具输出
    code_execution_result: str
    documentation_result: str
    practice_evaluation_result: str

    # Agent输出
    understanding_result: Dict[str, Any]
    memory_retrieval_result: Dict[str, Any]
    explanation_result: str
    example_result: str
    practice_result: str
    validation_result: Dict[str, Any]
    memory_update_result: Dict[str, Any]

    # 中间状态
    is_complete: bool
    error_message: Optional[str]
    feedback: str


class TeachingWorkflow:
    """
    教学工作流编排类
    """

    def __init__(
        self,
        memory_system: Optional[MemorySystem] = None,
        checkpoint_path: Optional[str] = None,
    ):
        """
        初始化教学工作流

        Args:
            memory_system: 记忆系统实例
            checkpoint_path: 检查点路径，用于中断和恢复
        """
        self.memory_system = memory_system or MemorySystem()
        # 初始化工具
        self.code_execution_tool = CodeExecutionTool()
        self.documentation_tool = DocumentationRetrievalTool()
        self.practice_evaluation_tool = PracticeEvaluationTool()
        # 初始化检查点，支持中断恢复
        self.checkpointer = MemorySaver()

        # 初始化各功能Agent
        self.understanding_agent = UnderstandingAgent()
        self.memory_retrieval_agent = MemoryRetrievalAgent(self.memory_system)
        self.explanation_agent = ExplanationAgent()
        self.example_generation_agent = ExampleGenerationAgent()
        self.practice_generation_agent = PracticeGenerationAgent()
        self.validation_agent = ValidationAgent()
        self.memory_update_agent = MemoryUpdateAgent(self.memory_system)

        # 创建状态图
        self.graph = self._build_workflow_graph()
        self.checkpointer = MemorySaver() if checkpoint_path is None else None

    def _build_workflow_graph(self):
        """
        构建教学工作流图

        Returns:
            状态图实例
        """
        logger.info("正在构建教学工作流图")

        graph = StateGraph(TeachingWorkflowState)

        # 定义节点
        graph.add_node("understanding", self._run_understanding)
        graph.add_node("memory_retrieval", self._run_memory_retrieval)
        graph.add_node("explanation", self._run_explanation)
        graph.add_node("example_generation", self._run_example_generation)
        graph.add_node("practice_generation", self._run_practice_generation)
        graph.add_node("validation", self._run_validation)
        graph.add_node("memory_update", self._run_memory_update)

        # 定义边（流程编排）
        graph.set_entry_point("understanding")
        graph.add_edge("understanding", "memory_retrieval")
        graph.add_edge("memory_retrieval", "explanation")
        graph.add_edge("explanation", "example_generation")
        graph.add_edge("example_generation", "practice_generation")
        graph.add_edge("practice_generation", "validation")
        graph.add_edge("validation", "memory_update")
        graph.add_edge("memory_update", END)

        # 添加条件路由（根据验证结果决定是否需要补充讲解）
        graph.add_conditional_edges(
            "validation",
            self._should_supplement_explanation,
            {
                "supplement": "explanation",
                "continue": "memory_update",
            },
        )

        return graph.compile(checkpointer=self.checkpointer)

    def _should_supplement_explanation(self, state: TeachingWorkflowState):
        """
        条件路由：判断是否需要补充讲解

        Args:
            state: 当前状态

        Returns:
            路由方向
        """
        validation_result = state.get("validation_result", {})
        score = validation_result.get("score", 0)
        needs_supplement = validation_result.get("needs_supplement", False)
        supplement_count = state.get("supplement_count", 0)

        # 最多补充讲解1次，避免无限循环
        if (score < 0.7 or needs_supplement) and supplement_count < 1:
            logger.info(f"验证分数较低，需要补充讲解 (当前次数: {supplement_count})")
            return "supplement"
        return "continue"

    def _run_understanding(self, state: TeachingWorkflowState):
        """
        理解评估节点

        Args:
            state: 当前状态

        Returns:
            新状态
        """
        logger.info("执行理解评估")

        result = self.understanding_agent.process(
            user_query=state["user_query"],
            conversation_history=state["conversation_history"],
            user_level=state["user_level"],
        )

        return {
            "understanding_result": result,
            "current_step": "understanding_completed",
        }

    def _run_memory_retrieval(self, state: TeachingWorkflowState):
        """
        记忆检索节点

        Args:
            state: 当前状态

        Returns:
            新状态
        """
        logger.info("执行记忆检索")

        result = self.memory_retrieval_agent.process(
            user_query=state["user_query"],
            user_level=state["user_level"],
        )

        return {
            "memory_retrieval_result": result,
            "existing_knowledge": result.get("related_knowledge", []),
            "current_step": "memory_retrieval_completed",
        }

    def _run_explanation(self, state: TeachingWorkflowState):
        """
        个性化讲解节点

        Args:
            state: 当前状态

        Returns:
            新状态
        """
        logger.info("执行个性化讲解")

        result = self.explanation_agent.process(
            user_query=state["user_query"],
            user_level=state["user_level"],
            related_knowledge=state["existing_knowledge"],
            understanding_result=state["understanding_result"],
        )

        # 补充讲解时计数器加1
        current_count = state.get("supplement_count", 0)
        if state.get("current_step") == "validation_completed":
            current_count += 1

        return {
            "explanation_result": result,
            "current_step": "explanation_completed",
            "supplement_count": current_count,
        }

    def _run_example_generation(self, state: TeachingWorkflowState):
        """
        示例生成节点

        Args:
            state: 当前状态

        Returns:
            新状态
        """
        logger.info("执行示例生成")

        result = self.example_generation_agent.process(
            user_query=state["user_query"],
            user_level=state["user_level"],
            explanation=state["explanation_result"],
            related_knowledge=state["existing_knowledge"],
        )

        return {
            "example_result": result,
            "current_step": "example_generation_completed",
        }

    def _run_practice_generation(self, state: TeachingWorkflowState):
        """
        练习生成节点

        Args:
            state: 当前状态

        Returns:
            新状态
        """
        logger.info("执行练习生成")

        result = self.practice_generation_agent.process(
            user_query=state["user_query"],
            user_level=state["user_level"],
            explanation=state["explanation_result"],
            example=state["example_result"],
        )

        return {
            "practice_result": result,
            "current_step": "practice_generation_completed",
        }

    def _run_validation(self, state: TeachingWorkflowState):
        """
        验证环节节点

        Args:
            state: 当前状态

        Returns:
            新状态
        """
        logger.info("执行验证环节")

        result = self.validation_agent.process(
            user_query=state["user_query"],
            user_level=state["user_level"],
            practice_result=state["practice_result"],
            explanation=state["explanation_result"],
        )

        return {
            "validation_result": result,
            "current_step": "validation_completed",
        }

    def _run_memory_update(self, state: TeachingWorkflowState):
        """
        记忆更新节点

        Args:
            state: 当前状态

        Returns:
            新状态
        """
        logger.info("执行记忆更新")

        result = self.memory_update_agent.process(
            user_query=state["user_query"],
            user_level=state["user_level"],
            explanation=state["explanation_result"],
            example=state["example_result"],
            practice=state["practice_result"],
            validation_result=state["validation_result"],
        )

        return {
            "memory_update_result": result,
            "new_knowledge": result.get("new_knowledge", {}),
            "current_step": "memory_update_completed",
            "is_complete": True,
        }

    def run(
        self,
        user_query: str,
        user_level: str = "intermediate",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        workflow_id: str = "default",
    ) -> Dict[str, Any]:
        """
        运行教学工作流

        Args:
            user_query: 用户查询
            user_level: 用户水平（初级/中级/高级）
            conversation_history: 对话历史
            workflow_id: 工作流ID，用于中断和恢复

        Returns:
            工作流执行结果
        """
        logger.info(f"开始执行教学工作流，用户查询: {user_query}，用户水平: {user_level}")

        # 初始化状态
        initial_state = TeachingWorkflowState(
            user_input=user_query,
            user_query=user_query,
            user_level=user_level,
            conversation_history=conversation_history or [],
            current_step="start",
            workflow_id=workflow_id,
            supplement_count=0,
            existing_knowledge=[],
            new_knowledge={},
            code_execution_result="",
            documentation_result="",
            practice_evaluation_result="",
            understanding_result={},
            memory_retrieval_result={},
            explanation_result="",
            example_result="",
            practice_result="",
            validation_result={},
            memory_update_result={},
            is_complete=False,
            error_message=None,
            feedback="",
        )

        # 运行工作流
        try:
            final_state = self.graph.invoke(
                initial_state,
                config={"configurable": {"thread_id": workflow_id}},
            )
            logger.info("教学工作流执行完成")
            return self._format_response(final_state)

        except Exception as e:
            logger.error(f"教学工作流执行失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "current_step": initial_state.get("current_step", "start"),
            }

    def _format_response(self, state: TeachingWorkflowState) -> Dict[str, Any]:
        """
        格式化工作流响应

        Args:
            state: 最终状态

        Returns:
            格式化后的响应
        """
        return {
            "success": True,
            "is_complete": state.get("is_complete", False),
            "user_query": state["user_query"],
            "user_level": state["user_level"],
            "explanation": state["explanation_result"],
            "example": state["example_result"],
            "practice": state["practice_result"],
            "validation": state["validation_result"],
            "new_knowledge": state["new_knowledge"],
            "existing_knowledge": state["existing_knowledge"],
            "conversation_history": state["conversation_history"],
            "current_step": state["current_step"],
            "feedback": state.get("feedback", ""),
        }

    def run_step_by_step(
        self,
        user_query: str,
        user_level: str = "intermediate",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        workflow_id: str = "default",
    ):
        """
        分步运行教学工作流，每步后等待用户确认

        Args:
            user_query: 用户查询
            user_level: 用户水平（初级/中级/高级）
            conversation_history: 对话历史
            workflow_id: 工作流ID
        """
        logger.info(f"开始分步执行教学工作流，用户查询: {user_query}，用户水平: {user_level}")

        # 初始化状态
        state = TeachingWorkflowState(
            user_input=user_query,
            user_query=user_query,
            user_level=user_level,
            conversation_history=conversation_history or [],
            current_step="start",
            workflow_id=workflow_id,
            supplement_count=0,
            existing_knowledge=[],
            new_knowledge={},
            code_execution_result="",
            documentation_result="",
            practice_evaluation_result="",
            understanding_result={},
            memory_retrieval_result={},
            explanation_result="",
            example_result="",
            practice_result="",
            validation_result={},
            memory_update_result={},
            is_complete=False,
            error_message=None,
            feedback="",
        )

        # 定义步骤列表
        steps = [
            ("understanding", "理解评估", self._run_understanding, lambda s: s["understanding_result"]),
            ("memory_retrieval", "记忆检索", self._run_memory_retrieval, lambda s: s["memory_retrieval_result"]),
            ("explanation", "个性化讲解", self._run_explanation, lambda s: s["explanation_result"]),
            ("example_generation", "示例生成", self._run_example_generation, lambda s: s["example_result"]),
            ("practice_generation", "练习生成", self._run_practice_generation, lambda s: s["practice_result"]),
            ("validation", "学习验证", self._run_validation, lambda s: s["validation_result"]),
            ("memory_update", "记忆更新", self._run_memory_update, lambda s: s["memory_update_result"]),
        ]

        try:
            for step_name, step_display, step_func, result_extractor in steps:
                print(f"\n{'=' * 60}")
                print(f"📋 执行步骤: {step_display}")
                print('=' * 60)

                # 执行当前步骤
                update = step_func(state)
                state.update(update)

                # 显示结果
                result = result_extractor(state)
                self._display_step_result(step_name, result)

                # 检查是否需要补充讲解
                if step_name == "validation":
                    if self._should_supplement_explanation(state) == "supplement":
                        print("\n💡 需要补充讲解，重新执行讲解步骤...")
                        update = self._run_explanation(state)
                        state.update(update)
                        self._display_step_result("explanation", state["explanation_result"])
                        if not self._ask_continue("继续下一步"):
                            break

                # 询问用户是否继续（除了最后一步）
                if step_name != "memory_update":
                    if not self._ask_continue("继续下一步"):
                        print("\n👋 用户选择停止，工作流已暂停")
                        return state

            print(f"\n{'=' * 60}")
            print("✅ 所有步骤完成！")
            print('=' * 60)
            return state

        except Exception as e:
            logger.error(f"分步工作流执行失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return state

    def _display_step_result(self, step_name: str, result):
        """
        显示步骤结果

        Args:
            step_name: 步骤名称
            result: 步骤结果
        """
        if step_name == "understanding":
            print(f"\n📊 理解评估结果:")
            print(f"   - 查询类型: {result.get('query_type', 'N/A')}")
            print(f"   - 主题: {', '.join(result.get('topics', []))}")
            print(f"   - 学习目标: {result.get('learning_objective', 'N/A')}")
            print(f"   - 难度: {result.get('difficulty', 'N/A')}")
        elif step_name == "memory_retrieval":
            knowledge = result.get('related_knowledge', [])
            print(f"\n🔍 检索到 {len(knowledge)} 条相关知识")
            if knowledge:
                for i, k in enumerate(knowledge[:3], 1):
                    print(f"   {i}. {k.get('title', '未知')}")
        elif step_name == "explanation":
            print(f"\n📚 讲解内容:")
            print('-' * 60)
            print(result)
            print('-' * 60)
        elif step_name == "example_generation":
            print(f"\n💻 示例代码:")
            print('-' * 60)
            print(result)
            print('-' * 60)
        elif step_name == "practice_generation":
            print(f"\n📝 练习题:")
            print('-' * 60)
            print(result)
            print('-' * 60)
        elif step_name == "validation":
            print(f"\n🎯 学习验证:")
            print(f"   - 掌握分数: {result.get('score', 0):.2f}")
            print(f"   - 掌握程度: {result.get('mastery_level', 'N/A')}")
            print(f"   - 反馈: {result.get('feedback', 'N/A')}")
        elif step_name == "memory_update":
            print(f"\n💾 记忆已更新")

    def _ask_continue(self, message: str = "继续") -> bool:
        """
        询问用户是否继续

        Args:
            message: 提示消息

        Returns:
            是否继续
        """
        while True:
            try:
                response = input(f"\n▶️ {message}？(y/n，默认y): ").strip().lower()
                if response in ["", "y", "yes", "是"]:
                    return True
                elif response in ["n", "no", "否"]:
                    return False
                else:
                    print("❌ 请输入 y 或 n")
            except KeyboardInterrupt:
                print("\n👋 用户中断")
                return False

    def resume(self, workflow_id: str) -> Dict[str, Any]:
        """
        恢复工作流执行

        Args:
            workflow_id: 工作流ID

        Returns:
            工作流执行结果
        """
        logger.info(f"正在恢复工作流: {workflow_id}")

        if not self.checkpointer:
            raise ValueError("工作流未配置检查点功能")

        try:
            final_state = self.graph.invoke(
                None,
                config={"configurable": {"checkpoint_id": workflow_id}},
            )
            logger.info("工作流恢复执行完成")
            return self._format_response(final_state)

        except Exception as e:
            logger.error(f"工作流恢复执行失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }


if __name__ == "__main__":
    # 测试工作流
    logger.info("开始测试教学工作流")

    try:
        # 创建工作流实例
        workflow = TeachingWorkflow()

        # 运行测试查询
        test_query = "什么是Python的装饰器？"
        logger.info(f"测试查询: {test_query}")

        result = workflow.run(
            user_query=test_query,
            user_level="intermediate",
            workflow_id="test_workflow_1",
        )

        logger.info(f"工作流执行结果: {result}")

        if result["success"]:
            logger.info("✅ 工作流执行成功")
            logger.info(f"解释: {result['explanation']}")
            logger.info(f"示例: {result['example']}")
            logger.info(f"练习: {result['practice']}")
            logger.info(f"验证: {result['validation']}")

        else:
            logger.error("❌ 工作流执行失败")

    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
