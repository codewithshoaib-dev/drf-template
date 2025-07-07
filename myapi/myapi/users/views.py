from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import permissions

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.hashers import make_password


from .emails.services import send_reset_email
from .JWTAuthentication import CustomCookieJWTAuthentication
from .serializers import (CustomTokenObtainPairSerializer, 
                         UserRegisterSerializer,
                         UserInfoSerializer, 
                         PasswordResetRequestSerializer,
                         PasswordResetConfirmSerializer)


User = get_user_model()

token_generator = PasswordResetTokenGenerator()

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'status': 'success',
                'message': 'User registered successfully.',
                
            }, status=status.HTTP_201_CREATED)

        else:
            return Response({
                'status': 'error',
                'message': 'Registration failed.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
       serializer = CustomTokenObtainPairSerializer(data=request.data)

       if serializer.is_valid():
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)

            response = Response({
                'status': 'success',
                'message': 'Login successful.',

            }, status=status.HTTP_200_OK)
            
            response.set_cookie(key='access_token', value=str(refresh.access_token),
                                httponly=True, samesite='Lax', secure=False)
            response.set_cookie(key='refresh_token', value=str(refresh), 
                                httponly=True, samesite='Lax', secure=False)

            return response

       return Response({
            'status': 'error',
            'message': 'Invalid login credentials.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserInfoView(APIView):
   authentication_classes = [CustomCookieJWTAuthentication]
   permission_classes=[permissions.IsAuthenticated]


   def get(self, request):
       serializer = UserInfoSerializer(request.user)
       print(serializer.data)
       return Response(serializer.data)


class CookieTokenRefreshView(APIView):
    permission_classes=[AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        print(refresh_token)
        if refresh_token is None:
             return Response({
                'status': 'error',
                'message': 'Refresh token missing.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
           refresh = RefreshToken(refresh_token)  
           new_refresh_token = str(refresh) 
           new_access_token = str(refresh.access_token)

        except Exception:
            return Response({
                'status': 'error',
                'message': 'Invalid refresh token.'
            }, status=status.HTTP_401_UNAUTHORIZED)


        response = Response({
            'status': 'success',
            'message': 'Token refreshed successfully.'
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            key='refresh_token',
            value=new_refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=60000,  
        )
        response.set_cookie(
            key='access_token',
            value=new_access_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=3000,  
        )

        return response



class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        response = Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        
        
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        
        return response
  


class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user = User.objects.filter(email__iexact=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)
            reset_link = f"{settings.FRONTEND_RESET_URL}/{uid}/{token}"
            send_reset_email(user.email, reset_link)

        return Response(
            {'message': 'If the email exists in our system, a password reset link has been sent.'},
            status=status.HTTP_200_OK
        )



class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        if not token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(password)
        user.save()

        return Response({'message': 'Password successfully reset.'}, status=status.HTTP_200_OK)
