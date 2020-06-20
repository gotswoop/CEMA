from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from sms.models import SMS_Outgoing
from shorty.models import Short_Urls
from django.db import IntegrityError
import pandas as pd
from subjects.models import Subjects
import random, string

# TODO: 1st import study_users into profile table.
# Only insert records if user is in Subjects table and opt_out = 0
def build_message(_FROM_FNAME_, _TO_FNAME_, _LINK_, _TIME1_, msg):
	msg = msg.replace("_TO_FNAME_", _TO_FNAME_)
	msg = msg.replace("_FROM_FNAME_", _FROM_FNAME_)
	msg = msg.replace("_LINK_", _LINK_)
	msg = msg.replace("_TIME1_", _TIME1_)
	return msg


def shorten_url(url_long, user_obj):

	short_url_length = 7
	
	url_short = ''.join(random.choices(string.ascii_letters + string.digits, k=short_url_length))

	try:
		shorty_obj, url_created = Short_Urls.objects.get_or_create(url_long = url_long, 
			defaults={
				'url_short': url_short, 
				'generated_by': user_obj
			},
		)
	except IntegrityError as e:
		msg = '# ERROR - Shorty_Urls insert/lookup: ' + e.args
		raise CommandError(msg)

	if url_created is False:
		print("old url")
		print(shorty_obj.url_short)
	else:
		print("new url")
		print(shorty_obj.url_short)

	return 'https://uscstudy.com/l/' + shorty_obj.url_short



class Command(BaseCommand):

	help = 'Imports a spreadsheet into the SMS queue for bulk send. Argument is a filename'

	def add_arguments(self, parser):
		parser.add_argument('filename', type=str, help='Pass the spreadsheet that you want to import')

	def handle(self, *args, **kwargs):

		file_to_import = kwargs['filename']
		from_phone = settings.TWILIO_FROM_NUMBER
		# Load spreadsheet
		try:
			xl = pd.ExcelFile(file_to_import)
		except FileNotFoundError:
			msg = 'File ' + file_to_import + ' not found!'
			raise CommandError(msg)
		
		try:
			user_obj = User.objects.get(username = 'swoop')
		except User.DoesNotExist:
			raise CommandError('Cron user SWOOP not found')

		# Print the sheet names
		# print(xl.sheet_names)

		# Load a sheet into a DataFrame by name: df
		df = xl.parse('Sheet1')

		for index, row in df.iterrows():
			study_id = row['study_id']
			try:
				sub_obj = Subjects.objects.get(study_id=study_id)
			except Subjects.DoesNotExist:
				msg = '# ERROR: Cannot proceed as no account found for participant study id ' + str(study_id)
				raise CommandError(msg)
			
			to_phone = '+1' + row['to_phone'].replace("-","")
			
			short_link = shorten_url(row['_LINK_'], user_obj)

			sms_message = build_message(row['_FROM_FNAME_'], row['_TO_FNAME_'], short_link, row['_TIME1_'], row['message'])
						
			try:
				sms_obj = SMS_Outgoing.objects.create(from_phone=from_phone, to_phone=to_phone, message=sms_message, send_after=row['send_after'], study_id=sub_obj, sent_by_user=user_obj)
			except IntegrityError as e:
				msg = '# ERROR: MySQL ' + str(e.args)
				raise CommandError(msg)
			print(sms_obj.to_phone)
			print(sms_obj.send_after)
			print(sms_obj.message)
			print('')
