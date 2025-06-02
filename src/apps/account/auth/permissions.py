from rest_framework import permissions as _permissions
from ..enums import UserRoleEnum

class BasePermissionCustom(_permissions.BasePermission):
    user_role = ''

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or user.is_blocked:
            return False
        return user.role == self.get_roles()

    @classmethod
    def get_role(cls):
        return cls.user_role

    @classmethod
    def get_roles(cls):
        return [cls.get_role()]

    @classmethod
    def repr(cls):
        return cls.user_role


class BasePermissionAnyCustom(BasePermissionCustom):
    permission_classes_any = None

    def has_permission(self, request, view):
        if not request.user.is_authenticated or request.user.is_blocked:
            return False
        if not self.permission_classes_any:
            return False
        allowed_roles = {perm.get_role() for perm in self.get_permissions_any()}
        return request.user.role in allowed_roles

    @classmethod
    def get_permissions_any(cls):
        return cls.permission_classes_any

    @classmethod
    def get_roles(cls):
        return [perm.get_role() for perm in cls.permission_classes_any]


#---------------------------------------------------------------------------


class IsAdmin(BasePermissionCustom):
    user_role = UserRoleEnum.ADMIN


class IsProjectAdmin(BasePermissionCustom):
    user_role = UserRoleEnum.PROJECT_ADMIN


class IsProjectMember(BasePermissionCustom):
    user_role = UserRoleEnum.PROJECT_MEMBER


class IsViewer(BasePermissionCustom):
    user_role = UserRoleEnum.VIEWER


#---------------------------------------------------------------------------

class IsAdminOrProjectAdmin(BasePermissionAnyCustom):
    permission_classes_any = [IsAdmin, IsProjectAdmin]

    @classmethod
    def repr(cls):
        return 'Admin or Project Admin'


class IsTeamUser(BasePermissionAnyCustom):
    permission_classes_any = [IsProjectAdmin, IsProjectMember]

    @classmethod
    def repr(cls):
        return 'Team user (project_admin or project_member)'


class IsAdminOrViewer(BasePermissionAnyCustom):
    permission_classes_any = [IsAdmin, IsViewer]

    @classmethod
    def repr(cls):
        return 'Admin or Viewer'


class IsAdminOrMember(BasePermissionAnyCustom):
    permission_classes_any = [IsAdmin, IsProjectMember]

    @classmethod
    def repr(cls):
        return 'Admin or Project Member'

#---------------------------------------------------------------------------


class IsOwnerOrAdmin(BasePermissionAnyCustom):
    permission_classes_any = [IsAdmin, IsProjectAdmin]

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or request.user.is_blocked:
            return False
        if IsAdminOrProjectAdmin().has_permission(request, view):
            return True
        return obj.user == request.user