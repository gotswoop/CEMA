from django.db import models
from django.contrib.auth.models import User

class Subjects(models.Model):
	study_id = models.CharField(max_length=30, primary_key=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	phone_1 = models.CharField(max_length=50)
	phone_2 = models.CharField(null=True, max_length=50)
	phone_3 = models.CharField(null=True, max_length=50)
	phone_primary = models.IntegerField(default=1)
	email_1 = models.CharField(max_length=50)
	email_2 = models.CharField(null=True, max_length=50)
	email_3 = models.CharField(null=True, max_length=50)
	email_primary = models.IntegerField(default=1)
	emergency_contact = models.CharField(null=True, max_length=200)
	emergency_contact_phone = models.CharField(null=True, max_length=50)
	address_1 = models.CharField(null=True, max_length=100)
	address_2 = models.CharField(null=True, max_length=100)
	address_city = models.CharField(null=True, max_length=50)
	address_state = models.CharField(null=True, max_length=20)
	address_zip = models.CharField(null=True, max_length=10)
	address_country = models.CharField(null=True, max_length=20)
	language = models.CharField(default="English", max_length=10)
	treatment = models.CharField(null=True, max_length=10)
	time_zone = models.CharField(default="PT", null=True, max_length=10)
	optout = models.IntegerField(default=0)
	optout_reason = models.TextField(null=True)
	optout_date = models.DateTimeField(null=True)
	recruited_date = models.DateTimeField(null=True)
	# recruited_by = models.ForeignKey(User, db_column='recruited_by', on_delete=models.PROTECT, null=True)
	recruited_by = models.CharField(null=True, max_length=100)
	recruited_location = models.TextField(null=True)
	notes = models.TextField(null=True)
	ts_created = models.DateTimeField(auto_now_add=True)
	ts_updated = models.DateTimeField(auto_now=True)
	
	class Meta:
		db_table = "subjects"
