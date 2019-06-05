from django.db import models
from .survey_links import SurveyLinks

class SurveyData(models.Model):
	survey_link = models.ForeignKey(SurveyLinks, db_column='survey_link', on_delete=models.PROTECT)
	question = models.CharField(max_length=50)
	response = models.CharField(max_length=50)
	user_ip = models.CharField(max_length=15)
	ts_response = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		db_table = "survey_data"
		unique_together = ("survey_link", "question")

