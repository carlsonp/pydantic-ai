"""Logic related to making requests to an LLM.

The aim here is to make a common interface
"""

from __future__ import annotations as _annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol

from ..messages import LLMMessage, Message

if TYPE_CHECKING:
    from .._utils import ObjectJsonSchema
    from ..agent import KnownModelName


class Model(ABC):
    """Abstract class for a model."""

    @abstractmethod
    def agent_model(
        self, allow_text_result: bool, tools: list[AbstractToolDefinition], result_tool_name: str | None
    ) -> AgentModel:
        """Create an agent model.

        Args:
            allow_text_result: Whether a plain text final response/result is permitted.
            tools: The tools available to the agent.
            result_tool_name: The name of the tool that will be used to generate the final result if there is one.

        Returns:
            An agent model.
        """
        raise NotImplementedError()


class AgentModel(ABC):
    """Model configured for a specific agent."""

    @abstractmethod
    async def request(self, messages: list[Message]) -> LLMMessage:
        """Request a response from the model."""
        raise NotImplementedError()

    # TODO streamed response
    # TODO support for non JSON tool calls


def infer_model(model: Model | KnownModelName) -> Model:
    """Infer the model from the name."""
    if isinstance(model, Model):
        return model
    elif model.startswith('openai:'):
        from .openai import OpenAIModel

        return OpenAIModel(model[7:])  # pyright: ignore[reportArgumentType]
    else:
        raise TypeError(f'Invalid model: {model}')


class AbstractToolDefinition(Protocol):
    """Abstract definition of a function/tool.

    These are generally retrievers, but can also include the response function if one exists.
    """

    name: str
    description: str
    json_schema: ObjectJsonSchema
