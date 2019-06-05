"""uscstudy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from home import views as home_views
from sms import views as sms_views
from subjects import views as subject_views
from shorty import views as shorty_views
from survey import views as survey_views

urlpatterns = [
	path('admin/', admin.site.urls),
	#
	path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='home/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='home/logout.html'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='home/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='home/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='home/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='home/password_reset_complete.html'), name='password_reset_complete'),
    #
    path('', home_views.home, name='home'), # front page
    path('dashboard/', home_views.dashboard, name='dashboard'),
    #
	path('subjects/', subject_views.subjects_all, name='subjects_all'),
	path('subject/<int:study_id>/', subject_views.subject_details, name='subject_details'),
	path('subject/<int:study_id>/edit/', subject_views.subject_edit, name='subject_edit'),
	path('subjects/recruit/', subject_views.subject_recruit, name='subjects_recruit'),
	#
	path('sms/queue/', sms_views.sms_queue, name='sms_queue'),
	path('sms/sent/', sms_views.sms_sent, name='sms_sent'),
	path('sms/inbox/', sms_views.sms_inbox, name='sms_inbox'),
	#
	# POST - send SMS via form
	path('sms/send/', sms_views.sms_send, name='sms_send'),
	# POST - incoming webhook
	path('incoming_sms/', sms_views.incoming_sms, name='incoming_sms'),
	# path('ping/', user_views.ping, name='ping'),
	# URL Redirect
	path('l/<str:short_url>', shorty_views.redirect_url, name='redirect_url'),
	# URL Shortner
	path('shorty/', include('shorty.urls')),

	# Incoming survey request
	path('s/<str:survey_key>', survey_views.survey, name='survey'),
	# Test
	path('survey/test/', survey_views.survey_test, name='survey_test'),
]
