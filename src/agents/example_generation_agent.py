"""
示例生成Agent
负责生成教学代码示例
"""

import logging
from typing import Any, Dict, List, Optional
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ExampleGenerationAgent(BaseAgent):
    """
    示例生成Agent
    """

    def __init__(self):
        super().__init__("ExampleGenerationAgent")

    def process(
        self,
        user_query: str,
        user_level: str,
        explanation: str,
        related_knowledge: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> str:
        """
        生成示例代码

        Args:
            user_query: 用户查询
            user_level: 用户水平
            explanation: 讲解内容
            related_knowledge: 相关知识

        Returns:
            示例代码
        """
        logger.info(f"生成示例代码: {user_query}")

        if not self.validate_input(["user_query", "explanation"],
                                    user_query=user_query, explanation=explanation):
            return "抱歉，缺少必要信息来生成示例。"

        try:
            prompt = self._build_prompt(user_query, user_level, explanation)
            example = self._call_llm(prompt)

            self.log_process(
                {"user_query": user_query, "explanation": explanation},
                {"example_length": len(example)},
            )

            return example
        except Exception as e:
            logger.error(f"ExampleGenerationAgent 处理失败: {e}")
            return self._get_fallback_example(user_query, user_level)

    def _build_prompt(
        self,
        user_query: str,
        user_level: str,
        explanation: str,
    ) -> str:
        """
        构建提示词

        Args:
            user_query: 用户查询
            user_level: 用户水平
            explanation: 讲解内容

        Returns:
            提示词字符串
        """
        system_prompt = self.prompts.get("system_prompt", "")

        prompt = f"""{system_prompt}

用户问题: {user_query}
用户水平: {user_level}
讲解内容:
{explanation}

请直接给出示例代码，不要包含任何额外的说明文字。"""

        return prompt

    def _get_fallback_example(self, user_query: str, user_level: str) -> str:
        """
        获取降级示例

        Args:
            user_query: 用户查询
            user_level: 用户水平

        Returns:
            降级示例
        """
        return f"""## 编程学习示例

### 示例 1：基础语法练习
```python
# 变量和类型
name = "Python"
version = 3.12
is_awesome = True

print(f"{{name}} {{version}} 是很棒的: {{is_awesome}}")

# 列表操作
numbers = [1, 2, 3, 4, 5]
numbers.append(6)
numbers_double = [x * 2 for x in numbers]
print(numbers_double)

# 字典操作
person = {{"name": "Alice", "age": 25}}
person["city"] = "北京"
print(person)
```

### 示例 2：简单的类
```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return f"{{self.name}} 说: 汪汪！"

class Cat(Animal):
    def speak(self):
        return f"{{self.name}} 说: 喵喵！"

dog = Dog("旺财")
cat = Cat("咪咪")
print(dog.speak())
print(cat.speak())
```

### 动手练习
1. 尝试修改上面的代码
2. 添加新的功能
3. 运行看看效果

编程最好的学习方式就是动手写代码！"""
