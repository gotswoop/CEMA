import sys
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from sms.models import SMS_Outgoing
from subjects.models import Subjects
from twilio.rest import Client
from datetime import datetime
from survey.models import *
from django.db.models import Q
from django.db import IntegrityError

class Command(BaseCommand):

	help = 'Clears out future reminders of week 4 and 14 if they have completed the survey'

	def handle(self, *args, **kwargs):

		datetime_today = datetime.today().strftime('%Y-%m-%d')

		'''	
		# Clear week 4
		UPDATE uscstudy.sms_outgoing SET sent = -20 WHERE survey_link IN (
			SELECT id FROM uscstudy.survey_links WHERE survey_number IN (4, 14) AND start_datetime > now() AND study_id IN (
				SELECT study_id FROM uscstudy.survey_links WHERE survey_number IN (4, 14) AND start_datetime LIKE "2019-09-03%" AND status = 2
			)
		);
		SELECT *  FROM `survey_links` WHERE (`survey_links`.`start_datetime` LIKE BINARY "2019-09-10%" AND `survey_links`.`status` = 0 AND `survey_links`.`survey_number` IN (4, 14));
		'''

		# TODO Fix status = 2
		# SELECT study_id FROM uscstudy.survey_links WHERE survey_number IN (4, 14) AND start_datetime LIKE "2019-09-03%" AND status = 2
		# survey_ids = SurveyLinks.objects.filter(survey_number__in=[4,14], status=2, start_datetime__startswith=datetime_today).values_list('id', flat=True)
		study_ids = SurveyLinks.objects.filter(survey_number__in=[4,14], status=2, start_datetime__lt=datetime.now()).values_list('study_id', flat=True)
		print(study_ids.query)
		for study_id in study_ids:
			print(study_id)

		# SELECT id FROM uscstudy.survey_links WHERE survey_number IN (4, 14) AND start_datetime > now() AND study_id IN (
		survey_links = SurveyLinks.objects.filter(survey_number__in=[4,14], start_datetime__gt=datetime.now(), id__in = study_ids).values_list('id', flat=True)
		print(survey_links.query)
		for survey_link in survey_links:
			print(survey_link)

		'''
		# Resetting status of all future surveys. survey_links.status = 0
		# UPDATE survey_links SET status = 0, last_answered_question = NULL  WHERE status <> 0 AND start_datetime > NOW();
		# SurveyLinks.objects.filter(~Q(status=0), start_datetime__gt=datetime_now).update(status=0, last_answered_question=None)

		# Fetching the user with username = avacadobot to set the sent_by field
		try:
			user_obj = User.objects.get(username = self.sender)
		except User.DoesNotExist:
			raise CommandError('Cron user ' + self.sender + ' not found')

		# Fetching all the messages that need to be sent
		try:
			messages = SMS_Outgoing.objects.exclude(study_id__optout=1, study_id__deleted=1).filter(sent=0, send_after__lte = datetime_now).order_by('study_id','send_after')
		except IntegrityError as e:
			msg = '# ERROR: MySQL ' + str(e.args)
			raise CommandError(msg)

		# Exit if nothing to send
		if not messages:
			print('# OK: Nothing to send at ' + str(datetime.today()))
			sys.exit(0)

		for message in messages:

			sms_to = message.to_phone
			sms_from = message.from_phone
			sms_body = message.message
			study_id = message.study_id.pk 

			try:
				sub_obj = Subjects.objects.get(study_id=study_id)
			except Subjects.DoesNotExist:
				msg = '# ERROR: Cannot proceed as no account found for participant study id ' + str(study_id)
				raise CommandError(msg)

			# Checking if user has opted out
			# TODO: Redundant
			if sub_obj.optout != 0:
				print('# ERROR: ' + str(datetime.today()) + ' Message not sent as user with study id ' + str(study_id) + ' (' + str(sms_to) + ') has opted to not receive texts')
				continue
			
			sms = client.messages.create(
				body=sms_body,
				from_=from_number, # TODO: Switch to using sms_from
				to=sms_to,
			)

			if (sms.status != 'failed') and (sms.status != 'undelivered') :		
				message.sent = 1
				message.sent_on = datetime.today()
				message.sent_sid = sms.sid
				message.sent_by_user = user_obj
				message.save()
				print('# OK: ' + str(datetime.today()) + ' - ' + sms.sid + ' - ' + sms_to + ' - ' + sms_body)
			else:
				print('# ERROR: ' + str(datetime.today()) + ' SMS send error to ' + sms_to + ' - ' + sms_body + '. Sid: ' + sms.sid + '. Status: ' + sms.status + '. Error code: ' + str(sms.error_code) + '. Error message: ' + str(sms.error_message))
		'''
