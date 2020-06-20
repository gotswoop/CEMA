from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from sms.models import SMS_Incoming, SMS_Outgoing
from .models import Subjects, Schedule, PaymentDetails, PaymentSummary
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import SMS_Form, RecruitForm, EditSubjectForm

from datetime import datetime
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect

from django.core.mail import EmailMessage
from subjects.functions import send_enrollment_survey, send_sms, send_email_to_admins
import xlwt

@login_required()
def subjects_all(request):
	
	# To prevent BeeLab folks from accidentally deleting these accounts
	hide_test_accounts = (109, 110)

	subjects_active = Subjects.objects.filter(optout=0, deleted=0, test_account=0).order_by('-study_id')
	subjects_inactive = Subjects.objects.filter(optout=1, deleted=0).order_by('-study_id')
	subjects_test = Subjects.objects.exclude(study_id__in=hide_test_accounts).filter(optout=0, deleted=0, test_account=1).order_by('-study_id')
	subjects_deleted = Subjects.objects.filter(deleted=1).order_by('-study_id')

	context = {
		'title': 'Subjects',
		'subjects_active': subjects_active,
		'subjects_inactive': subjects_inactive,
		'subjects_test': subjects_test,
		'subjects_deleted': subjects_deleted,
	}
	return render(request, 'subjects/all.html', context)

# TODO: clean up messages. check for junk
@login_required()
def subject_details(request, study_id):

	sms_from = settings.TWILIO_FROM_NUMBER

	if request.method == 'POST':
		form = SMS_Form(request.POST)
		if form.is_valid():
			study_id = request.POST.get("study_id", "")
			sms_to = request.POST.get("to_phone", "")
			sms_body = request.POST.get("sms_message", "")
			
			try:
				sub_obj = Subjects.objects.get(study_id=study_id)
			except Subjects.DoesNotExist:
				msg = '# ERROR: No account found for participant with study id ' + str(study_id)
				return HttpResponse(msg)

			if sub_obj.phone != sms_to:
				msg = '# ERROR: Cannot proceed as provided number (' + str(sms_to) + ') does not match for phone number on record for study id ' + str(study_id)
				return HttpResponse(msg)

			# Checking if user has opted out
			if sub_obj.optout != 0:
				msg = '# ERROR: ' + str(datetime.today()) + ' Message not sent as user with study id ' + str(study_id) + ' (' + sms_to + ') has opted to not receive texts'
				return HttpResponse(msg)
		
			try:
				user_obj = User.objects.get(username = request.user)
			except User.DoesNotExist:
				msg = 'Not authorized to send texts'
				return HttpResponse(msg)		

			sms_result = send_sms(sms_to, sms_body)
			if sms_result['error'] == None:
				# good
				try:
					sms_outgoing_obj = SMS_Outgoing.objects.create(from_phone=sms_from, to_phone=sms_to, message=sms_body, send_after=datetime.today(), sent=1, sent_on=datetime.today(), sent_sid=sms_result['sms_sid'], study_id=sub_obj, sent_by_user=user_obj, send_mode="manual")
				except IntegrityError as e:
					msg = '# ERROR: MySQL ' + str(e.args)
					return HttpResponse(msg)

				# Setting processsed = 1 after replying to a message, and only for messages in the past
				today = datetime.today()
				SMS_Incoming.objects.filter(study_id=sub_obj,ts_created__lte=today).update(processed=1)

				# Notifying the group that someone responded
				email_subject = 'Outgoing text from ' + user_obj.first_name + ' to ' + sub_obj.fullname() + ' (' + str(sub_obj.study_id) + ')'
				email_body = user_obj.first_name + ' ' + user_obj.last_name + ' sent a message to ' + sub_obj.fullname() + ' (' + str(sub_obj.study_id) + ') @ ' + sub_obj.phone_number() + '\n\nMessage: ' + sms_body + '\n\n---\nHistory:\n'
				send_email_to_admins(email_subject, email_body)

				print('# OK: ' + str(datetime.today()) + ' - ' + sms_result['sms_sid'] + ' - ' + sms_to + ' - ' + sms_body)
				messages.success(request, format('Message "' + sms_body + '" sent!!'))
				return redirect('subject_details', study_id=study_id)
			else:
				# bad
				msg = sms_result['error_message']
				return HttpResponse(msg)
	else:
		form = SMS_Form()
		chat_list = []

		try:
			subject = Subjects.objects.get(study_id=study_id)
		except Subjects.DoesNotExist:
			msg = '# ERROR: No account found for participant with study id ' + str(study_id)
			return HttpResponse(msg)

		# Fetching all messages in queue
		messages_queue = SMS_Outgoing.objects.filter(sent=0).filter(study_id=study_id).order_by('send_after')
		
		# fetching all sent messages
		messages_sent = SMS_Outgoing.objects.filter(sent=1).filter(study_id=study_id)
		# Building a chat list of outgoing messages
		for msg in messages_sent:
			# message timestamp, incoming(1,0), message, message_sent_by, send_mode, processed)
			chat_list.append(tuple((msg.sent_on, 0, msg.message, msg.sent_by_user, msg.send_mode, None)))
		
		# Fetching all received messages
		messages_incoming = SMS_Incoming.objects.filter(study_id=study_id)
		# Adding incoming messages to the chat list
		for msg in messages_incoming:
			# message timestamp, incoming(1,0), message, message_sent_by, send_mode, processed)
			chat_list.append(tuple((msg.ts_created, 1, msg.message, None, None, msg.processed)))
		
		# sort the chat list by date
		chat_list_sorted_by_date = sorted(chat_list, key=lambda tup: tup[0], reverse=True)
		
		if subject.optout == 1 or subject.deleted == 1:
			form = None
		context = {
			'title': "User Details",
			'form': form,
			'subject': subject,
			'chat': chat_list_sorted_by_date,
			'msgs_sent': messages_sent,
			'msgs_queue': messages_queue,
			'msgs_incoming': messages_incoming,
		}	 
		return render(request, 'subjects/details.html', context)
	
