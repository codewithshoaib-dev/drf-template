from rest_framework import generics
from rest_framework.views import APIView
from .serializers import UserLoginSerializer, UserRegisterSerializer, UserInfoSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


User = get_user_model()

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Validation Errors:", serializer.errors)  # Debugging output
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
       serializer = UserLoginSerializer(data=request.data)

       if serializer.is_valid():
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)
            response = Response()
            
            response.set_cookie(key='access_token', value=str(refresh.access_token),
                                httponly=True, samesite='Lax', secure=False)
            response.set_cookie(key='refresh_token', value=str(refresh), 
                                httponly=True, samesite='Lax', secure=False)

            return response
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserInfoView(APIView):
   authentication_classes = []
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
            return Response({'detail': 'Refresh token missing'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
           refresh = RefreshToken(refresh_token)  
           new_refresh_token = str(refresh) 
           new_access_token = str(refresh.access_token)

        except Exception:
            return Response({'detail': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({'detail': 'Token refreshed'}, status=status.HTTP_200_OK)

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
            max_age=300,  
        )

        return response



class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        response = Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        
        
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        
        return response
