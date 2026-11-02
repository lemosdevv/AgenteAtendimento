# Agent Scenario Report

Date: 2026-10-31

## Scope

The \`scenarios\` skill was used to create multi-turn tests for the production
customer-support agent. The scenarios cover:

- recovering an order lookup after the customer initially omits the order number;
- keeping product, price, promotion, and cheapest-item answers tied to the catalog;
- running an adversarial red-team pass when a compatible red-team SDK is available.

## Collection result

Two multi-turn scenarios were collected successfully.

## Execution result

The scenarios did not reach the agent evaluation stage. LiteLLM could not
resolve \`raw.githubusercontent.com\` while updating its model cost map and then
remained waiting for the external provider. No agent trace or judge result was
produced, so this run is classified as an infrastructure failure rather than an
agent behavior failure.

The existing deterministic suite remains green:

\`\`\`text
Ran 24 tests
OK
\`\`\`

## Next run

After Gemini connectivity is available, run:

\`\`\`powershell
$env:SCENARIO_CACHE_DIR = (Join-Path (Get-Location) ".scenario-cache")
.venv\Scripts\python.exe -m pytest support/tests/test_agent_scenarios.py -q -s
\`\`\`

The failed scenario transcripts should be reviewed before changing prompts or
criteria. Fixes must address the failing behavior class and then be rerun with
different wording.