# TODO: clean up messages. check for junk
@login_required()
def subject_edit(request, study_id):

	try:
		subj_obj = Subjects.objects.get(study_id=study_id)
	except Subjects.DoesNotExist:
		msg = '# ERROR: No account found for participant with study id ' + str(study_id)
		return HttpResponse(msg)

	# POST	
	if request.method == 'POST': 
		form = EditSubjectForm(request.POST, instance=subj_obj)
		if form.is_valid():
			updated_user_obj = form.save(commit=False)
			updated_user_obj.record_modified_by = request.user
			# setting phone to something not unique when deleting an account
			if updated_user_obj.deleted:
				updated_user_obj.phone = updated_user_obj.phone + '_del_' + str(datetime.today())
				updated_user_obj.clincard = updated_user_obj.clincard + '_del_' + str(datetime.today())
			updated_user_obj.save()	
			message = updated_user_obj.fullname() + " was successfully updated!"
			messages.success(request, format(message))
			return redirect('subject_details', study_id=updated_user_obj.pk)
	# GET 		
	else:
		init_data={
			'phone': subj_obj.phone_number_with_dashes(),
			'clincard': subj_obj.clincard_number(),
		}
		initial=init_data	
		form = EditSubjectForm(instance=subj_obj, initial=init_data)
	
	context = {
		'form': form,
		'subject': subj_obj,
	}
	return render(request, 'subjects/edit.html', context)
	
@login_required()
def subject_recruit(request):
	# Req = POST
	if request.method == 'POST':
		form = RecruitForm(request.POST)
		if form.is_valid():
			new_user_obj = form.save(commit=False)
			new_user_obj.record_created_by = request.user
			new_user_obj.record_modified_by = request.user
			new_user_obj.save()
			if new_user_obj.sent_enrollment_survey:
				# TODO: This returns None or an error
				send_enrollment_survey(request, new_user_obj)
				message = new_user_obj.fullname() + " was successfully registered, and a test survey link was sent!"
			else:
				message = new_user_obj.fullname() + " was successfully registered!"

			messages.success(request, format(message))
			return redirect('subject_details', study_id=new_user_obj.pk)
	# Req = GET
	else:
		init_data={
			'recruited_by': request.user.id,
		}
		form = RecruitForm(initial=init_data)

	return render(request, 'subjects/add.html', {'form': form})

