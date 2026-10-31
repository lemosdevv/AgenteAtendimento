# Emporio da Musica Customer Support Agent

Django application for a Portuguese-language customer support agent for Emporio da Musica.

The source code, identifiers, documentation, and comments are written in English. The agent's customer-facing responses are written in Portuguese.

## Current status

The project currently contains the Django foundation, SQLite configuration, environment configuration, a health check endpoint, the operational data models, and an idempotent CSV import command. Gemini integration will be added in a separate increment.

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
python manage.py import_data
python manage.py runserver
```

On Windows PowerShell, replace the environment activation command with:

```powershell
.venv\Scripts\Activate.ps1
```

The health check is available at `http://127.0.0.1:8000/health/`.

The import command reads the CSV files from the repository `data/` directory. A different directory can be provided with `python manage.py import_data --data-dir <path>`.

## Planned increments

1. Add searchable policy documents.
2. Add the Gemini provider behind a service interface.
3. Add the customer support agent and conversation history.
4. Add tests and example conversations.

