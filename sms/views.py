import json
from django.shortcuts import render
from twilio.twiml.messaging_response import MessagingResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from sms.models import SMS_Incoming, SMS_Outgoing
from subjects.models import Subjects
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
from subjects.functions import send_email_to_admins

@login_required()
def sms_queue(request):
	messages = SMS_Outgoing.objects.filter(sent=0).order_by('send_after','study_id')

	context = {
		'title': "Outbound Messages",
		'msgs': messages,
	}
	return render(request, 'sms/queue.html', context)

@login_required()
def sms_sent(request):
	messages = SMS_Outgoing.objects.filter(sent=1).order_by('-sent_on')

	context = {
		'title': "Sent Messages",
		'msgs': messages,
	}
	return render(request, 'sms/sent.html', context)

@login_required()
def sms_inbox(request):
	unread_msgs = SMS_Incoming.objects.filter(processed=0).order_by('-ts_created')
	read_msgs = SMS_Incoming.objects.filter(processed=1).order_by('-ts_created')
	context = {
		'title': "Inbox",
		'unread_msgs': unread_msgs,
		'read_msgs': read_msgs,
	}
	return render(request, 'sms/inbox.html', context)

@login_required()
@require_http_methods(["POST"])
def sms_send(request):
	return HttpResponse('<h4>SENT</h4')

# Webhook
@require_http_methods(["POST"])
@csrf_exempt
def incoming_sms(request):

	phone_not_found = False

	incoming = request.POST
	# TODO: Log this to the LOGGER
	print(incoming)
	
	if not incoming:
		return HttpResponse('')

	# Search for other phone numbers here!!
	try:
		sub_obj = Subjects.objects.get(phone=incoming.get('From'))
	except Subjects.DoesNotExist:
		phone_not_found = True

	text_response = 'Thank you for your message. We will get back to you shortly.'
	if phone_not_found:
		study_id = None
		email_subject = 'Incoming text from ' + incoming.get('From') + ' (unrecognized)'
		email_body = 'Sender not recognized based on phone number: ' + incoming.get('From') + '\n\nMessage: ' + incoming.get('Body')
	else:
		study_id = sub_obj
		if sub_obj.language == "es":
			text_response = 'Gracias por su mensaje. Le responderemos pronto.'
		email_subject = 'Incoming text from ' + sub_obj.fullname() + ' (' + str(sub_obj.study_id) + ')'
		email_body = 'From: ' + sub_obj.fullname() + ' (' + str(sub_obj.study_id) + ') @ ' + sub_obj.phone_number() + '\n\nMessage: ' + incoming.get('Body')
	
	# TODO: If images show them!
	send_email_to_admins(email_subject, email_body)

	try:
		message = SMS_Incoming.objects.create(
			to_phone = incoming.get('To'),
			from_phone = incoming.get('From'),
			message = incoming.get('Body'),
			raw_incoming = incoming,
			study_id = study_id,
		)
	except IntegrityError as e:
		msg = '# ERROR: MySQL ' + str(e.args)
		print(msg)

	# TODO: Rate limit responses
	response = '<?xml version="1.0" encoding="UTF-8"?><Response><Message>' + text_response + '</Message></Response>'
	# Not responding for now...
	response = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
	return HttpResponse(response, content_type='text/xml')

def pretty_print_response(response):
	print(json.dumps(response, indent=2, sort_keys=True))

