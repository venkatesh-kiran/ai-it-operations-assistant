# AI IT Operations Assistant Using Agentic AI

## 1. Project Title

**AI IT Operations Assistant Using Agentic AI**

---

## 2. Problem Statement

IT support teams handle common employee requests such as:

- Finding IT troubleshooting instructions
- Checking the status of existing support tickets
- Raising new support tickets

This project demonstrates an Agentic AI assistant that understands an employee's request, selects an appropriate tool, executes the tool, processes the result, and generates a user-friendly response.

The application is designed for a fictional organization and uses local data sources.

---

## 3. Solution Overview

The application uses an LLM-based agent orchestrated with LangGraph.

The agent has access to three tools:

### 3.1 Knowledge Search

Searches the local IT knowledge base.

**Data source:**

`data/knowledge_base.json`

### 3.2 Ticket Lookup

Searches existing support tickets for an employee.

**Data source:**

`data/tickets.db`

### 3.3 Ticket Creation

Creates a new IT support ticket.

Before creating a ticket, the application:

1. Validates the employee ID.
2. Validates required ticket information.
3. Checks for an existing active ticket for the same employee and category.
4. Creates the ticket only when the request passes validation.
5. Generates a new ticket ID.
6. Stores the ticket in SQLite.

The application also maintains conversation messages as LangGraph state so information can be retained across multiple user interactions.

---

## 4. Architecture

The application follows this workflow:

```text
                         User
                           |
                           v
                     Streamlit UI
                           |
                           v
                    LangGraph Agent
                           |
                           v
                  Conditional Routing
                           |
           +---------------+---------------+
           |               |               |
           v               v               v
    Knowledge Search   Ticket Lookup   Ticket Creation
           |               |               |
           v               v               v
    knowledge_base.json   tickets.db   Employee Validation
                                           |
                                           v
                                    Duplicate Check
                                           |
                                           v
                                        tickets.db
           |               |               |
           +---------------+---------------+
                           |
                           v
                       Tool Result
                           |
                           v
                         Agent
                           |
                           v
                     Final Response
```

### LangGraph Workflow Concepts

The implementation demonstrates:

- **State** – conversation messages carried through the workflow.
- **Nodes** – agent node and tool execution node.
- **Edges** – connections between workflow steps.
- **Conditional Routing** – routes the workflow to the tool execution node when the LLM requests a tool call.
- **Tool Execution** – executes the selected Python tool.
- **Response Generation** – the LLM uses the tool result to generate the final response.

---

## 5. Technology Stack

- Python
- OpenAI API
- LangChain
- LangGraph
- Streamlit
- SQLite
- JSON
- python-dotenv
- pytest

---

## 6. Project Structure

```text
ai-it-operations-assistant/
│
├── .env.example
├── .gitignore
├── README.md
├── app.py
├── requirements.txt
├── pytest.ini
│
├── agent/
│   ├── graph.py
│   └── state.py
│
├── data/
│   ├── employees.json
│   ├── knowledge_base.json
│   └── tickets.db
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── README.md
│   ├── test_agent_workflow.py
│   ├── test_knowledge_search.py
│   └── test_ticket_tools.py
│
├── tools/
│   ├── knowledge_search.py
│   ├── ticket_creation.py
│   └── ticket_lookup.py
│
└── utils/
    └── logging_config.py
```

### File Responsibilities

**`app.py`**

Application entry point and Streamlit user interface.

**`agent/state.py`**

Defines the LangGraph state used to maintain conversation messages.

**`agent/graph.py`**

Builds the LangGraph workflow, including the agent node, conditional routing, and tool execution.

**`tools/knowledge_search.py`**

Searches the local IT knowledge base.

**`tools/ticket_lookup.py`**

Retrieves existing support tickets for an employee from SQLite.

**`tools/ticket_creation.py`**

Validates and creates support tickets in SQLite, including duplicate-ticket prevention.

**`utils/logging_config.py`**

Configures application logging.

**`data/employees.json`**

