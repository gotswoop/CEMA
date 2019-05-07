from django import forms

class SMS_Form(forms.Form):
	sms_message = forms.CharField(label='Message Body:', max_length=160)
