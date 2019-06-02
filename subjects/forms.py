from django import forms
from subjects.models import Subjects
import re

class SMS_Form(forms.Form):
	sms_message = forms.CharField(label='Message Body:', max_length=1000, widget=forms.Textarea(attrs={'rows': 10}))

class RecruitForm(forms.ModelForm):

	def clean_phone(self):

		phone = self.cleaned_data.get('phone')

		rgxpattern='^\d{3}-\d{3}-\d{4}$'
		regexp = re.compile(rgxpattern)

		if not regexp.match(phone):
			raise forms.ValidationError("Incorrect format for phone number. Please enter as XXX-XXX-XXXX")
		phone_db = '+1' + phone.replace("-","")
		if Subjects.objects.filter(phone=phone_db).exists():
			raise forms.ValidationError("A user with this phone number already in the system")
		return phone_db

	class Meta:
		model = Subjects
		fields = ['first_name', 'last_name', 'phone', 'language', 'recruited_by', 'recruited_location', 'recruited_date']
		widgets = {
			'phone': forms.TextInput(attrs={"required": "required"}),
			'language': forms.RadioSelect(attrs={"required": "required"}),
			'recruited_location': forms.RadioSelect(attrs={"required": "required"}),
			'recruited_by': forms.HiddenInput(),
			'recruited_date': forms.HiddenInput(),
		}
