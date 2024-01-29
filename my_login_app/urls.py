from django.urls import path
from . import views

app_name='my_login_app'

urlpatterns=[
    
    path('',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('profile/',views.profile_view,name='profile'),
    path('home/',views.home, name = 'home'),
    path('message_response',views.message_response,name='message_response')
     
    ]