import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from pypdf import PdfReader

from support.models import PolicyChunk
from support.services.policy_search import normalize_text


class Command(BaseCommand):
    help = "Extract and store searchable chunks from the store policy PDF."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="data/políticas_da_loja.pdf",
            help="Path to the policy PDF.",
        )
        parser.add_argument(
            "--source-name",
            default="políticas_da_loja.pdf",
            help="Logical name used to identify the source document.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        pdf_path = Path(options["file"]).resolve()
        source_name = options["source_name"]
        if not pdf_path.is_file():
            raise CommandError(f"Policy PDF not found: {pdf_path}")

        reader = PdfReader(str(pdf_path))
        PolicyChunk.objects.filter(source_name=source_name).delete()

        imported_chunks = 0
        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if not text:
                continue

            for chunk_index, content in enumerate(self._split_text(text)):
                PolicyChunk.objects.create(
                    source_name=source_name,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    content=content,
                    search_text=normalize_text(content),
                )
                imported_chunks += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {imported_chunks} policy chunks from {len(reader.pages)} pages."
            )
        )

    @staticmethod
    def _split_text(text: str) -> list[str]:
        paragraphs = [paragraph.strip() for paragraph in re.split(r"\n{2,}", text)]
        return [paragraph for paragraph in paragraphs if paragraph]

