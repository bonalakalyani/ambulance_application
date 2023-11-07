import json 
from django.urls import reverse
import pymongo 
from rest_framework import status 
from rest_framework.test import APITestCase
from app.backends import EmailBackend
from app.models import USER_details
import jwt
JWT_SECRET_KEY = 'vqua1i2qh8&i!w&mfkeo^uex0v*(u)08x-x!q)ggv!+k94rxxy'
JWT_ACCESS_TOKEN_EXPIRATION = 60
JWT_REFRESH_TOKEN_EXPIRATION = 1440
JWT_ALGORITHM = 'HS256'



class RegisterTests(APITestCase):
    """
    test api url's
    """
    register_url=reverse("Register")
    login_url=reverse("LoginView")



    def setUp(self):
        self.user=USER_details.objects.create(email='admin@gmail.com',password='admin')
        # self.access_token = access_token.objects.create(user=self.user, token='your_token_value')



    def test_register_new_user(self):

        url =reverse('Register')
        data={
            "email":"ganesh77@gmail.com",
            "password":"ganesh"
            }
        response=self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), {"Message": "User created successfully"})

    def test_register_exitisting_user_with_email(self):
        existing_user=USER_details.objects.create(
                                         email="santhoshkumardhavala@gmail.com",
                                         password="Santhu@123"
                                        )
        url=reverse('Register')
        data={
            "email":"santhoshkumardhavala@gmail.com",
            "password":"santhu"
        }
        response=self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content),{'Message': 'Email already exists'})

    def test_register_invalid_data(self):
        url=reverse('Register')
        data={
            'email':"kalyani@gmail.com",
            "password":""
        }
        response=self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content),{"password": ["This field may not be blank."]})

    def test_login_with_invalid_data(self):
        url=reverse("LoginView")
        data={
            "email":"ganesh@gmail.com",
            "password":"ganesh"
            }
        response=self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content),{"detail": "Email is not valid"})


    def test_login_new_user(self):
        self.user=USER_details.objects.create(email='admin@gmail.com',password='admin')
        response = self.client.post(self.login_url, {"email":"admin@gmail.com","password":"admin"})
        print(response.content)
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient['svg_data']
mycol3 = mydb['app_user_details']
mytokens = mydb['tokens']



# class LoginViewTests(APITestCase):
#     def test_login_with_valid_credentials(self):
#         url = reverse('LoginView')  # Replace 'login' with the actual URL name for the login endpoint
#         data = {
#             "email": "chintu8761@gmail.com",
#             "password": "Chintu1443"
#         }
#         response = self.client.post(url,data,format='json')
#         print(response,"***************")
#         self.assertEqual(response.status_code, 200)
        
#         # Retrieve the access_token from the response
#         response_data = response.json()
#         access_token = response_data.get('access_token')
        
#         # Assert that the access_token is not empty
#         self.assertIsNotNone(access_token)
#         access_token = response_data.get('access_token')
#         print(access_token,"**********************")
        
#         # Additional assertions or actions based on the access_token
#         user=EmailBackend.authenticate(self, username='chintu8761@gmail.com', password="Chintu1443")

#         # Example: Retrieve the stored MyTokens instance and assert its values
#         my_token = mytokens.find_one({"access_token":access_token})
#         self.assertEqual(my_token.user_id, str(user._id))
#         self.assertEqual(my_token.access_token, access_token)
#         self.assertEqual(my_token.refresh_token, response_data.get('refresh_token'))
#         self.assertTrue(my_token.active)
        
#         # Additional assertions or actions based on the MyTokens instance
        
