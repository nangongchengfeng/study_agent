"""
文档检索工具组件
内置常用Python编程知识，支持检索权威编程概念、语法说明
保证教学内容准确性
"""

import re
from typing import Any, Dict, List, Optional, Tuple


class ProgrammingConcept:
    """编程概念定义"""

    def __init__(self, name: str, category: str, description: str,
                 syntax: Optional[str] = None, examples: Optional[List[str]] = None,
                 related: Optional[List[str]] = None, notes: Optional[str] = None):
        self.name = name
        self.category = category
        self.description = description
        self.syntax = syntax
        self.examples = examples or []
        self.related = related or []
        self.notes = notes


class DocumentIndex:
    """文档索引，用于快速检索"""

    def __init__(self):
        self.concepts: Dict[str, ProgrammingConcept] = {}
        self.category_index: Dict[str, List[str]] = {}
        self.keyword_index: Dict[str, List[str]] = {}

    def add_concept(self, concept: ProgrammingConcept):
        """添加概念到索引"""
        self.concepts[concept.name.lower()] = concept

        # 分类索引
        if concept.category not in self.category_index:
            self.category_index[concept.category] = []
        self.category_index[concept.category].append(concept.name)

        # 关键词索引
        keywords = self._extract_keywords(concept)
        for keyword in keywords:
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = []
            if concept.name not in self.keyword_index[keyword]:
                self.keyword_index[keyword].append(concept.name)

    def _extract_keywords(self, concept: ProgrammingConcept) -> List[str]:
        """提取关键词"""
        text = f"{concept.name} {concept.description}"
        words = re.findall(r'\b\w+\b', text.lower())
        return list(set(words))

    def search(self, query: str, category: Optional[str] = None,
               limit: int = 10) -> List[ProgrammingConcept]:
        """搜索概念"""
        query = query.lower()
        results: List[Tuple[ProgrammingConcept, int]] = []

        # 确定搜索范围
        if category and category in self.category_index:
            concept_names = self.category_index[category]
        else:
            concept_names = list(self.concepts.keys())

        # 精确匹配
        if query in self.concepts:
            results.append((self.concepts[query], 100))

        # 关键词匹配
        for name in concept_names:
            if name.lower() == query:
                continue
            concept = self.concepts.get(name.lower())
            if not concept:
                continue

            score = 0
            # 名称包含查询
            if query in name.lower():
                score += 50
            # 描述包含查询
            if query in concept.description.lower():
                score += 30
            # 关键词匹配
            query_words = query.split()
            for word in query_words:
                if word in concept.name.lower():
                    score += 20
                if word in concept.description.lower():
                    score += 10

            if score > 0:
                results.append((concept, score))

        # 排序并返回
        results.sort(key=lambda x: x[1], reverse=True)
        return [concept for concept, score in results[:limit]]

    def get_by_name(self, name: str) -> Optional[ProgrammingConcept]:
        """按名称获取概念"""
        return self.concepts.get(name.lower())

    def get_categories(self) -> List[str]:
        """获取所有分类"""
        return sorted(list(self.category_index.keys()))

    def get_by_category(self, category: str) -> List[ProgrammingConcept]:
        """按分类获取概念"""
        names = self.category_index.get(category, [])
        return [self.concepts[name.lower()] for name in names if name.lower() in self.concepts]