@login_required()
def subjects_dashboard(request, cohort):

	schedules = Schedule.objects.filter(cohort=cohort).order_by('-study_id')

	context = {
		'title': 'Status',
		'schedules': schedules,
		'cohort': cohort,
	}
	return render(request, 'subjects/dashboard.html', context)

@login_required()
def subjects_download(request):

	response = HttpResponse(content_type='application/ms-excel')
	response['Content-Disposition'] = 'attachment; filename="NG_Study_Users.xls"'

	wb = xlwt.Workbook(encoding='utf-8')
	ws_1 = wb.add_sheet('Active Users')
	ws_2 = wb.add_sheet('Inactive Users')

	# Active Users
	# Sheet header, first row
	row_num = 0

	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	columns = ['Study Id', 'First name', 'Last name', 'Language', 'Phone', 'Clincard', 'Recruited By', 'Recruited On', 'Recruited Location', 'Study Cohort', 'Notes' ]

	for col_num in range(len(columns)):
		ws_1.write(row_num, col_num, columns[col_num], font_style)

	# Sheet body, remaining rows
	font_style = xlwt.XFStyle()

	users = Subjects.objects.filter(deleted=0, optout=0, test_account=0).order_by('-study_id')
	for user in users:
		row = [
			user.study_id, user.first_name, user.last_name, user.lang(), user.phone_number(), user.clincard, user.recruited_by.first_name + ' ' + user.recruited_by.last_name,
			user.recruited_date.strftime("%Y-%m-%d"), user.recruited_location, user.cohort, user.notes
		]
		row_num += 1
		for col_num in range(len(row)):
			ws_1.write(row_num, col_num, row[col_num], font_style)


	# Inactive Users
	# Sheet header, first row
	row_num = 0

	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	columns = ['Study Id', 'First name', 'Last name', 'Language', 'Phone', 'Clincard', 'Recruited By', 'Recruited On', 'Recruited Location', 'Study Cohort', 'Notes' ]

	for col_num in range(len(columns)):
		ws_2.write(row_num, col_num, columns[col_num], font_style)

	# Sheet body, remaining rows
	font_style = xlwt.XFStyle()

	users = Subjects.objects.filter(deleted=0, optout=1, test_account=0).order_by('-study_id')
	for user in users:
		row = [
			user.study_id, user.first_name, user.last_name, user.lang(), user.phone_number(), user.clincard, user.recruited_by.first_name + ' ' + user.recruited_by.last_name,
			user.recruited_date.strftime("%Y-%m-%d"), user.recruited_location, user.cohort, user.notes
		]
		row_num += 1
		for col_num in range(len(row)):
			ws_2.write(row_num, col_num, row[col_num], font_style)

	wb.save(response)
	return response

@login_required()
def payments_all(request):

	today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	payments_today_pending = PaymentSummary.objects.filter(payment_date__lte=today, processed_on=None).order_by('payment_date')
	payments_today_done = PaymentSummary.objects.exclude(processed_on=None).filter(payment_date=today).order_by('payment_date')

	payments_later = PaymentSummary.objects.filter(payment_date__gt=today).order_by('payment_date')
	payments_past = PaymentSummary.objects.exclude(processed_on=None).filter(payment_date__lt=today).order_by('-payment_date')

	context = {
		'title': 'Payments',
		'payments_today_pending': payments_today_pending,
		'payments_today_done': payments_today_done,
		'payments_later': payments_later,
		'payments_past': payments_past,
	}
	return render(request, 'subjects/payments_all.html', context)

@login_required()
def payment_details(request, id):

	if request.method == 'POST':
		pass
	else:
		try:
			payment_summary = PaymentSummary.objects.get(id=id)
		except PaymentSummary.DoesNotExist:
			msg = 'Uh oh, Invalid payment details. Please notify the system administrator'
			return HttpResponse(msg)

		context = {
			'title': 'Payment Details',
			'p': payment_summary,
		}
		return render(request, 'subjects/payment_details.html', context)

@login_required()
def subject_details_back(request, study_id):
	 # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SMS_Form(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            # TODO: create a message header and send back to this page.
            return HttpResponse('Thanks')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SMS_Form()

    return render(request, 'subjects/details.html', {'form': form})
