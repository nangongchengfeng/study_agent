#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度追踪Agent：更新用户学习记录，维护用户知识图谱
"""

from src.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class ProgressTrackerAgent(BaseAgent):
    """
    进度追踪Agent，负责更新学习记录和知识图谱
    """

    def __init__(self):
        super().__init__("progress_tracker")

    def update_progress(self, learning_record: dict, current_knowledge_graph: dict) -> str:
        """
        更新用户知识图谱

        Args:
            learning_record: 学习记录
            current_knowledge_graph: 当前知识图谱

        Returns:
            更新后的知识图谱
        """
        prompt = self._format_prompt(
            "update_progress_prompt",
            {
                "learning_record": str(learning_record),
                "current_knowledge_graph": str(current_knowledge_graph)
            }
        )
        if not prompt:
            return "提示词配置错误"

        return self._call_llm(prompt)

    def analyze_behavior(self, learning_record: dict) -> str:
        """
        分析用户学习行为

        Args:
            learning_record: 学习记录

        Returns:
            行为分析结果
        """
        prompt = self._format_prompt("analyze_behavior_prompt", {"learning_record": str(learning_record)})
        if not prompt:
            return "提示词配置错误"

        return self._call_llm(prompt)

    def run(self, inputs: dict) -> dict:
        """
        执行进度追踪任务

        Args:
            inputs: 输入参数
                - action: 动作类型，可选值：update 更新进度，analyze 行为分析
                - learning_record: 学习记录
                - current_knowledge_graph: 当前知识图谱（update时需要）

        Returns:
            处理结果
        """
        try:
            action = inputs.get("action", "update")
            learning_record = inputs.get("learning_record", {})

            if not learning_record:
                return {
                    "success": False,
                    "error": "请提供学习记录"
                }

            if action == "update":
                current_knowledge_graph = inputs.get("current_knowledge_graph", {})

                if not current_knowledge_graph:
                    return {
                        "success": False,
                        "error": "请提供当前知识图谱"
                    }

                result = self.update_progress(learning_record, current_knowledge_graph)
            elif action == "analyze":
                result = self.analyze_behavior(learning_record)
            else:
                return {
                    "success": False,
                    "error": "无效的动作类型"
                }

            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"ProgressTrackerAgent运行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    # 测试ProgressTrackerAgent
    agent = ProgressTrackerAgent()

    # 示例学习记录
    sample_learning_record = {
        "日期": "2026-03-17",
        "学习内容": "Python函数编程",
        "练习数量": 10,
        "正确数量": 8,
        "学习时长": 90,
        "难度": "中等",
        "错题": ["递归函数", "装饰器"]
    }

    # 示例当前知识图谱
    sample_knowledge_graph = {
        "Python基础": {
            "掌握程度": 75,
            "已练习": 15,
            "正确率": 80,
            "弱项": ["函数", "列表推导式"]
        },
        "数据结构": {
            "掌握程度": 50,
            "已练习": 8,
            "正确率": 65,
            "弱项": ["链表", "栈"]
        }
    }

    # 测试进度更新
    print("=== 进度更新测试 ===\n")
    result1 = agent.run({
        "action": "update",
        "learning_record": sample_learning_record,
        "current_knowledge_graph": sample_knowledge_graph
    })
    print(f"成功: {result1['success']}")
    print(f"结果:\n{result1['result']}")
    print("\n" + "="*50 + "\n")

    # 测试行为分析
    print("=== 行为分析测试 ===\n")
    result2 = agent.run({
        "action": "analyze",
        "learning_record": [
            sample_learning_record,
            {
                "日期": "2026-03-16",
                "学习内容": "Python列表操作",
                "练习数量": 8,
                "正确数量": 7,
                "学习时长": 60,
                "难度": "简单",
                "错题": ["列表切片"]
            }
        ]
    })
    print(f"成功: {result2['success']}")
    print(f"结果:\n{result2['result']}")
