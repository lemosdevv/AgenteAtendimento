# Emporio da Musica Customer Support Agent

Django application for a Portuguese-language customer support agent for Emporio da Musica.

The source code, identifiers, documentation, and comments are written in English. The agent's customer-facing responses are written in Portuguese.

## Current status

This repository is for developers who want to run and review a Django customer support agent for Emporio da Musica. It includes SQLite-backed operational data, searchable store policies, Gemini integration, conversation history, and an HTTP endpoint.

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

On Windows PowerShell, replace the activation and copy commands with:

```powershell
.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

Before starting the server, open `.env` and replace `REPLACE_WITH_A_RANDOM_SECRET` with a random secret value. The application does not start without `DJANGO_SECRET_KEY`; test runs generate a temporary key automatically.

The health check is available at `http://127.0.0.1:8000/health/`.

The import command reads the CSV files from the repository `data/` directory. To use a different directory, run `python manage.py import_data --data-dir DATA_DIR` and replace `DATA_DIR` with the directory path.

The policy command extracts searchable content from `data/políticas_da_loja.pdf` and stores it in SQLite. To use a different file, run `python manage.py ingest_policies --file POLICY_FILE` and replace `POLICY_FILE` with the PDF path.

## Gemini configuration

The project uses the official Google GenAI Python SDK. Copy `.env.example` to `.env` and set `GEMINI_API_KEY` before making model requests. The default model is `gemini-3.5-flash-lite`, and it can be changed with `GEMINI_MODEL`.

For production, set `DJANGO_DEBUG=False` and provide a strong `DJANGO_SECRET_KEY`. Production mode enables HTTPS redirects, HSTS, secure cookies, and content-type sniffing protection. Gemini requests use a 30-second timeout and one retry attempt by default; change `GEMINI_TIMEOUT_MS` or `GEMINI_RETRY_ATTEMPTS` when needed.

## Customer support agent

The `CustomerSupportAgent` coordinates deterministic searches and delegates response generation to a text provider:

```python
from support.services.customer_support_agent import CustomerSupportAgent
from support.services.llm import GeminiTextGenerator

agent = CustomerSupportAgent(GeminiTextGenerator())
answer = agent.respond("Quais violões estão disponíveis até R$ 1.000?")
```

The agent checks the operational database for product and order questions, searches the policy chunks when relevant, and instructs the model to answer in Brazilian Portuguese without inventing unavailable information.

Before building the context, the local `IntentRouter` classifies each message as a product search, order lookup, policy question, general information request, or out-of-scope request. The agent then calls Gemini once to generate the response. Database searches remain deterministic after the intent is selected, which reduces latency and API cost.

The HTTP endpoint is available at `POST /api/chat/`:

```json
{
  "message": "Qual é o status do meu pedido?",
  "customer_id": 3
}
```

## Use the CLI

To start an interactive chat on Windows, double-click `start_chat.bat` or run:

```powershell
.\start_chat.bat
```

To associate the chat with a customer and enable order lookup by customer, pass the customer ID:

```powershell
.\start_chat.bat --customer-id 3
```

Type `exit` or `sair` to close the chat. The conversation and its messages are stored in SQLite.

The `customer_id` field is optional. The first request returns a `conversation_id` and a private `conversation_token`. Send both identifiers in later requests to preserve the previous messages:

```json
{
  "message": "E qual é o prazo estimado?",
  "conversation_id": "CONVERSATION_ID",
  "conversation_token": "CONVERSATION_TOKEN"
}
```

## Tests and examples

Run the test suite with:

```bash
python manage.py test
```

Conversation examples are available in `examples/conversations.md`.

## Before production

- Add authenticated user identity instead of relying only on bearer conversation tokens.
- Add rate limiting and request monitoring to the public chat endpoint.
- Configure a production database and secret management service.

