# python3 manage.py shell < _export_data.py

from survey.models import *
from subjects.models import Subjects, Schedule, SchedulePlus
from datetime import datetime
from django.conf import settings
from django.db import IntegrityError
from datetime import datetime

# schedules = Schedule.objects.filter(study_id=Subjects(study_id=100))
SchedulePlus.objects.all().delete()
schedules = Schedule.objects.all()

for s in schedules:

	# Week 1
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk1_d1_survey_1", survey_link=s.wk1_d1_survey_1)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk1_d1_survey_2", survey_link=s.wk1_d1_survey_2)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk1_d1_survey_3", survey_link=s.wk1_d1_survey_3)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk1_d1_survey_4", survey_link=s.wk1_d1_survey_4)

	SchedulePlus.objects.create(study_id=s.study_id, survey="wk1_d2_survey_1", survey_link=s.wk1_d2_survey_1)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk1_d2_survey_2", survey_link=s.wk1_d2_survey_2)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk1_d2_survey_3", survey_link=s.wk1_d2_survey_3)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk1_d2_survey_4", survey_link=s.wk1_d2_survey_4)

	# Week 2
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk2_d1_survey_1", survey_link=s.wk2_d1_survey_1)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk2_d1_survey_2", survey_link=s.wk2_d1_survey_2)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk2_d1_survey_3", survey_link=s.wk2_d1_survey_3)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk2_d1_survey_4", survey_link=s.wk2_d1_survey_4)

	SchedulePlus.objects.create(study_id=s.study_id, survey="wk2_d2_survey_1", survey_link=s.wk2_d2_survey_1)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk2_d2_survey_2", survey_link=s.wk2_d2_survey_2)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk2_d2_survey_3", survey_link=s.wk2_d2_survey_3)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk2_d2_survey_4", survey_link=s.wk2_d2_survey_4)

	# Week 3
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk3_d1_survey_1", survey_link=s.wk3_d1_survey_1)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk3_d1_survey_2", survey_link=s.wk3_d1_survey_2)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk3_d1_survey_3", survey_link=s.wk3_d1_survey_3)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk3_d1_survey_4", survey_link=s.wk3_d1_survey_4)

	SchedulePlus.objects.create(study_id=s.study_id, survey="wk3_d2_survey_1", survey_link=s.wk3_d2_survey_1)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk3_d2_survey_2", survey_link=s.wk3_d2_survey_2)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk3_d2_survey_3", survey_link=s.wk3_d2_survey_3)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk3_d2_survey_4", survey_link=s.wk3_d2_survey_4)

	# Week 4
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk4_d1_survey", survey_link=s.wk4_d1_survey)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk4_d2_survey", survey_link=s.wk4_d2_survey)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk4_d3_survey", survey_link=s.wk4_d3_survey)

	# Week 14
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk14_d1_survey", survey_link=s.wk14_d1_survey)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk14_d2_survey", survey_link=s.wk14_d2_survey)
	SchedulePlus.objects.create(study_id=s.study_id, survey="wk14_d3_survey", survey_link=s.wk14_d3_survey)


