import sys
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from sms.models import SMS_Outgoing
from subjects.models import Subjects
from twilio.rest import Client
from datetime import datetime
from django.db import IntegrityError
from django.conf import settings

# TODO: 1st import study_users into profile table.
# check if their number is listed as do-not-disturb before sending
# TODO ESCAPE sms_body

class Command(BaseCommand):

	help = 'manually send messages providing study_id, number and message'

	def add_arguments(self, parser):
		parser.add_argument('study_id', type=str, help='Provide the study id')
		parser.add_argument('sms_to', type=str, help='Provide the phone number')
		parser.add_argument('sms_body', type=str, help='Provide the SMS message')

	def handle(self, *args, **kwargs):

		study_id = kwargs['study_id']
		sms_to = kwargs['sms_to']
		sms_body = kwargs['sms_body']
		# Your Account Sid and Auth Token from twilio.com/console
		# Your Account Sid and Auth Token from twilio.com/console
		account_sid = settings.TWILIO_ACCOUNT_SID
		auth_token = settings.TWILIO_AUTH_TOKEN
		client = Client(account_sid, auth_token)
		from_number = settings.TWILIO_FROM_NUMBER

		try:
			sub_obj = Subjects.objects.get(study_id=study_id)
		except Subjects.DoesNotExist:
			msg = '# ERROR: Cannot proceed as no account found for participant study id ' + str(study_id)
			raise CommandError(msg)

		if sub_obj.phone != sms_to:
			msg = '# ERROR: Cannot proceed as provided number (' + str(sms_to) + ') does not match for phone number on record for study id ' + str(study_id)
			raise CommandError(msg)

		# Checking if user has opted out
		if sub_obj.optout != 0:
			print('# ERROR: ' + str(datetime.today()) + ' Message not sent as user with study id ' + study_id + ' (' + sms_to + ') has opted to not receive texts')
			sys.exit(1)
			
		print(sms_body)
		try:
			user_obj = User.objects.get(username = 'swoop')
		except User.DoesNotExist:
			raise CommandError('Cron user SWOOP not found')

		sms_from = from_number

		sms = client.messages.create(
			body=sms_body,
			from_=from_number, # TODO: Switch to using sms_from
			to=sms_to,
		)

		# TODO
		print(sms.status)
		if (sms.status != 'failed') and (sms.status != 'undelivered') :
			try:
				sms_outgoing_obj = SMS_Outgoing.objects.create(from_phone=sms_from, to_phone=sms_to, message=sms_body, send_after=datetime.today(), sent=1, sent_on=datetime.today(), sent_sid=sms.sid, study_id=sub_obj, sent_by_user=user_obj, send_mode="manual")
			except IntegrityError as e:
				msg = '# ERROR: MySQL ' + str(e.args)
				raise CommandError(msg)
			print('# OK: ' + str(datetime.today()) + ' - ' + sms.sid + ' - ' + sms_to + ' - ' + sms_body)
		else:
			print('# ERROR: ' + str(datetime.today()) + ' SMS send error to ' + sms_to + ' - ' + sms_body + '. Sid: ' + sms.sid + '. Status: ' + sms.status + '. Error code: ' + str(sms.error_code) + '. Error message: ' + str(sms.error_message))
