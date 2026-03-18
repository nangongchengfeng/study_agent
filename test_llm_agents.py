"""
测试所有 Agent 是否真正调用 LLM
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agents.understanding_agent import UnderstandingAgent
from agents.explanation_agent import ExplanationAgent
from agents.example_generation_agent import ExampleGenerationAgent
from agents.validation_agent import ValidationAgent
from agents.practice_generation_agent import PracticeGenerationAgent


def test_all_agents():
    """测试所有 Agent"""
    test_query = "什么是Python中的列表推导式？"
    user_level = "beginner"
    
    print("=" * 60)
    print("测试所有 Agent")
    print("=" * 60)
    
    try:
        print("\n1. 测试 UnderstandingAgent...")
        understanding_agent = UnderstandingAgent()
        understanding_result = understanding_agent.process(
            user_query=test_query,
            conversation_history=[],
            user_level=user_level
        )
        print(f"✓ UnderstandingAgent 成功！结果: {understanding_result}")
        
        print("\n2. 测试 ExplanationAgent...")
        explanation_agent = ExplanationAgent()
        explanation_result = explanation_agent.process(
            user_query=test_query,
            user_level=user_level,
            related_knowledge=[],
            understanding_result=understanding_result
        )
        print(f"✓ ExplanationAgent 成功！内容长度: {len(explanation_result)}")
        
        print("\n3. 测试 ExampleGenerationAgent...")
        example_agent = ExampleGenerationAgent()
        example_result = example_agent.process(
            user_query=test_query,
            user_level=user_level,
            explanation=explanation_result
        )
        print(f"✓ ExampleGenerationAgent 成功！内容长度: {len(example_result)}")
        
        print("\n4. 测试 PracticeGenerationAgent...")
        practice_agent = PracticeGenerationAgent()
        practice_result = practice_agent.process(
            user_query=test_query,
            user_level=user_level,
            explanation=explanation_result,
            example=example_result
        )
        print(f"✓ PracticeGenerationAgent 成功！内容长度: {len(practice_result)}")
        
        print("\n5. 测试 ValidationAgent...")
        validation_agent = ValidationAgent()
        validation_result = validation_agent.process(
            user_query=test_query,
            user_level=user_level,
            practice_result=practice_result,
            explanation=explanation_result
        )
        print(f"✓ ValidationAgent 成功！结果: {validation_result}")
        
        print("\n" + "=" * 60)
        print("所有 Agent 测试成功！🎉")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_all_agents()
