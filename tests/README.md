# Pytest Test Suite

This suite provides deterministic automated tests for the AI IT Operations Assistant.

## Run

From the project root:

```bash
pip install pytest
pytest
```

## Scope

The suite contains nine test functions mapped to the nine manual scenarios completed for the capstone:

- TC-001 Knowledge Search
- TC-002 Ticket Lookup
- TC-003 Successful Ticket Creation
- TC-004 Missing Required Information
- TC-005 Invalid Employee ID
- TC-006 Duplicate Ticket Prevention
- TC-007 Unsupported Knowledge Request
- TC-008 Multi-turn State / Memory
- TC-009 Fresh State After Reset

The tests use temporary SQLite/JSON data, so the project's submission database is not modified.

TC-008 and TC-009 use a deterministic fake LLM to exercise the LangGraph workflow without consuming OpenAI API credits. TC-009 validates a fresh graph state; the actual Streamlit button interaction remains a UI/manual test.
