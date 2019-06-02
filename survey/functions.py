import json
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from subjects.models import Subjects
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core import serializers
from django.conf import settings
from django.contrib import messages
from datetime import datetime
from survey.models import *
from django.db import IntegrityError
import random, string

def generate_survey_link(survey_number, study_id):

	timed = 60
	short_url_length = 10

	survey_key = ''.join(random.choices(string.ascii_letters + string.digits, k=short_url_length))
	
	try:
		survey_link = SurveyLinks.objects.create(survey_key=survey_key, start_datetime=datetime.now(), timed=timed, survey_number=survey_number, subject_study_id=Subjects(study_id=study_id))
	except IntegrityError as e:
		msg = '# ERROR - Error creating a survey link : ' + str(e.args)
		return msg

	return survey_link.survey_key

def save_survey_response(survey, question, question_response, user_ip):
	try:
		response = SurveyData.objects.get(survey_key=survey, question=question)
	except SurveyData.DoesNotExist:
		response = None
		
	if response is None:	
		SurveyData.objects.create(
			survey_key=survey, 
			question=question, 
			response=question_response, 
			user_ip=user_ip
		)
	else:
		response.response = question_response
		response.user_ip = user_ip
		response.ts_response = datetime.today()
		response.save()
	
	return None
