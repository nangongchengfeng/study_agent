"""
测试分步执行功能（非交互式）
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.workflows import TeachingWorkflow


def test_step_by_step():
    """测试分步执行"""
    print("=" * 60)
    print("测试分步执行功能")
    print("=" * 60)
    
    workflow = TeachingWorkflow()
    
    test_query = "什么是Python的继承？"
    
    # 我们手动模拟分步执行逻辑，不使用交互式输入
    state = {
        "user_input": test_query,
        "user_query": test_query,
        "user_level": "intermediate",
        "conversation_history": [],
        "current_step": "start",
        "workflow_id": "test_step",
        "supplement_count": 0,
        "existing_knowledge": [],
        "new_knowledge": {},
        "code_execution_result": "",
        "documentation_result": "",
        "practice_evaluation_result": "",
        "understanding_result": {},
        "memory_retrieval_result": {},
        "explanation_result": "",
        "example_result": "",
        "practice_result": "",
        "validation_result": {},
        "memory_update_result": {},
        "is_complete": False,
        "error_message": None,
        "feedback": "",
    }
    
    steps = [
        ("understanding", "理解评估"),
        ("memory_retrieval", "记忆检索"),
        ("explanation", "个性化讲解"),
        ("example_generation", "示例生成"),
        ("practice_generation", "练习生成"),
        ("validation", "学习验证"),
        ("memory_update", "记忆更新"),
    ]
    
    try:
        for step_name, step_display in steps:
            print(f"\n{'=' * 60}")
            print(f"📋 执行步骤: {step_display}")
            print('=' * 60)
            
            if step_name == "understanding":
                update = workflow._run_understanding(state)
                state.update(update)
                result = state["understanding_result"]
                print(f"\n📊 理解评估结果:")
                print(f"   - 查询类型: {result.get('query_type', 'N/A')}")
                print(f"   - 主题: {', '.join(result.get('topics', []))}")
                print(f"   - 学习目标: {result.get('learning_objective', 'N/A')}")
                print(f"   - 难度: {result.get('difficulty', 'N/A')}")
            
            elif step_name == "memory_retrieval":
                update = workflow._run_memory_retrieval(state)
                state.update(update)
                result = state["memory_retrieval_result"]
                knowledge = result.get('related_knowledge', [])
                print(f"\n🔍 检索到 {len(knowledge)} 条相关知识")
                if knowledge:
                    for i, k in enumerate(knowledge[:3], 1):
                        print(f"   {i}. {k.get('title', '未知')}")
            
            elif step_name == "explanation":
                update = workflow._run_explanation(state)
                state.update(update)
                result = state["explanation_result"]
                print(f"\n📚 讲解内容:")
                print('-' * 60)
                print(result[:500] + "..." if len(result) > 500 else result)
                print('-' * 60)
            
            elif step_name == "example_generation":
                update = workflow._run_example_generation(state)
                state.update(update)
                result = state["example_result"]
                print(f"\n💻 示例代码:")
                print('-' * 60)
                print(result[:500] + "..." if len(result) > 500 else result)
                print('-' * 60)
            
            elif step_name == "practice_generation":
                update = workflow._run_practice_generation(state)
                state.update(update)
                result = state["practice_result"]
                print(f"\n📝 练习题:")
                print('-' * 60)
                print(result[:500] + "..." if len(result) > 500 else result)
                print('-' * 60)
            
            elif step_name == "validation":
                update = workflow._run_validation(state)
                state.update(update)
                result = state["validation_result"]
                print(f"\n🎯 学习验证:")
                print(f"   - 掌握分数: {result.get('score', 0):.2f}")
                print(f"   - 掌握程度: {result.get('mastery_level', 'N/A')}")
                feedback = result.get('feedback', 'N/A')
                print(f"   - 反馈: {feedback[:200] + '...' if len(feedback) > 200 else feedback}")
            
            elif step_name == "memory_update":
                update = workflow._run_memory_update(state)
                state.update(update)
                print(f"\n💾 记忆已更新")
        
        print(f"\n{'=' * 60}")
        print("✅ 所有步骤测试通过！")
        print('=' * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_step_by_step()
    sys.exit(0 if success else 1)
