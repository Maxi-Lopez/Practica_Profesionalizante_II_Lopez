from django.urls import path
from .views import LoginView, RegisterView, UserDetailView

urlpatterns = [
    path("token/", LoginView.as_view(), name="token_obtain_pair"),
    path("register/", RegisterView.as_view(), name="api_register"),
    path("user/", UserDetailView.as_view(), name="user_detail"),
]