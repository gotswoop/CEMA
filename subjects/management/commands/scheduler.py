from django.conf import settings
from subjects.models import Subjects
from survey.models import SurveyLinks
from django.db import IntegrityError
from django.core.management.base import BaseCommand, CommandError
from sms.models import SMS_Outgoing
from django.contrib.auth.models import User
import random
from random import shuffle
from datetime import datetime, timedelta
from subjects.latin_squares import *
from survey.functions import generate_survey_link
from survey.settings import *
from subjects.models import Schedule

def assign_latin_squares(schedule, study_id):

	# latin_squares being read from subjects.latin_squares.py
	latin_sq = latin_squares.get(study_id)
	if not latin_sq:
		msg = 'This user has no latin square assignment'
		raise CommandError(msg)

	schedule['wk1_d1_survey_1']['survey_type'] = latin_sq[0]
	schedule['wk1_d1_survey_2']['survey_type'] = latin_sq[1]
	schedule['wk1_d1_survey_3']['survey_type'] = latin_sq[2]
	schedule['wk1_d1_survey_4']['survey_type'] = latin_sq[3]
	schedule['wk1_d2_survey_1']['survey_type'] = latin_sq[4]
	schedule['wk1_d2_survey_2']['survey_type'] = latin_sq[5]
	schedule['wk1_d2_survey_3']['survey_type'] = latin_sq[6]
	schedule['wk1_d2_survey_4']['survey_type'] = latin_sq[7] 
	schedule['wk2_d1_survey_1']['survey_type'] = latin_sq[8] 
	schedule['wk2_d1_survey_2']['survey_type'] = latin_sq[9] 
	schedule['wk2_d1_survey_3']['survey_type'] = latin_sq[10]
	schedule['wk2_d1_survey_4']['survey_type'] = latin_sq[11]
	schedule['wk2_d2_survey_1']['survey_type'] = latin_sq[12]
	schedule['wk2_d2_survey_2']['survey_type'] = latin_sq[13]
	schedule['wk2_d2_survey_3']['survey_type'] = latin_sq[14]
	schedule['wk2_d2_survey_4']['survey_type'] = latin_sq[15]
	schedule['wk3_d1_survey_1']['survey_type'] = latin_sq[16]
	schedule['wk3_d1_survey_2']['survey_type'] = latin_sq[17]
	schedule['wk3_d1_survey_3']['survey_type'] = latin_sq[18]
	schedule['wk3_d1_survey_4']['survey_type'] = latin_sq[19]
	schedule['wk3_d2_survey_1']['survey_type'] = latin_sq[20] 
	schedule['wk3_d2_survey_2']['survey_type'] = latin_sq[21]
	schedule['wk3_d2_survey_3']['survey_type'] = latin_sq[22]
	schedule['wk3_d2_survey_4']['survey_type'] = latin_sq[23]

	return schedule

