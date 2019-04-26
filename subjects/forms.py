from django import forms

class SMS_Form(forms.Form):
	sms_message = forms.CharField(label='Type Text Message', max_length=160)