"""
Agent模块
包含教学工作流中的各种功能Agent
"""

# 原有Agent
from .understanding_agent import UnderstandingAgent
from .memory_retrieval_agent import MemoryRetrievalAgent
from .explanation_agent import ExplanationAgent
from .example_generation_agent import ExampleGenerationAgent
from .practice_generation_agent import PracticeGenerationAgent
from .validation_agent import ValidationAgent
from .memory_update_agent import MemoryUpdateAgent

# 新增功能Agent
from .base_agent import BaseAgent
from .code_explainer_agent import CodeExplainerAgent
from .learning_path_agent import LearningPathAgent
from .debugging_guide_agent import DebuggingGuideAgent
from .progress_tracker_agent import ProgressTrackerAgent
from .content_validator_agent import ContentValidatorAgent

__all__ = [
    # 原有Agent
    "UnderstandingAgent",
    "MemoryRetrievalAgent",
    "ExplanationAgent",
    "ExampleGenerationAgent",
    "PracticeGenerationAgent",
    "ValidationAgent",
    "MemoryUpdateAgent",
    # 新增功能Agent
    "BaseAgent",
    "CodeExplainerAgent",
    "LearningPathAgent",
    "DebuggingGuideAgent",
    "ProgressTrackerAgent",
    "ContentValidatorAgent",
]