def assign_random_questions(schedule):

	# Not used
	bonus_questions_day1 = [
		'qr_01',
		'qr_02',
	]
	# Not used
	bonus_questions_day2 = [
		'qr_03',
	]
	bonus_questions_other = [
		'qr_04', 'qr_05', 'qr_06', 'qr_07', 'qr_08', 
		'qr_09', 'qr_10', 'qr_11', 'qr_12', 'qr_13', 
		'qr_14', 'qr_15', 'qr_16', 'qr_17', 'qr_18',
	]
	include_list = [
		'wk1_d1_survey_1', 'wk1_d1_survey_2', 'wk1_d1_survey_3', 'wk1_d1_survey_4', 
		'wk1_d2_survey_1', 'wk1_d2_survey_2', 'wk1_d2_survey_3', 'wk1_d2_survey_4', 
		'wk2_d1_survey_1', 'wk2_d1_survey_2', 'wk2_d1_survey_3', 'wk2_d1_survey_4', 
		'wk2_d2_survey_1', 'wk2_d2_survey_2', 'wk2_d2_survey_3', 'wk2_d2_survey_4', 
		'wk3_d1_survey_1', 'wk3_d1_survey_2', 'wk3_d1_survey_3', 'wk3_d1_survey_4', 
		'wk3_d2_survey_1', 'wk3_d2_survey_2', 'wk3_d2_survey_3', 'wk3_d2_survey_4',
	]

	# Assigning random questions 1 and 2 to day 1 surveys only
	random_a, random_b = random.sample(range(1,5),k=2)
	schedule['wk1_d1_survey_' + str(random_a)]['random_q'] = "qr_01"
	schedule['wk1_d1_survey_' + str(random_b)]['random_q'] = "qr_02" 

	random_a, random_b = random.sample(range(1,5),k=2)
	schedule['wk2_d1_survey_' + str(random_a)]['random_q'] = "qr_01"
	schedule['wk2_d1_survey_' + str(random_b)]['random_q'] = "qr_02" 

	random_a, random_b = random.sample(range(1,5),k=2)
	schedule['wk3_d1_survey_' + str(random_a)]['random_q'] = "qr_01"
	schedule['wk3_d1_survey_' + str(random_b)]['random_q'] = "qr_02" 

	# Assigning random questions 3 and 2 to day 2 surveys only
	random_c, = random.sample(range(1,5),k=1)
	schedule['wk1_d2_survey_' + str(random_c)]['random_q'] = "qr_03"

	random_c, = random.sample(range(1,5),k=1)
	schedule['wk2_d2_survey_' + str(random_c)]['random_q'] = "qr_03"
	
	random_c, = random.sample(range(1,5),k=1)
	schedule['wk3_d2_survey_' + str(random_c)]['random_q'] = "qr_03"
	
	shuffle(bonus_questions_other)
	cnt = 0
	for key, value in schedule.items():
		if any(key in s for s in include_list):
			if value['random_q'] is None:
				schedule[key]['random_q'] = bonus_questions_other[cnt]
				cnt = cnt + 1
	
	return schedule

