from django.urls import path

import views

urlpatterns = [
    path("", views.index, name="home"),
    path("index.html", views.index, name="index"),
    path("ExecuteProgram", views.ExecuteProgram, name="ExecuteProgram"),
    path("TextChatbot.html", views.text_chatbot, name="text_chatbot"),
    path("ChatData", views.ChatData, name="ChatData"),
]
