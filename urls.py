from django.urls import path

import views

urlpatterns = [
    path("", views.index, name="home"),
    path("index.html", views.index, name="index"),
    path("ExecuteProgram", views.ExecuteProgram, name="ExecuteProgram"),
    path("ChatData", views.ChatData, name="ChatData"),
]
