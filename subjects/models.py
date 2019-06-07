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
	
