from django.db import models
from subjects.models import Subjects
from datetime import datetime, timedelta

class SurveyLinks(models.Model):
	survey_key = models.CharField(max_length=50, unique=True)
	subject_study_id = models.ForeignKey(Subjects, to_field='study_id', db_column='subject_study_id', on_delete=models.PROTECT)
	start_datetime = models.DateTimeField()
	timed = models.IntegerField(null=True, default=75)
	status = models.IntegerField(default=0)
	survey_number = models.IntegerField()
	last_answered_question = models.CharField(max_length=10, null=True)
	ts_created = models.DateTimeField(auto_now_add=True)
	ts_updated = models.DateTimeField(auto_now=True)
	
	# Expiration time for untimed surveys
	untimed_expiration_days = 7	

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
		if self.survey_number == 1:
			return str(self.survey_number) + ' (Time Preference)'
		if self.survey_number == 2:
			return str(self.survey_number) + ' (Risk Preference)'
		if self.survey_number == 3:
			return str(self.survey_number) + ' (End of Week)'
	def end_time(self):
		if self.timed:
			end_datetime = self.start_datetime + timedelta(minutes=self.timed)
		else:
			end_datetime = self.start_datetime + timedelta(days=self.untimed_expiration_days)
		return end_datetime
	
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
			return 'You have already completed this survey, ' + self.subject_study_id.first_name + '. Thank you!'
		elif self.status == 3:
			return 'Sorry, ' + self.subject_study_id.first_name + '. The survey link expired at ' + str(end_datetime.strftime("%I:%M %p").lstrip('0')) + ' on ' + str(end_datetime.strftime("%B %d, %Y")) + '.'
		elif self.status == 4:
			return 'Sorry, ' + self.subject_study_id.first_name + '. The survey is closed.'
	
	def update_last_answered(self, question):
		self.last_answered_question = question
		self.save()

	def get_next_question(self):

		survey_number = self.survey_number
		last_question = self.last_answered_question
		
		surveys_and_questions = {
	        1: ('q_00', 'q_01', 'q_02', 'q_03', 'q_04', 'q_05', 'q_06', 'q_10', 'q_11', 'q_12'),
	        2: ('q_00', 'q_01', 'q_02', 'q_03', 'q_04', 'q_05', 'q_06', 'q_20', 'q_21'),
	        3: ('q_00', 'q_01', 'q_02', 'q_03', 'q_04', 'q_05'),
	    }

		questions = surveys_and_questions.get(survey_number)
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
