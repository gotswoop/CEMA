from django.conf import settings
from subjects.models import Subjects
from survey.models import SurveyLinks, SurveyData
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
from subjects.models import Schedule, PaymentDetails, PaymentSummary, SchedulePlus
import csv
import xlwt
'''
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
'''
def format_money(payment):
	if payment.is_integer():
		payment = int(payment)
		return str(payment)
	else:
		return format(payment, '.2f')

def build_message(msg, subj_obj, surveys_completed, payment_basic, bonus_pay=None):
	
	payment_basic = format_money(payment_basic)
			
	msg = msg.replace("_BASIC_PAY_", str(payment_basic))
	msg = msg.replace("_SURVEYS_", str(surveys_completed))
	msg = msg.replace("_TO_FNAME_", subj_obj.first_name)
	msg = msg.replace("_FROM_FNAME_", subj_obj.recruited_by.first_name)
	msg = msg.replace("_BONUS_PAY_", str(bonus_pay))
	return msg

def build_sms(subj_obj, survey_obj, key):
	lang = subj_obj.language.upper()
	url = 'https://uscstudy.com/s/' + survey_obj.survey_key
	
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
	# populate_sms_outgoing(send_after, sms_message, subj_obj, survey_obj)
	print(send_after.strftime('%Y-%m-%d %I:%M %p') + ' (1 of 2): ' + sms_message)
	# message 2 of 2 (666666 microseconds later)
	sms_message = url
	send_after = survey_obj.start_datetime + timedelta(microseconds=666666)
	# populate_sms_outgoing(send_after, sms_message, subj_obj, survey_obj)
	print(send_after.strftime('%Y-%m-%d %I:%M %p') + ' (2 of 2): ' + sms_message)

# TODO - THIS IS A PAIN..
def payments_for_completion(su, week_n_day):
	cnt = 0
	day_surveys = ['_survey_1', '_survey_2', '_survey_3', '_survey_4']
	for day_survey in day_surveys:
		key = week_n_day + day_survey
		# TODO catch
		sp = SchedulePlus.objects.get(survey=key, study_id=su)
		if sp.survey_link.status == 2:
			cnt += 1
	return cnt, cnt*2.50

def get_survey_details(su, key):
	# TODO catch
	sp = SchedulePlus.objects.get(survey=key, study_id=su)
	return sp.survey_link

def survey_status_description(status):
	if status == 0:
		return "Skipped Survey"
	if status == 1:
		return "Did not complete"
	if status == 2:
		return "Completed"
	if status == 3:
		return "Timed out"

def get_risk_outcome(computer_random_question, computer_random_question_response, user_response):
	
	future = None
	q_20_A = 'Lottery for $20'
	q_20_B = {
		1: 2,  # Sure payment of $2
		2: 4,  # Sure payment of $4
		3: 6,  # Sure payment of $6 
		4: 8,  # Sure payment of $8
		5: 10,  # Sure payment of $10
		6: 12,  # Sure payment of $12
		7: 14,  # Sure payment of $14
		8: 16,  # Sure payment of $16
	}

	user_response = int(user_response)
	if user_response >= computer_random_question_response:
		future = None
		# In Lottery.
		lottery = random.randint(1,2)
		if lottery == 1:
			msg = 'risk_lottery_won'
			return msg, future, 20, "Won Lottery for $20"
		else:
			msg = 'risk_lottery_lost'
			return msg, future, 0, "Did not win lottery."
	else:
		msg = 'risk_sure_payment'
		return msg, future, q_20_B[computer_random_question_response], 'Sure payment of $'+ str(q_20_B[computer_random_question_response])
	
