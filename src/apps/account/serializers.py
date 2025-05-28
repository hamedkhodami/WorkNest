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


class UserListDataResponseSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(UserRoleEnum)
    is_blocked = serializers.SerializerMethodField()

    def get_is_blocked(self, user):
        return user.is_blocked

    class Meta:
        model = models.User
        fields = ('id', 'created_at', 'updated_at',
                  'first_name', 'last_name', 'phone_number', 'is_active', 'role', 'is_blocked')


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


class UserProfileListResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    results = UserProfileSerializer(many=True)


class UserProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfileModel
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')


        if not request or not request.user.is_authenticated:
            data.pop('email', None)
            data.pop('phone_number', None)
        return data


class UserProfileDetailResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    data = UserProfileDetailSerializer()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfileModel
        exclude = ('user',)


class UserProfileUpdateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    updated_data = UserProfileUpdateSerializer()




