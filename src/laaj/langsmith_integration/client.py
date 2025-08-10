"""
LangSmith tracing client for LLM as Judge study.
Simplified version focused on observability and tracing.
"""

import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LangSmithClient:
    """
    Simplified LangSmith client focused on tracing and observability.
    """
    
    def __init__(
        self,
        project_name: Optional[str] = None,
        api_key: Optional[str] = None,
        enable_tracing: bool = True
    ):
        """
        Initialize LangSmith client for tracing.
        
        Args:
            project_name: Project name (defaults to LANGSMITH_PROJECT_NAME env var)
            api_key: LangSmith API key (optional - will use env var if available)
            enable_tracing: Whether to enable tracing (default: True)
        """
        self.project_name = project_name or os.getenv("LANGSMITH_PROJECT_NAME", "llm-as-judge-study")
        self.api_key = api_key or os.getenv("LANGSMITH_API_KEY")
        self.enable_tracing = enable_tracing and bool(self.api_key)
        
        # Configure environment variables for LangChain tracing
        self._configure_tracing()
        
        logger.info(f"LangSmith tracing {'enabled' if self.enable_tracing else 'disabled'} for project: {self.project_name}")
    
    def _configure_tracing(self):
        """Configure environment variables for LangChain tracing."""
        if self.enable_tracing and self.api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = self.project_name
            os.environ["LANGSMITH_API_KEY"] = self.api_key
            os.environ["LANGCHAIN_API_KEY"] = self.api_key
            
            endpoint = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
            os.environ["LANGCHAIN_ENDPOINT"] = endpoint
            
            logger.info("LangChain tracing configured")
        else:
            # Disable tracing if no API key
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
            logger.info("LangChain tracing disabled (no API key)")
    
    def is_tracing_enabled(self) -> bool:
        """Check if tracing is currently enabled."""
        return self.enable_tracing
    
    def get_project_name(self) -> str:
        """Get the current project name."""
        return self.project_name
    
    def get_tracing_info(self) -> Dict[str, Any]:
        """
        Get tracing configuration information.
        
        Returns:
            Dictionary with tracing configuration
        """
        return {
            "project_name": self.project_name,
            "tracing_enabled": self.enable_tracing,
            "has_api_key": bool(self.api_key),
            "langchain_tracing": os.getenv("LANGCHAIN_TRACING_V2", "false"),
            "langchain_project": os.getenv("LANGCHAIN_PROJECT", ""),
            "langchain_endpoint": os.getenv("LANGCHAIN_ENDPOINT", "")
        }