def get_time_outcome(computer_random_question, computer_random_question_response, user_response):
	
	q_10_A = '$10 today'
	q_10_B = {
		1: 12,  # $12 five weeks from today
		2: 14,  # $14 five weeks from today
		3: 16,  # $16 five weeks from today
		4: 18,  # $18 five weeks from today
		5: 20,  # $20 five weeks from today
	}
	q_11_A = '$10 five weeks from today'
	q_11_B = {
		1: 12,  # $12 ten weeks from today
		2: 14,  # $14 ten weeks from today
		3: 16,  # $15 ten weeks from today
		4: 18,  # $18 ten weeks from today 
		5: 20,  # $20 ten weeks from today
	}

	user_response = int(user_response)
	if computer_random_question == 'q_10':
		if user_response >= computer_random_question_response:
			future = None
			msg = 'time_today'
			return msg, future, 10, q_10_A
		else:
			future = 5
			msg = 'time_5'
			return msg, future, q_10_B[computer_random_question_response], '$'+str(q_10_B[computer_random_question_response]) + ' five weeks from today'
	if computer_random_question == 'q_11':
		if user_response >= computer_random_question_response:
			future = 5
			msg = 'time_5'
			return msg, future, 10, q_11_A
		else:
			future = 10
			msg = 'time_10'
			return msg, future, q_11_B[computer_random_question_response], '$'+str(q_11_B[computer_random_question_response]) + ' ten weeks from today'

