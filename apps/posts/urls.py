from django.urls import path

from apps.posts import views

app_name = "posts"

urlpatterns = [
    path("", views.PostListCreateView.as_view(), name="post-list-create"),
    path("<uuid:pk>/", views.PostDetailView.as_view(), name="post-detail"),
]