def set_dates(d):

	survey_days = {}
	times = [8, 12, 16, 20]
	
	weekday = 0 # 0=Monday, 1=Tuesday, 2=Wednesday...
	days_ahead = weekday - d.weekday()
	if days_ahead <= 0: # Target day already happened this week
		days_ahead += 7
	day_1 = d.replace(minute=00, second=0, microsecond=0) + timedelta(days_ahead)

	# Week 1
	wk1_d1_survey = day_1
	survey_days['wk1_d1_survey_1'] = {'survey_type': None, "random_q": None, "survey_time": wk1_d1_survey.replace(hour=8) }
	survey_days['wk1_d1_survey_2'] = {'survey_type': None, "random_q": None, "survey_time": wk1_d1_survey.replace(hour=12) }
	survey_days['wk1_d1_survey_3'] = {'survey_type': None, "random_q": None, "survey_time": wk1_d1_survey.replace(hour=16) }
	survey_days['wk1_d1_survey_4'] = {'survey_type': None, "random_q": None, "survey_time": wk1_d1_survey.replace(hour=20) }
	
	wk1_d1_payment = day_1 + timedelta(1)
	# survey_days['wk1_d1_payment'] = {'survey_type': "Payment", "random_q": None, "survey_time": wk1_d1_payment.replace(hour=12) }

	wk1_d2_survey = day_1 + timedelta(2)
	survey_days['wk1_d2_survey_1'] = {'survey_type': None, "random_q": None, "survey_time": wk1_d2_survey.replace(hour=8) }
	survey_days['wk1_d2_survey_2'] = {'survey_type': None, "random_q": None, "survey_time": wk1_d2_survey.replace(hour=12) }
	survey_days['wk1_d2_survey_3'] = {'survey_type': None, "random_q": None, "survey_time": wk1_d2_survey.replace(hour=16) }
	survey_days['wk1_d2_survey_4'] = {'survey_type': None, "random_q": None, "survey_time": wk1_d2_survey.replace(hour=20) }

	wk1_d2_payment = day_1 + timedelta(3)
	#survey_days['wk1_d2_payment'] = {'survey_type': "Payment", "random_q": None, "survey_time": wk1_d2_payment.replace(hour=12) }

	# Week 2
	wk2_d1_survey = day_1 + timedelta(7)
	survey_days['wk2_d1_survey_1'] = {'survey_type': None, "random_q": None, "survey_time": wk2_d1_survey.replace(hour=8) }
	survey_days['wk2_d1_survey_2'] = {'survey_type': None, "random_q": None, "survey_time": wk2_d1_survey.replace(hour=12) }
	survey_days['wk2_d1_survey_3'] = {'survey_type': None, "random_q": None, "survey_time": wk2_d1_survey.replace(hour=16) }
	survey_days['wk2_d1_survey_4'] = {'survey_type': None, "random_q": None, "survey_time": wk2_d1_survey.replace(hour=20) }

	wk2_d1_payment = day_1 + timedelta(8)
	# survey_days['wk2_d1_payment'] = {'survey_type': "Payment", "random_q": None, "survey_time": wk2_d1_payment.replace(hour=12) }

	wk2_d2_survey = day_1 + timedelta(9)
	survey_days['wk2_d2_survey_1'] = {'survey_type': None, "random_q": None, "survey_time": wk2_d2_survey.replace(hour=8) }
	survey_days['wk2_d2_survey_2'] = {'survey_type': None, "random_q": None, "survey_time": wk2_d2_survey.replace(hour=12) }
	survey_days['wk2_d2_survey_3'] = {'survey_type': None, "random_q": None, "survey_time": wk2_d2_survey.replace(hour=16) }
	survey_days['wk2_d2_survey_4'] = {'survey_type': None, "random_q": None, "survey_time": wk2_d2_survey.replace(hour=20) }

	wk2_d2_payment = day_1 + timedelta(10)
	# survey_days['wk2_d2_payment'] = {'survey_type': "Payment", "random_q": None, "survey_time": wk2_d2_payment.replace(hour=12) }

	# Week 3
	wk3_d1_survey = day_1 + timedelta(14)
	survey_days['wk3_d1_survey_1'] = {'survey_type': None, "random_q": None, "survey_time": wk3_d1_survey.replace(hour=8) }
	survey_days['wk3_d1_survey_2'] = {'survey_type': None, "random_q": None, "survey_time": wk3_d1_survey.replace(hour=12) }
	survey_days['wk3_d1_survey_3'] = {'survey_type': None, "random_q": None, "survey_time": wk3_d1_survey.replace(hour=16) }
	survey_days['wk3_d1_survey_4'] = {'survey_type': None, "random_q": None, "survey_time": wk3_d1_survey.replace(hour=20) }

	wk3_d1_payment = day_1 + timedelta(15)
	# survey_days['wk3_d1_payment'] = {'survey_type': "Payment", "random_q": None, "survey_time": wk3_d1_payment.replace(hour=12) }

	wk3_d2_survey = day_1 + timedelta(16)
	survey_days['wk3_d2_survey_1'] = {'survey_type': None, "random_q": None, "survey_time": wk3_d2_survey.replace(hour=8) }
	survey_days['wk3_d2_survey_2'] = {'survey_type': None, "random_q": None, "survey_time": wk3_d2_survey.replace(hour=12) }
	survey_days['wk3_d2_survey_3'] = {'survey_type': None, "random_q": None, "survey_time": wk3_d2_survey.replace(hour=16) }
	survey_days['wk3_d2_survey_4'] = {'survey_type': None, "random_q": None, "survey_time": wk3_d2_survey.replace(hour=20) }

	wk3_d2_payment = day_1 + timedelta(17)
	#survey_days['wk3_d2_payment'] = {'survey_type': "Payment", "random_q": None, "survey_time": wk3_d2_payment.replace(hour=12) }

	# WEEK 4
	week_4_random_time = random.choice(times)
	wk4_d1_survey = day_1 + timedelta(21)
	survey_days['wk4_d1_survey'] = {'survey_type': 4, "random_q": None, "survey_time": wk4_d1_survey.replace(hour=week_4_random_time) }
	wk4_d1_payment = day_1 + timedelta(22)
	# survey_days['wk4_d1_payment'] = {'survey_type': "Payment", "random_q": None, "survey_time": wk4_d1_payment.replace(hour=12) }

	# Week 4 reminder 1
	wk4_d2_survey = day_1 + timedelta(22)
	survey_days['wk4_d2_survey'] = {'survey_type': 4, "random_q": None, "survey_time": wk4_d2_survey.replace(hour=week_4_random_time) }
	wk4_d2_payment = day_1 + timedelta(23)
	# survey_days['wk4_d2_payment'] = {'survey_type': "Payment", "random_q": None, "survey_time": wk4_d2_payment.replace(hour=12) }
	
	# Week 4 reminder 2
	wk4_d3_survey = day_1 + timedelta(23)
	survey_days['wk4_d3_survey'] = {'survey_type': 4, "random_q": None, "survey_time": wk4_d3_survey.replace(hour=week_4_random_time) }
	wk4_d3_payment = day_1 + timedelta(24)
	# survey_days['wk4_d3_payment'] = {'survey_type': "Payment", "random_q": None, "survey_time": wk4_d3_payment.replace(hour=12) }
	
	# WEEK 14
	week_14_random_time = random.choice(times)
	wk14_d1_survey = day_1 + timedelta(98)
	survey_days['wk14_d1_survey'] = {'survey_type': 14, "random_q": None, "survey_time": wk14_d1_survey.replace(hour=week_14_random_time) }
	wk14_d1_payment = day_1 + timedelta(99)
	# survey_days['wk14_d1_payment'] = {'survey_type': "Payment", "random_q": None, "survey_time": wk14_d1_payment.replace(hour=12) }

	# Week 14 reminder 1
	wk14_d2_survey = day_1 + timedelta(99)
	survey_days['wk14_d2_survey'] = {'survey_type': 14, "random_q": None, "survey_time": wk14_d2_survey.replace(hour=week_14_random_time) }
	wk14_d2_payment = day_1 + timedelta(100)
	# survey_days['wk14_d2_payment'] = {'survey_type': "Payment", "random_q": None, "survey_time": wk14_d2_payment.replace(hour=12) }

	# Week 14 reminder 2
	wk14_d3_survey = day_1 + timedelta(100)
	survey_days['wk14_d3_survey'] = {'survey_type': 14, "random_q": None, "survey_time": wk14_d3_survey.replace(hour=week_14_random_time) }
	wk14_d3_payment = day_1 + timedelta(101)
	# survey_days['wk14_d3_payment'] = {'survey_type': "Payment", "random_q": None, "survey_time": wk14_d3_payment.replace(hour=12) }

	return survey_days

