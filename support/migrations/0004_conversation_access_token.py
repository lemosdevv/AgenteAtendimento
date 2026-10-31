import uuid

from django.db import migrations, models


def populate_access_tokens(apps, schema_editor):
    Conversation = apps.get_model("support", "Conversation")
    for conversation in Conversation.objects.filter(access_token__isnull=True):
        conversation.access_token = uuid.uuid4()
        conversation.save(update_fields=["access_token"])


class Migration(migrations.Migration):
    dependencies = [
        ("support", "0003_conversation_message"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="access_token",
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.RunPython(populate_access_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="conversation",
            name="access_token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]

