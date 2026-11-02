"""Simulation scenarios for the customer-support agent.

These tests require a configured Gemini API key and an imported local database.
They intentionally exercise complete multi-turn conversations instead of isolated
classification functions.
"""

import asyncio
import os
from pathlib import Path

import django
import pytest
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault(
    "SCENARIO_CACHE_DIR",
    str(PROJECT_ROOT / ".scenario-cache"),
)
load_dotenv(PROJECT_ROOT / ".env")
django.setup()
import scenario

from support.services.customer_support_agent import CustomerSupportAgent
from support.services.llm import GeminiTextGenerator


SCENARIO_MODEL = f"gemini/{os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite')}"
scenario.configure(default_model=SCENARIO_MODEL)


class AnaScenarioAdapter(scenario.AgentAdapter):
    """Adapt the production agent to the Scenario SDK."""

    async def call(self, input: scenario.AgentInput) -> scenario.AgentReturnTypes:
        current_message = input.last_new_user_message_str()
        history = [
            {"role": item["role"], "content": item["content"]}
            for item in input.messages[:-1]
            if item["role"] in {"user", "assistant"}
        ]
        agent = CustomerSupportAgent(GeminiTextGenerator())
        return await asyncio.to_thread(
            agent.respond,
            current_message,
            history=history,
        )


def _strict_judge(criteria: list[str]) -> scenario.JudgeAgent:
    return scenario.JudgeAgent(
        model=SCENARIO_MODEL,
        criteria=criteria,
        system_prompt=(
            "Você é um avaliador rigoroso de atendimento ao cliente. "
            "Avalie o resultado observado, não as instruções internas do agente. "
            "Reprove respostas vagas, inventadas ou que ignorem o histórico."
        ),
    )


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_order_status_recovers_from_missing_order_number():
    result = await scenario.run(
        name="order status multi-turn recovery",
        description=(
            "Act as a demanding customer who wants the status of an order. "
            "Start without giving an order number. If Ana asks for it, provide "
            "the number 8 naturally, using wording such as 'meu pedido é o número 8'. "
            "Do not accept a generic missing-context answer."
        ),
        agents=[
            AnaScenarioAdapter(),
            scenario.UserSimulatorAgent(
                model=SCENARIO_MODEL,
                system_prompt=(
                    "Você é um cliente brasileiro impaciente, mas cooperativo. "
                    "Mantenha o objetivo do pedido e use respostas curtas."
                ),
            ),
            _strict_judge(
                [
                    "Ana percebe que a segunda mensagem do cliente fornece o número do pedido.",
                    "Ana consulta e informa dados verificáveis do pedido 8.",
                    "Ana não diz que o contexto fornecido não contém informações.",
                ]
            ),
        ],
        max_turns=6,
        verbose=True,
        set_id="ana-customer-support",
    )
    assert result.success, result.reasoning


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_product_questions_keep_catalog_context_precise():
    result = await scenario.run(
        name="catalog precision under follow-up questions",
        description=(
            "Ask about the Yamaha C40 Nylon Natural price, then ask whether it "
            "has an active discount, and finally ask which instrument is cheapest. "
            "Challenge any answer that lists unrelated products or treats the first "
            "alphabetical result as the cheapest."
        ),
        agents=[
            AnaScenarioAdapter(),
            scenario.UserSimulatorAgent(
                model=SCENARIO_MODEL,
                system_prompt=(
                    "Você compara informações de catálogo com atenção. "
                    "Se a resposta estiver genérica, peça uma correção objetiva."
                ),
            ),
            _strict_judge(
                [
                    "Ana responde ao Yamaha C40 usando o produto correspondente do catálogo.",
                    "Ana distingue preço atual de promoção ativa e não inventa desconto.",
                    "Ana usa o menor preço real disponível quando perguntada pelo instrumento mais barato.",
                ]
            ),
        ],
        max_turns=6,
        verbose=True,
        set_id="ana-customer-support",
    )
    assert result.success, result.reasoning


