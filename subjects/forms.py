from django import forms
from subjects.models import Subjects
import re

class SMS_Form(forms.Form):
	sms_message = forms.CharField(label='Message Body:', max_length=1000, widget=forms.Textarea(attrs={'rows': 5}))

class RecruitForm(forms.ModelForm):

	send_test_survey = forms.BooleanField(label="<span class='text-danger'><strong>SEND DEMO SURVEY? </strong></span> This sends a text message with a link to the Demo Survey (Risk + Time)",required=False,initial=True)

	def clean_phone(self):

		phone = self.cleaned_data.get('phone')

		rgxpattern='^\d{3}-\d{3}-\d{4}$'
		regexp = re.compile(rgxpattern)

		if not regexp.match(phone):
			raise forms.ValidationError("Please enter phone number in the format xxx-xxx-xxxx")
		
		phone_db = '+1' + phone.replace("-","")
		
		if Subjects.objects.filter(phone=phone_db).exists():
			raise forms.ValidationError("A user with this phone number already exists")
		return phone_db

	def clean_clincard(self):

		clincard = self.cleaned_data.get('clincard')

		rgxpattern='^\d{8}$'
		regexp = re.compile(rgxpattern)

		if not regexp.match(clincard):
			raise forms.ValidationError("Please enter an 8 digit clincard number in the format xxxxxxxx")
				
		if Subjects.objects.filter(clincard=clincard).exists():
			raise forms.ValidationError("A user with this clincard number already exists")
		
		return clincard

	class Meta:
		model = Subjects
		fields = ['first_name', 'last_name', 'phone', 'clincard', 'language', 'recruited_by', 'recruited_location', 'test_account']
		labels = {
        	"phone": "Phone:",
        	"clincard": "Clincard Number:",
        	"test_account": "<span class='text-info'><strong>This is a BeeLab (test) user</strong></span>",
    	}
		widgets = {
			'phone': forms.TextInput(attrs={"required": "required", "placeholder": "xxx-xxx-xxxx"}),
			'clincard': forms.TextInput(attrs={"required": "required", "placeholder": "xxxxxxxx"}),
			'language': forms.RadioSelect(attrs={"required": "required"}),
			'recruited_location': forms.RadioSelect(attrs={"required": "required"}),
			'recruited_by': forms.HiddenInput(),
		}

class EditSubjectForm(forms.ModelForm):

	def clean_phone(self):

		phone = self.cleaned_data.get('phone')

		rgxpattern='^\d{3}-\d{3}-\d{4}$'
		regexp = re.compile(rgxpattern)

		if not regexp.match(phone):
			raise forms.ValidationError("Please enter phone number in the format xxx-xxx-xxxx")

		phone_db = '+1' + phone.replace("-","")

		# checking if unqiue after excluding current user
		if Subjects.objects.exclude(study_id=self.instance.study_id).filter(phone=phone_db).exists():
			raise forms.ValidationError("A user with this phone number already exists")
		return phone_db

	def clean_clincard(self):

		clincard = self.cleaned_data.get('clincard')

		rgxpattern='^\d{8}$'
		regexp = re.compile(rgxpattern)

		if not regexp.match(clincard):
			raise forms.ValidationError("Please enter an 8 digit clincard number in the format xxxxxxxx")
		
		# checking if unqiue after excluding current user		
		if Subjects.objects.exclude(study_id=self.instance.study_id).filter(clincard=clincard).exists():
			raise forms.ValidationError("A user with this clincard number already exists")
		
		return clincard

	class Meta:
		model = Subjects
		fields = ['first_name', 'last_name', 'phone', 'clincard', 'language', 'recruited_location', 'test_account', 'optout', 'deleted', 'notes']
		labels = {
			"phone": "Phone:",
			"clincard": "Clincard Number:",
			"optout": "<span class='text-danger'><strong>Opt-out from surveys.</strong></span>",
			"deleted": "<span class='text-danger'><strong>DELETE USER. Cannot be undone.</strong></span>",
			"notes": "<span class='text-danger'><strong>Notes</strong> (Please provide details on why this account was updated):</span>",
			"test_account": "<span class='text-info'><strong>This is a BeeLab (test) user</strong></span>",
		}
		widgets = {
			'phone': forms.TextInput(attrs={"required": "required", "placeholder": "xxx-xxx-xxxx"}),
			'clincard': forms.TextInput(attrs={"required": "required", "placeholder": "xxxxxxxx"}),
			'language': forms.RadioSelect(attrs={"required": "required"}),
			'recruited_location': forms.RadioSelect(attrs={"required": "required"}),
			'optout_reason': forms.TextInput(attrs={"rows": 1}),
			'notes': forms.Textarea(attrs={"rows": 10}),
		}
