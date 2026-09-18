
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State carried through the IT support workflow."""

    messages: Annotated[list, add_messages]
