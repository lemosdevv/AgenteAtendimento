# Emporio da Musica Customer Support Agent

Django application for a Portuguese-language customer support agent for Emporio da Musica.

The source code, identifiers, documentation, and comments are written in English. The agent's customer-facing responses are written in Portuguese.

## Current status

The project currently contains the Django foundation, SQLite configuration, environment configuration, and a health check endpoint. Data ingestion and Gemini integration will be added in separate increments.

## Requirements

- Python 3.12+
- A virtual environment

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

On Windows PowerShell, replace the environment activation command with:

```powershell
.venv\Scripts\Activate.ps1
```

The health check is available at `http://127.0.0.1:8000/health/`.

## Planned increments

1. Import the supplied CSV files and store operational data in SQLite.
2. Add searchable policy documents.
3. Add the Gemini provider behind a service interface.
4. Add the customer support agent and conversation history.
5. Add tests and example conversations.

