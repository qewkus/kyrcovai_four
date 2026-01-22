from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.apps import UsersConfig

from .views import BlockUserView, RegisterView, UserDetailList, UserListView, email_verification

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="mailing:home"), name="logout"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
    path("user_list/", UserListView.as_view(), name="user_list"),
    path("user_detail/<int:pk>", UserDetailList.as_view(), name="user_detail"),
    path("user_block/<int:user_id>", BlockUserView.as_view(), name="user_block"),
]
