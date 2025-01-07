from django.urls import path,include
from . import views
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('course_list/', views.course_list, name='course_list'),
    path('', views.home, name = 'home'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('create/', views.create_course, name='create_course'),
    path('login/', views.custom_login, name='custom_login'),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('signup/', views.signup, name='signup'),
    path('chat/user/', views.user_chat, name='user_chat'),
    path('chat/staff/', views.staff_chat, name='staff_chat'),
    path('send_message/', views.send_message_to_staff, name='send_message_to_staff'),
    path('view_messages/', views.view_messages, name='view_messages'),
    path('reply/<int:message_id>/', views.reply_to_message, name='reply_to_message'),
    ]
