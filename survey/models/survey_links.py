from django.db import models
from subjects.models import Subjects
from datetime import datetime, timedelta
from survey.settings import *
from numpy.random import choice
import random

class SurveyLinks(models.Model):
	survey_key = models.CharField(max_length=50, unique=True)
	study_id = models.ForeignKey(Subjects, to_field='study_id', db_column='study_id', on_delete=models.PROTECT)
	start_datetime = models.DateTimeField()
	timed = models.IntegerField(null=True, default=75)
	status = models.IntegerField(default=0)
	survey_number = models.IntegerField()
	bonus_questions = models.CharField(null=True, max_length=50)
	last_answered_question = models.CharField(max_length=30, null=True)
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

	def update_survey_data(self, **kwargs):
		question = kwargs.get('question', None)
		response = kwargs.get('response', None)
		user_ip = kwargs.get('user_ip', None)
		ts_response = kwargs.get('ts_response', datetime.now())

		'''
		self.surveydata_set.create(
			question=question,
			response=response,
			user_ip=user_ip,
			ts_response=ts_response
		)
		'''
		# TODO: Check this??
		survey_data, created = self.surveydata_set.get_or_create(question=question,
			defaults={
				'response': response,
				'user_ip': user_ip,
				'ts_response':ts_response,
			},
		)

	def get_next_question_for_week4(self, user_ip):
		q_41_A = 'Emergency kit'
		q_41_B = {1:0, 2:1, 3:3, 4:5, 5:10, 6:15, 7:20, 8:23, 9:25, 10:30, 11:40, 12:50}
		q_42_A = 'Financial Advice'
		q_42_B = {1:0, 2:1, 3:3, 4:5, 5:10, 6:15, 7:20, 8:23, 9:25, 10:30, 11:40, 12:50}

		survey_number = self.survey_number
		last_question = self.last_answered_question
		cash = None

		# Start randomization after user completes question "q_42a" - slider for financial advice
		if last_question == 'q_42b':

			# Set and save last question to q_42b so randomization doesn't trigger again on page refresh
			last_question = 'q_42c'
			self.update_last_answered(last_question)

			# Computer picking between q_41 and q_42 with 95% probablity for q_42
			wk4_q_draw, = choice(['q_41','q_42'], 1, p=[0.05, 0.95])
			self.update_survey_data(question="wk4_q_draw", response=wk4_q_draw, user_ip=user_ip)

			# If computer picked emergency kit question (q_41)
			if wk4_q_draw == "q_41":

				wk4_q41_draw = random.randint(1,12) #
				self.update_survey_data(question="wk4_q41_draw", response=wk4_q41_draw, user_ip=user_ip)

				# TODO: What if thy didn't pick anything??
				q_41_user_response = self.surveydata_set.get(question='q_41').response

				# Emergency Kit
				if int(q_41_user_response) >= wk4_q41_draw:
					self.update_survey_data(question="wk4_kit_win", response=1, user_ip=user_ip)
					self.bonus_questions = "q_45"
					self.save()
				# Emergency Kit Cash
				else:
					cash = str(q_41_B[wk4_q41_draw])
					self.update_survey_data(question="wk4_kit_cash", response=cash, user_ip=user_ip)
					self.bonus_questions = "q_46"
					self.save()

			# If computer picked financial advice question (q_42)
			else: # q_42
				# Computer picking between financial advice and cash with 95% probablity to advice
				draw, = choice([1, 2], 1, p=[0.95, 0.05])
				# 2 represents answers 2 - 12. So, now pick something between 2 and 12
				if draw == 2:
					wk4_q42_draw = random.randint(2,12)
				else: # draw == 1
					wk4_q42_draw = draw

				self.update_survey_data(question="wk4_q42_draw", response=wk4_q42_draw, user_ip=user_ip)

				# TODO: What if thy didn't pick anything??
				q_42_user_response = self.surveydata_set.get(question='q_42').response

				# Financial Advice
				if int(q_42_user_response) >= wk4_q42_draw:
					self.update_survey_data(question="wk4_fin_advice", response=1, user_ip=user_ip)
					self.bonus_questions = "q_43"
					self.save()
				# Financial Advice Cash
				else:
					cash = str(q_42_B[wk4_q42_draw])
					self.update_survey_data(question="wk4_fin_cash", response=cash, user_ip=user_ip)
					self.bonus_questions = "q_44"
					self.save()

		questions = survey_questions.get(survey_number)
		# Checking if this survey has any bonus_questions and adding to the tuple of "standard questions"
		if self.bonus_questions:
			questions = questions + (self.bonus_questions,)

		if questions == None:
			return cash, None

		# If last_answered_question was Null, then return the 1st question of the survey
		if last_question == None:
			return cash, questions[0]

		try:
			pos = questions.index(last_question)
		except ValueError:
			# Could not find the last question in tuple. Only true if there is a typo in the survey_and_questions tuple
			return cash, None

		try:
			next_question = questions[pos+1]
		except IndexError as e:
			# Already at last question. Set status as completed (=2)
			self.status=2
			self.save()
			return cash, None

		if next_question  == 'q_44':
			cash = self.surveydata_set.get(question='wk4_fin_cash').response
		elif next_question == 'q_46':
			cash = self.surveydata_set.get(question='wk4_kit_cash').response
		else:
			cash = None

		return cash, next_question

	def get_next_question(self, user_ip):

		survey_number = self.survey_number
		last_question = self.last_answered_question

		if survey_number == 4:
			next_question_data, next_question = self.get_next_question_for_week4(user_ip)
			return next_question_data, next_question

		questions = survey_questions.get(survey_number)
		# Checking if this survey has any bonus_questions and adding to the tuple of "standard questions"
		if self.bonus_questions:
			questions = questions + (self.bonus_questions,)

		if questions == None:
			return None, None

		# If last_answered_question was Null, then return the 1st question of the survey
		if last_question == None:
			return None, questions[0]

		try:
			pos = questions.index(last_question)
		except ValueError:
			# Could not find the last question in tuple. Only true if there is a typo in the survey_and_questions tuple
			return None, None

		try:
			next_question = questions[pos+1]
		except IndexError as e:
			# Already at last question. Set status as completed (=2)
			self.status=2
			self.save()
			return None, None

		return None, next_question
