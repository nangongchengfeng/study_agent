"""
记忆系统测试用例
验证感觉记忆、短期记忆、长期记忆功能
"""

import os
import sys
import shutil
import tempfile
from datetime import datetime, timedelta
from typing import Any

import pytest

# 确保能导入src目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.memory import MemorySystem
from src.memory.sensory_memory import SensoryMemory
from src.memory.short_term_memory import ShortTermMemory
from src.memory.long_term_memory import LongTermMemory


class TestSensoryMemory:
    """感觉记忆测试用例"""

    def test_initialization(self):
        """测试感觉记忆初始化"""
        sm = SensoryMemory()
        assert len(sm.get()) == 0

    def test_update_memory(self):
        """测试更新记忆"""
        sm = SensoryMemory()
        result = sm.update("Hello, world!", {"role": "user"})
        assert result is True
        assert len(sm.get()) == 1

    def test_max_rounds_limit(self):
        """测试最多保留10轮对话"""
        sm = SensoryMemory()
        for i in range(15):
            sm.update(f"Message {i}", {"role": "user"})

        contexts = sm.get()
        assert len(contexts) == 10
        # 检查第一个消息应该是 Message 5 而不是 Message 0
        assert contexts[0]["content"] == "Message 5"

    def test_filter_by_role(self):
        """测试按角色过滤"""
        sm = SensoryMemory()
        sm.update("User message", {"role": "user"})
        sm.update("Assistant message", {"role": "assistant"})
        sm.update("Another user message", {"role": "user"})

        user_messages = sm.get(query={"role": "user"})
        assert len(user_messages) == 2

        assistant_messages = sm.get(query={"role": "assistant"})
        assert len(assistant_messages) == 1

    def test_filter_by_keywords(self):
        """测试按关键词过滤"""
        sm = SensoryMemory()
        sm.update("Python tutorial", {"role": "user"})
        sm.update("JavaScript basics", {"role": "user"})
        sm.update("Python advanced", {"role": "user"})

        python_messages = sm.get(query={"keywords": ["Python"]})
        assert len(python_messages) == 2

    def test_delete_memory(self):
        """测试删除记忆"""
        sm = SensoryMemory()
        sm.update("Message 1", {"role": "user"})
        sm.update("Message 2", {"role": "user"})

        assert len(sm.get()) == 2
        sm.delete()
        assert len(sm.get()) == 0

    def test_to_prompt(self):
        """测试转换为prompt格式"""
        sm = SensoryMemory()
        sm.update("Hello", {"role": "user"})
        sm.update("Hi there!", {"role": "assistant"})

        simple_prompt = sm.to_prompt(format_style="simple")
        assert "user: Hello" in simple_prompt
        assert "assistant: Hi there!" in simple_prompt

    def test_get_status(self):
        """测试获取状态信息"""
        sm = SensoryMemory()
        sm.update("Test", {"role": "user", "type": "conversation"})

        status = sm.get_status()
        assert status["current_rounds"] == 1
        assert status["max_rounds"] == 10


