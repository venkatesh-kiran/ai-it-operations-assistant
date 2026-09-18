import sqlite3

from langchain_core.messages import AIMessage, HumanMessage

from agent.graph import build_graph


class FakeLLM:
    """Deterministic fake model for workflow tests; no OpenAI API call is made."""

    def __init__(self, responses):
        self.responses = iter(responses)

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        return next(self.responses)


def test_tc008_multi_turn_state(test_environment):
    """
    TC-008: Multi-turn workflow retains prior context and prevents a duplicate.
    The fake LLM makes the workflow deterministic; the real create_ticket tool
    performs the database validation and duplicate check.
    """
    llm = FakeLLM(
        [
            AIMessage(
                content=(
                    "Please provide your Employee ID and a description "
                    "of the VPN issue."
                )
            ),
            AIMessage(
                content="Please provide the VPN issue description."
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "create_ticket",
                        "args": {
                            "employee_id": "EMP1024",
                            "category": "VPN",
                            "description": "I cannot connect to the corporate VPN.",
                        },
                        "id": "call_create_ticket",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(
                content=(
                    "You already have an active VPN support ticket "
                    "INC-1001."
                )
            ),
        ]
    )

    graph = build_graph(llm)

    state = {"messages": [HumanMessage(
        content="I have a VPN issue. Please raise a support ticket."
    )]}
    result1 = graph.invoke(state)

    assert "Employee ID" in result1["messages"][-1].content

    result2 = graph.invoke({
        "messages": result1["messages"] + [
            HumanMessage(content="My employee ID is EMP1024.")
        ]
    })

    assert "VPN issue description" in result2["messages"][-1].content

    result3 = graph.invoke({
        "messages": result2["messages"] + [
            HumanMessage(content="I cannot connect to the corporate VPN.")
        ]
    })

    assert "INC-1001" in result3["messages"][-1].content

    connection = sqlite3.connect(test_environment["db"])
    count = connection.execute(
        """
        SELECT COUNT(*)
        FROM tickets
        WHERE employee_id = 'EMP1024'
          AND LOWER(category) = 'vpn'
        """
    ).fetchone()[0]
    connection.close()

    assert count == 1


def test_tc009_fresh_state_after_reset(test_environment):
    """
    TC-009: A new graph invocation starts with only the new request.
    This is the automated equivalent of the Streamlit Clear/Reset behavior.
    """
    llm = FakeLLM(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "lookup_ticket",
                        "args": {"employee_id": "EMP1024"},
                        "id": "call_lookup_ticket",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(
                content=(
                    "EMP1024 has INC-1001 in progress and "
                    "INC-1004 open."
                )
            ),
        ]
    )

    graph = build_graph(llm)

    result = graph.invoke({
        "messages": [
            HumanMessage(
                content=(
                    "What is the status of my ticket? "
                    "My employee ID is EMP1024."
                )
            )
        ]
    })

    assert "INC-1001" in result["messages"][-1].content
    assert "INC-1004" in result["messages"][-1].content

    human_messages = [
        message
        for message in result["messages"]
        if getattr(message, "type", None) == "human"
    ]

    assert len(human_messages) == 1
    assert "What is the status" in human_messages[0].content
