
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage

from agent.state import AgentState

from tools.knowledge_search import search_knowledge
from tools.ticket_lookup import lookup_ticket
from tools.ticket_creation import create_ticket


SYSTEM_PROMPT = """
You are an AI IT Support Assistant for a fictional organization.

Your job is to help employees with IT support requests.

Available tools:

1. search_knowledge
Use this for IT procedures, troubleshooting instructions, or information
available in the local IT knowledge base.

2. lookup_ticket
Use this when the user asks about an existing support ticket.
An employee ID is required.

3. create_ticket
Use this only when the user explicitly asks to create or raise a support
ticket.

Ticket creation rules:
- Employee ID is required.
- Issue category is required.
- Issue description is required.
- Priority is optional and defaults to Medium.
- If required information is missing, ask the user for it.
- Do not invent missing information.
- Do not create a ticket until required information is available.
- The create_ticket tool performs employee validation and duplicate checking.
- Treat the tool result as the source of truth.

Knowledge search rules:
- If search_knowledge returns an article with id "NO_RESULT",
  respond only that the requested information was not found in the
  available IT knowledge base.
- Do not provide alternative sources, recommendations, guesses,
  or additional actions when the result is "NO_RESULT".

General rules:
- Use tools when needed.
- Do not invent ticket IDs, employee information, ticket status, or other
  factual information.
- Do not add promises, timelines, or actions that are not supported by
  tool results.
- When information is not available, clearly say that it was not found.
- Keep responses professional and concise.
"""


def build_graph(llm):
    """Build and compile the IT support LangGraph workflow."""

    tools = [
        search_knowledge,
        lookup_ticket,
        create_ticket,
    ]

    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: AgentState):
        """Let the LLM decide whether and which tool should be used."""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT)
        ] + state["messages"]

        response = llm_with_tools.invoke(messages)

        return {
            "messages": [response]
        }

    tool_node = ToolNode(tools)

    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")

    graph.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            "__end__": END,
        },
    )

    graph.add_edge("tools", "agent")

    return graph.compile()
