# python3 manage.py shell < _export_data.py

import csv
import sys
import os
from survey.models import *
from subjects.models import Subjects
from datetime import datetime
from django.conf import settings
from django.db import IntegrityError
from datetime import datetime

out_file = 'ng_data_generated_on_' + datetime.today().strftime('%Y-%m-%d_%H-%M') + '.csv'

timeformat = '%Y-%m-%d %H:%M:%S'

survey_types = {1:'time', 2:'risk'}

with open(out_file, 'w') as outFile:
	writer = csv.writer(outFile)
	writer.writerow([
		'study_id','name',
		'survey_key','survey_number','survey_field_datetime','survey_window_time',
		'status','last_answered_question','q_00','q_00_time','q_01','q_01_time','q_02',
		'q_02_time','q_03','q_03_time','q_04','q_04_time','q_05','q_05_time','q_06',
		'q_06_time','q_10','q_10_time','q_11','q_11_time','q_12','q_12_time','q_13',
		'q_13_time','q_20','q_20_time','q_21','q_21_time'
	])

	surveys = SurveyLinks.objects.all()

	for survey in surveys:

		responses = {}
		responses['study_id'] = survey.study_id.pk
		responses['fullname'] = survey.study_id.fullname()
		responses['survey_key'] = survey.survey_key
		responses['survey'] = survey_types[survey.survey_number]
		responses['survey_field_datetime'] = survey.start_datetime
		responses['survey_window_time'] = survey.timed
		responses['status'] = survey.status
		responses['last_answered_question'] = survey.last_answered_question

		answers = SurveyData.objects.filter(survey_link=survey.pk)
		
		for answer in answers:
			q = answer.question
			q_time = q + '_time'
			responses[q] = answer.response
			responses[q_time] = answer.ts_response.strftime(timeformat)
		
		writer.writerow([
			responses.get('study_id',''),
			responses.get('fullname',''),
			responses.get('survey_key',''),
			responses.get('survey',''), 
			responses.get('survey_field_datetime',''),
			responses.get('survey_window_time',''),
			responses.get('status',''),
			responses.get('last_answered_question'),
			responses.get('q_00',''),
			responses.get('q_00_time',''),
			responses.get('q_01',''),
			responses.get('q_01_time',''),
			responses.get('q_02',''),
			responses.get('q_02_time',''),
			responses.get('q_03',''),
			responses.get('q_03_time',''),
			responses.get('q_04',''),
			responses.get('q_04_time',''),
			responses.get('q_05',''),
			responses.get('q_05_time',''),
			responses.get('q_06',''),
			responses.get('q_06_time',''),
			responses.get('q_10',''),
			responses.get('q_10_time',''),
			responses.get('q_11',''),
			responses.get('q_11_time',''),
			responses.get('q_12',''),
			responses.get('q_12_time',''),
			responses.get('q_13',''),
			responses.get('q_13_time',''),
			responses.get('q_20',''),
			responses.get('q_20_time',''),
			responses.get('q_21',''),
			responses.get('q_21_time',''),
		])

	writer.writerow([''])
	writer.writerow([''])
	writer.writerow(['q_xx value = null: question not part of survey or user did not get to this question (see status)'])
	writer.writerow(['q_xx value = -2: user skipped this question'])
	writer.writerow([''])
	writer.writerow(['status 0 = Never clicked on survey link'])
	writer.writerow(['status 1 = Started survey but did not complete'])
	writer.writerow(['status 2 = Completed survey'])
	writer.writerow(['status 3 = Survey timed out before completion'])

	outFile.close()
