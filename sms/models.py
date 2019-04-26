from django.db import models
from django.contrib.auth.models import User
from subjects.models import Subjects

class SMS_Incoming(models.Model):
	study_id = models.ForeignKey(Subjects, to_field='study_id', db_column='study_id', on_delete=models.PROTECT, null=True)
	to_phone = models.CharField(null=True, max_length=100)
	from_phone = models.CharField(null=True, max_length=100)
	message = models.TextField(null=True)
	attachments = models.TextField(null=True)
	raw_incoming = models.TextField(null=True)
	ts_created = models.DateTimeField(auto_now_add=True)
	ts_updated = models.DateTimeField(auto_now=True)
	processed = models.IntegerField(default=0)
	
	class Meta:
		db_table = "sms_incoming"

class SMS_Outgoing(models.Model):
	study_id = models.ForeignKey(Subjects, to_field='study_id', db_column='study_id', on_delete=models.PROTECT)
	from_phone = models.CharField(null=True, max_length=100)
	to_phone = models.CharField(null=True, max_length=100)
	message = models.TextField(null=True)
	send_after = models.DateTimeField(null=True)
	sent = models.IntegerField(default=0)
	sent_on = models.DateTimeField(null=True)
	sent_sid = models.CharField(null=True, max_length=200)
	sent_by_user = models.ForeignKey(User, db_column='sent_by_user', on_delete=models.PROTECT, null=True)
	send_mode = models.CharField(default="auto", max_length=10, null=True)
	ts_created = models.DateTimeField(auto_now_add=True)
	ts_updated = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ("to_phone", "send_after", "send_mode")
		db_table = "sms_outgoing"