class TestShortTermMemory:
    """短期记忆测试用例"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        # 清理
        shutil.rmtree(temp_path, ignore_errors=True)

    def test_initialization(self, temp_dir):
        """测试初始化"""
        stm = ShortTermMemory(temp_dir)
        status = stm.get_status()
        assert status["session_count"] == 0

    def test_update_and_get_memory(self, temp_dir):
        """测试更新和获取记忆"""
        stm = ShortTermMemory(temp_dir)

        # 更新记忆
        result = stm.update(
            "Learning Python today",
            {"type": "learning", "tags": ["python", "tutorial"]}
        )
        assert result is True

        # 获取所有会话
        sessions = stm.get()
        assert len(sessions) == 1
        assert "session_id" in sessions[0]

    def test_get_by_session_id(self, temp_dir):
        """测试按会话ID获取"""
        stm = ShortTermMemory(temp_dir)

        stm.update(
            "Test content",
            {"type": "test"}
        )

        sessions = stm.get()
        session_id = sessions[0]["session_id"]

        session = stm.get(key=session_id)
        assert session is not None
        assert session["session_id"] == session_id

    def test_search_by_tags(self, temp_dir):
        """测试按标签搜索"""
        stm = ShortTermMemory(temp_dir)

        stm.update("Python content", {"type": "learning", "tags": ["python"]})
        stm.update("JavaScript content", {"type": "learning", "tags": ["javascript"]})
        stm.update("More Python", {"type": "learning", "tags": ["python", "advanced"]})

        python_sessions = stm.get(query={"tags": ["python"]})
        assert len(python_sessions) == 2

    def test_delete_memory(self, temp_dir):
        """测试删除记忆"""
        stm = ShortTermMemory(temp_dir)

        stm.update("Content 1", {"type": "test"})
        sessions = stm.get()
        assert len(sessions) == 1

        session_id = sessions[0]["session_id"]
        result = stm.delete(key=session_id)
        assert result is True

        # 验证已删除
        sessions = stm.get()
        assert len(sessions) == 0

    def test_clear_expired(self, temp_dir):
        """测试清理过期数据"""
        stm = ShortTermMemory(temp_dir)
        stm.EXPIRY_DAYS = 1  # 缩短过期时间方便测试

        # 创建一个过期的会话文件
        session_id = "expired_test"
        session_file = os.path.join(temp_dir, f"session_{session_id}.json")

        import json
        expired_date = (datetime.now() - timedelta(days=2)).isoformat()
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump({
                "session_id": session_id,
                "created_at": expired_date,
                "updated_at": expired_date,
                "entries": []
            }, f)

        # 清理过期数据
        count = stm.clear_expired()
        assert count == 1


class TestLongTermMemory:
    """长期记忆测试用例"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        # 清理
        shutil.rmtree(temp_path, ignore_errors=True)

    def test_initialization(self, temp_dir):
        """测试初始化"""
        ltm = LongTermMemory(temp_dir)

        # 验证文件已创建
        assert os.path.exists(os.path.join(temp_dir, "knowledge_graph.json"))
        assert os.path.exists(os.path.join(temp_dir, "learning_history.json"))
        assert os.path.exists(os.path.join(temp_dir, "portfolio.json"))

        status = ltm.get_status()
        assert status["knowledge_points"]["total"] == 0

    def test_update_and_get_knowledge_point(self, temp_dir):
        """测试更新和获取知识点"""
        ltm = LongTermMemory(temp_dir)

        result = ltm.update(
            {"name": "Python", "category": "programming"},
            {"type": "knowledge_point"}
        )
        assert result is True

        # 获取摘要
        summary = ltm.get()
        assert summary["knowledge_points"]["total"] == 1

        # 按关键词搜索
        points = ltm.get(query={"type": "knowledge_point", "keywords": ["Python"]})
        assert len(points) == 1

    def test_knowledge_point_status(self, temp_dir):
        """测试知识点状态管理"""
        ltm = LongTermMemory(temp_dir)

        ltm.update(
            {"name": "Python", "category": "programming", "status": "mastered"},
            {"type": "knowledge_point"}
        )
        ltm.update(
            {"name": "Rust", "category": "programming", "status": "learning"},
            {"type": "knowledge_point"}
        )

        mastered = ltm.get(query={"type": "knowledge_point", "status": "mastered"})
        learning = ltm.get(query={"type": "knowledge_point", "status": "learning"})

        assert len(mastered) == 1
        assert len(learning) == 1

    def test_update_and_get_relationships(self, temp_dir):
        """测试知识点关联关系"""
        ltm = LongTermMemory(temp_dir)

        # 创建两个知识点
        ltm.update(
            {"name": "Variables", "category": "python"},
            {"type": "knowledge_point", "id": "kp1"}
        )
        ltm.update(
            {"name": "Functions", "category": "python"},
            {"type": "knowledge_point", "id": "kp2"}
        )

        # 创建关联关系
        result = ltm.update(
            {"source_id": "kp1", "target_id": "kp2", "type": "prerequisite"},
            {"type": "relationship"}
        )
        assert result is True

    def test_update_and_get_project(self, temp_dir):
        """测试项目作品集管理"""
        ltm = LongTermMemory(temp_dir)

        result = ltm.update(
            {"name": "Todo App", "description": "A simple todo list"},
            {"type": "project"}
        )
        assert result is True

        summary = ltm.get()
        assert summary["portfolio"]["projects_count"] == 1

    def test_update_and_get_code_snippet(self, temp_dir):
        """测试代码片段管理"""
        ltm = LongTermMemory(temp_dir)

        result = ltm.update(
            {
                "title": "Hello World",
                "language": "python",
                "code": "print('Hello World')"
            },
            {"type": "code_snippet"}
        )
        assert result is True

        snippets = ltm.get(query={"type": "code_snippet", "language": "python"})
        assert len(snippets) == 1

    def test_update_and_get_learning_session(self, temp_dir):
        """测试学习历史记录"""
        ltm = LongTermMemory(temp_dir)

        result = ltm.update(
            {"topic": "Python Basics", "duration": 60},
            {"type": "learning_session"}
        )
        assert result is True

        summary = ltm.get()
        assert summary["learning_history"]["sessions_count"] == 1

    def test_delete_by_id(self, temp_dir):
        """测试按ID删除"""
        ltm = LongTermMemory(temp_dir)

        ltm.update(
            {"name": "Test Point"},
            {"type": "knowledge_point", "id": "test-id"}
        )

        # 验证存在
        point = ltm.get(key="test-id")
        assert point is not None

        # 删除
        result = ltm.delete(key="test-id")
        assert result is True

        # 验证不存在
        point = ltm.get(key="test-id")
        assert point is None


