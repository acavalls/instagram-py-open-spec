from django.urls import path

from apps.web import views

app_name = "web"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("posts/create/", views.create_random_post, name="create_random_post"),
    path("posts/<uuid:post_id>/edit-form/", views.get_edit_form, name="get_edit_form"),
    path("posts/<uuid:post_id>/cancel-edit/", views.cancel_edit, name="cancel_edit"),
    path("posts/<uuid:post_id>/submit-edit/", views.submit_edit, name="submit_edit"),
    path("posts/<uuid:post_id>/delete/", views.delete_post, name="delete_post"),
]
