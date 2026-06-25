from django.urls import path

from .views import ChatbotMessageAPIView

urlpatterns = [
    path("message/", ChatbotMessageAPIView.as_view(), name="chatbot_message"),
]
