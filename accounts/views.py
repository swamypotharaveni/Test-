import logging
from django.shortcuts import render
from rest_framework import status,response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework .permissions import AllowAny,IsAuthenticated,IsAdminUser
from django.contrib.auth.models import User
from.serializer import UserSerializer
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from rest_framework.response import Response
from django.utils.crypto import get_random_string
import random
from.models import Profile
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
# Create your views here.
# Create the logger
logger = logging.getLogger(__name__)

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
#login view
    @action(detail=False,methods=['POST'],permission_classes=[AllowAny,])
    def login(self,request):
        username=request.data.get("username",None)
        password=request.data.get("password",None)
        user=authenticate(username=username,password=password)
        if(user):
            seriliaer=UserSerializer(user)
            token,created=Token.objects.get_or_create(user=user)
            data=seriliaer.data
            data["token"]=token.key
            user.last_login=timezone.now()
            user.save()
            return response.Response({"users":data},status=status.HTTP_200_OK)
        return response.Response({"details":"invalid details"},status=status.HTTP_400_BAD_REQUEST)
    #logout view
    @action(detail=False,methods=['POST'],permission_classes=[IsAuthenticated])
    def logout(self,request):
        """Logout user by deleting their auth token"""
        username = request.user.username 
        if(request.auth):
            request.auth.delete()
        logger.info(f"User '{username}' logged out.")

        return response.Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    @action(detail=False,methods=['POST'],permission_classes=[AllowAny,])
    def register(self,request):
         # Get the data from the request
        username=request.data.get("username",None)
        password=request.data.get("password",None)
        email=request.data.get("email",None)
         # Validate required fields
        if not username:
            return Response({"error": "Username is required!"}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({"error": "Password is required!"}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({"error": "Email is required!"}, status=status.HTTP_400_BAD_REQUEST)
         # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists!"}, status=status.HTTP_400_BAD_REQUEST)
         # Serialize the data and check for validity
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
             # Save the user and return success response
            user=serializer.save()
            user.set_password(password)
            user.save()
            return response.Response(serializer.data,status=status.HTTP_201_CREATED)
           # If serializer is invalid, return errors
        return response.Response({"erro":"new"},serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    #get all users
    @action(detail=False,methods=['GET'],permission_classes=[IsAuthenticated])
    def GetAllUsers(self,request):
        print(request.user)
        # Querying all users
        users=User.objects.all()
        #seriliging the query set
        seriliaer=UserSerializer(users,many=True)
        return response.Response(seriliaer.data,status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['DELETE'], permission_classes=[IsAuthenticated])
    def deleteuser(self, request, pk=None):
        try:
            # Attempt to retrieve the user by primary key
            user = User.objects.get(pk=pk)
             # Check permissions:
             # - Admin/superuser can delete anyone
             # - Normal user can only delete their own account
            if not request.user.is_superuser and user != request.user:
                return Response(
                {"error": "You are not allowed to delete this user."},
                status=status.HTTP_403_FORBIDDEN
            )
            

            user.delete()  # Delete the user
            return Response({"message": f"User {user.username} deleted successfully", "id": pk}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            # Return an error if the user does not exist
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
class PasswordChange(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        
        old_password=request.data.get("old_password",None)
        password=request.data.get("password",None)
        confirm_password=request.data.get("confirm_password",None)

        try:
            user=User.objects.get(username=request.user)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        #validte old password
        if not user.check_password(old_password):
            return Response({"detail": "old  password is not correct."}, status=status.HTTP_404_NOT_FOUND)
        #match Check
        if password!=confirm_password:
            return Response({"detail": " password and confirm password not match"}, status=status.HTTP_404_NOT_FOUND)
        # Prevent using the same password again

        # if user.check_password(password):
        #     return Response({"detail": "New password cannot be the same as the old password."}, status=status.HTTP_404_NOT_FOUND)
        if old_password == password:
            return Response({"detail": "New password cannot be the same as the old password."}, status=status.HTTP_404_NOT_FOUND)
        #set and save the db
        user.set_password(password)
        user.save()
        return Response({"detail": "Password has been successfully updated."}, status=status.HTTP_200_OK)
    
class ForgotPasswordOTP(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        email=request.data.get("email",None)
        if email is None:
            return Response({"detail": "Email is required!"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Email Not Found !"}, status=status.HTTP_400_BAD_REQUEST)
        # if not user.profile.is_otp_expired():
        #     remaining = user.profile.otp_expiry_remaining()
        #     return Response(
        #         {"detail": f"OTP already sent. Please wait {remaining} minutes."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        if not user.profile.can_request_otp():
            return Response({"detail": "Daily OTP request limit reached. Try again tomorrow."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS)
            
        otp=random.randint(10000,99999)
        user.profile.otp=otp
        user.profile.otp_created_at=timezone.now()
        user.profile.increment_otp_count()
        user.profile.save()
        
        #add the email configation send  otp 
        # send_mail( # type: ignore
        #     subject='Your OTP for password reset',
        #     message=f'Your OTP is {otp}. It will expire in 5 minutes.',
        #     from_email='noreply@example.com',
        #     recipient_list=[user.email],
        # )
    
        return Response({"detail": "OTP sent to your email."}, status=status.HTTP_200_OK)
class ResetPasswordWithOTP(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")
        if password != confirm_password:
            return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            profile = user.profile
        except User.DoesNotExist:
            return Response({"detail": "Invalid email."}, status=status.HTTP_404_NOT_FOUND)
        if not profile.otp:
            return Response({"detail": "OTP has not been generated yet. Please request an OTP first."}, status=status.HTTP_400_BAD_REQUEST)
        if profile.is_otp_expired():
            print(profile.is_otp_expired(),profile.otp_created_at)
            return Response({"detail": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)
        if profile.otp != otp:
            print(type(profile.otp))
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        profile.otp = None
        profile.otp_created_at = None
        profile.save()
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)




    

class Profile(APIView):
     def post(self, request):
         pass
