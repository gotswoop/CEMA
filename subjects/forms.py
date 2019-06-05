from django import forms
from subjects.models import Subjects
import re

class SMS_Form(forms.Form):
	sms_message = forms.CharField(label='Message Body:', max_length=1000, widget=forms.Textarea(attrs={'rows': 5}))

class RecruitForm(forms.ModelForm):

	send_test_survey = forms.BooleanField(label="<span class='text-danger'><strong>SEND TEST SURVEY? This triggers a text message with a link to the Test survey (Risk + Time)</strong></span>",required=False,initial=True)

	def clean_phone(self):

		phone = self.cleaned_data.get('phone')

		rgxpattern='^\d{3}-\d{3}-\d{4}$'
		regexp = re.compile(rgxpattern)

		if not regexp.match(phone):
			raise forms.ValidationError("Please enter phone number in the format xxx-xxx-xxxx")
		
		phone_db = '+1' + phone.replace("-","")
		
		if Subjects.objects.filter(phone=phone_db).exists():
			raise forms.ValidationError("A user with this phone number already in the system")
		return phone_db

	class Meta:
		model = Subjects
		fields = ['first_name', 'last_name', 'phone', 'language', 'recruited_by', 'recruited_location', 'test_account']
		labels = {
        	"phone": "Phone:",
        	"test_account": "<span class='text-info'><strong>This is a BeeLab (test) user.</strong></span>",
    	}
		widgets = {
			'phone': forms.TextInput(attrs={"required": "required", "placeholder": "xxx-xxx-xxxx"}),
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
			raise forms.ValidationError("A user with this phone number already in the system")
		return phone_db

	class Meta:
		model = Subjects
		fields = ['first_name', 'last_name', 'phone', 'language', 'recruited_location', 'test_account', 'optout', 'deleted', 'notes']
		labels = {
			"phone": "Phone:",
			"optout": "<span class='text-danger'><strong>Opt-out from surveys.</strong></span>",
			"deleted": "<span class='text-danger'><strong>DELETE USER. Cannot be undone.</strong></span>",
			"notes": "<span class='text-danger'><strong>Notes</strong> (Please provide some details on why this record was updated):</span>",
			"test_account": "<span class='text-info'><strong>This is BeeLab (test) user.</strong></span>",
		}
		widgets = {
			'phone': forms.TextInput(attrs={"required": "required", "placeholder": "xxx-xxx-xxxx"}),
			'language': forms.RadioSelect(attrs={"required": "required"}),
			'recruited_location': forms.RadioSelect(attrs={"required": "required"}),
			'optout_reason': forms.TextInput(attrs={"rows": 1}),
			'notes': forms.Textarea(attrs={"rows": 10}),
		}
