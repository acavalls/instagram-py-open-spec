import random

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.services import UserService
from apps.accounts.use_cases import (
    AuthenticateUserInput,
    AuthenticateUserUseCase,
    RegisterUserInput,
    RegisterUserUseCase,
)
from apps.posts.models import Post
from apps.posts.services import PostService
from apps.posts.use_cases import (
    CreatePostInput,
    CreatePostUseCase,
    DeletePostInput,
    DeletePostUseCase,
    UpdatePostInput,
    UpdatePostUseCase,
)

POSTS_PER_PAGE = 12

RANDOM_CAPTIONS = [
    "Living my best life!",
    "Another great day",
    "Making memories",
    "Good vibes only",
    "Adventure awaits",
    "Chasing dreams",
    "Sunset chasing",
    "Coffee and dreams",
    "Finding beauty in small moments",
    "Weekend mode: on",
]

GIF_BYTES = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9"
    b"\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00"
    b"\x00\x02\x02\x4c\x01\x00\x3b"
)


def _get_page_posts(user_id, page: int) -> tuple[list[Post], bool]:
    offset = (page - 1) * POSTS_PER_PAGE
    posts = list(
        PostService.list_for_user(
            user_id=user_id,
            limit=POSTS_PER_PAGE + 1,
            offset=offset,
        )
    )
    has_next = len(posts) > POSTS_PER_PAGE
    if has_next:
        posts = posts[:POSTS_PER_PAGE]
    return posts, has_next


@login_required
def index(request):
    """Personal feed — the logged-in user's own posts, newest first."""
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1
    page = max(page, 1)

    posts, has_next = _get_page_posts(request.user.id, page)

    return render(
        request,
        "web/index.html",
        {
            "posts": posts,
            "page": page,
            "has_next": has_next,
            "has_prev": page > 1,
        },
    )


def login_view(request):
    """Login page — authenticates user via session and redirects to home."""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        use_case = AuthenticateUserUseCase(user_service=UserService())
        output = use_case.execute(
            AuthenticateUserInput(username=username, password=password)
        )

        if output.success and output.user:
            auth_login(request, output.user)
            messages.success(request, "Logged in successfully")
            return redirect("web:index")

        messages.error(request, output.error or "Invalid credentials")
        return render(request, "web/login.html", {"error": output.error})

    return render(request, "web/login.html")


def register_view(request):
    """Register page — creates a new user and redirects to login."""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not 3 <= len(username) <= 150:
            msg = "Username must be between 3 and 150 characters"
            messages.error(request, msg)
            return render(request, "web/register.html", {"error": msg})

        if not username.isalnum():
            msg = "Username must contain only letters and numbers"
            messages.error(request, msg)
            return render(request, "web/register.html", {"error": msg})

        if len(password) < 8:
            msg = "Password must be at least 8 characters"
            messages.error(request, msg)
            return render(request, "web/register.html", {"error": msg})

        use_case = RegisterUserUseCase(user_service=UserService())
        input_dto = RegisterUserInput(email=email, username=username, password=password)
        output = use_case.execute(input_dto)

        if output.success:
            messages.success(request, "Account created successfully. Please login.")
            return redirect("web:login")

        messages.error(request, output.error or "Registration failed")
        return render(request, "web/register.html", {"error": output.error})

    return render(request, "web/register.html")


@login_required
def logout_view(request):
    """Logout — clears session and redirects to login."""
    auth_logout(request)
    messages.info(request, "You have been logged out")
    return redirect("web:login")


@login_required
@require_POST
def create_random_post(request):
    """Create a post with a generated placeholder image."""
    caption = random.choice(RANDOM_CAPTIONS)
    color = random.randint(0, 0xFFFFFF)
    placeholder_file = SimpleUploadedFile(
        f"post_{color}.jpg",
        GIF_BYTES,
        content_type="image/jpeg",
    )

    use_case = CreatePostUseCase(post_service=PostService())
    output = use_case.execute(
        CreatePostInput(
            owner_id=request.user.id,
            caption=caption,
            media_files=[
                {
                    "file": placeholder_file,
                    "media_type": "image",
                    "order": 0,
                }
            ],
        )
    )

    if output.success:
        messages.success(request, "Post created!")
        return redirect("web:index")

    messages.error(request, output.error or "Failed to create post")
    return redirect("web:index")


@login_required
def get_edit_form(request, post_id):
    """Return the inline edit form HTML."""
    post = PostService.get_by_id(post_id)
    if not post:
        raise Http404("Post not found")

    is_valid, error = post.can_edit(request.user.id)
    if not is_valid:
        raise Http404(error)

    return render(request, "web/_edit_form.html", {"post": post})


@login_required
def cancel_edit(request, post_id):
    """Return the hidden state for the edit form."""
    return render(request, "web/_cancel_edit.html", {"post_id": post_id})


@login_required
@require_POST
def submit_edit(request, post_id):
    """Submit the inline edit form."""
    post = PostService.get_by_id(post_id)
    if not post:
        messages.error(request, "Post not found")
        return render(request, "web/_toast.html")

    is_valid, error = post.can_edit(request.user.id)
    if not is_valid:
        messages.error(request, error)
        return render(request, "web/_toast.html")

    caption = request.POST.get("caption", "").strip()
    use_case = UpdatePostUseCase(post_service=PostService())
    output = use_case.execute(
        UpdatePostInput(post_id=post_id, user_id=request.user.id, caption=caption)
    )

    if output.success:
        messages.success(request, "Post updated!")
        updated = PostService.get_by_id(post_id)
        return render(
            request,
            "web/_post_card.html",
            {"post": updated, "render_toasts": True},
        )

    messages.error(request, output.error or "Failed to update post")
    return render(request, "web/_toast.html")


@login_required
@require_POST
def delete_post(request, post_id):
    """Delete a post."""
    use_case = DeletePostUseCase(post_service=PostService())
    output = use_case.execute(DeletePostInput(post_id=post_id, user_id=request.user.id))

    if output.success:
        messages.success(request, "Post deleted!")
        return render(request, "web/_deleted_post.html", {"post_id": post_id})

    messages.error(request, output.error or "Failed to delete post")
    return render(request, "web/_toast.html")
