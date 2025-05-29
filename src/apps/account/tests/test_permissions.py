import pytest
from apps.account.auth.permissions import IsAdmin, IsProjectAdmin, IsViewer, IsOwnerOrAdmin
from apps.account.tests.factories import UserFactory


@pytest.mark.django_db
def test_is_admin_permission():
    admin = UserFactory(role="admin")
    viewer = UserFactory(role="viewer")

    request = type("Request", (), {"user": admin})
    assert IsAdmin().has_permission(request, None) is True

    request = type("Request", (), {"user": viewer})
    assert IsAdmin().has_permission(request, None) is False


@pytest.mark.django_db
def test_is_project_admin_permission():
    project_admin = UserFactory(role="project_admin")
    viewer = UserFactory(role="viewer")

    request = type("Request", (), {"user": project_admin})
    assert IsProjectAdmin().has_permission(request, None) is True

    request = type("Request", (), {"user": viewer})
    assert IsProjectAdmin().has_permission(request, None) is False


@pytest.mark.django_db
def test_blocked_user_has_no_permission():
    blocked_user = UserFactory(role="viewer")

    blocked_user_mock = type("MockUser", (), {"is_authenticated": True, "is_blocked": True, "role": blocked_user.role})

    request = type("Request", (), {"user": blocked_user_mock})
    assert IsViewer().has_permission(request, None) is False


@pytest.mark.django_db
def test_is_owner_or_admin_permission():
    admin = UserFactory(role="admin")
    owner = UserFactory(role="viewer")
    another_user = UserFactory(role="viewer")

    mock_object = type("MockObject", (), {"user": owner})

    admin_request = type("Request", (), {"user": admin})
    assert IsOwnerOrAdmin().has_object_permission(admin_request, None, mock_object) is True

    # بررسی دسترسی مالک
    owner_request = type("Request", (), {"user": owner})
    assert IsOwnerOrAdmin().has_object_permission(owner_request, None, mock_object) is True

    # بررسی عدم دسترسی سایر کاربران
    another_request = type("Request", (), {"user": another_user})
    assert IsOwnerOrAdmin().has_object_permission(another_request, None, mock_object) is False