import json
from uuid import UUID

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from support.models import Conversation, Message
from support.services.customer_support_agent import CustomerSupportAgent
from support.services.llm import GeminiTextGenerator, MissingGeminiApiKeyError


@csrf_exempt
@require_POST
def chat(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Request body must be valid JSON."}, status=400)

    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        return JsonResponse(
            {"error": "The 'message' field must be a non-empty string."},
            status=400,
        )

    customer_id = payload.get("customer_id")
    if customer_id is not None and (
        isinstance(customer_id, bool) or not isinstance(customer_id, int)
    ):
        return JsonResponse(
            {"error": "The 'customer_id' field must be an integer."},
            status=400,
        )

    conversation_id = payload.get("conversation_id")
    conversation_token = payload.get("conversation_token")
    conversation = None
    new_conversation = conversation_id is None
    if conversation_id is not None:
        if not conversation_token:
            return JsonResponse(
                {"error": "The 'conversation_token' field is required."},
                status=403,
            )
        try:
            conversation_uuid = UUID(str(conversation_id))
            token_uuid = UUID(str(conversation_token))
            conversation = Conversation.objects.prefetch_related("messages").get(
                id=conversation_uuid,
                access_token=token_uuid,
            )
        except (ValueError, Conversation.DoesNotExist):
            return JsonResponse(
                {"error": "The 'conversation_id' does not identify a conversation."},
                status=404,
            )
        if customer_id is not None and conversation.customer_id not in (None, customer_id):
            return JsonResponse(
                {"error": "The conversation does not belong to this customer."},
                status=403,
            )

    history = []
    if conversation is not None:
        history = list(
            conversation.messages.values("role", "content").order_by("created_at", "id")
        )[-10:]
    trusted_customer_id = conversation.customer_id if conversation is not None else None

    try:
        agent = CustomerSupportAgent(GeminiTextGenerator())
        response = agent.respond(
            message.strip(),
            customer_id=trusted_customer_id,
            history=history,
        )
    except MissingGeminiApiKeyError as error:
        return JsonResponse({"error": str(error)}, status=503)

    with transaction.atomic():
        if conversation is None:
            conversation = Conversation.objects.create(customer_id=customer_id)
        elif customer_id is not None and conversation.customer_id is None:
            conversation.customer_id = customer_id
            conversation.save(update_fields=["customer", "updated_at"])
        Message.objects.create(
            conversation=conversation,
            role=Message.Role.USER,
            content=message.strip(),
        )
        Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=response,
        )

    response_data = {
        "conversation_id": str(conversation.id),
        "response": response,
    }
    if new_conversation:
        response_data["conversation_token"] = str(conversation.access_token)
    return JsonResponse(response_data)

