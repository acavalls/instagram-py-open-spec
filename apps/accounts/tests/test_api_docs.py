"""Smoke-checks for the OpenAPI documentation endpoints.

Scenarios: Schema endpoint serves the API contract, Docs UI renders
(spec delta: api-docs)."""

import json

import pytest

pytestmark = pytest.mark.django_db


class TestOpenApiDocs:
    def test_schema_endpoint_serves_the_api_contract(self, client):
        """Scenario: Schema endpoint serves the API contract."""
        response = client.get("/schema/?format=json")

        assert response.status_code == 200
        schema = json.loads(response.content)
        paths = schema["paths"]
        assert "/api/auth/login/" in paths
        assert "/api/posts/" in paths

    def test_docs_ui_renders(self, client):
        """Scenario: Docs UI renders."""
        response = client.get("/docs/")

        assert response.status_code == 200
        assert b"swagger" in response.content.lower()


class TestAdminConsole:
    def test_anonymous_visitor_redirected_to_admin_login(self, client):
        """Scenario: Anonymous visitor redirected to admin login."""
        response = client.get("/admin/", follow=True)

        assert response.status_code == 200
        assert "/admin/login/" in response.request["PATH_INFO"]
        assert b"username" in response.content.lower()
