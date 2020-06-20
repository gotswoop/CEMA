from django.core.management.base import BaseCommand, CommandError
from datetime import datetime as dt

from django.conf import settings
from django.contrib.auth.models import User
from sms.models import SMS_Outgoing
from subjects.models import Subjects
from django.db import IntegrityError
import pandas as pd

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

# TODO: 1st import study_users into profile table.
# Only insert records if user is in Subjects table and opt_out = 0
#def build_message(_TO_FNAME_, _SUR_, _TODAY_PAY_, _TENW_PAY_, _TENW_DATE_, msg):
# def build_message(_TO_FNAME_, _SUR_, _TODAY_PAY_, msg):
def build_message(msg, _TO_FNAME_, _FROM_FNAME_, _SUR_, _TODAY_PAY_, _FIVEW_PAY_, _FIVEW_DATE_, _TENW_PAY_, _TENW_DATE_):
	
	msg = msg.replace("_TO_FNAME_", _TO_FNAME_)
	msg = msg.replace("_FROM_FNAME_", _FROM_FNAME_)
	msg = msg.replace("_SUR_", str(_SUR_))

	msg = msg.replace("_TODAY_PAY_", "%.2f" % _TODAY_PAY_)

	msg = msg.replace("_FIVEW_PAY_", "%.2f" % _FIVEW_PAY_)
	if not pd.isnull(_FIVEW_DATE_):
		msg = msg.replace("_FIVEW_DATE_", custom_strftime('%B {S}, %Y', _FIVEW_DATE_))

	msg = msg.replace("_TENW_PAY_", "%.2f" % _TENW_PAY_)
	if not pd.isnull(_TENW_DATE_):
		msg = msg.replace("_TENW_DATE_", custom_strftime('%B {S}, %Y', _TENW_DATE_))

	return msg

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
			send_after = row['send_after']
			sms_message = build_message(row['message'], row['_TO_FNAME_'], row['_FROM_FNAME_'], row['_SUR_'], row['_TODAY_PAY_'], row['_FIVEW_PAY_'], row['_FIVEW_DATE_'], row['_TENW_PAY_'], row['_TENW_DATE_'])
			# sms_message = build_message(row['_TO_FNAME_'], row['_SUR_'], row['_TODAY_PAY_'], row['_FIVEW_PAY_'], row['_FIVEW_DATE_'], row['message'], row['_TENW_PAY_'], row['_TENW_DATE_'])
			# sms_message = build_message(row['_TO_FNAME_'], row['_SUR_'], row['_TODAY_PAY_'], row['_TENW_PAY_'], row['_TENW_DATE_'], row['message'])
			# sms_message = build_message(row['_TO_FNAME_'], row['_SUR_'], row['_TODAY_PAY_'], row['message'])
			
			try:
				sms_obj = SMS_Outgoing.objects.create(from_phone=from_phone, to_phone=to_phone, message=sms_message, send_after=send_after, study_id=sub_obj)
				pass
			except IntegrityError as e:
				msg = '# ERROR: MySQL ' + str(e.args)
				raise CommandError(msg)
			
			print(sms_obj.to_phone)
			print(sms_obj.send_after)
			print(sms_obj.message)
			print('')
