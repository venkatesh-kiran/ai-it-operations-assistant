
import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from agent.graph import build_graph
from utils.logging_config import get_logger


load_dotenv()

logger = get_logger(__name__)


st.set_page_config(
    page_title="AI IT Operations Assistant",
    page_icon="🛠️",
    layout="centered",
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error(
        "OPENAI_API_KEY is not configured. "
        "Please configure it before starting the application."
    )
    st.stop()


# ---------------------------------------------------------
# Initialize LangGraph
# ---------------------------------------------------------

@st.cache_resource
def create_graph():
    """Create and cache the LangGraph workflow."""

    logger.info("Initializing LangGraph workflow.")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=api_key,
    )

    return build_graph(llm)


graph = create_graph()


# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "graph_messages" not in st.session_state:
    st.session_state.graph_messages = []


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("🛠️ AI IT Operations Assistant")

st.write(
    "Ask IT support questions, check existing tickets, "
    "or create a new support ticket."
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header("Conversation")

    if st.button("Clear / Reset Conversation"):

        logger.info("Conversation reset.")

        st.session_state.messages = []
        st.session_state.graph_messages = []

        st.rerun()

    st.divider()

    st.caption("Available tools")

    st.write("🔎 Knowledge Search")
    st.write("🎫 Ticket Lookup")
    st.write("📝 Ticket Creation")


# ---------------------------------------------------------
# Display conversation history
# ---------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message.get("tool_calls"):

            with st.expander("Tool activity"):

                for tool_call in message["tool_calls"]:

                    st.write(
                        f"**Tool:** {tool_call['name']}"
                    )

                    st.write(
                        f"**Arguments:** {tool_call['args']}"
                    )


# ---------------------------------------------------------
# Handle user input
# ---------------------------------------------------------

user_input = st.chat_input(
    "Ask an IT support question..."
)


if user_input:

    logger.info("Received user request.")

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    try:

        # Add the current user message to LangGraph state.
        st.session_state.graph_messages.append(
            HumanMessage(content=user_input)
        )

        with st.chat_message("assistant"):

            with st.spinner(
                "Processing your request..."
            ):

                result = graph.invoke(
                    {
                        "messages":
                            st.session_state.graph_messages
                    }
                )

            # Save the complete updated LangGraph state.
            st.session_state.graph_messages = (
                result["messages"]
            )

            # -------------------------------------------------
            # Extract tool calls for CURRENT TURN ONLY
            # -------------------------------------------------

            tool_calls = []

            for message in reversed(result["messages"]):

                # Stop when we reach the current user message.
                if getattr(message, "type", None) == "human":
                    break

                if (
                    hasattr(message, "tool_calls")
                    and message.tool_calls
                ):
                    tool_calls.extend(
                        message.tool_calls
                    )

            # Reverse so tools appear in execution order.
            tool_calls.reverse()

            # -------------------------------------------------
            # Final assistant response
            # -------------------------------------------------

            final_message = result["messages"][-1]

            answer = (
                final_message.content
                or "The assistant did not return a response."
            )

            st.markdown(answer)

            # -------------------------------------------------
            # Tool activity for CURRENT TURN ONLY
            # -------------------------------------------------

            if tool_calls:

                with st.expander("Tool activity"):

                    for tool_call in tool_calls:

                        st.write(
                            f"**Tool:** {tool_call['name']}"
                        )

                        st.write(
                            f"**Arguments:** {tool_call['args']}"
                        )

            # Store the assistant response for Streamlit history.
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "tool_calls": tool_calls,
                }
            )

    except Exception:

        logger.exception(
            "Error while processing request."
        )

        st.error(
            "Sorry, I encountered an error while "
            "processing your request."
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": (
                    "Sorry, I encountered an error while "
                    "processing your request."
                ),
            }
        )
