# Agentic RAG

A powerful and flexible Retrieval-Augmented Generation (RAG) system with agent capabilities, built with FastAPI backend and JS.

## Features

- 🤖 OpenAI API Integration and local vLLM server
- 🛠️ Custom Agent Tools
- 🔍 RAG as a Tool
- 🎯 FastAPI Backend for Retrieval
- 🎨 JS Frontend
- 📚 Document Processing and Embedding
- 🔄 Streaming Responses
- 🧪 Comprehensive Testing


## Setup

1. Clone the repository:
```bash
git clone git@github.com:hongyingyue/ZeroRAG.git
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
