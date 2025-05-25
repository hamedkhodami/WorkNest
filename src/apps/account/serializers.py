from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField

from .exceptions import NationalIdNotMatch
from apps.core import serializers as core_serializers
from .auth import utils
from . import models, exceptions, text
from .enums import UserRoleEnum


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):

    referral = serializers.CharField(max_length=8, required=False)
    otp_code = serializers.CharField()

    class Meta:
        model = models.User
        fields = (
            'phone_number','email','first_name','last_name','role','national_id'
        )

    def validate_national_id(self, national_id):
        return self.national_id_is_not_valid(national_id)

    def national_id_is_not_valid(self, national_id):
        if not utils.is_melli_code(national_id):
            raise exceptions.NationalIdIsNotValid

        phone_number = self.initial_data.get('phone_number')
        if not phone_number:
            raise exceptions.PhoneNumberIsNotValid

        if not models.User.national_id_check_by_data(phone_number, national_id):
            raise exceptions.NationalIdNotMatch

        return national_id

    def create(self, validated_data):
        validated_data = validated_data.copy()
        validated_data.pop('otp_code', None)
        validated_data.pop('referral', None)

        user = self.Meta.model(**validated_data, is_phone_number_confirmed=True, is_national_id_confirmed=True)
        if not user.national_id_check(user.phone_number, user.national_id):
            raise exceptions.PhoneNumberIsNotMatchWithNationalId

        password = validated_data.get('password')
        if password:
            user.set_password(password)
        else:
            raise ValueError(text.required_phone_number)

        user.save()
        return user


class TokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user_role = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class AccessTokenSerializer(serializers.Serializer):
    access = serializers.CharField()


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(region='IR')


class LoginOTPSerializer(PhoneNumberSerializer, serializers.Serializer):
    code = serializers.CharField()


class ConfirmPhoneNumberSerializer(serializers.Serializer):
    code = serializers.CharField()


class ResetPasswordCheckSetPasswordSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(region='IR')
    code = serializers.CharField()
    password = serializers.CharField()


class UserCreateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=UserRoleEnum.choices)
    otp_code = serializers.CharField()

    class Meta:
        model = models.User
        fields = ('phone_number', 'email', 'first_name', 'last_name', 'role', 'national_id')

    def create(self, validated_data):
        validated_data = validated_data.copy()
        validated_data.pop('otp_code', None)

        user = self.Meta.model(
            **validated_data,
            is_phone_number_confirmed=True,
            is_national_id_confirmed=True
        )

        if not user.national_id_check(user.phone_number, user.national_id):
            raise exceptions.PhoneNumberIsNotMatchWithNationalId

        password = validated_data.get('password')
        if password:
            user.set_password(password)
        else:
            raise ValueError(text.required_phone_number)

        user.save()
        return user


class UserCreateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'created_at')


class UserListSerializer(core_serializers.ListParamsSerializer, core_serializers.FilterByDateSerializer,
                         serializers.Serializer):

    BLOCK_STATUS = (
        'all',
        'true',
        'false'
    )

    ROLE = (
        'all',
        *UserRoleEnum
    )

    ACTIVATE_STATUSES = (
        'all',
        'true',
        'false'
    )

    search = serializers.CharField(required=False, help_text='search by phone_number or full name')
    fb_role = serializers.ChoiceField(choices=ROLE, required=False, default='all',
                                      help_text='filter by role name')
    fb_activate_status = serializers.ChoiceField(choices=ACTIVATE_STATUSES, required=False, default='all',
                                                 help_text='filter by active status user')
    fb_phone_number_confirm_status = serializers.BooleanField(required=False,
                                                             help_text='filter by phone_number confirm status')

    fb_block_status = serializers.ChoiceField(BLOCK_STATUS, default='all', help_text='filter by user is blocked or not')


class UserListDataResponseSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(UserRoleEnum)
    is_blocked = serializers.SerializerMethodField()

    def get_is_blocked(self, user):
        return user.is_blocked

    class Meta:
        model = models.User
        fields = ('id', 'created_at', 'updated_at',
                  'first_name', 'last_name', 'phone_number', 'is_active', 'role', 'is_blocked')


class UserListResponseSerializer(core_serializers.ListSerializer):
    data = UserListDataResponseSerializer(many=True)


class UserDetailSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=False)


class UserDetailBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'email', 'role', 'first_name', 'last_name', 'phone_number')


class UserDetailBasicByOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'first_name', 'last_name')


class UserDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id',)



#---------------------------------------------------------------------------



class UserBlockSwaggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserBlock
        exclude = ('user', 'admin')


class UserBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserBlock
        fields = '__all__'


class UserUnBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserBlock
        fields = ('id',)


class UserBlockDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserBlock
        fields = '__all__'



#---------------------------------------------------------------------------




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfileModel
        fields = '__all__'

class UserProfileDetailSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = models.UserProfileModel
        fields = '__all__'

    def get_profile_picture_url(self, obj):
        return obj.get_profile_picture_url()

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfileModel
        exclude = ('user',)

class UserProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfileModel
        fields = ('image',)

class UserProfilePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfileModel
        fields = ('bio', 'image', 'city', 'degree')

class UserProfileMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfileModel
        fields = ('user', 'gender', 'bio')

class UserProfileSkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfileModel
        fields = ('skills',)




