import abc
import time
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    """Abstract Base Agent for the QuantAgent-Alpha Multi-Agent Ecosystem."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.execution_time_ms: float = 0.0

    @abc.abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Executes agent's specific domain logic."""
        pass

    def timed_run(self, *args, **kwargs) -> Any:
        """Executes run() with performance telemetry."""
        start_time = time.perf_counter()
        logger.info(f"[{self.name}] Initiating execution - Role: {self.role}")
        try:
            result = self.run(*args, **kwargs)
            elapsed = (time.perf_counter() - start_time) * 1000.0
            self.execution_time_ms = round(elapsed, 2)
            logger.info(f"[{self.name}] Completed successfully in {self.execution_time_ms} ms")
            return result
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            self.execution_time_ms = round(elapsed, 2)
            logger.error(f"[{self.name}] Execution failed after {self.execution_time_ms} ms: {e}")
            raise
