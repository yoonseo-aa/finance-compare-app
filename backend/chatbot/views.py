from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ChatbotMessageSerializer
from .services import ChatbotServiceError, generate_chatbot_answer


class ChatbotMessageAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ChatbotMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = generate_chatbot_answer(
                message=serializer.validated_data["message"],
                user=request.user if request.user.is_authenticated else None,
                context_type=serializer.validated_data.get("contextType", ""),
            )
        except ChatbotServiceError as exc:
            return Response(
                {
                    "detail": str(exc),
                    "answer": "일시적으로 답변을 불러오지 못했어요. 잠시 후 다시 시도해주세요.",
                    "model": getattr(settings, "OPENAI_CHAT_MODEL", "gpt-5.4-mini"),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(result)
