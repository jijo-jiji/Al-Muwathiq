from django.urls import path
from .views import ChatSessionView, ChatMessageView

urlpatterns = [
    path('chat/session/', ChatSessionView.as_view(), name='create_session'),
    path('chat/<uuid:session_id>/message/', ChatMessageView.as_view(), name='send_message'),
]
