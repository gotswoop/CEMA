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
		parser.add_argument('study_id', type=int, help='Provide a study_id and cohort number')

	def handle(self, *args, **kwargs):

		study_id  = kwargs['study_id']

		# Checking to see if user is already scheduled
		try:
			scheduled = Schedule.objects.get(study_id=study_id)
		except Schedule.DoesNotExist:
			msg = 'User you are trying to schedule does not exist'
			raise CommandError(msg)
		
		try:
			subj_obj = Subjects.objects.get(study_id=study_id)
		except Subjects.DoesNotExist:
			msg = 'User you are trying to schedule does not exist'
			raise CommandError(msg)

		if subj_obj.deleted or subj_obj.optout:
			msg = 'User you are trying to schedule has been deleted or opted out of the study'
			raise CommandError(msg)

		key = 'wk4_d1_survey'
		survey_obj = scheduled.wk4_d1_survey
		build_sms(subj_obj, survey_obj, key)

		key = 'wk4_d2_survey'
		survey_obj = scheduled.wk4_d2_survey
		build_sms(subj_obj, survey_obj, key)

		key = 'wk4_d3_survey'
		survey_obj = scheduled.wk4_d3_survey
		build_sms(subj_obj, survey_obj, key)
	
		'''
		# TODO: THIS IS PAINFUL
		# Week 3 day 1
		key = 'wk3_d1_survey_1'
		survey_obj = scheduled.wk3_d1_survey_1
		build_sms(subj_obj, survey_obj, key)

		key = 'wk3_d1_survey_2'
		survey_obj = scheduled.wk3_d1_survey_2
		build_sms(subj_obj, survey_obj, key)

		key = 'wk3_d1_survey_3'
		survey_obj = scheduled.wk3_d1_survey_3
		build_sms(subj_obj, survey_obj, key)

		key = 'wk3_d1_survey_4'
		survey_obj = scheduled.wk3_d1_survey_4
		build_sms(subj_obj, survey_obj, key)

		# Week 3 day 2
		key = 'wk3_d2_survey_1'
		survey_obj = scheduled.wk3_d2_survey_1
		build_sms(subj_obj, survey_obj, key)

		key = 'wk3_d2_survey_2'
		survey_obj = scheduled.wk3_d2_survey_2
		build_sms(subj_obj, survey_obj, key)

		key = 'wk3_d2_survey_3'
		survey_obj = scheduled.wk3_d2_survey_3
		build_sms(subj_obj, survey_obj, key)

		key = 'wk3_d2_survey_4'
		survey_obj = scheduled.wk3_d2_survey_4
		build_sms(subj_obj, survey_obj, key)
		'''
