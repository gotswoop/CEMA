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
	from_phone = '+12133400348'
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
	start_time = survey_obj.start_datetime.strftime('%I:%M %p').lstrip('0')
	msg = msg.replace("_TIME_", start_time)
	expires_at = survey_obj.end_time().strftime('%I:%M %p').lstrip('0')
	msg = msg.replace("_EXPIRES_AT_", expires_at)
	return msg

def build_sms_reminder(subj_obj, survey_obj, key):
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
	sms_message = sms_body
	send_after = survey_obj.start_datetime - timedelta(1)
	populate_sms_outgoing(send_after, sms_message, subj_obj, survey_obj)
	print(send_after.strftime('%Y-%m-%d %I:%M %p') + ' (1 of 2): ' + sms_message)
		
class Command(BaseCommand):

	help = "Populates Week 4's reminder only"

	def add_arguments(self, parser):
		parser.add_argument('cohort', type=int, help='Provide a cohort number')
		parser.add_argument('study_id', type=int, help='Provide a study_id and cohort number')

	def handle(self, *args, **kwargs):

		cohort = kwargs['cohort']
		study_id = kwargs['study_id']

		try:
			subj_obj = Subjects.objects.get(study_id=study_id, cohort=cohort)
		except Subjects.DoesNotExist:
			msg = 'User you are trying to schedule does not exist or cohort number does not match'
			raise CommandError(msg)

		if subj_obj.deleted or subj_obj.optout:
			msg = 'User you are trying to schedule has been deleted or opted out of the study'
			raise CommandError(msg)

		# Fetch Week 4 survey date 
		try:
			survey_obj = SurveyLinks.objects.filter(study_id=study_id, survey_number=4, status=0).order_by('start_datetime')[:1].get()
		except SurveyLinks.DoesNotExist:
			msg = 'User you are trying to schedule does not exist'
			raise CommandError(msg)

		key = 'wk4_reminder'
		print(key)
		build_sms_reminder(subj_obj, survey_obj, key)

		# Fetch Week 14 survey date 
		try:
			survey_obj = SurveyLinks.objects.filter(study_id=study_id, survey_number=14, status=0).order_by('start_datetime')[:1].get()
		except SurveyLinks.DoesNotExist:
			msg = 'User you are trying to schedule does not exist'
			raise CommandError(msg)

		key = 'wk14_reminder'
		print(key)
		build_sms_reminder(subj_obj, survey_obj, key)

