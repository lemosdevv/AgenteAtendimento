from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.status import Status

from support.models import Conversation, Customer, Message
from support.services.customer_support_agent import CustomerSupportAgent
from support.services.llm import (
    GeminiRequestError,
    GeminiTextGenerator,
    MissingGeminiApiKeyError,
    SERVICE_UNAVAILABLE_MESSAGE,
)


class Command(BaseCommand):
    help = "Start an interactive customer support chat in the terminal."

    def add_arguments(self, parser):
        parser.add_argument(
            "--customer-id",
            type=int,
            help="Optional customer ID used to look up that customer's orders.",
        )

    def handle(self, *args, **options):
        console = Console()
        customer_id = options.get("customer_id")
        if customer_id is not None and not Customer.objects.filter(id=customer_id).exists():
            raise CommandError(f"Customer not found: {customer_id}")

        conversation = Conversation.objects.create(customer_id=customer_id)
        agent = CustomerSupportAgent(GeminiTextGenerator())

        console.print(
            Panel.fit(
                "[bold white]Ana[/bold white]\n"
                "[cyan]Assistente virtual da Empório da Música[/cyan]\n\n"
                "[dim]Encontre instrumentos, consulte pedidos e tire dúvidas sobre nossas políticas.[/dim]",
                title="[bold magenta]Empório da Música[/bold magenta]",
                border_style="magenta",
                padding=(1, 3),
            )
        )
        console.print(
            f"[dim]Conversa:[/dim] [cyan]{conversation.id}[/cyan]  "
            "[dim]- Digite[/dim] [bold]sair[/bold] [dim]para encerrar.[/dim]\n"
        )

        while True:
            try:
                message = console.input("[bold green]Você[/bold green] [dim]>[/dim] ").strip()
            except (EOFError, KeyboardInterrupt):
                console.print("\n[dim]Até logo![/dim]")
                break

            if message.lower() in {"exit", "quit", "sair"}:
                console.print("[dim]Até logo![/dim]")
                break
            if not message:
                continue

            history = list(
                conversation.messages.values("role", "content")
                .order_by("created_at", "id")
            )[-10:]

            try:
                with Status("[cyan]Ana está pensando...[/cyan]", console=console):
                    response = agent.respond(
                        message,
                        customer_id=conversation.customer_id,
                        history=history,
                    )
            except (GeminiRequestError, MissingGeminiApiKeyError):
                console.print(
                    Panel(
                        SERVICE_UNAVAILABLE_MESSAGE,
                        title="[bold yellow]Ana[/bold yellow]",
                        border_style="yellow",
                    )
                )
                break

            with transaction.atomic():
                Message.objects.create(
                    conversation=conversation,
                    role=Message.Role.USER,
                    content=message,
                )
                Message.objects.create(
                    conversation=conversation,
                    role=Message.Role.ASSISTANT,
                    content=response,
                )

            console.print(
                Panel(
                    Markdown(response),
                    title="[bold magenta]Ana[/bold magenta]",
                    border_style="cyan",
                    padding=(0, 2),
                )
            )
            console.print()

