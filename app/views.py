from contextvars import Token
import json
import jwt
import logging
from django.contrib.auth.models import User, Group
from django.forms import EmailField
# from app.encrypt_decrypt import decrypt, encrypt
from app.serializers import *
from app.serializers import USER_Serializer
from django.views import View
from django.http import JsonResponse
from rest_framework import status
from project import settings
from django.shortcuts import get_object_or_404, get_list_or_404, render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView,ListCreateAPIView
from rest_framework.response import Response
from .models import *
from .models import USER_details
from django.contrib.auth import authenticate
from django.db.models import Q
from django.http import HttpResponse
import pymongo
import datetime
from .backends import EmailBackend
from datetime import datetime, timedelta
from rest_framework.exceptions import AuthenticationFailed
from bson import ObjectId
from .permissions import CustomIsauthenticated
from django.contrib.auth.hashers import make_password, check_password
from django.utils.decorators import method_decorator
from .utils import token_required
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
JWT_SECRET_KEY = 'vqua1i2qh8&i!w&mfkeo^uex0v*(u)08x-x!q)ggv!+k94rxxy'
JWT_ACCESS_TOKEN_EXPIRATION = 60
JWT_REFRESH_TOKEN_EXPIRATION = 1440
JWT_ALGORITHM = 'HS256'

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient['ambulance_data']
mycol3 = mydb['app_user_details']
mytokens = mydb['tokens']


import secrets
    

# logger = logging.getLogger("django_service.service.views")
logger = logging.getLogger("django")


class Register(APIView):
    def post(self, request, format=None):
        serializer = USER_Serializer(data=json.loads(request.body))
        # import pdb;pdb.set_trace()
        if serializer.is_valid():
            data = serializer.validated_data
            password = data['password']
            hased_password = make_password(password)
            email = data['email']
            existing_user = USER_details.objects.filter(email=email).first()
            if existing_user is not None:
                logger.warning("Email already exists")
                return JsonResponse({'Message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.error(f"Invalid data submitted: {serializer.errors}")

                serializer.save(password=hased_password)
                logger.info('User created successfully:%s',email)
                return JsonResponse({'Message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        else:
            logger.error("An error occurred while processing the request")
            return JsonResponse(serializer.errors , status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self,request):
        data = request.data
        email = data.get('email',None)
        password = data.get('password',None)
        user=EmailBackend.authenticate(self, request, username=email, password=password)
        if user is not None:
            token_payload = {
                'user_id': str(user._id),
                'exp': datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRATION),
                'iat': datetime.utcnow()
                }
            access_token = jwt.encode(token_payload, JWT_SECRET_KEY, JWT_ALGORITHM)

            refresh_token_payload = {
                'user_id': str(user._id),
                'exp': datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRATION),
                'iat': datetime.utcnow()
                }
            refresh_token = jwt.encode(refresh_token_payload, JWT_SECRET_KEY, JWT_ALGORITHM)

            mytokens.insert_one({
                "user_id":str(user._id),
                "access_token":access_token,
                "refresh_token":refresh_token,
                "active":True,
                "created_date":datetime.utcnow()
            })

            details = mycol3.find_one({"email":email})
            logedin = details['logged_in']
            user    = details['user']
            logger.info({"user successfully authenticated: %s",email})
            return JsonResponse({
                    "status": "success",
                    "msg": "user successfully authenticated",
                    "token": access_token,
                    "refresh_token": refresh_token,
                    "user":user,
                    "loggedin":logedin
                })
        else:
            logger.error(f"invalid data")
            return JsonResponse({"message":"invalid data"})
       
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["ambulance_data"]
my_col4=mydb["app_user_details"]
class ChangePassword(CreateAPIView):
    permission_classes = [CustomIsauthenticated]
    @method_decorator(token_required)
    def post(self,request):
        user_id= ObjectId(request.user._id)
        user = my_col4.find_one({"_id":user_id}) 
        data = request.data
        email = user['email']
        oldpassword = data['password']
        newpassword = data['newpassword']
        try:
            user_obj = USER_details.objects.get(email=email)
        except USER_details.DoesNotExist:
            logger.warning("User not found")
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if not check_password(oldpassword, user_obj.password):
            logger.warning("Invalid old password")
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
            
        user_obj.password=make_password(newpassword)
        user_obj.save()

        logger.info("Password changed successfully")
        return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)


class NewPassordGenerate(CreateAPIView):
    def post(self,request):
        data = request.data
        email = data['email']
        oldpassword = data['password']
        newpassword = data['newpassword']
        try:
            user_obj = USER_details.objects.get(email=email)
        except USER_details.DoesNotExist:
            logger.warning("User not found")
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if not check_password(oldpassword, user_obj.password):
            logger.warning("Invalid old password")
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
            
        user_obj.password=make_password(newpassword)
        user_obj.save()

        logger.info("Password changed successfully")
        return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)
    
from rest_framework.exceptions import APIException

class LogoutView(APIView):
    permission_classes = [CustomIsauthenticated]

    def post(self, request):
        try:
            user_id = request.user._id
            auth_header = request.headers.get('Authorization')
            
            if auth_header is None:
                logger.info(f"Authorization header is missing")

                raise APIException("Authorization header is missing")

            a_token = auth_header.split()[1]
            user_data = mytokens.find({})  # here we are getting all token collection information
            information = []
            
            for info in user_data:
                if (datetime.utcnow() - info['created_date']).days >= 1:
                    # if token created date is greater than or equal to 1 day, remove the token from collection
                    information.append(info['_id'])

            mytokens.remove({"_id": {"$in": information}})
            
            mytokens.update(
                {"user_id": str(user_id), "access_token": a_token},
                {"$set": {"active": False}}
            )
            logger.info("logout successfully")
            return Response('Logout successfully')
        
        except KeyError as e:
            logger.error(f"KeyError: {str(e)}")
            raise APIException(f"KeyError: {str(e)}")
        
        except IndexError as e:
            logger.error(f"IndexError: {str(e)}")
            raise APIException(f"IndexError: {str(e)}")
        
        except Exception as e:
            logger.error(str(e))
            raise APIException(str(e))



def generate_otp(length=6):
        """Generates a random OTP of the specified length."""
        return secrets.token_hex(length // 2 + 1)[:length]


class ForgotPassword(APIView):
    def post(self,request):
        data= request.data
        email=data["email"]
        try:
            user_obj = USER_details.objects.get(email=email)
        except USER_details.DoesNotExist:
            logger.info({'error': 'Email doesn\'t exist'})
            return Response({'error': 'Email doesn\'t exist'}, status=status.HTTP_404_NOT_FOUND)
        if user_obj is not None:
            otp = generate_otp()
            hased_password = make_password(otp)
            mycol3.update(
                    {"email": email},
                    {
                        "$set": {"password":hased_password}
                    }
                )
            email_msg = EmailMessage(
            'Email Details',
            f"RESET PASSWORD \n Hey there!\n It looks like you are trying to reset password.\n\nYOUR NEW LOGIN DETAILS:\n password: {otp}\n Email: {email}",
            settings.EMAIL_HOST_USER,
            [email],
            )
            email_msg.send(fail_silently=True)
            logger.info({"New password generated successfully"})
            return Response({"message":"New password generated successfully and send to your respective mail id"})
        else:
            logger.info({"invalid data"})
            return JsonResponse({"message":"invalid data"})
        
    


