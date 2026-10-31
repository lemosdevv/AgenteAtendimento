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
python manage.py ingest_policies
python manage.py runserver
```

On Windows PowerShell, replace the environment activation command with:

```powershell
.venv\Scripts\Activate.ps1
```

The health check is available at `http://127.0.0.1:8000/health/`.

The import command reads the CSV files from the repository `data/` directory. A different directory can be provided with `python manage.py import_data --data-dir <path>`.

The policy command extracts searchable content from `data/políticas_da_loja.pdf` and stores it in SQLite. A different file can be provided with `python manage.py ingest_policies --file <path>`.

## Gemini configuration

The project uses the official Google GenAI Python SDK. Copy `.env.example` to `.env` and set `GEMINI_API_KEY` before making model requests. The default model is `gemini-3.8-flash`, and it can be changed with `GEMINI_MODEL`.

## Customer support agent

The `CustomerSupportAgent` coordinates deterministic searches and delegates response generation to a text provider:

```python
from support.services.customer_support_agent import CustomerSupportAgent
from support.services.llm import GeminiTextGenerator

agent = CustomerSupportAgent(GeminiTextGenerator())
answer = agent.respond("Quais violões estão disponíveis até R$ 1.000?")
```

The agent checks the operational database for product and order questions, searches the policy chunks when relevant, and instructs the model to answer in Brazilian Portuguese without inventing unavailable information.

Before building the context, `IntentRouter` classifies each message as a product search, order lookup, policy question, general information request, or out-of-scope request. Gemini is used as the primary classifier, with a local fallback for tests or temporary provider unavailability. Database searches remain deterministic after the intent is selected.

The HTTP endpoint is available at `POST /api/chat/`:

```json
{
  "message": "Qual é o status do meu pedido?",
  "customer_id": 3
}
```

The `customer_id` field is optional. The first request returns a `conversation_id`. Send that identifier in later requests to preserve the previous messages:

```json
{
  "message": "E qual é o prazo estimado?",
  "conversation_id": "returned-conversation-uuid"
}
```

## Planned increments

1. Add conversation history.
2. Add tests and example conversations.

