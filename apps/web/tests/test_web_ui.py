"""Tests for the global web shell (sidebar, icons, auth layout).

Scenarios: Sidebar renders navigation for authenticated user, Profile link
points to own profile, Placeholder entries have no destination, Create
submits the post creation form, Logout available at the sidebar bottom,
Anonymous pages render without sidebar, Active link reflects current page,
Icon font is loaded, Login renders the auth card, Register renders the auth
card (spec delta: web-ui)."""

import pytest

from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestSidebarNavigation:
    def test_sidebar_renders_navigation_for_authenticated_user(self, client):
        """Scenario: Sidebar renders navigation for authenticated user."""
        user = UserFactory()
        client.force_login(user)

        response = client.get("/web/")

        assert response.status_code == 200
        content = response.content.decode()
        assert 'class="sidebar"' in content
        for label in (
            "Home",
            "Search",
            "Explore",
            "Messages",
            "Notifications",
            "Create",
            "Profile",
        ):
            assert label in content

    def test_profile_link_points_to_own_profile(self, client):
        """Scenario: Profile link points to own profile."""
        user = UserFactory()
        client.force_login(user)

        response = client.get("/web/")

        assert f'href="/web/profile/{user.id}/"' in response.content.decode()

    def test_placeholder_entries_have_no_destination(self, client):
        """Scenario: Placeholder entries have no destination."""
        user = UserFactory()
        client.force_login(user)

        response = client.get("/web/")

        content = response.content.decode()
        for label in ("Search", "Explore", "Messages", "Notifications"):
            entry = content.split(f">{label}</span>", 1)[0]
            assert entry.rsplit('href="', 1)[1].startswith('#"')

    def test_create_submits_the_post_creation_form(self, client):
        """Scenario: Create submits the post creation form."""
        user = UserFactory()
        client.force_login(user)

        response = client.get("/web/")

        content = response.content.decode()
        assert 'hx-post="/web/posts/create/"' in content

    def test_logout_available_at_the_sidebar_bottom(self, client):
        """Scenario: Logout available at the sidebar bottom."""
        user = UserFactory()
        client.force_login(user)

        response = client.get("/web/")

        content = response.content.decode()
        sidebar_bottom = content.split('class="sidebar__bottom"', 1)[1]
        assert "/web/logout/" in sidebar_bottom

    def test_anonymous_pages_render_without_sidebar(self, client):
        """Scenario: Anonymous pages render without sidebar."""
        response = client.get("/web/login/")

        assert response.status_code == 200
        content = response.content.decode()
        assert 'class="sidebar"' not in content
        assert 'class="auth-page"' in content

    def test_active_link_reflects_current_page(self, client):
        """Scenario: Active link reflects current page."""
        user = UserFactory()
        client.force_login(user)

        response = client.get("/web/")

        content = response.content.decode()
        home_entry = content.split('class="sidebar__link', 1)[1]
        assert "sidebar__link--active" in home_entry.split("</a>", 1)[0]
        # Profile entry is not active on the home page
        profile_entry = content.split(">Profile</span>", 1)[0]
        assert (
            "sidebar__link--active"
            not in profile_entry.rsplit('class="sidebar__link', 1)[1]
        )


class TestIconRendering:
    def test_icon_font_is_loaded(self, client):
        """Scenario: Icon font is loaded."""
        user = UserFactory()
        client.force_login(user)

        response = client.get("/web/")

        assert "bootstrap-icons.min.css" in response.content.decode()


class TestAuthLayout:
    def test_login_renders_the_auth_card(self, client):
        """Scenario: Login renders the auth card."""
        response = client.get("/web/login/")

        assert response.status_code == 200
        content = response.content.decode()
        assert 'class="auth-card"' in content
        assert "auth-logo" in content
        assert "/web/register/" in content
        assert "auth-card--secondary" in content

    def test_register_renders_the_auth_card(self, client):
        """Scenario: Register renders the auth card."""
        response = client.get("/web/register/")

        assert response.status_code == 200
        content = response.content.decode()
        assert 'class="auth-card"' in content
        assert "auth-logo" in content
        assert "/web/login/" in content
        assert "auth-card--secondary" in content