# 初始化文档索引
def _init_document_index() -> DocumentIndex:
    """初始化文档索引，加载内置编程知识"""
    index = DocumentIndex()

    # 基础语法概念
    concepts = [
        ProgrammingConcept(
            name="变量",
            category="基础语法",
            description="变量是存储数据的容器，在Python中不需要声明类型。",
            syntax="变量名 = 值",
            examples=[
                "x = 10",
                "name = \"张三\"",
                "is_student = True"
            ],
            related=["数据类型", "命名规范"],
            notes="Python是动态类型语言，变量类型可以随时改变。"
        ),
        ProgrammingConcept(
            name="数据类型",
            category="基础语法",
            description="Python支持多种数据类型，包括数字、字符串、列表、元组、字典等。",
            examples=[
                "整数: age = 25",
                "浮点数: price = 19.99",
                "字符串: message = \"Hello\"",
                "布尔值: is_valid = True"
            ],
            related=["变量", "类型转换"],
            notes="使用type()函数可以查看变量类型。"
        ),
        ProgrammingConcept(
            name="if语句",
            category="流程控制",
            description="条件语句，根据条件执行不同的代码块。",
            syntax="""if 条件:
    代码块
elif 条件:
    代码块
else:
    代码块""",
            examples=[
                """if age >= 18:
    print("成年")
else:
    print("未成年")"""
            ],
            related=["for循环", "while循环"],
            notes="注意缩进，Python用缩进来表示代码块。"
        ),
        ProgrammingConcept(
            name="for循环",
            category="流程控制",
            description="用于遍历可迭代对象（如列表、字符串等）。",
            syntax="""for 变量 in 可迭代对象:
    代码块""",
            examples=[
                """for i in range(5):
    print(i)""",
                """for name in names:
    print(name)"""
            ],
            related=["while循环", "if语句", "range"],
            notes="range(n)生成0到n-1的整数序列。"
        ),
        ProgrammingConcept(
            name="while循环",
            category="流程控制",
            description="当条件满足时重复执行代码块。",
            syntax="""while 条件:
    代码块""",
            examples=[
                """count = 0
while count < 10:
    print(count)
    count += 1"""
            ],
            related=["for循环", "if语句", "break", "continue"],
            notes="要确保循环最终会结束，避免无限循环。"
        ),
        ProgrammingConcept(
            name="函数",
            category="函数",
            description="封装可重用代码的块，接受输入并返回输出。",
            syntax="""def 函数名(参数):
    代码块
    return 返回值""",
            examples=[
                """def add(a, b):
    return a + b""",
                """def greet(name):
    print(f\"你好, {name}!\")"""
            ],
            related=["参数", "返回值", "作用域"],
            notes="函数定义后需要调用才能执行。"
        ),
        ProgrammingConcept(
            name="列表",
            category="数据结构",
            description="有序的可变序列，可以存储不同类型的元素。",
            syntax="列表名 = [元素1, 元素2, ...]",
            examples=[
                "numbers = [1, 2, 3, 4, 5]",
                "names = [\"张三\", \"李四\", \"王五\"]",
                "mixed = [1, \"two\", 3.0]"
            ],
            related=["元组", "字典", "列表方法"],
            notes="列表索引从0开始，负数索引从末尾开始计数。"
        ),
        ProgrammingConcept(
            name="字典",
            category="数据结构",
            description="键值对集合，用于存储映射关系。",
            syntax="字典名 = {键1: 值1, 键2: 值2, ...}",
            examples=[
                "student = {\"name\": \"张三\", \"age\": 20}",
                "scores = {\"math\": 90, \"english\": 85}"
            ],
            related=["列表", "元组", "集合"],
            notes="字典的键必须是不可变类型（如字符串、数字、元组）。"
        ),
        ProgrammingConcept(
            name="元组",
            category="数据结构",
            description="有序的不可变序列，类似于列表但不能修改。",
            syntax="元组名 = (元素1, 元素2, ...)",
            examples=[
                "point = (3, 4)",
                "colors = (\"red\", \"green\", \"blue\")"
            ],
            related=["列表", "字典"],
            notes="元组比列表更节省内存，访问速度更快。"
        ),
        ProgrammingConcept(
            name="类",
            category="面向对象",
            description="定义对象的属性和方法的模板。",
            syntax="""class 类名:
    def __init__(self, 参数):
        self.属性 = 参数

    def 方法名(self, 参数):
        代码块""",
            examples=[
                """class Person:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f\"你好, 我是{self.name}\")"""
            ],
            related=["对象", "继承", "方法"],
            notes="__init__是构造方法，用于初始化对象属性。"
        ),
        ProgrammingConcept(
            name="异常处理",
            category="错误处理",
            description="捕获和处理程序运行时的错误。",
            syntax="""try:
    可能出错的代码
except 异常类型:
    处理异常
finally:
    无论是否出错都执行""",
            examples=[
                """try:
    result = 10 / 0
except ZeroDivisionError:
    print("除数不能为零")"""
            ],
            related=["错误类型", "raise"],
            notes="使用try-except可以让程序在出错时继续运行。"
        ),
        ProgrammingConcept(
            name="模块导入",
            category="模块",
            description="从其他Python文件中导入功能。",
            syntax="""import 模块名
from 模块名 import 函数/类
from 模块名 import *""",
            examples=[
                "import math",
                "from datetime import datetime",
                "import pandas as pd"
            ],
            related=["模块", "包"],
            notes="避免使用from ... import *，会污染命名空间。"
        ),
        ProgrammingConcept(
            name="列表推导式",
            category="高级特性",
            description="简洁地创建列表的方式。",
            syntax="[表达式 for 变量 in 可迭代对象 if 条件]",
            examples=[
                "squares = [x*x for x in range(10)]",
                "evens = [x for x in numbers if x % 2 == 0]"
            ],
            related=["列表", "for循环"],
            notes="列表推导式比普通for循环更简洁高效。"
        ),
        ProgrammingConcept(
            name="lambda函数",
            category="高级特性",
            description="匿名函数，用于简单的操作。",
            syntax="lambda 参数: 表达式",
            examples=[
                "add = lambda x, y: x + y",
                "sorted_list = sorted(items, key=lambda x: x['price'])"
            ],
            related=["函数", "map", "filter"],
            notes="lambda函数只能包含一个表达式。"
        ),
        ProgrammingConcept(
            name="装饰器",
            category="高级特性",
            description="在不修改原函数的情况下扩展函数功能。",
            syntax="""@装饰器名
def 函数名():
    代码块""",
            examples=[
                """@staticmethod
def my_method():
    pass""",
                """@timer
def slow_function():
    time.sleep(1)"""
            ],
            related=["函数", "闭包"],
            notes="装饰器本质是接受函数并返回函数的函数。"
        ),
        ProgrammingConcept(
            name="生成器",
            category="高级特性",
            description="按需生成值的迭代器，节省内存。",
            syntax="""def 生成器名():
    yield 值""",
            examples=[
                """def count(n):
    for i in range(n):
        yield i""",
                "gen = (x*x for x in range(10))"
            ],
            related=["迭代器", "yield", "列表"],
            notes="生成器用next()获取下一个值，或用for循环遍历。"
        ),
        ProgrammingConcept(
            name="命名规范",
            category="最佳实践",
            description="Python代码的命名约定（PEP 8）。",
            examples=[
                "函数/变量: 使用小写加下划线: my_function",
                "类名: 使用大驼峰: MyClass",
                "常量: 全大写加下划线: MAX_SIZE",
                "私有变量: 前加单下划线: _internal"
            ],
            related=["代码风格", "PEP 8"],
            notes="遵循PEP 8规范可以提高代码可读性。"
        ),
        ProgrammingConcept(
            name="文件读写",
            category="输入输出",
            description="读取和写入文件的操作。",
            syntax="""with open("文件名", "模式") as f:
    内容 = f.read()
    f.write("内容")""",
            examples=[
                """with open("data.txt", "r") as f:
    content = f.read()""",
                """with open("output.txt", "w") as f:
    f.write("Hello World!")"""
            ],
            related=["with语句", "路径处理"],
            notes="使用with语句可以自动关闭文件。"
        ),
        ProgrammingConcept(
            name="类型提示",
            category="高级特性",
            description="为函数和变量添加类型注解。",
            syntax="""def 函数名(参数: 类型) -> 返回类型:
    变量: 类型 = 值""",
            examples=[
                """def add(a: int, b: int) -> int:
    return a + b""",
                "name: str = \"张三\""
            ],
            related=["函数", "数据类型"],
            notes="类型提示不影响运行，但能提高代码可读性。"
        ),
        ProgrammingConcept(
            name="作用域",
            category="基础语法",
            description="变量的有效范围，分为局部、全局、内置。",
            examples=[
                """x = 10  # 全局变量

def func():
    x = 20  # 局部变量
    print(x)

func()  # 输出20
print(x)  # 输出10"""
            ],
            related=["变量", "global", "nonlocal"],
            notes="函数内部可以读取全局变量，但修改需要global声明。"
        ),
    ]

    for concept in concepts:
        index.add_concept(concept)

    return index


