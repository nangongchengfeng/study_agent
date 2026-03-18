"""
教学工作流测试
"""

import sys
import os
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_workflow_initialization():
    """
    测试工作流初始化
    """
    logger.info("测试工作流初始化")

    try:
        from src.workflows import TeachingWorkflow

        workflow = TeachingWorkflow()
        logger.info("✅ 工作流初始化成功")

        return True

    except Exception as e:
        logger.error(f"❌ 工作流初始化失败: {str(e)}")
        return False


def test_memory_system():
    """
    测试记忆系统
    """
    logger.info("测试记忆系统")

    try:
        from src.memory import MemorySystem

        memory_system = MemorySystem()

        # 测试检索
        results = memory_system.retrieve(
            keywords=["Python", "装饰器"],
            user_level="intermediate",
            limit=3,
        )

        logger.info(f"✅ 记忆系统测试成功，检索到 {len(results)} 条结果")

        return True

    except Exception as e:
        logger.error(f"❌ 记忆系统测试失败: {str(e)}")
        return False


def test_agents():
    """
    测试各功能Agent
    """
    logger.info("测试功能Agent")

    try:
        from src.agents import (
            UnderstandingAgent,
            ExplanationAgent,
            ExampleGenerationAgent,
            PracticeGenerationAgent,
            ValidationAgent,
        )

        # 测试理解Agent
        understanding_agent = UnderstandingAgent()
        understanding_result = understanding_agent.process(
            user_query="什么是Python装饰器？",
            conversation_history=[],
            user_level="intermediate",
        )
        logger.info("✅ 理解Agent测试成功")

        # 测试讲解Agent
        explanation_agent = ExplanationAgent()
        explanation = explanation_agent.process(
            user_query="什么是Python装饰器？",
            user_level="intermediate",
            related_knowledge=[],
            understanding_result=understanding_result,
        )
        logger.info("✅ 讲解Agent测试成功")

        # 测试示例Agent
        example_agent = ExampleGenerationAgent()
        example = example_agent.process(
            user_query="什么是Python装饰器？",
            user_level="intermediate",
            explanation=explanation,
            related_knowledge=[],
        )
        logger.info("✅ 示例生成Agent测试成功")

        # 测试练习Agent
        practice_agent = PracticeGenerationAgent()
        practice = practice_agent.process(
            user_query="什么是Python装饰器？",
            user_level="intermediate",
            explanation=explanation,
            example=example,
        )
        logger.info("✅ 练习生成Agent测试成功")

        # 测试验证Agent
        validation_agent = ValidationAgent()
        validation = validation_agent.process(
            user_query="什么是Python装饰器？",
            user_level="intermediate",
            practice_result=practice,
            explanation=explanation,
        )
        logger.info("✅ 验证Agent测试成功")

        return True

    except Exception as e:
        logger.error(f"❌ Agent测试失败: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def test_tools():
    """
    测试工具层
    """
    logger.info("测试工具层")

    try:
        from src.tools import (
            CodeExecutionTool,
            DocumentationRetrievalTool,
            PracticeEvaluationTool,
        )

        # 测试代码执行工具
        code_tool = CodeExecutionTool()
        code_result = code_tool.run("print('Hello, World!')")
        logger.info("✅ 代码执行工具测试成功")

        # 测试文档检索工具
        doc_tool = DocumentationRetrievalTool()
        doc_result = doc_tool.run("Python 装饰器")
        logger.info("✅ 文档检索工具测试成功")

        # 测试练习评估工具
        eval_tool = PracticeEvaluationTool()
        eval_result = eval_tool.run(
            user_answer="装饰器是用来修改函数行为的",
            expected_answer="装饰器是Python中修改函数或类行为的设计模式",
        )
        logger.info("✅ 练习评估工具测试成功")

        return True

    except Exception as e:
        logger.error(f"❌ 工具层测试失败: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def test_workflow_end_to_end():
    """
    端到端工作流测试
    """
    logger.info("测试端到端工作流")

    try:
        from src.workflows import TeachingWorkflow

        workflow = TeachingWorkflow()

        # 运行工作流
        result = workflow.run(
            user_query="什么是Python装饰器？",
            user_level="intermediate",
            workflow_id="test_workflow_001",
        )

        if result.get("success", False):
            logger.info("✅ 端到端工作流测试成功")
            logger.info(f"   - 解释: {result.get('explanation', '')[:100]}...")
            logger.info(f"   - 验证分数: {result.get('validation', {}).get('score', 0)}")

            return True
        else:
            logger.error(f"❌ 工作流执行失败: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        logger.error(f"❌ 端到端工作流测试失败: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def run_all_tests():
    """
    运行所有测试
    """
    logger.info("=" * 60)
    logger.info("开始运行教学工作流测试")
    logger.info("=" * 60)

    results = []

    # 测试1: 记忆系统
    results.append(("记忆系统", test_memory_system()))

    # 测试2: 功能Agent
    results.append(("功能Agent", test_agents()))

    # 测试3: 工具层
    results.append(("工具层", test_tools()))

    # 测试4: 工作流初始化
    results.append(("工作流初始化", test_workflow_initialization()))

    # 测试5: 端到端工作流
    results.append(("端到端工作流", test_workflow_end_to_end()))

    # 输出总结
    logger.info("=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        logger.info(f"{name}: {status}")

    logger.info("=" * 60)
    logger.info(f"总计: {passed_tests}/{total_tests} 测试通过")
    logger.info("=" * 60)

    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
