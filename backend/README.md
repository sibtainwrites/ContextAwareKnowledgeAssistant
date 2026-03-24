# Context-Aware Knowledge Assistant Backend

A production-ready FastAPI backend for a Retrieval-Augmented Generation (RAG) system that processes documents and provides intelligent Q&A capabilities.

## Prerequisites

- Python 3.10 or higher
- Make (for using the Makefile)

## Setup

1. **Clone the repository and navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   make install
   ```
   This creates a virtual environment and installs all required packages.

3. **Configure environment variables:**
   Copy the `.env.example` file to `.env` and fill in your API keys and configuration:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your actual values.

## Environment Variables

The following environment variables are required (refer to `.env.example` for the exact format):

- `GOOGLE_API_KEY`: Your Google Generative AI API key
- `QDRANT_URL`: URL of your Qdrant vector database instance
- `QDRANT_API_KEY`: API key for Qdrant (if authentication is enabled)

## Running Locally

1. **Start the development server:**
   ```bash
   make run
   ```
   The server will start on `http://localhost:8000` with auto-reload enabled.

2. **Run tests:**
   ```bash
   make test
   ```
   This runs all tests in the `tests/` directory with verbose output.

## API Endpoints

- `POST /upload`: Upload documents (PDF, text) for processing and indexing
- `POST /query`: Submit questions to the knowledge base for RAG-based responses
- `GET /health`: Health check endpoint

For detailed API documentation, visit `http://localhost:8000/docs` when the server is running.