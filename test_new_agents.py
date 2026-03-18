#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新创建的功能Agent
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    print("=" * 60)
    print("Testing New Function Agents")
    print("=" * 60)

    # 检查文件是否存在
    print("\n[1/3] Checking file existence...")
    agent_files = [
        "src/agents/base_agent.py",
        "src/agents/code_explainer_agent.py",
        "src/agents/practice_generator_agent.py",
        "src/agents/learning_path_agent.py",
        "src/agents/debugging_guide_agent.py",
        "src/agents/progress_tracker_agent.py",
        "src/agents/content_validator_agent.py",
    ]

    prompt_files = [
        "config/prompts/code_explainer.yaml",
        "config/prompts/practice_generator.yaml",
        "config/prompts/learning_path.yaml",
        "config/prompts/debugging_guide.yaml",
        "config/prompts/progress_tracker.yaml",
        "config/prompts/content_validator.yaml",
    ]

    all_exist = True
    for f in agent_files + prompt_files:
        if os.path.exists(f):
            print(f"  [OK] {f}")
        else:
            print(f"  [FAIL] {f}")
            all_exist = False

    # 尝试单独导入BaseAgent
    print("\n[2/3] Testing BaseAgent import...")
    try:
        from src.agents.base_agent import BaseAgent
        print("  [OK] BaseAgent imported successfully")
    except Exception as e:
        print(f"  [FAIL] BaseAgent import failed: {e}")
        return 1

    # 尝试单独导入其他Agent
    print("\n[3/3] Testing other Agents import...")
    agents_to_test = [
        ("CodeExplainerAgent", "src.agents.code_explainer_agent"),
        ("PracticeGeneratorAgent", "src.agents.practice_generator_agent"),
        ("LearningPathAgent", "src.agents.learning_path_agent"),
        ("DebuggingGuideAgent", "src.agents.debugging_guide_agent"),
        ("ProgressTrackerAgent", "src.agents.progress_tracker_agent"),
        ("ContentValidatorAgent", "src.agents.content_validator_agent"),
    ]

    all_import_ok = True
    for name, module_path in agents_to_test:
        try:
            module = __import__(module_path, fromlist=[name])
            agent_class = getattr(module, name)
            print(f"  [OK] {name} imported successfully")
        except Exception as e:
            print(f"  [FAIL] {name} import failed: {e}")
            all_import_ok = False

    print("\n" + "=" * 60)
    if all_exist and all_import_ok:
        print("All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("Some tests failed.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
