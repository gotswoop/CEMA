from django.db import models
from django.contrib.auth.models import User

class Short_Urls(models.Model):
	url_long = models.CharField(unique=True,max_length=250)
	url_short = models.CharField(unique=True,max_length=16)
	active = models.IntegerField(default=1)
	generated_by = models.ForeignKey(User, db_column='generated_by', on_delete=models.PROTECT)
	ts_created = models.DateTimeField(auto_now_add=True)
	ts_updated = models.DateTimeField(auto_now=True)

	class Meta:
		# TODO: is this required??
		unique_together = ("url_long", "url_short")
		db_table = "short_urls"