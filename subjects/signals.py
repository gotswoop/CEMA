from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from subjects.models import Subjects, Subjects_History
from subjects.functions import insert_into_subjects_history, send_email_to_admins, build_subject_enrollment_notification_message, build_subject_update_notification_message

@receiver(post_save, sender=Subjects)
def subjects_save_signal(sender, **kwargs):
	user_obj = kwargs.get('instance', None)
	created = kwargs.get('created', None)
	if user_obj:
		insert_into_subjects_history(user_obj)
		# If new user
		if created:
			email_subject, email_body = build_subject_enrollment_notification_message(user_obj)
			send_email_to_admins(email_subject, email_body)
		else:
			old_user_obj = Subjects_History.objects.filter(study_id=user_obj.study_id).order_by('-ts_created')[1:2]
			# Notifying the group about the changes to the study participant
			email_subject, email_body = build_subject_update_notification_message(user_obj, old_user_obj)
			send_email_to_admins(email_subject, email_body)
