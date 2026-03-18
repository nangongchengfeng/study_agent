"""
短期记忆模块
基于本地JSON文件存储，支持内容提炼、增量更新、按需加载
存储最近7天的学习会话数据（代码片段、错误记录、学习进度）
自动清理过期数据
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Any, List, Dict, Optional

import uuid


class ShortTermMemory:
    """
    短期记忆类 - 本地JSON文件存储

    特性：
    - 会话级数据存储
    - 自动清理7天前的数据
    - 内容提炼和增量更新
    - 支持按需加载
    """

    EXPIRY_DAYS = 7  # 数据过期天数
    SESSION_FILE = "session_{id}.json"  # 会话文件命名格式

    def __init__(self, storage_dir: str):
        """
        初始化短期记忆

        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self._current_session = None

    def update(
        self,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        更新短期记忆

        Args:
            content: 记忆内容（支持多种格式）
            metadata: 元数据（会话ID、类型、标签等）

        Returns:
            是否更新成功
        """
        try:
            session_id = metadata.get("session_id") if metadata else None

            # 如果没有提供会话ID，创建新会话
            if not session_id:
                session_id = str(uuid.uuid4())
                if metadata:
                    metadata["session_id"] = session_id
                else:
                    metadata = {"session_id": session_id}

            # 加载或创建会话文件
            session_file = self._get_session_file(session_id)
            session_data = self._load_session(session_id) or {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "entries": [],
                "metadata": metadata or {},
            }

            # 添加新条目
            entry = {
                "id": str(uuid.uuid4()),
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {},
            }

            session_data["entries"].append(entry)
            session_data["updated_at"] = datetime.now().isoformat()

            # 保存会话数据
            self._save_session(session_file, session_data)

            self._current_session = session_id

            return True
        except Exception as e:
            print(f"Error updating short-term memory: {e}")
            return False

    def get(
        self,
        key: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        获取短期记忆内容

        Args:
            key: 会话ID或条目ID
            query: 查询条件（类型、时间范围、标签等）

        Returns:
            查询结果
        """
        try:
            if key:
                # 如果提供了会话ID，直接加载该会话
                if key.startswith("session_"):
                    session_id = key.replace("session_", "")
                    return self._load_session(session_id)
                elif len(key) == 36:  # UUID格式
                    return self._load_session(key)
                else:
                    # 尝试查找条目ID
                    return self._find_entry_by_id(key)
            elif query:
                # 根据查询条件搜索会话
                return self._search_sessions(query)
            else:
                # 获取所有有效会话
                return self._get_all_valid_sessions()

        except Exception as e:
            print(f"Error getting short-term memory: {e}")
            return None

    def delete(
        self,
        key: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        删除短期记忆内容

        Args:
            key: 会话ID或条目ID
            query: 查询条件（用于批量删除）

        Returns:
            是否删除成功
        """
        try:
            if key:
                if len(key) == 36:  # UUID格式
                    # 尝试删除整个会话
                    session_file = self._get_session_file(key)
                    if os.path.exists(session_file):
                        os.remove(session_file)
                        return True
                    else:
                        # 尝试删除条目
                        return self._delete_entry_by_id(key)
                else:
                    return False
            elif query:
                # 根据查询条件删除会话
                sessions = self._search_sessions(query)
                for session in sessions:
                    session_file = self._get_session_file(
                        session["session_id"]
                    )
                    if os.path.exists(session_file):
                        os.remove(session_file)
                return True
            else:
                # 清空所有短期记忆
                self._clear_all_sessions()
                return True

        except Exception as e:
            print(f"Error deleting short-term memory: {e}")
            return False

    def clear_expired(self) -> int:
        """
        清理过期的短期记忆数据（保留最近7天）

        Returns:
            清理的记录数量
        """
        try:
            count = 0
            expiry_date = datetime.now() - timedelta(days=self.EXPIRY_DAYS)

            # 遍历所有会话文件
            for filename in os.listdir(self.storage_dir):
                if filename.endswith(".json") and filename.startswith(
                    "session_"
                ):
                    filepath = os.path.join(self.storage_dir, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            session_data = json.load(f)
                        created_at = datetime.fromisoformat(
                            session_data["created_at"]
                        )
                        if created_at < expiry_date:
                            os.remove(filepath)
                            count += 1
                    except Exception as e:
                        print(f"Error checking {filename}: {e}")
                        continue

            return count
        except Exception as e:
            print(f"Error clearing expired memory: {e}")
            return 0

    def _load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        加载会话数据

        Args:
            session_id: 会话ID

        Returns:
            会话数据字典，或None（不存在时）
        """
        session_file = self._get_session_file(session_id)
        if os.path.exists(session_file):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading session {session_id}: {e}")
        return None

    def _save_session(self, session_file: str, data: Dict[str, Any]) -> None:
        """
        保存会话数据

        Args:
            session_file: 文件路径
            data: 会话数据
        """
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving session to {session_file}: {e}")

    def _get_session_file(self, session_id: str) -> str:
        """
        获取会话文件路径

        Args:
            session_id: 会话ID

        Returns:
            文件路径
        """
        return os.path.join(
            self.storage_dir,
            self.SESSION_FILE.format(id=session_id)
        )

    def _search_sessions(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据查询条件搜索会话

        Args:
            query: 查询条件字典

        Returns:
            匹配的会话列表
        """
        results = []
        for session in self._get_all_valid_sessions():
            if self._match_query(session, query):
                results.append(session)
        return results

    def _match_query(self, session: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """
        判断会话是否匹配查询条件

        Args:
            session: 会话数据
            query: 查询条件

        Returns:
            是否匹配
        """
        if "type" in query:
            session_type = session.get("metadata", {}).get("type")
            if session_type != query["type"]:
                return False

        if "tags" in query:
            session_tags = session.get("metadata", {}).get("tags", [])
            if not any(tag in query["tags"] for tag in session_tags):
                return False

        if "time_range" in query:
            time_range = query["time_range"]
            start_time = datetime.fromisoformat(time_range["start"])
            end_time = datetime.fromisoformat(time_range["end"])
            session_created = datetime.fromisoformat(session["created_at"])

            if session_created < start_time or session_created > end_time:
                return False

        if "keywords" in query:
            keywords = query["keywords"]
            if not any(keyword in str(session) for keyword in keywords):
                return False

        return True

    def _get_all_valid_sessions(self) -> List[Dict[str, Any]]:
        """
        获取所有有效的会话（未过期的）

        Returns:
            有效会话列表
        """
        sessions = []
        expiry_date = datetime.now() - timedelta(days=self.EXPIRY_DAYS)

        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json") and filename.startswith(
                "session_"
            ):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        session = json.load(f)
                    created_at = datetime.fromisoformat(session["created_at"])
                    if created_at > expiry_date:
                        sessions.append(session)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    continue

        return sorted(
            sessions,
            key=lambda x: datetime.fromisoformat(x["updated_at"]),
            reverse=True
        )

    def _find_entry_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        根据条目ID查找记忆条目

        Args:
            entry_id: 条目ID

        Returns:
            记忆条目，或None
        """
        for session in self._get_all_valid_sessions():
            for entry in session["entries"]:
                if entry["id"] == entry_id:
                    return entry
        return None

    def _delete_entry_by_id(self, entry_id: str) -> bool:
        """
        根据条目ID删除记忆条目

        Args:
            entry_id: 条目ID

        Returns:
            是否删除成功
        """
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json") and filename.startswith(
                "session_"
            ):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        session = json.load(f)

                    # 查找并删除条目
                    session["entries"] = [
                        e for e in session["entries"] if e["id"] != entry_id
                    ]

                    # 如果会话为空，删除整个文件
                    if not session["entries"]:
                        os.remove(filepath)
                    else:
                        session["updated_at"] = datetime.now().isoformat()
                        self._save_session(filepath, session)

                    return True
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    continue

        return False

    def _clear_all_sessions(self) -> None:
        """清除所有会话文件"""
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json") and filename.startswith(
                "session_"
            ):
                try:
                    os.remove(os.path.join(self.storage_dir, filename))
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        获取短期记忆状态信息

        Returns:
            状态字典
        """
        valid_sessions = self._get_all_valid_sessions()
        total_entries = sum(
            len(session.get("entries", [])) for session in valid_sessions
        )

        return {
            "storage_dir": self.storage_dir,
            "session_count": len(valid_sessions),
            "entry_count": total_entries,
            "expiry_days": self.EXPIRY_DAYS,
            "current_session": self._current_session,
            "earliest_session": min(
                (datetime.fromisoformat(s["created_at"])
                 for s in valid_sessions),
                default=None
            ).isoformat() if valid_sessions else None,
            "latest_session": max(
                (datetime.fromisoformat(s["updated_at"])
                 for s in valid_sessions),
                default=None
            ).isoformat() if valid_sessions else None,
        }
