#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BaseAgent基类：所有Agent的父类，封装LLM调用、记忆调用、工具调用的公共方法
"""

import os
import sys
import yaml
import logging
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional, Tuple

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BaseAgent:
    """
    所有Agent的基类，提供LLM调用、记忆管理、工具调用的公共方法
    """

    def __init__(self, agent_name: str):
        """
        初始化BaseAgent

        Args:
            agent_name: Agent名称，用于加载对应的提示词配置和记忆管理
        """
        self.agent_name = agent_name
        self.prompts = self._load_prompts()
        self.llm_config = self._load_llm_config()

    def _load_prompts(self) -> Dict[str, str]:
        """
        从配置文件加载提示词模板

        Returns:
            提示词模板字典
        """
        try:
            prompt_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "config",
                "prompts",
                f"{self.agent_name}.yaml"
            )

            if not os.path.exists(prompt_file):
                logger.warning(f"提示词配置文件不存在: {prompt_file}")
                return {}

            with open(prompt_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载提示词配置失败: {e}")
            return {}

    def _load_llm_config(self) -> Dict[str, Any]:
        """
        从环境变量加载LLM配置

        Returns:
            LLM配置字典
        """
        return {
            "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
            "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.siliconflow.cn/v1"),
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-V3.2"),
            "max_tokens": int(os.getenv("MAX_CONTEXT_TOKENS", "8192")),
            "temperature": 0.2  # 较低的温度，保证输出稳定
        }

    def _call_llm(self, prompt: str) -> str:
        """
        调用LLM接口

        Args:
            prompt: 输入提示词

        Returns:
            LLM返回的文本
        """
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=self.llm_config["api_key"],
                base_url=self.llm_config["base_url"]
            )

            response = client.chat.completions.create(
                model=self.llm_config["model"],
                messages=[
                    {"role": "system", "content": "You are a helpful programming learning assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.llm_config["max_tokens"],
                temperature=self.llm_config["temperature"]
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return f"调用LLM失败: {e}"

    def _format_prompt(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        格式化提示词模板

        Args:
            template_name: 模板名称
            variables: 模板变量字典

        Returns:
            格式化后的提示词
        """
        template = self.prompts.get(template_name, "")
        if not template:
            logger.warning(f"提示词模板不存在: {template_name}")
            return ""

        try:
            return template.format(**variables)
        except Exception as e:
            logger.error(f"提示词格式化失败: {e}")
            return ""

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Agent的主逻辑

        Args:
            inputs: 输入参数字典

        Returns:
            执行结果字典
        """
        raise NotImplementedError("子类必须实现run方法")

    def save_memory(self, key: str, value: Any) -> None:
        """
        保存记忆到内存（可以扩展到持久化存储）

        Args:
            key: 记忆的键
            value: 记忆的值
        """
        # 目前实现简单的内存存储
        if not hasattr(self, "_memory"):
            self._memory = {}
        self._memory[key] = value
        logger.info(f"记忆已保存: {key}")

    def load_memory(self, key: str, default: Any = None) -> Any:
        """
        从内存加载记忆

        Args:
            key: 记忆的键
            default: 缺省值

        Returns:
            记忆的值
        """
        if hasattr(self, "_memory"):
            return self._memory.get(key, default)
        return default

    def validate_input(self, required_fields: List[str], **kwargs) -> bool:
        """
        验证输入参数是否完整

        Args:
            required_fields: 必需的字段列表
            **kwargs: 输入参数

        Returns:
            是否验证通过
        """
        for field in required_fields:
            if field not in kwargs or kwargs[field] is None or kwargs[field] == "":
                logger.warning(f"缺少必需参数: {field}")
                return False
        return True

    def log_process(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        记录处理过程日志

        Args:
            inputs: 输入参数
            outputs: 输出结果
        """
        logger.debug(f"Agent {self.agent_name} 处理完成")
        logger.debug(f"输入: {inputs}")
        logger.debug(f"输出: {outputs}")


if __name__ == "__main__":
    # 测试BaseAgent
    try:
        agent = BaseAgent("base_agent")
        print("BaseAgent初始化成功")
        print("LLM配置:", agent.llm_config)
        print("提示词配置:", agent.prompts)

        # 测试LLM调用
        test_prompt = "Hello, world!"
        response = agent._call_llm(test_prompt)
        print(f"LLM调用测试: {response}")
    except Exception as e:
        print(f"测试失败: {e}")
