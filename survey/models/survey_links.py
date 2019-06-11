from django.db import models
from subjects.models import Subjects
from datetime import datetime, timedelta
from survey.settings import *

class SurveyLinks(models.Model):
	survey_key = models.CharField(max_length=50, unique=True)
	study_id = models.ForeignKey(Subjects, to_field='study_id', db_column='study_id', on_delete=models.PROTECT)
	start_datetime = models.DateTimeField()
	timed = models.IntegerField(null=True, default=75)
	status = models.IntegerField(default=0)
	survey_number = models.IntegerField()
	bonus_questions = models.CharField(null=True, max_length=50)
	last_answered_question = models.CharField(max_length=10, null=True)
	ts_created = models.DateTimeField(auto_now_add=True)
	ts_updated = models.DateTimeField(auto_now=True)
	
	class Meta:
		db_table = "survey_links"

	def check_and_update_survey_status(self):
		
		if self.timed:
			end_datetime = self.start_datetime + timedelta(minutes=self.timed)
		else:
			end_datetime = self.start_datetime + timedelta(days=self.untimed_expiration_days)

		# if now is greater than survey expiration time AND survey already not completed(=2) or closed (=4)
		if datetime.now() >= end_datetime and self.status not in [2, 4]:
			self.status = 3
			self.save()

		if self.status == 0:
			self.status = 1
			self.save()
	
	def survey_num(self):
		return str(self.survey_number) + ' (' + survey_labels.get(self.survey_number) + ')'
		
	def end_time(self):
		if self.timed:
			end_datetime = self.start_datetime + timedelta(minutes=self.timed)
		else:
			end_datetime = self.start_datetime + timedelta(days=self.untimed_expiration_days)
		return end_datetime
	
	def progress(self):
		if self.status == 0:
			return '-'
		elif self.status == 1:
			return '?'
		elif self.status == 2:
			return 'Y'
		elif self.status == 3:
			return 'X'

	def survey_type(self):
		if self.survey_number == 1:
			return 'Time'
		elif self.survey_number == 2:
			return 'Risk'
		elif self.survey_number == 4:
			return 'Week 4'
		elif self.survey_number == 14:
			return 'Week 14'

	def status_details(self):
		if self.timed:
			end_datetime = self.start_datetime + timedelta(minutes=self.timed)
		else:
			end_datetime = self.start_datetime + timedelta(days=self.untimed_expiration_days)
	
		if self.status == 0:
			return "Opened survey but did not start."
		elif self.status == 1:
			return "Started survey but did not complete."
		elif self.status == 2:
			if self.study_id.language == 'es':
				msg = 'Ya ha completado esta encuesta, ' + self.study_id.first_name + '. Gracias!'
			else:
				msg = 'You have already completed this survey, ' + self.study_id.first_name + '. Thank you!'
			return msg
		elif self.status == 3:
			if self.study_id.language == 'es':
				msg = 'Lo siento, ' + self.study_id.first_name + '. El enlace de la encuesta expiró a las ' + str(end_datetime.strftime("%I:%M %p").lstrip('0')) + ' el ' + str(end_datetime.strftime("%B %d, %Y")) + '.'
			else:
				msg = 'Sorry, ' + self.study_id.first_name + '. The survey link expired at ' + str(end_datetime.strftime("%I:%M %p").lstrip('0')) + ' on ' + str(end_datetime.strftime("%B %d, %Y")) + '.'
			return msg
		elif self.status == 4:
			if self.study_id.language == 'es':
				msg = 'Lo siento, ' + self.study_id.first_name + '. La encuesta esta cerrada.'
			else:
				msg = 'Sorry, ' + self.study_id.first_name + '. The survey is closed.'
			return msg
	
	def update_last_answered(self, question):
		self.last_answered_question = question
		self.save()

	def get_next_question(self):

		survey_number = self.survey_number
		last_question = self.last_answered_question
		
		questions = survey_questions.get(survey_number)
		# Checking if this survey has any bonus_questions and adding to the tuple of "standard questions"
		if self.bonus_questions:
			questions = questions + (self.bonus_questions,)

		if questions == None:
			return None

		# If last_answered_question was Null, then return the 1st question of the survey
		if last_question == None:
			return questions[0]

		try:
			pos = questions.index(last_question)
		except ValueError:
			# Could not find the last question in tuple. Only true if there is a typo in the survey_and_questions tuple
			return None

		try:
			next_question = questions[pos+1]
		except IndexError as e:
			# Already at last question. Set status as completed (=2)
			self.status=2
			self.save()
			return None

		return next_question