def populate_sms_outgoing(send_after, sms_message, subj_obj, survey_obj):
	from_phone = settings.TWILIO_FROM_NUMBER
	try:
		user_obj = User.objects.get(username = 'avocadobot')
	except User.DoesNotExist:
		raise CommandError('Cron user Avocado not found')

	try:
		sms_obj = SMS_Outgoing.objects.create(from_phone=from_phone, to_phone=subj_obj.phone, message=sms_message, send_after=send_after, study_id=subj_obj, sent_by_user=user_obj, send_mode='auto', survey_link=survey_obj)
	except IntegrityError as e:
		# Delete the last link you created.
		# TODO!!! survey_link_obj.delete()
		msg = '# ERROR: MySQL ' + str(e.args)
		raise CommandError(msg)

def build_message_body(msg, subj_obj, survey_obj):
	msg = msg.replace("_TO_FNAME_", subj_obj.first_name)
	msg = msg.replace("_FROM_FNAME_", subj_obj.recruited_by.first_name)
	expires_at = survey_obj.end_time().strftime('%I:%M %p').lstrip('0')
	msg = msg.replace("_EXPIRES_AT_", expires_at)
	return msg

def build_sms(subj_obj, survey_obj, key):
	lang = subj_obj.language.upper()
	url = 'https://uscstudy.beelab.site/s/' + survey_obj.survey_key
	
	s = key.rfind('_survey_')
	if s > 0:
		lang_key = lang.upper() + key[s:]
		sms_body = sms_messages[lang_key][random.randint(0,5)]
	else:
		lang_key = lang.upper() + '_' + key
		sms_body = sms_messages_week_4_14[lang_key]

	sms_body = build_message_body(sms_body, subj_obj, survey_obj)
	# message 1 of 2
	sms_message = sms_body
	send_after = survey_obj.start_datetime
	populate_sms_outgoing(send_after, sms_message, subj_obj, survey_obj)
	print(send_after.strftime('%Y-%m-%d %I:%M %p') + ' (1 of 2): ' + sms_message)
	# message 2 of 2 (666666 microseconds later)
	sms_message = url
	send_after = survey_obj.start_datetime + timedelta(microseconds=666666)
	populate_sms_outgoing(send_after, sms_message, subj_obj, survey_obj)
	print(send_after.strftime('%Y-%m-%d %I:%M %p') + ' (2 of 2): ' + sms_message)

