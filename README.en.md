# 🧠 AI Media Library

[Read in Russian](README.md)

**A personal media library and learning platform that turns your media files into interactive study materials using AI.**

The system converts videos, audio, and text articles into structured knowledge, using large language models (LLMs) to extract concepts, create personalized study plans, and generate spaced-repetition flashcards.

## 🚀 Key Features

- **📂 Smart Media Processing**
  - **Multi-format support:** Supports video, audio, and text
  - **Transcription:** Automatic speech recognition via **WhisperX** or **OpenAI**
  - **OCR:** Automatic text recognition using **Tesseract**
  - **Analysis:** Smart summarization and key topic extraction

- **🤖 AI-Powered Learning**
  - **Concept Extraction:** Breaks complex content into small, clear concepts
  - **Personal Study Plans:** Generates quizzes (from easy to hard) based on uploaded materials
  - **Spaced Repetition:** Automatically creates cards for long-term retention (SRS)

- **👩‍🏫 AI Teacher**
  - **Smart Chat:** Chat with an AI teacher that has access to your entire knowledge library
  - **In-depth topic breakdowns:** Ability to ask questions about study plans or individual concepts

- **🧠 SRS System**
  - Built-in flashcard system for long-term retention
  - Smart scheduling of future reviews based on your individual memory level

## 🛠️ Tech Stack

- **Backend:** Python 3.13, Django 5.2
- **Async Tasks:** Redis + Celery
- **AI/ML:**
  - **LLM:** OpenAI, DeepSeek, LangChain
  - **Speech-to-Text:** WhisperX
  - **Vector Store:** ChromaDB
  - **OCR:** Tesseract
- **Database:** PostgreSQL
- **Infrastructure:** Docker, uv (package manager)

## ⚡ Quick Start

### Requirements
- Python 3.13+
- [uv](https://github.com/astral-sh/uv)
- Docker and Docker Compose (for PostgreSQL and Redis)
- **System utilities**:
  - `ffmpeg` (for audio processing)
  - `tesseract` + language packs `eng`, `rus` (for OCR)

### Installation and Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/kraspy/ai_media_library.git
   cd ai_media_library
   ```

2. **Start infrastructure (DB and Redis)**
   Use Docker Compose for a quick start:
   ```bash
   docker compose up -d
   ```

3. **Configure the environment**
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and set your API keys:
   ```env
   # Database (configured by default for docker compose)
   DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/aml_db

   # LLM Keys
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-...
   DEEPSEEK_API_KEY=sk-...
   ```

4. **Install dependencies**
   Use `uv` to sync the environment:
   ```bash
   uv sync
   ```

5. **Apply migrations**
   ```bash
   uv run python manage.py migrate
   ```

6. **Run components**

   **Terminal 1: Django web server**
   ```bash
   uv run python manage.py runserver
   ```

   **Terminal 2: Celery Worker**
   ```bash
   # For Linux/MacOS
   uv run celery -A config worker -l info
   ```

   The application is available at: http://127.0.0.1:8000

## 📚 Project Structure

- `apps/` - Main Django modules
- `docker-build/` - Dockerfile for building
- `config/` - Project settings