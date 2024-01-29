from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User
from my_login_app.models import UserProfile
import sys
from openai import OpenAI
client = OpenAI(api_key='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')

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
   


def message_response(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            received_message = request.POST.get('chat-input1','')
            received_role= request.POST.get('role')
            # print(received_message)
            #  return HttpResponse(received_message)

            original_message= received_role + ' And  ' + received_message
            print(original_message)

            response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={ "type": "json_object" },
            messages=[
                            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                            {"role": "user", "content": original_message}
                                    ]
                                )

            response_string = response.choices[0].message.content
            # Assuming the response string is formatted like a JSON object, let's parse it.
            # Remove the curly braces at the beginning and end, then replace escaped newlines and quotes
            formatted_response = response_string.strip("{}").replace('\\n', '<br>').replace('\\"', '"').replace('\n','<br>')

            #save chat history on backend
            user_message = original_message
            bot_response = formatted_response
            ChatHistory.objects.create(user=request.user, message=user_message, response=bot_response)


            # Return the formatted string, marked as safe to render as HTML
            return render(request, 'my_login_app/response.html', {'response': formatted_response})
    
    else:
            return render(request,'my_login_app/login.html')