# 全局文档索引
_document_index: Optional[DocumentIndex] = None


def get_document_index() -> DocumentIndex:
    """获取文档索引（单例）"""
    global _document_index
    if _document_index is None:
        _document_index = _init_document_index()
    return _document_index


def search_documents(query: str, category: Optional[str] = None,
                     limit: int = 10) -> List[Dict[str, Any]]:
    """
    搜索文档

    Args:
        query: 搜索关键词
        category: 分类（可选）
        limit: 返回结果数量限制

    Returns:
        搜索结果列表
    """
    index = get_document_index()
    results = index.search(query, category, limit)
    return [_concept_to_dict(concept) for concept in results]


def get_concept(name: str) -> Optional[Dict[str, Any]]:
    """
    按名称获取概念

    Args:
        name: 概念名称

    Returns:
        概念信息字典
    """
    index = get_document_index()
    concept = index.get_by_name(name)
    return _concept_to_dict(concept) if concept else None


def get_categories() -> List[str]:
    """
    获取所有分类

    Returns:
        分类列表
    """
    index = get_document_index()
    return index.get_categories()


def get_concepts_by_category(category: str) -> List[Dict[str, Any]]:
    """
    按分类获取概念

    Args:
        category: 分类名称

    Returns:
        概念列表
    """
    index = get_document_index()
    concepts = index.get_by_category(category)
    return [_concept_to_dict(concept) for concept in concepts]


