"""
长期记忆模块
用户知识图谱JSON文件存储，永久保存用户掌握的知识点、学习历史、代码作品集
支持知识点关联查询
"""

import os
import json
from datetime import datetime
from typing import Any, List, Dict, Optional, Set

import uuid


class LongTermMemory:
    """
    长期记忆类 - 用户知识图谱存储

    特性：
    - 知识点关联图谱
    - 学习历史永久记录
    - 代码作品集管理
    - 知识点状态跟踪（掌握/学习中/待学习）
    - 关联查询与推荐
    """

    KNOWLEDGE_GRAPH_FILE = "knowledge_graph.json"
    LEARNING_HISTORY_FILE = "learning_history.json"
    PORTFOLIO_FILE = "portfolio.json"

    def __init__(self, storage_dir: str):
        """
        初始化长期记忆

        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

        # 初始化文件（如不存在）
        self._initialize_files()

    def _initialize_files(self):
        """初始化必要的数据文件"""
        files_to_initialize = [
            (self.KNOWLEDGE_GRAPH_FILE, {
                "knowledge_points": {},
                "relationships": []
            }),
            (self.LEARNING_HISTORY_FILE, {
                "sessions": [],
                "milestones": []
            }),
            (self.PORTFOLIO_FILE, {
                "projects": [],
                "code_snippets": []
            }),
        ]

        for filename, default_data in files_to_initialize:
            filepath = os.path.join(self.storage_dir, filename)
            if not os.path.exists(filepath):
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(default_data, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Error initializing {filename}: {e}")

    def update(
        self,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        更新长期记忆

        Args:
            content: 记忆内容（知识点、学习记录或代码作品）
            metadata: 元数据（类型、标签等）

        Returns:
            是否更新成功
        """
        try:
            metadata = metadata or {}
            memory_type = metadata.get("type", "unknown")

            if memory_type == "knowledge_point":
                return self._update_knowledge_point(content, metadata)
            elif memory_type == "relationship":
                return self._update_relationship(content, metadata)
            elif memory_type == "learning_session":
                return self._update_learning_history(content, metadata)
            elif memory_type == "milestone":
                return self._update_milestone(content, metadata)
            elif memory_type == "project":
                return self._update_project(content, metadata)
            elif memory_type == "code_snippet":
                return self._update_code_snippet(content, metadata)
            else:
                # 默认按知识点处理
                return self._update_knowledge_point(content, metadata)

        except Exception as e:
            print(f"Error updating long-term memory: {e}")
            return False

    def get(
        self,
        key: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        获取长期记忆内容

        Args:
            key: 知识点ID或项目ID
            query: 查询条件（类型、标签、状态等）

        Returns:
            查询结果
        """
        try:
            if key:
                # 根据ID查询
                return self._get_by_id(key)
            elif query:
                # 根据查询条件搜索
                return self._search_by_query(query)
            else:
                # 返回所有数据摘要
                return self._get_summary()

        except Exception as e:
            print(f"Error getting long-term memory: {e}")
            return None

    def delete(
        self,
        key: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        删除长期记忆内容

        Args:
            key: 知识点ID或项目ID
            query: 查询条件（用于批量删除）

        Returns:
            是否删除成功
        """
        try:
            if key:
                return self._delete_by_id(key)
            elif query:
                return self._delete_by_query(query)
            else:
                # 清空所有长期记忆（谨慎使用）
                self._clear_all()
                return True

        except Exception as e:
            print(f"Error deleting long-term memory: {e}")
            return False

    def _update_knowledge_point(
        self,
        content: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> bool:
        """更新知识点"""
        filepath = os.path.join(self.storage_dir, self.KNOWLEDGE_GRAPH_FILE)
        data = self._load_file(filepath)

        # 确保有ID
        point_id = metadata.get("id") or content.get("id") or str(uuid.uuid4())
        content["id"] = point_id

        # 合并现有数据
        if point_id in data["knowledge_points"]:
            existing = data["knowledge_points"][point_id]
            existing.update(content)
            existing["updated_at"] = datetime.now().isoformat()
        else:
            data["knowledge_points"][point_id] = {
                **content,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": content.get("status", "learning"),  # learning | mastered | pending
                "proficiency": content.get("proficiency", 0),  # 0-100
            }

        self._save_file(filepath, data)
        return True

    def _update_relationship(
        self,
        content: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> bool:
        """更新知识点关联关系"""
        filepath = os.path.join(self.storage_dir, self.KNOWLEDGE_GRAPH_FILE)
        data = self._load_file(filepath)

        relationship = {
            "id": str(uuid.uuid4()),
            "source_id": content.get("source_id"),
            "target_id": content.get("target_id"),
            "type": content.get("type", "prerequisite"),  # prerequisite | related | extends
            "weight": content.get("weight", 0.5),
            "created_at": datetime.now().isoformat(),
        }

        # 检查是否已存在
        exists = False
        for rel in data["relationships"]:
            if (
                rel["source_id"] == relationship["source_id"]
                and rel["target_id"] == relationship["target_id"]
                and rel["type"] == relationship["type"]
            ):
                exists = True
                break

        if not exists:
            data["relationships"].append(relationship)
            self._save_file(filepath, data)

        return True

    def _update_learning_history(
        self,
        content: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> bool:
        """更新学习历史"""
        filepath = os.path.join(self.storage_dir, self.LEARNING_HISTORY_FILE)
        data = self._load_file(filepath)

        session = {
            "id": str(uuid.uuid4()),
            **content,
            "created_at": content.get("created_at") or datetime.now().isoformat(),
        }

        data["sessions"].append(session)
        self._save_file(filepath, data)
        return True

    def _update_milestone(
        self,
        content: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> bool:
        """更新学习里程碑"""
        filepath = os.path.join(self.storage_dir, self.LEARNING_HISTORY_FILE)
        data = self._load_file(filepath)

        milestone = {
            "id": str(uuid.uuid4()),
            **content,
            "created_at": datetime.now().isoformat(),
        }

        data["milestones"].append(milestone)
        self._save_file(filepath, data)
        return True

    def _update_project(
        self,
        content: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> bool:
        """更新项目作品集"""
        filepath = os.path.join(self.storage_dir, self.PORTFOLIO_FILE)
        data = self._load_file(filepath)

        project_id = metadata.get("id") or content.get("id") or str(uuid.uuid4())
        content["id"] = project_id

        # 查找并更新或添加
        updated = False
        for i, project in enumerate(data["projects"]):
            if project["id"] == project_id:
                data["projects"][i] = {
                    **project,
                    **content,
                    "updated_at": datetime.now().isoformat(),
                }
                updated = True
                break

        if not updated:
            data["projects"].append({
                **content,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            })

        self._save_file(filepath, data)
        return True

    def _update_code_snippet(
        self,
        content: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> bool:
        """更新代码片段"""
        filepath = os.path.join(self.storage_dir, self.PORTFOLIO_FILE)
        data = self._load_file(filepath)

        snippet_id = metadata.get("id") or content.get("id") or str(uuid.uuid4())
        content["id"] = snippet_id

        # 查找并更新或添加
        updated = False
        for i, snippet in enumerate(data["code_snippets"]):
            if snippet["id"] == snippet_id:
                data["code_snippets"][i] = {
                    **snippet,
                    **content,
                    "updated_at": datetime.now().isoformat(),
                }
                updated = True
                break

        if not updated:
            data["code_snippets"].append({
                **content,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            })

        self._save_file(filepath, data)
        return True

    def _get_by_id(self, key: str) -> Optional[Dict[str, Any]]:
        """根据ID获取记忆内容"""
        # 先查知识点
        graph_file = os.path.join(self.storage_dir, self.KNOWLEDGE_GRAPH_FILE)
        graph = self._load_file(graph_file)
        if key in graph["knowledge_points"]:
            return {
                "type": "knowledge_point",
                "data": graph["knowledge_points"][key]
            }

        # 查项目
        portfolio_file = os.path.join(self.storage_dir, self.PORTFOLIO_FILE)
        portfolio = self._load_file(portfolio_file)
        for project in portfolio["projects"]:
            if project["id"] == key:
                return {"type": "project", "data": project}

        # 查代码片段
        for snippet in portfolio["code_snippets"]:
            if snippet["id"] == key:
                return {"type": "code_snippet", "data": snippet}

        # 查学习历史
        history_file = os.path.join(self.storage_dir, self.LEARNING_HISTORY_FILE)
        history = self._load_file(history_file)
        for session in history["sessions"]:
            if session["id"] == key:
                return {"type": "learning_session", "data": session}

        return None

    def _search_by_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据查询条件搜索"""
        search_type = query.get("type", "all")
        results = []

        if search_type in ["all", "knowledge_point"]:
            results.extend(self._search_knowledge_points(query))

        if search_type in ["all", "project"]:
            results.extend(self._search_projects(query))

        if search_type in ["all", "code_snippet"]:
            results.extend(self._search_code_snippets(query))

        if search_type in ["all", "learning_session"]:
            results.extend(self._search_learning_sessions(query))

        if search_type == "related":
            # 查找相关知识点
            point_id = query.get("knowledge_point_id")
            results = self._get_related_knowledge_points(point_id)

        return results

    def _search_knowledge_points(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """搜索知识点"""
        filepath = os.path.join(self.storage_dir, self.KNOWLEDGE_GRAPH_FILE)
        graph = self._load_file(filepath)
        points = list(graph["knowledge_points"].values())

        if "status" in query:
            points = [p for p in points if p.get("status") == query["status"]]

        if "category" in query:
            points = [p for p in points if p.get("category") == query["category"]]

        if "tags" in query:
            query_tags = query["tags"] if isinstance(query["tags"], list) else [query["tags"]]
            points = [
                p for p in points
                if any(tag in p.get("tags", []) for tag in query_tags)
            ]

        if "keywords" in query:
            keywords = query["keywords"] if isinstance(query["keywords"], list) else [query["keywords"]]
            points = [
                p for p in points
                if any(
                    keyword.lower() in str(p).lower()
                    for keyword in keywords
                )
            ]

        return [{"type": "knowledge_point", "data": p} for p in points]

    def _search_projects(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """搜索项目"""
        filepath = os.path.join(self.storage_dir, self.PORTFOLIO_FILE)
        portfolio = self._load_file(filepath)
        projects = portfolio["projects"]

        if "keywords" in query:
            keywords = query["keywords"] if isinstance(query["keywords"], list) else [query["keywords"]]
            projects = [
                p for p in projects
                if any(
                    keyword.lower() in str(p).lower()
                    for keyword in keywords
                )
            ]

        return [{"type": "project", "data": p} for p in projects]

    def _search_code_snippets(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """搜索代码片段"""
        filepath = os.path.join(self.storage_dir, self.PORTFOLIO_FILE)
        portfolio = self._load_file(filepath)
        snippets = portfolio["code_snippets"]

        if "language" in query:
            snippets = [s for s in snippets if s.get("language") == query["language"]]

        if "keywords" in query:
            keywords = query["keywords"] if isinstance(query["keywords"], list) else [query["keywords"]]
            snippets = [
                s for s in snippets
                if any(
                    keyword.lower() in str(s).lower()
                    for keyword in keywords
                )
            ]

        return [{"type": "code_snippet", "data": s} for s in snippets]

    def _search_learning_sessions(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """搜索学习会话"""
        filepath = os.path.join(self.storage_dir, self.LEARNING_HISTORY_FILE)
        history = self._load_file(filepath)
        sessions = history["sessions"]

        if "keywords" in query:
            keywords = query["keywords"] if isinstance(query["keywords"], list) else [query["keywords"]]
            sessions = [
                s for s in sessions
                if any(
                    keyword.lower() in str(s).lower()
                    for keyword in keywords
                )
            ]

        return [{"type": "learning_session", "data": s} for s in sessions]

    def _get_related_knowledge_points(self, point_id: str) -> List[Dict[str, Any]]:
        """获取关联的知识点"""
        filepath = os.path.join(self.storage_dir, self.KNOWLEDGE_GRAPH_FILE)
        graph = self._load_file(filepath)

        related = []
        for rel in graph["relationships"]:
            if rel["source_id"] == point_id:
                target = graph["knowledge_points"].get(rel["target_id"])
                if target:
                    related.append({
                        "type": "knowledge_point",
                        "relationship": rel["type"],
                        "data": target
                    })
            elif rel["target_id"] == point_id:
                source = graph["knowledge_points"].get(rel["source_id"])
                if source:
                    related.append({
                        "type": "knowledge_point",
                        "relationship": f"reverse_{rel['type']}",
                        "data": source
                    })

        return related

    def _get_summary(self) -> Dict[str, Any]:
        """获取所有数据的摘要"""
        graph = self._load_file(
            os.path.join(self.storage_dir, self.KNOWLEDGE_GRAPH_FILE)
        )
        history = self._load_file(
            os.path.join(self.storage_dir, self.LEARNING_HISTORY_FILE)
        )
        portfolio = self._load_file(
            os.path.join(self.storage_dir, self.PORTFOLIO_FILE)
        )

        points = list(graph["knowledge_points"].values())
        mastered_count = sum(1 for p in points if p.get("status") == "mastered")
        learning_count = sum(1 for p in points if p.get("status") == "learning")

        categories = list(set(p.get("category") for p in points if p.get("category")))

        return {
            "knowledge_points": {
                "total": len(points),
                "mastered": mastered_count,
                "learning": learning_count,
                "pending": len(points) - mastered_count - learning_count,
                "categories": categories,
            },
            "relationships": len(graph["relationships"]),
            "learning_history": {
                "sessions_count": len(history["sessions"]),
                "milestones_count": len(history["milestones"]),
            },
            "portfolio": {
                "projects_count": len(portfolio["projects"]),
                "code_snippets_count": len(portfolio["code_snippets"]),
            },
        }

    def _delete_by_id(self, key: str) -> bool:
        """根据ID删除记忆内容"""
        # 删知识点及关联关系
        graph_file = os.path.join(self.storage_dir, self.KNOWLEDGE_GRAPH_FILE)
        graph = self._load_file(graph_file)
        if key in graph["knowledge_points"]:
            del graph["knowledge_points"][key]
            graph["relationships"] = [
                r for r in graph["relationships"]
                if r["source_id"] != key and r["target_id"] != key
            ]
            self._save_file(graph_file, graph)
            return True

        # 删项目
        portfolio_file = os.path.join(self.storage_dir, self.PORTFOLIO_FILE)
        portfolio = self._load_file(portfolio_file)
        original_len = len(portfolio["projects"])
        portfolio["projects"] = [p for p in portfolio["projects"] if p["id"] != key]
        if len(portfolio["projects"]) < original_len:
            self._save_file(portfolio_file, portfolio)
            return True

        # 删代码片段
        original_len = len(portfolio["code_snippets"])
        portfolio["code_snippets"] = [s for s in portfolio["code_snippets"] if s["id"] != key]
        if len(portfolio["code_snippets"]) < original_len:
            self._save_file(portfolio_file, portfolio)
            return True

        # 删学习会话
        history_file = os.path.join(self.storage_dir, self.LEARNING_HISTORY_FILE)
        history = self._load_file(history_file)
        original_len = len(history["sessions"])
        history["sessions"] = [s for s in history["sessions"] if s["id"] != key]
        if len(history["sessions"]) < original_len:
            self._save_file(history_file, history)
            return True

        return False

    def _delete_by_query(self, query: Dict[str, Any]) -> bool:
        """根据查询条件批量删除"""
        # 先搜索，再删除
        items = self._search_by_query(query)
        success = True
        for item in items:
            item_id = item.get("data", {}).get("id")
            if item_id:
                if not self._delete_by_id(item_id):
                    success = False
        return success

    def _clear_all(self) -> None:
        """清空所有长期记忆（重置为初始状态）"""
        self._initialize_files()

    def _load_file(self, filepath: str) -> Dict[str, Any]:
        """加载JSON文件"""
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
        return {}

    def _save_file(self, filepath: str, data: Dict[str, Any]) -> None:
        """保存JSON文件"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        获取长期记忆状态信息

        Returns:
            状态字典
        """
        summary = self._get_summary()
        return {
            "storage_dir": self.storage_dir,
            **summary
        }