Contains fictional employee information used for employee validation.

**`data/knowledge_base.json`**

Contains fictional IT knowledge articles.

**`data/tickets.db`**

Local SQLite database containing sample support tickets.

**`tests/`**

Contains the executable pytest regression suite covering the nine core scenarios.

**`pytest.ini`**

Configures pytest to discover tests from the `tests/` directory.

---

## 7. Prerequisites

The application requires:

- Python 3.10 or later
- An OpenAI API key
- Internet access for OpenAI API requests

No GPU or high-end laptop is required.

---

## 8. Setup Instructions

### Step 1: Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ai-it-operations-assistant
```

### Step 2: Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure the OpenAI API key

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

Do not commit `.env` to GitHub.

---

## 9. Environment Variables

The application requires the following environment variable:

```text
OPENAI_API_KEY
```

Example:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

The repository contains `.env.example` as a configuration template.

The actual `.env` file containing the API key must not be committed to source control.

---

## 10. Running the Application

From the project root, run:

```bash
streamlit run app.py
```

The Streamlit application will open in a browser.

---

## 11. Automated Testing

The project includes an executable pytest regression suite covering the nine core scenarios used during functional validation.

### Install pytest

`pytest` is included in `requirements.txt`. If dependencies have already been installed with:

```bash
pip install -r requirements.txt
```

no separate installation is required.

### Run the automated tests

From the project root:

```bash
pytest
```

### Verified result

The completed regression run produced:

```text
.........                                                                [100%]
9 passed in 0.25s
```

### Automated test coverage

| Test ID | Scenario | Result |
|---|---|---|
| TC-001 | Knowledge Search | PASS |
| TC-002 | Ticket Lookup | PASS |
| TC-003 | Successful Ticket Creation | PASS |
| TC-004 | Missing Required Information | PASS |
| TC-005 | Invalid Employee ID | PASS |
| TC-006 | Duplicate Ticket Prevention | PASS |
| TC-007 | Unsupported Knowledge Request | PASS |
| TC-008 | Multi-turn State / Memory | PASS |
| TC-009 | Fresh State / Reset Equivalent | PASS |

### Test isolation

The tests use temporary JSON and SQLite data so the project's final sample database is not modified during test execution.

The LangGraph workflow tests use a deterministic fake LLM, so the automated suite does not require an OpenAI API call or consume API credits.

The actual Streamlit **Clear / Reset Conversation** button remains covered by the manual UI regression test; TC-009 verifies the corresponding fresh graph-state behavior programmatically.

---

## 12. Sample Inputs and Expected Outputs

### 12.1 Knowledge Search

**Input**

```text
How do I reset my VPN password?
```

**Expected behavior**

The agent selects the `search_knowledge` tool.

The tool retrieves the relevant article from the local knowledge base.

The LLM generates a user-friendly response using the retrieved information.

---

### 12.2 Ticket Lookup

**Input**

```text
What is the status of my ticket?
My employee ID is EMP1024.
```

**Expected behavior**

The agent selects the `lookup_ticket` tool.

The tool searches the local SQLite database.

For the supplied sample data, `EMP1024` has:

```text
INC-1001 → VPN → In Progress
INC-1004 → Email → Open
```

The response is generated from the actual ticket data.

---

### 12.3 Ticket Creation

**Input**

```text
My VPN is not working. Please create a support ticket.
My employee ID is EMP1002.
I cannot connect to the corporate VPN.
```

**Expected behavior**

The agent selects the `create_ticket` tool.

The application:

```text
Validate employee
       |
       v
Check active duplicate
       |
       v
Create ticket
       |
       v
Generate ticket ID
       |
       v