def _concept_to_dict(concept: ProgrammingConcept) -> Dict[str, Any]:
    """将概念对象转换为字典"""
    return {
        "name": concept.name,
        "category": concept.category,
        "description": concept.description,
        "syntax": concept.syntax,
        "examples": concept.examples,
        "related": concept.related,
        "notes": concept.notes
    }


def format_document_result(result: Dict[str, Any]) -> str:
    """
    格式化文档检索结果

    Args:
        result: 文档结果字典

    Returns:
        格式化的字符串
    """
    lines = []
    lines.append(f"## {result['name']}")
    lines.append("")
    lines.append(f"**分类:** {result['category']}")
    lines.append("")
    lines.append(result['description'])
    lines.append("")

    if result.get('syntax'):
        lines.append("### 语法")
        lines.append("```python")
        lines.append(result['syntax'])
        lines.append("```")
        lines.append("")

    if result.get('examples'):
        lines.append("### 示例")
        for example in result['examples']:
            lines.append("```python")
            lines.append(example)
            lines.append("```")
            lines.append("")

    if result.get('notes'):
        lines.append("### 注意")
        lines.append(result['notes'])
        lines.append("")

    if result.get('related'):
        lines.append("**相关概念:** " + ", ".join(result['related']))

    return "\n".join(lines)


if __name__ == "__main__":
    # 测试示例
    print("=== 文档检索测试 ===")
    print("")

    print("1. 搜索 '函数':")
    results = search_documents("函数", limit=3)
    for result in results:
        print(f"- {result['name']}: {result['description'][:50]}...")
    print("")

    print("2. 获取 'for循环' 详细信息:")
    concept = get_concept("for循环")
    if concept:
        print(format_document_result(concept))
    print("")

    print("3. 获取所有分类:")
    categories = get_categories()
    print(", ".join(categories))