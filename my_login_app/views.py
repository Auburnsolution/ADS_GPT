from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User
from my_login_app.models import UserProfile
import sys
from openai import OpenAI
import os


#  fetching from config method.
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)




from pathlib import Path
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from django.contrib.auth import login,logout
from .models import ChatHistory

my_directory=Path(__file__).resolve().parent.parent
sys.path.append(my_directory)


from custom_auth_backend import MyEmailBackend
# Create your views here.
def home(request):
            if request.user.is_authenticated:
                history = ChatHistory.objects.filter(user=request.user).order_by('-timestamp')
                for record in history:
                    record.response = record.response.replace('<br>', '\n')
                return render(request,'my_login_app/home.html',{'history': history})
            else:   
                return render(request,'my_login_app/login.html')
            

def registration_view(request):
    is_registered=False

    if request.method =="POST":
       
        full_name=request.POST.get('full_name')
        password=request.POST.get('password')
        email=request.POST.get('email')


        user=User()
        user.username=full_name
        user.set_password(password)
        user.email=email
        user.save()

        userProfile=UserProfile()
        userProfile.user=user
        userProfile.save()
        is_registered=True





    return render(request,'my_login_app/registration.html',{'is_registered':is_registered})


def logout_view(request):

    logout(request)
    return HttpResponseRedirect(reverse('my_login_app:login'))



def login_view(request):

    if request.user.is_authenticated:
        history = ChatHistory.objects.filter(user=request.user).order_by('-timestamp')
        for record in history:
            record.response = record.response.replace('<br>', '\n')

        return render(request,'my_login_app/home.html',{'history': history})

    else:
        if(request.method =="POST"):

            email=request.POST.get('email')
            password=request.POST.get('password')

            user=MyEmailBackend.authenticate(request=request,username=email,password=password)

            if user:
                if user.is_active:
                    login(request,user)
                    return HttpResponseRedirect(reverse('home'))
                else:
                    return HttpResponse("User is not Active.")

            else:
                return HttpResponse("Wrong login details provided.")



        else:
            return render(request,'my_login_app/login.html')


def profile_view(request):
    userProfile=UserProfile.objects.get(user=request.user)
    
    if request.method=="POST":
        if userProfile:
            profile_name=request.POST.get('name')
            profile_portfolio=request.POST.get('portfolio')
    
            profile_pic=request.FILES['profile_pic']

            
            if request.user.username!=profile_name:
                request.user.username=profile_name

            if userProfile.portfolio!=profile_portfolio:
                userProfile.portfolio=profile_portfolio

            if userProfile.profile_pic!=profile_pic:
                userProfile.profile_pic=profile_pic

            request.user.save()
            userProfile.save()


        
    if userProfile:
        name=userProfile.user.username
        email=userProfile.user.email
        portfolio=userProfile.portfolio

        return render(request,'my_login_app/profile.html',context={'profile_name':name,'profile_email':email,'portfolio':portfolio})
   
    

import json  # Ensure json is imported


def message_response(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            received_message = request.POST.get('chat-input1', '')
            received_role = request.POST.get('role')

            original_message = f"{received_role} And {received_message}"

            # Assuming the OpenAI client is correctly configured beforehand
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                    {"role": "user", "content": original_message}
                ]
            )

            response_string = response.choices[0].message.content
            # Parse the JSON string into a Python dictionary
            response_data = json.loads(response_string)

            # Extract and format only the values from the response_data
            values_only = [str(value).replace('\n', '<br>') for value in response_data.values()]

            # Convert list of values into a single string with HTML line breaks for separation
            bot_response = "<br>".join(values_only)

            # Your logic for managing chat history
            # Save the message and bot_response, manage the chat history as before

            ChatHistory.objects.create(user=request.user, message=original_message, response=bot_response)

            # Retrieve the latest 15 records again after creating the new entry
            history = ChatHistory.objects.filter(user=request.user).order_by('-timestamp')[:15]

            # When displaying, you now have a bot_response that is only values
            # No need for additional processing before rendering in the template

            return render(request, 'my_login_app/response.html', {
                'response': bot_response,  # This is now a string of values only
                'message': original_message,
                'history': history
            })

    else:
        return render(request, 'my_login_app/login.html')

