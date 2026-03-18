#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习路径规划Agent：根据用户知识图谱分析，生成个性化学习路径和学习建议
"""

from src.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class LearningPathAgent(BaseAgent):
    """
    学习路径规划Agent，负责分析知识图谱和生成学习路径
    """

    def __init__(self):
        super().__init__("learning_path")

    def analyze_knowledge(self, knowledge_graph: dict) -> str:
        """
        分析用户的知识图谱，评估用户的当前水平

        Args:
            knowledge_graph: 用户知识图谱

        Returns:
            分析结果
        """
        prompt = self._format_prompt(
            "analyze_prompt",
            {"knowledge_graph": str(knowledge_graph)}
        )
        if not prompt:
            return "提示词配置错误"

        return self._call_llm(prompt)

    def plan_learning(self, knowledge_graph: dict, learning_goal: str, duration: str = "30天") -> str:
        """
        生成个性化的学习路径

        Args:
            knowledge_graph: 用户知识图谱
            learning_goal: 学习目标
            duration: 预计学习时长

        Returns:
            学习路径
        """
        prompt = self._format_prompt(
            "plan_prompt",
            {
                "knowledge_graph": str(knowledge_graph),
                "learning_goal": learning_goal,
                "duration": duration
            }
        )
        if not prompt:
            return "提示词配置错误"

        return self._call_llm(prompt)

    def run(self, inputs: dict) -> dict:
        """
        执行知识图谱分析或学习路径规划任务

        Args:
            inputs: 输入参数
                - action: 动作类型，可选值：analyze 分析，plan 规划
                - knowledge_graph: 用户知识图谱
                - learning_goal: 学习目标（plan时需要）
                - duration: 预计学习时长（plan时可选）

        Returns:
            处理结果
        """
        try:
            action = inputs.get("action", "analyze")
            knowledge_graph = inputs.get("knowledge_graph", {})

            if not knowledge_graph:
                return {
                    "success": False,
                    "error": "请提供用户知识图谱"
                }

            if action == "analyze":
                result = self.analyze_knowledge(knowledge_graph)
            elif action == "plan":
                learning_goal = inputs.get("learning_goal", "成为Python开发者")
                duration = inputs.get("duration", "30天")

                result = self.plan_learning(knowledge_graph, learning_goal, duration)
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
            logger.error(f"LearningPathAgent运行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    # 测试LearningPathAgent
    agent = LearningPathAgent()

    # 示例知识图谱
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
        },
        "算法": {
            "掌握程度": 30,
            "已练习": 5,
            "正确率": 40,
            "弱项": ["动态规划"]
        }
    }

    # 测试知识图谱分析
    print("=== 知识图谱分析测试 ===\n")
    result1 = agent.run({
        "action": "analyze",
        "knowledge_graph": sample_knowledge_graph
    })
    print(f"成功: {result1['success']}")
    print(f"结果:\n{result1['result']}")
    print("\n" + "="*50 + "\n")

    # 测试学习路径规划
    print("=== 学习路径规划测试 ===\n")
    result2 = agent.run({
        "action": "plan",
        "knowledge_graph": sample_knowledge_graph,
        "learning_goal": "成为Python全栈开发工程师",
        "duration": "3个月"
    })
    print(f"成功: {result2['success']}")
    print(f"结果:\n{result2['result']}")
