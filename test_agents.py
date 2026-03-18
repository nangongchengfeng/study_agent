#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有功能Agent是否可以正常导入和初始化
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """测试所有Agent能否正常导入"""
    print("=" * 60)
    print("测试Agent导入")
    print("=" * 60)

    try:
        from src.agents import (
            BaseAgent,
            CodeExplainerAgent,
            PracticeGeneratorAgent,
            LearningPathAgent,
            DebuggingGuideAgent,
            ProgressTrackerAgent,
            ContentValidatorAgent
        )
        print("✅ 所有Agent导入成功")
        return True
    except Exception as e:
        print(f"❌ Agent导入失败: {e}")
        return False


def test_initialization():
    """测试所有Agent能否正常初始化"""
    print("\n" + "=" * 60)
    print("测试Agent初始化")
    print("=" * 60)

    try:
        from src.agents import (
            CodeExplainerAgent,
            PracticeGeneratorAgent,
            LearningPathAgent,
            DebuggingGuideAgent,
            ProgressTrackerAgent,
            ContentValidatorAgent
        )

        agents = [
            ("CodeExplainerAgent", CodeExplainerAgent),
            ("PracticeGeneratorAgent", PracticeGeneratorAgent),
            ("LearningPathAgent", LearningPathAgent),
            ("DebuggingGuideAgent", DebuggingGuideAgent),
            ("ProgressTrackerAgent", ProgressTrackerAgent),
            ("ContentValidatorAgent", ContentValidatorAgent),
        ]

        for name, agent_class in agents:
            try:
                agent = agent_class()
                print(f"✅ {name} 初始化成功")
            except Exception as e:
                print(f"❌ {name} 初始化失败: {e}")
                return False

        return True
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return False


def test_prompts():
    """测试提示词配置文件是否存在"""
    print("\n" + "=" * 60)
    print("测试提示词配置文件")
    print("=" * 60)

    prompt_files = [
        "code_explainer.yaml",
        "practice_generator.yaml",
        "learning_path.yaml",
        "debugging_guide.yaml",
        "progress_tracker.yaml",
        "content_validator.yaml",
    ]

    config_dir = os.path.join(os.path.dirname(__file__), "config", "prompts")

    all_exists = True
    for prompt_file in prompt_files:
        file_path = os.path.join(config_dir, prompt_file)
        if os.path.exists(file_path):
            print(f"✅ {prompt_file} 存在")
        else:
            print(f"❌ {prompt_file} 不存在")
            all_exists = False

    return all_exists


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "功能Agent测试" + " " * 34 + "║")
    print("╚" + "═" * 58 + "╝")

    results = []
    results.append(("导入测试", test_imports()))
    results.append(("初始化测试", test_initialization()))
    results.append(("提示词配置测试", test_prompts()))

    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)

    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查相关文件")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
