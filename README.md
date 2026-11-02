# Emporio da Musica customer support agent

This repository contains a Portuguese-language customer support agent for the fictional Emporio da Musica store. It is intended for reviewers and developers who want to run the technical challenge, inspect the design, and evaluate the agent's behavior.

After you complete the setup, you can run Ana in the terminal or call the HTTP API. Ana answers in Brazilian Portuguese, while the source code, identifiers, comments, and technical documentation use English.

## Scope

Ana handles product discovery, catalog filters, active promotions, order lookups, store policies, general store information, and out-of-scope requests. Product, order, and policy facts come from the local dataset and the policy PDF supplied with the challenge.

The project does not implement authentication, payment processing, order changes, shipping-provider integration, or a production deployment. See [Known limitations](#known-limitations) for the next improvements.

## Challenge coverage

The implementation maps the challenge requirements to these components:

| Requirement | Implementation |
| --- | --- |
| Store-aligned persona | Ana's prompt and CLI presentation define a clear, helpful store assistant. |
| Product and availability questions | Deterministic catalog queries against SQLite. |
| Order status questions | Deterministic order queries with conversation context. |
| Policy questions | Text extraction and search over the store policy PDF. |
| Out-of-scope requests | Local intent routing returns a bounded response without calling Gemini. |
| Multi-turn conversations | `Conversation` and `Message` records preserve recent context. |
| Human-readable interaction | Rich terminal interface and Portuguese responses. |

## Architecture

The agent uses a hybrid design: deterministic retrieval supplies factual context, and Gemini turns that context into a natural response.

```text
CLI or HTTP API
      |
      v
CustomerSupportAgent
      |
      +--> IntentRouter
      +--> CatalogSearch ------> SQLite
      +--> OrderLookup --------> SQLite
      +--> PolicySearch -------> SQLite policy chunks
      +--> GeminiTextGenerator -> Gemini API
```

The application never asks the model to invent catalog, order, or policy facts. The model receives the relevant context and a response policy that instructs it to acknowledge missing information instead of guessing.

## Technical decisions

- **Django:** provides the application structure, ORM, management commands, test runner, and HTTP endpoint while keeping the implementation in Python, as required by the challenge.
- **SQLite:** keeps the challenge self-contained and makes the imported CSV and PDF data easy to inspect locally.
- **Official Google GenAI SDK:** integrates Gemini without an additional model gateway.
- **Hybrid retrieval:** local routing and database queries keep operational facts deterministic; Gemini is used for language generation and conversation quality.
- **Rich CLI:** provides readable panels, Markdown responses, a thinking indicator, and a graceful Windows `.bat` entry point.
- **Environment configuration:** secrets, model settings, timeouts, and retry limits come from `.env` variables instead of source code.

## Requirements

- Python 3.12 or later
- A Gemini API key
- Network access to the Gemini API when you send a message

The application uses SQLite, so you do not need to install a separate database server.

## Set up the project

### Windows PowerShell

From the repository root, create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the runtime dependencies and create the environment file:

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and set `DJANGO_SECRET_KEY` to a private random value and `GEMINI_API_KEY` to your Gemini API key. Keep `.env` out of version control.

### macOS or Linux

From the repository root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the runtime dependencies and create the environment file:

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and set `DJANGO_SECRET_KEY` to a private random value and `GEMINI_API_KEY` to your Gemini API key. Keep `.env` out of version control.

## Load the challenge data

Run the following commands after you activate the virtual environment:

```bash
python manage.py migrate
python manage.py import_data
python manage.py ingest_policies
```

`import_data` loads the CSV files from `data/`. `ingest_policies` extracts searchable text from `data/políticas_da_loja.pdf` and stores policy chunks in SQLite. Both commands can be run again when you need to refresh the local database.

To use another source directory or policy file, run:

```bash
python manage.py import_data --data-dir DATA_DIR
python manage.py ingest_policies --file POLICY_FILE
```

Replace `DATA_DIR` with the CSV directory and `POLICY_FILE` with the PDF path.

## Run Ana

### Terminal chat

On Windows, double-click `start_chat.bat` or run:

```powershell
.\start_chat.bat
```

You can associate the conversation with a customer to enable order lookup by customer ID:

```powershell
.\start_chat.bat --customer-id 3
```

You can also start the CLI on any supported operating system:

```bash
python manage.py chat [--customer-id CUSTOMER_ID]
```

Type `sair` or `exit` to close the conversation. The CLI stores the conversation and messages in SQLite. If Gemini is unavailable, Ana shows a generic Portuguese message and the application writes diagnostic details to `logs/application.log`.

### HTTP API

Start Django with:

```bash
python manage.py runserver
```

The health endpoint is available at `http://127.0.0.1:8000/health/`.

Send a new message to `POST http://127.0.0.1:8000/api/chat/` with a JSON body:

```json
{
  "message": "Quais violões estão disponíveis até R$ 1.000?",
  "customer_id": 3
}
```

The first response includes `conversation_id`, `conversation_token`, and `response`. Keep the token private and send both identifiers on later requests:

```json
{
  "message": "E qual é o prazo estimado?",
  "conversation_id": "CONVERSATION_ID",
  "conversation_token": "CONVERSATION_TOKEN"
}
```

The API requires the conversation token for continuation requests. The application uses the customer associated with the conversation instead of trusting a different customer ID supplied later.

## Configure Gemini

The default model is `gemini-3.5-flash-lite`. You can change it in `.env` with `GEMINI_MODEL`. The remaining Gemini settings are:

| Variable | Purpose | Default |
| --- | --- | --- |
| `GEMINI_TEMPERATURE` | Controls response variation. | `0.2` |
| `GEMINI_MAX_OUTPUT_TOKENS` | Limits generated response size. | `512` |
| `GEMINI_TIMEOUT_MS` | Sets the request timeout in milliseconds. | `30000` |
| `GEMINI_RETRY_ATTEMPTS` | Sets the number of SDK request attempts. | `1` |

For production-like settings, set `DJANGO_DEBUG=False`, configure a strong `DJANGO_SECRET_KEY`, and set `DJANGO_ALLOWED_HOSTS`. Django then enables HTTPS redirects, HSTS, secure cookies, and content-type sniffing protection.

## Run the tests

Run the Django test suite from the repository root:

```bash
python manage.py test
```

The tests cover routing, catalog filters, product and promotion lookups, order context, policy retrieval, API conversation tokens, generic provider errors, and the CLI flow.

Optional scenario tests use `requirements-test.txt` and require network access to an available model provider:

```bash
python -m pip install -r requirements-test.txt
python -m pytest support/tests/test_agent_scenarios.py -q -s
```

These tests are supplementary. The deterministic Django test suite remains the required local verification because scenario execution depends on external provider availability.

## Interaction examples

See [examples/conversations.md](examples/conversations.md) for five representative conversations covering product search, store information, order lookup, policies, and out-of-scope requests. The examples describe expected behavior; runtime facts are read from SQLite and the policy document.

See [examples/agent_scenario_report.md](examples/agent_scenario_report.md) for the optional scenario-test report and its external dependency notes.

## Error handling and security

- Gemini failures are logged with the model name and exception details in `logs/application.log`.
- Customers receive a generic service-unavailable message instead of provider diagnostics.
- `DJANGO_SECRET_KEY` and `GEMINI_API_KEY` are read from environment variables.
- Conversation continuation requires a private UUID token.
- The API validates message, customer ID, conversation ID, and conversation token types.
- A new conversation does not use an untrusted customer ID to retrieve orders before the conversation is associated with that customer.
- Logs, the local SQLite database, and `.env` are excluded from Git by `.gitignore`.

## Known limitations

This challenge implementation is intentionally local and focused. A production version should add:

- authenticated user identity and authorization;
- rate limiting, metrics, tracing, and alerting;
- a production database and managed secret storage;
- a real order-management and shipping-provider integration;
- broader catalog search, including a dedicated search index and fuzzy matching;
- an evaluation dataset with automated quality and safety thresholds.

## AI-assisted development

Coding assistants supported repository setup, code review, test design, debugging, and documentation editing. The implementation decisions, requirement mapping, data validation, security checks, and final verification were reviewed manually. The assistant was not used as a source of store facts: those facts come from the supplied CSV files and policy PDF.

## Publication checklist

Before you publish the repository, verify the following:

- `python manage.py test` passes from a clean virtual environment;
- `.env`, API keys, generated logs, and local database files are not tracked;
- the README commands match the checked-in files;
- `examples/conversations.md` contains three to five varied examples;
- the repository is public and contains the real commit history;
- you create the final commit before submitting the repository link and make no further changes after the challenge submission deadline.

## License

This repository contains challenge-specific code and data. Add a project license before redistributing it outside the evaluation context.
