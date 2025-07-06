from rest_framework import serializers
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate, get_user_model
from django.utils.html import escape
from rest_framework.response import Response


User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
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
        

    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data['username']
        password = data['password']

        if username is None or password is None:
            raise serializers.ValidationError('Both fields are required.')

        user = authenticate(username=username, password=password)

        if user:
            data['user'] = user
            return data
           
        raise serializers.ValidationError('Invalid Credentials')


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
        ]
