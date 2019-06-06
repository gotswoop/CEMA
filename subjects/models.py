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
	clincard = models.CharField(null=False, blank=False, max_length=50, unique=True)
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
	recruited_date = models.DateTimeField(auto_now_add=True)
	recruited_by = models.ForeignKey(User, db_column='recruited_by', on_delete=models.PROTECT)
	recruited_location = models.CharField(blank=False, default=None, max_length=20, choices=LOCATION_CHOICES)
	notes = models.TextField(null=True, blank=True)
	ts_created = models.DateTimeField(auto_now_add=True)
	ts_updated = models.DateTimeField(auto_now=True)
	
	class Meta:
		db_table = "subjects"

	def lang(self):
		if self.language == "es":
			return "Spanish"
		return "English"

	def fullname(self):
		return self.first_name + ' ' + self.last_name

	# Fetching primary phone number (TODO) and return it in format (XXX) XXX-XXXX
	def phone_number(self):
		# TODO: get primary phone 
		primary_number = self.phone
		a = primary_number[2:5]
		b = primary_number[5:8]
		c = primary_number[8:12]
		return '(' + a + ')' + ' ' + b + '-' + c

	def phone_number_with_dashes(self):
		primary_number = self.phone
		a = primary_number[2:5]
		b = primary_number[5:8]
		c = primary_number[8:12]
		return a + '-' + b + '-' + c

	
