from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
               path("UserLogin.html", views.UserLogin, name="UserLogin"),	      
               path("UserLoginAction", views.UserLoginAction, name="UserLoginAction"),
               path("SignupAction", views.SignupAction, name="SignupAction"),
               path("Signup.html", views.Signup, name="Signup"),
               path("TrainModel", views.TrainModel, name="TrainModel"),
	       path("ViewHistory", views.ViewHistory, name="ViewHistory"),
	       path("Chatbot.html", views.Chatbot, name="Chatbot"),
	       path("record", views.record, name="record"),
	       path("TextChatbot.html", views.TextChatbot, name="TextChatbot"),
	       path("ChatData", views.ChatData, name="ChatData"),
]
