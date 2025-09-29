import logging
import os
from typing import Optional


class AgentLogger:
    """Simple logging framework for AgentCorp with configurable verbosity"""

    def __init__(self, name: str = "AgentCorp", level: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self._setup_logger(level)

    def _setup_logger(self, level: Optional[str]):
        """Setup the logger with appropriate level and format"""
        if level is None:
            # Check environment variable for verbose mode
            verbose = os.getenv('AGENTCORP_VERBOSE', 'false').lower() in ('true', '1', 'yes')
            level = 'DEBUG' if verbose else 'INFO'

        numeric_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(numeric_level)

        # Remove any existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(numeric_level)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(message, *args, **kwargs)

    def log_tool_call(self, tool_name: str, args: dict, result: Optional[str] = None):
        """Log tool call with arguments and optional result"""
        if result is not None:
            self.debug(f"Tool call: {tool_name}({args}) -> {result}")
        else:
            self.debug(f"Tool call: {tool_name}({args})")

    def log_task_action(self, action: str, task_id: str, description: str, **kwargs):
        """Log task-related actions"""
        extra_info = ""
        if kwargs:
            extra_info = f" - {kwargs}"
        self.debug(f"Task {action}: [{task_id}] {description}{extra_info}")


# Global logger instance
logger = AgentLogger()


def get_logger(name: str = "AgentCorp") -> AgentLogger:
    """Get a logger instance"""
    return AgentLogger(name)


def set_verbose_logging(enabled: bool = True):
    """Enable or disable verbose (debug) logging"""
    level = 'DEBUG' if enabled else 'INFO'
    logger._setup_logger(level)