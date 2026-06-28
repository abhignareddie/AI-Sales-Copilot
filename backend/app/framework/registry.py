"""Registry module for registering agents, tools, prompts, and plugins."""

from __future__ import annotations

from typing import Any, Dict, Type, Callable

from app.framework.interfaces import BaseAgent, BaseTool
from app.core.logging import logger


class AgentRegistry:
    """Registry to record and resolve agent implementations dynamically."""

    _agents: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register(
        cls, name: str
    ) -> Callable[[Type[BaseAgent]], Type[BaseAgent]]:
        """Decorator to register an Agent class."""

        def decorator(klass: Type[BaseAgent]) -> Type[BaseAgent]:
            cls._agents[name] = klass
            logger.info(
                f"[Framework] Registered Agent: '{name}' -> {klass.__name__}"
            )
            return klass

        return decorator

    @classmethod
    def get(cls, name: str) -> Type[BaseAgent]:
        """Retrieve an agent class by name."""
        if name not in cls._agents:
            raise KeyError(
                f"Agent '{name}' is not registered in the AgentRegistry"
            )

        return cls._agents[name]

    @classmethod
    def list_registered(cls) -> list[str]:
        """List names of all registered agents."""
        return list(cls._agents.keys())


class ToolRegistry:
    """Registry to manage and resolve reusable tools."""

    _tools: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def register(
        cls, name: str
    ) -> Callable[[Type[BaseTool]], Type[BaseTool]]:
        """Decorator to register a Tool class."""

        def decorator(klass: Type[BaseTool]) -> Type[BaseTool]:
            cls._tools[name] = klass
            logger.info(
                f"[Framework] Registered Tool: '{name}' -> {klass.__name__}"
            )
            return klass

        return decorator

    @classmethod
    def get(cls, name: str) -> Type[BaseTool]:
        """Retrieve a tool class by name."""
        if name not in cls._tools:
            raise KeyError(
                f"Tool '{name}' is not registered in the ToolRegistry"
            )

        return cls._tools[name]

    @classmethod
    def list_registered(cls) -> list[str]:
        """List names of all registered tools."""
        return list(cls._tools.keys())


class PromptRegistry:
    """
    Registry to store and template prompts,
    separating prompts from execution code.
    """

    _prompts: Dict[str, str] = {}

    @classmethod
    def register(cls, name: str, prompt_text: str) -> None:
        """Register a prompt template."""
        cls._prompts[name] = prompt_text
        logger.info(
            f"[Framework] Registered Prompt template: '{name}'"
        )

    @classmethod
    def get(cls, prompt_name: str, **kwargs: Any) -> str:
        """Retrieve a prompt and optionally format it."""
        if prompt_name not in cls._prompts:
            raise KeyError(
                f"Prompt template '{prompt_name}' not found"
            )

        template = cls._prompts[prompt_name]

        if kwargs:
            try:
                return template.format(**kwargs)
            except KeyError as e:
                logger.warning(
                    f"Missing variable for prompt template "
                    f"{prompt_name}: {e}"
                )
                return template

        return template