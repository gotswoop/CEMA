from django.conf import settings
from subjects.models import Subjects
from django.db import IntegrityError
import pandas as pd
from django.core.management.base import BaseCommand, CommandError

# TODO: 1st import study_users into profile table.
# Only insert records if user is in Subjects table and opt_out = 0
def build_message(_FROM_FNAME_, _TO_FNAME_, _LINK_, msg):
	msg = msg.replace("_TO_FNAME_", _TO_FNAME_)
	msg = msg.replace("_FROM_FNAME_", _FROM_FNAME_)
	msg = msg.replace("_LINK_", _LINK_)
	return msg

class Command(BaseCommand):

	help = 'Imports a spreadsheet with Subjects into the Sujects table'

	def add_arguments(self, parser):
		parser.add_argument('filename', type=str, help='Pass the spreadsheet that you want to import')

	def handle(self, *args, **kwargs):

		file_to_import = kwargs['filename']
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
			recruited_date = row['recruited_date']
			recruited_location = row['recruited_location']
			recruited_by = row['recruited_by']
			first_name = row['first_name']
			last_name = row['last_name']
			language = row['language']
			treatment = row['treatment']
			phone_1 = '+1' + row['phone_1'].replace("-","")

			try:
				sub_obj = Subjects.objects.create(study_id=study_id, recruited_date=recruited_date, recruited_location=recruited_location, 
					recruited_by=recruited_by, first_name=first_name, last_name=last_name,	phone_1=phone_1, language=language, treatment=treatment)
			except IntegrityError as e:
				msg = '# ERROR: MySQL ' + str(e.args)
				raise CommandError(msg)
			print(sub_obj.study_id)
			print('')
			
