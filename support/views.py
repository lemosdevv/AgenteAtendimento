import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

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

    try:
        agent = CustomerSupportAgent(GeminiTextGenerator())
        response = agent.respond(message.strip(), customer_id=customer_id)
    except MissingGeminiApiKeyError as error:
        return JsonResponse({"error": str(error)}, status=503)

    return JsonResponse({"response": response})

