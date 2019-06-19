from django.db import models
from django.contrib.auth.models import User

class Subjects(models.Model):

	LANG_EN = 'en'
	LANG_ES = 'es'
	LANGUAGE_CHOICES = (
		(LANG_EN, 'English'),
		(LANG_ES, 'Spanish'),
	)

	LOC_1 = 'Bell'
	LOC_2 = 'Long Beach'
	LOCATION_CHOICES = (
		(LOC_1, 'Bell'),
		(LOC_2, 'Long Beach'),
	)

	study_id = models.AutoField(auto_created=True, primary_key=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	phone = models.CharField(null=False, blank=False, max_length=50, unique=True)
	clincard = models.CharField(null=False, blank=False, max_length=60, unique=True)
	email = models.CharField(null=True, max_length=50)
	emergency_contact = models.CharField(null=True, max_length=200)
	emergency_contact_phone = models.CharField(null=True, max_length=50)
	address_1 = models.CharField(null=True, max_length=100)
	address_2 = models.CharField(null=True, max_length=100)
	address_city = models.CharField(null=True, max_length=50)
	address_state = models.CharField(null=True, max_length=20)
	address_zip = models.CharField(null=True, max_length=10)
	address_country = models.CharField(null=True, max_length=20)
	language = models.CharField(blank=False, default=None, max_length=10, choices=LANGUAGE_CHOICES)
	treatment = models.CharField(null=True, max_length=10)
	time_zone = models.CharField(default="PT", null=True, max_length=10)
	optout = models.BooleanField(default=False)
	deleted = models.BooleanField(default=False)
	cohort = models.IntegerField(default=0)
	test_account = models.BooleanField(default=False)
	sent_enrollment_survey = models.BooleanField(default=False)
	recruited_date = models.DateTimeField(auto_now_add=True)
	recruited_by = models.ForeignKey(User, db_column='recruited_by', related_name='subjects_recruited_by', on_delete=models.PROTECT)
	recruited_location = models.CharField(blank=False, default=None, max_length=20, choices=LOCATION_CHOICES)
	notes = models.TextField(null=True, blank=True)
	ts_created = models.DateTimeField(auto_now_add=True)
	ts_updated = models.DateTimeField(auto_now=True)
	record_created_by = models.ForeignKey(User, db_column='record_created_by', related_name='subjects_record_created_by', on_delete=models.PROTECT)
	record_modified_by = models.ForeignKey(User, db_column='record_modified_by', related_name='subjects_record_modified_by', on_delete=models.PROTECT)
	
	class Meta:
		db_table = "subjects"

	def lang(self):
		if self.language == "es":
			return "Spanish"
		return "English"

	def fullname(self):
		return self.first_name + ' ' + self.last_name

	# Phone number in the format (800) 555-1234
	def phone_number(self):
		phone = self.phone
		a = phone[2:5]
		b = phone[5:8]
		c = phone[8:12]
		return '(' + a + ')' + ' ' + b + '-' + c

	# Phone number in the format 800-555-1234
	def phone_number_with_dashes(self):
		phone = self.phone
		a = phone[2:5]
		b = phone[5:8]
		c = phone[8:12]
		return a + '-' + b + '-' + c

	# Clincard without "_del_YYYY-MM-DD HH:SS:"
	def clincard_number(self):
		return self.clincard[0:8]
		
class Subjects_History(models.Model):

	study_id = models.IntegerField()
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	phone = models.CharField(null=False, max_length=50)
	clincard = models.CharField(null=False, max_length=50)
	email = models.CharField(null=True, max_length=50)
	emergency_contact = models.CharField(null=True, max_length=200)
	emergency_contact_phone = models.CharField(null=True, max_length=50)
	address_1 = models.CharField(null=True, max_length=100)
	address_2 = models.CharField(null=True, max_length=100)
	address_city = models.CharField(null=True, max_length=50)
	address_state = models.CharField(null=True, max_length=20)
	address_zip = models.CharField(null=True, max_length=10)
	address_country = models.CharField(null=True, max_length=20)
	language = models.CharField(default=None, max_length=10)
	treatment = models.CharField(null=True, max_length=10)
	time_zone = models.CharField(default="PT", null=True, max_length=10)
	optout = models.BooleanField(default=False)
	deleted = models.BooleanField(default=False)
	cohort = models.IntegerField(default=0)
	test_account = models.BooleanField(default=False)
	sent_enrollment_survey = models.BooleanField(default=False)
	recruited_date = models.DateTimeField()
	recruited_by = models.ForeignKey(User, db_column='recruited_by', related_name='subjects_history_recruited_by', on_delete=models.PROTECT)
	recruited_location = models.CharField(default=None, max_length=20)
	notes = models.TextField(null=True)
	record_created_by = models.ForeignKey(User, db_column='record_created_by', related_name='subjects_history_record_created_by', on_delete=models.PROTECT)
	record_modified_by = models.ForeignKey(User, db_column='record_modified_by', related_name='subjects_history_record_modified_by', on_delete=models.PROTECT)
	ts_created = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "subjects_history"

	def lang(self):
		if self.language == "es":
			return "Spanish"
		return "English"

	def fullname(self):
		return self.first_name + ' ' + self.last_name

	# Phone number in the format (800) 555-1234
	def phone_number(self):
		phone = self.phone
		a = phone[2:5]
		b = phone[5:8]
		c = phone[8:12]
		return '(' + a + ')' + ' ' + b + '-' + c

	# Clincard without "_del_YYYY-MM-DD HH:SS:"
	def clincard_number(self):
		return self.clincard[0:8]

class Schedule(models.Model):

	study_id = models.OneToOneField(Subjects, to_field='study_id', db_column='study_id', related_name='schedule_study_id', on_delete=models.PROTECT)
	cohort = models.IntegerField()

	wk1_d1_survey_1 = models.OneToOneField('survey.SurveyLinks', db_column='wk1_d1_survey_1', related_name='wk1_d1_survey_1', on_delete=models.PROTECT)
	wk1_d1_survey_2 = models.OneToOneField('survey.SurveyLinks', db_column='wk1_d1_survey_2', related_name='wk1_d1_survey_2', on_delete=models.PROTECT)
	wk1_d1_survey_3 = models.OneToOneField('survey.SurveyLinks', db_column='wk1_d1_survey_3', related_name='wk1_d1_survey_3', on_delete=models.PROTECT)
	wk1_d1_survey_4 = models.OneToOneField('survey.SurveyLinks', db_column='wk1_d1_survey_4', related_name='wk1_d1_survey_4', on_delete=models.PROTECT)

	wk1_d2_survey_1 = models.OneToOneField('survey.SurveyLinks', db_column='wk1_d2_survey_1', related_name='wk1_d2_survey_1', on_delete=models.PROTECT)
	wk1_d2_survey_2 = models.OneToOneField('survey.SurveyLinks', db_column='wk1_d2_survey_2', related_name='wk1_d2_survey_2', on_delete=models.PROTECT)
	wk1_d2_survey_3 = models.OneToOneField('survey.SurveyLinks', db_column='wk1_d2_survey_3', related_name='wk1_d2_survey_3', on_delete=models.PROTECT)
	wk1_d2_survey_4 = models.OneToOneField('survey.SurveyLinks', db_column='wk1_d2_survey_4', related_name='wk1_d2_survey_4', on_delete=models.PROTECT)

	wk2_d1_survey_1 = models.OneToOneField('survey.SurveyLinks', db_column='wk2_d1_survey_1', related_name='wk2_d1_survey_1', on_delete=models.PROTECT)
	wk2_d1_survey_2 = models.OneToOneField('survey.SurveyLinks', db_column='wk2_d1_survey_2', related_name='wk2_d1_survey_2', on_delete=models.PROTECT)
	wk2_d1_survey_3 = models.OneToOneField('survey.SurveyLinks', db_column='wk2_d1_survey_3', related_name='wk2_d1_survey_3', on_delete=models.PROTECT)
	wk2_d1_survey_4 = models.OneToOneField('survey.SurveyLinks', db_column='wk2_d1_survey_4', related_name='wk2_d1_survey_4', on_delete=models.PROTECT)

	wk2_d2_survey_1 = models.OneToOneField('survey.SurveyLinks', db_column='wk2_d2_survey_1', related_name='wk2_d2_survey_1', on_delete=models.PROTECT)
	wk2_d2_survey_2 = models.OneToOneField('survey.SurveyLinks', db_column='wk2_d2_survey_2', related_name='wk2_d2_survey_2', on_delete=models.PROTECT)
	wk2_d2_survey_3 = models.OneToOneField('survey.SurveyLinks', db_column='wk2_d2_survey_3', related_name='wk2_d2_survey_3', on_delete=models.PROTECT)
	wk2_d2_survey_4 = models.OneToOneField('survey.SurveyLinks', db_column='wk2_d2_survey_4', related_name='wk2_d2_survey_4', on_delete=models.PROTECT)

	wk3_d1_survey_1 = models.OneToOneField('survey.SurveyLinks', db_column='wk3_d1_survey_1', related_name='wk3_d1_survey_1', on_delete=models.PROTECT)
	wk3_d1_survey_2 = models.OneToOneField('survey.SurveyLinks', db_column='wk3_d1_survey_2', related_name='wk3_d1_survey_2', on_delete=models.PROTECT)
	wk3_d1_survey_3 = models.OneToOneField('survey.SurveyLinks', db_column='wk3_d1_survey_3', related_name='wk3_d1_survey_3', on_delete=models.PROTECT)
	wk3_d1_survey_4 = models.OneToOneField('survey.SurveyLinks', db_column='wk3_d1_survey_4', related_name='wk3_d1_survey_4', on_delete=models.PROTECT)

	wk3_d2_survey_1 = models.OneToOneField('survey.SurveyLinks', db_column='wk3_d2_survey_1', related_name='wk3_d2_survey_1', on_delete=models.PROTECT)
	wk3_d2_survey_2 = models.OneToOneField('survey.SurveyLinks', db_column='wk3_d2_survey_2', related_name='wk3_d2_survey_2', on_delete=models.PROTECT)
	wk3_d2_survey_3 = models.OneToOneField('survey.SurveyLinks', db_column='wk3_d2_survey_3', related_name='wk3_d2_survey_3', on_delete=models.PROTECT)
	wk3_d2_survey_4 = models.OneToOneField('survey.SurveyLinks', db_column='wk3_d2_survey_4', related_name='wk3_d2_survey_4', on_delete=models.PROTECT)

	wk4_d1_survey = models.OneToOneField('survey.SurveyLinks', db_column='wk4_d1_survey', related_name='wk4_d1_survey', on_delete=models.PROTECT)
	wk4_d2_survey = models.OneToOneField('survey.SurveyLinks', db_column='wk4_d2_survey', related_name='wk4_d2_survey', on_delete=models.PROTECT)
	wk4_d3_survey = models.OneToOneField('survey.SurveyLinks', db_column='wk4_d3_survey', related_name='wk4_d3_survey', on_delete=models.PROTECT)

	wk14_d1_survey = models.OneToOneField('survey.SurveyLinks', db_column='wk14_d1_survey', related_name='wk14_d1_survey', on_delete=models.PROTECT)
	wk14_d2_survey = models.OneToOneField('survey.SurveyLinks', db_column='wk14_d2_survey', related_name='wk14_d2_survey', on_delete=models.PROTECT)
	wk14_d3_survey = models.OneToOneField('survey.SurveyLinks', db_column='wk14_d3_survey', related_name='wk14_d3_survey', on_delete=models.PROTECT)

	class Meta:
		db_table = "schedule"

class SchedulePlus(models.Model):

	study_id = models.ForeignKey(Subjects, to_field='study_id', db_column='study_id', on_delete=models.PROTECT)
	survey = models.CharField(max_length=200)
	survey_link = models.OneToOneField('survey.SurveyLinks', db_column='survey_link', on_delete=models.PROTECT, null=True)

	class Meta:
		db_table = "schedule_plus"
		unique_together = ("study_id", "survey")

class PaymentDetails(models.Model):

	study_id = models.ForeignKey(Subjects, to_field='study_id', db_column='study_id', on_delete=models.PROTECT)
	payment_for = models.CharField(max_length=20) # wk1_d1, wk1_d2, wk2_d1, wk2_d2, wk3_d1, wk3_d2, wk4_d1, wk4_d2, wk4_d3, wk14_d1, wk14_d2, wk14_d3
	surveys_completed = models.IntegerField(default=0)
	payment_for_completion = models.DecimalField(max_digits=6, decimal_places=2)
	random_survey_picked = models.CharField(max_length=20) # wk1_d1_survey_1
	survey_number = models.IntegerField()
	survey_number_type = models.CharField(max_length=20) # Risk, Time
	survey_status = models.IntegerField()
	survey_status_desc = models.CharField(max_length=20) # completed, Skipped, Time out etc
	random_survey_question = models.CharField(max_length=10, null=True) # q_10, q_11, q_20
	user_answer = models.IntegerField(null=True) # This could be char in future?
	random_answer_computer_picked = models.IntegerField(null=True) # This could be char in future?
	randomization_outcome = models.CharField(max_length=50, null=True) # Sure payment of $6, Did not win lottery.
	randomization_outcome_payment = models.DecimalField(max_digits=6, decimal_places=2, null=True)
	pay_today = models.DecimalField(max_digits=6, decimal_places=2, null=True)
	pay_5wks = models.DecimalField(max_digits=6, decimal_places=2, null=True)
	pay_10wks = models.DecimalField(max_digits=6, decimal_places=2, null=True)
	message = models.TextField()
	generated_on = models.DateTimeField(auto_now_add=True)
	ts_updated = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "payment_details"
		unique_together = ("study_id", "payment_for")

class PaymentSummary(models.Model):

	payment_id = models.ForeignKey(PaymentDetails, db_column='payment_id', on_delete=models.PROTECT)
	payment_type = models.CharField(max_length=20) # pay_today, pay_5wks, pay_10wks
	payment_amount = models.DecimalField(max_digits=6, decimal_places=2)
	payment_date = models.DateTimeField()
	payment_message = models.TextField()
	clincard_processed = models.BooleanField(default=False) # 0, 1
	notified_user = models.BooleanField(default=False) # 0, 1
	processed_by = models.ForeignKey(User, db_column='processed_by', related_name='payment_processed_by', on_delete=models.PROTECT, null=True)
	processed_on = models.DateTimeField(null=True)
	ts_created = models.DateTimeField(auto_now_add=True)
	ts_updated = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "payment_summary"