class TestMemorySystem:
    """记忆系统统一接口测试用例"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        # 清理
        shutil.rmtree(temp_path, ignore_errors=True)

    def test_initialization(self, temp_dir):
        """测试记忆系统初始化"""
        ms = MemorySystem(base_dir=temp_dir)
        status = ms.get_all_memory_types()

        assert "sensory" in status
        assert "short" in status
        assert "long" in status

    def test_sensory_memory_via_system(self, temp_dir):
        """测试通过统一接口操作感觉记忆"""
        ms = MemorySystem(base_dir=temp_dir)

        ms.update_memory("sensory", "Hello", {"role": "user"})
        ms.update_memory("sensory", "Hi", {"role": "assistant"})

        memory = ms.get_memory("sensory")
        assert len(memory) == 2

    def test_short_term_memory_via_system(self, temp_dir):
        """测试通过统一接口操作短期记忆"""
        ms = MemorySystem(base_dir=temp_dir)

        ms.update_memory("short", "Learning content", {"type": "learning"})

        memory = ms.get_memory("short")
        assert len(memory) == 1

    def test_long_term_memory_via_system(self, temp_dir):
        """测试通过统一接口操作长期记忆"""
        ms = MemorySystem(base_dir=temp_dir)

        ms.update_memory("long", {
            "name": "Python", "category": "programming"
        }, {"type": "knowledge_point"})

        summary = ms.get_memory("long")
        assert summary["knowledge_points"]["total"] == 1

    def test_delete_memory_via_system(self, temp_dir):
        """测试通过统一接口删除记忆"""
        ms = MemorySystem(base_dir=temp_dir)

        ms.update_memory("sensory", "Hello", {"role": "user"})
        assert len(ms.get_memory("sensory")) == 1

        ms.delete_memory("sensory")
        assert len(ms.get_memory("sensory")) == 0

    def test_clear_expired_via_system(self, temp_dir):
        """测试通过统一接口清理过期数据"""
        ms = MemorySystem(base_dir=temp_dir)

        # 添加一些短期记忆
        ms.update_memory("short", "Test", {"type": "test"})

        # 清理过期数据（即使没有过期的也应正常执行）
        count = ms.clear_expired_memory()
        assert isinstance(count, int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
