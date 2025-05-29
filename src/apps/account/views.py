from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions as base_permissions
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView as _TokenObtainPairView,
    TokenRefreshView as _TokenRefreshView,
)

from drf_yasg.utils import swagger_auto_schema

from apps.core.views import mixins
from apps.core.swagger import mixins as ms
from apps.core import utils, redis_utils
from apps.core.exceptions import ValidationError, OperationHasAlreadyBeenDoneError

from . import serializers, models, exceptions, text
from .auth import permissions as per


User = get_user_model()



class TokenRefresh(ms.SwaggerViewMixin, _TokenRefreshView):
    """
        get access token by refresh token(update login)
    """
    swagger_title = 'Token refresh'
    swagger_tags = ['Account']
    serializer_response = serializers.AccessTokenSerializer
    permission_classes = (base_permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        return super(TokenRefresh, self).post(request, *args, **kwargs)


class LoginBasic(ms.SwaggerViewMixin, _TokenObtainPairView):
    """
        Get token pair (access & refresh tokens)
    """
    swagger_title = 'Login basic by raw password'
    swagger_tags = ['Account']
    serializer_response = serializers.TokenResponseSerializer
    permission_classes = (base_permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        resp = super(LoginBasic, self).post(request, *args, **kwargs)

        phone_number = request.data.get('phone_number')
        try:
            user = get_user_model().objects.get(phone_number=phone_number)
            resp.data['user_role'] = user.role
        except get_user_model().DoesNotExist:
            resp.data['user_role'] = None

        return resp


class LoginOTP(APIView):
    """View to handle OTP-based authentication"""

    parser_classes = (base_permissions.AllowAny,)

    @swagger_auto_schema(
        tags=['Account'],
        operation_id='Login OTP: Send Code',
        security=[],
        query_serializer=serializers.PhoneNumberSerializer,
        responses={200: serializers.MessageSerializer}
    )
    def get(self, request):
        """Handles OTP code generation & sending"""
        ser = serializers.PhoneNumberSerializer(data=request.GET)
        ser.is_valid(raise_exception=True)

        phone_number = ser.validated_data['phone_number']
        try:
            user = User.objects.get(phone_number=phone_number, is_active=True)
        except ObjectDoesNotExist:
            raise exceptions.UserNotFound

        conf = settings.LOGIN_OTP_CONFIG
        user_key = conf['STORE_BY'].format(phone_number)

        if redis_utils.get_value(user_key):
            raise exceptions.CodeHasAlreadyBeenSent

        otp_code = utils.random_num(conf['CODE_LENGTH'])
        redis_utils.set_value_expire(user_key, otp_code, conf['TIMEOUT'])

        # TODO: Implement notification system

        res = {'message': text.otp_code_sent}
        return Response(serializers.MessageSerializer(res).data)

    @swagger_auto_schema(
        tags=['Account'],
        operation_id='Login OTP: Verify Code & Get Tokens',
        request_body=serializers.LoginOTPSerializer,
        operation_description='Get token pair (access & refresh tokens)',
        security=[],
        responses={200: serializers.TokenResponseSerializer}
    )
    def post(self, request, *args, **kwargs):
        """Handles OTP verification & token retrieval"""
        ser = serializers.LoginOTPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        phone_number = ser.validated_data['phone_number']
        user_code = ser.validated_data['code']

        try:
            user = User.objects.get(phone_number=phone_number, is_active=True)
        except ObjectDoesNotExist:
            raise exceptions.UserNotFound

        conf = settings.LOGIN_OTP_CONFIG
        user_key = conf['STORE_BY'].format(phone_number)

        code = redis_utils.get_value(user_key)
        if not code or code != user_code:
            raise exceptions.CodeIsWrong

        redis_utils.remove_key(user_key)

        # TODO: Implement notification system

        tokens = RefreshToken.for_user(user)
        response_data = {
            'refresh': str(tokens),
            'access': str(tokens.access_token),
            'user_role': user.role
        }
        return Response(serializers.TokenResponseSerializer(response_data).data)


class Logout(ms.SwaggerViewMixin, APIView):
    """
        need to destroy access token from client side
    """
    swagger_title = 'Logout'
    swagger_tags = ['Account']
    serializer = serializers.RegisterSerializer
    serializer_response = serializers.MessageSerializer

    def post(self, request, *args, **kwargs):

        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        refresh_token = ser.validated_data['refresh']
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            pass
        return Response(serializers.MessageSerializer({'message': 'bye...'}).data)


class Register(ms.SwaggerViewMixin, APIView):
    """
        Register user and return user tokens
    """
    swagger_title = 'Register user'
    swagger_tags = ['Account']
    swagger_response_code = 201
    permission_classes = (base_permissions.AllowAny,)
    serializer = serializers.RegisterSerializer
    serializer_response = serializers.TokenResponseSerializer

    @transaction.atomic
    def post(self, request):
        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        # check OTP
        phone_number = ser.validated_data['phone_number']
        otp_code = ser.validated_data['otp_code']
        conf = settings.USER_OTP_CONFIG
        user_key = conf['STORE_BY'].format(phone_number)

        #check key
        redis_otp = redis_utils.get_value(user_key)
        if not redis_otp or redis_otp != otp_code:
            raise exceptions.CodeIsWrong

        # create user
        user = ser.save()

        # create jwt tokens
        tokens = RefreshToken.for_user(user)
        tokens_dict = {
            'refresh': str(tokens),
            'access': str(tokens.access_token),
            'user_role': user.role
        }

        # TODO: Implement notification system

        return Response(self.serializer_response(tokens_dict).data, status=status.HTTP_201_CREATED)


class ResetPassword(ms.SwaggerViewMixin, APIView):
    """
        reset password
        create and send reset code
    """
    swagger_title = 'Reset password send code'
    swagger_tags = ['Account']
    permission_classes = (base_permissions.AllowAny,)
    serializer = serializers.PhoneNumberSerializer
    serializer_response = serializers.MessageSerializer

    def post(self, request):
        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        phone_number = ser.validated_data['phone_number']
        # get user
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise exceptions.UserNotFound

        conf = settings.RESET_PASSWORD_CONFIG
        user_key = conf['STORE_BY'].format(phone_number)

        # check user request(if have previous request)
        if redis_utils.get_value(user_key):
            # reset code has already been sent
            raise exceptions.CodeHasAlreadyBeenSent

        # generate and set code on redis
        reset_code = utils.random_num(conf['CODE_LENGTH'])
        redis_utils.set_value_expire(user_key, reset_code, conf['TIMEOUT'])

        # TODO: Implement notification system


        res = {'message': text.reset_password_send_code}
        return Response(self.serializer_response(res).data)


class ResetPasswordCheckAndSet(ms.SwaggerViewMixin, APIView):
    """
        reset password
        check code and set new password
    """
    swagger_title = 'Reset password check and set'
    swagger_tags = ['Account']
    permission_classes = (base_permissions.AllowAny,)
    serializer = serializers.ResetPasswordCheckSetPasswordSerializer
    serializer_response = serializers.MessageSerializer

    def post(self, request):
        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        phone_number = ser.validated_data['phone_number']
        user_code = ser.validated_data['code']

        # get user
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise exceptions.UserNotFound

        conf = settings.RESET_PASSWORD_CONFIG
        user_key = conf['STORE_BY'].format(phone_number)

        # check reset code
        code = redis_utils.get_value(user_key)
        if not code:
            # reset code not match(is wrong)
            raise exceptions.CodeIsWrong

        if not code == user_code:
            # reset code not match(is wrong)
            raise exceptions.CodeIsWrong

        # clear key
        redis_utils.remove_key(user_key)
        # set password user
        password = ser.validated_data['password']
        user.set_password(password)

        # TODO: Implement notification system

        res = {'message': text.reset_password_successfully}
        return Response(self.serializer_response(res).data)


class ConfirmPhoneNumber(APIView):
    """
        confirm phonenumber
        send code
    """
    serializer_response = serializers.MessageSerializer

    @swagger_auto_schema(
        tags=['Account'],
        operation_id='Confirm phonenumber. send code',
        responses={200: serializers.MessageSerializer}
    )
    def get(self, request):
        user = request.user
        phone_number = user.phone_number

        if user.is_phone_number_confirmed:
            raise OperationHasAlreadyBeenDoneError

        conf = settings.CONFIRM_PHONENUMBER_CONFIG
        user_key = conf['STORE_BY'].format(phone_number)

        # check code request(if have previous request)
        if redis_utils.get_value(user_key):
            # confirm code has already been sent
            raise exceptions.CodeHasAlreadyBeenSent

        code = utils.random_num(conf['CODE_LENGTH'])

        redis_utils.set_value_expire(user_key, code, conf['TIMEOUT'])

        # TODO: Implement notification system

        res = {'message': text.confirm_code_sent}
        return Response(self.serializer_response(res).data)

    @swagger_auto_schema(tags=['Account'],
                         operation_id='Confirm phone_number. check code and confirm',
                         request_body=serializers.ConfirmPhoneNumberSerializer,
                         responses={200: serializers.MessageSerializer})
    def post(self, request):

        ser = serializers.ConfirmPhoneNumberSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        user = request.user
        phone_number = user.phone_number
        user_code = ser.validated_data['code']

        conf = settings.CONFIRM_PHONENUMBER_CONFIG
        user_key = conf['STORE_BY'].format(phone_number)

        # check code
        code = redis_utils.get_value(user_key)

        if not code:
            # confirm code is not exists
            raise exceptions.CodeIsWrong

        if not code == user_code:
            # confirm code is not match(is wrong)
            raise exceptions.CodeIsWrong

        # clear key
        redis_utils.remove_key(user_key)

        # phone_number confirmed
        user.is_phone_number_confirmed = True
        user.save(update_fields=['is_phone_number_confirmed'])

        # TODO: Implement notification system

        res = {'message': text.confirm_phone_number_successfully}
        return Response(self.serializer_response(res).data)


class UserSendOTP(ms.SwaggerViewMixin, APIView):
    """
        send otp code user
    """
    swagger_title = 'Send otp code for user'
    swagger_tags = ['Account']
    serializer = serializers.PhoneNumberSerializer
    serializer_response = serializers.MessageSerializer
    permission_classes = (base_permissions.AllowAny,)

    def post(self, request):
        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        phone_number = ser['phone_number'].value

        try:
            user = models.User.objects.available_users.get(phone_number=phone_number)
            if request.data.get('request_type') == 'register':
                raise exceptions.UserIsExists
        except models.User.DoesNotExist:
            pass  # اگر کاربر وجود نداشت، ادامه فرآیند ارسال OTP

        conf = settings.USER_OTP_CONFIG
        user_key = conf['STORE_BY'].format(phone_number)

        # check key(code)
        if redis_utils.get_value(user_key):
            raise exceptions.CodeHasAlreadyBeenSent

        # generate and set code on redis
        otp_code = utils.random_num(conf['CODE_LENGTH'])
        redis_utils.set_value_expire(user_key, otp_code, conf['TIMEOUT'])

        # TODO: Implement notification system

        res = {'message': text.create_user_otp_sent_code}
        return Response(self.serializer_response(res).data)


class UserCreate(ms.SwaggerViewMixin, APIView):
    """
        create user.
    """
    swagger_title = 'Create user'
    swagger_tags = ['Account']
    swagger_response_code = 201
    permission_classes = (per.IsAdmin,)
    serializer = serializers.UserCreateSerializer
    serializer_response = serializers.UserCreateResponseSerializer

    def post(self, request):
        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        admin = request.user

        validated_data = ser.validated_data
        otp_code = validated_data.get('otp_code')

        # check otp code
        conf = settings.USER_OTP_CONFIG
        user_phone_number = validated_data['phone_number']
        user_key = conf['STORE_BY'].format(user_phone_number)
        if not redis_utils.get_value(user_key) == otp_code:
            raise exceptions.CodeIsWrong

        # clear otp key
        redis_utils.remove_key(user_key)

        # create user
        user = ser.save()

        # TODO: Implement notification system

        return Response(self.serializer_response(instance=user).data, status=status.HTTP_201_CREATED)


class UserDelete(ms.SwaggerViewMixin, mixins.DeleteViewMixin, APIView):
    """
        delete user.
    """
    swagger_title = 'Delete user'
    swagger_tags = ['Account']
    permission_classes = (per.IsAdmin,)
    serializer_response = serializers.UserDeleteSerializer

    def delete(self, request, *args, **kwargs):
        return self.delete_instance(request)

    def get_instance(self):
        try:
            user_id = self.kwargs['user_id']
            return User.base_objects.available_users.get(id=user_id)
        except (User.DoesNotExist, ValidationError):
            raise exceptions.UserNotFound


#---------------------------------------------------------------------------


class UserBlock(ms.SwaggerViewMixin, mixins.CreateViewMixin, APIView):
    """
        user block
    """
    swagger_title = 'Block user'
    swagger_tags = ['Account']
    swagger_serializer = serializers.UserBlockSwaggerSerializer
    swagger_response_code = 201
    serializer = serializers.UserBlockSerializer
    permission_classes = (per.IsAdmin,)

    def post(self, request, *args, **kwargs):
        return self.create(request)

    def additional_data(self):
        user_id = self.kwargs['user_id']
        try:
            user = User.base_objects.available_users.get(id=user_id)
        except (User.DoesNotExist,):
            raise exceptions.UserNotFound
        return {
            'user': user.id,
            'admin': self.request.user.id
        }


class UserUnBlock(ms.SwaggerViewMixin, mixins.DeleteViewMixin, APIView):
    """
        unblock user
    """
    swagger_title = 'Unblock user'
    swagger_tags = ['Account']
    serializer = serializers.UserUnBlockSerializer
    permission_classes = (per.IsAdmin,)

    def delete(self, request, *args, **kwargs):
        return self.delete_instance(request)

    def get_instance(self):
        user_id = self.kwargs['user_id']
        try:
            user = User.base_objects.available_users.get(id=user_id)
            return user.userblock
        except ObjectDoesNotExist:
            raise exceptions.UserIsNotBlocked


class UserBlockDetail(ms.SwaggerViewMixin, mixins.DetailViewMixin, APIView):
    """
        user block detail
    """
    swagger_title = 'Block user detail'
    swagger_tags = ['Account']
    permission_classes = (per.IsAdmin,)
    serializer_response = serializers.UserBlockDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.detail(request)

    def get_instance(self):
        user_id = self.kwargs['user_id']
        try:
            user = User.base_objects.available_users.get(id=user_id)
            return user.userblock
        except ObjectDoesNotExist:
            raise exceptions.UserIsNotBlocked


#---------------------------------------------------------------------------


class ProfileListView(ms.SwaggerViewMixin, mixins.ListViewMixin, APIView):
    """
        profile user list
    """
    permission_classes = (base_permissions.AllowAny,)
    swagger_tags = ['Account']
    swagger_title = 'ListProfiles'
    serializer = serializers.UserProfileSerializer
    serializer_response = serializers.UserProfileListResponseSerializer

    def get_queryset(self):
        return models.UserProfileModel.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        ser = self.serializer(queryset, many=True, context={'request': request})
        response_data = {
            "message": text.success_profile_list,
            "results": ser.data
        }
        return Response(response_data, status=200)


class ProfileDetailView(ms.SwaggerViewMixin, mixins.DetailViewMixin, APIView):
    """
        profile user  detail
    """
    permission_classes = (base_permissions.AllowAny,)
    swagger_tags = ['Account']
    swagger_title = 'ProfileDetail'
    serializer = serializers.UserProfileDetailSerializer
    serializer_response = serializers.UserProfileDetailResponseSerializer

    def get_instance(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(models.UserProfileModel, pk=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        instance = self.get_instance()
        ser = self.serializer(instance, context={'request': request})
        response_data = {
            "message": text.success_profile_list,
            "data": ser.data
        }
        return Response(response_data, status=200)


class ProfileUpdateView(ms.SwaggerViewMixin, mixins.UpdateViewMixin, APIView):
    """
        update profile user
    """
    permission_classes = (per.IsOwnerOrAdmin,)
    swagger_tags = ['Profile']
    swagger_title = 'UpdateProfile'
    serializer = serializers.UserProfileUpdateSerializer
    serializer_response = serializers.UserProfileUpdateResponseSerializer

    def get_instance(self):
        try:
            return models.UserProfileModel.objects.get(pk=self.kwargs.get('pk'))
        except models.UserProfileModel.DoesNotExist:
            raise exceptions.ProfileNotFound()

    def put(self, request, *args, **kwargs):
        instance = self.get_instance()

        if request.user.role != instance.user.role:
            raise exceptions.AccessDenied()

        ser = self.serializer(instance, data=request.data, partial=True, context={'request': request})
        ser.is_valid(raise_exception=True)
        ser.save()

        return Response({
            "message": text.success_profile_update,
            "updated_data": ser.data
        }, status=200)


