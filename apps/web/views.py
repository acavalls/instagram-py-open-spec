from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.services import UserService
from apps.accounts.use_cases import (
    AuthenticateUserInput,
    AuthenticateUserUseCase,
    RegisterUserInput,
    RegisterUserUseCase,
)


@login_required
def index(request):
    """Placeholder home page until the feed capability lands."""
    return render(request, "web/index.html")


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
