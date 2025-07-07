from rest_framework import serializers
from rest_framework.response import Response

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate, get_user_model
from django.utils.html import escape

from .backends import UsernameOrEmailBackend

backend = UsernameOrEmailBackend()
User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    class Meta:
       
        model = User
        fields = [
            'username',
            'email',
            'password'
        ]

    def clean_username(self, value):
        return escape(value.strip())

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError('Usernname must be at least 3 characters.')
        return value
    
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
        

    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username_or_email'

    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')

        if username_or_email and password:
            user = backend.authenticate(
                request=self.context.get('request'),
                username=username_or_email,
                password=password
            )
            if not user:
                raise serializers.ValidationError(_('Invalid credentials.'))
            
            attrs['user'] = user
            

            return attrs

        else:
            raise serializers.ValidationError(_('Must include Username or Email and Password.'))

        

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6)



class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
        ]

        read_only_fields = fields