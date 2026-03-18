"""
记忆系统使用示例
演示如何使用三层记忆系统
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.memory import MemorySystem


def demo_sensory_memory():
    """演示感觉记忆的使用"""
    print("=" * 50)
    print("演示感觉记忆")
    print("=" * 50)

    ms = MemorySystem()

    # 添加对话历史
    ms.update_memory(
        "sensory",
        "如何在Python中实现单例模式？",
        {"role": "user", "type": "question"}
    )
    ms.update_memory(
        "sensory",
        "Python实现单例模式有几种方式，包括使用装饰器、元类、__new__方法等。",
        {"role": "assistant", "type": "answer"}
    )
    ms.update_memory(
        "sensory",
        "可以给我一个装饰器的例子吗？",
        {"role": "user", "type": "question"}
    )

    # 获取所有对话
    memory = ms.get_memory("sensory")
    print(f"当前对话轮数: {len(memory)}")
    print()

    # 获取角色为用户的对话
    user_messages = ms.get_memory("sensory", query={"role": "user"})
    print(f"用户消息数: {len(user_messages)}")
    for msg in user_messages:
        print(f"  - {msg['content']}")
    print()

    # 转换为prompt格式
    prompt = ms.sensory_memory.to_prompt("simple")
    print("Prompt格式:")
    print(prompt)
    print()


def demo_short_term_memory():
    """演示短期记忆的使用"""
    print("=" * 50)
    print("演示短期记忆")
    print("=" * 50)

    ms = MemorySystem()

    # 记录学习会话
    session_metadata = {
        "type": "learning",
        "topic": "Python 装饰器",
        "tags": ["python", "decorator", "design-pattern"],
    }

    ms.update_memory("short", {
        "code_snippet": """def singleton(cls):
    instances = {}
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper""",
        "notes": "使用装饰器实现单例模式",
        "errors": [],
    }, session_metadata)

    # 再记录一个会话
    ms.update_memory("short", {
        "code_snippet": """class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]""",
        "notes": "使用元类实现单例模式",
        "errors": [],
    }, {
        "type": "learning",
        "topic": "Python 元类",
        "tags": ["python", "metaclass", "design-pattern"],
    })

    # 获取所有会话
    sessions = ms.get_memory("short")
    print(f"学习会话数: {len(sessions)}")
    for session in sessions:
        print(f"  - {session['metadata'].get('topic', 'Unknown')}")
    print()

    # 按标签搜索
    decorator_sessions = ms.get_memory("short", query={"tags": ["decorator"]})
    print(f"标签为'decorator'的会话数: {len(decorator_sessions)}")
    print()


def demo_long_term_memory():
    """演示长期记忆的使用"""
    print("=" * 50)
    print("演示长期记忆（知识图谱）")
    print("=" * 50)

    ms = MemorySystem()

    # 添加知识点
    ms.update_memory("long", {
        "name": "Python 装饰器",
        "description": "装饰器是一种设计模式，用于在不修改原函数代码的情况下扩展其功能",
        "category": "python",
        "difficulty": "intermediate",
        "status": "learning",
        "proficiency": 75,
        "tags": ["python", "decorator", "design-pattern"],
    }, {"type": "knowledge_point", "id": "kp-decorator"})

    ms.update_memory("long", {
        "name": "Python 元类",
        "description": "元类是创建类的类，Python中所有类都是type的实例",
        "category": "python",
        "difficulty": "advanced",
        "status": "learning",
        "proficiency": 40,
        "tags": ["python", "metaclass", "advanced"],
    }, {"type": "knowledge_point", "id": "kp-metaclass"})

    ms.update_memory("long", {
        "name": "单例模式",
        "description": "确保一个类只有一个实例，并提供全局访问点",
        "category": "design-pattern",
        "difficulty": "beginner",
        "status": "mastered",
        "proficiency": 90,
        "tags": ["design-pattern", "creational"],
    }, {"type": "knowledge_point", "id": "kp-singleton"})

    # 添加知识点关联
    ms.update_memory("long", {
        "source_id": "kp-decorator",
        "target_id": "kp-singleton",
        "type": "prerequisite",
        "weight": 0.8,
    }, {"type": "relationship"})

    ms.update_memory("long", {
        "source_id": "kp-metaclass",
        "target_id": "kp-singleton",
        "type": "prerequisite",
        "weight": 0.6,
    }, {"type": "relationship"})

    # 添加代码作品
    ms.update_memory("long", {
        "title": "单例模式实现集锦",
        "description": "展示Python中实现单例模式的多种方法",
        "language": "python",
        "code": """# 装饰器实现
def singleton(cls):
    instances = {}
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper

# 元类实现
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

# 使用
@singleton
class MyClass:
    pass

class MyClass2(metaclass=SingletonMeta):
    pass
""",
        "tags": ["singleton", "decorator", "metaclass"],
    }, {"type": "code_snippet"})

    # 添加学习记录
    ms.update_memory("long", {
        "topic": "学习Python装饰器",
        "duration": 45,  # 分钟
        "focus_points": ["基本语法", "带参数的装饰器", "类装饰器"],
        "resources": ["Real Python", "Python官方文档"],
    }, {"type": "learning_session"})

    # 获取知识图谱摘要
    summary = ms.get_memory("long")
    print("知识图谱摘要:")
    print(f"  知识点总数: {summary['knowledge_points']['total']}")
    print(f"  - 已掌握: {summary['knowledge_points']['mastered']}")
    print(f"  - 学习中: {summary['knowledge_points']['learning']}")
    print(f"  关联关系数: {summary['relationships']}")
    print(f"  代码片段数: {summary['portfolio']['code_snippets_count']}")
    print()

    # 查询已掌握的知识点
    mastered = ms.get_memory("long", query={"type": "knowledge_point", "status": "mastered"})
    print(f"已掌握的知识点: {len(mastered)}")
    for point in mastered:
        print(f"  - {point['data']['name']}")
    print()

    # 按关键词搜索
    python_points = ms.get_memory("long", query={"type": "knowledge_point", "keywords": ["python"]})
    print(f"Python相关知识点: {len(python_points)}")
    for point in python_points:
        print(f"  - {point['data']['name']} ({point['data']['proficiency']}%)")
    print()


def demo_system_status():
    """演示系统状态查询"""
    print("=" * 50)
    print("系统状态查询")
    print("=" * 50)

    ms = MemorySystem()
    status = ms.get_all_memory_types()

    print("感觉记忆状态:")
    print(f"  当前轮数: {status['sensory']['current_rounds']}")
    print(f"  最大轮数: {status['sensory']['max_rounds']}")
    print()

    print("短期记忆状态:")
    print(f"  会话数: {status['short']['session_count']}")
    print(f"  条目数: {status['short']['entry_count']}")
    print()

    print("长期记忆状态:")
    print(f"  知识点总数: {status['long']['knowledge_points']['total']}")
    print(f"  项目数: {status['long']['portfolio']['projects_count']}")
    print()


if __name__ == "__main__":
    demo_sensory_memory()
    demo_short_term_memory()
    demo_long_term_memory()
    demo_system_status()

    print("=" * 50)
    print("演示完成")
    print("=" * 50)
