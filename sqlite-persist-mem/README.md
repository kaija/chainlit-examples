# Chainlit + LangGraph with SQLite Persistence Example

This project demonstrates how to build a conversational AI application using [Chainlit](https://docs.chainlit.io) for the user interface and [LangGraph](https://python.langchain.com/docs/langgraph) for conversation flow management with SQLite-based persistence for chat history.

## Overview

This application showcases:
- Building a chat interface with Chainlit
- Managing conversation flow with LangGraph
- Using SQLite for persistent conversation history storage
- User authentication with username/password
- Session resumption with message type conversion
- Integration with OpenAI's language models
- Containerization with Docker

## Architecture

The application follows a simple architecture:
1. **User Interface**: Chainlit provides a web-based chat interface
2. **Authentication**: Password-based authentication system
3. **Conversation Management**: LangGraph manages the conversation flow
4. **Language Model**: OpenAI's GPT-4o-mini processes and generates responses
5. **Persistence**: SQLite database stores conversation history and user data

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Chainlit  │────▶│  LangGraph  │────▶│   OpenAI    │
│  Interface  │◀────│    Flow     │◀────│    Model    │
└─────────────┘     └─────────────┘     └─────────────┘
      │                    │
      │                    │
      ▼                    ▼
┌─────────────┐     ┌─────────────┐
│    Auth     │     │   SQLite    │
│   System    │     │  Database   │
└─────────────┘     └─────────────┘
```

## Prerequisites

- Docker and Docker Compose
- OpenAI API key

## Setup

1. Clone this repository
2. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Running the Application

### Using Docker Compose

```bash
docker-compose up --build
```

The application will be available at http://localhost:8000

### Without Docker

1. Make sure you have Python 3.13+ installed
2. Install the dependencies:
   ```bash
   pip install -e .
   ```
3. Initialize the SQLite database:
   ```bash
   python src/init_db.py
   ```
4. Run the application:
   ```bash
   chainlit run src/app.py
   ```

## How It Works

### Key Components

1. **app.py**: The main application file that:
   - Initializes the Chainlit chat interface
   - Sets up the LangGraph conversation flow
   - Configures the OpenAI language model
   - Implements authentication with username/password
   - Manages the conversation state with SQLite persistence
   - Handles chat session resumption with message type conversion

2. **init_db.py**: Initializes the SQLite database:
   - Creates the database file if it doesn't exist
   - Sets up the required tables using the schema in sqlite.sql

3. **LangGraph Flow**:
   - The conversation flow is defined as a simple graph with a single agent node
   - The agent node processes user messages and generates responses using the OpenAI model
   - The conversation state is maintained in the SQLite database

4. **Chainlit Handlers**:
   - `on_chat_start`: Initializes the model, graph, and SQLite data layer when a new chat session starts
   - `on_message`: Processes user messages through the graph and streams the response
   - `on_chat_resume`: Restores the chat state when a user resumes a previous session, converting OpenAI message types to LangChain message objects

### Authentication

The application implements a simple username/password authentication system using Chainlit's `@cl.password_auth_callback` decorator. Two test users are provided:
- Username: `alice`, Password: `alice`
- Username: `bob`, Password: `bob`

```python
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (username, password) == ("alice", "alice"):
        return cl.User(
            identifier="alice", metadata={"role": "admin", "provider": "credentials"}
        )
    elif (username, password) == ("bob", "bob"):
        return cl.User(
            identifier="bob", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None
```

### Message Type Conversion

When resuming a chat session, the application needs to convert OpenAI-style message dictionaries to LangChain message objects. This is handled by the `message_converter` function:

```python
def message_converter(history: list[dict]) -> list:
    """Convert OpenAI style dict to LangChain Message Object"""
    role_map = {
        "user": HumanMessage,
        "assistant": AIMessage,
        "system": SystemMessage,
    }
    messages = []
    for item in history:
        role = item.get("role")
        content = item.get("content", "")
        msg_cls = role_map.get(role)
        if not msg_cls:
            # Fallback to HumanMessage if no match
            msg_cls = HumanMessage
        messages.append(msg_cls(content=content))
    return messages
```

### SQLite Persistence

The application uses SQLite for persistent storage of chat history and user data. The database schema includes tables for:
- Users: Stores user authentication information
- Threads: Stores chat threads
- Steps: Stores individual steps within a thread
- Elements: Stores UI elements associated with threads
- Feedbacks: Stores user feedback on responses

The SQLite data layer is initialized in the `on_chat_start` handler:

```python
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("chat_history", [])

    cl_data._data_layer = SQLAlchemyDataLayer(
        conninfo=f"sqlite+aiosqlite:///./sqlite/chainlit.db",
    )
```

## Customization

### Changing the Language Model

To use a different language model, modify the `init_chat_model` call:

```python
model = init_chat_model("openai:your-preferred-model")
```

### Extending the Conversation Flow

To add more nodes to the conversation flow, modify the graph building section:

```python
builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
# Add more nodes here
builder.add_edge(START, "agent")
# Add more edges here
builder.add_edge("agent", END)
```

### Enhancing Authentication

For a production application, you would want to:
1. Store hashed passwords in the database
2. Implement proper user management
3. Add role-based access control
4. Consider OAuth or other authentication providers

## License

[MIT License](LICENSE)