Return ticket details
```

---

### 12.4 Missing Information

**Input**

```text
My laptop is not working. Please create a support ticket.
```

**Expected behavior**

The agent asks for the required missing information rather than attempting to create an incomplete ticket.

---

### 12.5 Invalid Employee

**Input**

```text
Create a VPN ticket for employee EMP9999.
The VPN is not working.
```

**Expected behavior**

The application reports that the employee could not be verified and does not create a ticket.

---

### 12.6 Duplicate Ticket

**Input**

```text
Create another VPN ticket for EMP1024.
My VPN is still not working.
```

**Expected behavior**

The application detects the existing active VPN ticket and does not create a duplicate ticket.

---

### 12.7 Unsupported Information

**Input**

```text
What is the company's holiday policy?
```

**Expected behavior**

The application states that the requested information was not found in the available IT knowledge base.

The system does not invent a policy or an external source.

---

## 13. Key Design Decisions

### 13.1 Local Data

JSON and SQLite are used for local data storage so that no real enterprise system integration is required.

### 13.2 Separate Tools

Each tool has a specific responsibility:

```text
Knowledge Search
      |
      +--> retrieves knowledge

Ticket Lookup
      |
      +--> retrieves ticket data

Ticket Creation
      |
      +--> validates and creates ticket data
```

The LLM selects an appropriate tool, while the Python tool performs the actual operation.

### 13.3 LangGraph

LangGraph is used to orchestrate the Agentic AI workflow and demonstrate state, nodes, edges, conditional routing, tool execution, and response generation.

### 13.4 Deterministic Validation

Employee validation and duplicate-ticket checking are performed in Python rather than relying only on the LLM.

This helps prevent invalid or duplicate ticket creation.

### 13.5 Conversation State

Conversation messages are maintained as LangGraph state to support multi-turn interactions.

### 13.6 Automated Testing

The pytest suite provides repeatable validation of the core tool and workflow behavior while keeping test data isolated from the submission database.

---

## 14. Error Handling

The application handles common situations including:

- Missing API configuration
- Missing required ticket information
- Invalid employee ID
- Duplicate active ticket
- Database errors during ticket creation
- Knowledge requests for information that is not available

User-facing errors are kept simple.

Application errors are recorded using the logging configuration.

---

## 15. Limitations

- The IT knowledge base contains fictional sample information.
- Employee and ticket information are stored locally.
- No real enterprise IT service-management system is integrated.
- Knowledge search uses simple keyword matching.
- The project does not implement embeddings, vector search, or an advanced RAG pipeline because they are outside the scope of this Project 3 implementation.
- LLM-based functionality requires an OpenAI API key.
- Sample data is intended for demonstration and evaluation purposes.

---

## 16. Demonstrated Agentic AI Flow

```text
User Request
     |
     v
LLM / Agent
     |
     v
Tool Selection
     |
     +-----------------------+
     |           |           |
     v           v           v
Knowledge    Ticket       Ticket
Search       Lookup       Creation
     |           |           |
     +-----------+-----------+
                 |
                 v
             Tool Result
                 |
                 v
                LLM
                 |
                 v
           Final Response
```

---

## 17. Certification Project Scope

This project demonstrates the required Project 3 capabilities:

- Python
- LangGraph
- Agentic AI
- Tool Calling
- Function Calling
- State Management
- Conditional Routing
- Local Data / Database Integration
- Prompt Engineering
- Streamlit
- Error Handling
- Modular Architecture
- Automated Testing with pytest

---

## 18. Security

API keys and secrets must never be committed to GitHub.

The `.env` file is excluded through `.gitignore`.

Use `.env.example` as the configuration template.

---

## 19. Sample Data

The repository includes sample data so that the evaluator can run the application without creating data from scratch.

Sample data includes:

- Fictional employee records
- IT knowledge articles
- Existing IT support tickets

---

## 20. Demonstration

The demonstration should show the major functional requirements of the application, including:

1. Knowledge search
2. Existing ticket lookup
3. Ticket creation
4. Missing information handling
5. Duplicate-ticket prevention
6. Unsupported-information handling
7. Conversation reset
8. Automated pytest regression

For the automated test demonstration:

```bash
pytest
```

Expected verified result:

```text
9 passed in 0.25s
```

---

## 21. Author

GenAI Development Program – Final Evaluation Project
