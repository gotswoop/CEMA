import json
import random
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from subjects.models import Subjects, SchedulePlus
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core import serializers
from django.conf import settings
from django.contrib import messages
from datetime import datetime
from survey.models import *
from django.db import IntegrityError
from survey.functions import *
from survey.settings import *
import xlwt

# No login required
@require_http_methods(["GET", "POST"])
def survey(request, survey_key):

	try:
		survey = SurveyLinks.objects.get(survey_key=survey_key)
	except SurveyLinks.DoesNotExist:
		# Key not found in database
		msg = '<h3>Sorry, the survey link is invalid <br/><br/> Lo siento, el link de encuesta no es válido</h3>'
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
			if survey.study_id.language == 'es':
				msg = 'Gracias por participar, ' + survey.study_id.first_name + '! Le enviaremos un mensaje de texto una vez que le agregamos dinero a su tarjeta.'
			else: 
				msg = 'Thanks for participating, ' + survey.study_id.first_name + '! We will text you once your card is loaded.'
			context = {
				'survey_key': survey.survey_key, 
				'survey_status': survey.status, 
				'survey_status_details': msg, 
			}
			return JsonResponse(context)

		else:
			context = {
				'survey_key': survey.survey_key, 
				'survey_status': survey.status, 
				'survey_question': survey.study_id.language + '/' + next_question
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
				'survey_question': survey.study_id.language + '/' + next_question,
			}
			return render(request, 'survey/main.html', context)

@login_required
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
		# Add a random bonus question only if Time(1) or Risk(2) survey
		if survey_number in ["1", "2"]:
			random_pick, = random.sample(range(0,len(survey_bonus_questions)),k=1)
			bonus_questions = survey_bonus_questions[random_pick]
		else:
			bonus_questions = None

		survey_obj = generate_survey_link(survey_number, study_id, bonus_questions=bonus_questions)
		survey_link = ('https://' if request.is_secure() else 'http://') + request.get_host() + '/s/' + survey_obj.survey_key
		context = {
			'survey_link': survey_link,
		}
	else:
		context = {
			'survey_link': None,
		}
	
	return render(request, 'survey/test.html', context)

@login_required
def survey_download(request):

	# populating all schedules into a dictionary
	user_schedules = {}
	schedules = SchedulePlus.objects.all().values()
	for s in schedules:
		study_id = s['study_id_id']
		if study_id not in user_schedules:
			user_schedules[study_id] = {}
		user_schedules[study_id][s['survey']] = s['survey_link_id']

	response = HttpResponse(content_type='application/ms-excel')
	response['Content-Disposition'] = 'attachment; filename="NG_Survey_Data.xls"'

	tab = 'Updated now on ' + datetime.now().strftime('%Y-%m-%d')
	wb = xlwt.Workbook(encoding='utf-8')
	ws_1 = wb.add_sheet(tab)

	# Sheet header, first row
	row_num = 0

	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	columns = ['study_id', 'cohort', 'first_name', 'last_name', 'language', 'survey', 'fielded_datetime', 'time_limit', 'survey_status', 'survey_status_desc', 'survey_number', 'survey_number_desc', 'bonus_questions', 'last_answered_question']
	columns = columns + all_survey_questions
	for col_num in range(len(columns)):
		ws_1.write(row_num, col_num, columns[col_num], font_style)

	# Sheet body, remaining rows
	font_style = xlwt.XFStyle()

	users = Subjects.objects.filter(deleted=0, optout=0, test_account=0, cohort__gte=2, cohort__lt=200).order_by('-study_id')
	for user in users:

		for week in ['wk1', 'wk2', 'wk3']:
			for day in ['d1', 'd2']:
				for survey in ['1', '2', '3', '4']:
					sur = week + '_' + day + '_survey_' + survey
					survey_id = user_schedules[user.study_id][sur]
					# TODO: Exceptions are not handled here...
					survey_info = SurveyLinks.objects.get(id=survey_id)
					if survey_info.status > 0:
						answers = fetch_survey_responses(survey_id)
						row = [
							user.study_id, user.cohort, user.first_name, user.last_name, user.lang(), sur, survey_info.start_datetime.strftime('%Y-%m-%d %H:%M'),
							survey_info.timed, survey_info.status, survey_info.progress(), survey_info.survey_number, survey_info.survey_type(), survey_info.bonus_questions, survey_info.last_answered_question,
						]
						row_plus = row + answers
						row_num += 1
						for col_num in range(len(row_plus)):
							ws_1.write(row_num, col_num, row_plus[col_num], font_style)

		for week in ['wk4', 'wk14']:
			for day in ['d1', 'd2', 'd3']:
				sur = week + '_' + day + '_survey'
				survey_id = user_schedules[user.study_id][sur]
				# TODO: Exceptions are not handled here...
				survey_info = SurveyLinks.objects.get(id=survey_id)
				if survey_info.status > 0:
					answers = fetch_survey_responses(survey_id)
					row = [
						user.study_id, user.cohort, user.first_name, user.last_name, user.lang(), sur, survey_info.start_datetime.strftime('%Y-%m-%d %H:%M'),
						survey_info.timed, survey_info.status, survey_info.progress(), survey_info.survey_number, survey_info.survey_type(), survey_info.bonus_questions, survey_info.last_answered_question,
					]
					row_plus = row + answers
					row_num += 1
					for col_num in range(len(row_plus)):
						ws_1.write(row_num, col_num, row_plus[col_num], font_style)

	wb.save(response)
	return response
