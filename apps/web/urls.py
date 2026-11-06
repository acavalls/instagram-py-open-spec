from django.urls import path

from apps.web import views

app_name = "web"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("follow/<uuid:user_id>/", views.follow_user, name="follow"),
    path("unfollow/<uuid:user_id>/", views.unfollow_user, name="unfollow"),
    path("profile/<uuid:user_id>/", views.profile_view, name="profile"),
    path(
        "profile/<uuid:user_id>/following/",
        views.following_list,
        name="following_list",
    ),
    path("posts/create/", views.create_random_post, name="create_random_post"),
    path("stories/create/", views.create_story, name="create_story"),
    path("stories/<uuid:story_id>/view/", views.view_story, name="view_story"),
    path("posts/<uuid:post_id>/edit-form/", views.get_edit_form, name="get_edit_form"),
    path("posts/<uuid:post_id>/cancel-edit/", views.cancel_edit, name="cancel_edit"),
    path("posts/<uuid:post_id>/submit-edit/", views.submit_edit, name="submit_edit"),
    path("posts/<uuid:post_id>/delete/", views.delete_post, name="delete_post"),
]
