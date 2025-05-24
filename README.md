# Agentic RAG

A powerful and flexible Retrieval-Augmented Generation (RAG) system with agent capabilities, built with FastAPI backend and Streamlit UI.

## Features

- 🤖 OpenAI API Integration
- 🛠️ Custom Agent Tools
- 🔍 RAG as a Tool
- 🎯 FastAPI Backend for Retrieval
- 🎨 Streamlit UI
- 📚 Document Processing and Embedding
- 🔄 Streaming Responses
- 🧪 Comprehensive Testing

## Project Structure

```
.
├── app/
│   ├── api/            # FastAPI endpoints
│   ├── core/           # Core functionality
│   ├── models/         # Data models
│   ├── services/       # Business logic
│   ├── tools/          # Agent tools
│   └── ui/             # Streamlit UI
├── data_generation/    # Data processing scripts
├── docs/              # Documentation
├── tests/             # Test suite
└── docker/            # Docker configuration
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agentic-rag.git
cd agentic-rag
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other configurations
```

## Running the Application

1. Start the FastAPI backend:
```bash
uvicorn app.api.main:app --reload
```

2. Start the Streamlit UI:
```bash
streamlit run app/ui/main.py
```

## Development

- Run tests: `pytest`
- Format code: `black .`
- Sort imports: `isort .`
- Type checking: `mypy .`

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
