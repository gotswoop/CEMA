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
from survey.models import *
import random, string

# TODO: 1st import study_users into profile table.
# Only insert records if user is in Subjects table and opt_out = 0
# def build_message(_FROM_FNAME_, _TO_FNAME_, _LINK_, _TIME1_, msg):
def build_message(msg, placeholders):
	msg = msg.replace("_TO_FNAME_", placeholders['_TO_FNAME_'])
	msg = msg.replace("_FROM_FNAME_", placeholders['_FROM_FNAME_'])
	msg = msg.replace("_SURVEY_LINK_", placeholders['_SURVEY_LINK_'])
	msg = msg.replace("_EXPIRES_AT_", placeholders['_EXPIRES_AT_'])
	return msg

# res = SurveyLinks.objects.create(survey_key=123, start_datetime="2019-05-22 16:00:00", status=0, timed=timed, survey_number=survey_number, study_id=Subjects(study_id=study_id));
def generate_survey_link(start_datetime, timed, survey_number, subj_obj):

	short_url_length = 10
	
	survey_key = ''.join(random.choices(string.ascii_letters + string.digits, k=short_url_length))

	try:
		survey_link = SurveyLinks.objects.create(survey_key=survey_key, start_datetime=start_datetime, timed=timed, survey_number=survey_number, study_id=subj_obj)
	except IntegrityError as e:
		msg = '# ERROR - Error creating a survey link : ' + str(e.args)
		raise CommandError(msg)

	return survey_link
	
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
			user_obj = User.objects.get(username = 'avocadobot')
		except User.DoesNotExist:
			raise CommandError('Cron user avocadobot not found')

		# Print the sheet names
		# print(xl.sheet_names)

		# Load a sheet into a DataFrame by name: df
		df = xl.parse('Sheet1')

		for index, row in df.iterrows():
			study_id = row['study_id']
			try:
				subj_obj = Subjects.objects.get(study_id=study_id)
			except Subjects.DoesNotExist:
				msg = '# ERROR: Cannot proceed as no account found for participant study id ' + str(study_id)
				raise CommandError(msg)
			
			if subj_obj.optout != 0:
				msg = '# ERROR: Cannot proceed as user ' + subj_obj.fullname() + '(' + str(study_id) + ') has opted out of the study.'
				raise CommandError(msg)

			to_phone = subj_obj.phone

			send_after_format = '%Y-%m-%d %H:%M:%S'
			send_after = datetime.strptime(row['send_after'], send_after_format)
			
			if row['survey'] in ['time', 'risk']:
				timed = 60
				end_datetime = send_after + timedelta(minutes=timed)
				_EXPIRES_AT_ = str(end_datetime.strftime("%I:%M %p").lstrip('0'))
			else: 
				timed = None
				end_datetime = send_after + timedelta(days=7)
				_EXPIRES_AT_ = str(end_datetime.strftime("%I:%M %p").lstrip('0')) + ' on ' + str(end_datetime.strftime("%B %d, %Y")) + '.'
					
			surveys = {'time': 1, 'risk':2, 'three': 3}
			survey_number = surveys[row['survey']]
			
			survey_link_obj = generate_survey_link(send_after, timed, survey_number, subj_obj)

			placeholders = {
				'_TO_FNAME_': subj_obj.first_name,
				'_FROM_FNAME_': subj_obj.recruited_by,
				'_EXPIRES_AT_': _EXPIRES_AT_,
				'_SURVEY_LINK_': 'https://uscstudy.com/s/' + survey_link_obj.survey_key,
			}

			sms_message = build_message(row['message'], placeholders)
						
			try:
				sms_obj = SMS_Outgoing.objects.create(from_phone=from_phone, to_phone=to_phone, message=sms_message, send_after=send_after, study_id=subj_obj, sent_by_user=user_obj)
			except IntegrityError as e:
				# Delete the last link you created.
				survey_link_obj.delete()
				msg = '# ERROR: MySQL ' + str(e.args)
				raise CommandError(msg)
			print(sms_obj.to_phone)
			print(sms_obj.send_after)
			print(sms_obj.message)
			print('')
