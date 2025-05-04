# Chainlit + LangGraph Memory Example

This project demonstrates how to build a conversational AI application using [Chainlit](https://docs.chainlit.io) for the user interface and [LangGraph](https://python.langchain.com/docs/langgraph) for conversation flow management with in-memory session history.

## Overview

This application showcases:
- Building a chat interface with Chainlit
- Managing conversation flow with LangGraph
- Using in-memory storage for conversation history
- Integration with OpenAI's language models
- Containerization with Docker

## Architecture

The application follows a simple architecture:
1. **User Interface**: Chainlit provides a web-based chat interface
2. **Conversation Management**: LangGraph manages the conversation flow
3. **Language Model**: OpenAI's GPT-4o-mini processes and generates responses
4. **Memory**: InMemorySaver stores conversation history

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Chainlit  │────▶│  LangGraph  │────▶│   OpenAI    │
│  Interface  │◀────│    Flow     │◀────│    Model    │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                          ▼
                    ┌─────────────┐
                    │ InMemorySaver│
                    │   Storage   │
                    └─────────────┘
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
3. Run the application:
   ```bash
   chainlit run src/app.py
   ```

## How It Works

### Key Components

1. **app.py**: The main application file that:
   - Initializes the Chainlit chat interface
   - Sets up the LangGraph conversation flow
   - Configures the OpenAI language model
   - Manages the conversation state with InMemorySaver

2. **LangGraph Flow**:
   - The conversation flow is defined as a simple graph with a single agent node
   - The agent node processes user messages and generates responses using the OpenAI model
   - The conversation state is maintained in memory using InMemorySaver

3. **Chainlit Handlers**:
   - `on_chat_start`: Initializes the model and graph when a new chat session starts
   - `on_message`: Processes user messages through the graph and streams the response

## Customization

### Changing the Language Model

To use a different language model, modify the `init_chat_model` call in the `on_chat_start` function:

```python
model = init_chat_model("openai:your-preferred-model")
```

### Extending the Conversation Flow

To add more nodes to the conversation flow, modify the graph building section in `on_chat_start`:

```python
builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
# Add more nodes here
builder.add_edge(START, "agent")
# Add more edges here
builder.add_edge("agent", END)
```

### Persistent Storage

This example uses in-memory storage with `InMemorySaver`. For persistent storage, you can replace it with other storage options provided by LangGraph.

## License

[MIT License](LICENSE)
