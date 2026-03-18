"""
智能编程学习导师 - 入口程序
演示如何使用教学工作流
"""

import sys
import os
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    主程序
    """
    logger.info("=" * 60)
    logger.info("智能编程学习导师")
    logger.info("=" * 60)

    try:
        from src.workflows import TeachingWorkflow

        # 创建工作流实例
        workflow = TeachingWorkflow()

        logger.info("✅ 教学工作流已启动")
        logger.info("")
        logger.info("请输入您的问题（输入 q 退出）:")
        logger.info("")

        while True:
            try:
                user_input = input("💬 用户: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["q", "quit", "exit"]:
                    logger.info("👋 再见！感谢使用智能编程学习导师")
                    break

                # 运行分步工作流
                logger.info("🤔 正在处理您的问题...")

                workflow.run_step_by_step(
                    user_query=user_input,
                    user_level="intermediate",
                    workflow_id="demo_workflow",
                )

                logger.info("")
                logger.info("=" * 60)

            except KeyboardInterrupt:
                logger.info("")
                logger.info("👋 再见！感谢使用智能编程学习导师")
                break
            except Exception as e:
                logger.error(f"❌ 发生错误: {str(e)}")
                import traceback

                logger.error(traceback.format_exc())

    except Exception as e:
        logger.error(f"❌ 启动失败: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        sys.exit(1)


def quick_start():
    """
    快速开始示例
    """
    logger.info("=" * 60)
    logger.info("智能编程学习导师 - 快速开始")
    logger.info("=" * 60)

    try:
        from src.workflows import TeachingWorkflow

        workflow = TeachingWorkflow()

        # 测试查询
        logger.info("🧪 正在演示教学工作流...")

        test_query = "什么是Python装饰器？"
        logger.info(f"💬 用户问题: {test_query}")

        # 使用分步执行模式
        workflow.run_step_by_step(
            user_query=test_query,
            user_level="intermediate",
            workflow_id="quick_start_demo",
        )

        logger.info("")
        logger.info("=" * 60)
        logger.info("")
        logger.info("✅ 演示完成！")
        logger.info("")
        logger.info("如需交互式体验，请运行: python main.py")

    except Exception as e:
        logger.error(f"❌ 演示失败: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_start()
    else:
        main()