class Command(BaseCommand):

	help = 'Schedules a user to survey'

	def add_arguments(self, parser):
		parser.add_argument('cohort', type=int, help='Provide a cohort number')
		parser.add_argument('study_id', type=int, help='Provide a study_id')

	def handle(self, *args, **kwargs):

		cohort = kwargs['cohort']
		study_id  = kwargs['study_id']

		'''
		if cohort not in [2, 200, 3, 4]:
			msg = 'Invalid cohort number'
			raise CommandError(msg)
		'''

		# Checking to see if user is already scheduled
		try:
			scheduled = Schedule.objects.get(study_id=study_id)
		except Schedule.DoesNotExist:
			scheduled = None

		if scheduled is not None:
			msg = 'This user is already scheduled.'
			raise CommandError(msg)

		# MAKE SURE HE IS NOT EXCLUDED, DELETED or opt-ed out
		try:
			subj_obj = Subjects.objects.get(study_id=study_id, cohort=cohort)
		except Subjects.DoesNotExist:
			msg = 'User you are trying to schedule does not exist or cohort number does not match'
			raise CommandError(msg)

		if subj_obj.deleted or subj_obj.optout:
			msg = 'User you are trying to schedule has been deleted or opted out of the study'
			raise CommandError(msg)

		# TODO!!!!
		# enrollment_date = subj_obj.recruited_date
		enrollment_date = datetime.today()
		# Start
		'''
		# Only use when adding people in the middle of a wave
		enrollment_date = datetime.today() - timedelta(days=7)
		print('')
		print("# -------------------------")
		print("# Adding this person mid-wave by faking today's date to: " + str(enrollment_date))
		print("# -------------------------")
		'''
		# End
		
		schedule = set_dates(enrollment_date)
		schedule = assign_latin_squares(schedule, study_id)
		schedule = assign_random_questions(schedule)
		
		final_schedule = {}
		for key, value in schedule.items():
			if value['random_q']:
				bonus_questions = value['random_q']
			else:
				bonus_questions = None
			survey_number = str(value['survey_type'])
			start_datetime = value['survey_time']
			survey_obj = generate_survey_link(survey_number, study_id, bonus_questions=bonus_questions, start_datetime=start_datetime)
			final_schedule[key] = survey_obj.pk
			# Don't create SMS messages if start_datetime in the past
			# Added this to handle cases where I added test accounts mid-wave, and didn't want to spam user with old unsent emails.
			if start_datetime > datetime.now():
				build_sms(subj_obj, survey_obj, key)

		new_item = Schedule.objects.create(
			study_id=Subjects(study_id=study_id),
			cohort=cohort,
			wk1_d1_survey_1=SurveyLinks(id=final_schedule['wk1_d1_survey_1']), 
			wk1_d1_survey_2=SurveyLinks(id=final_schedule['wk1_d1_survey_2']), 
			wk1_d1_survey_3=SurveyLinks(id=final_schedule['wk1_d1_survey_3']), 
			wk1_d1_survey_4=SurveyLinks(id=final_schedule['wk1_d1_survey_4']), 

			wk1_d2_survey_1=SurveyLinks(id=final_schedule['wk1_d2_survey_1']), 
			wk1_d2_survey_2=SurveyLinks(id=final_schedule['wk1_d2_survey_2']), 
			wk1_d2_survey_3=SurveyLinks(id=final_schedule['wk1_d2_survey_3']), 
			wk1_d2_survey_4=SurveyLinks(id=final_schedule['wk1_d2_survey_4']), 

			wk2_d1_survey_1=SurveyLinks(id=final_schedule['wk2_d1_survey_1']), 
			wk2_d1_survey_2=SurveyLinks(id=final_schedule['wk2_d1_survey_2']), 
			wk2_d1_survey_3=SurveyLinks(id=final_schedule['wk2_d1_survey_3']), 
			wk2_d1_survey_4=SurveyLinks(id=final_schedule['wk2_d1_survey_4']), 

			wk2_d2_survey_1=SurveyLinks(id=final_schedule['wk2_d2_survey_1']), 
			wk2_d2_survey_2=SurveyLinks(id=final_schedule['wk2_d2_survey_2']), 
			wk2_d2_survey_3=SurveyLinks(id=final_schedule['wk2_d2_survey_3']), 
			wk2_d2_survey_4=SurveyLinks(id=final_schedule['wk2_d2_survey_4']), 

			wk3_d1_survey_1=SurveyLinks(id=final_schedule['wk3_d1_survey_1']), 
			wk3_d1_survey_2=SurveyLinks(id=final_schedule['wk3_d1_survey_2']), 
			wk3_d1_survey_3=SurveyLinks(id=final_schedule['wk3_d1_survey_3']), 
			wk3_d1_survey_4=SurveyLinks(id=final_schedule['wk3_d1_survey_4']), 

			wk3_d2_survey_1=SurveyLinks(id=final_schedule['wk3_d2_survey_1']), 
			wk3_d2_survey_2=SurveyLinks(id=final_schedule['wk3_d2_survey_2']), 
			wk3_d2_survey_3=SurveyLinks(id=final_schedule['wk3_d2_survey_3']), 
			wk3_d2_survey_4=SurveyLinks(id=final_schedule['wk3_d2_survey_4']), 

			wk4_d1_survey=SurveyLinks(id=final_schedule['wk4_d1_survey']), 
			wk4_d2_survey=SurveyLinks(id=final_schedule['wk4_d2_survey']), 
			wk4_d3_survey=SurveyLinks(id=final_schedule['wk4_d3_survey']), 

			wk14_d1_survey=SurveyLinks(id=final_schedule['wk14_d1_survey']),
			wk14_d2_survey=SurveyLinks(id=final_schedule['wk14_d2_survey']),
			wk14_d3_survey=SurveyLinks(id=final_schedule['wk14_d3_survey'])
		)
		# TODO: WHAT THE FUCK IS GOING ON HERE?? . Can't do new_item.wk1_d1_survey_1.start_datetime comes up as None
		sch = Schedule.objects.get(study_id=Subjects(study_id=study_id))
		out = subj_obj.fullname() + ' (' + str(study_id) + ') successfully scheduled for ' + subj_obj.lang() + ' surveys starting on ' + sch.wk1_d1_survey_1.start_datetime.strftime('%Y-%m-%d at %I:%M %p')
		print('')
		print(out)
		print('')
						
		
