from rest_framework import permissions as _permissions


class BasePermissionCustom(_permissions.BasePermission):
    user_role = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or user.is_blocked:
            return False
        return request.user and request.user.role == self.user_role

    @classmethod
    def get_role(cls):
        return cls.user_role

    @classmethod
    def get_roles(cls):
        return [cls.get_role()]

    @classmethod
    def repr(cls):
        return cls.get_role()


class BasePermissionAnyCustom(BasePermissionCustom):
    # TODO: better to change check multiple role structure
    """
        If the user has any of the permissions can have access
    """
    permission_classes_any = None

    def has_permission(self, request, view):
        allowed_roles = {perm.get_role() for perm in self.get_permissions_any()}
        return request.user.role in allowed_roles if request.user.is_authenticated else False

    @classmethod
    def get_permissions_any(cls):
        return cls.permission_classes_any

    @classmethod
    def get_roles(cls):
        return [perm.get_role() for perm in cls.get_permissions_any()]


class IsDistributorUser(BasePermissionCustom):
    user_role = 'distributor_user'


class IsCommonUser(BasePermissionCustom):
    user_role = 'common_user'


class IsSuperUser(BasePermissionCustom):
    user_role = 'super_user'


class IsOperator(BasePermissionCustom):
    user_role = 'operator_user'


class IsAdmin(BasePermissionAnyCustom):
    permission_classes_any = [IsSuperUser, IsOperator]

    @classmethod
    def repr(cls):
        return 'admin user(super_user or operator_user)'


class IsAdminOrCommonUser(BasePermissionAnyCustom):
    permission_classes_any = [IsSuperUser, IsOperator, IsCommonUser]

    @classmethod
    def repr(cls):
        return 'user(super_user or operator_user or common_user)'


class IsAdminOrDistributorUser(BasePermissionAnyCustom):
    permission_classes_any = [IsSuperUser, IsOperator, IsDistributorUser]

    @classmethod
    def repr(cls):
        return 'user(super_user or operator_user or distributor_user)'


class IsSuperOrDistributorUser(BasePermissionAnyCustom):
    permission_classes_any = [IsSuperUser, IsDistributorUser]

    @classmethod
    def repr(cls):
        return 'user(super_user or distributor_user)'


class IsSuperOrCommonUser(BasePermissionAnyCustom):
    permission_classes_any = [IsSuperUser, IsCommonUser]

    @classmethod
    def repr(cls):
        return 'user(super_user or common_user)'