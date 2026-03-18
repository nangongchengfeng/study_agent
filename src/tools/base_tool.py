"""
工具基类
定义所有工具的通用接口和功能
"""

import logging
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    工具基类
    """

    def __init__(self, name: Optional[str] = None):
        """
        初始化工具

        Args:
            name: 工具名称
        """
        self.name = name or self.__class__.__name__
        logger.info(f"初始化工具: {self.name}")

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        执行工具的核心方法

        Args:
            **kwargs: 工具执行所需的参数

        Returns:
            执行结果
        """
        pass

    def validate_input(self, required_fields: list, **kwargs) -> bool:
        """
        验证输入参数

        Args:
            required_fields: 必需字段列表
            **kwargs: 输入参数

        Returns:
            验证结果
        """
        for field in required_fields:
            if field not in kwargs or kwargs[field] is None:
                logger.warning(f"工具 {self.name} 缺少必需参数: {field}")
                return False
        return True

    def log_execution(self, input_data: Dict[str, Any], output_data: Dict[str, Any]):
        """
        记录执行过程日志

        Args:
            input_data: 输入数据
            output_data: 输出数据
        """
        logger.debug(f"工具 [{self.name}] 输入: {input_data}")
        logger.debug(f"工具 [{self.name}] 输出: {output_data}")

    def handle_error(self, error: Exception, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        错误处理

        Args:
            error: 异常对象
            input_data: 输入数据

        Returns:
            错误结果
        """
        logger.error(f"工具 {self.name} 执行失败: {str(error)}")

        return {
            "success": False,
            "error": str(error),
            "tool": self.name,
            "input": input_data,
        }

    def format_output(self, data: Any) -> Dict[str, Any]:
        """
        格式化输出结果

        Args:
            data: 原始结果数据

        Returns:
            格式化后的结果
        """
        return {
            "success": True,
            "tool": self.name,
            "result": data,
        }
