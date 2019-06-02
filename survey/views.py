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
from survey.functions import *

@require_http_methods(["GET", "POST"])
def survey(request, survey_key):

	try:
		survey = SurveyLinks.objects.get(survey_key=survey_key)
	except SurveyLinks.DoesNotExist:
		# Key not found in database
		msg = '<h3>Sorry, the survey link is invalid.</h3>'
		return HttpResponse(msg)

	# POST Method
	if request.method == 'POST':

		question = request.POST.get("question", "")
		question_response = request.POST.get("question_response", "")
		
		save_survey_response(survey, question, question_response, request.META['REMOTE_ADDR'])
		
		survey.update_last_answered(question)

		# Timing out a user only after we saved the survey question response
		survey.check_and_update_survey_status()
		
		if survey.status > 1:
			context = {
				'survey_key': survey.survey_key, 
				'survey_status': survey.status, 
				'survey_status_details': survey.status_details(), 
			}
			return JsonResponse(context)
			
		next_question = survey.get_next_question()
		if next_question == None:
			context = {
				'survey_key': survey.survey_key, 
				'survey_status': survey.status, 
				'survey_status_details': 'Thanks for participating, ' + survey.subject_study_id.first_name + '! We will text you once your card is loaded.', 
			}
			return JsonResponse(context)

		else:
			context = {
				'survey_key': survey.survey_key, 
				'survey_status': survey.status, 
				'survey_question': survey.subject_study_id.language + '/' + next_question
			}
			return JsonResponse(context)

	# GET Method
	else:

		if survey.status > 1:
			context = {
				'survey': survey,
				'survey_status_details': survey.status_details(),
			}
			return render(request, 'survey/main.html', context)
		else:
			# Check if survey has expired
			survey.check_and_update_survey_status()
			next_question = survey.get_next_question()
			context = {
				'survey': survey,
				'survey_question': survey.subject_study_id.language + '/' + next_question,
			}
			return render(request, 'survey/main.html', context)

@require_http_methods(["GET", "POST"])
def survey_test(request):

	# POST Method
	if request.method == 'POST':
		survey_number = request.POST.get("survey", "1")
		spanish = request.POST.get("language", "0")
		if spanish == "1":
			# Test user for Spanish
			study_id = 110
		else:
			# Test user for English
			study_id = 109
		print(spanish)
		print(study_id)
		survey_key = generate_survey_link(survey_number, study_id)
		survey_link = ('https://' if request.is_secure() else 'http://') + request.get_host() + '/s/' + survey_key
		context = {
			'survey_link': survey_link,
		}
	else:
		context = {
			'survey_link': None,
		}
	
	return render(request, 'survey/test.html', context)
