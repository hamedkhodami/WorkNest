import abc
import functools

from drf_yasg.utils import swagger_auto_schema


def swagger_schema(*args, **kwargs):
    def decorator(f):
        swagger_auto_schema(*args, **kwargs)(f)

        @functools.wraps(f)
        def wrapper(*viewargs, **viewkw):
            return f(*viewargs, **viewkw)

        return wrapper

    return decorator


class SwaggerViewMixin(abc.ABC):
    """
        set and implement swagger
        can use for view with one method not more
    """
    _swagger_inited = False
    permission_classes_any = None
    swagger_tags = None
    swagger_title = None
    swagger_description = None
    swagger_response_code = 200
    swagger_serializer = None
    serializer = None
    serializer_response = None
    _security = None
    _responses = None

    def __init_subclass__(cls, **kwargs):
        cls._initial_swagger()

    @classmethod
    def _initial_swagger(cls):
        if cls._swagger_inited:
            return

        assert type(cls.swagger_title) == str, '`swagger_title` field must be string not %s' % type(cls.swagger_title)

        cls._swagger_inited = True
        cls.swagger_description = (cls.__doc__ or '').strip()

        def add_perm_roles(perms, sign):

            roles = []
            for perm in perms:
                rpr = getattr(perm, 'repr', None)
                if not rpr or not callable(rpr):
                    continue
                roles.append(rpr())
                roles.append(sign)

            roles_doc = ' '.join(roles).strip(sign)
            # add user roles to description
            if roles:
                cls.swagger_description += """
                    <br>
                    <br>
                    <b>permissions_required</b> = <mark>[%s]</mark>
                """.strip() % roles_doc

        if cls.permission_classes_any:
            add_perm_roles(cls.permission_classes_any, 'OR')

        permission_classes = getattr(cls, 'permission_classes', None)
        if permission_classes and not cls.permission_classes_any:
            add_perm_roles(permission_classes, 'AND')
        else:
            cls._security = []

        # prepare responses
        cls._responses = {
            cls.swagger_response_code: cls.serializer_response or cls.serializer
        }

        _get_view = getattr(cls, 'get', None)
        _post_view = getattr(cls, 'post', None)
        _put_view = getattr(cls, 'put', None)
        _delete_view = getattr(cls, 'delete', None)

        view = _get_view or _post_view or _put_view or _delete_view
        if not view:
            raise AttributeError('You must define one of http methods')

        additional_context = {}
        if view == _get_view:
            additional_context['query_serializer'] = cls.swagger_serializer or cls.serializer
        else:
            additional_context['request_body'] = cls.swagger_serializer or cls.serializer

        swagger_schema(operation_id=cls.swagger_title, operation_description=cls.swagger_description,
                       security=cls._security,
                       responses=cls._responses,
                       tags=cls.swagger_tags, **additional_context)(view)