class Command(BaseCommand):

	help = 'processes payments for a day of the week'

	def handle(self, *args, **kwargs):

		datetime_now = datetime.now()
	
		users = {}		
		subjects = Subjects.objects.filter(test_account=0, deleted=0, optout=0, cohort__gt=19).order_by('study_id')
		for su in subjects:
			try:
				# select * from survey_links where start_datetime < NOW() and study_id = 5041 order by start_datetime desc limit 1;
				most_recent_survey = SurveyLinks.objects.filter(study_id=su, start_datetime__lt=datetime_now).order_by('-start_datetime')[:1].get()
			except SurveyLinks.DoesNotExist:
				most_recent_survey = None
		
			if most_recent_survey is None:
				print("SHOULD NOT BE IN HERE!!!!")
				print(su.pk, su.fullname(), su.cohort, " - No recent survey", " - Nothing Scheduled")
				continue

			try:
				# select * from schedule_plus where survey_link = 211;
				most_recent_scheduled_survey = SchedulePlus.objects.get(study_id=su, survey_link=most_recent_survey)
			except SchedulePlus.DoesNotExist:
				most_recent_scheduled_survey = None

			if most_recent_scheduled_survey is None:
				print("SHOULD NOT BE IN HERE!!!!")
				print(su.pk, su.fullname(), su.cohort, most_recent_survey.pk, " - Nothing Scheduled")
				continue
			else:
				loc = most_recent_scheduled_survey.survey.find('_survey_4')
							
			if loc > 0:
				week_n_day = most_recent_scheduled_survey.survey[0:loc]
				# print(su.pk, su.fullname(), su.cohort, most_recent_survey.pk, week_n_day)
			else:
				print(su.pk, su.fullname(), su.cohort, most_recent_survey.pk, " - TOO SOON!!!")
		
			blank = None
			computer_random_question = None
			computer_random_question_response = None
			user_response = None
			randomization_outcome = None
			randomization_outcome_payment = None
			pay_today = None
			pay_5_weeks_from_now = None
			pay_10_weeks_from_now = None

			study_id = su.pk
			clincard = su.clincard
			language = su.lang()
			cohort = su.cohort
			name = su.fullname()

			surveys_completed, payment_basic = payments_for_completion(su, week_n_day)

			computer_survey_random = week_n_day + '_survey_' + str(random.randint(1,4))
			
			survey_obj = get_survey_details(su, computer_survey_random)

			survey_number = survey_obj.survey_number
			survey_number_type = survey_obj.survey_type()
			survey_status = survey_obj.status
			survey_status_desc = survey_status_description(survey_status)

			# Time calulations
			date_pay_today = survey_obj.start_datetime + timedelta(days=1)
			date_pay_5_weeks = survey_obj.start_datetime + timedelta(weeks=5,days=1)
			date_pay_10_weeks = survey_obj.start_datetime + timedelta(weeks=10,days=1)
			
			# message = build_message_basic(su, surveys_completed, payment_basic)
			if surveys_completed > 0:
				lang = su.language.upper() + '_survey_payment'
			else:
				lang = su.language.upper() + '_no_surveys'
			message_basic = sms_payment_messages[lang]

			if survey_status != 2:
				# User did not complete the survey. Skip to next user
				pay_today = payment_basic
				message = message_basic
				message = build_message(message, su, surveys_completed, payment_basic)
				users[study_id] = [study_id, name, clincard, cohort, language, week_n_day, surveys_completed, payment_basic, blank, computer_survey_random, survey_number, survey_number_type, survey_status, 
					survey_status_desc, computer_random_question, user_response, computer_random_question_response, randomization_outcome, randomization_outcome_payment, blank, 
					pay_today, pay_5_weeks_from_now, pay_10_weeks_from_now, message ]
				continue

			if survey_number == 1:
				computer_random_question = random.choice(['q_10', 'q_11']);
				computer_random_question_response = random.randint(1,5)
			elif survey_number == 2:
				computer_random_question = "q_20"
				computer_random_question_response = random.randint(1,8)
			else:
				msg = 'Should not be in here.'
				raise CommandError(msg)

			try:
				user_response_obj = SurveyData.objects.get(survey_link=survey_obj.pk, question=computer_random_question)
			except SurveyData.DoesNotExist:	
				user_response_obj = None

			if user_response_obj is None:
				# User did not answer the random question that the computer selected question or never clicked on the survey link
				# Skip to next user
				pay_today = payment_basic
				message = message_basic
				message = build_message(message, su, surveys_completed, payment_basic)
				users[study_id] = [study_id, name, clincard, cohort, language, week_n_day, surveys_completed, payment_basic, blank, computer_survey_random, survey_number, survey_number_type, survey_status, 
					survey_status_desc, computer_random_question, user_response, computer_random_question_response, randomization_outcome, randomization_outcome_payment, blank, 
					pay_today, pay_5_weeks_from_now, pay_10_weeks_from_now, message ]
				continue
			else:
				user_response = user_response_obj.response

			if user_response in ["-1", "-2"]:
				# User Skipped the question
				lang_key = su.language.upper() + '_no_choice'
				message = message_basic + ' ' + sms_payment_messages[lang_key]
				message = build_message(message, su, surveys_completed, payment_basic)
				pay_today = payment_basic
				users[study_id] = [study_id, name, clincard, cohort, language, week_n_day,surveys_completed, payment_basic, blank, computer_survey_random, survey_number, survey_number_type, survey_status, 
					survey_status_desc, computer_random_question, user_response, computer_random_question_response, randomization_outcome, randomization_outcome_payment, blank, 
					pay_today, pay_5_weeks_from_now, pay_10_weeks_from_now, message ]
				continue
			
			# Time outcome
			if survey_number == 1:
				msg, future, randomization_outcome_payment, randomization_outcome = get_time_outcome(computer_random_question, computer_random_question_response, user_response)
			else: 
				msg, future, randomization_outcome_payment, randomization_outcome = get_risk_outcome(computer_random_question, computer_random_question_response, user_response)

			message = message_basic + " " + msg
			if future is None:
				pay_today = payment_basic + randomization_outcome_payment
				pay_5_weeks_from_now = None
				pay_10_weeks_from_now = None
			elif future == 5:
				pay_today = payment_basic
				pay_5_weeks_from_now = randomization_outcome_payment
				pay_10_weeks_from_now = None
			elif future == 10:
				pay_today = payment_basic
				pay_5_weeks_from_now = None
				pay_10_weeks_from_now = randomization_outcome_payment

			lang_key = su.language.upper() + '_' + msg
			message = message_basic + ' ' + sms_payment_messages[lang_key]	
			message = build_message(message, su, surveys_completed, payment_basic, randomization_outcome_payment)

			users[study_id] = [study_id, name, clincard, cohort, language, week_n_day, surveys_completed, payment_basic, blank, computer_survey_random, survey_number, survey_number_type, survey_status, 
					survey_status_desc, computer_random_question, user_response, computer_random_question_response, randomization_outcome, randomization_outcome_payment, blank,
					 pay_today, pay_5_weeks_from_now, pay_10_weeks_from_now, message]

		# Writing everything into the database
		for key, value in users.items():
			row = users[key]
			print(value)
			# [5041, 'Karen Alvarez', '11964522', 2, 'English', 'wk3_d1', 4, 10.0, None, 'wk3_d1_survey_4', 1, 'Time', 2, 'Completed', 'q_10', '3', 2, '$10 today', 10, None, 20.0, None, None, 'Your card is loaded! You got $10 for 4 surveys. In the choice-that-counts, you also got $10 today.']
			payment_details = PaymentDetails.objects.create(
				study_id=Subjects(study_id=key), 
				payment_for=row[5],
				surveys_completed = row[6],
				payment_for_completion = row[7],
				random_survey_picked = row[9],
				survey_number = row[10],
				survey_number_type = row[11],
				survey_status = row[12],
				survey_status_desc = row[13],
				random_survey_question = row[14],
				user_answer = row[15],
				random_answer_computer_picked = row[16],
				randomization_outcome = row[17],
				randomization_outcome_payment = row[18],
				pay_today = row[20],
				pay_5wks = row[21],
				pay_10wks = row[22],
				message = row[23],
			)

			if row[20]:
				PaymentSummary.objects.create(
					payment_id = payment_details,
					payment_type = 'pay_today',
					payment_amount = row[20],
					payment_date = date_pay_today.replace(hour=0, minute=0, second=0, microsecond=0),
					payment_message = row[23],
				)
			
			if row[21]:
				PaymentSummary.objects.create(
					payment_id = payment_details,
					payment_type = 'pay_5wks_out',
					payment_amount = row[21],
					payment_date = date_pay_5_weeks.replace(hour=0, minute=0, second=0, microsecond=0),
					payment_message = '-',
				)
							

			if row[22]:
				PaymentSummary.objects.create(
					payment_id = payment_details,
					payment_type = 'pay_10wks_out',
					payment_amount = row[22],
					payment_date = date_pay_10_weeks.replace(hour=0, minute=0, second=0, microsecond=0),
					payment_message = '-',
				)
		
		# Writing everything out to a file
		out_file = 'Payments_' + datetime.today().strftime('%Y.%m.%d') + '.xls'
		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('Payments')

		# Sheet header, first row
		row_num = 0

		font_style = xlwt.XFStyle()
		font_style.font.bold = True
			
		columns = [
				'Study Id', 'Name', 'ClinCard', 'Cohort', 'Language', 'Processed for',
				'Surveys Completed', ' Payment for Completion', '',
				'random_survey_picked', 'survey_number', 'survey_number_type', 'survey_status', 'survey_status_desc', 
				'random_survey_question', 'user_answer', 'random_answer_computer_picked', 'randomization_outcome', 'randomization_outcome_payment', '',
				'Pay Today ('+ str(date_pay_today.strftime("%Y-%m-%d")) +')', 'Pay 5 weeks from today ('+ str(date_pay_5_weeks.strftime("%Y-%m-%d"))+')', 'Pay 10 weeks from today ('+ str(date_pay_10_weeks.strftime("%Y-%m-%d"))+')', 'Text message to send *AFTER* processing clincard']

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		# Sheet body, remaining rows
		font_style = xlwt.XFStyle()

		for key, value in users.items():
			row = users[key] # same as row = value
			row_num += 1
			for col_num in range(len(row)):
				ws.write(row_num, col_num, row[col_num], font_style)
		wb.save(out_file)
