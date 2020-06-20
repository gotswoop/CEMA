from subjects.models import Subjects, Subjects_History
from sms.models import SMS_Outgoing
from survey.functions import *
from django.db import IntegrityError
from datetime import datetime
from django.contrib.auth.models import User
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from django.core.mail import EmailMessage
from django.conf import settings

def insert_into_subjects_history(user_obj):
	Subjects_History.objects.create(
		study_id = user_obj.study_id,
		first_name = user_obj.first_name,
		last_name = user_obj.last_name,
		phone = user_obj.phone,
		clincard = user_obj.clincard,
		email = user_obj.email,
		emergency_contact = user_obj.emergency_contact,
		emergency_contact_phone = user_obj.emergency_contact_phone,
		address_1 = user_obj.address_1,
		address_2 = user_obj.address_2,
		address_city = user_obj.address_city,
		address_state = user_obj.address_state,
		address_zip = user_obj.address_zip,
		address_country = user_obj.address_country,
		language = user_obj.language,
		treatment = user_obj.treatment,
		time_zone = user_obj.time_zone,
		optout = user_obj.optout,
		deleted = user_obj.deleted,
		cohort = user_obj.cohort,
		test_account = user_obj.test_account,
		sent_enrollment_survey = user_obj.sent_enrollment_survey,
		recruited_date = user_obj.recruited_date,
		recruited_by = user_obj.recruited_by,
		recruited_location = user_obj.recruited_location,
		notes = user_obj.notes,
		record_created_by = user_obj.record_created_by, 
		record_modified_by = user_obj.record_modified_by,
	)

def send_enrollment_survey(request, user_obj):
	survey_obj = generate_survey_link(123, user_obj.study_id)
	survey_link = ('https://' if request.is_secure() else 'http://') + request.get_host() + '/s/' + survey_obj.survey_key
	sms_to = user_obj.phone
	sms_body = survey_link
	sms_result = send_sms(sms_to, sms_body)
	if sms_result['error'] == None:
		try:
			sms_outgoing_obj = SMS_Outgoing.objects.create(
				from_phone=settings.TWILIO_FROM_NUMBER,
				to_phone=sms_to,
				message=sms_body,
				send_after=datetime.today(),
				sent=1,
				sent_on=datetime.today(),
				sent_sid=sms_result['sms_sid'],
				study_id=user_obj,
				sent_by_user=User(id=request.user.id),
				survey_link=survey_obj,
				send_mode="auto"
			)
		except IntegrityError as e:
			msg = '# ERROR (send_enrollment_survey): MySQL ' + str(e.args)
			return msg
	else:
		msg = '# ERROR (send_enrollment_survey): ' + sms_result['error_message']
		print(msg)
		return msg

	return None

def send_sms(sms_to, sms_body):

	result = {'error': None, 'sms_sid': None, 'error_message': None}
	account_sid = settings.TWILIO_ACCOUNT_SID
	auth_token = settings.TWILIO_AUTH_TOKEN
	client = Client(account_sid, auth_token)
	from_number = settings.TWILIO_FROM_NUMBER

	sms_from = from_number

	sms = client.messages.create(
		body=sms_body,
		from_=from_number, # TODO: Switch to using sms_from
		to=sms_to,
	)

	if (sms.status != 'failed') and (sms.status != 'undelivered') :
		result['sms_sid'] = sms.sid
	else:
		result['error'] = "FAIL"
		result['sms_sid'] = sms.sid
		result['error_message'] = '# ERROR: ' + str(datetime.today()) + ' SMS send error to ' + sms_to + ' - ' + sms_body + '. Sid: ' + sms.sid + '. Status: ' + sms.status + '. Error code: ' + str(sms.error_code) + '. Error message: ' + str(sms.error_message)

	return result

def send_email_to_admins(email_subject, email_body):

	to_emails=settings.ADMIN_NOTIFICATION_EMAILS
	notify_admins = EmailMessage(email_subject, email_body, settings.EMAIL_HOST_USER, to_emails, reply_to=['beelab-northgate-l@mymaillists.usc.edu'])
	notify_admins.send()


def build_subject_enrollment_notification_message(user_obj):

	email_subject = '[Enrollment] ' + user_obj.recruited_by.first_name + ' enrolled ' + user_obj.fullname() + ' (' + str(user_obj.study_id) + ') at '  + user_obj.recruited_location

	email_body = ''
	
	if user_obj.test_account == 1:
		email_body = '[BeeLab Test Account]\n\n'
	
	email_body += 'Study Id: ' + str(user_obj.study_id)  + '\nName: ' + user_obj.fullname() + '\nPhone: ' + user_obj.phone_number() + '\nClincard #: ' + user_obj.clincard_number() + '\n Language: ' + user_obj.lang() + '\nInterviewer: ' + user_obj.recruited_by.first_name + ' ' + user_obj.recruited_by.last_name + '\nLocation: ' + user_obj.recruited_location + '\nCohort: ' + str(user_obj.cohort) + '\n Recruited Date: ' + str(user_obj.recruited_date) + '\nDemo survey sent? '

	if user_obj.sent_enrollment_survey:
		email_body += 'Yes'
	else: 
		email_body += 'No'

	return email_subject, email_body

			
def build_subject_update_notification_message(user_obj, old_user_obj):

	email_subject = '[User updated] ' + user_obj.record_modified_by.first_name + ' updated ' + user_obj.fullname() + '\'s (' + str(user_obj.study_id) + ') information'

	email_body = 'Study Id: ' + str(user_obj.study_id)

	email_body += '\n\nName: ' + user_obj.fullname() + '\nPhone: ' + user_obj.phone_number() + '\nClincard #: ' + user_obj.clincard_number() + '\n Language: ' + user_obj.lang() + '\nLocation: ' + user_obj.recruited_location + '\nCohort: ' + str(user_obj.cohort) + '\nBeeLab Test Account: '

	if user_obj.test_account == 1:
		email_body += 'Yes'
	else:
		email_body += 'No'

	email_body += '\nOpted-Out: '	
	if user_obj.optout == 1:
		email_body += 'Yes'
	else:
		email_body += 'No'

	email_body += '\nDeleted: '	
	if user_obj.deleted == 1:
		email_body += 'Yes'
	else:
		email_body += 'No'

	if user_obj.notes != None:
		email_body += '\n Notes:\n' + '\t'.join(('\n'+user_obj.notes.lstrip()).splitlines(True))

	# Showing old record. If exists
	if old_user_obj.count():

		old_user_obj = old_user_obj[0]
		
		email_body += '\n\n-------------------------------------------------------------------\nOld Record\n-------------------------------------------------------------------'
		email_body += '\nName: ' + old_user_obj.fullname() + '\nPhone: ' + old_user_obj.phone_number() + '\nClincard #: ' + old_user_obj.clincard_number() + '\n Language: ' + old_user_obj.lang() + '\nLocation: ' + old_user_obj.recruited_location + '\nCohort: ' + str(old_user_obj.cohort) + '\nBeeLab Test Account: '
		if old_user_obj.test_account == 1:
			email_body += 'Yes'
		else:
			email_body += 'No'

		email_body += '\nOpted-Out: '	
		if old_user_obj.optout == 1:
			email_body += 'Yes'
		else:
			email_body += 'No'

		email_body += '\nDeleted: '	
		if old_user_obj.deleted == 1:
			email_body += 'Yes'
		else:
			email_body += 'No'

		if old_user_obj.notes !=None:
			email_body += '\n Notes:\n' + '\t'.join(('\n'+old_user_obj.notes.lstrip()).splitlines(True))

	return email_subject, email_body


